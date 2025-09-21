"""
通知相关业务逻辑
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from models.notification import (
    Notification, NotificationTemplate, UserNotificationSettings,
    NotificationType, NotificationPriority
)
from models.user import User, UserRole
from schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationQuery,
    NotificationTemplateCreate, NotificationTemplateUpdate,
    UserNotificationSettingsUpdate, NotificationStatistics,
    BulkNotificationCreate
)
from services.system_log_service import SystemLogService


class NotificationService:
    """通知管理服务"""
    
    @staticmethod
    def create_notification(db: Session, notification_data: NotificationCreate, current_user: User = None) -> Notification:
        """创建通知"""
        # 验证接收者存在
        recipient = db.query(User).filter(User.id == notification_data.recipient_id).first()
        if not recipient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="接收者不存在"
            )
        
        # 检查用户通知设置
        settings = NotificationService.get_user_settings(db, notification_data.recipient_id)
        if not NotificationService._should_send_notification(notification_data.type, settings):
            # 如果用户关闭了此类通知，仍创建记录但不发送
            notification_data.send_email = False
            notification_data.send_sms = False
            notification_data.send_push = False
        
        notification = Notification(**notification_data.model_dump())
        if current_user:
            notification.sender_id = current_user.id
        
        # 设置发送时间
        if not notification.scheduled_at:
            notification.scheduled_at = datetime.now()
        
        notification.sent_at = datetime.now()
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # 记录日志
        if current_user:
            SystemLogService.log_action(
                db=db,
                user_id=current_user.id,
                action="create_notification",
                resource_type="notification",
                resource_id=notification.id,
                details=f"发送通知: {notification.title}"
            )
        
        return notification
    
    @staticmethod
    def create_bulk_notifications(db: Session, bulk_data: BulkNotificationCreate, current_user: User) -> List[Notification]:
        """批量创建通知"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以批量发送通知"
            )
        
        notifications = []
        for recipient_id in bulk_data.recipient_ids:
            notification_data = NotificationCreate(
                title=bulk_data.title,
                content=bulk_data.content,
                type=bulk_data.type,
                priority=bulk_data.priority,
                recipient_id=recipient_id,
                send_email=bulk_data.send_email,
                send_sms=bulk_data.send_sms,
                send_push=bulk_data.send_push,
                scheduled_at=bulk_data.scheduled_at,
                expires_at=bulk_data.expires_at
            )
            
            notification = NotificationService.create_notification(db, notification_data, current_user)
            notifications.append(notification)
        
        return notifications
    
    @staticmethod
    def get_notifications(db: Session, user_id: int, query: NotificationQuery) -> List[Notification]:
        """获取用户通知列表"""
        q = db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_deleted == False
        )
        
        if query.type:
            q = q.filter(Notification.type == query.type)
        if query.is_read is not None:
            q = q.filter(Notification.is_read == query.is_read)
        if query.priority:
            q = q.filter(Notification.priority == query.priority)
        if query.start_date:
            q = q.filter(Notification.created_at >= query.start_date)
        if query.end_date:
            q = q.filter(Notification.created_at <= query.end_date)
        
        # 排序和分页
        q = q.order_by(desc(Notification.created_at))
        offset = (query.page - 1) * query.size
        notifications = q.offset(offset).limit(query.size).all()
        
        return notifications
    
    @staticmethod
    def get_notification(db: Session, notification_id: int, user_id: int) -> Notification:
        """获取通知详情"""
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.recipient_id == user_id,
            Notification.is_deleted == False
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="通知不存在"
            )
        
        return notification
    
    @staticmethod
    def update_notification(db: Session, notification_id: int, notification_data: NotificationUpdate, user_id: int) -> Notification:
        """更新通知状态"""
        notification = NotificationService.get_notification(db, notification_id, user_id)
        
        # 更新字段
        for field, value in notification_data.model_dump(exclude_unset=True).items():
            setattr(notification, field, value)
        
        # 如果标记为已读，设置阅读时间
        if notification_data.is_read and not notification.read_at:
            notification.read_at = datetime.now()
        
        notification.updated_at = datetime.now()
        db.commit()
        db.refresh(notification)
        
        return notification
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Notification:
        """标记为已读"""
        return NotificationService.update_notification(
            db, notification_id, 
            NotificationUpdate(is_read=True), 
            user_id
        )
    
    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """标记所有通知为已读"""
        updated_count = db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False,
            Notification.is_deleted == False
        ).update({
            "is_read": True,
            "read_at": datetime.now(),
            "updated_at": datetime.now()
        })
        
        db.commit()
        return updated_count
    
    @staticmethod
    def delete_notification(db: Session, notification_id: int, user_id: int) -> Notification:
        """删除通知（软删除）"""
        return NotificationService.update_notification(
            db, notification_id,
            NotificationUpdate(is_deleted=True),
            user_id
        )
    
    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """获取未读通知数量"""
        return db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False,
            Notification.is_deleted == False
        ).count()
    
    @staticmethod
    def get_user_settings(db: Session, user_id: int) -> UserNotificationSettings:
        """获取用户通知设置"""
        settings = db.query(UserNotificationSettings).filter(
            UserNotificationSettings.user_id == user_id
        ).first()
        
        if not settings:
            # 创建默认设置
            settings = UserNotificationSettings(user_id=user_id)
            db.add(settings)
            db.commit()
            db.refresh(settings)
        
        return settings
    
    @staticmethod
    def update_user_settings(db: Session, user_id: int, settings_data: UserNotificationSettingsUpdate) -> UserNotificationSettings:
        """更新用户通知设置"""
        settings = NotificationService.get_user_settings(db, user_id)
        
        for field, value in settings_data.model_dump(exclude_unset=True).items():
            setattr(settings, field, value)
        
        settings.updated_at = datetime.now()
        db.commit()
        db.refresh(settings)
        
        return settings
    
    @staticmethod
    def create_template(db: Session, template_data: NotificationTemplateCreate, current_user: User) -> NotificationTemplate:
        """创建通知模板"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以创建通知模板"
            )
        
        # 检查模板代码唯一性
        existing = db.query(NotificationTemplate).filter(
            NotificationTemplate.code == template_data.code
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模板代码已存在"
            )
        
        template = NotificationTemplate(**template_data.model_dump())
        db.add(template)
        db.commit()
        db.refresh(template)
        
        return template
    
    @staticmethod
    def get_templates(db: Session) -> List[NotificationTemplate]:
        """获取通知模板列表"""
        return db.query(NotificationTemplate).filter(
            NotificationTemplate.is_active == True
        ).all()
    
    @staticmethod
    def send_from_template(db: Session, template_code: str, recipient_id: int, 
                          variables: Dict[str, Any], current_user: User = None) -> Notification:
        """使用模板发送通知"""
        template = db.query(NotificationTemplate).filter(
            NotificationTemplate.code == template_code,
            NotificationTemplate.is_active == True
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="通知模板不存在"
            )
        
        # 渲染模板
        title = template.title_template.format(**variables)
        content = template.content_template.format(**variables)
        
        notification_data = NotificationCreate(
            title=title,
            content=content,
            type=template.type,
            priority=template.default_priority,
            recipient_id=recipient_id,
            send_email=template.default_send_email,
            send_sms=template.default_send_sms,
            send_push=template.default_send_push
        )
        
        return NotificationService.create_notification(db, notification_data, current_user)
    
    @staticmethod
    def get_statistics(db: Session, user_id: int) -> NotificationStatistics:
        """获取通知统计信息"""
        total = db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_deleted == False
        ).count()
        
        unread = db.query(Notification).filter(
            Notification.recipient_id == user_id,
            Notification.is_read == False,
            Notification.is_deleted == False
        ).count()
        
        read = total - unread
        
        # 按类型统计
        type_stats = db.query(
            Notification.type,
            func.count(Notification.id).label('count')
        ).filter(
            Notification.recipient_id == user_id,
            Notification.is_deleted == False
        ).group_by(Notification.type).all()
        
        # 按优先级统计
        priority_stats = db.query(
            Notification.priority,
            func.count(Notification.id).label('count')
        ).filter(
            Notification.recipient_id == user_id,
            Notification.is_deleted == False
        ).group_by(Notification.priority).all()
        
        return NotificationStatistics(
            total_notifications=total,
            unread_notifications=unread,
            read_notifications=read,
            notifications_by_type=[{"type": type_, "count": count} for type_, count in type_stats],
            notifications_by_priority=[{"priority": priority, "count": count} for priority, count in priority_stats]
        )
    
    @staticmethod
    def _should_send_notification(notification_type: str, settings: UserNotificationSettings) -> bool:
        """检查是否应该发送通知"""
        type_mapping = {
            NotificationType.SYSTEM.value: settings.system_notifications,
            NotificationType.BOOKING.value: settings.booking_notifications,
            NotificationType.PAYMENT.value: settings.payment_notifications,
            NotificationType.COMPETITION.value: settings.competition_notifications,
            NotificationType.EVALUATION.value: settings.evaluation_notifications,
            NotificationType.COACH_STUDENT.value: settings.coach_student_notifications,
        }
        
        return type_mapping.get(notification_type, True)
    
    @staticmethod
    def cleanup_old_notifications(db: Session, days_old: int = 30) -> int:
        """清理旧通知"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        deleted_count = db.query(Notification).filter(
            Notification.created_at < cutoff_date,
            Notification.is_deleted == True
        ).delete()
        
        db.commit()
        return deleted_count
