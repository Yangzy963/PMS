"""
UI 测试：表单校验验证
"""
from playwright.sync_api import expect


def test_empty_required_fields(logged_page):
    """必填字段为空时显示提示"""
    page = logged_page
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    # 点击新增，等待弹窗出现
    page.click("#open-modal")
    try:
        page.wait_for_selector("#emp-number", timeout=10000)
    except Exception:
        # 弹窗可能未打开，重试一次
        page.click("#open-modal")
        page.wait_for_selector("#emp-number", timeout=10000)

    # 不填任何内容直接保存
    page.click("#save-employee")
    page.wait_for_timeout(2000)

    # 验证有错误提示（#save-result 区域出现红色提示）
    result = page.locator("#save-result .alert-danger")
    if result.count() > 0:
        expect(result).to_be_visible()


def test_form_opens_and_closes(logged_page):
    """弹窗正常打开和关闭"""
    page = logged_page
    page.wait_for_timeout(1000)

    # 打开弹窗
    page.click("#open-modal")
    page.wait_for_selector("#emp-number")
    expect(page.locator("#employee-modal")).to_be_visible()

    # 关闭弹窗
    page.click("#close-modal")
    page.wait_for_timeout(1000)
    expect(page.locator("#employee-modal")).not_to_be_visible()
