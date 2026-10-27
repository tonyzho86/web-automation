"""pytest 全局装置：把"每个用例都要写的准备工作"变成 fixture。"""

from __future__ import annotations

import base64

import pytest

from config.settings import settings
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

try:  # pytest-html 是可选的，没装也不影响跑测试
    from pytest_html import extras
except ImportError:  # pragma: no cover
    extras = None


# --------------------------------------------------------------------------
# 环境
# --------------------------------------------------------------------------


@pytest.fixture(scope="session")
def base_url() -> str:
    """覆盖 pytest-base-url 的 base_url。

    这样 page.goto("/inventory.html") 里的相对路径会自动拼上 BASE_URL，
    切环境只要改 .env，用例一行都不用动。
    """
    return settings.base_url


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict) -> dict:
    """统一浏览器上下文参数。"""
    return {
        **browser_context_args,
        "viewport": {"width": 1440, "height": 900},
        # 时间和语言固定下来，避免不同机器上日期/文案渲染不一致导致用例飘
        "locale": "zh-CN",
        "timezone_id": "Asia/Shanghai",
    }


# --------------------------------------------------------------------------
# 业务 fixture
# --------------------------------------------------------------------------


@pytest.fixture
def login_page(page) -> LoginPage:
    """打开登录页。"""
    return LoginPage(page).open()


@pytest.fixture
def inventory_page(page) -> InventoryPage:
    """已登录并停留在商品列表页 —— 大多数业务用例的起点。"""
    return LoginPage(page).open().login(settings.standard_user, settings.password)


# --------------------------------------------------------------------------
# 失败现场
# --------------------------------------------------------------------------


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例失败时把截图直接嵌进 HTML 报告。

    截图/录像/Trace 的落盘由运行参数控制（见 pyproject.toml 的 addopts），
    这里额外做的是"让人不用点开文件夹就能看到现场"。
    """
    outcome = yield
    report = outcome.get_result()

    if extras is None or report.when != "call" or not report.failed:
        return

    page = item.funcargs.get("page")
    if page is None or page.is_closed():
        return

    try:
        png = page.screenshot(full_page=True)
    except Exception:  # 页面已崩溃时截图会失败，不能因此掩盖真正的报错
        return

    report.extras = list(getattr(report, "extras", []))
    report.extras.append(
        extras.image(base64.b64encode(png).decode("utf-8"), name="失败截图")
    )
