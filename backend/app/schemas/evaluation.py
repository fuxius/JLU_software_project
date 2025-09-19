from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EvaluationBase(BaseModel):
    """评价基础Schema"""
    content: str
    rating: Optional[int] = None

class EvaluationCreate(EvaluationBase):
    """评价创建Schema"""
    course_id: int
    evaluator_type: str  # student/coach

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
