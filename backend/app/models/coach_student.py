from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base

class CoachStudent(Base):
    """教练学员双选关系表"""
    __tablename__ = "coach_students"
    
    id = Column(Integer, primary_key=True, index=True)
    coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False, comment="教练ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学员ID")
    status = Column(String(20), default="pending", comment="申请状态: pending/approved/rejected")
    applied_by = Column(String(20), nullable=False, comment="申请发起方: student/admin")
    application_message = Column(Text, comment="申请留言")
    response_message = Column(Text, comment="回复留言")
    responded_by = Column(Integer, ForeignKey("users.id"), comment="回复人ID")
    responded_at = Column(DateTime(timezone=True), comment="回复时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    coach = relationship("Coach", foreign_keys=[coach_id])
    student = relationship("Student", foreign_keys=[student_id])
    responder = relationship("User", foreign_keys=[responded_by])
    
    def __repr__(self):
        return f"<CoachStudent(id={self.id}, coach={self.coach_id}, student={self.student_id}, status='{self.status}')>"
