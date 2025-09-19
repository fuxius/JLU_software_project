from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from ..models.coach import CoachLevel

class CoachBase(BaseModel):
    """教练基础Schema"""
    level: CoachLevel
    achievements: Optional[str] = None
    max_students: Optional[int] = 20

class CoachCreate(CoachBase):
    """教练创建Schema"""
    user_id: int

class CoachUpdate(BaseModel):
    """教练更新Schema"""
    level: Optional[CoachLevel] = None
    achievements: Optional[str] = None
    max_students: Optional[int] = None
    approval_status: Optional[str] = None

class CoachResponse(CoachBase):
    """教练响应Schema"""
    id: int
    user_id: int
    hourly_rate: Decimal
    current_students: int
    approval_status: str
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CoachApproval(BaseModel):
    """教练审核Schema"""
    approval_status: str  # approved/rejected
    level: CoachLevel
    response_message: Optional[str] = None
