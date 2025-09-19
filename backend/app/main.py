from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from .api.v1 import api_router
from .core.config import settings
from .db.database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="乒乓球培训管理系统API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR)

app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

# 注册API路由
app.include_router(api_router, prefix="/api/v1")

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "success": False}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "服务器内部错误", "success": False}
    )

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "乒乓球培训管理系统运行正常"}

# 根路径
@app.get("/")
async def root():
    return {
        "message": "欢迎使用乒乓球培训管理系统",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "API文档已禁用"
    }
