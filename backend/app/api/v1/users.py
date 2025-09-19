from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...db.database import get_db
from ...schemas.user import UserResponse, UserUpdate, PasswordChange
from ...services.user_service import UserService
from ...core.deps import get_current_user, get_admin
from ...models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新当前用户信息"""
    user = UserService.update_user(db, current_user.id, user_data, current_user)
    return UserResponse.from_orm(user)

@router.post("/change-password", summary="修改密码")
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改密码"""
    success = UserService.change_password(
        db, 
        current_user.id, 
        password_data.old_password, 
        password_data.new_password
    )
    if success:
        return {"message": "密码修改成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码修改失败"
        )

@router.get("/campus/{campus_id}", response_model=List[UserResponse], summary="获取校区用户列表")
def get_campus_users(
    campus_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin)
):
    """获取校区用户列表"""
    users = UserService.get_users_by_campus(db, campus_id, skip, limit)
    return [UserResponse.from_orm(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse, summary="获取用户信息")
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin)
):
    """获取用户信息"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return UserResponse.from_orm(user)

@router.put("/{user_id}", response_model=UserResponse, summary="更新用户信息")
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin)
):
    """更新用户信息"""
    user = UserService.update_user(db, user_id, user_data, current_user)
    return UserResponse.from_orm(user)

@router.delete("/{user_id}", summary="停用用户")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin)
):
    """停用用户"""
    success = UserService.deactivate_user(db, user_id, current_user)
    if success:
        return {"message": "用户已停用"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="停用用户失败"
        )
