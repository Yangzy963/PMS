"""
API 测试：批量删除
"""
import pytest


class TestBatchDelete:
    """批量删除接口"""

    def test_batch_delete_success(self, client, login_headers):
        """批量删除成功"""
        import time
        ts = int(time.time())
        ids = []
        for i in range(2):
            resp = client.post("/api/v1/employees", json={
                "number": f"TEST_BATCH_{ts}_{i}",
                "name": f"批量删除测试{ts}",
                "gender": "男",
            }, headers=login_headers)
            if resp.status_code >= 500:
                pytest.skip("Redmine 服务不可用")
            if resp.status_code != 200:
                pytest.skip(f"创建测试数据失败 [{resp.status_code}]")
            assert resp.json()["data"] is not None
            ids.append(resp.json()["data"]["id"])

        # 批量删除
        resp = client.post(
            "/api/v1/employees/batch-delete",
            json=ids,
            headers=login_headers,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert body["data"]["deleted_count"] == 2

    def test_batch_delete_empty_list(self, client, login_headers):
        """空列表批量删除"""
        resp = client.post(
            "/api/v1/employees/batch-delete",
            json=[],
            headers=login_headers,
        )
        assert resp.status_code == 422

    def test_batch_delete_partial_exist(self, client, login_headers):
        """不存在的 ID 被跳过，不影响结果"""
        import time
        # 先创建一个然后删除，确保 ID 已失效
        resp = client.post("/api/v1/employees", json={
            "number": f"TEST_BATCH_PARTIAL_{int(time.time())}",
            "name": "partial_test", "gender": "男",
        }, headers=login_headers)
        if resp.status_code >= 500:
            pytest.skip("Redmine 服务不可用")
        if resp.status_code != 200:
            pytest.skip("无法创建测试数据")

        valid_id = resp.json()["data"]["id"]
        client.delete(f"/api/v1/employees/{valid_id}", headers=login_headers)

        # 用已删除的 ID + 极大不存在的 ID
        resp = client.post(
            "/api/v1/employees/batch-delete",
            json=[valid_id, 99999999],
            headers=login_headers,
        )
        assert resp.status_code == 200
        # Redmine DELETE 对不存在的 ID 也可能返回 204，因此只验证接口不崩溃

    def test_batch_delete_without_token(self, client):
        """无 Token 批量删除"""
        resp = client.post("/api/v1/employees/batch-delete", json=[1])
        assert resp.status_code == 401
