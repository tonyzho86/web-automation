"""商品列表页。"""

from __future__ import annotations

from playwright.sync_api import Locator, expect

from pages.base_page import BasePage
from pages.cart_page import CartPage


class InventoryPage(BasePage):
    """https://www.saucedemo.com/inventory.html"""

    path = "/inventory.html"

    TITLE = '[data-test="title"]'
    CART_LINK = '[data-test="shopping-cart-link"]'
    CART_BADGE = '[data-test="shopping-cart-badge"]'
    ITEM_CARD = ".inventory_item"
    ITEM_NAME = '[data-test="inventory-item-name"]'
    ITEM_PRICE = '[data-test="inventory-item-price"]'

    # ---------- 定位 ----------

    def item_card(self, name: str) -> Locator:
        """按商品名定位到整张商品卡片。

        拿到卡片后再往里找按钮，比拼字符串拼出 add-to-cart-xxx 更抗改版。
        """
        return self.page.locator(self.ITEM_CARD, has_text=name)

    # ---------- 业务动作 ----------

    def add_to_cart(self, name: str) -> "InventoryPage":
        card = self.item_card(name)
        card.get_by_role("button", name="Add to cart").click()
        # 等按钮翻成 Remove 再返回：这既代表"加入成功"，
        # 也保证购物车角标已经刷新，后面读 cart_count() 不会读到旧值
        expect(card.get_by_role("button", name="Remove")).to_be_visible()
        return self

    def remove_from_cart(self, name: str) -> "InventoryPage":
        card = self.item_card(name)
        card.get_by_role("button", name="Remove").click()
        expect(card.get_by_role("button", name="Add to cart")).to_be_visible()
        return self

    def add_all_to_cart(self) -> "InventoryPage":
        """把当前页所有商品都加入购物车。"""
        for name in self.item_names():
            self.add_to_cart(name)
        return self

    def open_cart(self) -> CartPage:
        self.click(self.CART_LINK)
        return CartPage(self.page)

    # ---------- 读取状态 ----------

    def cart_count(self) -> int:
        """购物车角标数量。没加商品时角标不渲染，所以返回 0。"""
        badge = self.page.locator(self.CART_BADGE)
        if badge.count() == 0:
            return 0
        return int(badge.inner_text())

    def item_names(self) -> list[str]:
        return self.page.locator(self.ITEM_NAME).all_inner_texts()

    def item_count(self) -> int:
        return self.page.locator(self.ITEM_CARD).count()

    def expect_loaded(self) -> None:
        """断言商品列表已渲染完成。

        必须用 .first —— Playwright 的 expect 是严格模式，
        定位符一次命中多个元素（这里每件商品都是一个 .inventory_item）
        会被判定为失败，而不是"只要有一个可见就算过"。
        """
        expect(self.page.locator(self.ITEM_CARD).first).to_be_visible()
