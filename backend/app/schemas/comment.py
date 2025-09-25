from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    """评论基础schema"""
    rating: int
    content: Optional[str] = None
    
    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('评分必须在1-5分之间')
        return v
    
    @validator('content')
    def validate_content(cls, v):
        if v and len(v) > 100:
            raise ValueError('评论内容不能超过100个字符')
        return v

class CommentCreate(CommentBase):
    """创建评论schema"""
    booking_id: int

class CommentUpdate(CommentBase):
    """更新评论schema"""
    pass

class CommentResponse(CommentBase):
    """评论响应schema"""
    id: int
    booking_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CommentWithBookingInfo(CommentResponse):
    """包含预约信息的评论响应schema"""
    coach_name: Optional[str] = None
    student_name: Optional[str] = None
    booking_start_time: Optional[datetime] = None
    booking_end_time: Optional[datetime] = None
    booking_status: Optional[str] = None

class CoachCommentStats(BaseModel):
    """教练评价统计schema"""
    coach_id: int
    coach_name: str
    total_comments: int
    average_rating: float
    rating_distribution: dict  # {1: 数量, 2: 数量, 3: 数量, 4: 数量, 5: 数量}
    recent_comments: list  # 最近几条评论

class StudentCommentStats(BaseModel):
    """学员评价统计schema"""
    student_id: int
    student_name: str
    total_comments_given: int
    average_rating_given: float
    recent_comments: list  # 最近给出的评论
