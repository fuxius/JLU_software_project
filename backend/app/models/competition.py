from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..db.database import Base

class CompetitionGroup(enum.Enum):
    """比赛组别枚举"""
    GROUP_A = "group_a"  # 甲组
    GROUP_B = "group_b"  # 乙组
    GROUP_C = "group_c"  # 丙组

class Competition(Base):
    """比赛表"""
    __tablename__ = "competitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="比赛名称")
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False, comment="举办校区ID")
    competition_date = Column(DateTime(timezone=True), nullable=False, comment="比赛日期")
    registration_fee = Column(Numeric(10, 2), default=30.00, comment="报名费")
    registration_deadline = Column(DateTime(timezone=True), nullable=False, comment="报名截止时间")
    max_participants_per_group = Column(Integer, default=6, comment="每组最大参赛人数")
    status = Column(String(20), default="registration_open", comment="比赛状态")
    description = Column(Text, comment="比赛描述")
    created_by = Column(Integer, ForeignKey("users.id"), comment="创建人ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    campus = relationship("Campus", foreign_keys=[campus_id])
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Competition(id={self.id}, name='{self.name}', date={self.competition_date})>"

class CompetitionRegistration(Base):
    """比赛报名表"""
    __tablename__ = "competition_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False, comment="比赛ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学员ID")
    group_type = Column(String(20), nullable=False, comment="报名组别")
    player_number = Column(Integer, comment="参赛编号")
    table_assignments = Column(Text, comment="球台分配(JSON格式)")
    match_schedule = Column(Text, comment="比赛赛程(JSON格式)")
    payment_id = Column(Integer, ForeignKey("payments.id"), comment="支付记录ID")
    registration_status = Column(String(20), default="registered", comment="报名状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    competition = relationship("Competition", foreign_keys=[competition_id])
    student = relationship("Student", foreign_keys=[student_id])
    payment = relationship("Payment", foreign_keys=[payment_id])
    
    def __repr__(self):
        return f"<CompetitionRegistration(id={self.id}, competition={self.competition_id}, student={self.student_id})>"
