#!/usr/bin/env python3
"""
初始化示例数据脚本
用于快速创建测试数据，包括用户、校区、教练、学员等
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.app.db.database import SessionLocal, engine
from backend.app.models import *
from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole
from backend.app.models.campus import Campus
from backend.app.models.coach import Coach, CoachLevel
from backend.app.models.student import Student
from backend.app.models.coach_student import CoachStudent
from backend.app.models.payment import Payment, PaymentType, PaymentStatus
from backend.app.models.booking import Booking, BookingStatus
from backend.app.models.course import Course

def create_sample_data():
    """创建示例数据"""
    db = SessionLocal()
    
    try:
        print("开始创建示例数据...")
        
        # 检查是否已有数据，如果有则清理
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"检测到已有 {existing_users} 个用户，清理现有数据...")
            # 清理相关表数据
            db.query(Payment).delete()
            db.query(Course).delete()
            db.query(Booking).delete()
            db.query(CoachStudent).delete()
            db.query(Student).delete()
            db.query(Coach).delete()
            db.query(User).delete()
            db.query(Campus).delete()
            db.commit()
            print("数据清理完成")
        
        # 1. 创建校区
        print("创建校区...")
        main_campus = Campus(
            name="中心校区",
            address="吉林大学中心校区体育馆",
            contact_person="体育馆管理员",
            contact_phone="0431-88888888",
            contact_email="main@jlu.edu.cn",
            is_main_campus=1,
            is_active=1
        )
        
        south_campus = Campus(
            name="南岭校区",
            address="吉林大学南岭校区体育中心",
            contact_person="南岭管理员",
            contact_phone="0431-88888889",
            contact_email="south@jlu.edu.cn",
            is_main_campus=0,
            is_active=1
        )
        
        db.add_all([main_campus, south_campus])
        db.commit()
        
        # 2. 创建超级管理员
        print("创建管理员用户...")
        admin_user = User(
            username="admin",
            email="admin@jlu.edu.cn",
            password_hash=get_password_hash("admin123"),
            real_name="系统管理员",
            role=UserRole.SUPER_ADMIN,
            phone="13800138000",
            is_active=1
        )
        
        # 3. 创建校区管理员
        campus_admin_user = User(
            username="campus_admin",
            email="campus@jlu.edu.cn",
            password_hash=get_password_hash("campus123"),
            real_name="校区管理员",
            role=UserRole.CAMPUS_ADMIN,
            phone="13800138001",
            campus_id=main_campus.id,
            is_active=1
        )
        
        db.add_all([admin_user, campus_admin_user])
        db.commit()
        
        # 4. 创建教练
        print("创建教练用户...")
        coaches_data = [
            {
                "username": "coach_zhang",
                "email": "zhang@jlu.edu.cn",
                "real_name": "张教练",
                "phone": "13800138002",
                "level": CoachLevel.SENIOR,
                "hourly_rate": Decimal("200.00"),
                "achievements": "全国大学生乒乓球锦标赛冠军，从事乒乓球教学10年",
                "bio": "专业乒乓球教练，擅长技术指导和战术分析"
            },
            {
                "username": "coach_li",
                "email": "li@jlu.edu.cn",
                "real_name": "李教练",
                "phone": "13800138003",
                "level": CoachLevel.INTERMEDIATE,
                "hourly_rate": Decimal("150.00"),
                "achievements": "省级乒乓球比赛前三名，教学经验5年",
                "bio": "注重基础训练，帮助学员快速提升技术水平"
            },
            {
                "username": "coach_wang",
                "email": "wang@jlu.edu.cn", 
                "real_name": "王教练",
                "phone": "13800138004",
                "level": CoachLevel.JUNIOR,
                "hourly_rate": Decimal("80.00"),
                "achievements": "校级乒乓球比赛冠军，新手教学专家",
                "bio": "专门负责新手入门训练，耐心细致"
            }
        ]
        
        coaches = []
        for coach_data in coaches_data:
            # 创建用户
            user = User(
                username=coach_data["username"],
                email=coach_data["email"],
                password_hash=get_password_hash("coach123"),
                real_name=coach_data["real_name"],
                role=UserRole.COACH,
                phone=coach_data["phone"],
                campus_id=main_campus.id,
                is_active=1
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # 创建教练信息
            coach = Coach(
                user_id=user.id,
                level=coach_data["level"],
                hourly_rate=coach_data["hourly_rate"],
                achievements=coach_data["achievements"],
                approval_status="approved",
                approved_by=admin_user.id,
                approved_at=datetime.utcnow()
            )
            coaches.append(coach)
        
        db.add_all(coaches)
        db.commit()
        
        # 5. 创建学员
        print("创建学员用户...")
        students_data = [
            {
                "username": "student_xiaoming",
                "email": "xiaoming@stu.jlu.edu.cn",
                "real_name": "小明",
                "phone": "13800138010",
                "student_id": "2021001001",
                "emergency_contact": "张三",
                "emergency_phone": "13900139001"
            },
            {
                "username": "student_xiaohong",
                "email": "xiaohong@stu.jlu.edu.cn",
                "real_name": "小红",
                "phone": "13800138011",
                "student_id": "2021001002",
                "emergency_contact": "李四",
                "emergency_phone": "13900139002"
            },
            {
                "username": "student_xiaogang",
                "email": "xiaogang@stu.jlu.edu.cn",
                "real_name": "小刚",
                "phone": "13800138012",
                "student_id": "2021001003",
                "emergency_contact": "王五",
                "emergency_phone": "13900139003"
            }
        ]
        
        students = []
        student_users = []
        for student_data in students_data:
            # 创建用户
            user = User(
                username=student_data["username"],
                email=student_data["email"],
                password_hash=get_password_hash("student123"),
                real_name=student_data["real_name"],
                role=UserRole.STUDENT,
                phone=student_data["phone"],
                campus_id=main_campus.id,
                is_active=1
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            student_users.append(user)
            
            # 创建学员信息
            student = Student(
                user_id=user.id,
                account_balance=Decimal("1000.00")  # 初始余额
            )
            students.append(student)
        
        db.add_all(students)
        db.commit()
        
        # 6. 创建教练学员关系
        print("创建教练学员关系...")
        # 小明选择张教练和李教练
        relation1 = CoachStudent(
            coach_id=coaches[0].id,  # 张教练
            student_id=students[0].id,  # 小明
            status="approved",
            applied_by="student",
            application_message="希望提升技术水平",
            response_message="欢迎加入训练",
            responded_by=admin_user.id,
            responded_at=datetime.utcnow() - timedelta(days=9)
        )
        
        relation2 = CoachStudent(
            coach_id=coaches[1].id,  # 李教练
            student_id=students[0].id,  # 小明
            status="approved",
            applied_by="student",
            application_message="想学习基础技巧",
            response_message="好的，一起努力",
            responded_by=admin_user.id,
            responded_at=datetime.utcnow() - timedelta(days=7)
        )
        
        # 小红选择王教练
        relation3 = CoachStudent(
            coach_id=coaches[2].id,  # 王教练
            student_id=students[1].id,  # 小红
            status="approved",
            applied_by="student",
            application_message="新手求指导",
            response_message="没问题，从基础开始",
            responded_by=admin_user.id,
            responded_at=datetime.utcnow() - timedelta(days=4)
        )
        
        db.add_all([relation1, relation2, relation3])
        db.commit()
        
        # 7. 创建充值记录
        print("创建支付记录...")
        # 给学员充值
        for i, student_user in enumerate(student_users):
            payment = Payment(
                user_id=student_user.id,
                type="recharge",  # 使用字符串值
                amount=Decimal("1000.00"),
                payment_method="offline",
                status="success",  # 使用字符串值
                description="初始充值",
                transaction_id=f"INIT_{student_user.id}_{int(datetime.utcnow().timestamp())}",
                paid_at=datetime.utcnow() - timedelta(days=10)
            )
            db.add(payment)
        
        db.commit()
        
        # 8. 创建预约记录
        print("创建预约和课程记录...")
        # 创建一些历史预约和课程
        bookings_data = [
            {
                "coach_id": coaches[0].id,
                "student_id": students[0].id,
                "start_time": datetime.utcnow() - timedelta(days=3, hours=2),
                "end_time": datetime.utcnow() - timedelta(days=3, hours=1),
                "status": "completed",  # 使用字符串值
                "table_number": "T001"
            },
            {
                "coach_id": coaches[1].id,
                "student_id": students[0].id,
                "start_time": datetime.utcnow() - timedelta(days=1, hours=2),
                "end_time": datetime.utcnow() - timedelta(days=1, hours=1),
                "status": "completed",  # 使用字符串值
                "table_number": "T002"
            },
            {
                "coach_id": coaches[2].id,
                "student_id": students[1].id,
                "start_time": datetime.utcnow() + timedelta(days=1, hours=2),
                "end_time": datetime.utcnow() + timedelta(days=1, hours=3),
                "status": "confirmed",  # 使用字符串值
                "table_number": "T003"
            }
        ]
        
        for booking_data in bookings_data:
            booking = Booking(
                coach_id=booking_data["coach_id"],
                student_id=booking_data["student_id"],
                campus_id=main_campus.id,
                start_time=booking_data["start_time"],
                end_time=booking_data["end_time"],
                duration_hours=1,
                table_number=booking_data["table_number"],
                hourly_rate=Decimal("150.00"),
                total_cost=Decimal("150.00"),
                status=booking_data["status"],
                booking_message="测试预约"
            )
            db.add(booking)
            db.commit()
            db.refresh(booking)
            
            # 如果是已完成的预约，创建对应的课程记录
            if booking.status == "completed":
                course = Course(
                    coach_id=booking.coach_id,
                    student_id=booking.student_id,
                    campus_id=booking.campus_id,
                    table_number=booking.table_number,
                    start_time=booking.start_time,
                    end_time=booking.end_time,
                    duration_hours=booking.duration_hours,
                    hourly_rate=booking.hourly_rate,
                    total_cost=booking.total_cost,
                    status="completed",
                    notes="示例课程记录"
                )
                db.add(course)
                
                # 创建扣费记录
                payment = Payment(
                    user_id=booking.student_id,
                    type="booking",  # 使用字符串值
                    amount=-booking.total_cost,  # 负数表示扣费
                    payment_method="balance",
                    status="success",  # 使用字符串值
                    description=f"课程费用 - 预约ID: {booking.id}",
                    transaction_id=f"BOOKING_{booking.id}_{int(datetime.utcnow().timestamp())}",
                    paid_at=booking.start_time
                )
                db.add(payment)
        
        db.commit()
        
        print("示例数据创建完成!")
        print("\n=== 登录信息 ===")
        print("超级管理员: admin / admin123")
        print("校区管理员: campus_admin / campus123") 
        print("教练账户: coach_zhang / coach123, coach_li / coach123, coach_wang / coach123")
        print("学员账户: student_xiaoming / student123, student_xiaohong / student123, student_xiaogang / student123")
        print("\n=== 数据统计 ===")
        print(f"校区数量: {db.query(Campus).count()}")
        print(f"用户数量: {db.query(User).count()}")
        print(f"教练数量: {db.query(Coach).count()}")
        print(f"学员数量: {db.query(Student).count()}")
        print(f"师生关系: {db.query(CoachStudent).count()}")
        print(f"预约记录: {db.query(Booking).count()}")
        print(f"支付记录: {db.query(Payment).count()}")
        
    except Exception as e:
        print(f"创建示例数据时出错: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
