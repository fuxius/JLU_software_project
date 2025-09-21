"""
通知管理API
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.user import User
from ...core.deps import get_current_user
from ...services.notification_service import NotificationService
from ...schemas.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse, NotificationQuery,
    NotificationTemplateCreate, NotificationTemplateUpdate, NotificationTemplateResponse,
    UserNotificationSettingsUpdate, UserNotificationSettingsResponse,
    NotificationStatistics, BulkNotificationCreate
)

router = APIRouter()


@router.post("/", response_model=NotificationResponse, summary="创建通知")
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建通知
    
    - 验证接收者存在性
    - 检查用户通知设置
    - 自动设置发送时间
    """
    notification = NotificationService.create_notification(db, notification_data, current_user)
    return NotificationResponse.from_orm(notification)


@router.post("/bulk", response_model=List[NotificationResponse], summary="批量发送通知")
def create_bulk_notifications(
    bulk_data: BulkNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量发送通知
    
    - 只有管理员可以批量发送
    - 同时发送给多个接收者
    - 自动处理每个用户的通知设置
    """
    notifications = NotificationService.create_bulk_notifications(db, bulk_data, current_user)
    return [NotificationResponse.from_orm(notif) for notif in notifications]


@router.get("/", response_model=List[NotificationResponse], summary="获取通知列表")
def get_notifications(
    type: str = Query(None, description="通知类型筛选"),
    is_read: bool = Query(None, description="是否已读筛选"),
    priority: str = Query(None, description="优先级筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取用户通知列表
    
    - 支持按类型、状态、优先级筛选
    - 支持分页
    - 按创建时间倒序排列
    """
    query = NotificationQuery(
        type=type,
        is_read=is_read,
        priority=priority,
        page=page,
        size=size
    )
    notifications = NotificationService.get_notifications(db, current_user.id, query)
    return [NotificationResponse.from_orm(notif) for notif in notifications]


@router.get("/{notification_id}", response_model=NotificationResponse, summary="获取通知详情")
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取通知详情"""
    notification = NotificationService.get_notification(db, notification_id, current_user.id)
    return NotificationResponse.from_orm(notification)


@router.put("/{notification_id}", response_model=NotificationResponse, summary="更新通知状态")
def update_notification(
    notification_id: int,
    notification_data: NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新通知状态
    
    - 标记已读/未读
    - 软删除通知
    - 自动设置阅读时间
    """
    notification = NotificationService.update_notification(db, notification_id, notification_data, current_user.id)
    return NotificationResponse.from_orm(notification)


@router.post("/{notification_id}/read", response_model=NotificationResponse, summary="标记为已读")
def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记通知为已读"""
    notification = NotificationService.mark_as_read(db, notification_id, current_user.id)
    return NotificationResponse.from_orm(notification)


@router.post("/mark-all-read", summary="标记所有通知为已读")
def mark_all_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    标记所有通知为已读
    
    - 批量更新未读通知
    - 返回更新数量
    """
    updated_count = NotificationService.mark_all_as_read(db, current_user.id)
    return {"message": f"已标记 {updated_count} 条通知为已读"}


@router.delete("/{notification_id}", summary="删除通知")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除通知（软删除）"""
    NotificationService.delete_notification(db, notification_id, current_user.id)
    return {"message": "通知已删除"}


@router.get("/unread/count", summary="获取未读通知数量")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取未读通知数量
    
    - 用于前端显示小红点
    - 实时更新
    """
    count = NotificationService.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.get("/statistics/summary", response_model=NotificationStatistics, summary="获取通知统计")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取通知统计信息
    
    - 总数、已读、未读统计
    - 按类型和优先级分组统计
    """
    return NotificationService.get_statistics(db, current_user.id)


# 用户通知设置相关API
@router.get("/settings/me", response_model=UserNotificationSettingsResponse, summary="获取我的通知设置")
def get_my_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的通知设置"""
    settings = NotificationService.get_user_settings(db, current_user.id)
    return UserNotificationSettingsResponse.from_orm(settings)


@router.put("/settings/me", response_model=UserNotificationSettingsResponse, summary="更新我的通知设置")
def update_my_settings(
    settings_data: UserNotificationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新当前用户的通知设置
    
    - 控制各类通知开关
    - 设置发送方式偏好
    - 配置免打扰时间
    """
    settings = NotificationService.update_user_settings(db, current_user.id, settings_data)
    return UserNotificationSettingsResponse.from_orm(settings)


# 通知模板管理API（管理员专用）
@router.post("/templates", response_model=NotificationTemplateResponse, summary="创建通知模板")
def create_template(
    template_data: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建通知模板
    
    - 只有管理员可以创建
    - 支持变量占位符
    - 设置默认发送方式
    """
    template = NotificationService.create_template(db, template_data, current_user)
    return NotificationTemplateResponse.from_orm(template)


@router.get("/templates", response_model=List[NotificationTemplateResponse], summary="获取通知模板列表")
def get_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取通知模板列表"""
    templates = NotificationService.get_templates(db)
    return [NotificationTemplateResponse.from_orm(template) for template in templates]


@router.post("/templates/{template_code}/send", response_model=NotificationResponse, summary="使用模板发送通知")
def send_from_template(
    template_code: str,
    recipient_id: int = Query(..., description="接收者ID"),
    variables: Dict[str, Any] = {},
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    使用模板发送通知
    
    - 自动渲染模板变量
    - 应用模板默认设置
    - 支持个性化变量替换
    """
    notification = NotificationService.send_from_template(db, template_code, recipient_id, variables, current_user)
    return NotificationResponse.from_orm(notification)
