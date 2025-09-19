from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PaymentBase(BaseModel):
    """支付基础Schema"""
    amount: Decimal
    payment_method: str
    payment_type: str
    related_id: Optional[int] = None
    notes: Optional[str] = None

class PaymentCreate(PaymentBase):
    """支付创建Schema"""
    user_id: int

class PaymentResponse(PaymentBase):
    """支付响应Schema"""
    id: int
    user_id: int
    payment_status: str
    transaction_id: Optional[str] = None
    qr_code_url: Optional[str] = None
    payment_time: Optional[datetime] = None
    refund_time: Optional[datetime] = None
    refund_reason: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PaymentStatusUpdate(BaseModel):
    """支付状态更新Schema"""
    payment_status: str
    transaction_id: Optional[str] = None

class RefundRequest(BaseModel):
    """退款请求Schema"""
    refund_reason: str
