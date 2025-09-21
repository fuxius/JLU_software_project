"""
软件授权相关数据模型
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base
import enum


class LicenseStatus(enum.Enum):
    """授权状态"""
    ACTIVE = "active"      # 有效
    EXPIRED = "expired"    # 已过期
    SUSPENDED = "suspended"  # 暂停
    CANCELLED = "cancelled"  # 已取消


class LicenseType(enum.Enum):
    """授权类型"""
    BASIC = "basic"        # 基础版
    PREMIUM = "premium"    # 高级版
    ENTERPRISE = "enterprise"  # 企业版


class License(Base):
    """软件授权表"""
    __tablename__ = "licenses"
    
    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String(100), unique=True, nullable=False, comment="授权密钥")
    license_type = Column(String(20), nullable=False, comment="授权类型")
    status = Column(String(20), default=LicenseStatus.ACTIVE.value, comment="授权状态")
    
    # 授权对象
    campus_id = Column(Integer, ForeignKey("campuses.id"), nullable=False, comment="校区ID")
    organization_name = Column(String(200), nullable=False, comment="机构名称")
    contact_person = Column(String(50), nullable=False, comment="联系人")
    contact_phone = Column(String(20), nullable=False, comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    
    # 授权时间
    start_date = Column(DateTime(timezone=True), nullable=False, comment="开始日期")
    end_date = Column(DateTime(timezone=True), nullable=False, comment="结束日期")
    
    # 授权限制
    max_users = Column(Integer, default=100, comment="最大用户数")
    max_coaches = Column(Integer, default=20, comment="最大教练数")
    max_students = Column(Integer, default=500, comment="最大学员数")
    
    # 功能权限
    allow_competitions = Column(Boolean, default=True, comment="是否允许比赛功能")
    allow_evaluations = Column(Boolean, default=True, comment="是否允许评价功能")
    allow_advanced_reports = Column(Boolean, default=False, comment="是否允许高级报表")
    allow_api_access = Column(Boolean, default=False, comment="是否允许API访问")
    
    # 支付信息
    annual_fee = Column(Numeric(10, 2), default=500.00, comment="年费")
    payment_id = Column(Integer, ForeignKey("payments.id"), comment="支付记录ID")
    
    # 系统信息
    hardware_fingerprint = Column(String(255), comment="硬件指纹")
    last_heartbeat = Column(DateTime(timezone=True), comment="最后心跳时间")
    activation_count = Column(Integer, default=0, comment="激活次数")
    max_activations = Column(Integer, default=3, comment="最大激活次数")
    
    # 备注和说明
    notes = Column(Text, comment="备注")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    activated_at = Column(DateTime(timezone=True), comment="激活时间")
    
    # 关系
    campus = relationship("Campus", back_populates="licenses")
    payment = relationship("Payment")
    activations = relationship("LicenseActivation", back_populates="license")


class LicenseActivation(Base):
    """授权激活记录表"""
    __tablename__ = "license_activations"
    
    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, ForeignKey("licenses.id"), nullable=False, comment="授权ID")
    
    # 激活信息
    activation_code = Column(String(50), unique=True, nullable=False, comment="激活码")
    hardware_fingerprint = Column(String(255), nullable=False, comment="硬件指纹")
    client_ip = Column(String(45), comment="客户端IP")
    client_info = Column(Text, comment="客户端信息")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否有效")
    last_used = Column(DateTime(timezone=True), comment="最后使用时间")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="激活时间")
    deactivated_at = Column(DateTime(timezone=True), comment="停用时间")
    
    # 关系
    license = relationship("License", back_populates="activations")


class LicenseUsageLog(Base):
    """授权使用日志表"""
    __tablename__ = "license_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    license_id = Column(Integer, ForeignKey("licenses.id"), nullable=False, comment="授权ID")
    
    # 使用统计
    date = Column(DateTime(timezone=True), nullable=False, comment="统计日期")
    active_users = Column(Integer, default=0, comment="活跃用户数")
    active_coaches = Column(Integer, default=0, comment="活跃教练数")
    active_students = Column(Integer, default=0, comment="活跃学员数")
    bookings_count = Column(Integer, default=0, comment="预约次数")
    competitions_count = Column(Integer, default=0, comment="比赛次数")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    license = relationship("License")