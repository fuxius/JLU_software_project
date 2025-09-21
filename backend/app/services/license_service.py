"""
软件授权相关业务逻辑
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status

from ..models.license import License, LicenseActivation, LicenseUsageLog, LicenseStatus, LicenseType
from ..models.user import User, UserRole
from ..models.campus import Campus
from ..models.payment import Payment, PaymentType, PaymentStatus
from ..schemas.license import (
    LicenseCreate, LicenseUpdate, LicenseQuery,
    LicenseValidationRequest, LicenseValidationResponse,
    LicenseActivationCreate, LicenseRenewalRequest,
    LicenseUsageStats, LicenseStatistics, HeartbeatRequest
)
from .payment_service import PaymentService
from .system_log_service import SystemLogService


class LicenseService:
    """软件授权服务"""
    
    @staticmethod
    def create_license(db: Session, license_data: LicenseCreate, current_user: User) -> License:
        """创建软件授权"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以创建授权"
            )
        
        # 验证校区存在
        campus = db.query(Campus).filter(Campus.id == license_data.campus_id).first()
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="校区不存在"
            )
        
        # 验证日期
        if license_data.start_date >= license_data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="开始日期必须早于结束日期"
            )
        
        # 生成唯一的授权密钥
        license_key = LicenseService._generate_license_key()
        
        # 创建支付订单
        payment = PaymentService.create_payment(
            db=db,
            user_id=current_user.id,
            amount=license_data.annual_fee,
            payment_type=PaymentType.LICENSE,
            description=f"软件授权费: {license_data.organization_name}"
        )
        
        license = License(
            **license_data.model_dump(),
            license_key=license_key,
            payment_id=payment.id
        )
        
        db.add(license)
        db.commit()
        db.refresh(license)
        
        # 记录日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="create_license",
            resource_type="license",
            resource_id=license.id,
            details=f"创建授权: {license.organization_name}"
        )
        
        return license
    
    @staticmethod
    def get_licenses(db: Session, query: LicenseQuery) -> List[License]:
        """获取授权列表"""
        q = db.query(License)
        
        if query.status:
            q = q.filter(License.status == query.status)
        if query.license_type:
            q = q.filter(License.license_type == query.license_type)
        if query.campus_id:
            q = q.filter(License.campus_id == query.campus_id)
        if query.start_date:
            q = q.filter(License.start_date >= query.start_date)
        if query.end_date:
            q = q.filter(License.end_date <= query.end_date)
        
        # 分页
        offset = (query.page - 1) * query.size
        licenses = q.offset(offset).limit(query.size).all()
        
        return licenses
    
    @staticmethod
    def get_license(db: Session, license_id: int) -> License:
        """获取授权详情"""
        license = db.query(License).filter(License.id == license_id).first()
        if not license:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="授权不存在"
            )
        return license
    
    @staticmethod
    def get_license_by_key(db: Session, license_key: str) -> License:
        """根据密钥获取授权"""
        license = db.query(License).filter(License.license_key == license_key).first()
        if not license:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="授权不存在"
            )
        return license
    
    @staticmethod
    def update_license(db: Session, license_id: int, license_data: LicenseUpdate, current_user: User) -> License:
        """更新授权信息"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以更新授权"
            )
        
        license = LicenseService.get_license(db, license_id)
        
        for field, value in license_data.model_dump(exclude_unset=True).items():
            setattr(license, field, value)
        
        license.updated_at = datetime.now()
        db.commit()
        db.refresh(license)
        
        # 记录日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="update_license",
            resource_type="license",
            resource_id=license.id,
            details=f"更新授权: {license.organization_name}"
        )
        
        return license
    
    @staticmethod
    def validate_license(db: Session, validation_request: LicenseValidationRequest) -> LicenseValidationResponse:
        """验证授权"""
        try:
            license = LicenseService.get_license_by_key(db, validation_request.license_key)
        except HTTPException:
            return LicenseValidationResponse(
                valid=False,
                message="授权密钥不存在",
                features={}
            )
        
        # 检查授权状态
        if license.status != LicenseStatus.ACTIVE.value:
            return LicenseValidationResponse(
                valid=False,
                license_info=license,
                message=f"授权状态异常: {license.status}",
                features={}
            )
        
        # 检查有效期
        current_time = datetime.now()
        if current_time < license.start_date:
            return LicenseValidationResponse(
                valid=False,
                license_info=license,
                message="授权尚未生效",
                features={}
            )
        
        if current_time > license.end_date:
            # 自动更新为过期状态
            license.status = LicenseStatus.EXPIRED.value
            db.commit()
            
            return LicenseValidationResponse(
                valid=False,
                license_info=license,
                message="授权已过期",
                features={}
            )
        
        # 检查激活次数限制
        if license.activation_count >= license.max_activations:
            existing_activation = db.query(LicenseActivation).filter(
                LicenseActivation.license_id == license.id,
                LicenseActivation.hardware_fingerprint == validation_request.hardware_fingerprint,
                LicenseActivation.is_active == True
            ).first()
            
            if not existing_activation:
                return LicenseValidationResponse(
                    valid=False,
                    license_info=license,
                    message="超出最大激活次数限制",
                    features={}
                )
        
        # 生成功能权限
        features = {
            "max_users": license.max_users,
            "max_coaches": license.max_coaches,
            "max_students": license.max_students,
            "allow_competitions": license.allow_competitions,
            "allow_evaluations": license.allow_evaluations,
            "allow_advanced_reports": license.allow_advanced_reports,
            "allow_api_access": license.allow_api_access,
        }
        
        # 更新心跳时间
        license.last_heartbeat = current_time
        license.hardware_fingerprint = validation_request.hardware_fingerprint
        
        # 创建或更新激活记录
        activation = db.query(LicenseActivation).filter(
            LicenseActivation.license_id == license.id,
            LicenseActivation.hardware_fingerprint == validation_request.hardware_fingerprint
        ).first()
        
        if not activation:
            activation = LicenseActivation(
                license_id=license.id,
                activation_code=LicenseService._generate_activation_code(),
                hardware_fingerprint=validation_request.hardware_fingerprint,
                client_info=validation_request.client_info
            )
            db.add(activation)
            license.activation_count += 1
            
            if not license.activated_at:
                license.activated_at = current_time
        else:
            activation.last_used = current_time
            activation.is_active = True
        
        db.commit()
        
        return LicenseValidationResponse(
            valid=True,
            license_info=license,
            message="授权验证成功",
            features=features
        )
    
    @staticmethod
    def renew_license(db: Session, renewal_request: LicenseRenewalRequest, current_user: User) -> License:
        """续费授权"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以续费授权"
            )
        
        license = LicenseService.get_license(db, renewal_request.license_id)
        
        # 计算新的结束日期
        current_end = license.end_date
        if current_end < datetime.now():
            # 如果已过期，从当前时间开始计算
            new_end_date = datetime.now() + timedelta(days=30 * renewal_request.extend_months)
        else:
            # 如果未过期，从原结束日期开始计算
            new_end_date = current_end + timedelta(days=30 * renewal_request.extend_months)
        
        # 计算续费金额
        monthly_fee = license.annual_fee / 12
        renewal_amount = monthly_fee * renewal_request.extend_months
        
        # 创建支付订单
        payment = PaymentService.create_payment(
            db=db,
            user_id=current_user.id,
            amount=renewal_amount,
            payment_type=PaymentType.LICENSE,
            description=f"授权续费: {license.organization_name} ({renewal_request.extend_months}个月)"
        )
        
        # 更新授权
        license.end_date = new_end_date
        license.status = LicenseStatus.ACTIVE.value
        license.updated_at = datetime.now()
        
        db.commit()
        
        # 记录日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="renew_license",
            resource_type="license",
            resource_id=license.id,
            details=f"续费授权: {license.organization_name} 延长{renewal_request.extend_months}个月"
        )
        
        return license
    
    @staticmethod
    def heartbeat(db: Session, heartbeat_request: HeartbeatRequest) -> dict:
        """授权心跳检测"""
        try:
            license = LicenseService.get_license_by_key(db, heartbeat_request.license_key)
        except HTTPException:
            return {"status": "error", "message": "授权不存在"}
        
        # 更新心跳时间
        license.last_heartbeat = datetime.now()
        license.hardware_fingerprint = heartbeat_request.hardware_fingerprint
        
        # 更新激活记录
        activation = db.query(LicenseActivation).filter(
            LicenseActivation.license_id == license.id,
            LicenseActivation.hardware_fingerprint == heartbeat_request.hardware_fingerprint,
            LicenseActivation.is_active == True
        ).first()
        
        if activation:
            activation.last_used = datetime.now()
        
        # 记录使用统计
        if heartbeat_request.usage_stats:
            usage_log = LicenseUsageLog(
                license_id=license.id,
                date=datetime.now().date(),
                active_users=heartbeat_request.usage_stats.current_users,
                active_coaches=heartbeat_request.usage_stats.current_coaches,
                active_students=heartbeat_request.usage_stats.current_students,
                bookings_count=heartbeat_request.usage_stats.monthly_bookings,
                competitions_count=heartbeat_request.usage_stats.monthly_competitions
            )
            db.add(usage_log)
        
        db.commit()
        
        return {
            "status": "success",
            "message": "心跳更新成功",
            "license_status": license.status,
            "expires_at": license.end_date.isoformat()
        }
    
    @staticmethod
    def deactivate_license(db: Session, license_id: int, hardware_fingerprint: str, current_user: User) -> bool:
        """停用授权激活"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以停用授权"
            )
        
        activation = db.query(LicenseActivation).filter(
            LicenseActivation.license_id == license_id,
            LicenseActivation.hardware_fingerprint == hardware_fingerprint,
            LicenseActivation.is_active == True
        ).first()
        
        if not activation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="激活记录不存在"
            )
        
        activation.is_active = False
        activation.deactivated_at = datetime.now()
        
        # 减少激活计数
        license = db.query(License).filter(License.id == license_id).first()
        if license and license.activation_count > 0:
            license.activation_count -= 1
        
        db.commit()
        return True
    
    @staticmethod
    def get_license_statistics(db: Session) -> LicenseStatistics:
        """获取授权统计信息"""
        total_licenses = db.query(License).count()
        active_licenses = db.query(License).filter(
            License.status == LicenseStatus.ACTIVE.value
        ).count()
        expired_licenses = db.query(License).filter(
            License.status == LicenseStatus.EXPIRED.value
        ).count()
        
        # 即将过期（30天内）
        thirty_days_later = datetime.now() + timedelta(days=30)
        expiring_soon = db.query(License).filter(
            License.status == LicenseStatus.ACTIVE.value,
            License.end_date <= thirty_days_later
        ).count()
        
        # 总收入
        total_revenue = db.query(func.sum(License.annual_fee)).filter(
            License.status != LicenseStatus.CANCELLED.value
        ).scalar() or Decimal("0.00")
        
        # 按类型统计
        type_stats = db.query(
            License.license_type,
            func.count(License.id).label('count')
        ).group_by(License.license_type).all()
        
        # 月度激活统计（最近12个月）
        twelve_months_ago = datetime.now() - timedelta(days=365)
        monthly_stats = db.query(
            func.date_trunc('month', License.activated_at).label('month'),
            func.count(License.id).label('count')
        ).filter(
            License.activated_at >= twelve_months_ago
        ).group_by(
            func.date_trunc('month', License.activated_at)
        ).all()
        
        return LicenseStatistics(
            total_licenses=total_licenses,
            active_licenses=active_licenses,
            expired_licenses=expired_licenses,
            expiring_soon=expiring_soon,
            total_revenue=total_revenue,
            licenses_by_type=[{"type": type_, "count": count} for type_, count in type_stats],
            monthly_activations=[{"month": month.strftime("%Y-%m"), "count": count} for month, count in monthly_stats if month]
        )
    
    @staticmethod
    def _generate_license_key() -> str:
        """生成授权密钥"""
        # 生成格式: XXXX-XXXX-XXXX-XXXX
        segments = []
        for _ in range(4):
            segment = ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(4))
            segments.append(segment)
        return '-'.join(segments)
    
    @staticmethod
    def _generate_activation_code() -> str:
        """生成激活码"""
        return secrets.token_hex(16).upper()
    
    @staticmethod
    def cleanup_old_usage_logs(db: Session, days_old: int = 90) -> int:
        """清理旧的使用日志"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        deleted_count = db.query(LicenseUsageLog).filter(
            LicenseUsageLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        return deleted_count
