# 系统架构文档

## 一、概览

人员信息管理系统采用 **前后端分离** 架构：

- **后端**：FastAPI REST API，负责认证、业务逻辑、Redmine 数据交互
- **前端**：Dash (Plotly)，多页面 SPA，通过 HTTP 调用后端 API
- **数据存储**：Redmine Issue 作为持久化存储（无传统数据库）

```
浏览器 (Dash UI)
    │  HTTP REST (JSON)
    ▼
FastAPI Server (:8000)
    │  Redmine REST API
    ▼
Redmine Server (:3001)
    └── Issues (每条 Issue = 一名员工)
```

---

## 二、技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端框架 | FastAPI 0.139 | 异步 Web 框架，自动生成 Swagger 文档 |
| 数据校验 | Pydantic 2.13 | 请求/响应模型定义与校验 |
| 认证 | JWT (python-jose) | 无状态 Token 认证 |
| 缓存/黑名单 | Redis 8.0 | Token 退出登录黑名单 |
| 前端框架 | Dash 4.4 | Plotly 出品的低代码 Web 框架 |
| UI 组件 | dash-bootstrap-components 2.0 | Bootstrap 风格组件 |
| 数据存储 | Redmine REST API | 以 Issue 形式存储人员信息 |
| 数据处理 | pandas + openpyxl | CSV/Excel 文件解析 |
| 测试 | Pytest + Playwright + httpx | 四层测试体系 |

---

## 三、目录结构

```
PMS/
├── backend/                      # 后端服务
│   ├── main.py                   # FastAPI 应用入口
│   ├── requirements.txt          # 后端依赖（锁定版本）
│   └── app/
│       ├── api/
│       │   ├── router.py         # 路由聚合（prefix: /api/v1）
│       │   └── v1/
│       │       ├── auth.py       # 认证接口（登录/退出/获取用户）
│       │       ├── employee.py   # 人员 CRUD 接口
│       │       └── employee_import.py  # 批量导入接口
│       ├── core/
│       │   ├── config.py         # 配置管理（Pydantic Settings，.env）
│       │   ├── exceptions.py     # 业务异常体系
│       │   └── middleware.py     # 全局异常处理器
│       ├── schemas/
│       │   ├── common.py         # 统一响应模型 CommonResponse[T]
│       │   ├── employee.py       # 员工模型（增删改查+搜索+分页）
│       │   └── user.py           # 用户模型（登录、Token、用户信息）
│       ├── services/
│       │   ├── auth_services.py  # 认证业务逻辑
│       │   ├── redmine_services.py # Redmine API 客户端（核心）
│       │   └── import_services.py  # 导入业务逻辑
│       ├── utils/
│       │   ├── response.py       # 统一响应格式（success/error）
│       │   ├── excel.py          # CSV/Excel 文件解析
│       │   └── password.py       # 密码工具（预留）
│       ├── security.py           # JWT 创建与解析
│       └── redis.py              # Redis 客户端（Token 黑名单）
│
├── frontend/                     # 前端 Dash 应用
│   ├── app.py                    # Dash 应用入口 + 登录状态/路由守卫
│   ├── requirements.txt          # 前端依赖
│   ├── pages/
│   │   ├── login.py              # 登录页面
│   │   └── employee.py           # 人员管理页面（核心页面）
│   ├── components/
│   │   ├── navbar.py             # 导航栏
│   │   ├── search_bar.py         # 搜索栏
│   │   ├── employee_table.py     # 人员表格
│   │   └── employee_form.py      # 新增/编辑表单弹窗
│   ├── services/
│   │   └── api_client.py         # 后端 API 调用封装
│   └── data/
│       └── mock_employee.py      # 测试用 Mock 数据
│
├── tests/                        # 测试（四层体系）
│   ├── conftest.py               # 根配置：Python 路径注入
│   ├── unit/                     # 单元测试（Mock 依赖）
│   ├── api/                      # 接口测试（httpx + TestClient）
│   ├── integration/              # 集成测试（真实 Redmine 交互）
│   └── ui/                       # UI 自动化测试（Playwright）
│
├── docs/                         # 项目文档
│   ├── user_manual.md            # 用户使用手册
│   ├── requirements.md           # 项目需求文档
│   ├── architecture.md           # 系统架构文档（本文件）
│   ├── deployment.md             # 部署说明文档
│   └── development.md            # 开发指南
│
├── .env.example                  # 环境变量模板
├── .env                          # 实际环境变量（不提交）
├── .gitignore
├── pyproject.toml                # Pytest 配置
├── requirements-dev.txt          # 开发/测试依赖
└── README.md
```

---

## 四、数据模型

### 员工（Redmine Issue 中的自定义字段）

```
┌──────────────┬──────────┬─────────────────────┐
│ 字段         │ 类型      │ Redmine 存储          │
├──────────────┼──────────┼─────────────────────┤
│ id           │ int      │ Issue ID            │
│ number       │ str      │ 自定义字段: 人员编号   │
│ name         │ str      │ 自定义字段: 姓名      │
│ gender       │ str      │ 自定义字段: 性别      │
│ age          │ int/null │ 自定义字段: 年龄      │
│ phone        │ str/null │ 自定义字段: 手机号    │
│ email        │ str/null │ 自定义字段: 邮箱      │
│ department   │ str/null │ 自定义字段: 部门      │
│ position     │ str/null │ 自定义字段: 职位      │
│ jointime     │ str/null │ 自定义字段: 入职时间   │
│ createtime   │ str      │ Issue created_on    │
│ updatetime   │ str      │ Issue updated_on    │
└──────────────┴──────────┴─────────────────────┘
```

- **主题格式**：`【人员编号】姓名` → Redmine Issue Subject
- **唯一标识**：人员编号（number），创建前先查重

---

## 五、架构决策记录 (ADR)

### ADR-1: 为什么用 Redmine Issue 代替数据库？

- 项目需求规定基于 Redmine API 实现数据交互
- Redmine 提供 REST API，天然支持 CRUD
- 适合小规模数据量（< 1000 人），避免引入额外数据库

**代价**：
- 无法使用 SQL 进行复杂查询，需拉取数据后在本地过滤/排序
- Redmine API 单次最多返回 100 条，需分批次 `_fetch_all_issues()`
- 排序仅支持 `created_on`/`updated_on`，其他字段需本地排序

### ADR-2: 为什么所有排序都在本地执行？

- Redmine REST API 只支持对 Issue 原生字段排序（created_on, updated_on）
- 人员信息的核心字段（姓名、部门、年龄）都是自定义字段，Redmine 不支持排序
- 因此采用"全量拉取 + 本地排序 + 分页"策略

### ADR-3: 为什么 Token 退出用 Redis 黑名单而不是直接删除？

- JWT 是无状态的，服务端无法主动使其失效
- 使用 Redis 黑名单机制，退出时将 Token 加入黑名单（设置 TTL = Token 剩余有效期）
- Redis 不可用时自动降级（跳过黑名单检查），不影响登录功能

### ADR-4: 为什么前端每个请求都用 `allow_duplicate=True`？

- Dash 默认不允许同一 Output 被多个 callback 更新
- 登录、退出、页面导航等多个 callback 都需要更新 `auth-store` 和 `url`
- `allow_duplicate=True` 允许多个 callback 输出到同一个组件

---

## 六、数据流

### 登录流程

```
浏览器                     FastAPI
  │                          │
  │── POST /api/v1/login ──→│
  │   {username, password}   │── authenticate_user()
  │                          │── create_access_token(sub=username)
  │←── {access_token} ──────│
  │                          │
  │  存入 dcc.Store(local)   │
```

### 人员查询流程

```
Dash Callback              FastAPI                    Redmine
  │                          │                          │
  │── GET /api/v1/employees │                          │
  │   ?name=张&limit=20      │── _fetch_all_issues() ──→│
  │                          │   GET /issues.json       │
  │                          │←── issues[] ────────────│
  │                          │── 本地过滤(name)          │
  │                          │── 本地排序               │
  │                          │── 分页 offset/limit       │
  │←── {total, items[]} ────│                          │
```

### 退出登录流程

```
浏览器                     FastAPI                    Redis
  │                          │                          │
  │── POST /api/v1/logout ──→│                          │
  │   Authorization: Bearer X│── decode_token(token)     │
  │                          │── blacklist_token(token) ─→│ SET blacklist:token:X 1 EX <ttl>
  │←── 200 OK ──────────────│                          │
  │                          │                          │
  │  清除 auth-store         │                          │
  │  跳转到登录页            │                          │
```

---

## 七、安全设计

| 层面 | 措施 |
|------|------|
| 传输 | JWT Token 通过 HTTP Bearer 头传递 |
| 存储 | Token 存在浏览器 localStorage（dcc.Store local） |
| 退出 | Redis 黑名单使已签发 Token 失效 |
| 路由 | 前端路由守卫 + 后端 `Depends(get_current_user)` 双重校验 |
| 密码 | 当前硬编码明文（生产环境需改为 bcrypt 哈希） |
| CORS | `allow_origins=["*"]`（生产环境应限制为前端域名） |
