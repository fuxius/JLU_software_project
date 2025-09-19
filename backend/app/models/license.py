from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric
from sqlalchemy.sql import func
from ..db.database import Base

class License(Base):
    """软件许可证表"""
    __tablename__ = "licenses"
    
    id = Column(Integer, primary_key=True, index=True)
    license_key = Column(String(255), unique=True, nullable=False, comment="许可证密钥")
    organization_name = Column(String(200), nullable=False, comment="购买机构名称")
    contact_person = Column(String(100), nullable=False, comment="联系人")
    contact_email = Column(String(100), nullable=False, comment="联系邮箱")
    contact_phone = Column(String(20), nullable=False, comment="联系电话")
    device_fingerprint = Column(String(255), comment="设备指纹")
    annual_fee = Column(Numeric(10, 2), default=500.00, comment="年费")
    purchase_date = Column(DateTime(timezone=True), nullable=False, comment="购买日期")
    expiry_date = Column(DateTime(timezone=True), nullable=False, comment="到期日期")
    is_active = Column(Integer, default=1, comment="是否激活")
    activation_date = Column(DateTime(timezone=True), comment="激活日期")
    last_validation = Column(DateTime(timezone=True), comment="最后验证时间")
    validation_count = Column(Integer, default=0, comment="验证次数")
    notes = Column(Text, comment="备注")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    def is_expired(self):
        """检查许可证是否过期"""
        from datetime import datetime
        return datetime.now() > self.expiry_date
    
    def days_until_expiry(self):
        """计算距离过期还有多少天"""
        from datetime import datetime
        if self.is_expired():
            return 0
        return (self.expiry_date - datetime.now()).days
    
    def __repr__(self):
        return f"<License(id={self.id}, key='{self.license_key[:10]}...', active={self.is_active})>"
