from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...db.database import get_db
from ...schemas.campus import CampusCreate, CampusUpdate, CampusResponse
from ...services.campus_service import CampusService
from ...core.deps import get_current_user, get_super_admin, get_admin
from ...models.user import User

router = APIRouter()

@router.post("/", response_model=CampusResponse, summary="创建校区")
def create_campus(
    campus_data: CampusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """创建校区"""
    campus = CampusService.create_campus(db, campus_data, current_user)
    return CampusResponse.from_orm(campus)

@router.get("/", response_model=List[CampusResponse], summary="获取所有校区")
def get_campuses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取所有校区"""
    campuses = CampusService.get_all_campuses(db, skip, limit)
    return [CampusResponse.from_orm(campus) for campus in campuses]

@router.get("/main", response_model=CampusResponse, summary="获取中心校区")
def get_main_campus(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取中心校区"""
    campus = CampusService.get_main_campus(db)
    if not campus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="中心校区不存在"
        )
    return CampusResponse.from_orm(campus)

@router.get("/{campus_id}", response_model=CampusResponse, summary="获取校区信息")
def get_campus(
    campus_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取校区信息"""
    campus = CampusService.get_campus_by_id(db, campus_id)
    if not campus:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="校区不存在"
        )
    return CampusResponse.from_orm(campus)

@router.put("/{campus_id}", response_model=CampusResponse, summary="更新校区信息")
def update_campus(
    campus_id: int,
    campus_data: CampusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """更新校区信息"""
    campus = CampusService.update_campus(db, campus_id, campus_data, current_user)
    return CampusResponse.from_orm(campus)

@router.delete("/{campus_id}", summary="删除校区")
def delete_campus(
    campus_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """删除校区"""
    success = CampusService.delete_campus(db, campus_id, current_user)
    if success:
        return {"message": "校区删除成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="删除校区失败"
        )

@router.post("/{campus_id}/assign-admin/{admin_id}", response_model=CampusResponse, summary="指定校区管理员")
def assign_campus_admin(
    campus_id: int,
    admin_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """指定校区管理员"""
    campus = CampusService.assign_admin(db, campus_id, admin_id, current_user)
    return CampusResponse.from_orm(campus)
