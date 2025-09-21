"""
比赛相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class CompetitionStatus(enum.Enum):
    """比赛状态"""
    UPCOMING = "upcoming"      # 即将开始
    REGISTRATION = "registration"  # 报名中
    DRAW_COMPLETE = "draw_complete"  # 抽签完成
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"    # 已结束
    CANCELLED = "cancelled"    # 已取消


class CompetitionGroup(enum.Enum):
    """比赛组别"""
    GROUP_A = "A"  # 甲组
    GROUP_B = "B"  # 乙组
    GROUP_C = "C"  # 丙组


class Competition(Base):
    """比赛表"""
    __tablename__ = "competitions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, comment="比赛标题")
    description = Column(Text, comment="比赛描述")
    competition_date = Column(DateTime(timezone=True), nullable=False, comment="比赛日期")
    registration_deadline = Column(DateTime(timezone=True), nullable=False, comment="报名截止时间")
    registration_fee = Column(Numeric(10, 2), default=30.00, comment="报名费")
    max_participants = Column(Integer, default=32, comment="最大参赛人数")
    status = Column(String(20), default=CompetitionStatus.UPCOMING.value, comment="比赛状态")
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False, comment="校区ID")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    campus = relationship("Campus", back_populates="competitions")
    registrations = relationship("CompetitionRegistration", back_populates="competition")
    matches = relationship("CompetitionMatch", back_populates="competition")


class CompetitionRegistration(Base):
    """比赛报名表"""
    __tablename__ = "competition_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False, comment="比赛ID")
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, comment="学员ID")
    group_type = Column(String(1), nullable=False, comment="报名组别")
    payment_id = Column(Integer, ForeignKey("payments.id"), comment="支付记录ID")
    is_confirmed = Column(Boolean, default=False, comment="是否确认参赛")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="报名时间")
    
    # 关系
    competition = relationship("Competition", back_populates="registrations")
    student = relationship("Student")
    payment = relationship("Payment")


class CompetitionMatch(Base):
    """比赛对阵表"""
    __tablename__ = "competition_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    competition_id = Column(Integer, ForeignKey("competitions.id"), nullable=False, comment="比赛ID")
    group_type = Column(String(1), nullable=False, comment="比赛组别")
    round_number = Column(Integer, nullable=False, comment="轮次")
    match_number = Column(Integer, nullable=False, comment="对阵编号")
    
    player1_id = Column(Integer, ForeignKey("students.id"), comment="选手1ID")
    player2_id = Column(Integer, ForeignKey("students.id"), comment="选手2ID")
    
    # 比赛结果
    player1_score = Column(Integer, comment="选手1得分")
    player2_score = Column(Integer, comment="选手2得分")
    winner_id = Column(Integer, ForeignKey("students.id"), comment="获胜者ID")
    
    # 比赛状态
    match_status = Column(String(20), default="pending", comment="对阵状态: pending/completed/cancelled")
    scheduled_time = Column(DateTime(timezone=True), comment="预定比赛时间")
    actual_start_time = Column(DateTime(timezone=True), comment="实际开始时间")
    actual_end_time = Column(DateTime(timezone=True), comment="实际结束时间")
    
    table_id = Column(Integer, ForeignKey("tables.id"), comment="球台ID")
    referee_notes = Column(Text, comment="裁判备注")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    competition = relationship("Competition", back_populates="matches")
    player1 = relationship("Student", foreign_keys=[player1_id])
    player2 = relationship("Student", foreign_keys=[player2_id])
    winner = relationship("Student", foreign_keys=[winner_id])
    table = relationship("Table")