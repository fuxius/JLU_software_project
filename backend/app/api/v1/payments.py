from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from ...db.database import get_db
from ...core.deps import get_current_user
from ...models.user import User, UserRole
from ...schemas.payment import (
    RechargeRequest, OfflinePaymentRequest, PaymentResponse, 
    BalanceResponse, PaymentSummary, RefundRequest, PaymentStatusUpdate
)
from ...services.payment_service import PaymentService
from ...services.system_log_service import SystemLogService

router = APIRouter()

@router.post("/recharge", response_model=PaymentResponse, summary="账户充值")
def create_recharge(
    recharge_data: RechargeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建充值订单"""
    if current_user.role not in [UserRole.STUDENT, UserRole.COACH]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有学员和教练可以充值"
        )
    
    payment = PaymentService.create_recharge(
        db=db,
        user_id=current_user.id,
        amount=recharge_data.amount,
        payment_method=recharge_data.payment_method,
        description=recharge_data.description
    )
    
    return PaymentResponse.from_orm(payment)

@router.post("/wechat-qr/{payment_id}", summary="生成微信支付二维码")
def generate_wechat_qr(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成微信支付二维码"""
    qr_url = PaymentService.generate_wechat_qr(db, payment_id)
    return {"qr_code_url": qr_url}

@router.post("/alipay-qr/{payment_id}", summary="生成支付宝支付二维码")
def generate_alipay_qr(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """生成支付宝支付二维码"""
    qr_url = PaymentService.generate_alipay_qr(db, payment_id)
    return {"qr_code_url": qr_url}

@router.post("/offline", response_model=PaymentResponse, summary="线下充值录入")
def create_offline_payment(
    payment_data: OfflinePaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """管理员录入线下充值"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以录入线下充值"
        )
    
    payment = PaymentService.create_offline_payment(
        db=db,
        user_id=payment_data.user_id,
        amount=payment_data.amount,
        operator_id=current_user.id,
        description=payment_data.description
    )
    
    return PaymentResponse.from_orm(payment)

@router.put("/{payment_id}/status", response_model=PaymentResponse, summary="更新支付状态")
def update_payment_status(
    payment_id: int,
    status_data: PaymentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新支付状态（支付回调或管理员操作）"""
    # 这里应该验证支付回调的签名
    # 现在简化为管理员操作
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    payment = PaymentService.confirm_payment(
        db=db,
        payment_id=payment_id,
        transaction_id=status_data.transaction_id
    )
    
    return PaymentResponse.from_orm(payment)

@router.get("/balance", response_model=BalanceResponse, summary="获取账户余额")
def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户账户余额"""
    balance = PaymentService.get_user_balance(db, current_user.id)
    
    return BalanceResponse(
        user_id=current_user.id,
        balance=balance,
        last_updated=current_user.updated_at or current_user.created_at
    )

@router.get("/balance/{user_id}", response_model=BalanceResponse, summary="获取指定用户余额")
def get_user_balance(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定用户账户余额（管理员）"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
        # 用户只能查看自己的余额
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
    
    balance = PaymentService.get_user_balance(db, user_id)
    
    # 获取用户信息
    from ...services.user_service import UserService
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return BalanceResponse(
        user_id=user_id,
        balance=balance,
        last_updated=user.updated_at or user.created_at
    )

@router.get("/records", response_model=List[PaymentResponse], summary="获取支付记录")
def get_payment_records(
    payment_type: Optional[str] = Query(None, description="支付类型"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的支付记录"""
    payments = PaymentService.get_payment_records(
        db=db,
        user_id=current_user.id,
        payment_type=payment_type,
        skip=skip,
        limit=limit
    )
    
    return [PaymentResponse.from_orm(payment) for payment in payments]

@router.get("/records/{user_id}", response_model=List[PaymentResponse], summary="获取指定用户支付记录")
def get_user_payment_records(
    user_id: int,
    payment_type: Optional[str] = Query(None, description="支付类型"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定用户的支付记录（管理员）"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    payments = PaymentService.get_payment_records(
        db=db,
        user_id=user_id,
        payment_type=payment_type,
        skip=skip,
        limit=limit
    )
    
    return [PaymentResponse.from_orm(payment) for payment in payments]

@router.get("/all", response_model=List[PaymentResponse], summary="获取所有支付记录")
def get_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有支付记录（管理员）"""
    payments = PaymentService.get_all_payments(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit
    )
    
    return [PaymentResponse.from_orm(payment) for payment in payments]

@router.get("/summary", response_model=PaymentSummary, summary="获取支付汇总")
def get_payment_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的支付汇总信息"""
    from ...models.payment import Payment, PaymentType, PaymentStatus
    
    # 计算各类金额
    recharge_total = db.query(Payment).filter(
        Payment.user_id == current_user.id,
        Payment.type == str(PaymentType.RECHARGE),
        Payment.status == str(PaymentStatus.SUCCESS)
    ).with_entities(Payment.amount).all()

    expense_total = db.query(Payment).filter(
        Payment.user_id == current_user.id,
        Payment.type.in_([str(PaymentType.BOOKING), str(PaymentType.COMPETITION)]),
        Payment.status == str(PaymentStatus.SUCCESS)
    ).with_entities(Payment.amount).all()

    refund_total = db.query(Payment).filter(
        Payment.user_id == current_user.id,
        Payment.type == str(PaymentType.REFUND),
        Payment.status == str(PaymentStatus.SUCCESS)
    ).with_entities(Payment.amount).all()
    
    payment_count = db.query(Payment).filter(
        Payment.user_id == current_user.id
    ).count()
    
    recharge_sum = sum([p.amount for p in recharge_total]) if recharge_total else Decimal('0')
    expense_sum = sum([p.amount for p in expense_total]) if expense_total else Decimal('0')
    refund_sum = sum([p.amount for p in refund_total]) if refund_total else Decimal('0')
    
    return PaymentSummary(
        total_recharge=recharge_sum,
        total_expense=expense_sum,
        total_refund=refund_sum,
        current_balance=recharge_sum - expense_sum + refund_sum,
        payment_count=payment_count
    )

@router.post("/refund", response_model=PaymentResponse, summary="申请退款")
def request_refund(
    refund_data: RefundRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """申请退款（管理员操作）"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以处理退款"
        )
    
    # 检查用户余额是否足够退款
    if not PaymentService.check_balance(db, current_user.id, refund_data.amount):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="余额不足，无法退款"
        )
    
    payment = PaymentService.refund_balance(
        db=db,
        user_id=current_user.id,
        amount=refund_data.amount,
        description=f"管理员退款: {refund_data.reason}"
    )
    
    return PaymentResponse.from_orm(payment)
