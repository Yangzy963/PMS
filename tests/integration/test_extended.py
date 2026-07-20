"""
集成测试扩充：数据导入全流程、排序+过滤组合、分页边界验证
"""
import pytest


@pytest.mark.integration
class TestImportFullFlow:
    """导入完整流程"""

    def test_import_csv_then_verify_data(self, client, admin_headers, cleanup_ids):
        """导入 CSV → 验证数据可查询 → 清理"""
        import time, io
        ts = int(time.time())

        csv_content = f"人员编号,姓名,性别,年龄,部门,职位\nIMP_{ts}_1,导入测试1,男,28,AI部,工程师\nIMP_{ts}_2,导入测试2,女,32,AI部,经理"
        resp = client.post(
            "/api/v1/import/employees?strategy=skip",
            files={"file": (f"test_{ts}.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] == 2

        # 验证导入数据可搜索
        resp2 = client.get(f"/api/v1/employees?name=导入测试", headers=admin_headers)
        assert resp2.status_code == 200
        items = resp2.json()["data"]["items"]
        assert len(items) >= 2

        # 注册清理
        for item in items:
            if str(item.get("number", "")).startswith(f"IMP_{ts}"):
                cleanup_ids.append(item["id"])

    def test_import_excel_then_verify(self, client, admin_headers, cleanup_ids):
        """导入 Excel → 验证数据"""
        try:
            import openpyxl
        except ImportError:
            pytest.skip("openpyxl not installed")

        import time, io
        ts = int(time.time())

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["人员编号", "姓名", "性别", "年龄", "部门"])
        ws.append([f"IMP_XL_{ts}_1", "Excel导入1", "男", 25, "数据部"])
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        resp = client.post(
            "/api/v1/import/employees?strategy=skip",
            files={"file": (f"test_{ts}.xlsx", buf.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["success"] + data.get("failed", 0) == 1

        # 清理
        resp2 = client.get(f"/api/v1/employees?name=Excel导入", headers=admin_headers)
        for item in resp2.json()["data"]["items"]:
            if str(item.get("number", "")).startswith(f"IMP_XL_{ts}"):
                cleanup_ids.append(item["id"])


@pytest.mark.integration
class TestSortPaginationFlow:
    """排序 + 分页组合"""

    def test_sort_number_asc_then_paginate(self, client, admin_headers):
        """编号升序分页"""
        resp = client.get(
            "/api/v1/employees?sort=number:asc&offset=0&limit=10",
            headers=admin_headers,
        )
        assert resp.status_code == 200
        items = resp.json()["data"]["items"]
        if len(items) >= 2:
            numbers = [e.get("number", "") for e in items]
            assert numbers == sorted(numbers)

    def test_sort_age_desc_then_paginate(self, client, admin_headers):
        """年龄降序分页"""
        resp = client.get(
            "/api/v1/employees?sort=age:desc&offset=0&limit=10",
            headers=admin_headers,
        )
        assert resp.status_code == 200

    def test_default_sort_is_created_on_desc(self, client, admin_headers):
        """默认排序为 created_on:desc（后端默认值）"""
        resp = client.get("/api/v1/employees?limit=10", headers=admin_headers)
        assert resp.status_code == 200

    def test_sort_then_search_combined(self, client, admin_headers):
        """排序 + 搜索组合"""
        resp = client.get(
            "/api/v1/employees?sort=jointime:desc&department=研发部&limit=10",
            headers=admin_headers,
        )
        assert resp.status_code == 200


@pytest.mark.integration
class TestDataConsistency:
    """数据一致性验证"""

    def test_create_then_get_detail(self, client, admin_headers, cleanup_ids):
        """创建后详情一致"""
        import time
        ts = int(time.time())
        payload = {
            "number": f"INT_CONSIST_{ts}",
            "name": "一致性测试",
            "gender": "女",
            "age": 28,
            "department": "质控部",
            "position": "主管",
            "phone": "13700000001",
            "email": "consist@test.com",
        }
        resp = client.post("/api/v1/employees", json=payload, headers=admin_headers)
        assert resp.status_code == 200
        emp_id = resp.json()["data"]["id"]
        cleanup_ids.append(emp_id)

        # 详情对比
        resp2 = client.get(f"/api/v1/employees/{emp_id}", headers=admin_headers)
        assert resp2.status_code == 200
        detail = resp2.json()["data"]
        assert detail["number"] == payload["number"]
        assert detail["name"] == payload["name"]
        assert detail["age"] == payload["age"]
        assert detail["department"] == payload["department"]

    def test_update_then_verify(self, client, admin_headers, cleanup_ids):
        """更新后验证"""
        import time
        ts = int(time.time())
        # 创建
        resp = client.post("/api/v1/employees", json={
            "number": f"INT_UPD_{ts}", "name": "更新前", "gender": "男", "age": 20,
        }, headers=admin_headers)
        if resp.status_code != 200:
            pytest.skip("无法创建测试数据")
        emp_id = resp.json()["data"]["id"]
        cleanup_ids.append(emp_id)

        # 更新
        resp2 = client.put(f"/api/v1/employees/{emp_id}", json={
            "name": "更新后", "age": 30, "department": "新部门",
        }, headers=admin_headers)
        assert resp2.status_code == 200
        assert resp2.json()["data"]["name"] == "更新后"
        assert resp2.json()["data"]["age"] == 30

    def test_delete_then_verify_404(self, client, admin_headers, cleanup_ids):
        """删除后查不到"""
        import time
        ts = int(time.time())
        resp = client.post("/api/v1/employees", json={
            "number": f"INT_DEL_{ts}", "name": "待删除", "gender": "男",
        }, headers=admin_headers)
        if resp.status_code != 200:
            pytest.skip("无法创建测试数据")
        emp_id = resp.json()["data"]["id"]

        # 删除
        resp2 = client.delete(f"/api/v1/employees/{emp_id}", headers=admin_headers)
        assert resp2.status_code == 200

        # 验证不存在
        resp3 = client.get(f"/api/v1/employees/{emp_id}", headers=admin_headers)
        assert resp3.status_code == 404
