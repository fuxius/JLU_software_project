from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...db.database import get_db
from ...core.deps import get_current_user
from ...models.user import User, UserRole
from ...models.coach import Coach
from ...schemas.comment import (
    CommentCreate, CommentUpdate, CommentResponse, 
    CommentWithBookingInfo, CoachCommentStats, StudentCommentStats
)
from ...services.comment_service import CommentService

router = APIRouter()

@router.post("/", response_model=CommentResponse, summary="创建评论")
def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建评论
    
    - 只有学员可以对已完成的预约进行评价
    - 每个预约只能评价一次
    - 评分必须在1-5分之间
    - 评论内容不能超过100个字符
    """
    comment = CommentService.create_comment(db, comment_data, current_user)
    return comment

@router.put("/{comment_id}", response_model=CommentResponse, summary="更新评论")
def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新评论
    
    - 只能更新自己的评论
    - 只能在创建后24小时内修改
    """
    comment = CommentService.update_comment(db, comment_id, comment_data, current_user)
    return comment

@router.delete("/{comment_id}", summary="删除评论")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除评论
    
    - 只能删除自己的评论
    - 管理员可以删除任何评论
    """
    result = CommentService.delete_comment(db, comment_id, current_user)
    return {"message": "评论删除成功"}

@router.get("/{comment_id}", response_model=CommentResponse, summary="获取评论详情")
def get_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取评论详情
    
    - 学员只能查看自己的评论
    - 教练只能查看自己的评论
    - 管理员可以查看所有评论
    """
    comment = CommentService.get_comment_by_id(db, comment_id, current_user)
    return comment

@router.get("/coach/{coach_id}", response_model=List[CommentWithBookingInfo], summary="获取教练的评论列表")
def get_comments_by_coach(
    coach_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取教练的评论列表
    
    - 教练只能查看自己的评论
    - 管理员可以查看所有教练的评论
    - 包含预约信息和学员信息
    """
    comments = CommentService.get_comments_by_coach(db, coach_id, current_user, skip, limit)
    return comments

@router.get("/student/{student_id}", response_model=List[CommentWithBookingInfo], summary="获取学员的评论列表")
def get_comments_by_student(
    student_id: int,
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取学员的评论列表
    
    - 学员只能查看自己的评论
    - 管理员可以查看所有学员的评论
    - 包含预约信息和教练信息
    """
    comments = CommentService.get_comments_by_student(db, student_id, current_user, skip, limit)
    return comments

@router.get("/coach/{coach_id}/stats", response_model=CoachCommentStats, summary="获取教练评价统计")
def get_coach_comment_stats(
    coach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取教练评价统计
    
    - 教练只能查看自己的统计信息
    - 管理员可以查看所有教练的统计信息
    - 包含总评论数、平均评分、评分分布、最近评论
    """
    stats = CommentService.get_coach_comment_stats(db, coach_id, current_user)
    return stats

@router.get("/student/{student_id}/stats", response_model=StudentCommentStats, summary="获取学员评价统计")
def get_student_comment_stats(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取学员评价统计
    
    - 学员只能查看自己的统计信息
    - 管理员可以查看所有学员的统计信息
    - 包含总评论数、平均评分、最近评论
    """
    stats = CommentService.get_student_comment_stats(db, student_id, current_user)
    return stats

@router.get("/my/comments", response_model=List[CommentWithBookingInfo], summary="获取我的评论")
def get_my_comments(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的评论
    
    - 学员：获取自己给出的评论
    - 教练：获取自己收到的评论
    - 管理员：获取所有评论（需要指定教练或学员ID）
    """
    if current_user.role == UserRole.STUDENT:
        comments = CommentService.get_comments_by_student(db, current_user.id, current_user, skip, limit)
    elif current_user.role == UserRole.COACH:
        # 教练用户需要先获取对应的 coach_id
        coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
        if not coach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教练信息不存在"
            )
        comments = CommentService.get_comments_by_coach(db, coach.id, current_user, skip, limit)
    else:
        # 管理员需要指定具体的教练或学员ID
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理员请使用具体的教练或学员ID接口"
        )
    
    return comments

@router.get("/my/stats", summary="获取我的评价统计")
def get_my_comment_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的评价统计
    
    - 学员：获取自己给出的评价统计
    - 教练：获取自己收到的评价统计
    """
    if current_user.role == UserRole.STUDENT:
        stats = CommentService.get_student_comment_stats(db, current_user.id, current_user)
    elif current_user.role == UserRole.COACH:
        # 教练用户需要先获取对应的 coach_id
        coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
        if not coach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教练信息不存在"
            )
        stats = CommentService.get_coach_comment_stats(db, coach.id, current_user)
    else:
        # 管理员需要指定具体的教练或学员ID
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="管理员请使用具体的教练或学员统计接口"
        )
    
    return stats

@router.get("/booking/{booking_id}", response_model=CommentResponse, summary="获取预约的评论")
def get_comment_by_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定预约的评论
    
    - 学员只能查看自己预约的评论
    - 教练只能查看自己预约的评论
    - 管理员可以查看所有预约的评论
    """
    # 检查预约是否存在
    from ...models.booking import Booking
    from ...models.comment import Comment
    from ...models.student import Student
    
    # 联合查询 booking 和 student 表，获取对应的 user_id
    booking_with_user = (
        db.query(Booking, Student.user_id)
        .join(Student, Booking.student_id == Student.id)
        .filter(Booking.id == booking_id)
        .first()
    )
    
    if not booking_with_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="预约不存在"
        )
    
    booking, student_user_id = booking_with_user
    
    # 检查权限（学生：比较 user_id）
    if current_user.role == UserRole.STUDENT and student_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限查看此预约的评论"
        )
    elif current_user.role == UserRole.COACH:
        coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
        if not coach or booking.coach_id != coach.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看此预约的评论"
            )

    # 查找评论
    comment = db.query(Comment).filter(Comment.booking_id == booking_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该预约暂无评论"
        )
    
    return comment
