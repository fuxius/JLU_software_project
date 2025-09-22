from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .user import UserResponse

class StudentBase(BaseModel):
    """学员基础信息"""
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None

class StudentCreate(StudentBase):
    """创建学员"""
    pass

class StudentUpdate(BaseModel):
    """更新学员信息"""
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None

class StudentResponse(BaseModel):
    """学员响应"""
    id: int
    user_id: int
    account_balance: float
    max_coaches: int = 2
    current_coaches: int = 0
    monthly_cancellations: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # 关联的用户信息
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True