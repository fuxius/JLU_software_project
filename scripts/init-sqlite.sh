#!/bin/bash
# SQLite版本的开发环境初始化脚本

set -e  # 遇到错误立即退出

echo "🏓 乒乓球培训管理系统 - SQLite开发环境初始化"
echo "=============================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 未安装${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $1 已安装${NC}"
        return 0
    fi
}

# 检查环境依赖
echo -e "${YELLOW}📋 检查环境依赖...${NC}"
deps_ok=true

if ! check_command python3; then
    echo "请安装 Python 3.9+"
    deps_ok=false
fi

if ! check_command node; then
    echo "请安装 Node.js 16+"
    deps_ok=false
fi

if ! check_command git; then
    echo "请安装 Git"
    deps_ok=false
fi

if [ "$deps_ok" = false ]; then
    echo -e "${RED}❌ 请先安装缺少的依赖，然后重新运行此脚本${NC}"
    exit 1
fi

# 检查uv是否安装
if ! check_command uv; then
    echo -e "${YELLOW}📦 正在安装 uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc 2>/dev/null || source ~/.zshrc 2>/dev/null || true
    
    if ! command -v uv &> /dev/null; then
        echo -e "${RED}❌ uv 安装失败，请手动安装${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ uv 安装成功${NC}"
fi

echo -e "${GREEN}✅ 使用SQLite数据库，无需额外配置${NC}"

# 创建.env文件
echo -e "${YELLOW}⚙️  配置环境变量...${NC}"
if [ ! -f .env ]; then
    cat > .env << EOF
# 数据库配置 (SQLite - 轻量级，无需安装数据库服务)
DATABASE_URL=sqlite:///./tabletennis.db

# JWT配置
SECRET_KEY=dev-secret-key-please-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
DEBUG=true

# 支付配置（开发环境可选）
WECHAT_PAY_APP_ID=
WECHAT_PAY_MCH_ID=
ALIPAY_APP_ID=

# 许可证服务器配置（开发环境可选）
LICENSE_SERVER_URL=https://license.example.com
LICENSE_VALIDATION_KEY=
EOF
    echo -e "${GREEN}✅ 环境配置文件创建成功${NC}"
else
    echo -e "${GREEN}✅ 环境配置文件已存在${NC}"
fi

# 安装Python依赖
echo -e "${YELLOW}📦 安装Python依赖...${NC}"
uv sync --extra dev
echo -e "${GREEN}✅ Python依赖安装完成${NC}"

# 初始化数据库迁移
echo -e "${YELLOW}🗄️  初始化数据库迁移...${NC}"
if [ ! -d "alembic" ]; then
    uv run alembic init alembic
    echo -e "${GREEN}✅ Alembic初始化完成${NC}"
else
    echo -e "${GREEN}✅ Alembic已初始化${NC}"
fi

# 创建并应用迁移
echo -e "${YELLOW}🔄 创建数据库迁移...${NC}"
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head
echo -e "${GREEN}✅ SQLite数据库初始化完成${NC}"

# 安装前端依赖
echo -e "${YELLOW}📦 安装前端依赖...${NC}"
cd frontend
npm install
cd ..
echo -e "${GREEN}✅ 前端依赖安装完成${NC}"

# 创建启动脚本的快捷方式
echo -e "${YELLOW}🔗 创建便捷命令...${NC}"
chmod +x scripts/start-dev.sh

echo ""
echo -e "${GREEN}🎉 SQLite开发环境初始化完成！${NC}"
echo ""
echo "📖 下一步操作："
echo "1. 启动开发服务器："
echo "   ./scripts/start-dev.sh"
echo ""
echo "2. 或者分别启动前后端："
echo "   后端: uv run dev"
echo "   前端: cd frontend && npm run dev"
echo ""
echo "3. 访问应用："
echo "   前端: http://localhost:3000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "4. 创建超级管理员账户："
echo "   - 访问 http://localhost:3000/register 注册用户"
echo "   - 然后运行: uv run python -c \""
echo "     from backend.app.db.database import SessionLocal"
echo "     from backend.app.models.user import User"
echo "     db = SessionLocal()"
echo "     user = db.query(User).filter(User.username == 'your_username').first()"
echo "     user.role = 'super_admin'"
echo "     db.commit()"
echo "     print('超级管理员设置成功')\""
echo ""
echo -e "${YELLOW}💡 SQLite优势：${NC}"
echo "- ✅ 无需安装和配置数据库服务"
echo "- ✅ 数据库文件自动创建在项目目录"
echo "- ✅ 完全便携，适合开发和小规模部署"
echo "- ✅ 支持完整的SQL功能"
echo ""
echo -e "${YELLOW}📁 数据库文件位置：${NC}"
echo "- 数据库文件: ./tabletennis.db"
echo "- 可以使用SQLite浏览器工具查看数据"
echo ""
echo -e "${GREEN}✨ 开始你的开发之旅吧！${NC}"
