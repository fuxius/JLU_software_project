"""
比赛相关的数据模型
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field
from .user import UserResponse
from .student import StudentResponse


class CompetitionBase(BaseModel):
    title: str = Field(..., max_length=200, description="比赛标题")
    description: Optional[str] = Field(None, description="比赛描述")
    competition_date: datetime = Field(..., description="比赛日期")
    registration_deadline: datetime = Field(..., description="报名截止时间")
    registration_fee: Decimal = Field(Decimal("30.00"), description="报名费")
    max_participants: int = Field(32, description="最大参赛人数")
    campus_id: int = Field(..., description="校区ID")


class CompetitionCreate(CompetitionBase):
    pass


class CompetitionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="比赛标题")
    description: Optional[str] = Field(None, description="比赛描述")
    competition_date: Optional[datetime] = Field(None, description="比赛日期")
    registration_deadline: Optional[datetime] = Field(None, description="报名截止时间")
    registration_fee: Optional[Decimal] = Field(None, description="报名费")
    max_participants: Optional[int] = Field(None, description="最大参赛人数")
    status: Optional[str] = Field(None, description="比赛状态")


class CompetitionResponse(CompetitionBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    registered_count: int = Field(0, description="已报名人数")
    
    class Config:
        from_attributes = True


class CompetitionRegistrationBase(BaseModel):
    competition_id: int = Field(..., description="比赛ID")
    group_type: str = Field(..., pattern="^[ABC]$", description="报名组别: A/B/C")


class CompetitionRegistrationCreate(CompetitionRegistrationBase):
    pass


class CompetitionRegistrationResponse(CompetitionRegistrationBase):
    id: int
    student_id: int
    payment_id: Optional[int]
    is_confirmed: bool
    created_at: datetime
    student: Optional[StudentResponse] = None
    competition: Optional[CompetitionResponse] = None
    
    class Config:
        from_attributes = True


class CompetitionMatchBase(BaseModel):
    competition_id: int = Field(..., description="比赛ID")
    group_type: str = Field(..., pattern="^[ABC]$", description="比赛组别")
    round_number: int = Field(..., description="轮次")
    match_number: int = Field(..., description="对阵编号")
    player1_id: Optional[int] = Field(None, description="选手1ID")
    player2_id: Optional[int] = Field(None, description="选手2ID")


class CompetitionMatchCreate(CompetitionMatchBase):
    scheduled_time: Optional[datetime] = Field(None, description="预定比赛时间")
    table_id: Optional[int] = Field(None, description="球台ID")


class CompetitionMatchUpdate(BaseModel):
    player1_score: Optional[int] = Field(None, description="选手1得分")
    player2_score: Optional[int] = Field(None, description="选手2得分")
    winner_id: Optional[int] = Field(None, description="获胜者ID")
    match_status: Optional[str] = Field(None, description="对阵状态")
    actual_start_time: Optional[datetime] = Field(None, description="实际开始时间")
    actual_end_time: Optional[datetime] = Field(None, description="实际结束时间")
    referee_notes: Optional[str] = Field(None, description="裁判备注")


class CompetitionMatchResponse(CompetitionMatchBase):
    id: int
    player1_score: Optional[int]
    player2_score: Optional[int]
    winner_id: Optional[int]
    match_status: str
    scheduled_time: Optional[datetime]
    actual_start_time: Optional[datetime]
    actual_end_time: Optional[datetime]
    table_id: Optional[int]
    referee_notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    player1: Optional[UserResponse] = None
    player2: Optional[UserResponse] = None
    winner: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class CompetitionQuery(BaseModel):
    status: Optional[str] = Field(None, description="比赛状态筛选")
    campus_id: Optional[int] = Field(None, description="校区筛选")
    start_date: Optional[datetime] = Field(None, description="开始日期筛选")
    end_date: Optional[datetime] = Field(None, description="结束日期筛选")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")


class DrawRequest(BaseModel):
    competition_id: int = Field(..., description="比赛ID")
    group_type: str = Field(..., pattern="^[ABC]$", description="组别")


class CompetitionStatistics(BaseModel):
    total_competitions: int = Field(0, description="总比赛数")
    upcoming_competitions: int = Field(0, description="即将开始的比赛数")
    ongoing_competitions: int = Field(0, description="进行中的比赛数")
    completed_competitions: int = Field(0, description="已完成的比赛数")
    total_participants: int = Field(0, description="总参赛人数")
    popular_groups: List[dict] = Field([], description="热门组别统计")