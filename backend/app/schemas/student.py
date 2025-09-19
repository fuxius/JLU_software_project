from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class StudentBase(BaseModel):
    """学员基础Schema"""
    max_coaches: Optional[int] = 2

class StudentCreate(StudentBase):
    """学员创建Schema"""
    user_id: int

class StudentUpdate(BaseModel):
    """学员更新Schema"""
    max_coaches: Optional[int] = None

class StudentResponse(StudentBase):
    """学员响应Schema"""
    id: int
    user_id: int
    account_balance: Decimal
    current_coaches: int
    monthly_cancellations: int
    last_cancellation_reset: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class StudentBalanceUpdate(BaseModel):
    """学员余额更新Schema"""
    amount: Decimal
    operation: str  # add/subtract
