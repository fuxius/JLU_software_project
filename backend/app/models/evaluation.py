from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base

class Evaluation(Base):
    """课后评价表"""
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, comment="课程ID")
    evaluator_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="评价人ID")
    evaluator_type = Column(String(20), nullable=False, comment="评价人类型: student/coach")
    content = Column(Text, nullable=False, comment="评价内容")
    rating = Column(Integer, comment="评分(1-5)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    course = relationship("Course", foreign_keys=[course_id])
    evaluator = relationship("User", foreign_keys=[evaluator_id])
    
    def __repr__(self):
        return f"<Evaluation(id={self.id}, course={self.course_id}, evaluator={self.evaluator_id})>"
