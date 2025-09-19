from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .coach import CoachResponse
from .student import StudentResponse

class CoachStudentBase(BaseModel):
    """教练学员关系基础"""
    coach_id: int

class CoachStudentCreate(CoachStudentBase):
    """创建教练学员关系"""
    pass

class CoachStudentUpdate(BaseModel):
    """更新教练学员关系"""
    status: Optional[str] = None

class CoachStudentResponse(CoachStudentBase):
    """教练学员关系响应"""
    id: int
    student_id: int
    status: str
    applied_at: Optional[datetime]
    approved_at: Optional[datetime]
    deleted_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    # 关联信息
    coach: Optional[CoachResponse] = None
    student: Optional[StudentResponse] = None
    
    class Config:
        from_attributes = True
        
    @classmethod
    def from_orm(cls, obj):
        """从ORM对象创建响应对象"""
        data = {
            'id': obj.id,
            'coach_id': obj.coach_id,
            'student_id': obj.student_id,
            'status': obj.status,
            'applied_at': obj.applied_at,
            'approved_at': obj.approved_at,
            'deleted_at': obj.deleted_at,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
            'coach': CoachResponse.from_orm(obj.coach) if obj.coach else None,
            'student': StudentResponse.from_orm(obj.student) if obj.student else None
        }
        
        return cls(**data)
