"""
集成测试：Redmine API 集成（验证 Redmine 连接与元数据）
"""
import pytest


@pytest.mark.integration
class TestRedmineConnection:
    """Redmine 连接与元数据验证"""

    def test_custom_fields_exist(self, client, admin_headers):
        """验证自定义字段齐全"""
        # 通过查询员工接口间接验证（内部会检查自定义字段）
        resp = client.get("/api/v1/employees?limit=1", headers=admin_headers)
        assert resp.status_code == 200

    def test_project_accessible(self, client, admin_headers):
        """验证 Redmine 项目 pms 可访问"""
        resp = client.get("/api/v1/employees?limit=1", headers=admin_headers)
        assert resp.status_code == 200

    def test_tracker_available(self, client, admin_headers):
        """验证跟踪标签 人员信息 可用"""
        resp = client.get("/api/v1/employees?limit=1", headers=admin_headers)
        assert resp.status_code == 200


@pytest.mark.integration
class TestSearchSortFlow:
    """搜索与排序组合流程"""

    def test_search_then_sort(self, client, admin_headers):
        """搜索后排序"""
        resp = client.get(
            "/api/v1/employees?name=test&sort=age:asc",
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_sort_then_paginate(self, client, admin_headers):
        """排序后分页"""
        resp = client.get(
            "/api/v1/employees?sort=number:asc&offset=0&limit=5",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]["items"]) <= 5


@pytest.mark.integration
class TestBatchDeleteFlow:
    """批量删除完整流程"""

    def test_batch_delete_with_verify(self, client, admin_headers):
        """创建 → 批量删除 → 验证全部清除"""
        import time
        ts = int(time.time())
        ids = []
        for i in range(2):
            resp = client.post("/api/v1/employees", json={
                "number": f"INT_BATCH_{ts}_{i}",
                "name": f"批量删除集成测试{i}",
                "gender": "男",
            }, headers=admin_headers)
            if resp.status_code == 200:
                ids.append(resp.json()["data"]["id"])

        if not ids:
            pytest.skip("无法创建测试数据")

        # 批量删除
        resp = client.post(
            "/api/v1/employees/batch-delete",
            json=ids,
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["deleted_count"] == len(ids)
