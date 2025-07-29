import json
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.models.notification import (
    Notification, NotificationTemplate, NotificationSettings,
    NotificationType, NotificationChannel, NotificationStatus
)
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationTemplateCreate
from app.core.config import settings


class NotificationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        channel: NotificationChannel,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            channel=channel,
            title=title,
            message=message,
            metadata=json.dumps(metadata) if metadata else None
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification
    
    def send_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Notification]:
        """Send notification to user through all enabled channels"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Get user notification settings
        settings = self.db.query(NotificationSettings).filter(
            NotificationSettings.user_id == user_id
        ).first()
        
        if not settings:
            # Create default settings
            settings = NotificationSettings(user_id=user_id)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        notifications = []
        
        # Check if user should receive this type of notification
        if not self._should_send_notification(settings, notification_type):
            return notifications
        
        # Send through enabled channels
        if settings.app_enabled:
            app_notification = self.create_notification(
                user_id, notification_type, NotificationChannel.APP, title, message, metadata
            )
            notifications.append(app_notification)
        
        if settings.email_enabled and user.email:
            email_notification = self.create_notification(
                user_id, notification_type, NotificationChannel.EMAIL, title, message, metadata
            )
            self._send_email_notification(user.email, title, message)
            email_notification.status = NotificationStatus.SENT
            email_notification.sent_at = datetime.utcnow()
            notifications.append(email_notification)
        
        if settings.sms_enabled and user.phone:
            sms_notification = self.create_notification(
                user_id, notification_type, NotificationChannel.SMS, title, message, metadata
            )
            self._send_sms_notification(user.phone, message)
            sms_notification.status = NotificationStatus.SENT
            sms_notification.sent_at = datetime.utcnow()
            notifications.append(sms_notification)
        
        self.db.commit()
        return notifications
    
    def _should_send_notification(self, settings: NotificationSettings, notification_type: NotificationType) -> bool:
        """Check if user should receive this type of notification"""
        if notification_type == NotificationType.LOGIN:
            return settings.login_notifications
        elif notification_type in [NotificationType.TRANSFER_SENT, NotificationType.TRANSFER_RECEIVED]:
            return settings.transfer_notifications
        elif notification_type == NotificationType.PROMOTION:
            return settings.promotion_notifications
        elif notification_type in [NotificationType.SECURITY_ALERT, NotificationType.SYSTEM_UPDATE]:
            return settings.security_notifications
        else:
            return settings.system_notifications
    
    def _send_email_notification(self, email: str, subject: str, message: str) -> bool:
        """Send email notification"""
        try:
            # Configure email settings from environment
            smtp_server = getattr(settings, 'SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = getattr(settings, 'SMTP_PORT', 587)
            smtp_username = getattr(settings, 'SMTP_USERNAME', None)
            smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
            
            if not all([smtp_username, smtp_password]):
                # Log that email service is not configured
                print(f"Email service not configured. Would send to {email}: {subject}")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = smtp_username
            msg['To'] = email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send email to {email}: {str(e)}")
            return False
    
    def _send_sms_notification(self, phone: str, message: str) -> bool:
        """Send SMS notification"""
        try:
            # Configure SMS settings from environment
            sms_api_key = getattr(settings, 'SMS_API_KEY', None)
            sms_api_url = getattr(settings, 'SMS_API_URL', None)
            
            if not all([sms_api_key, sms_api_url]):
                # Log that SMS service is not configured
                print(f"SMS service not configured. Would send to {phone}: {message}")
                return False
            
            # Example using a generic SMS API
            payload = {
                'api_key': sms_api_key,
                'to': phone,
                'message': message
            }
            
            response = requests.post(sms_api_url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print(f"Failed to send SMS to {phone}: {str(e)}")
            return False
    
    def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """Get user notifications with pagination"""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.status == NotificationStatus.PENDING)
        
        total = query.count()
        unread_count = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.status == NotificationStatus.PENDING
        ).count()
        
        notifications = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
        
        return {
            "notifications": notifications,
            "total": total,
            "unread_count": unread_count
        }
    
    def mark_notification_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if notification:
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def mark_all_notifications_as_read(self, user_id: int) -> int:
        """Mark all user notifications as read"""
        result = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.status == NotificationStatus.PENDING
        ).update({
            "status": NotificationStatus.READ,
            "read_at": datetime.utcnow()
        })
        self.db.commit()
        return result
    
    def create_notification_template(self, template_data: NotificationTemplateCreate) -> NotificationTemplate:
        """Create a new notification template"""
        template = NotificationTemplate(**template_data.dict())
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def get_notification_templates(self, skip: int = 0, limit: int = 50) -> List[NotificationTemplate]:
        """Get notification templates"""
        return self.db.query(NotificationTemplate).offset(skip).limit(limit).all()
    
    def update_notification_template(self, template_id: int, template_data: Dict[str, Any]) -> Optional[NotificationTemplate]:
        """Update notification template"""
        template = self.db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
        if template:
            for key, value in template_data.items():
                if hasattr(template, key):
                    setattr(template, key, value)
            template.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(template)
        return template
    
    def get_or_create_user_settings(self, user_id: int) -> NotificationSettings:
        """Get or create user notification settings"""
        settings = self.db.query(NotificationSettings).filter(
            NotificationSettings.user_id == user_id
        ).first()
        
        if not settings:
            settings = NotificationSettings(user_id=user_id)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        
        return settings
    
    def update_user_settings(self, user_id: int, settings_data: Dict[str, Any]) -> NotificationSettings:
        """Update user notification settings"""
        settings = self.get_or_create_user_settings(user_id)
        
        for key, value in settings_data.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        settings.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(settings)
        return settings


# Convenience functions for common notifications
def send_login_notification(db: Session, user_id: int, ip_address: str = None):
    """Send login notification"""
    service = NotificationService(db)
    title = "New Login Detected"
    message = f"Your account was accessed from a new device/location."
    if ip_address:
        message += f" IP: {ip_address}"
    
    service.send_notification(user_id, NotificationType.LOGIN, title, message)


def send_transfer_notification(db: Session, user_id: int, amount: str, currency: str, transaction_type: str):
    """Send transfer notification"""
    service = NotificationService(db)
    title = f"Transfer {transaction_type.title()}"
    message = f"Your {transaction_type} of {amount} {currency} has been processed successfully."
    
    notification_type = NotificationType.TRANSFER_SENT if transaction_type == "sent" else NotificationType.TRANSFER_RECEIVED
    service.send_notification(user_id, notification_type, title, message)


def send_promotion_notification(db: Session, user_id: int, title: str, message: str):
    """Send promotion notification"""
    service = NotificationService(db)
    service.send_notification(user_id, NotificationType.PROMOTION, title, message)


def send_security_alert(db: Session, user_id: int, alert_type: str, message: str):
    """Send security alert"""
    service = NotificationService(db)
    title = f"Security Alert: {alert_type}"
    service.send_notification(user_id, NotificationType.SECURITY_ALERT, title, message) 