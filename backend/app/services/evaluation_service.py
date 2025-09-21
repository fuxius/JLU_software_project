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
        
        # 验证用户权限
        if current_user.role == UserRole.STUDENT:
            if booking.student_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="您没有权限评价该课程"
                )
            evaluator_type = "student"
        elif current_user.role == UserRole.COACH:
            if booking.coach_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="您没有权限评价该课程"
                )
            evaluator_type = "coach"
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学员和教练可以评价课程"
            )
        
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
        
        # 权限过滤
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            # 非管理员只能看到自己相关的评价
            if current_user.role == UserRole.STUDENT:
                # 学员可以看到自己的评价和自己课程的教练评价
                from ..models.booking import Booking
                from ..models.course import Course
                student_course_ids = db.query(Course.id).join(Booking).filter(
                    Booking.student_id == current_user.id
                ).subquery()
                query = query.filter(
                    (Evaluation.evaluator_id == current_user.id) |
                    (Evaluation.course_id.in_(student_course_ids))
                )
            elif current_user.role == UserRole.COACH:
                # 教练可以看到自己的评价和自己课程的学员评价
                from ..models.booking import Booking
                from ..models.course import Course
                coach_course_ids = db.query(Course.id).join(Booking).filter(
                    Booking.coach_id == current_user.id
                ).subquery()
                query = query.filter(
                    (Evaluation.evaluator_id == current_user.id) |
                    (Evaluation.course_id.in_(coach_course_ids))
                )
        
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
                    if current_user.role == UserRole.STUDENT and course.booking.student_id != current_user.id:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="权限不足"
                        )
                    elif current_user.role == UserRole.COACH and course.booking.coach_id != current_user.id:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="权限不足"
                        )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="权限不足"
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
        
        # 权限检查：只有评价创建者可以更新
        if evaluation.evaluator_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有评价创建者可以修改评价"
            )
        
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
        if (evaluation.evaluator_id != current_user.id and 
            current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
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
        # 检查用户是否有权限查看该课程的评价
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="课程不存在"
            )
        
        # 权限检查
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            if course.booking:
                if (current_user.role == UserRole.STUDENT and course.booking.student_id != current_user.id) or \
                   (current_user.role == UserRole.COACH and course.booking.coach_id != current_user.id):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="权限不足"
                    )
        
        return db.query(Evaluation).filter(
            Evaluation.course_id == course_id
        ).order_by(Evaluation.created_at.desc()).all()
    
    @staticmethod
    def get_pending_evaluations(db: Session, current_user: User) -> List[Dict[str, Any]]:
        """获取待评价课程"""
        # 查找已完成但未评价的课程
        from ..models.booking import Booking
        
        if current_user.role == UserRole.STUDENT:
            # 学员的待评价课程
            completed_courses = db.query(Course).join(Booking).filter(
                Booking.student_id == current_user.id,
                Course.status == "completed"
            ).all()
        elif current_user.role == UserRole.COACH:
            # 教练的待评价课程
            completed_courses = db.query(Course).join(Booking).filter(
                Booking.coach_id == current_user.id,
                Course.status == "completed"
            ).all()
        else:
            return []
        
        pending_courses = []
        for course in completed_courses:
            # 检查是否已评价
            existing_evaluation = db.query(Evaluation).filter(
                Evaluation.course_id == course.id,
                Evaluation.evaluator_id == current_user.id
            ).first()
            
            if not existing_evaluation:
                pending_courses.append({
                    "course_id": course.id,
                    "booking_id": course.booking_id,
                    "completed_at": course.completed_at,
                    "booking": {
                        "start_time": course.booking.start_time,
                        "end_time": course.booking.end_time,
                        "coach_name": course.booking.coach.user.real_name if current_user.role == UserRole.STUDENT else None,
                        "student_name": course.booking.student.user.real_name if current_user.role == UserRole.COACH else None
                    }
                })
        
        return pending_courses
    
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
