from fastapi import APIRouter, Depends, File, Query, UploadFile

from app.api.v1.auth import get_current_user
from app.core.exceptions import ValidationException
from app.schemas.common import CommonResponse
from app.schemas.user import UserInfo
from app.services.import_services import import_employees
from app.utils.excel import parse_import_file
from app.utils.response import success_response

router = APIRouter(prefix="/import", tags=["数据导入"])


@router.post("/employees", response_model=CommonResponse[dict])
def import_employees_file(
    file: UploadFile = File(..., description="CSV 或 Excel 文件"),
    strategy: str = Query("skip", description="重复处理策略: skip/overwrite/abort"),
    current_user: UserInfo = Depends(get_current_user),
):
    """批量导入人员数据"""
    if not file.filename:
        raise ValidationException("请上传文件")

    content = file.file.read()

    try:
        rows = parse_import_file(content, file.filename)
    except Exception as e:
        raise ValidationException(f"文件解析失败: {str(e)}")

    if not rows:
        raise ValidationException("文件内容为空或无法识别表头")

    result = import_employees(rows, strategy=strategy)
    return success_response(data=result, message="导入完成")
