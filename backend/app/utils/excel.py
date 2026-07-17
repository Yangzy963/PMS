import io
from typing import Any

import pandas as pd


def parse_import_file(content: bytes, filename: str) -> list[dict[str, Any]]:
    """
    解析上传的 Excel 或 CSV 文件

    :param content: 文件二进制内容
    :param filename: 文件名，用于判断文件类型
    :return: 员工数据字典列表
    """
    lower_name = filename.lower()

    if lower_name.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(content), dtype=str)
    elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(content), dtype=str)
    else:
        raise ValueError("仅支持 CSV 或 Excel(.xlsx/.xls) 文件")

    # 去除空行空列
    df = df.dropna(how="all")

    # 列名标准化：去除首尾空格
    df.columns = [str(c).strip() for c in df.columns]

    # 将 NaN 转为空字符串
    df = df.fillna("")

    return df.to_dict(orient="records")
