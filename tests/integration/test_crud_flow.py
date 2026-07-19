"""
集成测试：人员 CRUD 完整链路（需要 Redmine）
"""
import time

import pytest


@pytest.mark.integration
class TestCRUDFlow:
    """CRUD 完整流程"""

    def test_full_lifecycle(self, client, admin_headers, cleanup_ids):
        """新增 → 查询 → 修改 → 删除 完整流程"""
        ts = int(time.time())

        # 1. 新增
        resp = client.post("/api/v1/employees", json={
            "number": f"INT_TEST_{ts}",
            "name": "集成测试员工",
            "gender": "女",
            "age": 28,
            "phone": "13800000099",
            "email": "int_test@example.com",
            "department": "集成测试部",
            "position": "测试专员",
            "jointime": "2023-06-01",
        }, headers=admin_headers)

        assert resp.status_code == 200
        eid = resp.json()["data"]["id"]
        cleanup_ids.append(eid)

        # 2. 查详情
        resp = client.get(f"/api/v1/employees/{eid}", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["number"] == f"INT_TEST_{ts}"

        # 3. 修改
        resp = client.put(f"/api/v1/employees/{eid}", json={
            "name": "已修改姓名",
            "department": "产品部",
        }, headers=admin_headers)

        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "已修改姓名"
        assert resp.json()["data"]["department"] == "产品部"
        # 未修改的字段保持不变
        assert resp.json()["data"]["age"] == 28

        # 4. 删除
        resp = client.delete(f"/api/v1/employees/{eid}", headers=admin_headers)
        assert resp.status_code == 200

        # 5. 确认已删除
        resp = client.get(f"/api/v1/employees/{eid}", headers=admin_headers)
        assert resp.status_code == 404

    def test_data_persistence(self, client, admin_headers, cleanup_ids):
        """数据持久化：新建后可通过列表查询到"""
        ts = int(time.time())

        # 创建
        resp = client.post("/api/v1/employees", json={
            "number": f"INT_PERSIST_{ts}",
            "name": "持久化测试",
            "gender": "男",
        }, headers=admin_headers)

        assert resp.status_code == 200
        eid = resp.json()["data"]["id"]
        cleanup_ids.append(eid)

        # 通过列表查询确认存在
        resp = client.get(f"/api/v1/employees?limit=100", headers=admin_headers)
        assert resp.status_code == 200
        numbers = [e["number"] for e in resp.json()["data"]["items"]]
        assert f"INT_PERSIST_{ts}" in numbers

    def test_duplicate_prevention(self, client, admin_headers, cleanup_ids):
        """重复人员编号被拒绝"""
        ts = int(time.time())

        # 创建第一个
        resp = client.post("/api/v1/employees", json={
            "number": f"INT_DUP_{ts}",
            "name": "重复测试",
            "gender": "男",
        }, headers=admin_headers)

        assert resp.status_code == 200
        eid = resp.json()["data"]["id"]
        cleanup_ids.append(eid)

        # 尝试创建重复编号
        resp = client.post("/api/v1/employees", json={
            "number": f"INT_DUP_{ts}",
            "name": "重复测试2",
            "gender": "女",
        }, headers=admin_headers)

        assert resp.status_code == 422
