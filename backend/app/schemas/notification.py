"""
通知相关的数据模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    title: str = Field(..., max_length=200, description="通知标题")
    content: str = Field(..., description="通知内容")
    type: str = Field(..., description="通知类型")
    priority: str = Field("normal", description="优先级")
    recipient_id: int = Field(..., description="接收者ID")
    resource_type: Optional[str] = Field(None, description="关联资源类型")
    resource_id: Optional[int] = Field(None, description="关联资源ID")


class NotificationCreate(NotificationBase):
    sender_id: Optional[int] = Field(None, description="发送者ID")
    send_email: bool = Field(False, description="是否发送邮件")
    send_sms: bool = Field(False, description="是否发送短信")
    send_push: bool = Field(True, description="是否推送到应用")
    scheduled_at: Optional[datetime] = Field(None, description="预定发送时间")
    expires_at: Optional[datetime] = Field(None, description="过期时间")


class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = Field(None, description="是否已读")
    is_deleted: Optional[bool] = Field(None, description="是否删除")


class NotificationResponse(NotificationBase):
    id: int
    sender_id: Optional[int]
    is_read: bool
    read_at: Optional[datetime]
    is_deleted: bool
    send_email: bool
    send_sms: bool
    send_push: bool
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class NotificationQuery(BaseModel):
    type: Optional[str] = Field(None, description="通知类型筛选")
    is_read: Optional[bool] = Field(None, description="是否已读筛选")
    priority: Optional[str] = Field(None, description="优先级筛选")
    start_date: Optional[datetime] = Field(None, description="开始日期筛选")
    end_date: Optional[datetime] = Field(None, description="结束日期筛选")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")


class NotificationTemplateBase(BaseModel):
    code: str = Field(..., max_length=50, description="模板代码")
    name: str = Field(..., max_length=100, description="模板名称")
    type: str = Field(..., description="通知类型")
    title_template: str = Field(..., max_length=200, description="标题模板")
    content_template: str = Field(..., description="内容模板")


class NotificationTemplateCreate(NotificationTemplateBase):
    default_priority: str = Field("normal", description="默认优先级")
    default_send_email: bool = Field(False, description="默认发送邮件")
    default_send_sms: bool = Field(False, description="默认发送短信")
    default_send_push: bool = Field(True, description="默认推送到应用")


class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="模板名称")
    title_template: Optional[str] = Field(None, max_length=200, description="标题模板")
    content_template: Optional[str] = Field(None, description="内容模板")
    default_priority: Optional[str] = Field(None, description="默认优先级")
    default_send_email: Optional[bool] = Field(None, description="默认发送邮件")
    default_send_sms: Optional[bool] = Field(None, description="默认发送短信")
    default_send_push: Optional[bool] = Field(None, description="默认推送到应用")
    is_active: Optional[bool] = Field(None, description="是否启用")


class NotificationTemplateResponse(NotificationTemplateBase):
    id: int
    default_priority: str
    default_send_email: bool
    default_send_sms: bool
    default_send_push: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserNotificationSettingsBase(BaseModel):
    system_notifications: bool = Field(True, description="系统通知")
    booking_notifications: bool = Field(True, description="预约通知")
    payment_notifications: bool = Field(True, description="支付通知")
    competition_notifications: bool = Field(True, description="比赛通知")
    evaluation_notifications: bool = Field(True, description="评价通知")
    coach_student_notifications: bool = Field(True, description="师生关系通知")
    email_enabled: bool = Field(False, description="邮件通知")
    sms_enabled: bool = Field(False, description="短信通知")
    push_enabled: bool = Field(True, description="应用内推送")


class UserNotificationSettingsUpdate(UserNotificationSettingsBase):
    quiet_start_time: Optional[str] = Field(None, description="免打扰开始时间")
    quiet_end_time: Optional[str] = Field(None, description="免打扰结束时间")
    weekend_quiet: Optional[bool] = Field(None, description="周末免打扰")


class UserNotificationSettingsResponse(UserNotificationSettingsBase):
    id: int
    user_id: int
    quiet_start_time: str
    quiet_end_time: str
    weekend_quiet: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class NotificationStatistics(BaseModel):
    total_notifications: int = Field(0, description="总通知数")
    unread_notifications: int = Field(0, description="未读通知数")
    read_notifications: int = Field(0, description="已读通知数")
    notifications_by_type: List[dict] = Field([], description="按类型统计")
    notifications_by_priority: List[dict] = Field([], description="按优先级统计")


class BulkNotificationCreate(BaseModel):
    title: str = Field(..., max_length=200, description="通知标题")
    content: str = Field(..., description="通知内容")
    type: str = Field(..., description="通知类型")
    priority: str = Field("normal", description="优先级")
    recipient_ids: List[int] = Field(..., description="接收者ID列表")
    send_email: bool = Field(False, description="是否发送邮件")
    send_sms: bool = Field(False, description="是否发送短信")
    send_push: bool = Field(True, description="是否推送到应用")
    scheduled_at: Optional[datetime] = Field(None, description="预定发送时间")
    expires_at: Optional[datetime] = Field(None, description="过期时间")
