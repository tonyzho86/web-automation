"""结算流程的三个页面（填信息 → 确认订单 → 下单成功）。"""

from __future__ import annotations

from pages.base_page import BasePage


class CheckoutInfoPage(BasePage):
    """第一步：填写收货信息。"""

    path = "/checkout-step-one.html"

    FIRST_NAME = '[data-test="firstName"]'
    LAST_NAME = '[data-test="lastName"]'
    POSTAL_CODE = '[data-test="postalCode"]'
    CONTINUE_BUTTON = '[data-test="continue"]'
    ERROR_MESSAGE = '[data-test="error"]'

    def fill_info(
        self, first_name: str, last_name: str, postal_code: str
    ) -> "CheckoutOverviewPage":
        self.fill(self.FIRST_NAME, first_name)
        self.fill(self.LAST_NAME, last_name)
        self.fill(self.POSTAL_CODE, postal_code)
        self.click(self.CONTINUE_BUTTON)
        return CheckoutOverviewPage(self.page)

    def continue_expecting_error(self) -> "CheckoutInfoPage":
        """不填信息直接继续，用于校验必填提示。"""
        self.click(self.CONTINUE_BUTTON)
        return self

    def error_message(self) -> str:
        return self.text_of(self.ERROR_MESSAGE)


class CheckoutOverviewPage(BasePage):
    """第二步：订单确认。"""

    path = "/checkout-step-two.html"

    ITEM_NAME = '[data-test="inventory-item-name"]'
    SUBTOTAL_LABEL = '[data-test="subtotal-label"]'
    FINISH_BUTTON = '[data-test="finish"]'

    def item_names(self) -> list[str]:
        return self.page.locator(self.ITEM_NAME).all_inner_texts()

    def subtotal_text(self) -> str:
        """形如 'Item total: $39.98'。"""
        return self.text_of(self.SUBTOTAL_LABEL)

    def finish(self) -> "CheckoutCompletePage":
        self.click(self.FINISH_BUTTON)
        return CheckoutCompletePage(self.page)


class CheckoutCompletePage(BasePage):
    """第三步：下单成功。"""

    path = "/checkout-complete.html"

    COMPLETE_HEADER = '[data-test="complete-header"]'
    BACK_HOME_BUTTON = '[data-test="back-to-products"]'

    def success_message(self) -> str:
        return self.text_of(self.COMPLETE_HEADER)

    def is_success(self) -> bool:
        # 下单后页面要跳转，必须等成功页出现才能判断，不能用 is_visible 立即求值
        return self.wait_visible(self.COMPLETE_HEADER)
