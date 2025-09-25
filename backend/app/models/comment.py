from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base

class Comment(Base):
    """评论表"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False, comment="关联的预约ID")
    rating = Column(Integer, nullable=False, comment="评分(1-5分)")
    content = Column(String(100), nullable=True, comment="评论内容")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    booking = relationship("Booking", foreign_keys=[booking_id])
    
    def __repr__(self):
        return f"<Comment(id={self.id}, booking_id={self.booking_id}, rating={self.rating})>"
