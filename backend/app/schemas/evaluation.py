from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EvaluationBase(BaseModel):
    """评价基础Schema"""
    content: str = Field(..., min_length=1, max_length=2000, description="评价内容")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分(1-5)")

class EvaluationCreate(EvaluationBase):
    """评价创建Schema"""
    course_id: int = Field(..., description="课程ID")

class EvaluationUpdate(BaseModel):
    """评价更新Schema"""
    content: Optional[str] = Field(None, min_length=1, max_length=2000, description="评价内容")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分(1-5)")

class EvaluationResponse(EvaluationBase):
    """评价响应Schema"""
    id: int
    course_id: int
    evaluator_id: int
    evaluator_type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EvaluationSummary(BaseModel):
    """评价汇总Schema"""
    total_evaluations: int
    average_rating: float
    rating_distribution: dict
    recent_evaluations: int

class PendingEvaluationCourse(BaseModel):
    """待评价课程Schema"""
    course_id: int
    booking_id: int
    completed_at: Optional[datetime]
    booking: dict
