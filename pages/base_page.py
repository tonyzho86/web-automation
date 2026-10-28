"""页面基类：所有 Page Object 共用的基础能力。

设计原则：只封装"每个页面都会用到"的动作。
不要把 Playwright 的 API 再包一遍（比如给 click 加五层参数），
那会让 POM 变成负担，而不是资产。
"""

from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect


class BasePage:
    """所有页面的父类。"""

    #: 页面路径，相对于 BASE_URL。子类按需覆盖。
    path: str = "/"

    def __init__(self, page: Page) -> None:
        self.page = page

    # ---------- 导航 ----------

    def open(self) -> "BasePage":
        """打开当前页面，返回自身以支持链式调用。

        用 domcontentloaded 而不是默认的 load：
        load 会等所有图片/字体加载完，网络慢时容易卡满 30 秒超时。
        DOM 就绪即可，后续元素操作有 Playwright 的自动等待兜底。
        """
        self.page.goto(self.path, wait_until="domcontentloaded")
        return self

    @property
    def url(self) -> str:
        return self.page.url

    # ---------- 定位 ----------

    def locator(self, selector: str, **kwargs) -> Locator:
        return self.page.locator(selector, **kwargs)

    def by_test_id(self, test_id: str) -> Locator:
        """按 data-test 属性定位。

        saucedemo 给关键元素都加了 data-test，用它定位比 CSS 类名稳定得多。
        建议团队内统一：data-test > 语义化 role > CSS 类名 > XPath。
        """
        return self.page.locator(f'[data-test="{test_id}"]')

    # ---------- 常用动作 ----------
    # Playwright 自带自动等待，这里不需要手写 sleep 或显式等待

    def click(self, selector: str) -> None:
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str) -> None:
        self.page.locator(selector).fill(value)

    def text_of(self, selector: str) -> str:
        return self.page.locator(selector).inner_text().strip()

    def is_visible(self, selector: str) -> bool:
        """立即判断元素是否可见，不做任何等待。

        只能用在"页面已经稳定"的场景。凡是刚触发过跳转/异步刷新的地方，
        都用 wait_visible()，否则会拿到跳转前的旧状态 —— 这是 flaky 的头号来源。
        """
        return self.page.locator(selector).is_visible()

    def wait_visible(self, selector: str, timeout: float = 5000) -> bool:
        """等待元素出现并可见，超时返回 False（不抛异常）。

        适合"跳转之后判断到底成没成功"这类场景。

        注意：expect 是严格模式，selector 必须**唯一命中**一个元素。
        要判断"一类元素中至少有一个在"（比如商品列表），请显式加 .first。
        """
        try:
            expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
        except AssertionError:
            return False
        return True

    # ---------- 断言辅助 ----------
    # 用 Playwright 的 expect（自动重试），而不是 assert + 立即取值，
    # 否则页面还没渲染完就会误报失败

    def expect_visible(self, selector: str, timeout: float | None = None) -> None:
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)

    def expect_text(self, selector: str, expected: str) -> None:
        expect(self.page.locator(selector)).to_have_text(expected)

    def expect_url_contains(self, fragment: str) -> None:
        """断言当前 URL 包含指定片段。

        注意必须传正则：to_have_url 收到字符串时是**精确匹配**，
        写 "./cart.html." 这种"模糊"字符串是匹配不上的。
        """
        expect(self.page).to_have_url(re.compile(re.escape(fragment)))
