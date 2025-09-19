# 数据库设计文档

## 数据库概述

乒乓球培训管理系统支持两种数据库：
- **SQLite** (默认): 轻量级，零配置，适合开发和小规模部署
- **PostgreSQL**: 功能强大，适合生产环境和大规模部署

系统使用SQLAlchemy ORM进行数据访问，确保数据库无关性。数据库设计遵循第三范式，确保数据一致性和完整性。

## 数据表结构

### 1. 用户基础表 (users)

存储所有用户的基本信息，支持四种用户角色。

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    gender VARCHAR(10),
    age INTEGER,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    role user_role_enum NOT NULL,
    campus_id INTEGER,
    avatar_url VARCHAR(255),
    id_number VARCHAR(18),
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TYPE user_role_enum AS ENUM ('super_admin', 'campus_admin', 'coach', 'student');
```

**字段说明:**
- `username`: 登录用户名，唯一
- `password_hash`: 密码哈希值
- `role`: 用户角色（超级管理员/校区管理员/教练/学员）
- `campus_id`: 所属校区ID
- `is_active`: 账户状态（1=激活，0=停用）

### 2. 校区表 (campuses)

存储校区基本信息和管理关系。

```sql
CREATE TABLE campuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address TEXT NOT NULL,
    contact_person VARCHAR(50) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    contact_email VARCHAR(100),
    admin_id INTEGER REFERENCES users(id),
    is_main_campus INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**字段说明:**
- `admin_id`: 校区管理员用户ID
- `is_main_campus`: 是否为中心校区（1=是，0=否）
- `is_active`: 校区状态

### 3. 教练表 (coaches)

存储教练的专业信息和审核状态。

```sql
CREATE TABLE coaches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    level coach_level_enum NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL,
    achievements TEXT,
    max_students INTEGER DEFAULT 20,
    current_students INTEGER DEFAULT 0,
    approval_status VARCHAR(20) DEFAULT 'pending',
    approved_by INTEGER REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TYPE coach_level_enum AS ENUM ('senior', 'intermediate', 'junior');
```

**字段说明:**
- `level`: 教练级别（高级/中级/初级）
- `hourly_rate`: 每小时收费标准
- `max_students`: 最多指导学员数
- `approval_status`: 审核状态（pending/approved/rejected）

### 4. 学员表 (students)

存储学员的账户和限制信息。

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    account_balance DECIMAL(10,2) DEFAULT 0.00,
    max_coaches INTEGER DEFAULT 2,
    current_coaches INTEGER DEFAULT 0,
    monthly_cancellations INTEGER DEFAULT 0,
    last_cancellation_reset TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**字段说明:**
- `account_balance`: 账户余额
- `monthly_cancellations`: 本月取消预约次数
- `last_cancellation_reset`: 上次重置取消次数时间

### 5. 教练学员关系表 (coach_students)

管理教练和学员的双选关系。

```sql
CREATE TABLE coach_students (
    id SERIAL PRIMARY KEY,
    coach_id INTEGER NOT NULL REFERENCES coaches(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    status VARCHAR(20) DEFAULT 'pending',
    applied_by VARCHAR(20) NOT NULL,
    application_message TEXT,
    response_message TEXT,
    responded_by INTEGER REFERENCES users(id),
    responded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(coach_id, student_id)
);
```

**字段说明:**
- `status`: 申请状态（pending/approved/rejected）
- `applied_by`: 申请发起方（student/admin）

### 6. 课程预约表 (bookings)

存储课程预约信息和状态。

```sql
CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    coach_id INTEGER NOT NULL REFERENCES coaches(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    campus_id INTEGER NOT NULL REFERENCES campuses(id),
    table_number VARCHAR(10),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_hours DECIMAL(3,1) NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    booking_message TEXT,
    response_message TEXT,
    cancelled_by INTEGER REFERENCES users(id),
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    cancel_confirmed_by INTEGER REFERENCES users(id),
    cancel_confirmed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**字段说明:**
- `status`: 预约状态（pending/confirmed/rejected/cancelled/completed）
- `table_number`: 球台编号
- `total_cost`: 总费用

### 7. 课程记录表 (courses)

存储已完成的课程信息。

```sql
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    coach_id INTEGER NOT NULL REFERENCES coaches(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    campus_id INTEGER NOT NULL REFERENCES campuses(id),
    table_number VARCHAR(10) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_hours DECIMAL(3,1) NOT NULL,
    hourly_rate DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### 8. 支付记录表 (payments)

存储所有支付相关的记录。

```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending',
    transaction_id VARCHAR(100),
    payment_type VARCHAR(20) NOT NULL,
    related_id INTEGER,
    qr_code_url VARCHAR(255),
    payment_time TIMESTAMP WITH TIME ZONE,
    refund_time TIMESTAMP WITH TIME ZONE,
    refund_reason TEXT,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**字段说明:**
- `payment_method`: 支付方式（wechat/alipay/offline）
- `payment_type`: 支付类型（recharge/course/competition/license）
- `payment_status`: 支付状态（pending/completed/failed/refunded）

### 9. 课后评价表 (evaluations)

存储课程结束后的评价信息。

```sql
CREATE TABLE evaluations (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id),
    evaluator_id INTEGER NOT NULL REFERENCES users(id),
    evaluator_type VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    rating INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

**字段说明:**
- `evaluator_type`: 评价人类型（student/coach）
- `rating`: 评分（1-5星）

### 10. 比赛表 (competitions)

存储比赛基本信息。

```sql
CREATE TABLE competitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    campus_id INTEGER NOT NULL REFERENCES campuses(id),
    competition_date TIMESTAMP WITH TIME ZONE NOT NULL,
    registration_fee DECIMAL(10,2) DEFAULT 30.00,
    registration_deadline TIMESTAMP WITH TIME ZONE NOT NULL,
    max_participants_per_group INTEGER DEFAULT 6,
    status VARCHAR(20) DEFAULT 'registration_open',
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

### 11. 比赛报名表 (competition_registrations)

存储比赛报名信息和赛程安排。

```sql
CREATE TABLE competition_registrations (
    id SERIAL PRIMARY KEY,
    competition_id INTEGER NOT NULL REFERENCES competitions(id),
    student_id INTEGER NOT NULL REFERENCES students(id),
    group_type VARCHAR(20) NOT NULL,
    player_number INTEGER,
    table_assignments TEXT,
    match_schedule TEXT,
    payment_id INTEGER REFERENCES payments(id),
    registration_status VARCHAR(20) DEFAULT 'registered',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(competition_id, student_id)
);
```

**字段说明:**
- `group_type`: 报名组别（group_a/group_b/group_c）
- `table_assignments`: 球台分配（JSON格式）
- `match_schedule`: 比赛赛程（JSON格式）

### 12. 系统日志表 (system_logs)

记录所有重要的系统操作。

```sql
CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    target_type VARCHAR(50),
    target_id INTEGER,
    description TEXT NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    extra_data TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 13. 软件许可证表 (licenses)

管理软件授权和付费服务。

```sql
CREATE TABLE licenses (
    id SERIAL PRIMARY KEY,
    license_key VARCHAR(255) UNIQUE NOT NULL,
    organization_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(100) NOT NULL,
    contact_email VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    device_fingerprint VARCHAR(255),
    annual_fee DECIMAL(10,2) DEFAULT 500.00,
    purchase_date TIMESTAMP WITH TIME ZONE NOT NULL,
    expiry_date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active INTEGER DEFAULT 1,
    activation_date TIMESTAMP WITH TIME ZONE,
    last_validation TIMESTAMP WITH TIME ZONE,
    validation_count INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 索引设计

为了优化查询性能，创建以下索引：

```sql
-- 用户表索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_campus_id ON users(campus_id);
CREATE INDEX idx_users_role ON users(role);

-- 预约表索引
CREATE INDEX idx_bookings_coach_id ON bookings(coach_id);
CREATE INDEX idx_bookings_student_id ON bookings(student_id);
CREATE INDEX idx_bookings_start_time ON bookings(start_time);
CREATE INDEX idx_bookings_status ON bookings(status);

-- 支付表索引
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_payment_type ON payments(payment_type);
CREATE INDEX idx_payments_payment_status ON payments(payment_status);
CREATE INDEX idx_payments_created_at ON payments(created_at);

-- 系统日志索引
CREATE INDEX idx_system_logs_user_id ON system_logs(user_id);
CREATE INDEX idx_system_logs_action ON system_logs(action);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);
```

## 外键约束

```sql
-- 用户表外键
ALTER TABLE users ADD CONSTRAINT fk_users_campus_id 
    FOREIGN KEY (campus_id) REFERENCES campuses(id);

-- 校区表外键
ALTER TABLE campuses ADD CONSTRAINT fk_campuses_admin_id 
    FOREIGN KEY (admin_id) REFERENCES users(id);

-- 教练表外键
ALTER TABLE coaches ADD CONSTRAINT fk_coaches_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE coaches ADD CONSTRAINT fk_coaches_approved_by 
    FOREIGN KEY (approved_by) REFERENCES users(id);

-- 学员表外键
ALTER TABLE students ADD CONSTRAINT fk_students_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id);

-- 其他表的外键约束...
```

## 触发器和函数

### 1. 自动更新时间戳触发器

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为需要的表创建触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campuses_updated_at BEFORE UPDATE ON campuses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 其他表的触发器...
```

### 2. 账户余额检查函数

```sql
CREATE OR REPLACE FUNCTION check_student_balance()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.account_balance < 0 THEN
        RAISE EXCEPTION '账户余额不能为负数';
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER check_balance BEFORE UPDATE ON students
    FOR EACH ROW EXECUTE FUNCTION check_student_balance();
```

## 数据库连接配置

### SQLite配置 (默认)

```python
# database.py - SQLite配置
from sqlalchemy import create_engine

# SQLite配置
DATABASE_URL = "sqlite:///./tabletennis.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite特有配置
    echo=False  # 开发时可设为True查看SQL
)
```

### PostgreSQL配置 (生产环境)

```python
# database.py - PostgreSQL配置
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# PostgreSQL配置
DATABASE_URL = "postgresql://user:pass@localhost:5432/tabletennis_db"
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)
```

### 数据库切换

通过环境变量轻松切换数据库：

```bash
# 使用SQLite
DATABASE_URL=sqlite:///./tabletennis.db

# 使用PostgreSQL  
DATABASE_URL=postgresql://user:pass@localhost:5432/tabletennis_db
```

## 数据迁移

使用Alembic进行数据库版本管理：

```bash
# 初始化迁移环境
alembic init alembic

# 创建初始迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

## 备份策略

### 1. 定时备份脚本

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h localhost -U username -d tabletennis_db > backup_$DATE.sql
```

### 2. 数据保留策略

- 日备份保留30天
- 周备份保留12周
- 月备份保留12个月

## 性能优化建议

1. **索引优化**: 根据查询模式创建合适的索引
2. **分区表**: 对于大量数据的表考虑分区
3. **连接池**: 合理配置数据库连接池
4. **查询优化**: 使用EXPLAIN分析慢查询
5. **缓存策略**: 对热点数据使用Redis缓存

## 安全考虑

1. **数据加密**: 敏感数据字段加密存储
2. **访问控制**: 数据库用户权限最小化
3. **审计日志**: 记录所有数据修改操作
4. **备份加密**: 备份文件加密存储
5. **网络安全**: 使用SSL连接数据库

---

本文档描述了乒乓球培训管理系统的完整数据库设计，包括表结构、索引、约束和优化建议。
