#!/usr/bin/env python3
"""
Script to initialize default notification templates in the database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, get_db
from app.models.notification import NotificationTemplate, NotificationType, NotificationChannel


def init_notification_templates():
    """Initialize default notification templates"""
    db = next(get_db())
    
    # Default notification templates
    default_templates = [
        {
            "name": "login_notification",
            "type": NotificationType.LOGIN,
            "channel": NotificationChannel.EMAIL,
            "title_template": "New Login Detected",
            "message_template": "Your account was accessed from a new device/location. If this wasn't you, please contact support immediately."
        },
        {
            "name": "login_notification_sms",
            "type": NotificationType.LOGIN,
            "channel": NotificationChannel.SMS,
            "title_template": "New Login",
            "message_template": "Your DARI wallet was accessed from a new device. Contact support if this wasn't you."
        },
        {
            "name": "transfer_sent_email",
            "type": NotificationType.TRANSFER_SENT,
            "channel": NotificationChannel.EMAIL,
            "title_template": "Transfer Sent Successfully",
            "message_template": "Your transfer of {amount} {currency} has been sent successfully. Transaction ID: {tx_id}"
        },
        {
            "name": "transfer_sent_sms",
            "type": NotificationType.TRANSFER_SENT,
            "channel": NotificationChannel.SMS,
            "title_template": "Transfer Sent",
            "message_template": "Transfer of {amount} {currency} sent. TX: {tx_id}"
        },
        {
            "name": "transfer_received_email",
            "type": NotificationType.TRANSFER_RECEIVED,
            "channel": NotificationChannel.EMAIL,
            "title_template": "Transfer Received",
            "message_template": "You have received {amount} {currency}. Transaction ID: {tx_id}"
        },
        {
            "name": "transfer_received_sms",
            "type": NotificationType.TRANSFER_RECEIVED,
            "channel": NotificationChannel.SMS,
            "title_template": "Transfer Received",
            "message_template": "Received {amount} {currency}. TX: {tx_id}"
        },
        {
            "name": "security_alert_email",
            "type": NotificationType.SECURITY_ALERT,
            "channel": NotificationChannel.EMAIL,
            "title_template": "Security Alert: {alert_type}",
            "message_template": "A security alert has been triggered: {alert_type}. Please review your account activity."
        },
        {
            "name": "security_alert_sms",
            "type": NotificationType.SECURITY_ALERT,
            "channel": NotificationChannel.SMS,
            "title_template": "Security Alert",
            "message_template": "Security alert: {alert_type}. Review your account."
        },
        {
            "name": "promotion_email",
            "type": NotificationType.PROMOTION,
            "channel": NotificationChannel.EMAIL,
            "title_template": "{promotion_title}",
            "message_template": "{promotion_message}"
        },
        {
            "name": "promotion_sms",
            "type": NotificationType.PROMOTION,
            "channel": NotificationChannel.SMS,
            "title_template": "DARI Promotion",
            "message_template": "{promotion_message}"
        },
        {
            "name": "wallet_created_email",
            "type": NotificationType.WALLET_CREATED,
            "channel": NotificationChannel.EMAIL,
            "title_template": "New Wallet Created",
            "message_template": "A new wallet has been created for {chain} network. Address: {address}"
        },
        {
            "name": "alias_created_email",
            "type": NotificationType.ALIAS_CREATED,
            "channel": NotificationChannel.EMAIL,
            "title_template": "New Alias Created",
            "message_template": "A new alias '{alias_name}' has been created and linked to your wallet."
        },
        {
            "name": "verification_email",
            "type": NotificationType.VERIFICATION,
            "channel": NotificationChannel.EMAIL,
            "title_template": "Account Verification",
            "message_template": "Please verify your account by clicking the link: {verification_link}"
        }
    ]
    
    try:
        # Check if templates already exist
        existing_templates = db.query(NotificationTemplate).count()
        if existing_templates > 0:
            print(f"Found {existing_templates} existing templates. Skipping initialization.")
            return
        
        # Add templates
        for template_data in default_templates:
            template = NotificationTemplate(**template_data)
            db.add(template)
        
        db.commit()
        print(f"Successfully initialized {len(default_templates)} notification templates:")
        for template in default_templates:
            print(f"  - {template['name']} ({template['type'].value} - {template['channel'].value})")
            
    except Exception as e:
        print(f"Error initializing notification templates: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_notification_templates() 