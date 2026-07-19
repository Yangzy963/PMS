"""
单元测试：Excel/CSV 文件解析工具
"""
import io
import pytest


class TestParseImportFile:
    """文件解析"""

    def test_csv_parse(self):
        """CSV 解析"""
        from app.utils.excel import parse_import_file
        content = "人员编号,姓名,性别\n001,张三,男\n002,李四,女".encode("utf-8")
        rows = parse_import_file(content, "test.csv")
        assert len(rows) == 2
        assert rows[0]["人员编号"] == "001"
        assert rows[0]["姓名"] == "张三"
        assert rows[1]["人员编号"] == "002"

    def test_excel_parse(self):
        """Excel 解析"""
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(["人员编号", "姓名"])
            ws.append(["001", "张三"])
            buf = io.BytesIO()
            wb.save(buf)
            buf.seek(0)
        except ImportError:
            pytest.skip("openpyxl not installed")

        from app.utils.excel import parse_import_file
        rows = parse_import_file(buf.getvalue(), "test.xlsx")
        assert len(rows) == 1
        assert rows[0]["人员编号"] == "001"

    def test_empty_csv(self):
        """纯表头无数据"""
        from app.utils.excel import parse_import_file
        content = "人员编号,姓名,性别\n".encode("utf-8")
        rows = parse_import_file(content, "test.csv")
        assert rows == []

    def test_column_strip(self):
        """列名去除空格"""
        from app.utils.excel import parse_import_file
        content = " 人员编号 , 姓名 \n001,张三".encode("utf-8")
        rows = parse_import_file(content, "test.csv")
        assert "人员编号" in rows[0]

    def test_invalid_extension(self):
        """不支持的文件类型"""
        from app.utils.excel import parse_import_file
        with pytest.raises(ValueError, match="CSV"):
            parse_import_file(b"test", "test.txt")
