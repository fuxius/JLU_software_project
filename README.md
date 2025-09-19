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

## 📦 安装部署

### 1. 克隆项目
```bash
git clone <repository-url>
cd JLU_software_project
```

### 2. 后端设置

#### 安装uv（如果尚未安装）
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 创建Python虚拟环境并安装依赖
```bash
# 创建虚拟环境并安装依赖
uv sync

# 安装开发依赖
uv sync --extra dev
```

#### 配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑环境变量文件
vim .env
```

#### 数据库设置
```bash
# 创建PostgreSQL数据库
createdb tabletennis_db

# 运行数据库迁移
uv run alembic upgrade head
```

#### 启动后端服务
```bash
# 开发模式（自动重载）
uv run dev

# 或者直接运行
uv run python backend/run.py

# 生产模式
uv run start
```

后端API文档访问: http://localhost:8000/docs

### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

前端应用访问: http://localhost:3000

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

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件

## 📞 支持与联系

如有问题或建议，请通过以下方式联系：
- 项目Issues: [GitHub Issues]
- 邮箱: admin@example.com

## 🎯 路线图

- [ ] 移动端适配
- [ ] 微信小程序版本
- [ ] 数据统计分析
- [ ] 智能排课算法
- [ ] 视频教学功能
- [ ] 多语言支持

---

**乒乓球培训管理系统** - 让培训管理更简单高效！