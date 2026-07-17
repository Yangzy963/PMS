# 人员信息管理系统使用手册

## 一、系统简介

人员信息管理系统是一个基于 **FastAPI + Dash + Redmine** 的 Web 应用，用于管理人员基本信息，支持新增、查询、修改、删除、搜索、批量导入等功能。

### 技术栈

- 后端：FastAPI + Pydantic + JWT + Requests
- 前端：Dash + dash-bootstrap-components
- 数据存储：Redmine（通过 REST API 交互）
- 测试：Pytest

---

## 二、环境准备

### 1. 安装 Python

确保已安装 Python 3.10+。

### 2. 安装 Redmine

本系统使用 Redmine 作为数据存储，需要先在本地或服务器部署 Redmine。

默认配置要求：

- Redmine 访问地址：`http://localhost:3001`
- 项目 Key：`pms`
- 跟踪标签：`人员信息`
- 自定义字段：人员编号、姓名、性别、年龄、手机号、邮箱、部门、职位、入职时间

### 3. 克隆代码

```bash
git clone https://github.com/你的用户名/PMS.git
cd PMS
```

---

## 三、安装依赖

### 1. 创建并激活虚拟环境

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd ../frontend
pip install -r requirements.txt
```

---

## 四、配置文件

在项目根目录 `PMS/` 下创建 `.env` 文件，可从 `.env.example` 复制：

```bash
cp .env.example .env
```

修改 `.env` 中的配置：

```env
# Redmine 配置
REDMINE_BASE_URL=http://localhost:3001
REDMINE_API_KEY=你的Redmine管理员APIKey
REDMINE_PROJECT_KEY=pms
REDMINE_TRACKER_NAME=人员信息

# JWT 密钥（生产环境请修改）
SECRET_KEY=your-secret-key-change-in-production

# 管理员账号
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

---

## 五、启动系统

### 1. 启动 Redmine

确保 Redmine 服务已启动，可以通过浏览器访问：

```text
http://localhost:3001
```

### 2. 启动后端

```bash
cd backend
python main.py
```

后端默认运行在 `http://127.0.0.1:8000`。

Swagger 接口文档地址：

```text
http://127.0.0.1:8000/docs
```

### 3. 启动前端

新建一个终端窗口，激活虚拟环境后执行：

```bash
cd frontend
python app.py
```

前端默认运行在 `http://127.0.0.1:8050`。

---

## 六、登录系统

打开前端地址：

```text
http://127.0.0.1:8050
```

使用默认管理员账号登录：

| 字段 | 值 |
|------|-----|
| 用户名 | `admin` |
| 密码 | `admin123` |

---

## 七、功能说明

### 1. 人员管理

登录后进入「人员管理」页面，可进行：

- **新增人员**：点击「新增人员」按钮，填写表单后保存
- **查看人员**：表格展示所有人员信息
- **编辑人员**：点击行末「编辑」按钮修改
- **删除人员**：点击行末「删除」按钮删除单条
- **批量删除**：点击「批量删除」，勾选多行后确认删除

### 2. 搜索功能

人员管理页面上方提供搜索栏，支持：

- 姓名模糊搜索
- 部门筛选
- 职位筛选
- 入职时间范围查询

### 3. 数据导入

点击「数据导入」按钮，选择 CSV 或 Excel 文件上传。

导入文件要求：

- 支持 `.csv` 或 `.xlsx` 格式
- 必须包含表头：人员编号、姓名、性别、年龄、手机号、邮箱、部门、职位、入职时间
- 入职时间支持多种格式，如 `2023-01-01`、`2023/1/1`、`2023年1月1日`

重复数据处理策略：

- **跳过**：跳过已存在的人员编号
- **覆盖**：更新已存在的人员信息
- **终止**：发现重复立即停止导入

---

## 八、接口说明

系统对外提供标准 REST API，主要接口如下：

| 方法 | 接口 | 说明 |
|------|------|------|
| POST | `/api/v1/login` | 用户登录 |
| GET | `/api/v1/me` | 获取当前用户 |
| POST | `/api/v1/employees` | 新增人员 |
| GET | `/api/v1/employees` | 查询人员列表 |
| GET | `/api/v1/employees/{id}` | 查看人员详情 |
| PUT | `/api/v1/employees/{id}` | 修改人员 |
| DELETE | `/api/v1/employees/{id}` | 删除人员 |
| POST | `/api/v1/employees/batch-delete` | 批量删除 |
| POST | `/api/v1/import/employees` | 导入人员 |

所有业务接口都需要在请求头中携带 JWT Token：

```bash
Authorization: Bearer your-access-token
```

---

## 九、常见问题

### 1. 后端启动报 `ModuleNotFoundError: No module named 'fastapi'`

原因：虚拟环境中没有安装依赖。

解决：

```bash
pip install -r backend/requirements.txt
```

### 2. 访问 `http://0.0.0.0:8000` 打不开

`0.0.0.0` 是服务端监听地址，浏览器请访问：

```text
http://127.0.0.1:8000/docs
```

### 3. 新增人员报 500，提示连接 Redmine 失败

检查 `.env` 中的 `REDMINE_BASE_URL` 和 `REDMINE_API_KEY` 是否正确，Redmine 是否已启动。

### 4. 导入时提示入职时间格式错误

入职时间支持以下格式：

- `2023-01-01`
- `2023/1/1`
- `2023.01.01`
- `2023年1月1日`
- `2023-01-01 10:30:00`

---

## 十、开发账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |

> 生产环境请务必修改默认密码和 JWT 密钥。
