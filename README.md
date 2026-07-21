# 人员信息管理系统

基于 FastAPI + Dash + Redmine 的人员信息管理系统。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | FastAPI + Pydantic + JWT | REST API，自动生成 Swagger 文档 |
| 前端 | Dash + dash-bootstrap-components | 响应式 Web UI |
| 存储 | Redmine REST API | 以 Issue 形式存储人员信息 |
| 缓存 | Redis（可选） | Token 黑名单 |
| 测试 | Pytest + Playwright + httpx | 四层测试体系 |

## 项目结构

```
PMS/
├── backend/              # FastAPI 后端
│   ├── main.py           # 应用入口
│   └── app/
│       ├── api/v1/       # 路由层（auth, employee, import）
│       ├── services/     # 业务层（Redmine 客户端、导入逻辑）
│       ├── schemas/      # Pydantic 数据模型
│       ├── core/         # 配置、异常、中间件
│       └── utils/        # 工具函数
├── frontend/             # Dash 前端
│   ├── app.py            # 应用入口 + 路由守卫
│   ├── pages/            # 页面（login, employee）
│   ├── components/       # 组件（navbar, table, form, search）
│   └── services/         # API 调用封装
├── tests/                # 四层测试
│   ├── unit/             # 单元测试
│   ├── api/              # 接口测试
│   ├── integration/      # 集成测试
│   └── ui/               # UI 自动化测试
└── docs/                 # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / Mac
# .\.venv\Scripts\activate  # Windows

pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填写 Redmine 地址、API Key 等信息。

### 3. 启动服务

```bash
# 终端 1：启动后端
cd backend
python main.py

# 终端 2：启动前端
cd frontend
python app.py
```

| 服务 | 地址 |
|------|------|
| 后端 API | http://127.0.0.1:8000/docs |
| 前端页面 | http://127.0.0.1:8050 |

### 4. 登录

- 用户名：`admin`
- 密码：`admin123`

## 主要功能

- 用户登录与认证（JWT + Redis 黑名单退出）
- 人员信息增删改查
- 多条件搜索（姓名、部门、职位、入职时间）
- 分页与排序（支持全部字段）
- 批量删除
- CSV/Excel 数据导入（跳过/覆盖/终止策略）
- Swagger 接口文档

## 运行测试

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行全部测试
pytest tests/ -v

# 仅单元测试（无外部依赖）
pytest tests/unit/ -v

# 跳过集成测试（不需要 Redmine）
pytest tests/ -v -m "not integration"

# 覆盖率报告
pytest tests/ --cov=backend --cov-report=html
```
tests/ --cov=backend --cov-report=html
### 测试统计

| 测试类型 | 用例数 | 说明 |
|----------|--------|------|
| 单元测试 | 141 | 模型校验、业务逻辑、工具函数 |
| API 测试 | 37+ | 接口契约、参数校验、权限验证 |
| 集成测试 | 14+ | Redmine 交互、完整业务流程 |
| UI 测试 | 17 | Playwright 浏览器自动化 |

覆盖率：综合 96%，接口覆盖率 98%。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/login` | 用户登录 |
| POST | `/api/v1/logout` | 退出登录 |
| GET | `/api/v1/me` | 获取当前用户 |
| POST | `/api/v1/employees` | 新增人员 |
| GET | `/api/v1/employees` | 查询人员列表 |
| GET | `/api/v1/employees/{id}` | 查看人员详情 |
| PUT | `/api/v1/employees/{id}` | 修改人员 |
| DELETE | `/api/v1/employees/{id}` | 删除人员 |
| POST | `/api/v1/employees/batch-delete` | 批量删除 |
| POST | `/api/v1/import/employees` | 导入人员 |

启动后端后访问 http://127.0.0.1:8000/docs 查看完整 Swagger 文档。

## 文档

| 文档 | 说明 |
|------|------|
| [用户使用手册](docs/user_manual.md) | 系统安装、配置与使用说明 |
| [系统架构文档](docs/architecture.md) | 架构设计、数据流、技术决策 |
| [部署说明文档](docs/deployment.md) | 生产环境部署指南 |
| [开发指南](docs/development.md) | 开发环境搭建、测试、代码规范 |
| [项目需求文档](docs/requirements.md) | 需求规格与验收标准 |

## 许可证

MIT
