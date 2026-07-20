"""
UI 测试：登录与退出
"""
from playwright.sync_api import expect


def test_login_success(page):
    """登录成功跳转到人员管理页"""
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    page.click("#login-button")
    page.wait_for_url("**/employee")
    expect(page).to_have_url("http://127.0.0.1:8050/employee")


def test_login_wrong_password(page):
    """错误密码提示"""
    page.fill("#username", "admin")
    page.fill("#password", "wrong")
    page.click("#login-button")
    error = page.locator("#login-error")
    expect(error).not_to_be_empty()


def test_logout(page):
    """退出登录返回登录页"""
    # 先登录
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    page.click("#login-button")
    page.wait_for_url("**/employee")

    # 退出
    page.click("#logout-button")
    page.wait_for_url("**/")
    expect(page).to_have_url("http://127.0.0.1:8050/")


def test_route_guard(page):
    """未登录访问 /employee 被拦截"""
    page.goto("http://127.0.0.1:8050/employee")
    page.wait_for_url("**/")
    expect(page).to_have_url("http://127.0.0.1:8050/")
