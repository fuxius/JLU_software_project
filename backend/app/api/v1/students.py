from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ...db.database import get_db
from ...schemas.student import StudentResponse, StudentUpdate
from ...services.student_service import StudentService
from ...core.deps import get_current_user, get_admin
from ...models.user import User

router = APIRouter()

@router.get("/", response_model=List[StudentResponse], summary="获取学员列表")
def get_students(
    campus_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin)
):
    """获取学员列表"""
    students = StudentService.get_students(db, campus_id, skip, limit)
    return [StudentResponse.from_orm(student) for student in students]

@router.get("/me", response_model=StudentResponse, summary="获取当前学员信息")
def get_current_student(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取当前学员信息"""
    student = StudentService.get_student_by_user_id(db, current_user.id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学员信息不存在"
        )
    return StudentResponse.from_orm(student)

@router.get("/{student_id}", response_model=StudentResponse, summary="获取学员详情")
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取学员详情"""
    student = StudentService.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="学员不存在"
        )
    return StudentResponse.from_orm(student)

@router.put("/{student_id}", response_model=StudentResponse, summary="更新学员信息")
def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin)
):
    """更新学员信息"""
    student = StudentService.update_student(db, student_id, student_data, current_user)
    return StudentResponse.from_orm(student)

@router.get("/{student_id}/coaches", response_model=List, summary="获取学员的教练列表")
def get_student_coaches(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取学员的教练列表"""
    coaches = StudentService.get_student_coaches(db, student_id)
    return coaches

@router.get("/{student_id}/bookings", response_model=List, summary="获取学员预约记录")
def get_student_bookings(
    student_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取学员预约记录"""
    bookings = StudentService.get_student_bookings(db, student_id, status)
    return bookings

@router.get("/{student_id}/balance", summary="获取学员账户余额")
def get_student_balance(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取学员账户余额"""
    balance = StudentService.get_student_balance(db, student_id)
    return {"balance": balance}
