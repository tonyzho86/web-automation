"""购物车页。"""

from __future__ import annotations

from playwright.sync_api import expect

from pages.base_page import BasePage


class CartPage(BasePage):
    """https://www.saucedemo.com/cart.html"""

    path = "/cart.html"

    CART_ITEM = '[data-test="inventory-item"]'
    ITEM_NAME = '[data-test="inventory-item-name"]'
    CHECKOUT_BUTTON = '[data-test="checkout"]'
    CONTINUE_SHOPPING_BUTTON = '[data-test="continue-shopping"]'

    # ---------- 业务动作 ----------

    def remove(self, name: str) -> "CartPage":
        item = self.page.locator(self.CART_ITEM, has_text=name)
        item.get_by_role("button", name="Remove").click()
        # 等这一行真的从列表里消失，否则紧接着的 item_count() 可能还是旧值
        expect(item).to_have_count(0)
        return self

    def checkout(self):
        """进入结算流程第一步。这里延迟导入，避免与 checkout_page 循环引用。"""
        from pages.checkout_page import CheckoutInfoPage

        self.click(self.CHECKOUT_BUTTON)
        return CheckoutInfoPage(self.page)

    # ---------- 读取状态 ----------

    def item_names(self) -> list[str]:
        return self.page.locator(self.ITEM_NAME).all_inner_texts()

    def item_count(self) -> int:
        return self.page.locator(self.CART_ITEM).count()

    def contains(self, name: str) -> bool:
        return name in self.item_names()

    def is_empty(self) -> bool:
        return self.item_count() == 0
