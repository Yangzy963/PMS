"""
API 测试：人员管理 CRUD 与搜索
"""
import pytest


def _has_redmine(client, login_headers):
    """检查 Redmine 是否可用"""
    resp = client.get("/api/v1/employees?limit=1", headers=login_headers)
    return resp.status_code != 500


class TestCreateEmployee:
    """新增人员"""

    def test_create_success(self, client, login_headers):
        """新增成功"""
        resp = client.post("/api/v1/employees", json={
            "number": "TEST_NEW_001",
            "name": "新建测试",
            "gender": "女",
            "age": 25,
            "phone": "13800000002",
            "email": "new@example.com",
            "department": "研发部",
            "position": "前端工程师",
            "jointime": "2024-01-01",
        }, headers=login_headers)

        if resp.status_code >= 500:
            pytest.skip("Redmine 服务不可用")

        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert body["data"]["number"] == "TEST_NEW_001"
        assert body["data"]["name"] == "新建测试"

        # 清理
        eid = body["data"]["id"]
        client.delete(f"/api/v1/employees/{eid}", headers=login_headers)

    def test_create_duplicate_number(self, client, login_headers, test_employee):
        """重复人员编号"""
        resp = client.post("/api/v1/employees", json={
            "number": "TEST_API_001",
            "name": "重复测试",
            "gender": "男",
        }, headers=login_headers)

        assert resp.status_code == 422
        assert resp.json()["code"] == 422

    def test_create_missing_required(self, client, login_headers):
        """缺少必填字段"""
        resp = client.post("/api/v1/employees", json={
            "name": "无编号",
        }, headers=login_headers)
        # Pydantic 校验返回 422
        assert resp.status_code == 422

    def test_create_invalid_age(self, client, login_headers):
        """年龄超出范围"""
        resp = client.post("/api/v1/employees", json={
            "number": "TEST_AGE_001",
            "name": "年龄测试",
            "gender": "男",
            "age": 200,
        }, headers=login_headers)
        assert resp.status_code == 422

    def test_create_without_token(self, client):
        """无 Token 新增"""
        resp = client.post("/api/v1/employees", json={
            "number": "TEST_001", "name": "test",
        })
        assert resp.status_code == 401


class TestGetEmployee:
    """查询人员"""

    def test_list_with_data(self, client, login_headers, test_employee):
        """查询列表（有数据）"""
        resp = client.get("/api/v1/employees", headers=login_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert "items" in body["data"]
        assert body["data"]["total"] > 0

    def test_list_pagination(self, client, login_headers):
        """分页查询"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.get("/api/v1/employees?offset=0&limit=5", headers=login_headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]["items"]) <= 5

    def test_get_detail(self, client, login_headers, test_employee):
        """查看详情"""
        resp = client.get(f"/api/v1/employees/{test_employee}", headers=login_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["id"] == test_employee

    def test_get_not_found(self, client, login_headers):
        """查看不存在的人员"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.get("/api/v1/employees/999999", headers=login_headers)
        assert resp.status_code == 404

    def test_get_without_token(self, client):
        """无 Token 查询"""
        resp = client.get("/api/v1/employees")
        assert resp.status_code == 401


class TestUpdateEmployee:
    """修改人员"""

    def test_update_success(self, client, login_headers, test_employee):
        """修改成功"""
        resp = client.put(f"/api/v1/employees/{test_employee}", json={
            "name": "已修改姓名",
            "department": "产品部",
        }, headers=login_headers)

        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["name"] == "已修改姓名"
        assert body["data"]["department"] == "产品部"

    def test_update_not_found(self, client, login_headers):
        """修改不存在的人员"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.put("/api/v1/employees/999999", json={
            "name": "不存在",
        }, headers=login_headers)
        assert resp.status_code == 404


class TestDeleteEmployee:
    """删除人员"""

    def test_delete_success(self, client, login_headers):
        """删除成功"""
        # 先创建一个
        create_resp = client.post("/api/v1/employees", json={
            "number": "TEST_DEL_001",
            "name": "待删除",
            "gender": "男",
        }, headers=login_headers)

        if create_resp.status_code >= 500:
            pytest.skip("Redmine 服务不可用")

        eid = create_resp.json()["data"]["id"]

        # 删除
        resp = client.delete(f"/api/v1/employees/{eid}", headers=login_headers)
        assert resp.status_code == 200

        # 确认已删除
        get_resp = client.get(f"/api/v1/employees/{eid}", headers=login_headers)
        assert get_resp.status_code == 404

    def test_delete_not_found(self, client, login_headers):
        """删除不存在的人员"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.delete("/api/v1/employees/999999", headers=login_headers)
        assert resp.status_code == 404


class TestSearch:
    """搜索功能"""

    def test_search_by_name(self, client, login_headers):
        """姓名模糊搜索"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.get("/api/v1/employees?name=API测试", headers=login_headers)
        assert resp.status_code == 200

    def test_search_by_department(self, client, login_headers):
        """部门精确搜索"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.get("/api/v1/employees?department=测试部", headers=login_headers)
        assert resp.status_code == 200

    def test_search_by_position(self, client, login_headers):
        """职位精确搜索"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.get("/api/v1/employees?position=测试工程师", headers=login_headers)
        assert resp.status_code == 200

    def test_search_date_range(self, client, login_headers):
        """入职时间范围查询"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.get(
            "/api/v1/employees?jointime_start=2023-01-01&jointime_end=2024-12-31",
            headers=login_headers,
        )
        assert resp.status_code == 200

    def test_search_sort(self, client, login_headers):
        """排序查询"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.get("/api/v1/employees?sort=age:asc", headers=login_headers)
        assert resp.status_code == 200

    def test_search_no_result(self, client, login_headers):
        """无匹配结果"""
        if not _has_redmine(client, login_headers):
            pytest.skip("Redmine 服务不可用")
        resp = client.get("/api/v1/employees?name=不存在的名字xyz", headers=login_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 0
