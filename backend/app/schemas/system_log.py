from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SystemLogResponse(BaseModel):
    """系统日志响应Schema"""
    id: int
    user_id: Optional[int] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    description: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    extra_data: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class SystemLogQuery(BaseModel):
    """系统日志查询Schema"""
    action: Optional[str] = None
    user_id: Optional[int] = None
    target_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100

class SystemLogCreate(BaseModel):
    """系统日志创建Schema"""
    user_id: Optional[int] = None
    action: str
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    description: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    extra_data: Optional[str] = None
