from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
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
    def create_booking(db: Session, booking_data: BookingCreate, current_user: User) -> Booking:
        """创建课程预约"""
        # 验证用户权限（只有学员可以预约）
        if current_user.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学员可以创建预约"
            )
        
        # 验证学员和教练关系
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学员信息不存在"
            )
        
        # 检查教练学员关系
        from ..models.coach_student import CoachStudent
        relation = db.query(CoachStudent).filter(
            CoachStudent.coach_id == booking_data.coach_id,
            CoachStudent.student_id == student.id,
            CoachStudent.status == "approved"
        ).first()
        
        if not relation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您与该教练没有建立双选关系"
            )
        
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
        
        # 验证预约时间（不能预约过去的时间）
        if booking_data.start_time <= datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能预约过去的时间"
            )
        
        # 验证预约时间（不能超过7天）
        if booking_data.start_time > datetime.now() + timedelta(days=7):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能预约7天内的课程"
            )
        
        # 分配球台
        table_number = booking_data.table_number or BookingService._assign_table(
            db, booking_data.start_time, booking_data.end_time, booking_data.campus_id
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
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            duration_hours=booking_data.duration_hours,
            table_number=table_number,
            hourly_rate=coach.hourly_rate,
            total_cost=total_cost,
            status=BookingStatus.PENDING,
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
            description=f"创建预约: {booking_data.start_time.strftime('%Y-%m-%d %H:%M')}"
        )
        
        return booking
    
    @staticmethod
    def _check_time_conflict(db: Session, booking_data: BookingCreate) -> bool:
        """检查时间冲突"""
        conflicts = db.query(Booking).filter(
            Booking.coach_id == booking_data.coach_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
            Booking.start_time < booking_data.end_time,
            Booking.end_time > booking_data.start_time
        ).first()
        
        return conflicts is not None
    
    @staticmethod
    def _assign_table(db: Session, start_time: datetime, end_time: datetime, campus_id: int) -> str:
        """自动分配球台"""
        # 查询该时间段已占用的球台
        occupied_tables = db.query(Booking.table_number).filter(
            Booking.campus_id == campus_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
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
        
        # 验证权限（教练可以确认自己的预约）
        if current_user.role == UserRole.COACH:
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if not coach or booking.coach_id != coach.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能确认自己的预约"
                )
        elif current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        if booking.status != BookingStatus.PENDING:
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
            booking.status = BookingStatus.CONFIRMED
        elif action == "reject":
            booking.status = BookingStatus.REJECTED
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
        
        # 验证权限（学员和教练都可以取消）
        can_cancel = False
        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if student and booking.student_id == student.id:
                can_cancel = True
        elif current_user.role == UserRole.COACH:
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if coach and booking.coach_id == coach.id:
                can_cancel = True
        elif current_user.role in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            can_cancel = True
        
        if not can_cancel:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只能取消自己的预约"
            )
        
        if booking.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该预约无法取消"
            )
        
        # 检查24小时规则
        if booking.start_time - datetime.now() < timedelta(hours=24):
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
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_by = current_user.id
        booking.cancelled_at = datetime.now()
        booking.cancellation_reason = cancellation_data.cancellation_reason
        
        # 如果已确认的预约被取消，需要退费
        if booking.status == BookingStatus.CONFIRMED:
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
            description=f"取消预约: {booking.start_time.strftime('%Y-%m-%d %H:%M')}"
        )
        
        return booking
    
    @staticmethod
    def _check_monthly_cancel_limit(db: Session, user_id: int) -> bool:
        """检查当月取消次数限制"""
        from datetime import date
        current_month_start = date.today().replace(day=1)
        
        cancel_count = db.query(Booking).filter(
            Booking.cancelled_by == user_id,
            Booking.cancelled_at >= current_month_start,
            Booking.status == BookingStatus.CANCELLED
        ).count()
        
        return cancel_count >= 3
    
    @staticmethod
    def get_bookings(db: Session, current_user: User, status: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Booking]:
        """获取预约列表"""
        query = db.query(Booking)
        
        # 根据用户角色过滤
        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if student:
                query = query.filter(Booking.student_id == student.id)
            else:
                # 学员用户但暂未建立student扩展记录，返回空列表而不是403
                return []
        elif current_user.role == UserRole.COACH:
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if coach:
                query = query.filter(Booking.coach_id == coach.id)
        elif current_user.role == UserRole.CAMPUS_ADMIN:
            # 校区管理员只能看自己校区的预约
            query = query.filter(Booking.campus_id == current_user.campus_id)
        # SUPER_ADMIN 可以看所有预约
        
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
        
        # 验证权限
        can_view = False
        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if student and booking.student_id == student.id:
                can_view = True
        elif current_user.role == UserRole.COACH:
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if coach and booking.coach_id == coach.id:
                can_view = True
        elif current_user.role in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            can_view = True
        
        if not can_view:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        return booking
    
    @staticmethod
    def get_coach_schedule(db: Session, coach_id: int, date_from: datetime, date_to: datetime) -> List[Dict[str, Any]]:
        """获取教练课表"""
        bookings = db.query(Booking).filter(
            Booking.coach_id == coach_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
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
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED]),
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
