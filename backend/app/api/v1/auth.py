from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import timedelta

from ...db.database import get_db
from ...schemas.user import UserLogin, Token, UserCreate, UserRegister, UserResponse, AdminRegister
from ...services.user_service import UserService
from ...core.deps import get_current_user
from ...core.security import create_access_token
from ...core.config import settings

router = APIRouter()
security = HTTPBearer()

@router.post("/login", response_model=Token, summary="用户登录")
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = UserService.authenticate_user(db, login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.username,
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.post("/register/student", response_model=UserResponse, summary="学员注册")
def register_student(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """学员注册"""
    from ...models.user import UserRole
    
    # 转换为UserCreate并设置角色
    create_data = UserCreate(
        **user_data.dict(),
        role=UserRole.STUDENT
    )
    
    user = UserService.create_user(db, create_data)
    return UserResponse.from_orm(user)

@router.post("/register/coach", response_model=UserResponse, summary="教练注册")
def register_coach(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """教练注册申请"""
    from ...models.user import UserRole
    
    # 转换为UserCreate并设置角色
    create_data = UserCreate(
        **user_data.dict(),
        role=UserRole.COACH
    )
    
    user = UserService.create_user(db, create_data)
    return UserResponse.from_orm(user)


@router.post("/register/admin", response_model=UserResponse, summary="管理员注册")
def register_admin(
    user_data: AdminRegister,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """管理员注册（需超级管理员权限）"""
    from ...models.user import UserRole

    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以创建管理员账户"
        )

    create_data = UserCreate(**user_data.dict())

    user = UserService.create_admin_user(db, create_data, current_user)
    return UserResponse.from_orm(user)
