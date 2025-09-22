from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ...db.database import get_db
from ...schemas.coach import CoachResponse, CoachCreate, CoachUpdate
from ...services.coach_service import CoachService
from ...core.deps import get_current_user, get_admin
from ...models.user import User

router = APIRouter()

@router.get("/", response_model=List[CoachResponse], summary="获取教练列表")
def get_coaches(
    campus_id: Optional[int] = None,
    level: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取教练列表"""
    coaches = CoachService.get_coaches(db, campus_id, level, skip, limit)
    return [CoachResponse.from_orm(coach) for coach in coaches]

@router.get("/search", response_model=List[CoachResponse], summary="搜索教练")
def search_coaches(
    name: Optional[str] = None,
    gender: Optional[str] = None,
    age_min: Optional[int] = None,
    age_max: Optional[int] = None,
    campus_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据条件搜索教练"""
    coaches = CoachService.search_coaches(
        db, name, gender, age_min, age_max, campus_id
    )
    return [CoachResponse.from_orm(coach) for coach in coaches]

@router.get("/my-students", summary="获取我的学员列表")
def get_my_students(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前教练的学员列表"""
    from ...models.coach import Coach
    
    # 获取当前用户的教练记录
    coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
    if not coach:
        return []
    
    students = CoachService.get_coach_students(db, coach.id)
    return students

@router.get("/{coach_id}", response_model=CoachResponse, summary="获取教练详情")
def get_coach(
    coach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取教练详情"""
    coach = CoachService.get_coach_by_id(db, coach_id)
    if not coach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="教练不存在"
        )
    return CoachResponse.from_orm(coach)

@router.put("/{coach_id}", response_model=CoachResponse, summary="更新教练信息")
def update_coach(
    coach_id: int,
    coach_data: CoachUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin)
):
    """更新教练信息"""
    coach = CoachService.update_coach(db, coach_id, coach_data, current_user)
    return CoachResponse.from_orm(coach)

@router.post("/{coach_id}/approve", response_model=CoachResponse, summary="审核教练")
def approve_coach(
    coach_id: int,
    approved: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin)
):
    """审核教练申请"""
    coach = CoachService.approve_coach(db, coach_id, approved, current_user)
    return CoachResponse.from_orm(coach)

@router.get("/{coach_id}/students", response_model=List, summary="获取教练的学员列表")
def get_coach_students(
    coach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取教练的学员列表"""
    students = CoachService.get_coach_students(db, coach_id)
    return students

@router.get("/{coach_id}/schedule", response_model=List, summary="获取教练课表")
def get_coach_schedule(
    coach_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取教练课表"""
    schedule = CoachService.get_coach_schedule(db, coach_id, date_from, date_to)
    return schedule
