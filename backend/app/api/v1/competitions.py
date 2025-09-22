"""
比赛管理API
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from ...db.database import get_db
from ...models.user import User
from ...core.deps import get_current_user
from ...services.competition_service import CompetitionService
from ...schemas.competition import (
    CompetitionCreate, CompetitionUpdate, CompetitionResponse, CompetitionQuery,
    CompetitionRegistrationCreate, CompetitionRegistrationResponse,
    CompetitionMatchCreate, CompetitionMatchUpdate, CompetitionMatchResponse,
    DrawRequest, CompetitionStatistics
)

router = APIRouter()


@router.post("/", response_model=CompetitionResponse, summary="创建比赛")
def create_competition(
    competition_data: CompetitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建比赛
    
    - 只有管理员可以创建比赛
    - 自动设置比赛状态为即将开始
    - 验证日期有效性
    """
    competition = CompetitionService.create_competition(db, competition_data, current_user)
    return CompetitionResponse.from_orm(competition)


@router.get("/", response_model=List[CompetitionResponse], summary="获取比赛列表")
def get_competitions(
    status: str = Query(None, description="比赛状态筛选"),
    campus_id: int = Query(None, description="校区筛选"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db)
):
    """
    获取比赛列表
    
    - 支持按状态、校区筛选
    - 支持分页
    - 返回报名人数统计
    """
    query = CompetitionQuery(
        status=status,
        campus_id=campus_id,
        page=page,
        size=size
    )
    competitions = CompetitionService.get_competitions(db, query)
    return [CompetitionResponse.from_orm(comp) for comp in competitions]


@router.get("/my-registrations", response_model=List[CompetitionRegistrationResponse], summary="获取我的所有报名")
def get_my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户的所有比赛报名
    
    - 只返回当前用户的报名记录
    - 包含比赛信息
    """
    from ...models.student import Student
    from ...models.competition import CompetitionRegistration
    
    # 获取当前用户的student记录
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    
    # 获取该学员的所有报名记录
    registrations = db.query(CompetitionRegistration).options(
        joinedload(CompetitionRegistration.student).joinedload(Student.user),
        joinedload(CompetitionRegistration.competition)
    ).filter(CompetitionRegistration.student_id == student.id).all()
    
    return [CompetitionRegistrationResponse.from_orm(reg) for reg in registrations]


@router.get("/{competition_id}", response_model=CompetitionResponse, summary="获取比赛详情")
def get_competition(
    competition_id: int,
    db: Session = Depends(get_db)
):
    """获取比赛详情"""
    competition = CompetitionService.get_competition(db, competition_id)
    return CompetitionResponse.from_orm(competition)


@router.put("/{competition_id}", response_model=CompetitionResponse, summary="更新比赛信息")
def update_competition(
    competition_id: int,
    competition_data: CompetitionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新比赛信息
    
    - 只有管理员可以更新
    - 比赛开始后限制可修改字段
    """
    competition = CompetitionService.update_competition(db, competition_id, competition_data, current_user)
    return CompetitionResponse.from_orm(competition)


@router.post("/{competition_id}/register", response_model=CompetitionRegistrationResponse, summary="报名比赛")
def register_competition(
    competition_id: int,
    group_type: str = Query(..., pattern="^[ABC]$", description="报名组别: A/B/C"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    报名比赛
    
    - 只有学员可以报名
    - 检查比赛状态和截止时间
    - 自动创建支付订单
    - 检查重复报名和人数限制
    """
    registration_data = CompetitionRegistrationCreate(
        competition_id=competition_id,
        group_type=group_type
    )
    registration = CompetitionService.register_competition(db, registration_data, current_user)
    return CompetitionRegistrationResponse.from_orm(registration)


@router.get("/{competition_id}/registrations", response_model=List[CompetitionRegistrationResponse], summary="获取报名列表")
def get_registrations(
    competition_id: int,
    group_type: str = Query(None, pattern="^[ABC]$", description="组别筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取比赛报名列表
    
    - 管理员可查看所有报名
    - 学员只能查看自己的报名
    """
    registrations = CompetitionService.get_registrations(db, competition_id, group_type)
    
    # 权限控制
    if current_user.role.value != "admin":
        # 获取当前用户的student记录
        from ...models.student import Student
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if student:
            registrations = [
                reg for reg in registrations 
                if reg.student_id == student.id
            ]
        else:
            registrations = []
    
    return [CompetitionRegistrationResponse.from_orm(reg) for reg in registrations]


@router.post("/{competition_id}/draw", response_model=List[CompetitionMatchResponse], summary="生成比赛对阵")
def generate_draw(
    competition_id: int,
    group_type: str = Query(..., pattern="^[ABC]$", description="组别"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    生成比赛对阵
    
    - 只有管理员可以操作
    - 随机分配对阵
    - 处理轮空情况
    - 更新比赛状态
    """
    draw_request = DrawRequest(
        competition_id=competition_id,
        group_type=group_type
    )
    matches = CompetitionService.generate_draw(db, draw_request, current_user)
    return [CompetitionMatchResponse.from_orm(match) for match in matches]


@router.get("/{competition_id}/matches", response_model=List[CompetitionMatchResponse], summary="获取比赛对阵")
def get_matches(
    competition_id: int,
    group_type: str = Query(None, pattern="^[ABC]$", description="组别筛选"),
    db: Session = Depends(get_db)
):
    """获取比赛对阵列表"""
    matches = CompetitionService.get_competition_matches(db, competition_id, group_type)
    return [CompetitionMatchResponse.from_orm(match) for match in matches]


@router.put("/matches/{match_id}", response_model=CompetitionMatchResponse, summary="录入比赛结果")
def update_match_result(
    match_id: int,
    match_data: CompetitionMatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    录入比赛结果
    
    - 只有管理员可以操作
    - 自动判定获胜者
    - 更新比赛状态
    """
    match = CompetitionService.update_match_result(db, match_id, match_data, current_user)
    return CompetitionMatchResponse.from_orm(match)


@router.post("/registrations/{registration_id}/confirm", response_model=CompetitionRegistrationResponse, summary="确认报名")
def confirm_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    确认报名（支付成功后调用）
    
    - 学员确认自己的报名
    - 管理员可确认任意报名
    - 检查支付状态
    """
    registration = CompetitionService.confirm_registration(db, registration_id, current_user)
    return CompetitionRegistrationResponse.from_orm(registration)


@router.get("/statistics/summary", response_model=CompetitionStatistics, summary="获取比赛统计")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取比赛统计信息
    
    - 总比赛数、状态分布
    - 参赛人数统计
    - 热门组别分析
    """
    return CompetitionService.get_competition_statistics(db)
