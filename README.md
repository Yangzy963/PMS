# 人员信息管理系统

基于 FastAPI + Dash + Redmine 的人员信息管理系统。

## 技术栈

- **后端**：FastAPI、Pydantic、JWT、Requests
- **前端**：Dash、dash-bootstrap-components
- **数据存储**：Redmine REST API
- **测试**：Pytest

## 快速开始

### 1. 安装依赖

```bash
python -m venv .venv
.\.venv\Scripts\activate

cd backend
pip install -r requirements.txt

cd ../frontend
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cd ..
cp .env.example .env
```

编辑 `.env`，填写 Redmine 地址和 API Key。

### 3. 启动服务

```bash
# 启动后端
cd backend
python main.py

# 启动前端（新终端）
cd frontend
python app.py
```

- 后端：`http://127.0.0.1:8000/docs`
- 前端：`http://127.0.0.1:8050`

### 4. 登录

默认账号：

- 用户名：`admin`
- 密码：`admin123`

## 主要功能

- 用户登录与认证
- 人员信息增删改查
- 多条件搜索与分页
- 批量删除
- CSV/Excel 数据导入
- Swagger 接口文档

## 文档

- [用户使用手册](docs/user_manual.md)
- [项目需求文档](docs/requirements.md)（已加入 .gitignore，不提交到仓库）

## 许可证

MIT
