from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.database import Base

class PaymentMethod(enum.Enum):
    """支付方式枚举"""
    WECHAT = "wechat"  # 微信支付
    ALIPAY = "alipay"  # 支付宝
    OFFLINE = "offline"  # 线下支付

class PaymentStatus(enum.Enum):
    """支付状态枚举"""
    PENDING = "pending"  # 待支付
    COMPLETED = "completed"  # 支付完成
    FAILED = "failed"  # 支付失败
    REFUNDED = "refunded"  # 已退款

class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    amount = Column(Numeric(10, 2), nullable=False, comment="金额")
    payment_method = Column(String(20), nullable=False, comment="支付方式")
    payment_status = Column(String(20), default="pending", comment="支付状态")
    transaction_id = Column(String(100), comment="交易ID")
    payment_type = Column(String(20), nullable=False, comment="支付类型: recharge/course/competition/license")
    related_id = Column(Integer, comment="关联ID(课程ID/比赛ID等)")
    qr_code_url = Column(String(255), comment="支付二维码URL")
    payment_time = Column(DateTime(timezone=True), comment="支付时间")
    refund_time = Column(DateTime(timezone=True), comment="退款时间")
    refund_reason = Column(Text, comment="退款原因")
    notes = Column(Text, comment="备注")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID(线下支付时)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Payment(id={self.id}, user={self.user_id}, amount={self.amount}, status='{self.payment_status}')>"
