import requests


BASE_URL = "http://127.0.0.1:8000"


def logout(token: str) -> dict:
    """退出登录"""
    return api_request("POST", "/api/v1/logout", token=token)


def login(username: str, password: str) -> dict:
    """
    用户登录

    后端使用 OAuth2PasswordRequestForm，需要用 form-data 提交
    """
    response = requests.post(
        f"{BASE_URL}/api/v1/login",
        data={
            "username": username,
            "password": password,
        },
    )
    return response.json()


def api_request(method: str, path: str, token: str = None, **kwargs) -> dict:
    """
    带认证的通用 API 请求

    :param method: HTTP 方法，如 GET/POST/PUT/DELETE
    :param path: API 路径，如 /api/v1/employees
    :param token: JWT Token
    """
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{BASE_URL}{path}"
    response = requests.request(method, url, headers=headers, **kwargs)
    return response.json()


def get_employees(token: str, params: dict = None) -> dict:
    """查询人员列表"""
    return api_request("GET", "/api/v1/employees", token=token, params=params)


def get_employee(token: str, employee_id: int) -> dict:
    """查询人员详情"""
    return api_request("GET", f"/api/v1/employees/{employee_id}", token=token)


def create_employee(token: str, data: dict) -> dict:
    """新增人员"""
    return api_request("POST", "/api/v1/employees", token=token, json=data)


def update_employee(token: str, employee_id: int, data: dict) -> dict:
    """修改人员"""
    return api_request("PUT", f"/api/v1/employees/{employee_id}", token=token, json=data)


def delete_employee(token: str, employee_id: int) -> dict:
    """删除人员"""
    return api_request("DELETE", f"/api/v1/employees/{employee_id}", token=token)


def batch_delete_employees(token: str, employee_ids: list) -> dict:
    """批量删除人员"""
    return api_request("POST", "/api/v1/employees/batch-delete", token=token, json=employee_ids)


def import_employees(token: str, files: dict, strategy: str = "skip") -> dict:
    """导入人员数据"""
    return api_request(
        "POST",
        f"/api/v1/import/employees?strategy={strategy}",
        token=token,
        files=files,
    )
