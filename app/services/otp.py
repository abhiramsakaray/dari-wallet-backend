import random
import string
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.models.otp import OTP, OTPConfig, OTPType, OTPChannel, OTPStatus
from app.models.user import User
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token


class OTPService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_otp(self, length: int = 6) -> str:
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))
    
    def get_otp_config(self, otp_type: OTPType, channel: OTPChannel) -> Optional[OTPConfig]:
        """Get OTP configuration for specific type and channel"""
        return self.db.query(OTPConfig).filter(
            OTPConfig.otp_type == otp_type,
            OTPConfig.channel == channel
        ).first()
    
    def is_otp_enabled(self, otp_type: OTPType, channel: OTPChannel) -> bool:
        """Check if OTP is enabled for specific type and channel"""
        config = self.get_otp_config(otp_type, channel)
        return config.is_enabled if config else False
    
    def can_request_otp(self, user_id: int, otp_type: OTPType, channel: OTPChannel) -> Tuple[bool, int]:
        """Check if user can request OTP (cooldown period)"""
        config = self.get_otp_config(otp_type, channel)
        if not config:
            return False, 0
        
        # Check for recent OTP requests
        cooldown_time = datetime.utcnow() - timedelta(minutes=config.cooldown_minutes)
        recent_otp = self.db.query(OTP).filter(
            OTP.user_id == user_id,
            OTP.otp_type == otp_type,
            OTP.channel == channel,
            OTP.created_at > cooldown_time
        ).first()
        
        if recent_otp:
            remaining_time = (recent_otp.created_at + timedelta(minutes=config.cooldown_minutes) - datetime.utcnow).total_seconds() / 60
            return False, int(remaining_time)
        
        return True, 0
    
    def create_otp(self, user_id: int, otp_type: OTPType, channel: OTPChannel) -> Optional[OTP]:
        """Create a new OTP for user"""
        config = self.get_otp_config(otp_type, channel)
        if not config or not config.is_enabled:
            return None
        
        # Check cooldown
        can_request, cooldown_remaining = self.can_request_otp(user_id, otp_type, channel)
        if not can_request:
            raise ValueError(f"Please wait {cooldown_remaining} minutes before requesting another OTP")
        
        # Generate OTP
        otp_code = self.generate_otp(config.otp_length)
        expires_at = datetime.utcnow() + timedelta(minutes=config.expiry_minutes)
        
        # Create OTP record
        otp = OTP(
            user_id=user_id,
            otp_code=otp_code,
            otp_type=otp_type,
            channel=channel,
            max_attempts=config.max_attempts,
            expires_at=expires_at
        )
        
        self.db.add(otp)
        self.db.commit()
        self.db.refresh(otp)
        
        return otp
    
    def send_otp_email(self, email: str, otp_code: str, otp_type: OTPType) -> bool:
        """Send OTP via email"""
        try:
            # Configure email settings
            smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = getattr(settings, 'SMTP_PORT', 587)
            smtp_username = getattr(settings, 'SMTP_USERNAME', None)
            smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
            
            if not all([smtp_username, smtp_password]):
                print(f"Email service not configured. Would send OTP {otp_code} to {email}")
                return False
            
            # Create email message
            subject = f"DARI Wallet - {otp_type.value.title()} OTP"
            message = f"""
            Your DARI Wallet {otp_type.value.replace('_', ' ').title()} OTP is: {otp_code}
            
            This OTP will expire in 10 minutes.
            If you didn't request this OTP, please ignore this email.
            
            Best regards,
            DARI Wallet Team
            """
            
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send OTP email to {email}: {str(e)}")
            return False
    
    def send_otp_sms(self, phone: str, otp_code: str, otp_type: OTPType) -> bool:
        """Send OTP via SMS"""
        try:
            # Configure SMS settings
            sms_api_key = getattr(settings, 'SMS_API_KEY', None)
            sms_api_url = getattr(settings, 'SMS_API_URL', None)
            
            if not all([sms_api_key, sms_api_url]):
                print(f"SMS service not configured. Would send OTP {otp_code} to {phone}")
                return False
            
            # Create SMS message
            message = f"Your DARI Wallet {otp_type.value.replace('_', ' ').title()} OTP is: {otp_code}. Valid for 10 minutes."
            
            # Send SMS
            payload = {
                'api_key': sms_api_key,
                'to': phone,
                'message': message
            }
            
            response = requests.post(sms_api_url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send OTP SMS to {phone}: {str(e)}")
            return False
    
    def request_otp(self, email: str, otp_type: OTPType = OTPType.LOGIN, channel: OTPChannel = OTPChannel.EMAIL) -> dict:
        """Request OTP for user"""
        # Find user by email
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("User not found")
        
        # Check if OTP is enabled for this type and channel
        if not self.is_otp_enabled(otp_type, channel):
            raise ValueError(f"OTP is not enabled for {otp_type.value} via {channel.value}")
        
        # Create OTP
        otp = self.create_otp(user.id, otp_type, channel)
        if not otp:
            raise ValueError("Failed to create OTP")
        
        # Send OTP
        success = False
        if channel == OTPChannel.EMAIL:
            success = self.send_otp_email(user.email, otp.otp_code, otp_type)
        elif channel == OTPChannel.SMS:
            if not user.phone:
                raise ValueError("User does not have a phone number for SMS OTP")
            success = self.send_otp_sms(user.phone, otp.otp_code, otp_type)
        
        if not success:
            # Mark OTP as failed
            otp.status = OTPStatus.FAILED
            self.db.commit()
            raise ValueError(f"Failed to send OTP via {channel.value}")
        
        config = self.get_otp_config(otp_type, channel)
        return {
            "message": f"OTP sent successfully via {channel.value}",
            "expires_in_minutes": config.expiry_minutes,
            "can_resend_in_minutes": config.cooldown_minutes
        }
    
    def verify_otp(self, email: str, otp_code: str, otp_type: OTPType = OTPType.LOGIN) -> dict:
        """Verify OTP and return tokens if valid"""
        # Find user by email
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("User not found")
        
        # Find valid OTP
        otp = self.db.query(OTP).filter(
            OTP.user_id == user.id,
            OTP.otp_type == otp_type,
            OTP.status == OTPStatus.PENDING,
            OTP.otp_code == otp_code
        ).first()
        
        if not otp:
            raise ValueError("Invalid OTP code")
        
        # Check if OTP is expired
        if otp.is_expired:
            otp.status = OTPStatus.EXPIRED
            self.db.commit()
            raise ValueError("OTP has expired")
        
        # Check attempts
        if otp.attempts >= otp.max_attempts:
            otp.status = OTPStatus.FAILED
            self.db.commit()
            raise ValueError("Maximum OTP attempts exceeded")
        
        # Increment attempts
        otp.attempts += 1
        
        # Verify OTP
        if otp.otp_code == otp_code:
            otp.status = OTPStatus.VERIFIED
            otp.verified_at = datetime.utcnow()
            self.db.commit()
            
            # Generate tokens
            access_token = create_access_token(data={"sub": user.id})
            refresh_token = create_refresh_token(data={"sub": user.id})
            
            return {
                "message": "OTP verified successfully",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 30 * 60  # 30 minutes
            }
        else:
            self.db.commit()
            raise ValueError("Invalid OTP code")
    
    def get_user_otps(self, user_id: int, otp_type: Optional[OTPType] = None) -> list[OTP]:
        """Get user's OTPs"""
        query = self.db.query(OTP).filter(OTP.user_id == user_id)
        if otp_type:
            query = query.filter(OTP.otp_type == otp_type)
        return query.order_by(OTP.created_at.desc()).all()
    
    def cleanup_expired_otps(self) -> int:
        """Clean up expired OTPs"""
        expired_otps = self.db.query(OTP).filter(
            OTP.status == OTPStatus.PENDING,
            OTP.expires_at < datetime.utcnow()
        ).all()
        
        for otp in expired_otps:
            otp.status = OTPStatus.EXPIRED
        
        self.db.commit()
        return len(expired_otps)


# Convenience functions
def request_login_otp(db: Session, email: str, channel: OTPChannel = OTPChannel.EMAIL) -> dict:
    """Request login OTP"""
    service = OTPService(db)
    return service.request_otp(email, OTPType.LOGIN, channel)


def verify_login_otp(db: Session, email: str, otp_code: str) -> dict:
    """Verify login OTP"""
    service = OTPService(db)
    return service.verify_otp(email, otp_code, OTPType.LOGIN)


def is_login_otp_enabled(db: Session, channel: OTPChannel = OTPChannel.EMAIL) -> bool:
    """Check if login OTP is enabled"""
    service = OTPService(db)
    return service.is_otp_enabled(OTPType.LOGIN, channel) 