from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

from .user import UserResponse

class CoachLevelEnum(str, Enum):
    """教练级别枚举"""
    SENIOR = "senior"
    INTERMEDIATE = "intermediate" 
    JUNIOR = "junior"

class CoachBase(BaseModel):
    """教练基础信息"""
    level: CoachLevelEnum
    hourly_rate: float
    achievements: Optional[str] = None

class CoachCreate(CoachBase):
    """创建教练"""
    pass

class CoachUpdate(BaseModel):
    """更新教练信息"""
    level: Optional[CoachLevelEnum] = None
    hourly_rate: Optional[float] = None
    achievements: Optional[str] = None
    approval_status: Optional[str] = None

class CoachResponse(CoachBase):
    """教练响应"""
    id: int
    user_id: int
    approval_status: str
    student_count: Optional[int] = 0
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    # 关联的用户信息
    user: UserResponse
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建响应对象"""
        # 计算学员数量
        student_count = 0
        if hasattr(obj, 'coach_students'):
            student_count = len([cs for cs in obj.coach_students if cs.status == 'active'])
        
        data = {
            'id': obj.id,
            'user_id': obj.user_id,
            'level': obj.level,
            'hourly_rate': obj.hourly_rate,
            'achievements': obj.achievements,
            'approval_status': obj.approval_status,
            'student_count': student_count,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'user': UserResponse.from_orm(obj.user) if obj.user else None
        }
        
        return cls(**data)

class CoachSearchRequest(BaseModel):
    """教练搜索请求"""
    name: Optional[str] = None
    gender: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    level: Optional[CoachLevelEnum] = None
    campus_id: Optional[int] = None