from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from ..db.database import get_db
from ..models.user import User, UserRole
from ..core.security import verify_token

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账户已被禁用"
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    return current_user

def require_role(required_role: UserRole):
    """要求特定角色"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker

def require_roles(*required_roles: UserRole):
    """要求特定角色之一"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        return current_user
    return role_checker

def get_super_admin(current_user: User = Depends(require_role(UserRole.SUPER_ADMIN))) -> User:
    """获取超级管理员"""
    return current_user

def get_admin(current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN))) -> User:
    """获取管理员(超级管理员或校区管理员)"""
    return current_user

def get_coach(current_user: User = Depends(require_role(UserRole.COACH))) -> User:
    """获取教练"""
    return current_user

def get_student(current_user: User = Depends(require_role(UserRole.STUDENT))) -> User:
    """获取学员"""
    return current_user
