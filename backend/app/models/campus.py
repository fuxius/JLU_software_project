from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base

class Campus(Base):
    """校区表"""
    __tablename__ = "campuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="校区名称")
    address = Column(Text, nullable=False, comment="校区地址")
    contact_person = Column(String(50), nullable=False, comment="联系人")
    contact_phone = Column(String(20), nullable=False, comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    admin_id = Column(Integer, ForeignKey("users.id"), comment="校区管理员ID")
    is_main_campus = Column(Integer, default=0, comment="是否为中心校区")
    is_active = Column(Integer, default=1, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    admin = relationship("User", foreign_keys=[admin_id])
    competitions = relationship("Competition", back_populates="campus")
    licenses = relationship("License", back_populates="campus")
    
    def __repr__(self):
        return f"<Campus(id={self.id}, name='{self.name}', is_main={self.is_main_campus})>"
