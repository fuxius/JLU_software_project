from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...db.database import get_db
from ...core.deps import get_current_user
from ...models.user import User
from ...models.coach import Coach
from ...models.booking import Booking
from ...models.comment import Comment
from ...schemas.comment import CoachCommentStats

router = APIRouter()

@router.get("/{coach_id}/stats", response_model=CoachCommentStats, summary="获取教练评价统计")
def get_coach_comment_stats(
    coach_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取教练的评价统计信息
    - 总评价数
    - 平均评分
    - 评分分布
    - 最近的10条评价
    """
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
    
    # 计算评分分布
    rating_distribution = {}
    for rating in range(1, 6):  # 1-5分
        count = (base_query.filter(Comment.rating == rating).count())
        if count > 0:  # 只包含有评价的分数
            rating_distribution[rating] = count
    
    # 获取最近的10条评价
    recent_comments = (base_query
                      .order_by(Comment.created_at.desc())
                      .limit(10)
                      .all())
    
    # 构建评价统计数据
    stats = {
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
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "booking_start_time": comment.booking.start_time,
            "booking_end_time": comment.booking.end_time,
            "booking_status": comment.booking.status,
            "student_name": comment.booking.student.user.real_name
        } for comment in recent_comments]
    }
    
    return stats