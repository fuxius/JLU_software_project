from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CampusBase(BaseModel):
    """校区基础Schema"""
    name: str
    address: str
    contact_person: str
    contact_phone: str
    contact_email: Optional[EmailStr] = None

class CampusCreate(CampusBase):
    """校区创建Schema"""
    admin_id: Optional[int] = None
    is_main_campus: Optional[int] = 0

class CampusUpdate(BaseModel):
    """校区更新Schema"""
    name: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    admin_id: Optional[int] = None
    is_main_campus: Optional[int] = None

class CampusResponse(CampusBase):
    """校区响应Schema"""
    id: int
    admin_id: Optional[int] = None
    is_main_campus: int
    is_active: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
