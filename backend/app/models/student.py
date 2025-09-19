from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base

class Student(Base):
    """学员表"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="用户ID")
    account_balance = Column(Numeric(10, 2), default=0.00, comment="账户余额")
    max_coaches = Column(Integer, default=2, comment="最多选择教练数")
    current_coaches = Column(Integer, default=0, comment="当前教练数")
    monthly_cancellations = Column(Integer, default=0, comment="本月取消预约次数")
    last_cancellation_reset = Column(DateTime(timezone=True), comment="上次重置取消次数时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    
    def can_cancel_booking(self):
        """检查是否可以取消预约"""
        return self.monthly_cancellations < 3
    
    def __repr__(self):
        return f"<Student(id={self.id}, balance={self.account_balance}, coaches={self.current_coaches})>"
