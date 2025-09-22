from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException, status

from ..models.payment import Payment, PaymentStatus, PaymentType
from ..models.user import User, UserRole
from ..models.student import Student
from ..schemas.payment import RechargeRequest, PaymentResponse
from ..services.system_log_service import SystemLogService

class PaymentService:
    """支付服务"""
    
    @staticmethod
    def check_balance(db: Session, user_id: int, amount: Decimal) -> bool:
        """检查用户余额是否足够"""
        balance = PaymentService.get_user_balance(db, user_id)
        return balance >= amount
    
    @staticmethod
    def get_user_balance(db: Session, user_id: int) -> Decimal:
        """获取用户账户余额"""
        # 计算充值总额
        recharge_total = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.type == str(PaymentType.RECHARGE),
            Payment.status == str(PaymentStatus.SUCCESS)
        ).with_entities(Payment.amount).all()

        recharge_sum = sum([p.amount for p in recharge_total]) if recharge_total else Decimal('0')

        # 计算消费总额
        expense_total = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.type.in_([str(PaymentType.BOOKING), str(PaymentType.COMPETITION)]),
            Payment.status == str(PaymentStatus.SUCCESS)
        ).with_entities(Payment.amount).all()

        expense_sum = sum([p.amount for p in expense_total]) if expense_total else Decimal('0')

        # 计算退费总额
        refund_total = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.type == str(PaymentType.REFUND),
            Payment.status == str(PaymentStatus.SUCCESS)
        ).with_entities(Payment.amount).all()

        refund_sum = sum([p.amount for p in refund_total]) if refund_total else Decimal('0')

        return recharge_sum - expense_sum + refund_sum
    
    @staticmethod
    def create_recharge(db: Session, user_id: int, amount: Decimal, payment_method: str, description: Optional[str] = None) -> Payment:
        """创建充值记录
        说明：为方便当前环境演示，线上充值创建后即视为成功并计入余额。
        如需真实支付流程，可改为 PENDING 并通过回调/管理接口置为 SUCCESS。
        """
        payment = Payment(
            user_id=user_id,
            type=str(PaymentType.RECHARGE),
            amount=amount,
            payment_method=payment_method,
            status=str(PaymentStatus.SUCCESS),
            description=description or f"账户充值 {amount}元",
            paid_at=datetime.now()
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        return payment
    
    @staticmethod
    def confirm_payment(db: Session, payment_id: int, transaction_id: Optional[str] = None) -> Payment:
        """确认支付成功"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        if payment.status != str(PaymentStatus.PENDING):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="支付状态无法更新"
            )
        
        payment.status = str(PaymentStatus.SUCCESS)
        payment.transaction_id = transaction_id
        payment.paid_at = datetime.now()
        
        db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=payment.user_id,
            action="payment_success",
            target_type="payment",
            target_id=payment.id,
            description=f"支付成功: {payment.amount}元"
        )
        
        return payment
    
    @staticmethod
    def deduct_balance(db: Session, user_id: int, amount: Decimal, description: str) -> bool:
        """扣除用户余额"""
        # 检查余额
        if not PaymentService.check_balance(db, user_id, amount):
            return False
        
        # 创建消费记录
        payment = Payment(
            user_id=user_id,
            type=PaymentType.BOOKING,
            amount=amount,
            payment_method="balance",
            status=str(PaymentStatus.SUCCESS),
            description=description,
            paid_at=datetime.now()
        )
        
        db.add(payment)
        db.commit()
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=user_id,
            action="balance_deduct",
            target_type="payment",
            target_id=payment.id,
            description=f"余额扣除: {amount}元 - {description}"
        )
        
        return True
    
    @staticmethod
    def refund_balance(db: Session, user_id: int, amount: Decimal, description: str) -> Payment:
        """退费到用户余额"""
        payment = Payment(
            user_id=user_id,
            type=PaymentType.REFUND,
            amount=amount,
            payment_method="balance",
            status=str(PaymentStatus.SUCCESS),
            description=description,
            paid_at=datetime.now()
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=user_id,
            action="balance_refund",
            target_type="payment",
            target_id=payment.id,
            description=f"余额退费: {amount}元 - {description}"
        )
        
        return payment
    
    @staticmethod
    def create_offline_payment(db: Session, user_id: int, amount: Decimal, operator_id: int, description: Optional[str] = None) -> Payment:
        """创建线下支付记录（管理员录入）"""
        payment = Payment(
            user_id=user_id,
            type=PaymentType.RECHARGE,
            amount=amount,
            payment_method="offline",
            status=str(PaymentStatus.SUCCESS),
            description=description or f"线下充值 {amount}元",
            paid_at=datetime.now()
        )
        
        db.add(payment)
        db.commit()
        db.refresh(payment)
        
        # 记录系统日志
        SystemLogService.log_action(
            db=db,
            user_id=operator_id,
            action="offline_payment",
            target_type="payment",
            target_id=payment.id,
            description=f"线下充值录入: 用户ID {user_id}, 金额 {amount}元"
        )
        
        return payment
    
    @staticmethod
    def get_payment_records(db: Session, user_id: int, payment_type: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Payment]:
        """获取支付记录"""
        query = db.query(Payment).filter(Payment.user_id == user_id)

        if payment_type:
            query = query.filter(Payment.type == payment_type)

        return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_payment_records_by_type(db: Session, user_id: int, payment_type_enum: PaymentType, skip: int = 0, limit: int = 100) -> List[Payment]:
        """根据枚举类型获取支付记录"""
        query = db.query(Payment).filter(
            Payment.user_id == user_id,
            Payment.type == str(payment_type_enum)
        )

        return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_payments(db: Session, current_user: User, skip: int = 0, limit: int = 100) -> List[Payment]:
        """获取所有支付记录（管理员）"""
        if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.CAMPUS_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足"
            )
        
        query = db.query(Payment)
        
        # 校区管理员只能看自己校区的支付记录
        if current_user.role == UserRole.CAMPUS_ADMIN:
            query = query.join(User).filter(User.campus_id == current_user.campus_id)
        
        return query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def generate_wechat_qr(db: Session, payment_id: int) -> str:
        """生成微信支付二维码（模拟）"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        # 这里应该调用微信支付API生成二维码
        # 现在返回模拟的二维码URL
        qr_url = f"https://api.tabletennis.com/wechat/pay?payment_id={payment_id}&amount={payment.amount}"
        
        return qr_url
    
    @staticmethod
    def generate_alipay_qr(db: Session, payment_id: int) -> str:
        """生成支付宝支付二维码（模拟）"""
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="支付记录不存在"
            )
        
        # 这里应该调用支付宝API生成二维码
        # 现在返回模拟的二维码URL
        qr_url = f"https://api.tabletennis.com/alipay/pay?payment_id={payment_id}&amount={payment.amount}"
        
        return qr_url
