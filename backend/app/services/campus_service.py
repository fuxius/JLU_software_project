from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.campus import Campus
from ..models.user import User, UserRole
from ..schemas.campus import CampusCreate, CampusUpdate
from ..services.system_log_service import SystemLogService
from fastapi import HTTPException, status

class CampusService:
    """校区服务"""
    
    @staticmethod
    def create_campus(db: Session, campus_data: CampusCreate, current_user: User) -> Campus:
        """创建校区"""
        if current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有超级管理员可以创建校区"
            )
        
        # 检查校区名称是否已存在
        if db.query(Campus).filter(Campus.name == campus_data.name).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="校区名称已存在"
            )
        
        # 如果设置为中心校区，需要将其他校区的中心校区标记取消
        if campus_data.is_main_campus:
            db.query(Campus).filter(Campus.is_main_campus == 1).update(
                {Campus.is_main_campus: 0}
            )
        
        db_campus = Campus(**campus_data.dict())
        db.add(db_campus)
        db.commit()
        db.refresh(db_campus)
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="campus_create",
            target_type="campus",
            target_id=db_campus.id,
            description=f"创建校区: {db_campus.name}"
        )
        
        return db_campus
    
    @staticmethod
    def get_campus_by_id(db: Session, campus_id: int) -> Optional[Campus]:
        """根据ID获取校区"""
        return db.query(Campus).filter(Campus.id == campus_id, Campus.is_active == 1).first()
    
    @staticmethod
    def get_all_campuses(db: Session, skip: int = 0, limit: int = 100) -> List[Campus]:
        """获取所有校区"""
        return db.query(Campus).filter(Campus.is_active == 1).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_main_campus(db: Session) -> Optional[Campus]:
        """获取中心校区"""
        return db.query(Campus).filter(
            Campus.is_main_campus == 1, 
            Campus.is_active == 1
        ).first()
    
    @staticmethod
    def update_campus(db: Session, campus_id: int, campus_data: CampusUpdate, current_user: User) -> Campus:
        """更新校区信息"""
        if current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有超级管理员可以更新校区信息"
            )
        
        campus = db.query(Campus).filter(Campus.id == campus_id).first()
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="校区不存在"
            )
        
        # 如果设置为中心校区，需要将其他校区的中心校区标记取消
        if campus_data.is_main_campus and campus_data.is_main_campus == 1:
            db.query(Campus).filter(Campus.id != campus_id, Campus.is_main_campus == 1).update(
                {Campus.is_main_campus: 0}
            )
        
        # 更新字段
        for field, value in campus_data.dict(exclude_unset=True).items():
            setattr(campus, field, value)
        
        db.commit()
        db.refresh(campus)
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="campus_update",
            target_type="campus",
            target_id=campus_id,
            description=f"更新校区信息: {campus.name}"
        )
        
        return campus
    
    @staticmethod
    def delete_campus(db: Session, campus_id: int, current_user: User) -> bool:
        """删除校区(软删除)"""
        if current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有超级管理员可以删除校区"
            )
        
        campus = db.query(Campus).filter(Campus.id == campus_id).first()
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="校区不存在"
            )
        
        # 检查是否有用户关联到此校区
        user_count = db.query(User).filter(User.campus_id == campus_id).count()
        if user_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="校区下还有用户，无法删除"
            )
        
        campus.is_active = 0
        db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="campus_delete",
            target_type="campus",
            target_id=campus_id,
            description=f"删除校区: {campus.name}"
        )
        
        return True
    
    @staticmethod
    def assign_admin(db: Session, campus_id: int, admin_id: int, current_user: User) -> Campus:
        """指定校区管理员"""
        if current_user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="只有超级管理员可以指定校区管理员"
            )
        
        campus = db.query(Campus).filter(Campus.id == campus_id).first()
        if not campus:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="校区不存在"
            )
        
        admin_user = db.query(User).filter(User.id == admin_id).first()
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="管理员用户不存在"
            )
        
        # 更新用户角色为校区管理员
        admin_user.role = UserRole.CAMPUS_ADMIN
        admin_user.campus_id = campus_id
        
        # 更新校区管理员
        campus.admin_id = admin_id
        
        db.commit()
        db.refresh(campus)
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=current_user.id,
            action="campus_assign_admin",
            target_type="campus",
            target_id=campus_id,
            description=f"为校区 {campus.name} 指定管理员: {admin_user.real_name}"
        )
        
        return campus
