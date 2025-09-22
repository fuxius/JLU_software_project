from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...db.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...schemas.booking import (
    BookingCreate, BookingUpdate, BookingResponse, 
    BookingCancellation, BookingConfirmation
)
from ...services.booking_service import BookingService

router = APIRouter()

@router.post("/", response_model=BookingResponse, summary="创建课程预约")
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建课程预约
    
    - 只有学员可以创建预约
    - 需要与教练建立双选关系
    - 自动检查时间冲突和余额
    - 自动分配球台或手动指定
    """
    booking = BookingService.create_booking(db, booking_data, current_user)
    return BookingResponse.from_orm(booking)

@router.get("/", response_model=List[BookingResponse], summary="获取预约列表")
def get_bookings(
    status: Optional[str] = Query(None, description="预约状态筛选"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取预约列表
    
    - 学员只能看自己的预约
    - 教练只能看自己的预约
    - 校区管理员只能看本校区的预约
    - 超级管理员可以看所有预约
    """
    bookings = BookingService.get_bookings(db, current_user, status, skip, limit)
    # 构造包含教练和学员姓名的响应
    result = []
    for booking in bookings:
        booking_data = BookingResponse.from_orm(booking)
        # 添加教练姓名
        if booking.coach and booking.coach.user:
            booking_data.coach_name = booking.coach.user.real_name
        # 添加学员姓名
        if booking.student and booking.student.user:
            booking_data.student_name = booking.student.user.real_name
        result.append(booking_data)
    return result

@router.get("/{booking_id}", response_model=BookingResponse, summary="获取预约详情")
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取预约详情"""
    booking = BookingService.get_booking_by_id(db, booking_id, current_user)
    return BookingResponse.from_orm(booking)

@router.post("/{booking_id}/confirm", response_model=BookingResponse, summary="确认/拒绝预约")
def confirm_booking(
    booking_id: int,
    confirmation: BookingConfirmation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    确认/拒绝预约
    
    - 教练可以确认自己的预约
    - 管理员可以确认任何预约
    - 确认预约时自动扣费
    """
    booking = BookingService.confirm_booking(
        db, booking_id, confirmation.action, current_user, confirmation.message
    )
    return BookingResponse.from_orm(booking)

@router.post("/{booking_id}/cancel", response_model=BookingResponse, summary="取消预约")
def cancel_booking(
    booking_id: int,
    cancellation: BookingCancellation,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    取消预约
    
    - 学员和教练都可以取消预约
    - 需要提前24小时取消
    - 每月最多取消3次
    - 已确认的预约取消后自动退费
    """
    booking = BookingService.cancel_booking(db, booking_id, cancellation, current_user)
    return BookingResponse.from_orm(booking)

@router.get("/schedule/coach/{coach_id}", summary="获取教练课表")
def get_coach_schedule(
    coach_id: int,
    date_from: datetime = Query(..., description="开始日期"),
    date_to: datetime = Query(..., description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取教练课表
    
    - 显示指定时间范围内的预约安排
    - 包含时间、球台、学员信息
    """
    if (date_to - date_from).days > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="查询时间范围不能超过30天"
        )
    
    schedule = BookingService.get_coach_schedule(db, coach_id, date_from, date_to)
    return {"coach_id": coach_id, "schedule": schedule}

@router.get("/tables/available", summary="获取可用球台")
def get_available_tables(
    campus_id: int = Query(..., description="校区ID"),
    start_time: datetime = Query(..., description="开始时间"),
    end_time: datetime = Query(..., description="结束时间"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定时间段的可用球台
    
    - 用于预约时选择球台
    - 自动排除已被预约的球台
    """
    if end_time <= start_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结束时间必须晚于开始时间"
        )
    
    if (end_time - start_time).total_seconds() > 4 * 3600:  # 4小时
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="单次预约时间不能超过4小时"
        )
    
    available_tables = BookingService.get_available_tables(db, campus_id, start_time, end_time)
    return {
        "campus_id": campus_id,
        "time_range": {
            "start_time": start_time,
            "end_time": end_time
        },
        "available_tables": available_tables
    }

@router.get("/my/pending", response_model=List[BookingResponse], summary="获取我的待处理预约")
def get_my_pending_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的待处理预约
    
    - 学员：待确认的预约
    - 教练：待审核的预约申请
    """
    bookings = BookingService.get_bookings(db, current_user, "pending")
    return [BookingResponse.from_orm(booking) for booking in bookings]

@router.get("/statistics/monthly", summary="获取月度预约统计")
def get_monthly_booking_statistics(
    year: int = Query(..., description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取月度预约统计
    
    - 管理员可以查看校区统计
    - 教练可以查看自己的统计
    - 学员可以查看自己的统计
    """
    # 这里可以添加统计逻辑
    # 暂时返回简单响应
    return {
        "year": year,
        "month": month,
        "message": "统计功能待实现"
    }
