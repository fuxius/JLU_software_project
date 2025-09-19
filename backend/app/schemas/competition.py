from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class CompetitionBase(BaseModel):
    """比赛基础Schema"""
    name: str
    campus_id: int
    competition_date: datetime
    registration_deadline: datetime
    registration_fee: Optional[Decimal] = Decimal("30.00")
    max_participants_per_group: Optional[int] = 6
    description: Optional[str] = None

class CompetitionCreate(CompetitionBase):
    """比赛创建Schema"""
    pass

class CompetitionResponse(CompetitionBase):
    """比赛响应Schema"""
    id: int
    status: str
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CompetitionRegistrationBase(BaseModel):
    """比赛报名基础Schema"""
    competition_id: int
    group_type: str  # group_a/group_b/group_c

class CompetitionRegistrationCreate(CompetitionRegistrationBase):
    """比赛报名创建Schema"""
    pass

class CompetitionRegistrationResponse(CompetitionRegistrationBase):
    """比赛报名响应Schema"""
    id: int
    student_id: int
    player_number: Optional[int] = None
    table_assignments: Optional[str] = None
    match_schedule: Optional[str] = None
    payment_id: Optional[int] = None
    registration_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MatchSchedule(BaseModel):
    """比赛赛程Schema"""
    round: int
    player1: int
    player2: Optional[int] = None  # None表示轮空
    table_number: str
    scheduled_time: datetime

class GroupScheduleResponse(BaseModel):
    """组别赛程响应Schema"""
    group_type: str
    participants: List[dict]
    schedule: List[MatchSchedule]
