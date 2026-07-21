# 开发指南

## 一、开发环境搭建

```bash
# 1. 克隆代码
git clone <仓库地址>
cd PMS

# 2. 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .\.venv\Scripts\activate  # Windows

# 3. 安装所有依赖
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
pip install -r requirements-dev.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 填写 Redmine 配置
```

---

## 二、运行测试

### 运行全部测试

```bash
# 项目根目录下
pytest tests/ -v
```

### 按测试类型运行

```bash
# 单元测试（无外部依赖，最快）
pytest tests/unit/ -v

# API 接口测试（httpx TestClient）
pytest tests/api/ -v

# 集成测试（需要 Redmine 运行）
pytest tests/integration/ -v -m integration

# UI 自动化测试（需要前后端已启动）
pytest tests/ui/ -v

# 跳过集成测试（不需要 Redmine）
pytest tests/ -v -m "not integration"

# 所有测试以 Allure 方式执行（跑完统一查看报告）
pytest tests/ -v --alluredir=./allure-results
allure serve ./allure-results
```

---

### 覆盖率（对照 requirements.md 五项指标）

```bash
# 清空旧数据
coverage erase

# 1. 单元测试覆盖率（目标 ≥80%）
pytest tests/unit/ -v --cov=backend --cov-report=term --alluredir=./allure-results

# 2. 核心业务模块覆盖率（目标 ≥90%）
pytest tests/unit/ -v \
  --cov=backend/app/services \
  --cov=backend/app/schemas \
  --cov=backend/app/utils \
  --cov=backend/app/core/config.py \
  --cov=backend/app/core/exceptions.py \
  --cov=backend/security.py \
  --cov-report=term --alluredir=./allure-results

# 3. 接口覆盖率（目标 100%）
pytest tests/api/ -v --cov=backend --cov-report=term --alluredir=./allure-results

# 4. 集成测试覆盖率（目标 100%）
pytest tests/integration/ -v --cov=backend --cov-report=term --alluredir=./allure-results

# 5. UI 测试覆盖率（见下方「UI 测试覆盖率」小节）

# 五条跑完后，一次性查看所有 Allure 报告
allure serve ./allure-results
```


---

### UI 测试覆盖率

UI 测试通过 HTTP 请求与后端通信，后端是独立进程，pytest-cov 无法统计。需给后端进程单独挂 coverage：

```powershell
# 终端 1：后端挂 coverage 启动
cd D:\OSP\PMS
$env:COVERAGE_FILE = ".coverage_ui"
coverage run --source=backend/app backend/main.py

# 终端 2：跑 UI 测试
pytest tests/ui/ -v --alluredir=./allure-results

# 终端 1 按 Ctrl+C 优雅退出后查看
coverage report
```

### UI 测试注意事项

```bash
# 首次运行需安装 Playwright 浏览器
playwright install chromium

# UI 测试需要前后端都已启动
# 终端 1:
cd backend && python main.py

# 终端 2:
cd frontend && python app.py

# 终端 3: 默认无头模式（后台运行，不弹出浏览器窗口）
pytest tests/ui/ -v

# 有头模式（弹出浏览器窗口，可观察操作过程，便于调试）
pytest tests/ui/ -v --headed

# 有头 + 慢放（每步操作间隔 1 秒，方便看清步骤）
pytest tests/ui/ -v --headed --slowmo 1000

# 失败时自动截图（保存在 test-results/ 目录）
pytest tests/ui/ -v --screenshot only-on-failure

# 生成 Playwright Trace 文件（可用 playwright show-trace 回放）
pytest tests/ui/ -v --tracing on

# 运行单个 UI 测试文件
pytest tests/ui/test_login.py -v --headed
```

---

## 三、代码规范

### PEP 8

项目遵循 PEP 8 编码规范，可使用以下工具检查：

```bash
# 代码格式化
black backend/ frontend/ tests/

# 代码检查
flake8 backend/ frontend/ tests/ --max-line-length=100
```

### Git 提交规范

```text
feat: 新功能
fix: 修复 bug
docs: 文档更新
test: 测试相关
refactor: 代码重构
chore: 构建/工具/依赖更新
```

示例：
```bash
git commit -m "feat: 实现人员导出功能"
git commit -m "fix: 修复空值排序崩溃问题"
```

---

## 四、项目架构速览

### 后端：分层架构

```
api/          ← 路由层：处理 HTTP 请求，参数解析，调用 Service
  └── v1/
      ├── auth.py
      ├── employee.py
      └── employee_import.py

services/     ← 业务层：核心逻辑，与 Redmine/Redis 交互
  ├── auth_services.py
  ├── redmine_services.py    ← RedmineClient 核心类（500+ 行）
  └── import_services.py

schemas/      ← 数据层：Pydantic 模型，请求/响应定义
  ├── common.py
  ├── employee.py
  └── user.py

core/         ← 基础设施
  ├── config.py         ← Settings（Pydantic Settings，加载 .env）
  ├── exceptions.py     ← 异常类体系
  └── middleware.py      ← 全局异常处理

utils/        ← 工具函数
  ├── response.py       ← 统一响应格式
  ├── excel.py          ← 文件解析
  └── password.py       ← 密码工具
```

### 前端：Dash 多页面应用

```
app.py                  ← Dash 实例 + 全局 callback（登录状态/路由守卫）
pages/
  ├── login.py          ← dash.register_page("/") 登录页面
  └── employee.py       ← dash.register_page("/employee") 人员管理页面
components/
  ├── navbar.py         ← 导航栏组件
  ├── search_bar.py     ← 搜索栏组件
  ├── employee_table.py ← 人员表格组件
  └── employee_form.py  ← 新增/编辑 Modal 表单组件
services/
  └── api_client.py     ← 所有后端 API 调用封装
```

### 数据流

```
前端 Dash → api_client.py (HTTP) → FastAPI Route → Service → RedmineClient
                                                              ↓
                                                         Redmine API
```

---

## 五、添加新功能指南

### 添加新的 API 接口

1. 在 `backend/app/schemas/` 定义请求/响应模型
2. 在 `backend/app/services/` 实现业务逻辑
3. 在 `backend/app/api/v1/` 添加路由处理函数
4. 在 `backend/app/api/router.py` 注册路由

### 添加新的前端页面

1. 在 `frontend/pages/` 新建 `page_name.py`
2. 使用 `dash.register_page(__name__, path="/page-path", title="页面标题")`
3. 定义 `layout` 变量和 callback
4. 页面自动注册到 Dash 路由，无需手动修改 `app.py`

### 添加新的前端组件

1. 在 `frontend/components/` 新建 `component_name.py`
2. 定义组件函数，返回 Dash HTML 元素
3. 在页面中 `from components.component_name import component_name`

---

## 六、Redmine 自定义字段扩展

如需添加新的员工字段（如"工号"）：

### 1. Redmine 侧

在 Redmine 管理页面创建自定义字段，名称如 `工号`

### 2. 后端修改

**`backend/app/schemas/employee.py`**：
```python
class EmployeeBase(BaseModel):
    # ... 现有字段 ...
    work_id: Optional[str] = Field(None, max_length=50, description="工号")
```

**`backend/app/services/redmine_services.py`**：
```python
# get_custom_field_map() 的 required_names 中添加 "工号"
# _build_custom_fields() 的 field_values 中添加 ("工号", employee.get("work_id"))
# _issue_to_employee() 中添加 "work_id": custom.get("工号", "")
```

### 3. 前端修改

在 `employee_form.py` 和 `employee_table.py` 中添加对应字段的输入框和列。

---

## 七、调试技巧

### 后端调试

```bash
# 开启 DEBUG 模式（默认开启）
# .env 中设置 DEBUG=True，后端会自动 reload
cd backend && python main.py
```

### 查看 Redmine API 原始请求

在 `redmine_services.py` 的 `_request()` 方法中添加日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# 在 _request() 中添加:
logger.debug(f"{method} {url} -> {response.status_code}")
```

### 前端调试

Dash 默认开启热重载，修改代码后浏览器自动刷新。浏览器 DevTools → Console 可查看 callback 错误。

### 测试单个用例

```bash
pytest tests/unit/test_schemas.py::test_employee_create -v
pytest tests/api/test_auth.py::test_login_success -v
```
