"""登录页。"""

from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    """https://www.saucedemo.com/"""

    path = "/"

    # 定位符集中放这里，页面改版时只改这一处
    USERNAME_INPUT = "#user-name"
    PASSWORD_INPUT = "#password"
    LOGIN_BUTTON = "#login-button"
    ERROR_MESSAGE = '[data-test="error"]'

    def open(self) -> "LoginPage":
        self.page.goto(self.path, wait_until="domcontentloaded")
        return self

    # ---------- 业务动作 ----------

    def login(self, username: str, password: str) -> InventoryPage:
        """执行登录。

        成功时返回下一个页面对象（InventoryPage），
        让"登录 → 进商品页"这个跳转在类型上就表达清楚。
        """
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        return InventoryPage(self.page)

    def login_expecting_failure(self, username: str, password: str) -> "LoginPage":
        """登录并停留在当前页（用于失败场景）。"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        return self

    # ---------- 读取状态 ----------

    def error_message(self) -> str:
        expect(self.page.locator(self.ERROR_MESSAGE)).to_be_visible()
        return self.text_of(self.ERROR_MESSAGE)

    def has_error(self) -> bool:
        return self.is_visible(self.ERROR_MESSAGE)

    def is_loaded(self) -> bool:
        return self.is_visible(self.LOGIN_BUTTON)
