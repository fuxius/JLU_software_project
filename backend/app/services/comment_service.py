from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from ..models.comment import Comment
from ..models.booking import Booking, BookingStatus
from ..models.user import User, UserRole
from ..models.coach import Coach
from ..models.student import Student
from ..schemas.comment import CommentCreate, CommentUpdate, CommentWithBookingInfo, CoachCommentStats, StudentCommentStats

class CommentService:
    """评论服务类"""
    
    @staticmethod
    def create_comment(db: Session, comment_data: CommentCreate, current_user: User) -> Comment:
        """
        创建评论
        - 只有学员可以对已完成的预约进行评价
        - 每个预约只能评价一次
        """
        # 检查预约是否存在
        booking = db.query(Booking).filter(Booking.id == comment_data.booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="预约不存在"
            )
        
        # 检查当前用户是否有权限评价此预约
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student or booking.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限评价此预约"
            )
        
        # # 检查预约是否已完成
        # if booking.status != BookingStatus.COMPLETED.value:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="只能对已完成的预约进行评价"
        #     )
        
        # 检查是否已经评价过
        existing_comment = db.query(Comment).filter(Comment.booking_id == comment_data.booking_id).first()
        if existing_comment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该预约已经评价过了"
            )
        
        # 创建评论
        comment = Comment(
            booking_id=comment_data.booking_id,
            rating=comment_data.rating,
            content=comment_data.content
        )
        
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        return comment
    
    @staticmethod
    def update_comment(db: Session, comment_id: int, comment_data: CommentUpdate, current_user: User) -> Comment:
        """
        更新评论
        - 只能更新自己的评论
        - 只能在创建后24小时内修改
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        # 检查权限
        booking = db.query(Booking).filter(Booking.id == comment.booking_id).first()
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not booking or not student or booking.student_id != student.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限修改此评论"
            )
        
        # 检查是否在可修改时间内（24小时内）
        if datetime.now() - comment.created_at > timedelta(hours=24):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="评论创建超过24小时，无法修改"
            )
        
        # 更新评论
        comment.rating = comment_data.rating
        comment.content = comment_data.content
        comment.updated_at = datetime.now()
        
        db.commit()
        db.refresh(comment)
        
        return comment
    
    @staticmethod
    def delete_comment(db: Session, comment_id: int, current_user: User) -> bool:
        """
        删除评论
        - 只能删除自己的评论
        - 管理员可以删除任何评论
        """
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        # 检查权限
        booking = db.query(Booking).filter(Booking.id == comment.booking_id).first()
        if current_user.role != UserRole.ADMIN:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if not booking or not student or booking.student_id != student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限删除此评论"
                )
        
        db.delete(comment)
        db.commit()
        
        return True
    
    @staticmethod
    def get_comment_by_id(db: Session, comment_id: int, current_user: User) -> Comment:
        """根据ID获取评论详情"""
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="评论不存在"
            )
        
        # 检查权限
        booking = db.query(Booking).filter(Booking.id == comment.booking_id).first()
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="关联的预约不存在"
            )

        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if not student or booking.student_id != student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限查看此评论"
                )
        elif current_user.role == UserRole.COACH:
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if not coach or booking.coach_id != coach.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="没有权限查看此评论"
                )
        elif current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有权限查看此评论"
            )
        
        return comment
    
    @staticmethod
    def get_comments_by_coach(db: Session, coach_id: int, current_user: User, 
                            skip: int = 0, limit: int = 100) -> List[CommentWithBookingInfo]:
        """
        根据教练ID获取评论列表
        - 管理员可以看到所有评论
        """
        # 检查权限
        if current_user.role == UserRole.COACH:
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if not coach or coach_id != coach.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能查看自己的评论"
                )
        
        # 查询教练的评论
        comments = (db.query(Comment)
                   .join(Booking, Comment.booking_id == Booking.id)
                   .filter(Booking.coach_id == coach_id)
                   .order_by(Comment.created_at.desc())
                   .offset(skip)
                   .limit(limit)
                   .all())
        
        # 构造返回结果
        result = []
        for comment in comments:
            comment_info = {
                "id": comment.id,
                "booking_id": comment.booking_id,
                "rating": comment.rating,
                "content": comment.content,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
                "coach_name": comment.booking.coach.user.real_name if comment.booking.coach and comment.booking.coach.user else None,
                "student_name": comment.booking.student.user.real_name if comment.booking.student and comment.booking.student.user else None,
                "booking_start_time": comment.booking.start_time,
                "booking_end_time": comment.booking.end_time,
                "booking_status": comment.booking.status
            }
            result.append(comment_info)
        
        return result

    @staticmethod
    def get_coach_comment_stats(db: Session, coach_id: int, current_user: User) -> CoachCommentStats:
        """获取教练的评价统计信息"""
        # 检查权限
        if current_user.role == UserRole.COACH:
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if not coach or coach_id != coach.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能查看自己的评价统计"
                )

        # 检查教练是否存在
        coach = db.query(Coach).filter(Coach.id == coach_id).first()
        if not coach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教练不存在"
            )

        # 获取所有评价的基本信息
        base_query = (db.query(Comment)
                    .join(Booking, Comment.booking_id == Booking.id)
                    .filter(Booking.coach_id == coach_id))
        
        # 计算总评价数和平均评分
        total_comments = base_query.count()
        
        if total_comments == 0:
            # 如果没有评价，返回空统计
            return {
                "coach_id": coach_id,
                "coach_name": coach.user.real_name,
                "total_comments": 0,
                "average_rating": 0.0,
                "rating_distribution": {},
                "recent_comments": []
            }
        
        average_rating = (db.query(func.avg(Comment.rating))
                        .select_from(Comment)
                        .join(Booking, Comment.booking_id == Booking.id)
                        .filter(Booking.coach_id == coach_id)
                        .scalar() or 0.0)
        
        # 计算评分分布（包含所有分数，即使是0）
        rating_distribution = {}
        for rating in range(1, 6):  # 1-5分
            count = (base_query.filter(Comment.rating == rating).count())
            rating_distribution[str(rating)] = count  # 包含所有评分，即使计数为0
        
        # 获取最近的10条评价
        recent_comments = (base_query
                        .order_by(Comment.created_at.desc())
                        .limit(10)
                        .all())
        
        # 构建评价统计数据
        def format_datetime(dt):
            if dt is None:
                return None
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        result = {
            "coach_id": coach_id,
            "coach_name": coach.user.real_name,
            "total_comments": total_comments,
            "average_rating": float(average_rating),
            "rating_distribution": rating_distribution,
            "recent_comments": [{
                "id": comment.id,
                "booking_id": comment.booking_id,
                "rating": comment.rating,
                "content": comment.content,
                "created_at": format_datetime(comment.created_at),
                "updated_at": format_datetime(comment.updated_at),
                "booking_start_time": format_datetime(comment.booking.start_time),
                "booking_end_time": format_datetime(comment.booking.end_time),
                "booking_status": comment.booking.status,
                "student_name": comment.booking.student.user.real_name if comment.booking.student and comment.booking.student.user else None
            } for comment in recent_comments]
        }
        
        return result
        
        # 构造包含预约信息的响应
        result = []
        for comment in comments:
            booking = db.query(Booking).filter(Booking.id == comment.booking_id).first()
            if booking:
                comment_data = CommentWithBookingInfo.from_orm(comment)
                
                # 添加教练和学员信息
                if booking.coach and booking.coach.user:
                    comment_data.coach_name = booking.coach.user.real_name
                if booking.student and booking.student.user:
                    comment_data.student_name = booking.student.user.real_name
                
                # 添加预约时间信息
                comment_data.booking_start_time = booking.start_time
                comment_data.booking_end_time = booking.end_time
                comment_data.booking_status = booking.status
                
                result.append(comment_data)
        
        return result
    
    @staticmethod
    def get_comments_by_student(db: Session, student_id: int, current_user: User,
                              skip: int = 0, limit: int = 100) -> List[CommentWithBookingInfo]:
        """
        根据学员ID获取评论列表
        - 学员只能看到自己的评论
        - 管理员可以看到所有评论
        """
        # 检查权限
        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if not student or student_id != student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能查看自己的评论"
                )
        
        # 查询学员的评论
        comments = (db.query(Comment)
                   .join(Booking, Comment.booking_id == Booking.id)
                   .filter(Booking.student_id == student_id)
                   .order_by(Comment.created_at.desc())
                   .offset(skip)
                   .limit(limit)
                   .all())
        
        # 构造包含预约信息的响应
        result = []
        for comment in comments:
            booking = db.query(Booking).filter(Booking.id == comment.booking_id).first()
            if booking:
                comment_data = CommentWithBookingInfo.from_orm(comment)
                
                # 添加教练和学员信息
                if booking.coach and booking.coach.user:
                    comment_data.coach_name = booking.coach.user.real_name
                if booking.student and booking.student.user:
                    comment_data.student_name = booking.student.user.real_name
                
                # 添加预约时间信息
                comment_data.booking_start_time = booking.start_time
                comment_data.booking_end_time = booking.end_time
                comment_data.booking_status = booking.status
                
                result.append(comment_data)
        
        return result
    
    @staticmethod
    def get_coach_comment_stats(db: Session, coach_id: int, current_user: User) -> CoachCommentStats:
        """
        获取教练评价统计
        """
        # 检查权限
        if current_user.role == UserRole.COACH:
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if not coach or coach_id != coach.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能查看自己的统计信息"
                )
        
        # 获取教练信息
        coach = db.query(Coach).filter(Coach.id == coach_id).first()
        if not coach:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="教练不存在"
            )
        
        # 统计评论数据
        stats = (db.query(
                    func.count(Comment.id).label('total_comments'),
                    func.avg(Comment.rating).label('average_rating'),
                    func.count(Comment.id).filter(Comment.rating == 1).label('rating_1'),
                    func.count(Comment.id).filter(Comment.rating == 2).label('rating_2'),
                    func.count(Comment.id).filter(Comment.rating == 3).label('rating_3'),
                    func.count(Comment.id).filter(Comment.rating == 4).label('rating_4'),
                    func.count(Comment.id).filter(Comment.rating == 5).label('rating_5')
                )
                .join(Booking, Comment.booking_id == Booking.id)
                .filter(Booking.coach_id == coach_id)
                .first())
        
        # 获取最近5条评论
        recent_comments = (db.query(Comment)
                          .join(Booking, Comment.booking_id == Booking.id)
                          .filter(Booking.coach_id == coach_id)
                          .order_by(Comment.created_at.desc())
                          .limit(5)
                          .all())
        
        # 构造统计信息
        rating_distribution = {
            1: stats.rating_1 or 0,
            2: stats.rating_2 or 0,
            3: stats.rating_3 or 0,
            4: stats.rating_4 or 0,
            5: stats.rating_5 or 0
        }
        
        return CoachCommentStats(
            coach_id=coach_id,
            coach_name=coach.user.real_name if coach.user else "未知",
            total_comments=stats.total_comments or 0,
            average_rating=round(float(stats.average_rating or 0), 2),
            rating_distribution=rating_distribution,
            recent_comments=[CommentWithBookingInfo.from_orm(comment) for comment in recent_comments]
        )
    
    @staticmethod
    def get_student_comment_stats(db: Session, student_id: int, current_user: User) -> StudentCommentStats:
        """
        获取学员评价统计
        """
        # 检查权限
        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if not student or student_id != student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能查看自己的统计信息"
                )
        
        # 获取学员信息
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学员不存在"
            )
        
        # 统计评论数据
        stats = (db.query(
                    func.count(Comment.id).label('total_comments'),
                    func.avg(Comment.rating).label('average_rating')
                )
                .join(Booking, Comment.booking_id == Booking.id)
                .filter(Booking.student_id == student_id)
                .first())
        
        # 获取最近5条评论
        recent_comments = (db.query(Comment)
                          .join(Booking, Comment.booking_id == Booking.id)
                          .filter(Booking.student_id == student_id)
                          .order_by(Comment.created_at.desc())
                          .limit(5)
                          .all())
        
        return StudentCommentStats(
            student_id=student_id,
            student_name=student.user.real_name if student.user else "未知",
            total_comments_given=stats.total_comments or 0,
            average_rating_given=round(float(stats.average_rating or 0), 2),
            recent_comments=[CommentWithBookingInfo.from_orm(comment) for comment in recent_comments]
        )
