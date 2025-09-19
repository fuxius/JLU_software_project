from sqlalchemy import Column, Integer, String, DateTime, Enum, Text
from sqlalchemy.sql import func
import enum
from ..db.database import Base

class UserRole(enum.Enum):
    """用户角色枚举"""
    SUPER_ADMIN = "super_admin"  # 超级管理员
    CAMPUS_ADMIN = "campus_admin"  # 校区管理员
    COACH = "coach"  # 教练
    STUDENT = "student"  # 学员

class User(Base):
    """用户基础表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    real_name = Column(String(50), nullable=False, comment="真实姓名")
    gender = Column(String(10), comment="性别")
    age = Column(Integer, comment="年龄")
    phone = Column(String(20), nullable=False, comment="电话")
    email = Column(String(100), comment="邮箱")
    role = Column(Enum(UserRole), nullable=False, comment="用户角色")
    campus_id = Column(Integer, nullable=True, comment="所属校区ID")
    avatar_url = Column(String(255), comment="头像URL")
    id_number = Column(String(18), comment="身份证号")
    is_active = Column(Integer, default=1, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
