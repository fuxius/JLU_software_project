from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ...db.database import get_db
from ...core.deps import get_current_user
from ...models.user import User, UserRole
from ...schemas.system_log import SystemLogResponse, SystemLogQuery
from ...services.system_log_service import SystemLogService

router = APIRouter()

@router.get("/", response_model=List[SystemLogResponse], summary="获取系统日志")
def get_system_logs(
    action: Optional[str] = Query(None, description="操作类型筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取系统日志
    
    - 只有管理员可以查看系统日志
    - 支持按操作类型、用户、时间范围筛选
    """
    # 权限检查：只有管理员可以查看系统日志
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有管理员可以查看系统日志"
        )
    
    logs = SystemLogService.get_logs(
        db=db,
        action=action,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return [SystemLogResponse.from_orm(log) for log in logs]

@router.get("/{log_id}", response_model=SystemLogResponse, summary="获取日志详情")
def get_system_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取系统日志详情"""
    # 权限检查
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    log = SystemLogService.get_log_by_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="日志记录不存在"
        )
    
    return SystemLogResponse.from_orm(log)

@router.get("/export/csv", summary="导出日志为CSV")
def export_logs_csv(
    action: Optional[str] = Query(None, description="操作类型筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出系统日志为CSV文件
    
    - 只有超级管理员可以导出日志
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以导出日志"
        )
    
    csv_content = SystemLogService.export_logs_csv(
        db=db,
        action=action,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    from fastapi.responses import Response
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=system_logs.csv"}
    )

@router.get("/statistics/summary", summary="获取日志统计")
def get_log_statistics(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取系统日志统计信息
    
    - 按操作类型统计
    - 按用户统计
    - 按时间统计
    """
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    statistics = SystemLogService.get_log_statistics(db, days)
    return statistics

@router.delete("/cleanup", summary="清理旧日志")
def cleanup_old_logs(
    days: int = Query(90, ge=30, description="保留天数，删除指定天数之前的日志"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    清理旧的系统日志
    
    - 只有超级管理员可以清理日志
    - 默认删除90天之前的日志
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以清理日志"
        )
    
    deleted_count = SystemLogService.cleanup_old_logs(db, days)
    
    # 记录清理操作
    SystemLogService.log_action(
        db=db,
        user_id=current_user.id,
        action="CLEANUP_LOGS",
        description=f"清理了{deleted_count}条{days}天前的日志记录"
    )
    
    return {
        "message": f"成功清理了{deleted_count}条日志记录",
        "deleted_count": deleted_count,
        "retention_days": days
    }
