"""
软件授权管理API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.user import User
from ...core.deps import get_current_user
from ...services.license_service import LicenseService
from ...schemas.license import (
    LicenseCreate, LicenseUpdate, LicenseResponse, LicenseQuery,
    LicenseValidationRequest, LicenseValidationResponse,
    LicenseRenewalRequest, LicenseStatistics, HeartbeatRequest
)

router = APIRouter()


@router.post("/", response_model=LicenseResponse, summary="创建软件授权")
def create_license(
    license_data: LicenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建软件授权
    
    - 只有管理员可以创建授权
    - 自动生成唯一授权密钥
    - 创建对应的支付订单
    - 验证校区和日期有效性
    """
    license = LicenseService.create_license(db, license_data, current_user)
    return LicenseResponse.from_orm(license)


@router.get("/", response_model=List[LicenseResponse], summary="获取授权列表")
def get_licenses(
    status: str = Query(None, description="状态筛选"),
    license_type: str = Query(None, description="类型筛选"),
    campus_id: int = Query(None, description="校区筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取授权列表
    
    - 支持按状态、类型、校区筛选
    - 支持分页
    - 管理员可查看所有授权
    """
    query = LicenseQuery(
        status=status,
        license_type=license_type,
        campus_id=campus_id,
        page=page,
        size=size
    )
    licenses = LicenseService.get_licenses(db, query)
    return [LicenseResponse.from_orm(license) for license in licenses]


@router.get("/{license_id}", response_model=LicenseResponse, summary="获取授权详情")
def get_license(
    license_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取授权详情"""
    license = LicenseService.get_license(db, license_id)
    return LicenseResponse.from_orm(license)


@router.put("/{license_id}", response_model=LicenseResponse, summary="更新授权信息")
def update_license(
    license_id: int,
    license_data: LicenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新授权信息
    
    - 只有管理员可以更新
    - 支持修改授权状态、有效期等
    - 记录操作日志
    """
    license = LicenseService.update_license(db, license_id, license_data, current_user)
    return LicenseResponse.from_orm(license)


@router.post("/validate", response_model=LicenseValidationResponse, summary="验证授权")
def validate_license(
    validation_request: LicenseValidationRequest,
    db: Session = Depends(get_db)
):
    """
    验证授权
    
    - 检查授权密钥有效性
    - 验证授权状态和有效期
    - 检查激活次数限制
    - 返回可用功能权限
    - 更新心跳时间和激活记录
    """
    return LicenseService.validate_license(db, validation_request)


@router.post("/{license_id}/renew", response_model=LicenseResponse, summary="续费授权")
def renew_license(
    license_id: int,
    renewal_request: LicenseRenewalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    续费授权
    
    - 只有管理员可以续费
    - 延长授权有效期
    - 创建对应的支付订单
    - 计算续费金额
    """
    renewal_request.license_id = license_id
    license = LicenseService.renew_license(db, renewal_request, current_user)
    return LicenseResponse.from_orm(license)


@router.post("/heartbeat", summary="授权心跳检测")
def heartbeat(
    heartbeat_request: HeartbeatRequest,
    db: Session = Depends(get_db)
):
    """
    授权心跳检测
    
    - 更新授权使用状态
    - 记录使用统计数据
    - 验证授权有效性
    - 客户端定期调用
    """
    return LicenseService.heartbeat(db, heartbeat_request)


@router.delete("/{license_id}/activations", summary="停用授权激活")
def deactivate_license(
    license_id: int,
    hardware_fingerprint: str = Query(..., description="硬件指纹"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    停用授权激活
    
    - 只有管理员可以停用
    - 释放激活次数限制
    - 标记激活记录为无效
    """
    success = LicenseService.deactivate_license(db, license_id, hardware_fingerprint, current_user)
    if success:
        return {"message": "授权激活已停用"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="停用授权激活失败"
        )


@router.get("/statistics/summary", response_model=LicenseStatistics, summary="获取授权统计")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取授权统计信息
    
    - 总授权数、状态分布
    - 收入统计
    - 按类型统计
    - 月度激活趋势
    - 即将过期提醒
    """
    return LicenseService.get_license_statistics(db)


# 公开API（无需认证）
@router.get("/key/{license_key}", response_model=LicenseResponse, summary="根据密钥获取授权信息")
def get_license_by_key(
    license_key: str,
    db: Session = Depends(get_db)
):
    """
    根据授权密钥获取授权信息
    
    - 公开接口，无需认证
    - 客户端激活时使用
    - 返回基本授权信息
    """
    license = LicenseService.get_license_by_key(db, license_key)
    return LicenseResponse.from_orm(license)
