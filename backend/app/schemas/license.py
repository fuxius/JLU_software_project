"""
软件授权相关的数据模型
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class LicenseBase(BaseModel):
    license_type: str = Field(..., description="授权类型")
    campus_id: int = Field(..., description="校区ID")
    organization_name: str = Field(..., max_length=200, description="机构名称")
    contact_person: str = Field(..., max_length=50, description="联系人")
    contact_phone: str = Field(..., max_length=20, description="联系电话")
    contact_email: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")


class LicenseCreate(LicenseBase):
    max_users: int = Field(100, description="最大用户数")
    max_coaches: int = Field(20, description="最大教练数")
    max_students: int = Field(500, description="最大学员数")
    allow_competitions: bool = Field(True, description="是否允许比赛功能")
    allow_evaluations: bool = Field(True, description="是否允许评价功能")
    allow_advanced_reports: bool = Field(False, description="是否允许高级报表")
    allow_api_access: bool = Field(False, description="是否允许API访问")
    annual_fee: Decimal = Field(Decimal("500.00"), description="年费")
    notes: Optional[str] = Field(None, description="备注")


class LicenseUpdate(BaseModel):
    status: Optional[str] = Field(None, description="授权状态")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    max_users: Optional[int] = Field(None, description="最大用户数")
    max_coaches: Optional[int] = Field(None, description="最大教练数")
    max_students: Optional[int] = Field(None, description="最大学员数")
    allow_competitions: Optional[bool] = Field(None, description="是否允许比赛功能")
    allow_evaluations: Optional[bool] = Field(None, description="是否允许评价功能")
    allow_advanced_reports: Optional[bool] = Field(None, description="是否允许高级报表")
    allow_api_access: Optional[bool] = Field(None, description="是否允许API访问")
    notes: Optional[str] = Field(None, description="备注")


class LicenseResponse(LicenseBase):
    id: int
    license_key: str
    status: str
    max_users: int
    max_coaches: int
    max_students: int
    allow_competitions: bool
    allow_evaluations: bool
    allow_advanced_reports: bool
    allow_api_access: bool
    annual_fee: Decimal
    payment_id: Optional[int]
    hardware_fingerprint: Optional[str]
    last_heartbeat: Optional[datetime]
    activation_count: int
    max_activations: int
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    activated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LicenseQuery(BaseModel):
    status: Optional[str] = Field(None, description="状态筛选")
    license_type: Optional[str] = Field(None, description="类型筛选")
    campus_id: Optional[int] = Field(None, description="校区筛选")
    start_date: Optional[datetime] = Field(None, description="开始日期筛选")
    end_date: Optional[datetime] = Field(None, description="结束日期筛选")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页大小")


class LicenseValidationRequest(BaseModel):
    license_key: str = Field(..., description="授权密钥")
    hardware_fingerprint: str = Field(..., description="硬件指纹")
    client_info: Optional[str] = Field(None, description="客户端信息")


class LicenseValidationResponse(BaseModel):
    valid: bool = Field(..., description="是否有效")
    license_info: Optional[LicenseResponse] = Field(None, description="授权信息")
    message: str = Field(..., description="验证消息")
    features: dict = Field({}, description="可用功能")


class LicenseActivationBase(BaseModel):
    license_id: int = Field(..., description="授权ID")
    hardware_fingerprint: str = Field(..., description="硬件指纹")
    client_info: Optional[str] = Field(None, description="客户端信息")


class LicenseActivationCreate(LicenseActivationBase):
    pass


class LicenseActivationResponse(LicenseActivationBase):
    id: int
    activation_code: str
    client_ip: Optional[str]
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime
    deactivated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LicenseRenewalRequest(BaseModel):
    license_id: int = Field(..., description="授权ID")
    extend_months: int = Field(12, ge=1, le=60, description="延长月数")
    payment_method: str = Field(..., description="支付方式")


class LicenseUsageStats(BaseModel):
    license_id: int
    current_users: int = Field(0, description="当前用户数")
    current_coaches: int = Field(0, description="当前教练数")
    current_students: int = Field(0, description="当前学员数")
    monthly_bookings: int = Field(0, description="月度预约数")
    monthly_competitions: int = Field(0, description="月度比赛数")
    usage_percentage: float = Field(0.0, description="使用率百分比")


class LicenseStatistics(BaseModel):
    total_licenses: int = Field(0, description="总授权数")
    active_licenses: int = Field(0, description="有效授权数")
    expired_licenses: int = Field(0, description="过期授权数")
    expiring_soon: int = Field(0, description="即将过期数")
    total_revenue: Decimal = Field(Decimal("0.00"), description="总收入")
    licenses_by_type: List[dict] = Field([], description="按类型统计")
    monthly_activations: List[dict] = Field([], description="月度激活统计")


class HeartbeatRequest(BaseModel):
    license_key: str = Field(..., description="授权密钥")
    hardware_fingerprint: str = Field(..., description="硬件指纹")
    usage_stats: Optional[LicenseUsageStats] = Field(None, description="使用统计")
