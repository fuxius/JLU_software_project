from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from ..models.system_log import SystemLog
from datetime import datetime, timedelta
import csv
import io

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
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
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
        if start_date:
            query = query.filter(SystemLog.created_at >= start_date)
        if end_date:
            query = query.filter(SystemLog.created_at <= end_date)
        
        return query.order_by(SystemLog.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_log_by_id(db: Session, log_id: int) -> Optional[SystemLog]:
        """根据ID获取日志"""
        return db.query(SystemLog).filter(SystemLog.id == log_id).first()
    
    @staticmethod
    def export_logs_csv(
        db: Session,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """导出日志为CSV格式"""
        logs = SystemLogService.get_logs(
            db=db,
            action=action,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000  # 导出更多记录
        )
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        writer.writerow([
            'ID', '用户ID', '操作', '目标类型', '目标ID', 
            '描述', 'IP地址', '用户代理', '额外数据', '创建时间'
        ])
        
        # 写入数据
        for log in logs:
            writer.writerow([
                log.id,
                log.user_id,
                log.action,
                log.target_type,
                log.target_id,
                log.description,
                log.ip_address,
                log.user_agent,
                log.extra_data,
                log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    def get_log_statistics(db: Session, days: int = 30) -> Dict[str, Any]:
        """获取日志统计信息"""
        from sqlalchemy import func
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # 按操作类型统计
        action_stats = db.query(
            SystemLog.action,
            func.count(SystemLog.id).label('count')
        ).filter(
            SystemLog.created_at >= start_date
        ).group_by(SystemLog.action).all()
        
        # 按用户统计
        user_stats = db.query(
            SystemLog.user_id,
            func.count(SystemLog.id).label('count')
        ).filter(
            SystemLog.created_at >= start_date
        ).group_by(SystemLog.user_id).order_by(
            func.count(SystemLog.id).desc()
        ).limit(10).all()
        
        # 按日期统计
        date_stats = db.query(
            func.date(SystemLog.created_at).label('date'),
            func.count(SystemLog.id).label('count')
        ).filter(
            SystemLog.created_at >= start_date
        ).group_by(func.date(SystemLog.created_at)).order_by(
            func.date(SystemLog.created_at).desc()
        ).all()
        
        # 总记录数
        total_logs = db.query(SystemLog).filter(
            SystemLog.created_at >= start_date
        ).count()
        
        return {
            'total_logs': total_logs,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': datetime.utcnow().isoformat(),
                'days': days
            },
            'action_statistics': [
                {'action': action, 'count': count} 
                for action, count in action_stats
            ],
            'top_users': [
                {'user_id': user_id, 'count': count} 
                for user_id, count in user_stats
            ],
            'daily_statistics': [
                {'date': str(date), 'count': count} 
                for date, count in date_stats
            ]
        }
    
    @staticmethod
    def cleanup_old_logs(db: Session, days: int = 90) -> int:
        """清理旧日志"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 统计要删除的记录数
        count = db.query(SystemLog).filter(
            SystemLog.created_at < cutoff_date
        ).count()
        
        # 删除旧记录
        db.query(SystemLog).filter(
            SystemLog.created_at < cutoff_date
        ).delete()
        
        db.commit()
        return count
    
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
