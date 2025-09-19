from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.database import Base

class BookingStatus(enum.Enum):
    """预约状态枚举"""
    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    REJECTED = "rejected"  # 已拒绝
    CANCELLED = "cancelled"  # 已取消
    COMPLETED = "completed"  # 已完成

class Booking(Base):
    """预约表"""
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False, comment="教练ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学员ID")
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False, comment="校区ID")
    table_number = Column(String(10), comment="球台编号")
    start_time = Column(DateTime(timezone=True), nullable=False, comment="开始时间")
    end_time = Column(DateTime(timezone=True), nullable=False, comment="结束时间")
    duration_hours = Column(Numeric(3, 1), nullable=False, comment="预约时长(小时)")
    hourly_rate = Column(Numeric(10, 2), nullable=False, comment="每小时费用")
    total_cost = Column(Numeric(10, 2), nullable=False, comment="总费用")
    status = Column(String(20), default="pending", comment="预约状态")
    booking_message = Column(Text, comment="预约留言")
    response_message = Column(Text, comment="回复留言")
    cancelled_by = Column(Integer, ForeignKey("users.id"), comment="取消发起人ID")
    cancelled_at = Column(DateTime(timezone=True), comment="取消时间")
    cancellation_reason = Column(Text, comment="取消原因")
    cancel_confirmed_by = Column(Integer, ForeignKey("users.id"), comment="取消确认人ID")
    cancel_confirmed_at = Column(DateTime(timezone=True), comment="取消确认时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系 - 使用字符串引用避免循环导入
    coach = relationship("Coach", foreign_keys=[coach_id])
    student = relationship("Student", foreign_keys=[student_id])  
    campus = relationship("Campus", foreign_keys=[campus_id])
    canceller = relationship("User", foreign_keys=[cancelled_by])
    cancel_confirmer = relationship("User", foreign_keys=[cancel_confirmed_by])
    
    def can_cancel(self):
        """检查是否可以取消(24小时前)"""
        from datetime import datetime, timedelta
        now = datetime.now()
        return (self.start_time - now) >= timedelta(hours=24)
    
    def __repr__(self):
        return f"<Booking(id={self.id}, coach={self.coach_id}, student={self.student_id}, status='{self.status}')>"
