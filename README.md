# Web 自动化测试框架

基于 **Playwright + pytest** 的 Web UI 自动化测试工程，采用 POM（页面对象模型）分层。

当前示例跑在公开演示站 [saucedemo.com](https://www.saucedemo.com) 上，换成你自己的系统只需要改 `.env`。

---

## 快速开始

```powershell
# 1. 安装依赖（uv 会自动准备好 Python，不用手动装）
uv sync

# 2. 安装浏览器（只需执行一次）
uv run playwright install chromium

# 3. 跑测试
uv run pytest
```

> **国内网络提示**：`playwright install` 默认从 `cdn.playwright.dev` 拉浏览器（合计约 300MB），国内经常龟速甚至直接卡死。
> 换镜像后几秒就能下完：
>
> ```powershell
> $env:PLAYWRIGHT_DOWNLOAD_HOST = "https://cdn.npmmirror.com/binaries/playwright"
> uv run playwright install chromium
> ```
>
> 这个环境变量只对当前终端窗口有效，新开窗口要重设。

跑完后：

- HTML 报告 → `reports/report.html`（用浏览器直接打开）
- 失败现场 → `reports/artifacts/`（截图、录像、Trace）

---

## 目录结构

```
web-automation/
├── config/
│   └── settings.py          # 环境配置，统一从 .env 读取，禁止硬编码
├── pages/                   # 页面对象层（Page Object）
│   ├── base_page.py         # 基类：导航、定位、断言等公共能力
│   ├── login_page.py        # 登录页
│   ├── inventory_page.py    # 商品列表页
│   ├── cart_page.py         # 购物车页
│   └── checkout_page.py     # 结算流程三个页面
├── tests/                   # 用例层：只写业务逻辑和断言
│   ├── conftest.py          # fixture 与失败截图钩子
│   ├── test_login.py
│   └── test_cart.py
├── .github/workflows/e2e.yml # CI：推代码 / 定时自动跑
├── pyproject.toml           # 依赖 + pytest 配置
└── .env.example             # 配置模板
```

**分层的意义**：页面改版时，元素定位的变化被挡在 `pages/` 里，用例层不用动。

---

## 常用命令

```powershell
uv run pytest                        # 全部用例（无头模式）
uv run pytest --headed               # 显示浏览器窗口，调试用
uv run pytest -m smoke               # 只跑冒烟用例
uv run pytest tests/test_login.py    # 只跑某个文件
uv run pytest -k "cart and not remove"  # 按名字筛选
uv run pytest --slowmo 500           # 每步放慢 500ms，看清操作过程
uv run pytest -n 4                   # 4 进程并行（需先装 pytest-xdist）
uv run pytest --browser firefox      # 换浏览器：chromium / firefox / webkit
uv run pytest -x                     # 遇到第一个失败就停
```

失败证据是**只在失败时**才保留的（`retain-on-failure`），通过用例不会产生垃圾文件。

---

## 失败现场怎么看

| 产物 | 位置 | 用途 |
|---|---|---|
| 截图 | `reports/artifacts/<用例名>/test-failed-1.png` | 快速看失败那一刻的页面 |
| 录像 | `reports/artifacts/<用例名>/video.webm` | 看操作过程，排查时序问题 |
| Trace | `reports/artifacts/<用例名>/trace.zip` | **最好用**，可回放每一步的 DOM 快照 |

Trace 回放（相当于给测试过程开了时光机，能看到每一步的页面、网络请求、console 报错）：

```powershell
uv run playwright show-trace reports/artifacts/<用例名>/trace.zip
```

也支持把这个 zip 拖到 <https://trace.playwright.dev> 在线查看。

另外，失败截图会**自动嵌进 `report.html`**，不用翻文件夹。

---

## 报告

**HTML 报告**（默认，零配置）：直接打开 `reports/report.html`。

**Allure 报告**（更专业，适合给团队/领导看）：

```powershell
uv run pytest                       # 先产生 reports/allure-results
allure serve reports/allure-results  # 需要本机有 allure 命令
```

Allure CLI 依赖 Java，本机没装的话（你机器上确实没有 Java，二选一）：

```powershell
# 方式一：装 Java
winget install Microsoft.OpenJDK.21

# 方式二：不装 Java，直接用官网绿色包
# 下载 https://github.com/allure-framework/allure2/releases 解压后把 bin 目录加进 PATH
```

> CI 上不需要额外配置，GitHub Actions 的 runner 自带 Java。

---

## 如何加一条新用例

**第 1 步**：如果涉及新页面，在 `pages/` 下新建页面类。

```python
from pages.base_page import BasePage

class OrderPage(BasePage):
    path = "/orders.html"                       # 相对 BASE_URL
    SEARCH_INPUT = '[data-test="search"]'

    def search(self, keyword: str) -> "OrderPage":
        self.fill(self.SEARCH_INPUT, keyword)
        self.page.keyboard.press("Enter")
        return self

    def order_ids(self) -> list[str]:
        return self.page.locator(".order-id").all_inner_texts()
```

**第 2 步**：在 `tests/` 下写用例。

```python
import pytest

@pytest.mark.regression
def test_search_order(inventory_page):
    order = inventory_page.to_order_page().search("20260930")
    assert order.order_ids(), "没有搜到任何订单"
```

**第 3 步**：跑一下。

```powershell
uv run pytest tests/test_order.py --headed
```

只有一种情况需要动 `conftest.py`：你要新增一个**多个用例共用的前置状态**（比如"已下单的账号"）。单条用例的准备工作，直接写在用例里就好。

---

## 换成你自己的系统

复制 `.env.example` 为 `.env`：

```ini
BASE_URL=https://你的测试环境地址
STANDARD_USER=你的账号
PASSWORD=你的密码
```

然后按新系统的页面结构改 `pages/` 下的定位符即可。`.env` 已在 `.gitignore` 里，不会被提交。

定位符优先级建议：`data-test` 属性 > 语义化 `role` > CSS 类名 > XPath。XPath 最脆弱，能不用就不用。

---

## CI（GitHub Actions）

`.github/workflows/e2e.yml` 已配好，触发时机：

- push 到 `main` / `master`
- 提交 Pull Request
- 每天北京时间 09:00 定时跑一次
- 手动触发（Actions 页面点 Run workflow）

账号密码不要写进仓库，去 **仓库 Settings → Secrets and variables → Actions** 配置 `STANDARD_USER`、`PASSWORD`、`BASE_URL`。

用的是 Jenkins / GitLab CI？把工作流里的核心三步翻译过去就行：

```bash
uv sync
uv run playwright install --with-deps chromium
uv run pytest
```

---

## 常见问题

**Q：报 `Executable doesn't exist at ...`**
浏览器没装，执行 `uv run playwright install chromium`。

**Q：想看到浏览器界面**
加 `--headed`。注意 CI 上必须无头，所以这个参数不要写进 `addopts`。

**Q：用例偶尔失败，重跑又好了（flaky）**
先下载失败时的 Trace 回放看现场，八成是等元素的方式有问题。**不要用 `time.sleep()` 硬等** —— Playwright 的元素操作自带自动等待，绝大多数场景不需要手动等待；确实需要时用 `expect(...)` 断言式等待。

**Q：`reports/` 目录要不要提交到 git？**
不要，已经加进 `.gitignore` 了。

**Q：想并行跑，快一点**
`uv add --dev pytest-xdist`，然后 `uv run pytest -n auto`。注意并行时用例之间不能有数据依赖。

**Q：测试数据被写脏了怎么办**
用例应该自己造数据、自己清理（或用 API/数据库在 fixture 里准备）。不要依赖手工提前造好的数据，那会让回归结果不可复现。

**Q：元素明明在页面上，断言却说不可见**
大概率是 Playwright 的**严格模式**在起作用：`expect(...)` 要求定位符**唯一命中一个元素**，命中多个一律判失败。列表类元素（商品行、表格行）必须显式加 `.first`，参考 `InventoryPage.expect_loaded()`。

**Q：`to_have_url` 写通配符字符串怎么都匹配不上**
它收到**字符串时是精确匹配**，通配符会被当字面量。要模糊匹配必须传正则。框架里已经包好了 `expect_url_contains()`，直接用就行。

**Q：怎么判断一处代码"该等"还是"不该等"**
一条标准：**这个读取所依赖的前置动作，有没有触发跳转或异步刷新**。有 → 必须用会重试的 API（`expect_*` / `wait_visible`）；没有 → 才可以用立即求值的读取（`is_visible` / `item_count`）。

搞反了就会得到"时灵时不灵"的用例 —— 而且本地机器快的时候常常看不出来，一到 CI 机器上就集体翻车。本项目里 `add_to_cart()` 点击后等按钮翻转、`CheckoutCompletePage.is_success()` 用 `wait_visible`，都是按这条规则写的。
