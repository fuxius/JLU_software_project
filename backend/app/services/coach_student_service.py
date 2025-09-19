from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime

from ..models.user import User, UserRole
from ..models.coach import Coach
from ..models.student import Student
from ..models.coach_student import CoachStudent
from ..schemas.coach_student import CoachStudentCreate, CoachStudentUpdate
from .system_log_service import SystemLogService

class CoachStudentService:
    """教练学员关系服务"""
    
    @staticmethod
    def create_relation(
        db: Session, 
        relation_data: CoachStudentCreate,
        current_user: User
    ) -> CoachStudent:
        """创建教练学员关系（学员申请选择教练）"""
        
        # 验证当前用户是学员
        if current_user.role != UserRole.STUDENT:
            raise ValueError("只有学员可以申请选择教练")
        
        # 获取学员信息
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise ValueError("学员信息不存在")
        
        # 检查学员当前教练数量（不能超过2个）
        active_relations = db.query(CoachStudent).filter(
            CoachStudent.student_id == student.id,
            CoachStudent.status == "active"
        ).count()
        
        if active_relations >= 2:
            raise ValueError("学员最多只能选择2位教练")
        
        # 检查是否已经存在关系
        existing_relation = db.query(CoachStudent).filter(
            CoachStudent.coach_id == relation_data.coach_id,
            CoachStudent.student_id == student.id,
            CoachStudent.status.in_(["pending", "active"])
        ).first()
        
        if existing_relation:
            raise ValueError("已存在与该教练的关系")
        
        # 检查教练学员数量（不能超过20个）
        coach_student_count = db.query(CoachStudent).filter(
            CoachStudent.coach_id == relation_data.coach_id,
            CoachStudent.status == "active"
        ).count()
        
        if coach_student_count >= 20:
            raise ValueError("该教练学员数量已满")
        
        # 创建关系记录
        relation = CoachStudent(
            coach_id=relation_data.coach_id,
            student_id=student.id,
            status="pending",  # 等待教练确认
            applied_at=datetime.utcnow()
        )
        
        db.add(relation)
        db.commit()
        db.refresh(relation)
        
        # 记录系统日志
        SystemLogService.log_action(
            db, current_user.id, "APPLY_COACH", 
            f"学员 {current_user.username} 申请选择教练 {relation.coach.user.username}"
        )
        
        return relation
    
    @staticmethod
    def approve_relation(
        db: Session, 
        relation_id: int, 
        approved: bool,
        current_user: User
    ) -> CoachStudent:
        """教练审核学员申请"""
        
        relation = db.query(CoachStudent).filter(CoachStudent.id == relation_id).first()
        if not relation:
            raise ValueError("关系记录不存在")
        
        # 验证当前用户是该教练
        if relation.coach.user_id != current_user.id:
            raise ValueError("只能审核自己的学员申请")
        
        if relation.status != "pending":
            raise ValueError("该申请已经处理过")
        
        if approved:
            # 再次检查教练学员数量限制
            coach_student_count = db.query(CoachStudent).filter(
                CoachStudent.coach_id == relation.coach_id,
                CoachStudent.status == "active"
            ).count()
            
            if coach_student_count >= 20:
                raise ValueError("教练学员数量已满，无法通过申请")
            
            relation.status = "active"
            relation.approved_at = datetime.utcnow()
            action = "APPROVE_STUDENT"
            message = f"教练 {current_user.username} 通过了学员 {relation.student.user.username} 的申请"
        else:
            relation.status = "rejected"
            relation.approved_at = datetime.utcnow()
            action = "REJECT_STUDENT"
            message = f"教练 {current_user.username} 拒绝了学员 {relation.student.user.username} 的申请"
        
        db.commit()
        db.refresh(relation)
        
        # 记录系统日志
        SystemLogService.log_action(db, current_user.id, action, message)
        
        return relation
    
    @staticmethod
    def get_student_relations(db: Session, student_id: int) -> List[CoachStudent]:
        """获取学员的教练关系"""
        return db.query(CoachStudent).filter(
            CoachStudent.student_id == student_id
        ).order_by(CoachStudent.created_at.desc()).all()
    
    @staticmethod
    def get_coach_relations(db: Session, coach_id: int) -> List[CoachStudent]:
        """获取教练的学员关系"""
        return db.query(CoachStudent).filter(
            CoachStudent.coach_id == coach_id
        ).order_by(CoachStudent.created_at.desc()).all()
    
    @staticmethod
    def get_pending_approvals(db: Session, current_user: User) -> List[CoachStudent]:
        """获取当前用户的待审核申请"""
        if current_user.role == UserRole.COACH:
            # 教练查看待审核的学员申请
            coach = db.query(Coach).filter(Coach.user_id == current_user.id).first()
            if not coach:
                return []
            
            return db.query(CoachStudent).filter(
                CoachStudent.coach_id == coach.id,
                CoachStudent.status == "pending"
            ).all()
        
        elif current_user.role == UserRole.STUDENT:
            # 学员查看自己的申请状态
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if not student:
                return []
            
            return db.query(CoachStudent).filter(
                CoachStudent.student_id == student.id,
                CoachStudent.status == "pending"
            ).all()
        
        return []
    
    @staticmethod
    def request_coach_change(
        db: Session,
        student_id: int,
        old_coach_id: int,
        new_coach_id: int,
        current_user: User
    ) -> bool:
        """申请更换教练"""
        
        # 验证当前用户权限
        if current_user.role != UserRole.STUDENT:
            raise ValueError("只有学员可以申请更换教练")
        
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student or student.id != student_id:
            raise ValueError("只能为自己申请更换教练")
        
        # 检查旧教练关系是否存在且有效
        old_relation = db.query(CoachStudent).filter(
            CoachStudent.coach_id == old_coach_id,
            CoachStudent.student_id == student_id,
            CoachStudent.status == "active"
        ).first()
        
        if not old_relation:
            raise ValueError("与旧教练的关系不存在或无效")
        
        # 检查新教练是否可选
        new_coach_student_count = db.query(CoachStudent).filter(
            CoachStudent.coach_id == new_coach_id,
            CoachStudent.status == "active"
        ).count()
        
        if new_coach_student_count >= 20:
            raise ValueError("新教练学员数量已满")
        
        # 创建更换申请记录（这里简化处理，实际应该有专门的更换申请表）
        # 暂时标记旧关系为更换中
        old_relation.status = "changing"
        
        # 创建新的待审核关系
        new_relation = CoachStudent(
            coach_id=new_coach_id,
            student_id=student_id,
            status="pending_change",  # 特殊状态表示更换申请
            applied_at=datetime.utcnow()
        )
        
        db.add(new_relation)
        db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db, current_user.id, "REQUEST_COACH_CHANGE", 
            f"学员 {current_user.username} 申请从教练 {old_relation.coach.user.username} 更换到教练 {new_relation.coach.user.username}"
        )
        
        return True
    
    @staticmethod
    def delete_relation(
        db: Session, 
        relation_id: int,
        current_user: User
    ) -> bool:
        """删除教练学员关系"""
        
        relation = db.query(CoachStudent).filter(CoachStudent.id == relation_id).first()
        if not relation:
            return False
        
        # 验证权限（教练或学员本人可以删除）
        can_delete = False
        if current_user.role == UserRole.COACH and relation.coach.user_id == current_user.id:
            can_delete = True
        elif current_user.role == UserRole.STUDENT and relation.student.user_id == current_user.id:
            can_delete = True
        elif current_user.role in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            can_delete = True
        
        if not can_delete:
            raise ValueError("权限不足")
        
        # 软删除（标记为已删除）
        relation.status = "deleted"
        relation.deleted_at = datetime.utcnow()
        
        db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db, current_user.id, "DELETE_COACH_STUDENT", 
            f"删除教练 {relation.coach.user.username} 和学员 {relation.student.user.username} 的关系"
        )
        
        return True
