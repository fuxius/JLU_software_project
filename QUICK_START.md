# 快速启动指南

## 环境要求

- Python 3.9+
- Node.js 16+
- pnpm (推荐) 或 npm

## 启动步骤

### 1. 安装uv和pnpm

```bash
# 安装uv (Python包管理器)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装pnpm (前端包管理器)
npm install -g pnpm
```

### 2. 克隆项目

```bash
git clone <your-repository-url>
cd JLU_software_project
```

### 3. 配置环境

```bash
# 复制环境配置
cp env.example .env
```

### 4. 安装依赖

```bash
# 后端依赖
uv sync

# 前端依赖
cd frontend
pnpm install
cd ..
```

### 5. 初始化数据库

```bash
# 初始化Alembic（数据库迁移工具）
uv run alembic init alembic

# 创建初始迁移文件
uv run alembic revision --autogenerate -m "Initial migration"

# 应用迁移，创建数据库表
uv run alembic upgrade head
```

### 6. 启动服务

```bash
# 启动后端 (终端1)
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端 (终端2)
cd frontend && pnpm dev
```

## 访问应用

- **前端**: http://localhost:3000
- **后端API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 创建管理员

1. 访问 http://localhost:3000/register 注册用户
2. 修改用户角色为管理员：

```bash
# 使用Python脚本修改
uv run python -c "
from backend.app.db.database import SessionLocal
from backend.app.models.user import User
db = SessionLocal()
user = db.query(User).filter(User.username == 'your_username').first()
user.role = 'super_admin'
db.commit()
print('管理员设置完成')
"
```

## 常用命令

```bash
# 后端
uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000  # 启动开发服务器
uv run alembic upgrade head                                               # 应用数据库迁移

# 前端  
cd frontend && pnpm dev              # 启动开发服务器
cd frontend && pnpm build            # 构建生产版本
```

---

**完成！** 现在可以开始开发了 🏓