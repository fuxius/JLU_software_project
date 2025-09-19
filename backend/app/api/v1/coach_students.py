from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...db.database import get_db
from ...schemas.coach_student import (
    CoachStudentCreate, 
    CoachStudentResponse, 
    CoachStudentUpdate
)
from ...services.coach_student_service import CoachStudentService
from ...core.deps import get_current_user
from ...models.user import User

router = APIRouter()

@router.post("/", response_model=CoachStudentResponse, summary="学员申请选择教练")
def create_coach_student_relation(
    relation_data: CoachStudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """学员申请选择教练"""
    relation = CoachStudentService.create_relation(db, relation_data, current_user)
    return CoachStudentResponse.from_orm(relation)

@router.get("/student/{student_id}", response_model=List[CoachStudentResponse], summary="获取学员的教练关系")
def get_student_coaches(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取学员的教练关系"""
    relations = CoachStudentService.get_student_relations(db, student_id)
    return [CoachStudentResponse.from_orm(relation) for relation in relations]

@router.get("/coach/{coach_id}", response_model=List[CoachStudentResponse], summary="获取教练的学员关系")
def get_coach_students(
    coach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取教练的学员关系"""
    relations = CoachStudentService.get_coach_relations(db, coach_id)
    return [CoachStudentResponse.from_orm(relation) for relation in relations]

@router.put("/{relation_id}/approve", response_model=CoachStudentResponse, summary="教练审核学员申请")
def approve_student_application(
    relation_id: int,
    approved: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """教练审核学员申请"""
    relation = CoachStudentService.approve_relation(db, relation_id, approved, current_user)
    return CoachStudentResponse.from_orm(relation)

@router.post("/change-coach", summary="申请更换教练")
def request_coach_change(
    student_id: int,
    old_coach_id: int,
    new_coach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """申请更换教练"""
    result = CoachStudentService.request_coach_change(
        db, student_id, old_coach_id, new_coach_id, current_user
    )
    return {"message": "更换教练申请已提交，等待三方确认"}

@router.get("/pending-approvals", response_model=List[CoachStudentResponse], summary="获取待审核申请")
def get_pending_approvals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的待审核申请"""
    relations = CoachStudentService.get_pending_approvals(db, current_user)
    return [CoachStudentResponse.from_orm(relation) for relation in relations]

@router.delete("/{relation_id}", summary="删除教练学员关系")
def delete_coach_student_relation(
    relation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除教练学员关系"""
    success = CoachStudentService.delete_relation(db, relation_id, current_user)
    if success:
        return {"message": "关系删除成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="删除关系失败"
        )
