"""
UI 测试：页面权限与元素展示
"""
from playwright.sync_api import expect


def test_navbar_unauthenticated(page):
    """未登录时导航栏只显示首页"""
    nav = page.locator(".navbar")
    expect(nav).to_be_visible()
    # 未登录时有"首页"链接
    expect(nav.get_by_text("首页")).to_be_visible()


def test_navbar_after_login(logged_page):
    """登录后导航栏显示人员管理和退出"""
    nav = logged_page.locator(".navbar")
    expect(nav.get_by_role("link", name="人员管理")).to_be_visible()
    expect(nav.get_by_text("退出登录")).to_be_visible()


def test_table_visible(logged_page):
    """登录后表格可见"""
    logged_page.wait_for_timeout(2000)
    table = logged_page.locator("#employee-table-container table")
    expect(table).to_be_visible()


def test_action_buttons_visible(logged_page):
    """操作按钮可见"""
    logged_page.wait_for_timeout(2000)
    expect(logged_page.locator("#open-modal")).to_be_visible()
    expect(logged_page.locator("#batch-delete")).to_be_visible()
    expect(logged_page.locator("text=数据导入")).to_be_visible()
