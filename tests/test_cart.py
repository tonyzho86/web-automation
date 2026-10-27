"""购物车与下单主流程用例。"""

from __future__ import annotations

import pytest

BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"


@pytest.mark.smoke
def test_add_single_item_updates_badge(inventory_page):
    """加入一件商品后，购物车角标应变为 1。"""
    assert inventory_page.cart_count() == 0, "初始状态购物车应为空"

    inventory_page.add_to_cart(BACKPACK)

    assert inventory_page.cart_count() == 1


@pytest.mark.regression
def test_add_multiple_items(inventory_page):
    """连续加入多件商品，角标应累加。"""
    inventory_page.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)

    assert inventory_page.cart_count() == 2


@pytest.mark.regression
def test_cart_shows_added_item(inventory_page):
    """购物车里应该能看到刚才加的商品。"""
    inventory_page.add_to_cart(BACKPACK)

    cart = inventory_page.open_cart()

    cart.expect_url_contains("/cart.html")
    assert cart.item_count() == 1
    assert cart.contains(BACKPACK), f"购物车内容不符：{cart.item_names()}"


@pytest.mark.regression
def test_remove_item_empties_cart(inventory_page):
    """移除商品后购物车应回到空状态。"""
    inventory_page.add_to_cart(BACKPACK)

    cart = inventory_page.open_cart().remove(BACKPACK)

    assert cart.is_empty(), f"购物车应已清空，实际还有：{cart.item_names()}"


@pytest.mark.smoke
def test_full_checkout_flow(inventory_page):
    """端到端主流程：加购 → 购物车 → 填信息 → 下单成功。

    这条用例演示了 POM 的链式调用：每一步返回下一个页面对象，
    用例读起来就是一条业务链路。
    """
    inventory_page.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)

    complete = (
        inventory_page.open_cart()
        .checkout()
        .fill_info("测试", "工程师", "200000")
        .finish()
    )

    assert complete.is_success(), "下单后没有出现成功页"
    assert "thank you" in complete.success_message().lower()


@pytest.mark.regression
def test_checkout_requires_customer_info(inventory_page):
    """结算第一步不填信息时，应提示必填。"""
    info = inventory_page.add_to_cart(BACKPACK).open_cart().checkout()

    info.continue_expecting_error()

    assert "first name is required" in info.error_message().lower()
