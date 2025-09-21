"""
系统通知相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class NotificationType(enum.Enum):
    """通知类型"""
    SYSTEM = "system"          # 系统通知
    BOOKING = "booking"        # 预约相关
    PAYMENT = "payment"        # 支付相关
    COMPETITION = "competition"  # 比赛相关
    EVALUATION = "evaluation"  # 评价相关
    COACH_STUDENT = "coach_student"  # 师生关系相关


class NotificationPriority(enum.Enum):
    """通知优先级"""
    LOW = "low"        # 低
    NORMAL = "normal"  # 普通
    HIGH = "high"      # 高
    URGENT = "urgent"  # 紧急


class Notification(Base):
    """系统通知表"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    type = Column(String(20), nullable=False, comment="通知类型")
    priority = Column(String(10), default=NotificationPriority.NORMAL.value, comment="优先级")
    
    # 发送者和接收者
    sender_id = Column(Integer, ForeignKey("users.id"), comment="发送者ID")
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="接收者ID")
    
    # 关联资源
    resource_type = Column(String(50), comment="关联资源类型")
    resource_id = Column(Integer, comment="关联资源ID")
    
    # 状态信息
    is_read = Column(Boolean, default=False, comment="是否已读")
    read_at = Column(DateTime(timezone=True), comment="阅读时间")
    is_deleted = Column(Boolean, default=False, comment="是否删除")
    
    # 发送方式
    send_email = Column(Boolean, default=False, comment="是否发送邮件")
    send_sms = Column(Boolean, default=False, comment="是否发送短信")
    send_push = Column(Boolean, default=True, comment="是否推送到应用")
    
    # 时间字段
    scheduled_at = Column(DateTime(timezone=True), comment="预定发送时间")
    sent_at = Column(DateTime(timezone=True), comment="实际发送时间")
    expires_at = Column(DateTime(timezone=True), comment="过期时间")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])


class NotificationTemplate(Base):
    """通知模板表"""
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, comment="模板代码")
    name = Column(String(100), nullable=False, comment="模板名称")
    type = Column(String(20), nullable=False, comment="通知类型")
    
    # 模板内容
    title_template = Column(String(200), nullable=False, comment="标题模板")
    content_template = Column(Text, nullable=False, comment="内容模板")
    
    # 默认设置
    default_priority = Column(String(10), default=NotificationPriority.NORMAL.value, comment="默认优先级")
    default_send_email = Column(Boolean, default=False, comment="默认发送邮件")
    default_send_sms = Column(Boolean, default=False, comment="默认发送短信")
    default_send_push = Column(Boolean, default=True, comment="默认推送到应用")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")


class UserNotificationSettings(Base):
    """用户通知设置表"""
    __tablename__ = "user_notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="用户ID")
    
    # 通知类型开关
    system_notifications = Column(Boolean, default=True, comment="系统通知")
    booking_notifications = Column(Boolean, default=True, comment="预约通知")
    payment_notifications = Column(Boolean, default=True, comment="支付通知")
    competition_notifications = Column(Boolean, default=True, comment="比赛通知")
    evaluation_notifications = Column(Boolean, default=True, comment="评价通知")
    coach_student_notifications = Column(Boolean, default=True, comment="师生关系通知")
    
    # 发送方式设置
    email_enabled = Column(Boolean, default=False, comment="邮件通知")
    sms_enabled = Column(Boolean, default=False, comment="短信通知")
    push_enabled = Column(Boolean, default=True, comment="应用内推送")
    
    # 免打扰设置
    quiet_start_time = Column(String(5), default="22:00", comment="免打扰开始时间")
    quiet_end_time = Column(String(5), default="08:00", comment="免打扰结束时间")
    weekend_quiet = Column(Boolean, default=False, comment="周末免打扰")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", back_populates="notification_settings")
