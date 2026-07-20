"""
UI 测试：数据导入流程
"""
import os
import time

from playwright.sync_api import expect


def test_import_csv(logged_page):
    """上传 CSV 文件并查看导入结果"""
    page = logged_page
    page.wait_for_timeout(1000)

    # 生成临时测试文件
    ts = int(time.time())
    content = f"人员编号,姓名,性别\nUI_IMP_{ts},导入UI测试,男\n"

    # 通过 file chooser 上传
    file_chooser = page.locator("#upload-employee-data input[type=file]")
    file_chooser.set_input_files({
        "name": f"ui_import_{ts}.csv",
        "mimeType": "text/csv",
        "buffer": content.encode("utf-8"),
    })

    page.wait_for_timeout(3000)

    # 验证导入结果提示出现
    result = page.locator("#batch-delete-result")
    expect(result).not_to_be_empty()


def test_import_button_visible(logged_page):
    """数据导入按钮可见"""
    page = logged_page
    page.wait_for_timeout(1000)
    expect(page.get_by_text("数据导入")).to_be_visible()
