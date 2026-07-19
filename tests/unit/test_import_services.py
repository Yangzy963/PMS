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
