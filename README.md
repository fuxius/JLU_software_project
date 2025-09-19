# 乒乓球培训管理系统

一个基于 FastAPI + Vue 3 的现代化乒乓球培训机构管理系统，支持多校区管理、用户角色权限、课程预约、支付管理、赛事组织等完整功能。

## 🚀 技术栈

### 后端
- **FastAPI** - 现代化的Python Web框架
- **SQLAlchemy** - Python ORM框架
- **PostgreSQL** - 关系型数据库
- **JWT** - 身份认证
- **Pydantic** - 数据验证
- **Alembic** - 数据库迁移工具

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript
- **Element Plus** - Vue 3 UI组件库
- **Pinia** - Vue状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP客户端
- **Vite** - 前端构建工具

### 开发工具
- **uv** - Python包管理器
- **ESLint** - JavaScript代码检查
- **Prettier** - 代码格式化

## 📋 功能特性

### 用户角色管理
- **超级管理员**: 系统全局管理，校区创建与管理
- **校区管理员**: 校区内用户管理，教练审核
- **教练**: 学员管理，课程安排，课后评价
- **学员**: 教练选择，课程预约，比赛报名

### 核心功能模块

#### 1. 多校区管理
- 中心校区与分校区管理
- 校区信息维护（地址、联系方式等）
- 校区管理员指定

#### 2. 用户管理
- 学员公开注册（无需审核）
- 教练注册申请（需管理员审核）
- 用户信息维护（头像、密码等）
- 角色权限控制

#### 3. 教练选择系统
- 教练信息查询（按姓名、性别、年龄）
- 双选关系建立（学员申请+教练确认）
- 限制规则：学员最多2个教练，教练最多20个学员
- 更换教练（需三方确认）

#### 4. 课程预约管理
- 教练课表展示
- 球台自动/手动分配
- 预约确认机制
- 24小时前取消规则
- 每月最多取消3次限制
- 课前1小时提醒

#### 5. 财务计费系统
- 学员账户余额管理
- 多种充值方式（微信/支付宝/线下）
- 自动扣费（按教练级别收费）
- 自动退费（取消预约时）
- 支付记录查询

#### 6. 课后评价系统
- 课程结束后自动发起评价
- 学员评价：收获与教训
- 教练评价：表现与建议
- 评价历史查询

#### 7. 赛事管理系统
- 月度比赛组织（甲乙丙三组）
- 在线报名与缴费
- 自动赛程编排（循环赛/淘汰赛）
- 球台随机分配
- 比赛结果管理

#### 8. 系统日志
- 用户操作记录
- 管理员操作审计
- 系统安全监控

#### 9. 软件授权系统
- 年费制付费服务（500元/年）
- 设备绑定（一机一码）
- 到期自动锁定
- 续费管理

## 🛠️ 环境要求

### 后端环境
- Python 3.9+
- PostgreSQL 12+
- uv (Python包管理器)

### 前端环境
- Node.js 16+
- npm 或 yarn

## 📦 本地环境配置

### 环境要求

- **Python**: 3.9 或更高版本
- **Node.js**: 16 或更高版本  
- **数据库**: SQLite (默认，无需安装) 或 PostgreSQL 12+ (可选)
- **uv**: Python包管理器
- **Git**: 版本控制

### 1. 基础环境安装

#### 安装Python (如果未安装)
```bash
# macOS (使用Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-pip

# CentOS/RHEL
sudo yum install python3.11 python3.11-pip

# Windows
# 从 https://www.python.org/downloads/ 下载安装
```

#### 安装Node.js (如果未安装)
```bash
# macOS (使用Homebrew)
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Windows
# 从 https://nodejs.org/ 下载安装
```

#### 安装PostgreSQL (如果未安装)
```bash
# macOS (使用Homebrew)
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Windows
# 从 https://www.postgresql.org/download/windows/ 下载安装
```

#### 安装uv (Python包管理器)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 重启终端或执行
source ~/.bashrc  # Linux
source ~/.zshrc   # macOS with zsh
```

### 2. 克隆项目
```bash
git clone <repository-url>
cd JLU_software_project
```

### 3. 数据库配置

#### 创建数据库用户和数据库
```bash
# 切换到postgres用户
sudo -u postgres psql

# 在PostgreSQL命令行中执行
CREATE USER tabletennis_user WITH PASSWORD 'your_password';
CREATE DATABASE tabletennis_db OWNER tabletennis_user;
GRANT ALL PRIVILEGES ON DATABASE tabletennis_db TO tabletennis_user;
\q
```

#### 测试数据库连接
```bash
psql -h localhost -U tabletennis_user -d tabletennis_db
# 输入密码后如果能连接成功，说明数据库配置正确
```

### 4. 后端环境配置

#### 创建并配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑环境变量文件
vim .env  # 或使用其他编辑器
```

**.env 文件配置示例：**
```bash
# 数据库配置
DATABASE_URL=postgresql://tabletennis_user:your_password@localhost:5432/tabletennis_db

# JWT配置  
SECRET_KEY=your-super-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
DEBUG=true

# 支付配置（可选，后续配置）
WECHAT_PAY_APP_ID=
WECHAT_PAY_MCH_ID=
ALIPAY_APP_ID=

# 许可证服务器配置（可选）
LICENSE_SERVER_URL=https://license.example.com
LICENSE_VALIDATION_KEY=
```

#### 安装Python依赖
```bash
# 创建虚拟环境并安装依赖
uv sync

# 安装开发依赖
uv sync --extra dev

# 验证安装
uv run python --version
```

#### 初始化数据库
```bash
# 创建数据库迁移文件
uv run alembic init alembic

# 创建初始迁移
uv run alembic revision --autogenerate -m "Initial migration"

# 应用迁移
uv run alembic upgrade head
```

#### 启动后端服务
```bash
# 方式1: 使用项目脚本（推荐）
uv run dev

# 方式2: 直接运行启动脚本
uv run python backend/run.py

# 方式3: 使用uvicorn命令
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**验证后端启动成功：**
- 访问 http://localhost:8000 应该看到欢迎信息
- 访问 http://localhost:8000/docs 查看API文档
- 访问 http://localhost:8000/health 检查健康状态

### 5. 前端环境配置

#### 安装前端依赖
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 或使用yarn
yarn install
```

#### 启动前端开发服务器
```bash
# 启动开发服务器
npm run dev

# 或使用yarn
yarn dev
```

**验证前端启动成功：**
- 访问 http://localhost:3000 应该看到登录页面

### 6. 一键环境初始化 ⭐

**推荐方式：使用SQLite轻量级数据库**

```bash
# 运行SQLite版本的初始化脚本（推荐）
./scripts/init-sqlite.sh
```

**SQLite的优势：**
- ✅ **零配置**: 无需安装和配置数据库服务
- ✅ **轻量级**: 数据库文件自动创建，完全便携
- ✅ **快速启动**: 几分钟内完成环境搭建
- ✅ **开发友好**: 适合开发和小规模部署
- ✅ **功能完整**: 支持完整的SQL功能和事务

**如果需要PostgreSQL（生产环境推荐）：**

```bash
# 使用PostgreSQL版本的初始化脚本
./scripts/init-dev.sh
```

SQLite初始化脚本会自动完成：
- ✅ 检查基础环境依赖
- ✅ 安装uv包管理器
- ✅ 生成SQLite配置文件
- ✅ 安装所有Python和Node.js依赖
- ✅ 初始化SQLite数据库和迁移
- ✅ 设置开发环境

### 7. 启动开发服务

初始化完成后，使用启动脚本：

```bash
# 同时启动前后端服务
./scripts/start-dev.sh
```

或者分别启动：

```bash
# 后端服务
uv run dev

# 前端服务（新终端）
cd frontend && npm run dev
```

### 7. 开发环境验证

#### 后端验证
```bash
# 测试API健康检查
curl http://localhost:8000/health

# 测试数据库连接
uv run python -c "
from backend.app.db.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('数据库连接成功:', result.fetchone())
"
```

#### 前端验证
- 打开浏览器访问 http://localhost:3000
- 检查浏览器控制台是否有错误
- 尝试注册一个测试用户

### 8. 常见问题解决

#### PostgreSQL连接问题
```bash
# 检查PostgreSQL服务状态
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# 重启PostgreSQL
sudo systemctl restart postgresql  # Linux
brew services restart postgresql  # macOS

# 检查端口是否被占用
netstat -an | grep 5432
```

#### Python依赖问题
```bash
# 清理并重新安装依赖
uv sync --reinstall

# 检查Python版本
python --version
uv run python --version

# 检查虚拟环境
uv venv list
```

#### Node.js依赖问题
```bash
# 清理node_modules
cd frontend
rm -rf node_modules package-lock.json
npm install

# 或使用yarn
rm -rf node_modules yarn.lock
yarn install
```

#### 端口冲突问题
```bash
# 检查端口占用
lsof -i :8000  # 后端端口
lsof -i :3000  # 前端端口

# 杀死占用端口的进程
kill -9 <PID>
```

### 9. 开发工具推荐

#### VS Code插件
- Python
- Pylance
- Vetur (Vue 3 支持)
- TypeScript Vue Plugin
- PostgreSQL
- Thunder Client (API测试)

#### 数据库管理工具
- pgAdmin (Web界面)
- DBeaver (桌面应用)
- TablePlus (macOS)

### 10. 下一步

环境配置完成后，你可以：
1. 创建超级管理员账户
2. 添加测试校区和用户
3. 开始功能开发和测试
4. 查看API文档了解接口使用方法

**重要提示：**
- 确保.env文件不要提交到版本控制系统
- 生产环境使用时请修改默认密码和密钥
- 定期备份数据库数据

## 🗄️ 数据库设计

详细的数据库表结构设计请参考 [database_design.md](./database_design.md)

### 主要数据表
- `users` - 用户基础信息表
- `campuses` - 校区信息表
- `coaches` - 教练扩展信息表
- `students` - 学员扩展信息表
- `coach_students` - 教练学员关系表
- `bookings` - 课程预约表
- `courses` - 课程记录表
- `payments` - 支付记录表
- `evaluations` - 课后评价表
- `competitions` - 比赛信息表
- `competition_registrations` - 比赛报名表
- `system_logs` - 系统日志表
- `licenses` - 软件许可证表

## 🔧 开发指南

### 后端开发

#### 添加新的API端点
1. 在 `backend/app/models/` 中定义数据模型
2. 在 `backend/app/schemas/` 中定义请求/响应模式
3. 在 `backend/app/services/` 中实现业务逻辑
4. 在 `backend/app/api/v1/` 中创建路由

#### 数据库迁移
```bash
# 创建新的迁移文件
uv run alembic revision --autogenerate -m "描述"

# 应用迁移
uv run alembic upgrade head

# 回滚迁移
uv run alembic downgrade -1
```

### 前端开发

#### 项目结构
```
frontend/src/
├── api/          # API接口
├── components/   # 组件
├── router/       # 路由配置
├── store/        # 状态管理
├── types/        # TypeScript类型定义
├── utils/        # 工具函数
└── views/        # 页面组件
```

#### 添加新页面
1. 在 `src/views/` 中创建页面组件
2. 在 `src/router/index.ts` 中添加路由
3. 在 `src/api/` 中添加相关API调用
4. 在 `src/types/` 中定义相关类型

## 🧪 测试

### 后端测试
```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest tests/test_auth.py

# 生成测试覆盖率报告
uv run pytest --cov=app
```

### 前端测试
```bash
cd frontend

# 运行单元测试
npm run test

# 运行e2e测试
npm run test:e2e
```

## 📝 API文档

启动后端服务后，可以通过以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 安全特性

- JWT身份认证
- 密码强度验证（8-16位，包含字母数字特殊字符）
- 角色权限控制
- 操作日志记录
- SQL注入防护
- XSS攻击防护

## 📈 性能优化

- 数据库索引优化
- API响应缓存
- 前端代码分割
- 图片懒加载
- CDN静态资源

## 🚀 部署建议

### 生产环境部署
1. 使用Docker容器化部署
2. 配置反向代理（Nginx）
3. 启用HTTPS
4. 配置数据库连接池
5. 设置日志轮转
6. 配置监控告警

### 环境变量配置
确保在生产环境中正确配置以下环境变量：
- `DATABASE_URL` - 数据库连接字符串
- `SECRET_KEY` - JWT密钥
- `LICENSE_SERVER_URL` - 许可证验证服务器
- 支付相关配置

---

**乒乓球培训管理系统** - 让培训管理更简单高效！