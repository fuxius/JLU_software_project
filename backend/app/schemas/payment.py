from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class PaymentBase(BaseModel):
    """支付基础Schema"""
    amount: Decimal
    payment_method: str
    description: Optional[str] = None

class RechargeRequest(BaseModel):
    """充值请求Schema"""
    amount: Decimal
    payment_method: str  # wechat, alipay, offline
    description: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('充值金额必须大于0')
        if v > Decimal('10000'):
            raise ValueError('单次充值金额不能超过10000元')
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in ['wechat', 'alipay', 'offline']:
            raise ValueError('支付方式必须是: wechat, alipay, offline')
        return v

class OfflinePaymentRequest(BaseModel):
    """线下充值请求Schema"""
    user_id: int
    amount: Decimal
    description: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('充值金额必须大于0')
        return v

class PaymentResponse(BaseModel):
    """支付响应Schema"""
    id: int
    user_id: int
    type: str
    amount: Decimal
    payment_method: str
    status: str
    description: Optional[str] = None
    transaction_id: Optional[str] = None
    qr_code_url: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PaymentStatusUpdate(BaseModel):
    """支付状态更新Schema"""
    status: str
    transaction_id: Optional[str] = None

class BalanceResponse(BaseModel):
    """余额响应Schema"""
    user_id: int
    balance: Decimal
    last_updated: datetime

class PaymentSummary(BaseModel):
    """支付汇总Schema"""
    total_recharge: Decimal
    total_expense: Decimal  
    total_refund: Decimal
    current_balance: Decimal
    payment_count: int

class RefundRequest(BaseModel):
    """退款请求Schema"""
    amount: Decimal
    reason: str
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('退款金额必须大于0')
        return v
