from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.database import Base

class CourseStatus(enum.Enum):
    """课程状态枚举"""
    SCHEDULED = "scheduled"  # 已安排
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消

class Course(Base):
    """课程表"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False, comment="教练ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学员ID")
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False, comment="校区ID")
    table_number = Column(String(10), nullable=False, comment="球台编号")
    start_time = Column(DateTime(timezone=True), nullable=False, comment="开始时间")
    end_time = Column(DateTime(timezone=True), nullable=False, comment="结束时间")
    duration_hours = Column(Numeric(3, 1), nullable=False, comment="课程时长(小时)")
    hourly_rate = Column(Numeric(10, 2), nullable=False, comment="每小时费用")
    total_cost = Column(Numeric(10, 2), nullable=False, comment="总费用")
    status = Column(String(20), default="scheduled", comment="课程状态")
    notes = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    coach = relationship("Coach", foreign_keys=[coach_id])
    student = relationship("Student", foreign_keys=[student_id])
    campus = relationship("Campus", foreign_keys=[campus_id])
    
    def __repr__(self):
        return f"<Course(id={self.id}, coach={self.coach_id}, student={self.student_id}, status='{self.status}')>"
