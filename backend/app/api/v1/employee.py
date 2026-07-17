from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.api.v1.auth import get_current_user
from app.core.exceptions import NotFoundException, ValidationException
from app.schemas.common import CommonResponse
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeListResponse,
    EmployeeResponse,
    EmployeeSearchParams,
    EmployeeUpdate,
)
from app.schemas.user import UserInfo
from app.services.redmine_services import redmine_client
from app.utils.response import success_response

router = APIRouter(prefix="/employees", tags=["人员管理"])


@router.post("", response_model=CommonResponse[EmployeeResponse])
def create_employee(
    employee: EmployeeCreate,
    current_user: UserInfo = Depends(get_current_user),
):
    """新增人员"""
    # 重复数据检查：人员编号
    existing = redmine_client.find_by_number(employee.number)
    if existing:
        raise ValidationException(f"人员编号 {employee.number} 已存在")

    data = employee.model_dump()
    result = redmine_client.create_employee(data)
    return success_response(data=result, message="新增人员成功")


@router.get("", response_model=CommonResponse[EmployeeListResponse])
def list_employees(
    name: Optional[str] = Query(None, description="姓名模糊搜索"),
    department: Optional[str] = Query(None, description="部门"),
    position: Optional[str] = Query(None, description="职位"),
    jointime_start: Optional[str] = Query(None, description="入职时间开始 YYYY-MM-DD"),
    jointime_end: Optional[str] = Query(None, description="入职时间结束 YYYY-MM-DD"),
    offset: int = Query(0, ge=0, description="偏移量"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    sort: str = Query("created_on:desc", description="排序字段"),
    current_user: UserInfo = Depends(get_current_user),
):
    """查询人员列表（支持搜索与分页）"""
    params = EmployeeSearchParams(
        name=name,
        department=department,
        position=position,
        jointime_start=jointime_start,
        jointime_end=jointime_end,
        offset=offset,
        limit=limit,
        sort=sort,
    )

    # 先按部门和职位等可精确筛选的字段从 Redmine 拉取
    filters = {}
    if params.department:
        filters["department"] = params.department
    if params.position:
        filters["position"] = params.position

    # 由于 Redmine 对自定义字段的模糊搜索支持有限，先获取一批数据再本地过滤
    employees, total = redmine_client.list_employees(
        offset=0,
        limit=1000,  # 演示场景下先取较多数据本地过滤
        sort=params.sort,
        filters=filters,
    )

    # 姓名模糊搜索
    if params.name:
        employees = [e for e in employees if params.name in e.get("name", "")]
        total = len(employees)

    # 入职时间范围过滤
    if params.jointime_start or params.jointime_end:
        filtered = []
        for emp in employees:
            jointime = emp.get("jointime") or ""
            if not jointime:
                continue
            if params.jointime_start and jointime < params.jointime_start:
                continue
            if params.jointime_end and jointime > params.jointime_end:
                continue
            filtered.append(emp)
        employees = filtered
        total = len(employees)

    # 分页
    paginated = employees[offset:offset + limit]

    return success_response(
        data=EmployeeListResponse(total=total, items=paginated, offset=offset, limit=limit),
        message="查询成功",
    )


@router.get("/{employee_id}", response_model=CommonResponse[EmployeeResponse])
def get_employee(
    employee_id: int,
    current_user: UserInfo = Depends(get_current_user),
):
    """查看人员详情"""
    result = redmine_client.get_employee(employee_id)
    return success_response(data=result, message="查询成功")


@router.put("/{employee_id}", response_model=CommonResponse[EmployeeResponse])
def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    current_user: UserInfo = Depends(get_current_user),
):
    """修改人员信息"""
    existing = redmine_client.get_employee(employee_id)

    # 合并现有数据与更新数据
    data = {k: v for k, v in existing.items() if v is not None and v != ""}
    update_data = {k: v for k, v in employee.model_dump().items() if v is not None}
    data.update(update_data)

    # 如果修改了人员编号，检查重复
    if update_data.get("number") and update_data["number"] != existing.get("number"):
        dup = redmine_client.find_by_number(update_data["number"])
        if dup and dup["id"] != employee_id:
            raise ValidationException(f"人员编号 {update_data['number']} 已存在")

    result = redmine_client.update_employee(employee_id, data)
    return success_response(data=result, message="修改人员成功")


@router.delete("/{employee_id}", response_model=CommonResponse[dict])
def delete_employee(
    employee_id: int,
    current_user: UserInfo = Depends(get_current_user),
):
    """删除人员"""
    # 先查询确认存在
    redmine_client.get_employee(employee_id)
    redmine_client.delete_employee(employee_id)
    return success_response(data={"id": employee_id}, message="删除人员成功")


@router.post("/batch-delete", response_model=CommonResponse[dict])
def batch_delete_employees(
    employee_ids: list[int],
    current_user: UserInfo = Depends(get_current_user),
):
    """批量删除人员"""
    if not employee_ids:
        raise ValidationException("请选择要删除的人员")

    deleted = []
    for employee_id in employee_ids:
        try:
            redmine_client.delete_employee(employee_id)
            deleted.append(employee_id)
        except NotFoundException:
            continue

    return success_response(
        data={"deleted_count": len(deleted), "deleted_ids": deleted},
        message=f"成功删除 {len(deleted)} 条人员记录",
    )
