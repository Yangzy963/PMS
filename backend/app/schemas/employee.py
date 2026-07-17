from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EmployeeBase(BaseModel):
    """员工基础模型"""
    number: str = Field(..., min_length=1, max_length=50, description="人员编号")
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    gender: str = Field(..., description="性别")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    department: Optional[str] = Field(None, max_length=50, description="部门")
    position: Optional[str] = Field(None, max_length=50, description="职位")
    jointime: Optional[str] = Field(None, description="入职时间，格式 YYYY-MM-DD")


class EmployeeCreate(EmployeeBase):
    """创建员工请求模型"""
    pass


class EmployeeUpdate(BaseModel):
    """更新员工请求模型"""
    number: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    gender: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=150)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=50)
    position: Optional[str] = Field(None, max_length=50)
    jointime: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """员工响应模型"""
    id: int = Field(..., description="Redmine Issue ID")
    createtime: str = Field("", description="创建时间")
    updatetime: str = Field("", description="更新时间")

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    """员工列表响应模型"""
    total: int = Field(..., description="总数")
    items: list[EmployeeResponse] = Field(..., description="员工列表")
    offset: int = Field(0, description="偏移量")
    limit: int = Field(20, description="每页数量")


class EmployeeSearchParams(BaseModel):
    """员工搜索参数"""
    name: Optional[str] = Field(None, description="姓名模糊搜索")
    department: Optional[str] = Field(None, description="部门")
    position: Optional[str] = Field(None, description="职位")
    jointime_start: Optional[str] = Field(None, description="入职时间开始 YYYY-MM-DD")
    jointime_end: Optional[str] = Field(None, description="入职时间结束 YYYY-MM-DD")
    offset: int = Field(0, ge=0, description="偏移量")
    limit: int = Field(20, ge=1, le=100, description="每页数量")
    sort: Optional[str] = Field("created_on:desc", description="排序字段")
