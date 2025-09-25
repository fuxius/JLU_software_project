from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .campus import router as campus_router
from .coaches import router as coaches_router
from .students import router as students_router
from .coach_students import router as coach_students_router
from .bookings import router as bookings_router
from .payments import router as payments_router
from .evaluations import router as evaluations_router
from .system_logs import router as system_logs_router
from .competitions import router as competitions_router
from .notifications import router as notifications_router
from .licenses import router as licenses_router
from .comments import router as comments_router

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
api_router.include_router(evaluations_router, prefix="/evaluations", tags=["课后评价"])
api_router.include_router(system_logs_router, prefix="/system-logs", tags=["系统日志"])
api_router.include_router(competitions_router, prefix="/competitions", tags=["比赛管理"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["通知管理"])
api_router.include_router(licenses_router, prefix="/licenses", tags=["软件授权"])
api_router.include_router(comments_router, prefix="/comments", tags=["评论管理"])
