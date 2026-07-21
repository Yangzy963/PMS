# 部署说明文档

## 一、环境要求

| 组件 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 后端与前端运行环境 |
| Redmine | 任意版本（需 REST API） | 数据存储 |
| Redis | 6.0+（可选） | Token 黑名单，不部署则退出登录功能降级 |

---

## 二、Redmine 环境准备

### 1. 安装 Redmine

参考官方文档安装：https://www.redmine.org/projects/redmine/wiki/Installation

推荐使用 Docker 快速部署：

```bash
docker run -d \
  --name redmine \
  -p 3001:3000 \
  -e REDMINE_DB_POSTGRES=redmine-db \
  -e REDMINE_DB_USER=redmine \
  -e REDMINE_DB_PASSWORD=secret \
  redmine:latest
```

### 2. 配置 Redmine

1. 创建项目，记录 **项目标识符（Project Key）**，如 `pms`
2. 创建跟踪标签，名称设为 `人员信息`
3. 创建以下自定义字段（必须在「人员信息」跟踪标签下启用）：

| 字段名 | 类型 | 必填 |
|--------|------|------|
| 人员编号 | 文本 | 是 |
| 姓名 | 文本 | 是 |
| 性别 | 文本 | 否 |
| 年龄 | 整数 | 否 |
| 手机号 | 文本 | 否 |
| 邮箱 | 文本 | 否 |
| 部门 | 文本 | 否 |
| 职位 | 文本 | 否 |
| 入职时间 | 文本 | 否 |

4. 获取 API Key：右上角「个人账号」→「API 访问键」→「显示」

---

## 三、应用部署

### 方式一：直接运行（适用于开发/演示）

#### 1. 克隆代码

```bash
git clone git@github.com:Yangzy963/PMS.git
cd PMS
```

#### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

#### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填写实际配置：

```env
# Redmine 配置
REDMINE_BASE_URL=http://localhost:3001
REDMINE_API_KEY=从 Redmine 获取的 API Key
REDMINE_PROJECT_KEY=pms
REDMINE_TRACKER_NAME=人员信息

# JWT 密钥（务必修改为随机字符串）
SECRET_KEY=生成一个随机长字符串

# 管理员账号
ADMIN_USERNAME=admin
ADMIN_PASSWORD=修改为强密码

# Redis（可选，不填则退出功能降级）
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
```

> **生成 SECRET_KEY**：`python -c "import secrets; print(secrets.token_urlsafe(32))"`

#### 4. 启动服务

```bash
# 终端 1：启动后端
cd backend
python main.py
```

```bash
# 终端 2：启动前端
cd frontend
python app.py
```

启动后浏览器访问：

| 服务 | 地址 |
|------|------|
| 前端页面 | http://127.0.0.1:8050 |
| 后端 API 文档 | http://127.0.0.1:8000/docs |
| 健康检查 | http://127.0.0.1:8000/health |

> **注意**：后端监听地址是 `0.0.0.0:8000`（表示接受所有网络接口的连接），但浏览器访问时请用 `127.0.0.1`，`0.0.0.0` 不是有效的访问地址。

---

### 方式二：Windows 后台运行

直接 `python main.py` 的方式关闭终端就会停止服务。如需后台持续运行，推荐使用 **NSSM**（Non-Sucking Service Manager）将应用注册为 Windows 服务。

#### 1. 安装 NSSM

```powershell
# 使用 winget 安装
winget install nssm

# 或从官网下载：https://nssm.cc/download
```

#### 2. 注册后端服务

```powershell
# 以管理员身份运行 PowerShell
nssm install PMS-Backend
```

在弹出的窗口中填写：

| 字段 | 值 |
|------|-----|
| Application Path | `C:\path\to\PMS\.venv\Scripts\python.exe` |
| Startup Directory | `C:\path\to\PMS\backend` |
| Arguments | `main.py` |

#### 3. 注册前端服务

```powershell
nssm install PMS-Frontend
```

| 字段 | 值 |
|------|-----|
| Application Path | `C:\path\to\PMS\.venv\Scripts\python.exe` |
| Startup Directory | `C:\path\to\PMS\frontend` |
| Arguments | `app.py` |

#### 4. 启动与管理

```powershell
# 启动服务
nssm start PMS-Backend
nssm start PMS-Frontend

# 查看状态
nssm status PMS-Backend

# 停止服务
nssm stop PMS-Backend

# 卸载服务
nssm remove PMS-Backend confirm
```

注册完成后，服务会随 Windows 开机自动启动。

---

## 四、Redis 部署（可选）

### Windows

```powershell
# Docker 方式（推荐）
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 或下载 Windows 版 Redis：https://github.com/tporadowski/redis/releases
```

### Linux/Mac

```bash
# Docker
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 包管理器
sudo apt install redis-server   # Debian/Ubuntu
brew install redis              # macOS
```

不部署 Redis 的影响：
- 退出登录后 Token 不会被加入黑名单（已签发的 Token 在有效期内仍可使用）
- 用户仍可正常登录和操作

---

## 五、安全加固清单

部署到生产环境前，务必完成以下检查：

- [ ] 修改 `.env` 中 `SECRET_KEY` 为随机长字符串
- [ ] 修改 `ADMIN_PASSWORD` 为强密码
- [ ] CORS `allow_origins` 限制为前端实际域名（`backend/main.py` 第 19 行）
- [ ] 将密码改为 bcrypt 哈希存储（`backend/app/services/auth_services.py`）
- [ ] 配置 HTTPS（Nginx 反向代理 + SSL 证书）
- [ ] 设置防火墙，仅暴露必要端口
- [ ] 定期备份 Redmine 数据

---

## 六、验证部署

```bash
# 健康检查
curl http://127.0.0.1:8000/health
# 预期: {"status":"ok","app":"人员信息管理系统","version":"1.0.0"}

# API 文档可访问
curl -s http://127.0.0.1:8000/docs -o /dev/null -w "%{http_code}"
# 预期: 200

# 前端可访问
curl -s http://127.0.0.1:8050 -o /dev/null -w "%{http_code}"
# 预期: 200
```

---

## 七、常见部署问题

### 1. 启动报 `ModuleNotFoundError: No module named 'fastapi'`

确保虚拟环境已激活，且依赖已安装：

```bash
# Windows
.\.venv\Scripts\activate
pip install -r backend/requirements.txt

# Linux/Mac
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. 浏览器访问 `http://0.0.0.0:8000` 打不开

`0.0.0.0` 是服务端监听地址（表示监听本机所有网卡），不能直接在浏览器中使用。请访问：

```
http://127.0.0.1:8000/docs
http://localhost:8000/docs
```

### 3. Redmine 连接失败（新增人员报 500）

```bash
# 测试 Redmine API 连通性
curl -H "X-Redmine-API-Key: your-key" http://your-redmine-host/issues.json?limit=1
```

常见原因：
- `.env` 中 `REDMINE_BASE_URL` 地址不正确
- `REDMINE_API_KEY` 无效或过期
- Redmine 服务未启动
- Redmine 中缺少必需的自定义字段（见第二章配置）

### 4. 前端页面加载但数据为空

确认 `frontend/services/api_client.py` 中的 `BASE_URL` 指向正确的后端地址（默认 `http://127.0.0.1:8000`）。

### 5. 导入 Excel 报错 `Missing optional dependency 'openpyxl'`

```bash
pip install openpyxl
```
