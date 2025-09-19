#!/bin/bash
# 开发环境启动脚本

echo "🚀 启动乒乓球培训管理系统开发环境..."

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv未安装，请先安装uv"
    echo "安装命令: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ Node.js未安装，请先安装Node.js"
    exit 1
fi

# 检查数据库配置
if [[ "$DATABASE_URL" == *"postgresql"* ]]; then
    echo "🗄️  检查PostgreSQL连接..."
    if ! pg_isready &> /dev/null; then
        echo "❌ PostgreSQL未运行，请先启动PostgreSQL服务"
        exit 1
    fi
    echo "✅ PostgreSQL连接正常"
elif [[ "$DATABASE_URL" == *"sqlite"* ]]; then
    echo "🗄️  使用SQLite数据库，无需额外配置"
else
    echo "⚠️  数据库配置未明确指定，使用默认SQLite"
fi

# 创建.env文件（如果不存在）
if [ ! -f .env ]; then
    echo "📝 创建环境配置文件..."
    cp env.example .env
    echo "⚠️  请编辑 .env 文件配置数据库连接等信息"
fi

# 安装后端依赖
echo "📦 安装后端依赖..."
uv sync --extra dev

# 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend
npm install
cd ..

# 数据库迁移
echo "🗄️  执行数据库迁移..."
uv run alembic upgrade head

# 启动后端服务
echo "🔧 启动后端服务..."
uv run dev &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 启动前端服务
echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ 系统启动完成!"
echo "📖 后端API文档: http://localhost:8000/docs"
echo "🌐 前端应用: http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT
wait
