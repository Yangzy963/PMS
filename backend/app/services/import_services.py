from datetime import datetime
from typing import Any, Optional

import pandas as pd

from app.core.exceptions import ValidationException
from app.schemas.employee import EmployeeBase
from app.services.redmine_services import redmine_client


def normalize_date(value: Any) -> tuple[Optional[str], Optional[str]]:
    """
    解析并标准化日期格式

    :return: (标准化后的 YYYY-MM-DD 字符串, 错误信息)
    """
    if value is None or str(value).strip() == "" or str(value).lower() == "nan":
        return None, None

    # pandas Timestamp / datetime 对象
    if isinstance(value, (datetime, pd.Timestamp)):
        return value.strftime("%Y-%m-%d"), None

    date_str = str(value).strip()

    # 常见日期格式
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%Y年%m月%d日",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y%m%d",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime("%Y-%m-%d"), None
        except ValueError:
            continue

    return None, "入职时间格式无法识别，支持 YYYY-MM-DD、YYYY/MM/DD、YYYY年MM月DD日 等"


def validate_employee_row(row: dict[str, Any], row_index: int) -> tuple[dict, list[str]]:
    """
    校验单行员工数据

    :return: (标准化后的数据, 错误信息列表)
    """
    errors = []

    # 必需字段
    number = str(row.get("人员编号", "")).strip()
    name = str(row.get("姓名", "")).strip()

    if not number:
        errors.append("人员编号不能为空")
    if not name:
        errors.append("姓名不能为空")

    data = {
        "number": number,
        "name": name,
        "gender": str(row.get("性别", "")).strip(),
        "department": str(row.get("部门", "")).strip(),
        "position": str(row.get("职位", "")).strip(),
        "phone": str(row.get("手机号", "")).strip(),
        "email": str(row.get("邮箱", "")).strip(),
        "jointime": str(row.get("入职时间", "")).strip(),
    }

    # 年龄校验
    age_raw = row.get("年龄")
    if age_raw is not None and str(age_raw).strip() != "":
        try:
            age = int(float(str(age_raw).strip()))
            if age < 0 or age > 150:
                errors.append("年龄必须在 0-150 之间")
            else:
                data["age"] = age
        except (ValueError, TypeError):
            errors.append("年龄必须是整数")

    # 入职时间格式校验与标准化
    jointime_raw = row.get("入职时间")
    normalized_jointime, jointime_error = normalize_date(jointime_raw)
    if jointime_error:
        errors.append(jointime_error)
    else:
        data["jointime"] = normalized_jointime or ""

    # 使用 Pydantic 再做一层校验
    if not errors:
        try:
            EmployeeBase(**data)
        except Exception as e:
            errors.append(str(e))

    return data, errors


def import_employees(
    rows: list[dict[str, Any]],
    strategy: str = "skip",
) -> dict[str, Any]:
    """
    批量导入员工

    :param strategy: 重复数据处理策略 skip/overwrite/abort
    :return: 导入结果统计
    """
    if strategy not in {"skip", "overwrite", "abort"}:
        raise ValidationException("重复处理策略必须是 skip、overwrite 或 abort")

    success = 0
    skipped = 0
    overwritten = 0
    failed = 0
    errors = []

    for idx, row in enumerate(rows, start=1):
        data, row_errors = validate_employee_row(row, idx)

        if row_errors:
            failed += 1
            errors.append({"row": idx, "number": data.get("number"), "errors": row_errors})
            continue

        number = data["number"]
        existing = redmine_client.find_by_number(number)

        try:
            if existing:
                if strategy == "abort":
                    failed += 1
                    errors.append({
                        "row": idx,
                        "number": number,
                        "errors": [f"人员编号 {number} 已存在"],
                    })
                    break
                elif strategy == "skip":
                    skipped += 1
                    continue
                elif strategy == "overwrite":
                    redmine_client.update_employee(existing["id"], data)
                    overwritten += 1
            else:
                redmine_client.create_employee(data)
                success += 1
        except Exception as e:
            failed += 1
            errors.append({"row": idx, "number": number, "errors": [str(e)]})

    return {
        "total": len(rows),
        "success": success,
        "skipped": skipped,
        "overwritten": overwritten,
        "failed": failed,
        "errors": errors,
    }
