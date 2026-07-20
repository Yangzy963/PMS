"""
UI 自动化测试共享 fixtures（需要前后端运行）
"""
import pytest
from playwright.sync_api import Page, BrowserContext


BASE_URL = "http://127.0.0.1:8050"


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """每个测试独立页面，自动清理 localStorage"""
    page = context.new_page()
    page.goto(BASE_URL)
    yield page
    page.close()


@pytest.fixture(scope="function")
def logged_page(page):
    """已登录的页面"""
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    page.click("#login-button")
    page.wait_for_url("**/employee")
    return page
