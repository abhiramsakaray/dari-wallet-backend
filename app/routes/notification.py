from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.services.notification import NotificationService
from app.schemas.notification import (
    NotificationResponse, NotificationUpdate, NotificationList,
    NotificationTemplateCreate, NotificationTemplateUpdate, NotificationTemplateResponse, NotificationTemplateList,
    NotificationSettingsUpdate, NotificationSettingsResponse
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=NotificationList)
def get_user_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's notifications"""
    service = NotificationService(db)
    result = service.get_user_notifications(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        unread_only=unread_only
    )
    
    return NotificationList(
        notifications=result["notifications"],
        total=result["total"],
        unread_count=result["unread_count"]
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific notification"""
    service = NotificationService(db)
    notification = db.query(service.db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first())
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return notification


@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    service = NotificationService(db)
    success = service.mark_notification_as_read(notification_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    return {"message": "Notification marked as read"}


@router.put("/read-all")
def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark all user notifications as read"""
    service = NotificationService(db)
    count = service.mark_all_notifications_as_read(current_user.id)
    
    return {"message": f"Marked {count} notifications as read"}


@router.get("/settings", response_model=NotificationSettingsResponse)
def get_notification_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's notification settings"""
    service = NotificationService(db)
    settings = service.get_or_create_user_settings(current_user.id)
    return settings


@router.put("/settings", response_model=NotificationSettingsResponse)
def update_notification_settings(
    settings_data: NotificationSettingsUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user's notification settings"""
    service = NotificationService(db)
    settings = service.update_user_settings(current_user.id, settings_data.dict(exclude_unset=True))
    return settings


# Admin routes for notification templates
@router.get("/admin/templates", response_model=NotificationTemplateList)
def get_notification_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all notification templates (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = NotificationService(db)
    templates = service.get_notification_templates(skip=skip, limit=limit)
    
    return NotificationTemplateList(
        templates=templates,
        total=len(templates)
    )


@router.post("/admin/templates", response_model=NotificationTemplateResponse)
def create_notification_template(
    template_data: NotificationTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new notification template (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = NotificationService(db)
    template = service.create_notification_template(template_data)
    return template


@router.put("/admin/templates/{template_id}", response_model=NotificationTemplateResponse)
def update_notification_template(
    template_id: int,
    template_data: NotificationTemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a notification template (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    service = NotificationService(db)
    template = service.update_notification_template(template_id, template_data.dict(exclude_unset=True))
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    return template


@router.delete("/admin/templates/{template_id}")
def delete_notification_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a notification template (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    db.delete(template)
    db.commit()
    
    return {"message": "Template deleted successfully"}


# Admin routes for sending notifications
@router.post("/admin/send")
def send_notification_to_user(
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a notification to a specific user (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Validate notification type
    try:
        from app.models.notification import NotificationType
        notification_type_enum = NotificationType(notification_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification type"
        )
    
    service = NotificationService(db)
    notifications = service.send_notification(
        user_id=user_id,
        notification_type=notification_type_enum,
        title=title,
        message=message
    )
    
    return {
        "message": f"Notification sent successfully",
        "notifications_created": len(notifications)
    }


@router.post("/admin/send-bulk")
def send_notification_to_all_users(
    notification_type: str,
    title: str,
    message: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a notification to all users (admin only)"""
    if current_user.role.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Validate notification type
    try:
        from app.models.notification import NotificationType
        notification_type_enum = NotificationType(notification_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid notification type"
        )
    
    # Get all active users
    users = db.query(User).filter(User.is_active == True).all()
    
    service = NotificationService(db)
    total_notifications = 0
    
    for user in users:
        notifications = service.send_notification(
            user_id=user.id,
            notification_type=notification_type_enum,
            title=title,
            message=message
        )
        total_notifications += len(notifications)
    
    return {
        "message": f"Notification sent to {len(users)} users",
        "total_notifications_created": total_notifications
    } 