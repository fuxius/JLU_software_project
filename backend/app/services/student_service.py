from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from ..models.user import User, UserRole
from ..models.student import Student
from ..models.coach_student import CoachStudent
from ..models.booking import Booking
from ..models.payment import Payment, PaymentStatus
from ..schemas.student import StudentCreate, StudentUpdate
from .system_log_service import SystemLogService

class StudentService:
    """学员服务"""
    
    @staticmethod
    def get_students(
        db: Session, 
        campus_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Student]:
        """获取学员列表"""
        query = db.query(Student).join(User)
        
        if campus_id:
            query = query.filter(User.campus_id == campus_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_student_by_id(db: Session, student_id: int) -> Optional[Student]:
        """根据ID获取学员"""
        return db.query(Student).filter(Student.id == student_id).first()
    
    @staticmethod
    def get_student_by_user_id(db: Session, user_id: int) -> Optional[Student]:
        """根据用户ID获取学员"""
        return db.query(Student).filter(Student.user_id == user_id).first()
    
    @staticmethod
    def create_student(db: Session, student_data: StudentCreate, user: User) -> Student:
        """创建学员记录"""
        student = Student(
            user_id=user.id,
            balance=0.0,
            emergency_contact=student_data.emergency_contact,
            emergency_phone=student_data.emergency_phone
        )
        
        db.add(student)
        db.commit()
        db.refresh(student)
        
        # 记录系统日志
        SystemLogService.log_action(
            db, user.id, "CREATE_STUDENT", 
            f"用户 {user.username} 注册为学员"
        )
        
        return student
    
    @staticmethod
    def update_student(
        db: Session, 
        student_id: int, 
        student_data: StudentUpdate,
        current_user: User
    ) -> Student:
        """更新学员信息"""
        student = StudentService.get_student_by_id(db, student_id)
        if not student:
            raise ValueError("学员不存在")
        
        # 更新字段
        for field, value in student_data.dict(exclude_unset=True).items():
            setattr(student, field, value)
        
        db.commit()
        db.refresh(student)
        
        # 记录系统日志
        SystemLogService.log_action(
            db, current_user.id, "UPDATE_STUDENT", 
            f"更新学员 {student.user.username} 的信息"
        )
        
        return student
    
    @staticmethod
    def get_student_coaches(db: Session, student_id: int) -> List[dict]:
        """获取学员的教练列表"""
        coach_students = db.query(CoachStudent).filter(
            CoachStudent.student_id == student_id,
            CoachStudent.status == "active"
        ).all()
        
        coaches = []
        for cs in coach_students:
            coach_info = {
                "id": cs.coach.id,
                "name": cs.coach.user.real_name,
                "level": cs.coach.level.value,
                "hourly_rate": cs.coach.hourly_rate,
                "phone": cs.coach.user.phone,
                "bio": cs.coach.bio,
                "created_at": cs.created_at.isoformat() if cs.created_at else None
            }
            coaches.append(coach_info)
        
        return coaches
    
    @staticmethod
    def get_student_bookings(
        db: Session, 
        student_id: int,
        status: Optional[str] = None
    ) -> List[dict]:
        """获取学员预约记录"""
        query = db.query(Booking).filter(Booking.student_id == student_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        bookings = query.order_by(Booking.start_time.desc()).all()
        
        booking_list = []
        for booking in bookings:
            booking_info = {
                "id": booking.id,
                "coach_name": booking.coach.user.real_name,
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat(),
                "table_number": booking.table_number,
                "status": booking.status.value,
                "campus": booking.campus.name,
                "created_at": booking.created_at.isoformat() if booking.created_at else None
            }
            booking_list.append(booking_info)
        
        return booking_list
    
    @staticmethod
    def get_student_balance(db: Session, student_id: int) -> float:
        """获取学员账户余额"""
        student = StudentService.get_student_by_id(db, student_id)
        if not student:
            return 0.0
        return student.balance
    
    @staticmethod
    def update_balance(
        db: Session, 
        student_id: int, 
        amount: float,
        operation: str = "add",
        description: str = ""
    ) -> float:
        """更新学员余额"""
        student = StudentService.get_student_by_id(db, student_id)
        if not student:
            raise ValueError("学员不存在")
        
        if operation == "add":
            student.balance += amount
        elif operation == "subtract":
            if student.balance < amount:
                raise ValueError("余额不足")
            student.balance -= amount
        
        db.commit()
        db.refresh(student)
        
        # 记录系统日志
        action = "ADD_BALANCE" if operation == "add" else "SUBTRACT_BALANCE"
        SystemLogService.log_action(
            db, student.user_id, action, 
            f"学员 {student.user.username} {description}，金额：{amount}，余额：{student.balance}"
        )
        
        return student.balance
    
    @staticmethod
    def get_available_students_for_coach(
        db: Session, 
        coach_id: int,
        campus_id: int
    ) -> List[Student]:
        """获取教练可选择的学员（未达到2个教练上限）"""
        # 获取该校区的所有学员
        students = db.query(Student).join(User).filter(
            User.campus_id == campus_id
        ).all()
        
        available_students = []
        for student in students:
            # 检查学员当前教练数量
            coach_count = db.query(CoachStudent).filter(
                CoachStudent.student_id == student.id,
                CoachStudent.status == "active"
            ).count()
            
            # 检查是否已经是该学员的教练
            existing_relation = db.query(CoachStudent).filter(
                CoachStudent.coach_id == coach_id,
                CoachStudent.student_id == student.id,
                CoachStudent.status.in_(["active", "pending"])
            ).first()
            
            # 如果教练数量未满2且不是该学员的教练，则可选择
            if coach_count < 2 and not existing_relation:
                available_students.append(student)
        
        return available_students
