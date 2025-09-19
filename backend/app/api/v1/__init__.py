from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .campus import router as campus_router

api_router = APIRouter()

# 注册已存在的路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
api_router.include_router(campus_router, prefix="/campus", tags=["校区管理"])
