from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..db.database import Base

class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), comment="操作用户ID")
    action = Column(String(50), nullable=False, comment="操作类型")
    target_type = Column(String(50), comment="目标类型(user/booking/payment等)")
    target_id = Column(Integer, comment="目标ID")
    description = Column(Text, nullable=False, comment="操作描述")
    ip_address = Column(String(45), comment="IP地址")
    user_agent = Column(Text, comment="用户代理")
    extra_data = Column(Text, comment="额外数据(JSON格式)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, user={self.user_id}, action='{self.action}')>"
