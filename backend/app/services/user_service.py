from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.user import User, UserRole
from ..models.student import Student
from ..models.coach import Coach
from ..schemas.user import UserCreate, UserUpdate, UserLogin
from ..core.security import get_password_hash, verify_password, create_access_token
from ..services.system_log_service import SystemLogService
from fastapi import HTTPException, status

class UserService:
    """用户服务"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查手机号是否已存在
        if db.query(User).filter(User.phone == user_data.phone).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号已被注册"
            )
        
        # 创建用户
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            password_hash=hashed_password,
            real_name=user_data.real_name,
            gender=user_data.gender,
            age=user_data.age,
            phone=user_data.phone,
            email=user_data.email,
            role=user_data.role,
            campus_id=user_data.campus_id,
            avatar_url=user_data.avatar_url,
            id_number=user_data.id_number
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # 根据角色创建对应的扩展记录
        if user_data.role == UserRole.STUDENT:
            student = Student(user_id=db_user.id)
            db.add(student)
            db.commit()
        elif user_data.role == UserRole.COACH:
            # 教练需要审核，先创建待审核状态
            coach = Coach(
                user_id=db_user.id,
                level=user_data.level if hasattr(user_data, 'level') else None,
                hourly_rate=0,  # 审核通过后设置
                achievements=user_data.achievements if hasattr(user_data, 'achievements') else None,
                approval_status="pending"
            )
            db.add(coach)
            db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=db_user.id,
            action="user_register",
            description=f"用户注册: {db_user.username} ({db_user.role.value})"
        )
        
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> Optional[User]:
        """用户认证"""
        user = db.query(User).filter(User.username == login_data.username).first()
        if not user:
            return None
        if not verify_password(login_data.password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_users_by_campus(db: Session, campus_id: int, skip: int = 0, limit: int = 100) -> List[User]:
        """获取校区用户列表"""
        return db.query(User).filter(User.campus_id == campus_id).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate, current_user: User) -> User:
        """更新用户信息"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查权限
        if current_user.id != user_id and current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 更新字段
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="user_update",
            target_type="user",
            target_id=user_id,
            description=f"更新用户信息: {user.username}"
        )
        
        return user
    
    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="原密码错误"
            )
        
        user.password_hash = get_password_hash(new_password)
        db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=user_id,
            action="password_change",
            description="用户修改密码"
        )
        
        return True
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int, current_user: User) -> bool:
        """停用用户"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 检查权限
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        user.is_active = 0
        db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="user_deactivate",
            target_type="user",
            target_id=user_id,
            description=f"停用用户: {user.username}"
        )
        
        return True
