"""
单元测试：Redmine 数据映射与转换（不调用真实 API）
"""
import pytest


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch):
    """Mock Redmine 配置"""
    monkeypatch.setattr("app.core.config.settings.REDMINE_BASE_URL", "http://fake-redmine:3000")
    monkeypatch.setattr("app.core.config.settings.REDMINE_API_KEY", "fake-key")
    monkeypatch.setattr("app.core.config.settings.REDMINE_PROJECT_KEY", "pms")
    monkeypatch.setattr("app.core.config.settings.REDMINE_TRACKER_NAME", "人员信息")


class TestSubjectBuilder:
    """Issue 主题生成"""

    def test_normal(self):
        """正常主题"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        assert client._build_subject({"number": "001", "name": "张三"}) == "【001】张三"

    def test_empty_number(self):
        """空编号"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        assert client._build_subject({"number": "", "name": "张三"}) == "【】张三"

    def test_empty_name(self):
        """空姓名"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        assert client._build_subject({"number": "001", "name": ""}) == "【001】"


class TestSort:
    """本地排序"""

    def _employees(self):
        return [
            {"number": "003", "name": "王五", "age": 25, "jointime": "2023-01-01"},
            {"number": "001", "name": "张三", "age": 30, "jointime": "2022-06-15"},
            {"number": "002", "name": "李四", "age": None, "jointime": ""},
        ]

    def test_sort_number_asc(self):
        """编号升序"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._sort_employees(self._employees(), "number:asc")
        assert [e["number"] for e in result] == ["001", "002", "003"]

    def test_sort_number_desc(self):
        """编号降序"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._sort_employees(self._employees(), "number:desc")
        assert [e["number"] for e in result] == ["003", "002", "001"]

    def test_sort_age_asc(self):
        """年龄升序，None 排最后"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._sort_employees(self._employees(), "age:asc")
        ages = [e["age"] for e in result]
        assert ages == [25, 30, None]

    def test_sort_age_desc(self):
        """年龄降序，None 排最后"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._sort_employees(self._employees(), "age:desc")
        ages = [e["age"] for e in result]
        assert ages == [30, 25, None]

    def test_sort_jointime_desc(self):
        """入职时间降序"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._sort_employees(self._employees(), "jointime:desc")
        jointimes = [e["jointime"] for e in result]
        assert jointimes == ["2023-01-01", "2022-06-15", ""]

    def test_sort_invalid_direction(self):
        """无效排序方向，返回原序"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._sort_employees(self._employees(), "number:xxx")
        assert [e["number"] for e in result] == ["003", "001", "002"]

    def test_sort_unsupported_field(self):
        """不支持的字段"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._sort_employees(self._employees(), "xyz:asc")
        assert [e["number"] for e in result] == ["003", "001", "002"]
