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

class StudentResponse(StudentBase):
    """学员响应"""
    id: int
    user_id: int
    balance: float
    coach_count: Optional[int] = 0
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    # 关联的用户信息
    user: UserResponse
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建响应对象"""
        # 计算教练数量
        coach_count = 0
        if hasattr(obj, 'coach_students'):
            coach_count = len([cs for cs in obj.coach_students if cs.status == 'active'])
        
        data = {
            'id': obj.id,
            'user_id': obj.user_id,
            'balance': obj.balance,
            'emergency_contact': obj.emergency_contact,
            'emergency_phone': obj.emergency_phone,
            'coach_count': coach_count,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'user': UserResponse.from_orm(obj.user) if obj.user else None
        }
        
        return cls(**data)