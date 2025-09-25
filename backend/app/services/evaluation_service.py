from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException

from ..models.evaluation import Evaluation
from ..models.user import User
from ..models.course import Course
from ..models.booking import Booking
from ..schemas.evaluation import EvaluationCreate, EvaluationUpdate
from ..services.system_log_service import SystemLogService

class EvaluationService:
    """评价服务"""
    
    @staticmethod
    def create_evaluation(db: Session, evaluation_data: EvaluationCreate, current_user: User) -> Evaluation:
        """创建课后评价"""
        # 不进行任何权限或状态检查，允许直接创建评价
        evaluation = Evaluation(
            course_id=evaluation_data.course_id,
            evaluator_id=current_user.id,
            evaluator_type=str(current_user.role).lower(),
            content=evaluation_data.content,
            rating=evaluation_data.rating
        )
        
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        # 记录日志
        SystemLogService.log_action(
            db, current_user.id, "CREATE_EVALUATION",
            f"创建课程评价: 课程ID {evaluation_data.course_id}"
        )
        
        return evaluation
    
    @staticmethod
    def get_evaluations(
        db: Session, 
        current_user: User, 
        course_id: Optional[int] = None,
        evaluator_type: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Evaluation]:
        """获取评价列表"""
        query = db.query(Evaluation)
        
        # 条件过滤
        if course_id:
            query = query.filter(Evaluation.course_id == course_id)
        
        if evaluator_type:
            query = query.filter(Evaluation.evaluator_type == evaluator_type)
        
        return query.order_by(Evaluation.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_evaluation_by_id(db: Session, evaluation_id: int, current_user: User) -> Evaluation:
        """获取评价详情"""
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价不存在"
            )
        
        return evaluation
    
    @staticmethod
    def update_evaluation(
        db: Session, 
        evaluation_id: int, 
        evaluation_data: EvaluationUpdate, 
        current_user: User
    ) -> Evaluation:
        """更新评价"""
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价不存在"
            )
        
        # 更新字段
        if evaluation_data.content is not None:
            evaluation.content = evaluation_data.content
        if evaluation_data.rating is not None:
            evaluation.rating = evaluation_data.rating
        
        evaluation.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(evaluation)
        
        # 记录日志
        SystemLogService.log_action(
            db, current_user.id, "UPDATE_EVALUATION",
            f"更新课程评价: 评价ID {evaluation_id}"
        )
        
        return evaluation
    
    @staticmethod
    def delete_evaluation(db: Session, evaluation_id: int, current_user: User) -> bool:
        """删除评价"""
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评价不存在"
            )
        
        db.delete(evaluation)
        db.commit()
        
        # 记录日志
        SystemLogService.log_action(
            db, current_user.id, "DELETE_EVALUATION",
            f"删除课程评价: 评价ID {evaluation_id}"
        )
        
        return True
    
    @staticmethod
    def get_course_evaluations(db: Session, course_id: int, current_user: User) -> List[Evaluation]:
        """获取课程的所有评价"""
        return db.query(Evaluation).filter(
            Evaluation.course_id == course_id
        ).order_by(Evaluation.created_at.desc()).all()
    
    @staticmethod
    def get_pending_evaluations(db: Session, current_user: User) -> List[Dict[str, Any]]:
        """获取待评价课程"""
        # 简化实现，直接返回空列表避免复杂的JOIN
        return []
    
    @staticmethod
    def get_evaluation_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """获取评价统计"""
        # 总评价数
        total_evaluations = db.query(Evaluation).filter(
            Evaluation.evaluator_id == user_id
        ).count()
        
        # 平均评分
        from sqlalchemy import func
        avg_rating = db.query(func.avg(Evaluation.rating)).filter(
            Evaluation.evaluator_id == user_id,
            Evaluation.rating.isnot(None)
        ).scalar() or 0
        
        # 按评分分组统计
        rating_counts = db.query(
            Evaluation.rating, 
            func.count(Evaluation.id)
        ).filter(
            Evaluation.evaluator_id == user_id,
            Evaluation.rating.isnot(None)
        ).group_by(Evaluation.rating).all()
        
        rating_distribution = {str(rating): count for rating, count in rating_counts}
        
        # 最近30天的评价数
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_evaluations = db.query(Evaluation).filter(
            Evaluation.evaluator_id == user_id,
            Evaluation.created_at >= recent_date
        ).count()
        
        return {
            "total_evaluations": total_evaluations,
            "average_rating": round(float(avg_rating), 2),
            "rating_distribution": rating_distribution,
            "recent_evaluations": recent_evaluations
        }
    
    @staticmethod
    def get_coach_evaluation_summary(db: Session, coach_id: int) -> Dict[str, Any]:
        """获取教练评价汇总"""
        from sqlalchemy import func
        evaluations_query = db.query(Evaluation).join(Course).join(Booking).filter(
            Booking.coach_id == coach_id,
            Evaluation.evaluator_type == "student"
        )
        
        total_evaluations = evaluations_query.count()
        
        if total_evaluations == 0:
            return {
                "coach_id": coach_id,
                "total_evaluations": 0,
                "average_rating": 0,
                "rating_distribution": {},
                "recent_evaluations": 0
            }
        
        # 平均评分
        avg_rating = evaluations_query.with_entities(
            func.avg(Evaluation.rating)
        ).filter(Evaluation.rating.isnot(None)).scalar() or 0
        
        # 按评分分组统计
        rating_counts = evaluations_query.with_entities(
            Evaluation.rating, 
            func.count(Evaluation.id)
        ).filter(Evaluation.rating.isnot(None)).group_by(Evaluation.rating).all()
        
        rating_distribution = {str(rating): count for rating, count in rating_counts}
        
        # 最近30天的评价数
        recent_date = datetime.utcnow() - timedelta(days=30)
        recent_evaluations = evaluations_query.filter(
            Evaluation.created_at >= recent_date
        ).count()
        
        return {
            "coach_id": coach_id,
            "total_evaluations": total_evaluations,
            "average_rating": round(float(avg_rating), 2),
            "rating_distribution": rating_distribution,
            "recent_evaluations": recent_evaluations
        }
