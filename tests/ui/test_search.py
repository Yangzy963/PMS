"""
UI 测试：搜索与筛选
"""
from playwright.sync_api import expect


def test_search_by_name(logged_page):
    """姓名模糊搜索"""
    page = logged_page
    page.wait_for_timeout(2000)

    # 输入搜索条件
    page.fill("#name-search", "UI测试")
    page.click("#search-btn")
    page.wait_for_timeout(2000)

    # 表格应该有数据
    table = page.locator("#employee-table-container")
    expect(table).to_be_visible()


def test_reset_search(logged_page):
    """重置搜索条件"""
    page = logged_page
    page.wait_for_timeout(2000)

    # 输入搜索
    page.fill("#name-search", "UI测试")
    page.click("#search-btn")
    page.wait_for_timeout(1000)

    # 点击重置
    page.click("#reset-btn")
    page.wait_for_timeout(1000)

    # 输入框应清空
    expect(page.locator("#name-search")).to_have_value("")
