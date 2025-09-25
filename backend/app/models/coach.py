from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.database import Base

class CoachLevel(enum.Enum):
    """教练级别枚举"""
    SENIOR = "senior"  # 高级教练 200元/小时
    INTERMEDIATE = "intermediate"  # 中级教练 150元/小时
    JUNIOR = "junior"  # 初级教练 80元/小时

class Coach(Base):
    """教练表"""
    __tablename__ = "coaches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="用户ID")
    level = Column(Enum(CoachLevel), nullable=False, comment="教练级别")
    hourly_rate = Column(Numeric(10, 2), nullable=False, comment="每小时收费")
    achievements = Column(Text, comment="比赛成绩描述")
    max_students = Column(Integer, default=20, comment="最多指导学员数")
    current_students = Column(Integer, default=0, comment="当前指导学员数")
    approval_status = Column(String(20), default="pending", comment="审核状态")
    approved_by = Column(Integer, ForeignKey("users.id"), comment="审核人ID")
    approved_at = Column(DateTime(timezone=True), comment="审核时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approved_by])
    
    @property
    def hourly_rate_by_level(self):
        """根据级别获取每小时收费"""
        rates = {
            CoachLevel.SENIOR: 200.00,
            CoachLevel.INTERMEDIATE: 150.00,
            CoachLevel.JUNIOR: 80.00
        }
        return rates.get(self.level, 80.00)
    
    def __repr__(self):
        return f"<Coach(id={self.id}, level='{self.level}', rate={self.hourly_rate})>"
