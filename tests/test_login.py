"""登录功能用例。

注意：用例里只有"业务语言"——登录、看到什么、断言什么。
元素怎么找、怎么等，全部在 pages/ 里，改版时只改那一层。
"""

from __future__ import annotations

import pytest

from config.settings import settings


@pytest.mark.smoke
def test_standard_user_login_success(login_page):
    """标准用户能正常登录并进入商品列表页。"""
    inventory = login_page.login(settings.standard_user, settings.password)

    inventory.expect_url_contains("/inventory.html")
    inventory.expect_loaded()


@pytest.mark.smoke
def test_locked_user_is_rejected(login_page):
    """被锁定的用户登录时应看到明确提示，且不能进入系统。"""
    login_page.login_expecting_failure(settings.locked_user, settings.password)

    error = login_page.error_message()
    assert "locked out" in error.lower(), f"提示文案不符：{error}"
    assert "/inventory.html" not in login_page.url, "被锁定用户不应进入商品页"


@pytest.mark.regression
@pytest.mark.parametrize(
    ("username", "password", "expected_fragment"),
    [
        (settings.standard_user, "wrong_password", "do not match"),
        ("", settings.password, "Username is required"),
        (settings.standard_user, "", "Password is required"),
    ],
    ids=["密码错误", "用户名称为空", "密码为空"],
)
def test_login_failure_shows_message(login_page, username, password, expected_fragment):
    """各类登录失败场景都要给出对应的错误提示。"""
    login_page.login_expecting_failure(username, password)

    error = login_page.error_message()
    assert expected_fragment.lower() in error.lower(), f"提示文案不符：{error}"
