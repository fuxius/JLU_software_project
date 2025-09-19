from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .campus import router as campus_router
from .coaches import router as coaches_router
from .students import router as students_router
from .coach_students import router as coach_students_router
from .bookings import router as bookings_router
from .payments import router as payments_router

api_router = APIRouter()

# 注册已存在的路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
api_router.include_router(campus_router, prefix="/campus", tags=["校区管理"])
api_router.include_router(coaches_router, prefix="/coaches", tags=["教练管理"])
api_router.include_router(students_router, prefix="/students", tags=["学员管理"])
api_router.include_router(coach_students_router, prefix="/coach-students", tags=["教练学员关系"])
api_router.include_router(bookings_router, prefix="/bookings", tags=["课程预约"])
api_router.include_router(payments_router, prefix="/payments", tags=["支付管理"])
