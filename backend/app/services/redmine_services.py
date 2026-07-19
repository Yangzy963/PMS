from datetime import datetime
from typing import Any, Optional
from urllib.parse import urljoin

import requests

from app.core.config import settings
from app.core.exceptions import NotFoundException, RedmineException, ValidationException


# 排序字段映射：前端字段名 -> Redmine 排序参数
# None 表示该字段不支持 Redmine 原生排序，需本地排序
_SORT_FIELD_MAP = {
    "number": None,      # 本地排序
    "name": None,        # 本地排序
    "gender": None,      # 本地排序
    "age": None,         # 本地排序
    "phone": None,       # 本地排序
    "email": None,       # 本地排序
    "department": None,  # 本地排序
    "position": None,    # 本地排序
    "jointime": None,    # 本地排序
    "createtime": "created_on",
    "updatetime": "updated_on",
}

_SORT_DIRECTIONS = {"asc", "desc"}


class RedmineClient:
    """Redmine REST API 客户端（原生 requests 实现）"""

    def __init__(self):
        self.base_url = settings.REDMINE_BASE_URL.rstrip("/")
        self.api_key = settings.REDMINE_API_KEY
        self.project_key = settings.REDMINE_PROJECT_KEY
        self.tracker_name = settings.REDMINE_TRACKER_NAME

        self.session = requests.Session()
        self.session.headers.update({
            "X-Redmine-API-Key": self.api_key,
            "Content-Type": "application/json",
        })

        # 缓存项目、跟踪标签、自定义字段信息
        self._project_id: Optional[int] = None
        self._tracker_id: Optional[int] = None
        self._custom_field_map: Optional[dict[str, int]] = None

    def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> dict:
        """发起 HTTP 请求并处理响应"""
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        response = self.session.request(method, url, **kwargs)

        if response.status_code >= 400:
            raise RedmineException(
                message=f"Redmine 请求失败 [{response.status_code}]: {response.text}"
            )

        if response.status_code == 204 or not response.text:
            return {}

        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    # ====================== 元数据查询 ======================

    def get_project_id(self) -> int:
        """获取项目 ID"""
        if self._project_id is not None:
            return self._project_id

        data = self._request("GET", f"/projects/{self.project_key}.json")
        project = data.get("project")
        if not project:
            raise NotFoundException(f"Redmine 项目 {self.project_key} 不存在")

        self._project_id = project["id"]
        return self._project_id

    def get_tracker_id(self) -> int:
        """获取跟踪标签 ID"""
        if self._tracker_id is not None:
            return self._tracker_id

        data = self._request("GET", "/trackers.json")
        trackers = data.get("trackers", [])

        for tracker in trackers:
            if tracker["name"] == self.tracker_name:
                self._tracker_id = tracker["id"]
                return self._tracker_id

        raise NotFoundException(f"Redmine 跟踪标签 {self.tracker_name} 不存在")

    def get_custom_field_map(self) -> dict[str, int]:
        """获取自定义字段名称到 ID 的映射"""
        if self._custom_field_map is not None:
            return self._custom_field_map

        data = self._request("GET", "/custom_fields.json")
        fields = data.get("custom_fields", [])

        required_names = {
            "人员编号", "姓名", "性别", "年龄", "手机号",
            "邮箱", "部门", "职位", "入职时间",
        }
        mapping = {}

        for field in fields:
            if field["name"] in required_names:
                mapping[field["name"]] = field["id"]

        missing = required_names - set(mapping.keys())
        if missing:
            raise NotFoundException(f"Redmine 缺少自定义字段: {missing}")

        self._custom_field_map = mapping
        return self._custom_field_map

    def get_custom_field_id(self, name: str) -> int:
        """根据字段名获取自定义字段 ID"""
        mapping = self.get_custom_field_map()
        field_id = mapping.get(name)
        if field_id is None:
            raise NotFoundException(f"Redmine 自定义字段 {name} 不存在")
        return field_id

    # ====================== 数据转换 ======================

    def _build_subject(self, employee: dict) -> str:
        """生成 Issue 主题：【人员编号】姓名"""
        return f"【{employee.get('number', '')}】{employee.get('name', '')}"

    def _build_custom_fields(self, employee: dict) -> list[dict]:
        """将员工字典转成 Redmine custom_fields 数组"""
        mapping = self.get_custom_field_map()

        field_values = [
            ("人员编号", employee.get("number")),
            ("姓名", employee.get("name")),
            ("性别", employee.get("gender")),
            ("年龄", employee.get("age")),
            ("手机号", employee.get("phone")),
            ("邮箱", employee.get("email")),
            ("部门", employee.get("department")),
            ("职位", employee.get("position")),
            ("入职时间", employee.get("jointime")),
        ]

        custom_fields = []
        for name, value in field_values:
            if value is not None and value != "":
                custom_fields.append({
                    "id": mapping[name],
                    "value": value,
                })

        return custom_fields

    def _parse_custom_fields(self, custom_fields: list[dict]) -> dict:
        """将 Redmine custom_fields 数组解析成员工字典"""
        result = {}
        mapping = self.get_custom_field_map()
        name_by_id = {v: k for k, v in mapping.items()}

        for field in custom_fields:
            name = name_by_id.get(field["id"])
            if name:
                value = field.get("value")
                if name == "年龄":
                    try:
                        value = int(value) if value is not None else None
                    except (ValueError, TypeError):
                        value = None
                result[name] = value

        return result

    def _issue_to_employee(self, issue: dict) -> dict:
        """将 Redmine Issue 转为员工字典"""
        custom = self._parse_custom_fields(issue.get("custom_fields", []))

        return {
            "id": issue.get("id"),
            "number": custom.get("人员编号", ""),
            "name": custom.get("姓名", ""),
            "gender": custom.get("性别", ""),
            "age": custom.get("年龄"),
            "phone": custom.get("手机号", ""),
            "email": custom.get("邮箱", ""),
            "department": custom.get("部门", ""),
            "position": custom.get("职位", ""),
            "jointime": custom.get("入职时间", ""),
            "createtime": issue.get("created_on", ""),
            "updatetime": issue.get("updated_on", ""),
        }

    def _fetch_all_issues(self, base_params: dict) -> list[dict]:
        """
        分批从 Redmine 拉取所有 Issue

        Redmine REST API 单次最多返回 100 条记录，
        因此需要通过多次请求 offset/limit 来获取全部数据。
        """
        all_issues = []
        offset = 0
        batch_size = 100

        while True:
            params = {
                **base_params,
                "offset": offset,
                "limit": batch_size,
            }
            data = self._request("GET", "/issues.json", params=params)
            issues = data.get("issues", [])

            if not issues:
                break

            all_issues.extend(issues)

            # Redmine 返回数量不足 batch_size，说明已经取完
            if len(issues) < batch_size:
                break

            offset += batch_size

        return all_issues

    def create_employee(self, employee: dict) -> dict:
        """创建员工"""
        project_id = self.get_project_id()
        tracker_id = self.get_tracker_id()

        payload = {
            "issue": {
                "project_id": project_id,
                "tracker_id": tracker_id,
                "subject": self._build_subject(employee),
                "custom_fields": self._build_custom_fields(employee),
            }
        }

        data = self._request("POST", "/issues.json", json=payload)
        issue = data.get("issue")
        if not issue:
            raise RedmineException("创建员工失败，Redmine 未返回 Issue 数据")

        return self._issue_to_employee(issue)

    def get_employee(self, issue_id: int) -> dict:
        """根据 Issue ID 获取员工详情"""
        data = self._request("GET", f"/issues/{issue_id}.json?include=custom_fields")
        issue = data.get("issue")
        if not issue:
            raise NotFoundException(f"员工 {issue_id} 不存在")

        return self._issue_to_employee(issue)

    def update_employee(self, issue_id: int, employee: dict) -> dict:
        """更新员工"""
        payload = {
            "issue": {
                "subject": self._build_subject(employee),
                "custom_fields": self._build_custom_fields(employee),
            }
        }

        self._request("PUT", f"/issues/{issue_id}.json", json=payload)
        return self.get_employee(issue_id)

    def delete_employee(self, issue_id: int) -> None:
        """删除员工"""
        self._request("DELETE", f"/issues/{issue_id}.json")

    def list_employees(
        self,
        offset: int = 0,
        limit: int = 20,
        sort: str = "created_on:desc",
        filters: Optional[dict[str, Any]] = None,
    ) -> tuple[list[dict], int]:
        """
        查询员工列表

        Redmine 自定义字段过滤对文本类型默认是模糊匹配，不够精确，
        因此先按 tracker 拉取数据，然后在服务端做精确/模糊过滤和分页。

        :param filters: 筛选条件，例如 {"name": "张", "department": "技术部"}
        :return: (员工列表, 总数)
        """
        project_id = self.get_project_id()
        tracker_id = self.get_tracker_id()

        base_params = {
            "project_id": project_id,
            "tracker_id": tracker_id,
            "sort": sort,
            "status_id": "*",  # 包含所有状态
            "include": "custom_fields",
        }

        issues = self._fetch_all_issues(base_params)

        employees = [self._issue_to_employee(issue) for issue in issues]

        # 本地过滤
        if filters:
            employees = self._filter_employees(employees, filters)

        # 本地排序（Redmine API 只支持 created_on/updated_on 排序）
        employees = self._sort_employees(employees, sort)

        total = len(employees)

        # 分页
        paginated = employees[offset:offset + limit]
        return paginated, total

    def _filter_employees(self, employees: list[dict], filters: dict[str, Any]) -> list[dict]:
        """本地过滤员工列表"""
        result = employees

        if filters.get("name"):
            keyword = filters["name"]
            result = [e for e in result if keyword in (e.get("name") or "")]

        if filters.get("department"):
            dept = filters["department"]
            result = [e for e in result if dept == (e.get("department") or "")]

        if filters.get("position"):
            pos = filters["position"]
            result = [e for e in result if pos == (e.get("position") or "")]

        if filters.get("number"):
            number = filters["number"]
            result = [e for e in result if number == (e.get("number") or "")]

        if filters.get("gender"):
            gender = filters["gender"]
            result = [e for e in result if gender == (e.get("gender") or "")]

        if filters.get("phone"):
            phone = filters["phone"]
            result = [e for e in result if phone in (e.get("phone") or "")]

        if filters.get("email"):
            email = filters["email"]
            result = [e for e in result if email in (e.get("email") or "")]

        if filters.get("jointime_start") or filters.get("jointime_end"):
            start = filters.get("jointime_start") or ""
            end = filters.get("jointime_end") or ""
            filtered = []
            for e in result:
                jointime = e.get("jointime") or ""
                if not jointime:
                    continue
                if start and jointime < start:
                    continue
                if end and jointime > end:
                    continue
                filtered.append(e)
            result = filtered

        return result

    @staticmethod
    def _sort_employees(employees: list[dict], sort: str) -> list[dict]:
        """
        本地排序员工列表

        :param sort: 排序表达式，如 "number:asc", "age:desc", "createtime:desc"
        """
        if ":" not in sort:
            return employees

        field, direction = sort.rsplit(":", 1)
        direction = direction.lower()

        if field not in _SORT_FIELD_MAP or direction not in _SORT_DIRECTIONS:
            return employees

        reverse = direction == "desc"

        # 根据字段类型选择排序 key
        def sort_key(emp: dict):
            value = emp.get(field)
            if value is None or value == "":
                # None/空值排到最后
                return (1, "" if reverse else "￿")
            if field == "age":
                return (0, int(value))
            return (0, str(value))

        return sorted(employees, key=sort_key, reverse=reverse)

    def _filter_key_to_name(self, key: str) -> Optional[str]:
        """将查询参数 key 映射到自定义字段中文名"""
        mapping = {
            "number": "人员编号",
            "name": "姓名",
            "gender": "性别",
            "age": "年龄",
            "phone": "手机号",
            "email": "邮箱",
            "department": "部门",
            "position": "职位",
            "jointime": "入职时间",
        }
        return mapping.get(key)

    def find_by_number(self, number: str) -> Optional[dict]:
        """根据人员编号精确查找员工"""
        if not number:
            return None

        project_id = self.get_project_id()
        tracker_id = self.get_tracker_id()

        base_params = {
            "project_id": project_id,
            "tracker_id": tracker_id,
            "status_id": "*",
            "include": "custom_fields",
        }

        issues = self._fetch_all_issues(base_params)

        for issue in issues:
            employee = self._issue_to_employee(issue)
            if employee.get("number") == number:
                return employee

        return None


# 全局客户端实例
redmine_client = RedmineClient()
