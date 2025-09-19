# 快速开始指南

这个指南将帮助你在10分钟内搭建好乒乓球培训管理系统的开发环境。

## 🚀 一分钟检查清单

在开始之前，请确保你的系统已安装：

- [ ] Python 3.9+ (`python --version`)
- [ ] Node.js 16+ (`node --version`)  
- [ ] Git (`git --version`)

**数据库选择：**
- ✅ **SQLite** (推荐): 零配置，自动创建
- ⚪ PostgreSQL 12+ (可选): 需要额外安装配置

如果缺少任何组件，请参考 [README.md](./README.md) 的详细安装指南。

## 📋 快速搭建步骤

### 1. 安装uv包管理器 (30秒)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 重新加载shell配置
source ~/.bashrc  # 或 source ~/.zshrc
```

### 2. 克隆并进入项目 (30秒)

```bash
git clone <your-repository-url>
cd JLU_software_project
```

### 3. 配置数据库 (2分钟)

```bash
# 启动PostgreSQL服务
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# 创建数据库和用户
sudo -u postgres psql -c "CREATE USER tabletennis_user WITH PASSWORD 'dev123456';"
sudo -u postgres psql -c "CREATE DATABASE tabletennis_db OWNER tabletennis_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tabletennis_db TO tabletennis_user;"
```

### 4. 配置环境变量 (1分钟)

```bash
# 复制环境配置模板
cp env.example .env

# 快速配置（开发环境）
cat > .env << EOF
DATABASE_URL=postgresql://tabletennis_user:dev123456@localhost:5432/tabletennis_db
SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEBUG=true
EOF
```

### 5. 安装后端依赖 (2分钟)

```bash
# 创建虚拟环境并安装所有依赖
uv sync --extra dev
```

### 6. 初始化数据库 (1分钟)

```bash
# 初始化Alembic
uv run alembic init alembic

# 创建并应用初始迁移
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head
```

### 7. 安装前端依赖 (2分钟)

```bash
cd frontend
npm install
cd ..
```

### 8. 启动服务 (30秒)

```bash
# 使用一键启动脚本
chmod +x scripts/start-dev.sh
./scripts/start-dev.sh
```

或者手动启动：

```bash
# 终端1: 启动后端
uv run dev

# 终端2: 启动前端
cd frontend && npm run dev
```

## ✅ 验证安装

### 检查后端服务
```bash
# 健康检查
curl http://localhost:8000/health

# 应该返回: {"status": "healthy", "message": "乒乓球培训管理系统运行正常"}
```

### 检查前端服务
- 访问 http://localhost:3000
- 应该看到登录页面

### 检查API文档
- 访问 http://localhost:8000/docs
- 应该看到Swagger API文档

## 🎯 创建第一个用户

### 1. 创建超级管理员

访问 http://localhost:3000/register，填写信息：

```
用户名: admin
密码: Admin123!
真实姓名: 系统管理员
手机号: 13800000000
```

注册后，需要手动将用户角色改为超级管理员：

```bash
# 连接数据库
psql -h localhost -U tabletennis_user -d tabletennis_db

# 更新用户角色
UPDATE users SET role = 'super_admin' WHERE username = 'admin';
\q
```

### 2. 登录系统

使用刚创建的管理员账户登录：
- 访问 http://localhost:3000/login
- 输入用户名和密码
- 登录后应该进入校区管理页面

## 📖 下一步操作

现在你可以：

1. **创建校区**: 在校区管理页面添加第一个校区
2. **添加用户**: 注册教练和学员账户
3. **查看API**: 浏览 http://localhost:8000/docs 了解所有API接口
4. **开始开发**: 根据需求修改代码和添加功能

## 🛠️ 开发工作流

### 常用命令

```bash
# 后端开发
uv run dev                    # 启动后端服务
uv run python backend/run.py  # 直接运行后端
uv run pytest               # 运行测试
uv run alembic upgrade head  # 应用数据库迁移

# 前端开发  
cd frontend
npm run dev                  # 启动前端服务
npm run build               # 构建生产版本
npm run lint                # 代码检查

# 数据库操作
psql -h localhost -U tabletennis_user -d tabletennis_db  # 连接数据库
uv run alembic revision --autogenerate -m "描述"        # 创建迁移
```

### 推荐开发工具

- **IDE**: VS Code 或 PyCharm
- **数据库管理**: pgAdmin 或 DBeaver
- **API测试**: Thunder Client 或 Postman
- **版本控制**: Git

## ❗ 常见问题

### 数据库连接失败
```bash
# 检查PostgreSQL是否运行
sudo systemctl status postgresql

# 检查用户和数据库是否创建成功
sudo -u postgres psql -l
```

### uv命令找不到
```bash
# 重新安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载shell
source ~/.bashrc
```

### 端口被占用
```bash
# 查看端口占用
lsof -i :8000  # 后端
lsof -i :3000  # 前端

# 杀死进程
kill -9 <PID>
```

### 前端依赖安装失败
```bash
# 清理缓存重新安装
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📞 获取帮助

如果遇到问题：

1. 查看 [README.md](./README.md) 的详细说明
2. 检查 [database_design.md](./database_design.md) 了解数据库结构
3. 查看项目Issues或创建新Issue
4. 联系开发团队

---

**恭喜！** 你现在已经成功搭建了乒乓球培训管理系统的开发环境。开始你的开发之旅吧！ 🏓
