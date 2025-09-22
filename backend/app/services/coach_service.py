from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, date

from ..models.user import User, UserRole
from ..models.coach import Coach, CoachLevel
from ..models.campus import Campus
from ..models.coach_student import CoachStudent
from ..models.booking import Booking
from ..schemas.coach import CoachCreate, CoachUpdate
from .system_log_service import SystemLogService

class CoachService:
    """教练服务"""
    
    @staticmethod
    def get_coaches(
        db: Session, 
        campus_id: Optional[int] = None,
        level: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Coach]:
        """获取教练列表"""
        query = db.query(Coach).join(User, Coach.user_id == User.id)
        
        if campus_id:
            query = query.filter(User.campus_id == campus_id)
        
        if level:
            query = query.filter(Coach.level == level)
        
        # 只返回已审核通过的教练
        query = query.filter(Coach.approval_status == "approved")
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def search_coaches(
        db: Session,
        name: Optional[str] = None,
        gender: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        campus_id: Optional[int] = None
    ) -> List[Coach]:
        """搜索教练"""
        query = db.query(Coach).join(User, Coach.user_id == User.id)
        
        filters = [Coach.approval_status == "approved"]
        
        if name:
            filters.append(User.real_name.ilike(f"%{name}%"))
        
        if gender:
            filters.append(User.gender == gender)
        
        if age_min:
            filters.append(User.age >= age_min)
        
        if age_max:
            filters.append(User.age <= age_max)
        
        if campus_id:
            filters.append(User.campus_id == campus_id)
        
        query = query.filter(and_(*filters))
        
        return query.all()
    
    @staticmethod
    def get_coach_by_id(db: Session, coach_id: int) -> Optional[Coach]:
        """根据ID获取教练"""
        return db.query(Coach).filter(Coach.id == coach_id).first()
    
    @staticmethod
    def get_coach_by_user_id(db: Session, user_id: int) -> Optional[Coach]:
        """根据用户ID获取教练"""
        return db.query(Coach).filter(Coach.user_id == user_id).first()
    
    @staticmethod
    def create_coach(db: Session, coach_data: CoachCreate, user: User) -> Coach:
        """创建教练记录"""
        coach = Coach(
            user_id=user.id,
            level=coach_data.level,
            hourly_rate=coach_data.hourly_rate,
            bio=coach_data.bio,
            achievements=coach_data.achievements,
            approval_status="pending"  # 需要管理员审核
        )
        
        db.add(coach)
        db.commit()
        db.refresh(coach)
        
        # 记录系统日志
        SystemLogService.log_action(
            db, user.id, "CREATE_COACH", 
            f"用户 {user.username} 申请成为教练"
        )
        
        return coach
    
    @staticmethod
    def update_coach(
        db: Session, 
        coach_id: int, 
        coach_data: CoachUpdate,
        current_user: User
    ) -> Coach:
        """更新教练信息"""
        coach = CoachService.get_coach_by_id(db, coach_id)
        if not coach:
            raise ValueError("教练不存在")
        
        # 更新字段
        for field, value in coach_data.dict(exclude_unset=True).items():
            setattr(coach, field, value)
        
        db.commit()
        db.refresh(coach)
        
        # 记录系统日志
        SystemLogService.log_action(
            db, current_user.id, "UPDATE_COACH", 
            f"更新教练 {coach.user.username} 的信息"
        )
        
        return coach
    
    @staticmethod
    def approve_coach(
        db: Session, 
        coach_id: int, 
        approved: bool,
        current_user: User
    ) -> Coach:
        """审核教练"""
        coach = CoachService.get_coach_by_id(db, coach_id)
        if not coach:
            raise ValueError("教练不存在")
        
        coach.approval_status = "approved" if approved else "rejected"
        
        # 如果审核通过，更新用户角色为教练
        if approved:
            coach.user.role = UserRole.COACH
        
        db.commit()
        db.refresh(coach)
        
        # 记录系统日志
        action = "APPROVE_COACH" if approved else "REJECT_COACH"
        message = f"{'审核通过' if approved else '审核拒绝'}教练 {coach.user.username}"
        SystemLogService.log_action(db, current_user.id, action, message)
        
        return coach
    
    @staticmethod
    def get_coach_students(db: Session, coach_id: int) -> List[dict]:
        """获取教练的学员列表"""
        coach_students = db.query(CoachStudent).filter(
            CoachStudent.coach_id == coach_id,
            CoachStudent.status == "active"
        ).all()
        
        students = []
        for cs in coach_students:
            student_info = {
                "id": cs.student.id,
                "name": cs.student.user.real_name,
                "phone": cs.student.user.phone,
                "age": cs.student.user.age,
                "gender": cs.student.user.gender,
                "created_at": cs.created_at.isoformat() if cs.created_at else None
            }
            students.append(student_info)
        
        return students
    
    @staticmethod
    def get_coach_schedule(
        db: Session, 
        coach_id: int,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[dict]:
        """获取教练课表"""
        query = db.query(Booking).filter(Booking.coach_id == coach_id)
        
        if date_from:
            query = query.filter(Booking.start_time >= datetime.fromisoformat(date_from))
        
        if date_to:
            query = query.filter(Booking.end_time <= datetime.fromisoformat(date_to))
        
        bookings = query.order_by(Booking.start_time).all()
        
        schedule = []
        for booking in bookings:
            schedule_item = {
                "id": booking.id,
                "student_name": booking.student.user.real_name,
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat(),
                "table_number": booking.table_number,
                "status": booking.status.value,
                "campus": booking.campus.name
            }
            schedule.append(schedule_item)
        
        return schedule
    
    @staticmethod
    def get_available_coaches(
        db: Session, 
        campus_id: int,
        student_id: int
    ) -> List[Coach]:
        """获取学员可选择的教练（未达到20人上限）"""
        # 获取该校区的所有审核通过的教练
        coaches = db.query(Coach).join(User).filter(
            User.campus_id == campus_id,
            Coach.approval_status == "approved"
        ).all()
        
        available_coaches = []
        for coach in coaches:
            # 检查教练当前学员数量
            student_count = db.query(CoachStudent).filter(
                CoachStudent.coach_id == coach.id,
                CoachStudent.status == "active"
            ).count()
            
            # 检查是否已经是该教练的学员
            existing_relation = db.query(CoachStudent).filter(
                CoachStudent.coach_id == coach.id,
                CoachStudent.student_id == student_id,
                CoachStudent.status.in_(["active", "pending"])
            ).first()
            
            # 如果学员数量未满20且不是该教练的学员，则可选择
            if student_count < 20 and not existing_relation:
                available_coaches.append(coach)
        
        return available_coaches
