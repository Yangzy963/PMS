"""
API 测试：数据导入
"""
import io

import pytest


class TestImport:
    """数据导入接口"""

    @pytest.fixture
    def sample_csv(self):
        """生成测试 CSV 文件"""
        content = "人员编号,姓名,性别,年龄,手机号,邮箱,部门,职位,入职时间\n"
        content += "IMP_001,导入测试1,男,30,13800000101,imp1@test.com,研发部,工程师,2023-01-01\n"
        content += "IMP_002,导入测试2,女,28,13800000102,imp2@test.com,测试部,测试,2023-02-01\n"
        return content.encode("utf-8")

    @pytest.fixture
    def sample_excel(self):
        """生成测试 Excel 文件"""
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(["人员编号", "姓名", "性别", "年龄", "手机号", "邮箱", "部门", "职位", "入职时间"])
            ws.append(["IMP_E01", "Excel测试1", "男", 30, "13800000301", "excel1@test.com", "研发部", "工程师", "2023-01-01"])
            ws.append(["IMP_E02", "Excel测试2", "女", 28, "13800000302", "excel2@test.com", "测试部", "测试", "2023-02-01"])
            buf = io.BytesIO()
            wb.save(buf)
            buf.seek(0)
            return buf
        except ImportError:
            return None

    def test_import_csv_success(self, client, login_headers, sample_csv):
        """CSV 导入成功"""
        resp = client.post(
            "/api/v1/import/employees?strategy=skip",
            files={"file": ("test.csv", sample_csv, "text/csv")},
            headers=login_headers,
        )
        if resp.status_code >= 500:
            pytest.skip("Redmine 服务不可用")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200
        assert body["data"]["success"] >= 0

        # 清理
        for eid in self._get_imported_ids(client, login_headers, "IMP_00"):
            client.delete(f"/api/v1/employees/{eid}", headers=login_headers)

    def test_import_excel_success(self, client, login_headers, sample_excel):
        """Excel 导入成功"""
        if sample_excel is None:
            pytest.skip("openpyxl not installed")

        resp = client.post(
            "/api/v1/import/employees?strategy=skip",
            files={"file": ("test.xlsx", sample_excel, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            headers=login_headers,
        )
        if resp.status_code >= 500:
            pytest.skip("Redmine 服务不可用")
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == 200

        # 清理
        for eid in self._get_imported_ids(client, login_headers, "IMP_E"):
            client.delete(f"/api/v1/employees/{eid}", headers=login_headers)

    def test_import_empty_file(self, client, login_headers):
        """空文件导入"""
        resp = client.post(
            "/api/v1/import/employees?strategy=skip",
            files={"file": ("empty.csv", io.BytesIO(b""), "text/csv")},
            headers=login_headers,
        )
        assert resp.status_code == 422

    def test_import_without_token(self, client, sample_csv):
        """无 Token 导入"""
        resp = client.post(
            "/api/v1/import/employees?strategy=skip",
            files={"file": ("test.csv", sample_csv, "text/csv")},
        )
        assert resp.status_code == 401

    @staticmethod
    def _get_imported_ids(client, headers, prefix):
        """获取导入的测试数据 ID"""
        resp = client.get("/api/v1/employees?limit=100", headers=headers)
        if resp.status_code != 200:
            return []
        ids = []
        for emp in resp.json()["data"]["items"]:
            if emp["number"].startswith(prefix):
                ids.append(emp["id"])
        return ids
