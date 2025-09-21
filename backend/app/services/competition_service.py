"""
比赛相关业务逻辑
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status
import random

from models.competition import Competition, CompetitionRegistration, CompetitionMatch, CompetitionStatus
from models.user import User, UserRole
from models.student import Student
from models.payment import Payment, PaymentType, PaymentStatus
from schemas.competition import (
    CompetitionCreate, CompetitionUpdate, CompetitionQuery,
    CompetitionRegistrationCreate, CompetitionMatchCreate, CompetitionMatchUpdate,
    DrawRequest, CompetitionStatistics
)
from services.payment_service import PaymentService
from services.system_log_service import SystemLogService


class CompetitionService:
    """比赛管理服务"""
    
    @staticmethod
    def create_competition(db: Session, competition_data: CompetitionCreate, current_user: User) -> Competition:
        """创建比赛"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以创建比赛"
            )
        
        # 验证日期
        if competition_data.registration_deadline >= competition_data.competition_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="报名截止时间必须早于比赛日期"
            )
        
        competition = Competition(**competition_data.model_dump())
        db.add(competition)
        db.commit()
        db.refresh(competition)
        
        # 记录日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="create_competition",
            resource_type="competition",
            resource_id=competition.id,
            details=f"创建比赛: {competition.title}"
        )
        
        return competition
    
    @staticmethod
    def get_competitions(db: Session, query: CompetitionQuery) -> List[Competition]:
        """获取比赛列表"""
        q = db.query(Competition)
        
        if query.status:
            q = q.filter(Competition.status == query.status)
        if query.campus_id:
            q = q.filter(Competition.campus_id == query.campus_id)
        if query.start_date:
            q = q.filter(Competition.competition_date >= query.start_date)
        if query.end_date:
            q = q.filter(Competition.competition_date <= query.end_date)
        
        # 分页
        offset = (query.page - 1) * query.size
        competitions = q.offset(offset).limit(query.size).all()
        
        # 添加报名人数
        for competition in competitions:
            registered_count = db.query(CompetitionRegistration).filter(
                CompetitionRegistration.competition_id == competition.id,
                CompetitionRegistration.is_confirmed == True
            ).count()
            competition.registered_count = registered_count
        
        return competitions
    
    @staticmethod
    def get_competition(db: Session, competition_id: int) -> Competition:
        """获取比赛详情"""
        competition = db.query(Competition).filter(Competition.id == competition_id).first()
        if not competition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="比赛不存在"
            )
        
        # 添加报名人数
        registered_count = db.query(CompetitionRegistration).filter(
            CompetitionRegistration.competition_id == competition_id,
            CompetitionRegistration.is_confirmed == True
        ).count()
        competition.registered_count = registered_count
        
        return competition
    
    @staticmethod
    def update_competition(db: Session, competition_id: int, competition_data: CompetitionUpdate, current_user: User) -> Competition:
        """更新比赛信息"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以更新比赛"
            )
        
        competition = CompetitionService.get_competition(db, competition_id)
        
        # 如果比赛已开始，限制可修改的字段
        if competition.status in [CompetitionStatus.IN_PROGRESS.value, CompetitionStatus.COMPLETED.value]:
            allowed_fields = {"status", "description"}
            update_fields = {k: v for k, v in competition_data.model_dump(exclude_unset=True).items() 
                           if k in allowed_fields}
        else:
            update_fields = competition_data.model_dump(exclude_unset=True)
        
        for field, value in update_fields.items():
            setattr(competition, field, value)
        
        competition.updated_at = datetime.now()
        db.commit()
        db.refresh(competition)
        
        # 记录日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="update_competition",
            resource_type="competition",
            resource_id=competition.id,
            details=f"更新比赛: {competition.title}"
        )
        
        return competition
    
    @staticmethod
    def register_competition(db: Session, registration_data: CompetitionRegistrationCreate, current_user: User) -> CompetitionRegistration:
        """比赛报名"""
        if current_user.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有学员可以报名比赛"
            )
        
        competition = CompetitionService.get_competition(db, registration_data.competition_id)
        
        # 检查比赛状态
        if competition.status != CompetitionStatus.REGISTRATION.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="比赛不在报名期内"
            )
        
        # 检查报名截止时间
        if datetime.now() > competition.registration_deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="报名已截止"
            )
        
        # 检查是否已报名
        existing = db.query(CompetitionRegistration).filter(
            CompetitionRegistration.competition_id == registration_data.competition_id,
            CompetitionRegistration.student_id == current_user.student.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="您已报名此比赛"
            )
        
        # 检查报名人数限制
        registered_count = db.query(CompetitionRegistration).filter(
            CompetitionRegistration.competition_id == registration_data.competition_id,
            CompetitionRegistration.is_confirmed == True
        ).count()
        
        if registered_count >= competition.max_participants:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="报名人数已满"
            )
        
        # 创建支付订单
        payment = PaymentService.create_payment(
            db=db,
            user_id=current_user.id,
            amount=competition.registration_fee,
            payment_type=PaymentType.COMPETITION,
            description=f"比赛报名费: {competition.title}"
        )
        
        # 创建报名记录
        registration = CompetitionRegistration(
            competition_id=registration_data.competition_id,
            student_id=current_user.student.id,
            group_type=registration_data.group_type,
            payment_id=payment.id
        )
        
        db.add(registration)
        db.commit()
        db.refresh(registration)
        
        # 记录日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="register_competition",
            resource_type="competition_registration",
            resource_id=registration.id,
            details=f"报名比赛: {competition.title} ({registration_data.group_type}组)"
        )
        
        return registration
    
    @staticmethod
    def confirm_registration(db: Session, registration_id: int, current_user: User) -> CompetitionRegistration:
        """确认报名（支付成功后）"""
        registration = db.query(CompetitionRegistration).filter(
            CompetitionRegistration.id == registration_id
        ).first()
        
        if not registration:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="报名记录不存在"
            )
        
        # 检查权限
        if current_user.role == UserRole.STUDENT:
            if registration.student_id != current_user.student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只能确认自己的报名"
                )
        elif current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        # 检查支付状态
        if registration.payment:
            if registration.payment.status != PaymentStatus.SUCCESS.value:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="报名费尚未支付"
                )
        
        registration.is_confirmed = True
        db.commit()
        db.refresh(registration)
        
        return registration
    
    @staticmethod
    def get_registrations(db: Session, competition_id: int, group_type: Optional[str] = None) -> List[CompetitionRegistration]:
        """获取比赛报名列表"""
        q = db.query(CompetitionRegistration).filter(
            CompetitionRegistration.competition_id == competition_id
        )
        
        if group_type:
            q = q.filter(CompetitionRegistration.group_type == group_type)
        
        return q.all()
    
    @staticmethod
    def generate_draw(db: Session, draw_request: DrawRequest, current_user: User) -> List[CompetitionMatch]:
        """生成比赛对阵"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以生成对阵"
            )
        
        competition = CompetitionService.get_competition(db, draw_request.competition_id)
        
        # 检查比赛状态
        if competition.status not in [CompetitionStatus.REGISTRATION.value, CompetitionStatus.DRAW_COMPLETE.value]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="比赛状态不允许生成对阵"
            )
        
        # 获取该组别的已确认报名者
        registrations = db.query(CompetitionRegistration).filter(
            CompetitionRegistration.competition_id == draw_request.competition_id,
            CompetitionRegistration.group_type == draw_request.group_type,
            CompetitionRegistration.is_confirmed == True
        ).all()
        
        if len(registrations) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="报名人数不足，无法生成对阵"
            )
        
        # 清除该组别的现有对阵
        db.query(CompetitionMatch).filter(
            CompetitionMatch.competition_id == draw_request.competition_id,
            CompetitionMatch.group_type == draw_request.group_type
        ).delete()
        
        # 随机排列参赛者
        participants = [reg.student_id for reg in registrations]
        random.shuffle(participants)
        
        # 如果参赛人数为奇数，添加一个轮空
        if len(participants) % 2 == 1:
            participants.append(None)  # None 代表轮空
        
        matches = []
        round_number = 1
        
        # 生成第一轮对阵
        for i in range(0, len(participants), 2):
            match = CompetitionMatch(
                competition_id=draw_request.competition_id,
                group_type=draw_request.group_type,
                round_number=round_number,
                match_number=i // 2 + 1,
                player1_id=participants[i],
                player2_id=participants[i + 1] if i + 1 < len(participants) else None
            )
            
            # 如果有轮空，直接设置获胜者
            if match.player2_id is None:
                match.winner_id = match.player1_id
                match.match_status = "completed"
            
            matches.append(match)
            db.add(match)
        
        db.commit()
        
        # 更新比赛状态
        competition.status = CompetitionStatus.DRAW_COMPLETE.value
        db.commit()
        
        # 记录日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="generate_draw",
            resource_type="competition",
            resource_id=competition.id,
            details=f"生成对阵: {competition.title} {draw_request.group_type}组"
        )
        
        return matches
    
    @staticmethod
    def update_match_result(db: Session, match_id: int, match_data: CompetitionMatchUpdate, current_user: User) -> CompetitionMatch:
        """更新比赛结果"""
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有管理员可以录入比赛结果"
            )
        
        match = db.query(CompetitionMatch).filter(CompetitionMatch.id == match_id).first()
        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="比赛对阵不存在"
            )
        
        # 更新比赛结果
        for field, value in match_data.model_dump(exclude_unset=True).items():
            setattr(match, field, value)
        
        # 自动确定获胜者
        if match_data.player1_score is not None and match_data.player2_score is not None:
            if match_data.player1_score > match_data.player2_score:
                match.winner_id = match.player1_id
            elif match_data.player2_score > match_data.player1_score:
                match.winner_id = match.player2_id
            # 平局情况下winner_id保持None
            
            match.match_status = "completed"
        
        match.updated_at = datetime.now()
        db.commit()
        db.refresh(match)
        
        # 记录日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="update_match_result",
            resource_type="competition_match",
            resource_id=match.id,
            details=f"录入比赛结果: {match_data.player1_score}:{match_data.player2_score}"
        )
        
        return match
    
    @staticmethod
    def get_competition_matches(db: Session, competition_id: int, group_type: Optional[str] = None) -> List[CompetitionMatch]:
        """获取比赛对阵列表"""
        q = db.query(CompetitionMatch).filter(
            CompetitionMatch.competition_id == competition_id
        )
        
        if group_type:
            q = q.filter(CompetitionMatch.group_type == group_type)
        
        return q.order_by(CompetitionMatch.round_number, CompetitionMatch.match_number).all()
    
    @staticmethod
    def get_competition_statistics(db: Session) -> CompetitionStatistics:
        """获取比赛统计信息"""
        total_competitions = db.query(Competition).count()
        upcoming_competitions = db.query(Competition).filter(
            Competition.status == CompetitionStatus.UPCOMING.value
        ).count()
        ongoing_competitions = db.query(Competition).filter(
            Competition.status.in_([
                CompetitionStatus.REGISTRATION.value,
                CompetitionStatus.DRAW_COMPLETE.value,
                CompetitionStatus.IN_PROGRESS.value
            ])
        ).count()
        completed_competitions = db.query(Competition).filter(
            Competition.status == CompetitionStatus.COMPLETED.value
        ).count()
        
        total_participants = db.query(CompetitionRegistration).filter(
            CompetitionRegistration.is_confirmed == True
        ).count()
        
        # 热门组别统计
        popular_groups = db.query(
            CompetitionRegistration.group_type,
            func.count(CompetitionRegistration.id).label('count')
        ).filter(
            CompetitionRegistration.is_confirmed == True
        ).group_by(
            CompetitionRegistration.group_type
        ).all()
        
        popular_groups_data = [
            {"group": group, "count": count} 
            for group, count in popular_groups
        ]
        
        return CompetitionStatistics(
            total_competitions=total_competitions,
            upcoming_competitions=upcoming_competitions,
            ongoing_competitions=ongoing_competitions,
            completed_competitions=completed_competitions,
            total_participants=total_participants,
            popular_groups=popular_groups_data
        )
