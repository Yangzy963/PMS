"""
单元测试：导入数据校验与处理逻辑（Mock Redmine）
"""
import pytest
from unittest.mock import Mock, patch


class TestValidateEmployeeRow:
    """单行数据校验"""

    def test_valid_row(self):
        """正常行"""
        from app.services.import_services import validate_employee_row
        data, errors = validate_employee_row({
            "人员编号": "001",
            "姓名": "张三",
            "性别": "男",
            "年龄": "30",
            "手机号": "13800000000",
            "邮箱": "a@b.com",
            "部门": "研发部",
            "职位": "工程师",
            "入职时间": "2023-01-01",
        }, 1)
        assert errors == []
        assert data["number"] == "001"
        assert data["age"] == 30

    def test_missing_number(self):
        """缺少人员编号"""
        from app.services.import_services import validate_employee_row
        _, errors = validate_employee_row({
            "人员编号": "", "姓名": "张三", "性别": "男",
        }, 1)
        assert any("人员编号" in e for e in errors)

    def test_missing_name(self):
        """缺少姓名"""
        from app.services.import_services import validate_employee_row
        _, errors = validate_employee_row({
            "人员编号": "001", "姓名": "", "性别": "男",
        }, 1)
        assert any("姓名" in e for e in errors)

    def test_invalid_age(self):
        """年龄不是整数"""
        from app.services.import_services import validate_employee_row
        _, errors = validate_employee_row({
            "人员编号": "001", "姓名": "张三", "性别": "男",
            "年龄": "abc",
        }, 1)
        assert any("年龄" in e for e in errors)

    def test_age_out_of_range(self):
        """年龄超出范围"""
        from app.services.import_services import validate_employee_row
        _, errors = validate_employee_row({
            "人员编号": "001", "姓名": "张三", "性别": "男",
            "年龄": "200",
        }, 1)
        assert any("150" in e for e in errors)

    def test_strips_whitespace(self):
        """去除首尾空格"""
        from app.services.import_services import validate_employee_row
        data, _ = validate_employee_row({
            "人员编号": "  001  ",
            "姓名": " 张三 ",
            "性别": "男",
        }, 1)
        assert data["number"] == "001"
        assert data["name"] == "张三"


class TestDateNormalization:
    """日期标准化"""

    @pytest.mark.parametrize("raw,expected", [
        ("2023-01-01", "2023-01-01"),
        ("2023/1/1", "2023-01-01"),
        ("2023.01.01", "2023-01-01"),
        ("2023年1月1日", "2023-01-01"),
        ("20230101", "2023-01-01"),
        ("1/5/2023", "2023-01-05"),
        ("", None),
        (None, None),
    ])
    def test_formats(self, raw, expected):
        from app.services.import_services import normalize_date
        result, error = normalize_date(raw)
        assert error is None
        assert result == expected

    def test_invalid_date(self):
        """无法识别的日期"""
        from app.services.import_services import normalize_date
        result, error = normalize_date("not a date")
        assert result is None
        assert error is not None

    def test_pandas_timestamp(self):
        """pandas Timestamp 类型"""
        try:
            import pandas as pd
            ts = pd.Timestamp("2023-06-15")
            from app.services.import_services import normalize_date
            result, error = normalize_date(ts)
            assert error is None
            assert result == "2023-06-15"
        except ImportError:
            import pytest
            pytest.skip("pandas not installed")

    def test_datetime_object(self):
        """datetime 对象"""
        from datetime import datetime
        dt = datetime(2023, 12, 25, 10, 30, 0)
        from app.services.import_services import normalize_date
        result, error = normalize_date(dt)
        assert error is None
        assert result == "2023-12-25"

    def test_nan_string(self):
        """"nan" 字符串返回 None"""
        from app.services.import_services import normalize_date
        result, error = normalize_date("nan")
        assert error is None
        assert result is None

    def test_whitespace_only(self):
        """纯空格"""
        from app.services.import_services import normalize_date
        result, error = normalize_date("   ")
        assert error is None
        assert result is None

    def test_dmy_format(self):
        """dd/mm/YYYY 格式（用 31 日确保不被 m/d/Y 先匹配）"""
        from app.services.import_services import normalize_date
        result, error = normalize_date("31/01/2023")
        assert error is None
        assert result == "2023-01-31"


class TestImportEmployees:
    """批量导入流程"""

    def _valid_rows(self):
        return [
            {"人员编号": "001", "姓名": "张三", "性别": "男", "年龄": 30,
             "手机号": "138", "邮箱": "a@b.com", "部门": "研发部",
             "职位": "工程师", "入职时间": "2023-01-01"},
            {"人员编号": "002", "姓名": "李四", "性别": "女", "年龄": 25,
             "手机号": "139", "邮箱": "c@d.com", "部门": "测试部",
             "职位": "经理", "入职时间": "2024-06-15"},
        ]

    def test_import_all_new_success(self):
        """全部新增成功"""
        from app.services.import_services import import_employees
        with patch("app.services.import_services.redmine_client.find_by_number",
                   return_value=None), \
             patch("app.services.import_services.redmine_client.create_employee",
                   return_value={"id": 1}):
            result = import_employees(self._valid_rows(), strategy="skip")
            assert result["total"] == 2
            assert result["success"] == 2
            assert result["failed"] == 0

    def test_import_skip_duplicate(self):
        """跳过重复"""
        from app.services.import_services import import_employees
        with patch("app.services.import_services.redmine_client.find_by_number",
                   side_effect=[{"id": 1, "number": "001"}, None]), \
             patch("app.services.import_services.redmine_client.create_employee",
                   return_value={"id": 2}):
            result = import_employees(self._valid_rows(), strategy="skip")
            assert result["total"] == 2
            assert result["success"] == 1
            assert result["skipped"] == 1

    def test_import_overwrite_existing(self):
        """覆盖已有"""
        from app.services.import_services import import_employees
        with patch("app.services.import_services.redmine_client.find_by_number",
                   return_value={"id": 1, "number": "001"}), \
             patch("app.services.import_services.redmine_client.update_employee",
                   return_value={"id": 1}):
            result = import_employees(self._valid_rows()[:1], strategy="overwrite")
            assert result["total"] == 1
            assert result["overwritten"] == 1

    def test_import_abort_on_duplicate(self):
        """重复时终止"""
        from app.services.import_services import import_employees
        with patch("app.services.import_services.redmine_client.find_by_number",
                   side_effect=[{"id": 1, "number": "001"}, None]):
            result = import_employees(self._valid_rows(), strategy="abort")
            assert result["total"] == 2
            assert result["failed"] == 1  # 第一行重复导致失败
            # 第二行不会被处理（abort 在第一个重复时 break）

    def test_import_invalid_strategy(self):
        """非法策略"""
        from app.services.import_services import import_employees
        from app.core.exceptions import ValidationException
        with pytest.raises(ValidationException):
            import_employees(self._valid_rows(), strategy="invalid")

    def test_import_validation_error(self):
        """行校验失败"""
        from app.services.import_services import import_employees
        rows = [{"人员编号": "", "姓名": "", "性别": "男"}]
        result = import_employees(rows, strategy="skip")
        assert result["total"] == 1
        assert result["failed"] == 1
        assert len(result["errors"]) == 1

    def test_import_create_exception(self):
        """创建时 Redmine 异常"""
        from app.services.import_services import import_employees
        with patch("app.services.import_services.redmine_client.find_by_number",
                   return_value=None), \
             patch("app.services.import_services.redmine_client.create_employee",
                   side_effect=Exception("网络错误")):
            result = import_employees(self._valid_rows()[:1], strategy="skip")
            assert result["total"] == 1
            assert result["failed"] == 1
