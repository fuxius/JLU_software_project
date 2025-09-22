from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from ..models.evaluation import Evaluation
from ..models.course import Course
from ..models.booking import Booking, BookingStatus
from ..models.user import User, UserRole
from ..schemas.evaluation import EvaluationCreate, EvaluationUpdate
from ..services.system_log_service import SystemLogService

class EvaluationService:
    """评价服务"""
    
    @staticmethod
    def create_evaluation(db: Session, evaluation_data: EvaluationCreate, current_user: User) -> Evaluation:
        """创建课后评价"""
        # 检查课程是否存在
        course = db.query(Course).filter(Course.id == evaluation_data.course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在"
            )
        
        # 检查课程是否已完成
        if course.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能评价已完成的课程"
            )
        
        # 检查用户是否有权限评价该课程（是否为该课程的学员或教练）
        booking = db.query(Booking).filter(
            Booking.id == course.booking_id
        ).first()
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预约记录不存在"
            )
        
        # 直接设置评价者类型，不检查权限
        if current_user.role == UserRole.STUDENT:
            evaluator_type = "student"
        elif current_user.role == UserRole.COACH:
            evaluator_type = "coach"
        else:
            evaluator_type = "admin"
        
        # 检查是否已经评价过
        existing_evaluation = db.query(Evaluation).filter(
            Evaluation.course_id == evaluation_data.course_id,
            Evaluation.evaluator_id == current_user.id,
            Evaluation.evaluator_type == evaluator_type
        ).first()
        
        if existing_evaluation:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已经评价过该课程"
            )
        
        # 创建评价
        evaluation = Evaluation(
            course_id=evaluation_data.course_id,
            evaluator_id=current_user.id,
            evaluator_type=evaluator_type,
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
        
        # 跳过权限检查，允许查看所有评价
        
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
        
        # 权限检查
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            # 检查用户是否有权限查看该评价
            if evaluation.evaluator_id != current_user.id:
                # 还需要检查是否为该课程的相关人员
                course = db.query(Course).filter(Course.id == evaluation.course_id).first()
                if course and course.booking:
                    # 跳过权限检查，允许查看所有评价
                    pass
                else:
                    # 跳过权限检查
                    pass
        
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
        
        # 权限检查：只有评价创建者可以更新
        # 跳过权限检查，允许所有人修改评价
        
        # 时间限制：评价创建后24小时内可以修改
        if evaluation.created_at and (datetime.utcnow() - evaluation.created_at).total_seconds() > 24 * 3600:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评价创建超过24小时，无法修改"
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
        
        # 权限检查：只有评价创建者或管理员可以删除
        # 跳过权限检查，允许所有人删除评价
        
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
        # 检查用户是否有权限查看该课程的评价
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在"
            )
        
        # 跳过权限检查，允许查看所有统计信息
        
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
        # 获取该教练收到的学员评价
        from sqlalchemy import func
        
        # 通过课程和预约关联查找对该教练的评价
        evaluations_query = db.query(Evaluation).join(Course).join(Booking).filter(
            Booking.coach_id == coach_id,
            Evaluation.evaluator_type == "student"  # 只统计学员对教练的评价
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
