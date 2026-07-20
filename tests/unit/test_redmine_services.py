"""
单元测试：Redmine 数据映射与转换（不调用真实 API）
"""
import pytest
from unittest.mock import patch
from unittest.mock import patch


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

    def test_sort_no_colon(self):
        """无冒号的排序表达式返回原序"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._sort_employees(self._employees(), "number")
        assert [e["number"] for e in result] == ["003", "001", "002"]

    def test_sort_mixed_none_and_empty(self):
        """混合 None 和空字符串的排序"""
        from app.services.redmine_services import RedmineClient
        data = [
            {"number": "003", "jointime": None},
            {"number": "001", "jointime": ""},
            {"number": "002", "jointime": "2023-06-01"},
        ]
        result = RedmineClient._sort_employees(data, "jointime:asc")
        assert result[0]["number"] == "002"
        # None 和 "" 都在末尾
        assert result[1]["jointime"] in (None, "")
        assert result[2]["jointime"] in (None, "")


class TestFilterEmployees:
    """本地过滤"""

    def _employees(self):
        return [
            {"number": "001", "name": "张三", "department": "研发部", "position": "工程师",
             "gender": "男", "phone": "13800000001", "email": "a@b.com", "jointime": "2023-01-01"},
            {"number": "002", "name": "李四", "department": "测试部", "position": "经理",
             "gender": "女", "phone": "13800000002", "email": "c@d.com", "jointime": "2024-06-15"},
            {"number": "003", "name": "王小明", "department": "研发部", "position": "工程师",
             "gender": "男", "phone": "13800000003", "email": "e@f.com", "jointime": ""},
        ]

    def test_filter_by_name_fuzzy(self):
        """姓名模糊过滤"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(None, self._employees(), {"name": "张"})
        assert len(result) == 1
        assert result[0]["number"] == "001"

    def test_filter_by_department_exact(self):
        """部门精确过滤"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(None, self._employees(), {"department": "研发部"})
        assert len(result) == 2

    def test_filter_by_position_exact(self):
        """职位精确过滤"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(None, self._employees(), {"position": "经理"})
        assert len(result) == 1
        assert result[0]["name"] == "李四"

    def test_filter_by_number_exact(self):
        """编号精确过滤"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(None, self._employees(), {"number": "002"})
        assert len(result) == 1

    def test_filter_by_gender(self):
        """性别过滤"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(None, self._employees(), {"gender": "男"})
        assert len(result) == 2

    def test_filter_by_phone_fuzzy(self):
        """手机号模糊过滤"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(None, self._employees(), {"phone": "0000001"})
        assert len(result) == 1

    def test_filter_by_email_fuzzy(self):
        """邮箱模糊过滤"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(None, self._employees(), {"email": "b.com"})
        assert len(result) == 1

    def test_filter_by_jointime_range(self):
        """入职时间范围过滤"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(
            None, self._employees(),
            {"jointime_start": "2023-01-01", "jointime_end": "2024-01-01"},
        )
        assert len(result) == 1
        assert result[0]["number"] == "001"

    def test_filter_by_jointime_start_only(self):
        """仅入职开始时间"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(
            None, self._employees(), {"jointime_start": "2024-01-01"},
        )
        assert len(result) == 1
        assert result[0]["number"] == "002"

    def test_filter_by_jointime_end_only(self):
        """仅入职结束时间"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(
            None, self._employees(), {"jointime_end": "2023-06-01"},
        )
        assert len(result) == 1
        assert result[0]["number"] == "001"

    def test_filter_empty_filters(self):
        """空过滤条件"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(None, self._employees(), {})
        assert len(result) == 3

    def test_filter_multiple_conditions(self):
        """多条件组合"""
        from app.services.redmine_services import RedmineClient
        result = RedmineClient._filter_employees(
            None, self._employees(),
            {"department": "研发部", "gender": "男"},
        )
        assert len(result) == 2


class TestFilterKeyToName:
    """filter key -> 中文名映射"""

    def test_valid_keys(self):
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        assert client._filter_key_to_name("number") == "人员编号"
        assert client._filter_key_to_name("name") == "姓名"
        assert client._filter_key_to_name("gender") == "性别"
        assert client._filter_key_to_name("age") == "年龄"
        assert client._filter_key_to_name("phone") == "手机号"
        assert client._filter_key_to_name("email") == "邮箱"
        assert client._filter_key_to_name("department") == "部门"
        assert client._filter_key_to_name("position") == "职位"
        assert client._filter_key_to_name("jointime") == "入职时间"

    def test_invalid_key(self):
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        assert client._filter_key_to_name("xyz") is None


class TestBuildCustomFields:
    """构建 Redmine custom_fields"""

    def test_build_with_all_fields(self):
        """完整字段"""
        with patch(
            "app.services.redmine_services.RedmineClient.get_custom_field_map",
            return_value={
                "人员编号": 1, "姓名": 2, "性别": 3, "年龄": 4,
                "手机号": 5, "邮箱": 6, "部门": 7, "职位": 8, "入职时间": 9,
            },
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            emp = {
                "number": "001", "name": "张三", "gender": "男", "age": 30,
                "phone": "138", "email": "a@b.com", "department": "研发部",
                "position": "工程师", "jointime": "2023-01-01",
            }
            fields = client._build_custom_fields(emp)
            assert len(fields) == 9

    def test_build_skip_none_and_empty(self):
        """跳过 None 和空字符串"""
        with patch(
            "app.services.redmine_services.RedmineClient.get_custom_field_map",
            return_value={
                "人员编号": 1, "姓名": 2, "性别": 3, "年龄": 4,
                "手机号": 5, "邮箱": 6, "部门": 7, "职位": 8, "入职时间": 9,
            },
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            emp = {"number": "001", "name": "张三", "gender": ""}
            fields = client._build_custom_fields(emp)
            assert len(fields) == 2


class TestParseCustomFields:
    """解析 Redmine custom_fields"""

    def test_parse_all_fields(self):
        """所有字段解析"""
        with patch(
            "app.services.redmine_services.RedmineClient.get_custom_field_map",
            return_value={
                "人员编号": 1, "姓名": 2, "性别": 3, "年龄": 4,
                "手机号": 5, "邮箱": 6, "部门": 7, "职位": 8, "入职时间": 9,
            },
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            cf = [
                {"id": 1, "value": "001"},
                {"id": 2, "value": "张三"},
                {"id": 4, "value": "30"},
                {"id": 9, "value": "2023-01-01"},
            ]
            result = client._parse_custom_fields(cf)
            assert result["人员编号"] == "001"
            assert result["姓名"] == "张三"
            assert result["年龄"] == 30
            assert result["入职时间"] == "2023-01-01"

    def test_parse_age_invalid(self):
        """年龄解析失败返回 None"""
        with patch(
            "app.services.redmine_services.RedmineClient.get_custom_field_map",
            return_value={"年龄": 4},
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            result = client._parse_custom_fields([{"id": 4, "value": "abc"}])
            assert result["年龄"] is None

    def test_parse_age_none(self):
        """年龄为 None"""
        with patch(
            "app.services.redmine_services.RedmineClient.get_custom_field_map",
            return_value={"年龄": 4},
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            result = client._parse_custom_fields([{"id": 4, "value": None}])
            assert result["年龄"] is None

    def test_parse_unknown_field_id(self):
        """未知字段 ID"""
        with patch(
            "app.services.redmine_services.RedmineClient.get_custom_field_map",
            return_value={"姓名": 2},
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            result = client._parse_custom_fields([{"id": 999, "value": "xxx"}])
            assert "xxx" not in str(result)


class TestIssueToEmployee:
    """Issue -> Employee 转换"""

    def test_full_issue(self):
        """完整 Issue 转换"""
        with patch(
            "app.services.redmine_services.RedmineClient._parse_custom_fields",
            return_value={
                "人员编号": "001", "姓名": "张三", "性别": "男", "年龄": 30,
                "手机号": "138", "邮箱": "a@b.com", "部门": "研发部",
                "职位": "工程师", "入职时间": "2023-01-01",
            },
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            issue = {"id": 1, "created_on": "2023-01-01T00:00:00Z", "updated_on": "2023-06-01T00:00:00Z"}
            result = client._issue_to_employee(issue)
            assert result["id"] == 1
            assert result["number"] == "001"
            assert result["name"] == "张三"
            assert result["age"] == 30
            assert result["createtime"] == "2023-01-01T00:00:00Z"
            assert result["updatetime"] == "2023-06-01T00:00:00Z"

    def test_minimal_issue(self):
        """最小 Issue"""
        with patch(
            "app.services.redmine_services.RedmineClient._parse_custom_fields",
            return_value={},
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            issue = {"id": 1}
            result = client._issue_to_employee(issue)
            assert result["id"] == 1
            assert result["number"] == ""
            assert result["name"] == ""


class TestFindByNumber:
    """按编号查找"""

    def test_empty_number(self):
        """空编号返回 None"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        assert client.find_by_number("") is None

    def test_find_existing(self):
        """找到匹配"""
        employee = {"id": 1, "number": "001", "name": "张三"}
        with patch(
            "app.services.redmine_services.RedmineClient.get_project_id",
            return_value=1,
        ), patch(
            "app.services.redmine_services.RedmineClient.get_tracker_id",
            return_value=1,
        ), patch(
            "app.services.redmine_services.RedmineClient._fetch_all_issues",
            return_value=[{"id": 1, "custom_fields": []}],
        ), patch(
            "app.services.redmine_services.RedmineClient._issue_to_employee",
            return_value=employee,
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            result = client.find_by_number("001")
            assert result == employee

    def test_not_found(self):
        """未找到"""
        with patch(
            "app.services.redmine_services.RedmineClient.get_project_id",
            return_value=1,
        ), patch(
            "app.services.redmine_services.RedmineClient.get_tracker_id",
            return_value=1,
        ), patch(
            "app.services.redmine_services.RedmineClient._fetch_all_issues",
            return_value=[],
        ):
            from app.services.redmine_services import RedmineClient
            client = RedmineClient()
            result = client.find_by_number("999")
            assert result is None


class TestRequestStatusCodes:
    """_request 状态码处理（通过 mock requests.Session）"""

    def test_500_raises_redmine_exception(self):
        """500 状态码抛 RedmineException"""
        from unittest.mock import MagicMock
        from app.services.redmine_services import RedmineClient, RedmineException
        client = RedmineClient()
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        client.session = MagicMock()
        client.session.request.return_value = mock_resp
        with pytest.raises(RedmineException, match="500"):
            client._request("GET", "/test")

    def test_404_returns_status_dict(self):
        """404 返回 status_code 字典"""
        from unittest.mock import MagicMock
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        client.session = MagicMock()
        client.session.request.return_value = mock_resp
        result = client._request("GET", "/test")
        assert result == {"status_code": 404}

    def test_204_no_content(self):
        """204 返回空字典"""
        from unittest.mock import MagicMock
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        mock_resp = MagicMock()
        mock_resp.status_code = 204
        mock_resp.text = ""
        client.session = MagicMock()
        client.session.request.return_value = mock_resp
        result = client._request("GET", "/test")
        assert result == {}


class TestMetadataQueries:
    """元数据查询（get_project_id / get_tracker_id / get_custom_field_map）"""

    def test_get_project_id_cached(self):
        """缓存命中"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        client._project_id = 42
        assert client.get_project_id() == 42

    def test_get_project_id_fetch(self):
        """首次查询"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        mock_data = {"project": {"id": 1, "name": "pms"}}
        with patch.object(client, "_request", return_value=mock_data), \
             patch("app.services.redmine_services.settings.REDMINE_PROJECT_KEY", "pms"):
            client._project_id = None
            result = client.get_project_id()
            assert result == 1

    def test_get_project_id_not_found(self):
        """项目不存在"""
        from app.services.redmine_services import RedmineClient
        from app.core.exceptions import NotFoundException
        client = RedmineClient()
        client._project_id = None
        with patch.object(client, "_request", return_value={}), \
             patch("app.services.redmine_services.settings.REDMINE_PROJECT_KEY", "pms"):
            with pytest.raises(NotFoundException):
                client.get_project_id()

    def test_get_tracker_id_cached(self):
        """缓存命中"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        client._tracker_id = 7
        assert client.get_tracker_id() == 7

    def test_get_tracker_id_fetch(self):
        """首次查询 tracker"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        client._tracker_id = None
        mock_data = {"trackers": [
            {"id": 1, "name": "Bug"},
            {"id": 2, "name": "人员信息"},
        ]}
        with patch.object(client, "_request", return_value=mock_data), \
             patch("app.services.redmine_services.settings.REDMINE_TRACKER_NAME", "人员信息"):
            result = client.get_tracker_id()
            assert result == 2

    def test_get_tracker_id_not_found(self):
        """tracker 不存在"""
        from app.services.redmine_services import RedmineClient
        from app.core.exceptions import NotFoundException
        client = RedmineClient()
        client._tracker_id = None
        mock_data = {"trackers": [{"id": 1, "name": "Bug"}]}
        with patch.object(client, "_request", return_value=mock_data), \
             patch("app.services.redmine_services.settings.REDMINE_TRACKER_NAME", "人员信息"):
            with pytest.raises(NotFoundException):
                client.get_tracker_id()

    def test_get_custom_field_map_cached(self):
        """缓存命中"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        client._custom_field_map = {"人员编号": 1}
        assert client.get_custom_field_map() == {"人员编号": 1}

    def test_get_custom_field_map_fetch(self):
        """首次查询自定义字段"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        client._custom_field_map = None
        mock_data = {"custom_fields": [
            {"id": 1, "name": "人员编号"},
            {"id": 2, "name": "姓名"},
            {"id": 3, "name": "性别"},
            {"id": 4, "name": "年龄"},
            {"id": 5, "name": "手机号"},
            {"id": 6, "name": "邮箱"},
            {"id": 7, "name": "部门"},
            {"id": 8, "name": "职位"},
            {"id": 9, "name": "入职时间"},
        ]}
        with patch.object(client, "_request", return_value=mock_data):
            result = client.get_custom_field_map()
            assert result["人员编号"] == 1
            assert len(result) == 9

    def test_get_custom_field_map_missing_fields(self):
        """缺少必要自定义字段"""
        from app.services.redmine_services import RedmineClient
        from app.core.exceptions import NotFoundException
        client = RedmineClient()
        client._custom_field_map = None
        mock_data = {"custom_fields": [{"id": 1, "name": "人员编号"}]}
        with patch.object(client, "_request", return_value=mock_data):
            with pytest.raises(NotFoundException):
                client.get_custom_field_map()

    def test_get_custom_field_id(self):
        """根据名称获取字段 ID"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        client._custom_field_map = {"人员编号": 1, "姓名": 2}
        assert client.get_custom_field_id("姓名") == 2

    def test_get_custom_field_id_not_found(self):
        """字段名不存在"""
        from app.services.redmine_services import RedmineClient
        from app.core.exceptions import NotFoundException
        client = RedmineClient()
        client._custom_field_map = {"人员编号": 1}
        with pytest.raises(NotFoundException):
            client.get_custom_field_id("不存在的字段")


class TestFetchAllIssues:
    """分页拉取 Issue"""

    def test_single_page(self):
        """单页拉完"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        issues_page = [{"id": i} for i in range(5)]
        with patch.object(client, "_request", return_value={"issues": issues_page}):
            result = client._fetch_all_issues({"status_id": "*"})
            assert len(result) == 5

    def test_multi_page(self):
        """多页拉取"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        page1 = [{"id": i} for i in range(100)]
        page2 = [{"id": i} for i in range(100, 150)]
        page3 = []  # 第三页为空，结束
        responses = iter([
            {"issues": page1},
            {"issues": page2},
            {"issues": page3},
        ])
        with patch.object(client, "_request", side_effect=lambda *a, **kw: next(responses)):
            result = client._fetch_all_issues({"status_id": "*"})
            assert len(result) == 150

    def test_last_page_less_than_batch(self):
        """最后一页不足 batch_size"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        page1 = [{"id": i} for i in range(30)]
        with patch.object(client, "_request", return_value={"issues": page1}):
            result = client._fetch_all_issues({"status_id": "*"})
            assert len(result) == 30

    def test_empty_result(self):
        """无结果"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        with patch.object(client, "_request", return_value={"issues": []}):
            result = client._fetch_all_issues({"status_id": "*"})
            assert result == []


class TestCRUDMocked:
    """CRUD 方法（Mock _request）"""

    def _make_client_with_mocks(self):
        """创建已 mock 元数据的 client"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        client._project_id = 1
        client._tracker_id = 2
        client._custom_field_map = {
            "人员编号": 1, "姓名": 2, "性别": 3, "年龄": 4,
            "手机号": 5, "邮箱": 6, "部门": 7, "职位": 8, "入职时间": 9,
        }
        return client

    def test_create_employee_success(self):
        """创建成功"""
        from app.services.redmine_services import RedmineClient
        client = self._make_client_with_mocks()
        mock_issue = {
            "id": 123,
            "created_on": "2023-01-01T00:00:00Z",
            "updated_on": "2023-01-01T00:00:00Z",
            "custom_fields": [
                {"id": 1, "value": "001"},
                {"id": 2, "value": "张三"},
                {"id": 3, "value": "男"},
            ],
        }
        with patch.object(client, "_request", return_value={"issue": mock_issue}):
            result = client.create_employee({"number": "001", "name": "张三", "gender": "男"})
            assert result["id"] == 123
            assert result["number"] == "001"

    def test_create_employee_no_issue(self):
        """创建返回无 Issue"""
        from app.services.redmine_services import RedmineClient
        from app.core.exceptions import RedmineException
        client = self._make_client_with_mocks()
        with patch.object(client, "_request", return_value={}):
            with pytest.raises(RedmineException, match="创建员工失败"):
                client.create_employee({"number": "001", "name": "张三", "gender": "男"})

    def test_get_employee_success(self):
        """查询成功"""
        from app.services.redmine_services import RedmineClient
        client = self._make_client_with_mocks()
        mock_issue = {
            "id": 1,
            "created_on": "2023-01-01T00:00:00Z",
            "updated_on": "2023-01-01T00:00:00Z",
            "custom_fields": [
                {"id": 1, "value": "001"},
                {"id": 2, "value": "李四"},
            ],
        }
        with patch.object(client, "_request", return_value={"issue": mock_issue}):
            result = client.get_employee(1)
            assert result["id"] == 1
            assert result["name"] == "李四"

    def test_get_employee_not_found(self):
        """查询不存在的员工"""
        from app.services.redmine_services import RedmineClient
        from app.core.exceptions import NotFoundException
        client = RedmineClient()
        with patch.object(client, "_request", return_value={}):
            with pytest.raises(NotFoundException):
                client.get_employee(999999)

    def test_update_employee(self):
        """更新"""
        from app.services.redmine_services import RedmineClient
        client = self._make_client_with_mocks()
        updated_issue = {
            "id": 1,
            "created_on": "2023-01-01T00:00:00Z",
            "updated_on": "2023-06-01T00:00:00Z",
            "custom_fields": [
                {"id": 1, "value": "001"},
                {"id": 2, "value": "新名字"},
            ],
        }
        with patch.object(client, "_request") as mock_req:
            mock_req.side_effect = [
                {},  # PUT 请求（返回空）
                {"issue": updated_issue},  # GET 请求（返回更新后的 issue）
            ]
            result = client.update_employee(1, {"number": "001", "name": "新名字"})
            assert result["name"] == "新名字"

    def test_delete_employee(self):
        """删除"""
        from app.services.redmine_services import RedmineClient
        client = RedmineClient()
        with patch.object(client, "_request", return_value={}):
            result = client.delete_employee(1)
            assert result is None

    def test_list_employees_basic(self):
        """基本查询（Mock _fetch_all_issues）"""
        from app.services.redmine_services import RedmineClient
        client = self._make_client_with_mocks()
        issues = []
        for i in range(5):
            issues.append({
                "id": i + 1,
                "created_on": "2023-01-01T00:00:00Z",
                "updated_on": "2023-01-01T00:00:00Z",
                "custom_fields": [
                    {"id": 1, "value": f"00{i+1}"},
                    {"id": 2, "value": f"员工{i+1}"},
                    {"id": 3, "value": "男"},
                ],
            })
        with patch.object(client, "_fetch_all_issues", return_value=issues):
            employees, total = client.list_employees(offset=0, limit=2)
            assert total == 5
            assert len(employees) == 2
            assert employees[0]["name"] == "员工1"

    def test_list_employees_pagination(self):
        """分页验证"""
        from app.services.redmine_services import RedmineClient
        client = self._make_client_with_mocks()
        issues = []
        for i in range(5):
            issues.append({
                "id": i + 1,
                "created_on": "2023-01-01T00:00:00Z",
                "updated_on": "2023-01-01T00:00:00Z",
                "custom_fields": [
                    {"id": 1, "value": f"00{i+1}"},
                    {"id": 2, "value": f"员工{i+1}"},
                ],
            })
        with patch.object(client, "_fetch_all_issues", return_value=issues):
            employees, total = client.list_employees(offset=2, limit=2)
            assert total == 5
            assert len(employees) == 2
            assert employees[0]["id"] == 3  # offset=2 跳过前两条
