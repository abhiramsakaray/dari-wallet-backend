from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.login_log import LoginLog
from app.models.user import User
from app.models.role import Role
import requests
import json


class LoginLogger:
    def __init__(self, db: Session):
        self.db = db

    def log_login_attempt(
        self,
        email: str,
        success: bool,
        user: Optional[User] = None,
        device_info: str = None,
        ip_address: str = None,
        failure_reason: str = None,
        otp_required: bool = False,
        otp_verified: bool = False,
        admin_login: bool = False
    ) -> LoginLog:
        """Log a login attempt with comprehensive details"""
        
        # Get location info from IP (in production, use a proper geolocation service)
        location_info = self._get_location_from_ip(ip_address) if ip_address else {}
        
        login_log = LoginLog(
            user_id=user.id if user else None,
            email=email,
            success=success,
            device_info=device_info,
            ip_address=ip_address,
            location=location_info.get('location', 'Unknown'),
            country=location_info.get('country', 'Unknown'),
            city=location_info.get('city', 'Unknown'),
            timezone=location_info.get('timezone', 'Unknown'),
            failure_reason=failure_reason,
            otp_required=otp_required,
            otp_verified=otp_verified,
            admin_login=admin_login
        )
        
        self.db.add(login_log)
        self.db.commit()
        self.db.refresh(login_log)
        
        return login_log

    def log_successful_login(
        self,
        user: User,
        device_info: str = None,
        ip_address: str = None,
        otp_verified: bool = False,
        admin_login: bool = False
    ) -> LoginLog:
        """Log a successful login"""
        admin_login = admin_login or user.role.name in ['admin', 'role_admin']
        
        return self.log_login_attempt(
            email=user.email,
            success=True,
            user=user,
            device_info=device_info,
            ip_address=ip_address,
            otp_verified=otp_verified,
            admin_login=admin_login
        )

    def log_failed_login(
        self,
        email: str,
        failure_reason: str,
        device_info: str = None,
        ip_address: str = None,
        otp_required: bool = False
    ) -> LoginLog:
        """Log a failed login attempt"""
        return self.log_login_attempt(
            email=email,
            success=False,
            device_info=device_info,
            ip_address=ip_address,
            failure_reason=failure_reason,
            otp_required=otp_required
        )

    def _get_location_from_ip(self, ip_address: str) -> Dict[str, str]:
        """Get location information from IP address"""
        try:
            # In production, use a proper geolocation service like MaxMind or IP2Location
            # For now, return basic info
            if ip_address and ip_address != "Unknown":
                # You could integrate with a service like ipapi.co or similar
                # response = requests.get(f"http://ip-api.com/json/{ip_address}")
                # if response.status_code == 200:
                #     data = response.json()
                #     return {
                #         'location': f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}",
                #         'country': data.get('country', 'Unknown'),
                #         'city': data.get('city', 'Unknown'),
                #         'timezone': data.get('timezone', 'Unknown')
                #     }
                return {
                    'location': 'Location service not configured',
                    'country': 'Unknown',
                    'city': 'Unknown',
                    'timezone': 'Unknown'
                }
        except Exception as e:
            print(f"Error getting location from IP: {str(e)}")
        
        return {
            'location': 'Unknown',
            'country': 'Unknown',
            'city': 'Unknown',
            'timezone': 'Unknown'
        }

    def get_login_statistics(self, user_id: Optional[int] = None, days: int = 30) -> Dict[str, Any]:
        """Get login statistics for fraud analysis"""
        from datetime import timedelta
        
        start_date = datetime.utcnow() - timedelta(days=days)
        query = self.db.query(LoginLog).filter(LoginLog.created_at >= start_date)
        
        if user_id:
            query = query.filter(LoginLog.user_id == user_id)
        
        logs = query.all()
        
        # Calculate statistics
        total_attempts = len(logs)
        successful_logins = len([log for log in logs if log.success])
        failed_logins = total_attempts - successful_logins
        
        # Unique IPs and locations
        unique_ips = len(set(log.ip_address for log in logs if log.ip_address))
        unique_locations = len(set(log.location for log in logs if log.location))
        
        # Admin login attempts
        admin_logins = len([log for log in logs if log.admin_login])
        
        # Failed login reasons
        failure_reasons = {}
        for log in logs:
            if not log.success and log.failure_reason:
                failure_reasons[log.failure_reason] = failure_reasons.get(log.failure_reason, 0) + 1
        
        return {
            'total_attempts': total_attempts,
            'successful_logins': successful_logins,
            'failed_logins': failed_logins,
            'success_rate': (successful_logins / total_attempts * 100) if total_attempts > 0 else 0,
            'unique_ips': unique_ips,
            'unique_locations': unique_locations,
            'admin_logins': admin_logins,
            'failure_reasons': failure_reasons
        }

    def get_suspicious_activity(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Detect suspicious login activity"""
        from datetime import timedelta
        
        # Check last 7 days
        start_date = datetime.utcnow() - timedelta(days=7)
        query = self.db.query(LoginLog).filter(LoginLog.created_at >= start_date)
        
        if user_id:
            query = query.filter(LoginLog.user_id == user_id)
        
        logs = query.all()
        
        suspicious_indicators = []
        
        # Check for multiple failed attempts
        failed_attempts = len([log for log in logs if not log.success])
        if failed_attempts > 5:
            suspicious_indicators.append(f"Multiple failed login attempts: {failed_attempts}")
        
        # Check for logins from multiple locations
        unique_locations = len(set(log.location for log in logs if log.location and log.location != 'Unknown'))
        if unique_locations > 3:
            suspicious_indicators.append(f"Logins from multiple locations: {unique_locations}")
        
        # Check for logins from multiple IPs
        unique_ips = len(set(log.ip_address for log in logs if log.ip_address and log.ip_address != 'Unknown'))
        if unique_ips > 5:
            suspicious_indicators.append(f"Logins from multiple IP addresses: {unique_ips}")
        
        # Check for unusual login times (simplified)
        # In production, you'd analyze login patterns more sophisticatedly
        
        return {
            'suspicious_indicators': suspicious_indicators,
            'risk_level': 'high' if len(suspicious_indicators) > 2 else 'medium' if len(suspicious_indicators) > 0 else 'low'
        } 