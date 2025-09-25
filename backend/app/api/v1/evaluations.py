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
    evaluation = EvaluationService.create_evaluation(db, evaluation_data, current_user)
    return EvaluationResponse.from_orm(evaluation)

@router.get("/", response_model=List[EvaluationResponse], summary="获取评价列表")
def get_evaluations(
    course_id: Optional[int] = Query(None, description="课程ID筛选"),
    evaluator_type: Optional[str] = Query(None, description="评价人类型筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取评价列表
    
    - 不再进行权限限制，返回所有符合条件的评价
    """
    evaluations = EvaluationService.get_evaluations(
        db, current_user, course_id, evaluator_type, skip, limit
    )
    return [EvaluationResponse.from_orm(evaluation) for evaluation in evaluations]

@router.get("/{evaluation_id}", response_model=EvaluationResponse, summary="获取评价详情")
def get_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取评价详情"""
    evaluation = EvaluationService.get_evaluation_by_id(db, evaluation_id, current_user)
    return EvaluationResponse.from_orm(evaluation)

@router.put("/{evaluation_id}", response_model=EvaluationResponse, summary="更新评价")
def update_evaluation(
    evaluation_id: int,
    evaluation_data: EvaluationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新评价
    
    - 不再限制评价创建者或时间
    """
    evaluation = EvaluationService.update_evaluation(
        db, evaluation_id, evaluation_data, current_user
    )
    return EvaluationResponse.from_orm(evaluation)

@router.delete("/{evaluation_id}", summary="删除评价")
def delete_evaluation(
    evaluation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除评价"""
    success = EvaluationService.delete_evaluation(db, evaluation_id, current_user)
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定课程的所有评价"""
    evaluations = EvaluationService.get_course_evaluations(db, course_id, current_user)
    return [EvaluationResponse.from_orm(evaluation) for evaluation in evaluations]

@router.get("/pending/my", response_model=List, summary="获取我的待评价课程")
def get_my_pending_evaluations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的待评价课程
    
    - 返回已完成但未评价的课程列表
    """
    pending_courses = EvaluationService.get_pending_evaluations(db, current_user)
    return pending_courses

@router.get("/statistics/summary", summary="获取评价统计")
def get_evaluation_statistics(
    user_id: Optional[int] = Query(None, description="用户ID（管理员可指定）"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取评价统计信息
    
    - 普通用户只能查看自己的统计
    - 管理员可以查看所有用户的统计
    """
    target_user_id = user_id if user_id and current_user.role in [
        UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN
    ] else current_user.id
    
    statistics = EvaluationService.get_evaluation_statistics(db, target_user_id)
    return statistics

@router.get("/coach/{coach_id}/summary", summary="获取教练评价汇总")
def get_coach_evaluation_summary(
    coach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取教练的评价汇总信息"""
    summary = EvaluationService.get_coach_evaluation_summary(db, coach_id)
    return summary
