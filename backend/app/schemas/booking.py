from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class BookingBase(BaseModel):
    """预约基础Schema"""
    coach_id: int
    student_id: int
    campus_id: int
    start_time: datetime
    end_time: datetime
    duration_hours: Decimal
    booking_message: Optional[str] = None

class BookingCreate(BookingBase):
    """预约创建Schema"""
    table_number: Optional[str] = None

class BookingUpdate(BaseModel):
    """预约更新Schema"""
    status: Optional[str] = None
    response_message: Optional[str] = None
    table_number: Optional[str] = None

class BookingResponse(BookingBase):
    """预约响应Schema"""
    id: int
    table_number: Optional[str] = None
    hourly_rate: Decimal
    total_cost: Decimal
    status: str
    response_message: Optional[str] = None
    cancelled_by: Optional[int] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    cancel_confirmed_by: Optional[int] = None
    cancel_confirmed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class BookingCancellation(BaseModel):
    """预约取消Schema"""
    cancellation_reason: str

class BookingConfirmation(BaseModel):
    """预约确认Schema"""
    action: str  # confirm/reject/cancel_confirm
    message: Optional[str] = None
