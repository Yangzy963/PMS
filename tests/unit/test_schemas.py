"""
单元测试：Pydantic 数据模型校验
"""
import pytest
from pydantic import ValidationError


class TestEmployeeBase:
    """EmployeeBase 模型"""

    def test_valid_minimal(self):
        """最少必填字段"""
        from app.schemas.employee import EmployeeBase
        emp = EmployeeBase(number="001", name="张三", gender="男")
        assert emp.number == "001"
        assert emp.name == "张三"
        assert emp.gender == "男"
        assert emp.age is None
        assert emp.email is None

    def test_valid_full(self):
        """全部字段"""
        from app.schemas.employee import EmployeeBase
        emp = EmployeeBase(
            number="001", name="张三", gender="男", age=30,
            phone="13800000000", email="a@b.com",
            department="研发部", position="工程师", jointime="2023-01-01",
        )
        assert emp.age == 30
        assert emp.email == "a@b.com"

    def test_missing_required_number(self):
        """缺少必填字段 number"""
        from app.schemas.employee import EmployeeBase
        with pytest.raises(ValidationError):
            EmployeeBase(name="张三", gender="男")

    def test_missing_required_name(self):
        """缺少必填字段 name"""
        from app.schemas.employee import EmployeeBase
        with pytest.raises(ValidationError):
            EmployeeBase(number="001", gender="男")

    def test_age_out_of_range(self):
        """年龄超出 0-150"""
        from app.schemas.employee import EmployeeBase
        with pytest.raises(ValidationError):
            EmployeeBase(number="001", name="张三", gender="男", age=200)

    def test_age_negative(self):
        """负年龄"""
        from app.schemas.employee import EmployeeBase
        with pytest.raises(ValidationError):
            EmployeeBase(number="001", name="张三", gender="男", age=-1)

    def test_age_zero_is_valid(self):
        """年龄为 0 合法"""
        from app.schemas.employee import EmployeeBase
        emp = EmployeeBase(number="001", name="张三", gender="男", age=0)
        assert emp.age == 0


class TestEmployeeUpdate:
    """EmployeeUpdate 模型"""

    def test_all_fields_optional(self):
        """所有字段可选"""
        from app.schemas.employee import EmployeeUpdate
        emp = EmployeeUpdate()
        assert emp.number is None
        assert emp.name is None

    def test_partial_update(self):
        """只更新部分字段"""
        from app.schemas.employee import EmployeeUpdate
        emp = EmployeeUpdate(name="新名字", department="新部门")
        assert emp.name == "新名字"
        assert emp.department == "新部门"
        assert emp.number is None


class TestEmployeeResponse:
    """EmployeeResponse 模型"""

    def test_valid_response(self):
        """完整响应"""
        from app.schemas.employee import EmployeeResponse
        emp = EmployeeResponse(
            id=1, number="001", name="张三", gender="男",
            createtime="2023-01-01", updatetime="2023-01-02",
        )
        assert emp.id == 1

    def test_missing_id(self):
        """缺少 id"""
        from app.schemas.employee import EmployeeResponse
        with pytest.raises(ValidationError):
            EmployeeResponse(number="001", name="张三", gender="男")


class TestEmployeeListResponse:
    """EmployeeListResponse 模型"""

    def test_valid(self):
        """正常列表响应"""
        from app.schemas.employee import EmployeeListResponse
        resp = EmployeeListResponse(total=2, items=[], offset=0, limit=20)
        assert resp.total == 2
        assert resp.items == []


class TestUserSchemas:
    """用户相关模型"""

    def test_login_request(self):
        """登录请求"""
        from app.schemas.user import UserLogin
        u = UserLogin(username="admin", password="123")
        assert u.username == "admin"

    def test_login_missing_username(self):
        """缺少用户名"""
        from app.schemas.user import UserLogin
        with pytest.raises(ValidationError):
            UserLogin(password="123")

    def test_token_response(self):
        """Token 响应"""
        from app.schemas.user import TokenResponse
        t = TokenResponse(access_token="eyJ...")
        assert t.token_type == "bearer"
