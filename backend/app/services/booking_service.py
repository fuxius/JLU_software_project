from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi import HTTPException, status

from ..models.booking import Booking, BookingStatus
from ..models.user import User, UserRole
from ..models.coach import Coach
from ..models.student import Student
from ..schemas.booking import BookingCreate, BookingUpdate, BookingCancellation
from ..services.system_log_service import SystemLogService
# PaymentService 将在方法中按需导入以避免循环导入

class BookingService:
    """预约服务"""
    
    @staticmethod
    def _to_utc(dt: datetime) -> datetime:
        """将时间统一转换为UTC时区"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @staticmethod
    def create_booking(db: Session, booking_data: BookingCreate, current_user: User) -> Booking:
        """创建课程预约"""
        # 暂时跳过权限检查，允许所有用户预约
        
        # 获取或创建学员记录
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            # 自动创建学员记录
            student = Student(user_id=current_user.id)
            db.add(student)
            db.commit()
            db.refresh(student)
        
        # 暂时跳过双选关系检查，直接允许预约
        # TODO: 后续可以实现完整的双选申请流程
        
        # 获取教练信息
        coach = db.query(Coach).filter(Coach.id == booking_data.coach_id).first()
        if not coach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教练不存在"
            )
        
        # 验证时间冲突
        if BookingService._check_time_conflict(db, booking_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该时间段已有预约冲突"
            )
        
        # 统一将预约时间转换为UTC，避免时区混淆
        now_utc = datetime.now(timezone.utc)
        start_utc = BookingService._to_utc(booking_data.start_time)
        end_utc = BookingService._to_utc(booking_data.end_time)
        if start_utc <= now_utc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能预约过去的时间"
            )
        
        # 验证预约时间（不能超过7天）
        if start_utc > now_utc + timedelta(days=7):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能预约7天内的课程"
            )
        
        # 分配球台
        table_number = booking_data.table_number or BookingService._assign_table(
            db, start_utc, end_utc, booking_data.campus_id
        )
        
        # 计算费用
        total_cost = coach.hourly_rate * booking_data.duration_hours
        
        # 检查学员余额
        from ..services.payment_service import PaymentService
        if not PaymentService.check_balance(db, current_user.id, total_cost):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账户余额不足，请先充值"
            )
        
        # 创建预约
        booking = Booking(
            coach_id=booking_data.coach_id,
            student_id=student.id,
            campus_id=booking_data.campus_id,
            start_time=start_utc,
            end_time=end_utc,
            duration_hours=booking_data.duration_hours,
            table_number=table_number,
            hourly_rate=coach.hourly_rate,
            total_cost=total_cost,
            status=BookingStatus.PENDING.value,
            booking_message=booking_data.booking_message
        )
        
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="booking_create",
            target_type="booking",
            target_id=booking.id,
            description=f"创建预约: {start_utc.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        
        return booking
    
    @staticmethod
    def _check_time_conflict(db: Session, booking_data: BookingCreate) -> bool:
        """检查时间冲突"""
        start_time = BookingService._to_utc(booking_data.start_time)
        end_time = BookingService._to_utc(booking_data.end_time)
        conflicts = db.query(Booking).filter(
            Booking.coach_id == booking_data.coach_id,
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
            Booking.start_time < end_time,
            Booking.end_time > start_time
        ).first()
        
        return conflicts is not None
    
    @staticmethod
    def _assign_table(db: Session, start_time: datetime, end_time: datetime, campus_id: int) -> str:
        """自动分配球台"""
        # 查询该时间段已占用的球台
        start_time = BookingService._to_utc(start_time)
        end_time = BookingService._to_utc(end_time)
        occupied_tables = db.query(Booking.table_number).filter(
            Booking.campus_id == campus_id,
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
            Booking.start_time < end_time,
            Booking.end_time > start_time,
            Booking.table_number.isnot(None)
        ).all()
        
        occupied_set = {table[0] for table in occupied_tables if table[0]}
        
        # 简单的球台分配逻辑（1-20号球台）
        for i in range(1, 21):
            table_num = f"桌{i:02d}"
            if table_num not in occupied_set:
                return table_num
        
        # 如果都被占用，返回None让用户手动选择
        return None
    
    @staticmethod
    def confirm_booking(db: Session, booking_id: int, action: str, current_user: User, message: Optional[str] = None) -> Booking:
        """确认/拒绝预约"""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预约不存在"
            )
        
        # 暂时移除权限检查，允许所有用户确认预约
        
        if booking.status != BookingStatus.PENDING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能确认待审核的预约"
            )
        
        if action == "confirm":
            # 确认预约 - 扣费
            from ..services.payment_service import PaymentService
            if not PaymentService.deduct_balance(db, booking.student.user_id, booking.total_cost, f"课程预约费用 - 预约ID: {booking.id}"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="扣费失败，账户余额不足"
                )
            booking.status = BookingStatus.CONFIRMED.value
        elif action == "reject":
            booking.status = BookingStatus.REJECTED.value
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的操作"
            )
        
        booking.response_message = message
        db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action=f"booking_{action}",
            target_type="booking",
            target_id=booking.id,
            description=f"预约{action}: {booking.start_time.strftime('%Y-%m-%d %H:%M')}"
        )
        
        return booking
    
    @staticmethod
    def cancel_booking(db: Session, booking_id: int, cancellation_data: BookingCancellation, current_user: User) -> Booking:
        """取消预约"""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预约不存在"
            )
        
        # 暂时移除权限检查，允许所有用户取消预约
        
        if booking.status not in [BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该预约无法取消"
            )
        
        # 检查24小时规则（统一时区）
        start_time_utc = BookingService._to_utc(booking.start_time)
        now_utc = datetime.now(timezone.utc)
        if start_time_utc - now_utc < timedelta(hours=24):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="距离上课时间不足24小时，无法取消"
            )
        
        # 检查当月取消次数限制
        if BookingService._check_monthly_cancel_limit(db, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="本月取消次数已达上限（3次）"
            )
        
        # 取消预约
        original_status = booking.status
        booking.status = BookingStatus.CANCELLED.value
        booking.cancelled_by = current_user.id
        booking.cancelled_at = now_utc
        booking.cancellation_reason = cancellation_data.cancellation_reason
        
        # 如果已确认的预约被取消，需要退费
        if original_status == BookingStatus.CONFIRMED.value:
            from ..services.payment_service import PaymentService
            PaymentService.refund_balance(db, booking.student.user_id, booking.total_cost, f"预约取消退费 - 预约ID: {booking.id}")
        
        db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="booking_cancel",
            target_type="booking",
            target_id=booking.id,
            description=f"取消预约: {start_time_utc.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        
        return booking
    
    @staticmethod
    def _check_monthly_cancel_limit(db: Session, user_id: int) -> bool:
        """检查当月取消次数限制"""
        from datetime import date, time
        current_month_start_date = date.today().replace(day=1)
        # 将比较边界设置为UTC的当月起始时间，避免时区导致的筛选误差
        current_month_start = datetime.combine(current_month_start_date, time.min, tzinfo=timezone.utc)
        
        cancel_count = db.query(Booking).filter(
            Booking.cancelled_by == user_id,
            Booking.cancelled_at >= current_month_start,
            Booking.status == BookingStatus.CANCELLED.value
        ).count()
        
        return cancel_count >= 3
    
    @staticmethod
    def get_bookings(db: Session, current_user: User, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Booking]:
        """获取预约列表"""
        from sqlalchemy.orm import joinedload
        
        query = db.query(Booking).options(
            joinedload(Booking.coach).joinedload(Coach.user),
            joinedload(Booking.student).joinedload(Student.user)
        )
        
        # 根据用户角色返回相关预约
        user_role_str = str(current_user.role)
        if user_role_str == "STUDENT" or current_user.role == UserRole.STUDENT:
            # 学员：返回自己的预约
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if student:
                query = query.filter(Booking.student_id == student.id)
            else:
                return []
        elif user_role_str == "COACH" or current_user.role == UserRole.COACH:
            # 教练：返回自己作为教练的预约
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if coach:
                query = query.filter(Booking.coach_id == coach.id)
            else:
                return []
        else:
            # 管理员：返回所有预约（暂时不做校区限制）
            pass
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_booking_by_id(db: Session, booking_id: int, current_user: User) -> Booking:
        """获取预约详情"""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预约不存在"
            )
        
        # 暂时移除权限检查，允许所有用户查看预约详情
        
        return booking
    
    @staticmethod
    def get_coach_schedule(db: Session, coach_id: int, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """获取教练课表"""
        bookings = db.query(Booking).filter(
            Booking.coach_id == coach_id,
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
            Booking.start_time >= date_from,
            Booking.start_time < date_to
        ).all()
        
        schedule = []
        for booking in bookings:
            schedule.append({
                "id": booking.id,
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "table_number": booking.table_number,
                "status": booking.status,
                "student_name": booking.student.user.real_name if booking.student else None
            })
        
        return schedule
    
    @staticmethod
    def get_available_tables(db: Session, campus_id: int, start_time: datetime, end_time: datetime) -> List[str]:
        """获取可用球台"""
        # 查询该时间段已占用的球台
        occupied_tables = db.query(Booking.table_number).filter(
            Booking.campus_id == campus_id,
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
            Booking.start_time < end_time,
            Booking.end_time > start_time,
            Booking.table_number.isnot(None)
        ).all()
        
        occupied_set = {table[0] for table in occupied_tables if table[0]}
        
        # 返回所有可用球台（1-20号球台）
        available_tables = []
        for i in range(1, 21):
            table_num = f"桌{i:02d}"
            if table_num not in occupied_set:
                available_tables.append(table_num)
        
        return available_tables
