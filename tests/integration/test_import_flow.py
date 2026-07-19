"""
集成测试：导入完整流程（需要 Redmine）
"""
import io
import time

import pytest


@pytest.mark.integration
class TestImportFlow:
    """数据导入完整流程"""

    def test_import_then_query(self, client, admin_headers, cleanup_ids):
        """CSV 导入 → 查询确认 → 清理"""
        ts = int(time.time())
        content = "人员编号,姓名,性别,年龄,部门,职位,入职时间\n"
        content += f"INT_IMP_A_{ts},导入员工A,男,30,研发部,工程师,2023-01-01\n"
        content += f"INT_IMP_B_{ts},导入员工B,女,25,测试部,测试,2023-02-01\n"

        # 1. 导入
        resp = client.post(
            "/api/v1/import/employees?strategy=skip",
            files={"file": (f"import_{ts}.csv", content.encode("utf-8"), "text/csv")},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] == 2
        assert data["failed"] == 0

        # 2. 查询确认存在
        resp = client.get("/api/v1/employees?limit=100", headers=admin_headers)
        items = resp.json()["data"]["items"]
        imported = [e for e in items if e["number"].startswith(f"INT_IMP_") and str(ts) in e["number"]]
        assert len(imported) >= 2

        # 3. 注册到清理列表
        for e in imported:
            if e["id"] not in cleanup_ids:
                cleanup_ids.append(e["id"])

    def test_import_duplicate_skip(self, client, admin_headers, cleanup_ids):
        """重复数据跳过策略"""
        ts = int(time.time())
        content = "人员编号,姓名,性别\n"
        content += f"INT_SKIP_{ts},跳过测试,男\n"

        # 创建已有编号
        resp = client.post("/api/v1/employees", json={
            "number": f"INT_SKIP_{ts}",
            "name": "已存在",
            "gender": "男",
        }, headers=admin_headers)
        eid = resp.json()["data"]["id"]
        cleanup_ids.append(eid)

        # 导入同编号（skip 策略）
        resp = client.post(
            "/api/v1/import/employees?strategy=skip",
            files={"file": (f"skip_{ts}.csv", content.encode("utf-8"), "text/csv")},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["skipped"] >= 1

    def test_import_overwrite(self, client, admin_headers, cleanup_ids):
        """覆盖策略"""
        ts = int(time.time())
        content = "人员编号,姓名,性别,部门\n"
        content += f"INT_OVER_{ts},覆盖后姓名,女,新部门\n"

        # 创建
        resp = client.post("/api/v1/employees", json={
            "number": f"INT_OVER_{ts}",
            "name": "覆盖前姓名",
            "gender": "男",
        }, headers=admin_headers)
        eid = resp.json()["data"]["id"]
        cleanup_ids.append(eid)

        # 导入覆盖
        resp = client.post(
            "/api/v1/import/employees?strategy=overwrite",
            files={"file": (f"over_{ts}.csv", content.encode("utf-8"), "text/csv")},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["overwritten"] >= 1

        # 验证已覆盖
        resp = client.get(f"/api/v1/employees/{eid}", headers=admin_headers)
        assert resp.json()["data"]["name"] == "覆盖后姓名"
        assert resp.json()["data"]["department"] == "新部门"
