from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
from ..models.user import UserRole

class UserBase(BaseModel):
    """用户基础Schema"""
    username: str
    real_name: str
    gender: Optional[str] = None
    age: Optional[int] = None
    phone: str
    email: Optional[EmailStr] = None
    campus_id: Optional[int] = None
    avatar_url: Optional[str] = None
    id_number: Optional[str] = None

class UserRegister(UserBase):
    """用户注册Schema（不包含role）"""
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8 or len(v) > 16:
            raise ValueError('密码长度必须在8-16位之间')
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_letter and has_digit and has_special):
            raise ValueError('密码必须包含字母、数字和特殊字符')
        
        return v


class AdminRegister(UserRegister):
    """管理员注册Schema"""
    role: UserRole

    @validator('role', pre=True)
    def validate_role(cls, v):
        if isinstance(v, str):
            v = v.strip().upper()
        mapping = {
            'SUPER_ADMIN': UserRole.SUPER_ADMIN,
            'CAMPUS_ADMIN': UserRole.CAMPUS_ADMIN,
            UserRole.SUPER_ADMIN: UserRole.SUPER_ADMIN,
            UserRole.CAMPUS_ADMIN: UserRole.CAMPUS_ADMIN,
        }
        if v in mapping:
            return mapping[v]
        if isinstance(v, UserRole) and v in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            return v
        raise ValueError('管理员注册仅支持超级管理员或校区管理员角色')

class UserCreate(UserBase):
    """用户创建Schema"""
    password: str
    role: UserRole
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8 or len(v) > 16:
            raise ValueError('密码长度必须在8-16位之间')
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_letter and has_digit and has_special):
            raise ValueError('密码必须包含字母、数字和特殊字符')
        
        return v

    @validator('role', pre=True)
    def normalize_role(cls, v):
        if isinstance(v, str):
            v = v.strip().upper()
            mapping = {
                'SUPER_ADMIN': UserRole.SUPER_ADMIN,
                'CAMPUS_ADMIN': UserRole.CAMPUS_ADMIN,
                'COACH': UserRole.COACH,
                'STUDENT': UserRole.STUDENT,
            }
            if v in mapping:
                return mapping[v]
        return v

class UserUpdate(BaseModel):
    """用户更新Schema"""
    real_name: Optional[str] = None
    role: Optional[UserRole] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    id_number: Optional[str] = None
    
    @validator('role', pre=True)
    def normalize_role(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip().lower()
            mapping = {
                'super_admin': UserRole.SUPER_ADMIN,
                'campus_admin': UserRole.CAMPUS_ADMIN,
                'coach': UserRole.COACH,
                'student': UserRole.STUDENT,
            }
            if v in mapping:
                return mapping[v]
        return v

class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    role: UserRole
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录Schema"""
    username: str
    password: str

class Token(BaseModel):
    """令牌Schema"""
    access_token: str
    token_type: str
    user: UserResponse

class PasswordChange(BaseModel):
    """密码修改Schema"""
    old_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 8 or len(v) > 16:
            raise ValueError('密码长度必须在8-16位之间')
        
        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)
        
        if not (has_letter and has_digit and has_special):
            raise ValueError('密码必须包含字母、数字和特殊字符')
        
        return v
