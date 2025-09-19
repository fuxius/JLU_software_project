from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.system_log import SystemLog
from datetime import datetime

class SystemLogService:
    """系统日志服务"""
    
    @staticmethod
    def log_action(
        db: Session,
        user_id: Optional[int],
        action: str,
        description: str,
        target_type: Optional[str] = None,
        target_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_data: Optional[str] = None
    ) -> SystemLog:
        """记录系统日志"""
        log = SystemLog(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log
    
    @staticmethod
    def get_logs(
        db: Session,
        user_id: Optional[int] = None,
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[SystemLog]:
        """获取系统日志"""
        query = db.query(SystemLog)
        
        if user_id:
            query = query.filter(SystemLog.user_id == user_id)
        if action:
            query = query.filter(SystemLog.action == action)
        if target_type:
            query = query.filter(SystemLog.target_type == target_type)
        
        return query.order_by(SystemLog.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_logs_by_campus(
        db: Session,
        campus_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[SystemLog]:
        """获取校区相关日志"""
        from ..models.user import User
        
        # 获取该校区的所有用户ID
        user_ids = db.query(User.id).filter(User.campus_id == campus_id).all()
        user_ids = [uid[0] for uid in user_ids]
        
        if not user_ids:
            return []
        
        return db.query(SystemLog).filter(
            SystemLog.user_id.in_(user_ids)
        ).order_by(SystemLog.created_at.desc()).offset(skip).limit(limit).all()
