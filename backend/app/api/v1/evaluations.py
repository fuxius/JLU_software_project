from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...db.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...schemas.evaluation import (
    EvaluationCreate, EvaluationUpdate, EvaluationResponse
)
from ...services.evaluation_service import EvaluationService

router = APIRouter()

@router.post("/", response_model=EvaluationResponse, summary="创建课后评价")
def create_evaluation(
    evaluation_data: EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建课后评价
    
    - 学员和教练都可以评价
    - 每个课程每个用户只能评价一次
    - 只能评价已完成的课程
    """
    evaluation = EvaluationService.create_evaluation(db, evaluation_data)
    return EvaluationResponse.from_orm(evaluation)

@router.get("/", response_model=List[EvaluationResponse], summary="获取评价列表")
def get_evaluations(
    course_id: Optional[int] = Query(None, description="课程ID筛选"),
    evaluator_type: Optional[str] = Query(None, description="评价人类型筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """
    获取评价列表
    
    - 无权限限制
    """
    evaluations = EvaluationService.get_evaluations(
        db, course_id, evaluator_type, skip, limit
    )
    return [EvaluationResponse.from_orm(evaluation) for evaluation in evaluations]

@router.get("/{evaluation_id}", response_model=EvaluationResponse, summary="获取评价详情")
def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """获取评价详情"""
    evaluation = EvaluationService.get_evaluation_by_id(db, evaluation_id)
    return EvaluationResponse.from_orm(evaluation)

@router.put("/{evaluation_id}", response_model=EvaluationResponse, summary="更新评价")
def update_evaluation(
    evaluation_id: int,
    evaluation_data: EvaluationUpdate,
    db: Session = Depends(get_db)
):
    """
    更新评价
    
    - 无权限限制
    """
    evaluation = EvaluationService.update_evaluation(
        db, evaluation_id, evaluation_data
    )
    return EvaluationResponse.from_orm(evaluation)

@router.delete("/{evaluation_id}", summary="删除评价")
def delete_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db)
):
    """删除评价"""
    success = EvaluationService.delete_evaluation(db, evaluation_id)
    if success:
        return {"message": "评价删除成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="删除评价失败"
        )

@router.get("/course/{course_id}", response_model=List[EvaluationResponse], summary="获取课程的所有评价")
def get_course_evaluations(
    course_id: int,
    db: Session = Depends(get_db)
):
    """获取指定课程的所有评价"""
    evaluations = EvaluationService.get_course_evaluations(db, course_id)
    return [EvaluationResponse.from_orm(evaluation) for evaluation in evaluations]

@router.get("/pending/my", response_model=List, summary="获取待评价课程")
def get_pending_evaluations(
    db: Session = Depends(get_db)
):
    """
    获取待评价课程
    
    - 返回已完成但未评价的课程列表
    """
    pending_courses = EvaluationService.get_pending_evaluations(db)
    return pending_courses

@router.get("/statistics/summary", summary="获取评价统计")
def get_evaluation_statistics(
    user_id: Optional[int] = Query(None, description="用户ID"),
    db: Session = Depends(get_db)
):
    """
    获取评价统计信息
    
    - 无权限限制
    """
    target_user_id = user_id if user_id else 1  # 默认用户ID为1
    
    statistics = EvaluationService.get_evaluation_statistics(db, target_user_id)
    return statistics

@router.get("/coach/{coach_id}/summary", summary="获取教练评价汇总")
def get_coach_evaluation_summary(
    coach_id: int,
    db: Session = Depends(get_db)
):
    """获取教练的评价汇总信息"""
    summary = EvaluationService.get_coach_evaluation_summary(db, coach_id)
    return summary
