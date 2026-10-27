# Python 入门 —— 专门为了看懂本项目的自动化用例

> 这份文档**不是通用 Python 教程**。
> 它只讲 `web-automation` 这个项目里**实际出现过**的语法，一共 400 行代码。
> 学完你就能读懂每一条用例，也能自己改断言、加用例。

---

## 〇、先给你减负：这些**不用学**

我扫描了整个项目的代码，下面这些常见的"Python 高级特性"**一次都没出现过**：

| 特性 | 出现次数 | 结论 |
|---|---|---|
| `async` / `await`（异步） | **0** | 不用学 |
| `lambda`（匿名函数） | **0** | 不用学 |
| 列表推导式 | **0** | 不用学 |
| 多线程 / 多进程 | **0** | 不用学 |
| 元类、装饰器原理 | **0** | 只需会"看"装饰器，不用会"写" |
| 生成器 | 1（在框架里，你不用管） | 跳过 |

**真正需要掌握的，就是下面 10 章的内容。** 逐章读，每章都配了你项目里的真实代码。

### 代码分布（心里有个数）

| 文件 | 行数 | 你要读它的频率 |
|---|---|---|
| `tests/test_login.py` | 33 | ⭐⭐⭐ 天天看 |
| `tests/test_cart.py` | 50 | ⭐⭐⭐ 天天看 |
| `pages/login_page.py` | 38 | ⭐⭐ 偶尔 |
| `pages/inventory_page.py` | 54 | ⭐⭐ 偶尔 |
| `pages/base_page.py` | 58 | ⭐ 改版时才看 |
| `tests/conftest.py` | 62 | ⭐ 基本不用动 |

**你 90% 的时间只会读 `tests/` 里那两个文件，它们加起来才 83 行。**

---

## 第 1 章 · 文件、模块与 import

### 1.1 一个 `.py` 文件就是一个"模块"

`test_login.py` 是一个模块，`base_page.py` 也是一个模块。模块之间通过 `import` 互相使用。

### 1.2 三种 import 写法

**写法一：导入整个模块**

```python
import os
import re
```
用的时候要带模块名：`os.getenv("CI")`、`re.compile(...)`。

**写法二：只导入需要的名字**

```python
from pathlib import Path
from dataclasses import dataclass
```
用的时候直接写：`Path(...)`、`@dataclass`，不用带前缀。

**写法三：导入并重命名**

```python
import pytest
```
这个其实是写法一。项目里没用到 `as` 重命名。

### 1.3 项目里的真实例子

```python
# pages/login_page.py
from playwright.sync_api import expect

from pages.base_page import BasePage
from pages.inventory_page import InventoryPage
```

逐行理解：

- 第 1 行：从 `playwright.sync_api` 这个包里，拿 `expect` 这个工具
- 第 3 行：从 `pages/base_page.py` 这个文件里，拿 `BasePage` 这个类
- 第 4 行：同上，拿 `InventoryPage`

> 💡 **`pages.base_page` 是什么意思？**
> 点号相当于文件夹分隔符。`pages.base_page` = `pages` 文件夹下的 `base_page.py` 文件。

### 1.4 `__init__.py` 是干嘛的

项目里有 `config/__init__.py` 和 `pages/__init__.py`，**两个都是空文件**。

它的作用是告诉 Python："这个文件夹是一个**包**（package），可以被人 import"。
**你完全不用管它，知道它是空文件就行。**

### 1.5 一个反常识的写法：函数内部 import

```python
# pages/cart_page.py
def checkout(self):
    """进入结算流程第一步。这里延迟导入，避免与 checkout_page 循环引用。"""
    from pages.checkout_page import CheckoutInfoPage   # ← 写在函数里面！

    self.click(self.CHECKOUT_BUTTON)
    return CheckoutInfoPage(self.page)
```

通常 `import` 都写在文件开头，这里却写在函数里。原因注释里说了：**避免循环引用**。

> 循环引用 = A 文件 import B，B 文件又 import A，会死锁。
>
> **你只需要知道这是有意为之、不是写错了。** 平时写代码还是把 import 放开头。

---

## 第 2 章 · 变量与数据类型

### 2.1 变量就是"给值起个名字"

```python
# tests/test_cart.py
BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"
```

这两行定义了两个**模块级常量**（写在文件最外层，不属于任何函数）。约定俗成用**全大写**表示"这是个常量，不要改它"。

下面用例里就能直接用 `BACKPACK` 代表那个商品名 —— **改商品名时只改一处**。

### 2.2 本项目会用到的 5 种类型

| 类型 | 长什么样 | 项目里在哪 |
|---|---|---|
| 字符串 `str` | `"hello"` `'#user-name'` | 无处不在 |
| 整数 `int` | `1` `0` `5000` | 购物车数量 |
| 布尔 `bool` | `True` `False` | `is_visible()` 的返回值 |
| 列表 `list` | `["a", "b"]` | 商品名列表 |
| 对象 | `LoginPage(page)` | 页面对象 |

### 2.3 字符串：引号单双都行

```python
USERNAME_INPUT = "#user-name"          # 双引号
ERROR_MESSAGE = '[data-test="error"]'  # 单引号（因为里面已经有双引号了）
```

**规则**：字符串里面如果有双引号，外面就用单引号，反之亦然。完全等价，只是为了少转义。

### 2.4 类型转换

```python
# pages/inventory_page.py
def cart_count(self) -> int:
    badge = self.page.locator(self.CART_BADGE)
    if badge.count() == 0:
        return 0
    return int(badge.inner_text())      # ← 转换
```

`badge.inner_text()` 从网页上取回的角标文字是**字符串** `"1"`，而我们要的是**数字** 1，所以用 `int(...)` 转换。

> ⚠️ 这是自动化里非常常见的一步：**网页上的东西拿下来永远是字符串**，要比较数字就得转换。

### 2.5 列表

```python
# pages/inventory_page.py
def item_names(self) -> list[str]:
    return self.page.locator(self.ITEM_NAME).all_inner_texts()
```

`all_inner_texts()` 返回的是一个**列表**，比如 `["Sauce Labs Backpack", "Sauce Labs Bike Light", ...]`。

`list[str]` 表示"这是一个存放字符串的列表"（详见第 7 章）。

**判断某样东西在不在列表里，用 `in`**：

```python
# pages/cart_page.py
def contains(self, name: str) -> bool:
    return name in self.item_names()      # name 在不在这个列表里
```

### 2.6 字典（用得少，但要看懂）

```python
# tests/conftest.py
return {
    **browser_context_args,
    "viewport": {"width": 1440, "height": 900},
    "locale": "zh-CN",
    "timezone_id": "Asia/Shanghai",
}
```

这是**字典**（`{键: 值, 键: 值}`），类似其他语言的 Map / JSON 对象。

`**browser_context_args` 前面的两个星号表示"把另一个字典的内容**摊开**放进来"。

> 📌 **这一段你不需要会自己写**，知道它是在"配置浏览器参数"就够了。

---

## 第 3 章 · 字符串与 f-string

### 3.1 拼接字符串

```python
# pages/base_page.py
def by_test_id(self, test_id: str) -> Locator:
    return self.page.locator(f'[data-test="{test_id}"]')
```

`f'...'` 开头的字符串叫 **f-string**。它允许你在字符串里用 `{}` 直接嵌入变量。

假设 `test_id` 的值是 `"error"`，那 `f'[data-test="{test_id}"]'` 的结果就是：

```
[data-test="error"]
```

**f = format（格式化）**，项目里一共用了 5 处，都在拼定位符或拼提示信息。

### 3.2 断言失败信息里的 f-string

```python
# tests/test_login.py
assert expected_fragment.lower() in error.lower(), f"提示文案不符：{error}"
```

这句话的意思是：断言"期望文案在错误信息里"，**如果失败，就显示 `提示文案不符：<实际的错误信息>`**。

用 f-string 是为了**把真实的错误信息带进提示里**，方便你排查：

```
AssertionError: 提示文案不符：Epic sadface: Username and password do not match...
```

### 3.3 常用字符串方法

| 方法 | 作用 | 项目里的例子 |
|---|---|---|
| `.lower()` | 全部转小写 | `error.lower()` |
| `.strip()` | 去掉首尾空白 | `inner_text().strip()` |
| `.decode("utf-8")` | 字节转字符串 | `base64.b64encode(png).decode("utf-8")` |

**为什么老用 `.lower()`？** 因为网页文案的大小写可能变。把两边都转小写再比较，就不用担心 `"Locked out"` 还是 `"LOCKED OUT"`。

---

## 第 4 章 · 函数

### 4.1 定义函数

```python
def 函数名(参数1, 参数2):
    函数体
    return 返回值
```

### 4.2 最简单的情况：没有参数、没有返回值

```python
# pages/base_page.py
def click(self, selector: str) -> None:
    self.page.locator(selector).click()
```

`-> None` 表示**这个函数不返回任何东西**，它只是"执行一个动作"。

### 4.3 有参数

```python
# pages/login_page.py
def login(self, username: str, password: str) -> InventoryPage:
    self.fill(self.USERNAME_INPUT, username)
    self.fill(self.PASSWORD_INPUT, password)
    self.click(self.LOGIN_BUTTON)
    return InventoryPage(self.page)
```

调用时按顺序传值：

```python
login_page.login("standard_user", "secret_sauce")
```

### 4.4 有默认值的参数

```python
# pages/base_page.py
def wait_visible(self, selector: str, timeout: float = 5000) -> bool:
```

`timeout: float = 5000` 表示**这个参数可以不传，不传就是 5000**。

三种调用方式都合法：

```python
self.wait_visible(".item")              # timeout 用默认值 5000
self.wait_visible(".item", 10000)       # 传 10000
self.wait_visible(".item", timeout=300) # 指名道姓地传（推荐，可读性好）
```

**带默认值的参数必须放在不带默认值的后面。**

### 4.5 `return` 的两种含义

**含义一：把结果交出去**

```python
def cart_count(self) -> int:
    return 0                    # 返回数字 0
    ...
    return int(badge.inner_text())
```

> ⚠️ `return` 一旦执行，函数**立刻结束**。所以上面那个 `if badge.count() == 0: return 0` 之后的代码就不会跑了 —— 这正是我们想要的。

**含义二：把"下一个页面"交出去**（本项目最核心的用法）

```python
def login(self, username, password) -> InventoryPage:
    self.fill(...)
    self.click(...)
    return InventoryPage(self.page)     # ← 返回下一个页面对象
```

这样调用方就能**接着往下写**：

```python
inventory = login_page.login("standard_user", "secret_sauce")
inventory.add_to_cart("Sauce Labs Backpack")     # 直接操作登录后的页面
```

### 4.6 没有 `return` 就返回 `None`

```python
# pages/inventory_page.py
def add_to_cart(self, name: str) -> "InventoryPage":
    card = self.item_card(name)
    card.get_by_role("button", name="Add to cart").click()
    expect(card.get_by_role("button", name="Remove")).to_be_visible()
    return self                      # ← 这里有 return
```

---

## 第 5 章 · 类与对象（本项目最重要的一章）

**看不懂类，就看不懂 POM 分层。** 但好消息是：项目里的类都非常简单。

### 5.1 类是什么

**类 = 一组相关的"数据 + 动作"的打包。**

`LoginPage` 这个类，打包了：
- **数据**：这个页面的元素定位符（`USERNAME_INPUT = "#user-name"` 等）
- **动作**：在这个页面上能做的事（`login()`、`error_message()` 等）

### 5.2 定义一个类

```python
class LoginPage(BasePage):          # ← 括号里是"父类"，第 6 章讲
    """登录页。"""

    path = "/"                       # ← 类属性：本页面的路径
    USERNAME_INPUT = "#user-name"    # ← 类属性：元素定位符

    def login(self, username, password):   # ← 方法：能做的动作
        ...
```

### 5.3 `self` 到底是什么（初学者的头号困惑）

```python
def add_to_cart(self, name: str) -> "InventoryPage":
    card = self.item_card(name)          # 用 self 调用本类的另一个方法
    card.get_by_role("button", name="Add to cart").click()
    expect(...).to_be_visible()
    return self                          # 把"我自己"返回出去
```

**`self` 就是"我自己这个对象"。**

```python
inventory_page.add_to_cart("Sauce Labs Backpack")
```

Python 在背后偷偷做了一件事：把 `inventory_page` 这个对象，作为第一个参数传给了 `self`。

**所以 `self.item_card(name)` 的真实含义是：`inventory_page.item_card(name)`。**

> 💡 **记住三条就够了：**
> 1. 类里面的每个方法，**第一个参数永远是 `self`**
> 2. 想调用本类的其他方法，写 `self.方法名(...)`
> 3. 想读本类的属性，写 `self.属性名`
>
> 调用的时候**不用自己传 `self`**，Python 自动传。

### 5.4 `__init__` 是"创建对象时自动执行的方法"

```python
# pages/base_page.py
class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page          # ← 把传进来的 page 存到"我自己"身上
```

`__init__` 前后各两个下划线，是 Python 的固定写法，叫**构造方法**。

```python
LoginPage(page)
```

这一句执行时，Python 会自动：
1. 创建一个 `LoginPage` 对象
2. 把 `page` 传进去执行 `__init__`
3. 于是这个对象身上就有了 `self.page`

**这就是为什么后面每个方法里都能用 `self.page`** —— 它在创建对象时就被存进去了。

### 5.5 类属性 vs 实例属性

```python
class LoginPage(BasePage):
    path = "/"                       # 类属性：写在方法外面，所有实例共享
    USERNAME_INPUT = "#user-name"

    def __init__(self, page):
        self.page = page             # 实例属性：写在 __init__ 里，每个对象各有一份
```

| | 写在哪 | 特点 | 项目里的例子 |
|---|---|---|---|
| 类属性 | 方法外面 | 所有对象共用一份 | `path`、`USERNAME_INPUT` |
| 实例属性 | `__init__` 里 | 每个对象各有一份 | `self.page` |

**为什么定位符用类属性？** 因为它们对所有 `LoginPage` 对象都一样，没必要每个对象存一份。

### 5.6 为什么老看到 `return self`

```python
def add_to_cart(self, name: str) -> "InventoryPage":
    ...
    return self
```

返回"我自己"，是为了支持**链式调用**：

```python
inventory_page.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)
```

拆开看其实是：

```python
inventory_page.add_to_cart(BACKPACK)      # 返回 inventory_page 自己
inventory_page.add_to_cart(BIKE_LIGHT)    # 所以可以接着再调一次
```

**链式调用的前提就是：前一个方法把"自己"返回出来。**

---

## 第 6 章 · 继承

### 6.1 项目里的继承关系

```
        BasePage  （基类：所有页面共用的能力）
            ↑
    ┌───────┼───────┬────────────┐
LoginPage  InventoryPage  CartPage  CheckoutInfoPage
```

写法就是类名后面加括号：

```python
class LoginPage(BasePage):
```

读作：**"LoginPage 继承自 BasePage"**。

### 6.2 继承有什么用

`BasePage` 里定义了这些方法：

```python
class BasePage:
    def open(self): ...
    def click(self, selector): ...
    def fill(self, selector, value): ...
    def is_visible(self, selector): ...
    def wait_visible(self, selector, timeout=5000): ...
    def expect_url_contains(self, fragment): ...
```

`LoginPage` 里**一行都没写**这些，但可以直接用：

```python
login_page.fill(...)          # 来自 BasePage
login_page.click(...)         # 来自 BasePage
login_page.expect_url_contains("/cart.html")   # 来自 BasePage
```

**这就是继承的价值：公共能力写在父类，子类白捡。**

> 💡 看到 `self.某个方法()`，如果在本类里找不到定义，**就去父类 `BasePage` 里找**。

### 6.3 子类"改写"父类的方法

```python
# pages/login_page.py
class LoginPage(BasePage):
    def open(self) -> "LoginPage":        # ← 父类里也有 open()
        self.page.goto(self.path)
        return self
```

父类的 `open()` 返回类型是 `BasePage`，子类改成返回 `LoginPage`。

这叫**方法重写（override）**：名字一样，子类的版本会盖住父类的。

**为什么要重写？** 为了让链式调用时类型更准确：

```python
login_page = LoginPage(page).open()    # open() 返回 LoginPage，能继续调 .login()
inventory  = login_page.login(...)     # login() 返回 InventoryPage
```

---

## 第 7 章 · 类型标注（那些 `: str` 和 `-> None`）

项目里有 **46 处 `->`** 和 **33 处参数标注**，到处都能看到。它们是干嘛的？

### 7.1 它们**不影响运行**

```python
def login(self, username: str, password: str) -> InventoryPage:
```

- `username: str` = 提示"username 应该是个字符串"
- `-> InventoryPage` = 提示"这个函数会返回一个 InventoryPage 对象"

**这些只是"注释"，Python 运行时不会强制检查。** 写错了程序照样跑，只是起不到提示作用。

**那为什么还要写？** 因为编辑器（VS Code）能靠它给你**自动补全和报错提示**：

```python
inventory = login_page.login(u, p)
inventory.          # ← 敲个点，编辑器会自动列出 InventoryPage 的所有方法
```

### 7.2 常见的几种标注

| 写法 | 含义 |
|---|---|
| `name: str` | 参数 name 是字符串 |
| `timeout: float = 5000` | 浮点数，默认 5000 |
| `-> None` | 没有返回值 |
| `-> bool` | 返回 True 或 False |
| `-> int` | 返回整数 |
| `-> list[str]` | 返回一个字符串列表 |
| `-> InventoryPage` | 返回一个页面对象 |

### 7.3 为什么有时要加引号

```python
def open(self) -> "LoginPage":        # ← 有引号
def login(self) -> InventoryPage:     # ← 没有引号
```

**加引号是因为"这个名字还没定义"。**

写 `LoginPage` 这个类的时候，`InventoryPage` 已经被 import 进来了，可以直接写。
但 `LoginPage` **自己**在定义中，还不能引用自己，所以要写成字符串 `"LoginPage"`。

> 💡 **你不用会判断什么时候加引号。** 看到引号，知道是同一回事就行。

### 7.4 文件开头的 `from __future__ import annotations`

9 个文件里都有这一行。它是**为了让上面那些类型标注更省事**的（比如 `list[str]` 在旧版本 Python 里要写成 `List[str]`）。

**你完全不用管它，知道它是"让类型标注写法更现代"就行。**

---

## 第 8 章 · 装饰器（`@` 开头的东西）

项目里有 **18 处 `@`**，它们长这样：

```python
@dataclass(frozen=True)          # config/settings.py
@property                        # config/settings.py
@pytest.fixture                # tests/conftest.py
@dataclass / @pytest.mark.smoke
@pytest.mark.parametrize(...)
```

### 8.1 一句话理解装饰器

**装饰器 = 给下面那个函数/类"贴个标签"，让框架知道该怎么对待它。**

它不是 Python 语法难点，是**框架的约定**。你只要认识几个常用的就行。

### 8.2 项目里出现的 5 个装饰器

| 装饰器 | 含义 | 你要做什么 |
|---|---|---|
| `@pytest.fixture` | 标记"这是个测试装置" | 用例里写参数名就能用（见下） |
| `@pytest.mark.smoke` | 给用例贴"冒烟"标签 | 可以用 `-m smoke` 只跑它 |
| `@pytest.mark.regression` | 贴"回归"标签 | 同上 |
| `@pytest.mark.parametrize(...)` | 一条用例跑多组数据 | 看懂参数怎么对应 |
| `@dataclass` / `@property` | 简化类的写法 | **不用管**，框架代码里才会出现 |

### 8.3 `@pytest.mark.parametrize` 怎么看（重点）

```python
@pytest.mark.parametrize(
    ("username", "password", "expected_fragment"),      # ← 参数名，逗号分隔
    [
        (settings.standard_user, "wrong_password", "do not match"),      # 第 1 组
        ("", settings.password, "Username is required"),                 # 第 2 组
        (settings.standard_user, "", "Password is required"),            # 第 3 组
    ],
    ids=["密码错误", "用户名称为空", "密码为空"],           # ← 每组的显示名
)
def test_login_failure_shows_message(login_page, username, password, expected_fragment):
```

**读法**：上面那个元组里的三个名字，和下面函数括号里的三个参数，**一一对应**。

所以这条用例会**跑 3 遍**：

| 第几遍 | username | password | expected_fragment |
|---|---|---|---|
| 1（密码错误） | standard_user | wrong_password | do not match |
| 2（用户名称为空） | （空） | secret_sauce | Username is required |
| 3（密码为空） | standard_user | （空） | Password is required |

所以在测试报告里你会看到**一条用例展开成 3 条**：

```
test_login_failure_shows_message[密码错误]
test_login_failure_shows_message[用户名称为空]
test_login_failure_shows_message[密码为空]
```

> 💡 这就是为什么 `test_login.py` 里只有 **3 个函数**，跑出来却是 **5 条用例**。

### 8.4 `@pytest.fixture` —— 用例参数的来源

```python
# tests/conftest.py
@pytest.fixture
def login_page(page) -> LoginPage:
    """打开登录页。"""
    return LoginPage(page).open()
```

用例里写了 `login_page` 这个参数：

```python
def test_standard_user_login_success(login_page):
    inventory = login_page.login(settings.standard_user, settings.password)
```

**关键是：这个参数不用你传值。**

pytest 看到用例需要 `login_page`，就会**自动去找同名的 fixture 并执行它**，把返回值塞进来。

所以这条用例开始执行前，pytest 已经帮你：
1. 启动了浏览器
2. 打开了登录页
3. 把 `LoginPage` 对象交给了 `login_page` 这个变量

**这就是"用例里只写业务，不写准备工作"的实现方式。**

项目里的 fixture：

| fixture 名 | 做了什么 | 谁在用 |
|---|---|---|
| `page` | 启动浏览器、打开新页面（Playwright 自带） | 被下面两个依赖 |
| `login_page` | 打开登录页 | `test_login.py` |
| `inventory_page` | 登录好、停在商品页 | `test_cart.py` |
| `base_url` | 提供被测地址 | 框架内部 |

---

## 第 9 章 · if / for / try

项目里这三种控制结构很少：**3 处 if、1 处 for、3 处 try**。所以很快。

### 9.1 `if` 就是"如果……就……"

```python
# pages/inventory_page.py
def cart_count(self) -> int:
    badge = self.page.locator(self.CART_BADGE)
    if badge.count() == 0:          # 如果角标不存在
        return 0                    # 就返回 0
    return int(badge.inner_text())  # 否则返回角标上的数字
```

**注意缩进！** Python 靠缩进划分代码块，不用大括号。

```python
if 条件:
    条件成立时执行的代码       # ← 必须缩进
其他代码                       # ← 不缩进，就不属于 if
```

`==` 是"等于"（比较），`=` 是"赋值"。**这两个千万别写混。**

### 9.2 `for` 就是"挨个来一遍"

项目里只有 1 处：

```python
# pages/inventory_page.py
def add_all_to_cart(self) -> "InventoryPage":
    for name in self.item_names():     # 把商品名挨个取出来
        self.add_to_cart(name)         # 每个都加进购物车
    return self
```

读作：**"对于 item_names() 里的每一个 name，都执行一次 add_to_cart(name)"**。

### 9.3 `try / except` 就是"试试看，出错也别崩"

```python
# pages/base_page.py
def wait_visible(self, selector: str, timeout: float = 5000) -> bool:
    try:
        expect(self.page.locator(selector)).to_be_visible(timeout=timeout)
    except AssertionError:      # 如果上面那句失败了
        return False            # 就返回 False，而不是让程序崩溃
    return True
```

**为什么需要它？** `expect(...)` 失败时会**抛出异常**，异常会中断整个测试。但这个方法的设计意图是"**返回 True/False 让调用方自己判断**"，所以要把异常接住。

```python
try:
    可能出错的代码
except 某种错误:
    出错时怎么办
```

### 9.4 `yield`（只出现 1 次，可以跳过）

```python
# tests/conftest.py
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield           # ← 这里
    report = outcome.get_result()
    ...
```

这是 pytest 的**钩子函数**（框架内部机制），用来实现"用例失败时自动截图"。

**你可以完全跳过它**，只要知道：`conftest.py` 里那一段是**框架代码**，负责失败截图，你不需要动。

---

## 第 10 章 · 实战：把一条用例逐行读一遍

现在把所有知识串起来。看这条端到端用例：

```python
@pytest.mark.smoke
def test_full_checkout_flow(inventory_page):
    """端到端主流程：加购 → 购物车 → 填信息 → 下单成功。"""
    inventory_page.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)

    complete = (
        inventory_page.open_cart()
        .checkout()
        .fill_info("测试", "工程师", "200000")
        .finish()
    )

    assert complete.is_success(), "下单后没有出现成功页"
    assert "thank you" in complete.success_message().lower()
```

### 逐行拆解

**第 1 行 `@pytest.mark.smoke`**
装饰器，给这条用例贴"冒烟"标签。跑 `pytest -m smoke` 时会被选中。

**第 2 行 `def test_full_checkout_flow(inventory_page):`**
定义用例。函数名必须以 `test_` 开头，否则 pytest 不会认它是用例。

`inventory_page` 这个参数不用传 —— pytest 会自动执行同名的 fixture（打开浏览器 + 登录 + 停在商品页）。

**第 3 行 `"""..."""`**
文档字符串。三引号包起来的多行文本，纯粹给人看的，可以在报告里显示。

**第 4 行 `inventory_page.add_to_cart(BACKPACK).add_to_cart(BIKE_LIGHT)`**
链式调用。拆开是：

```python
inventory_page.add_to_cart("Sauce Labs Backpack")   # 返回 self（还是这个页面）
inventory_page.add_to_cart("Sauce Labs Bike Light") # 所以能接着调
```

`BACKPACK` 是文件开头定义的常量。

**第 6~11 行 `complete = (...)`**

```python
complete = (
    inventory_page.open_cart()              # ① 点购物车图标 → 返回 CartPage
    .checkout()                             # ② 点结算       → 返回 CheckoutInfoPage
    .fill_info("测试", "工程师", "200000")   # ③ 填姓名邮编   → 返回 CheckoutOverviewPage
    .finish()                               # ④ 点完成       → 返回 CheckoutCompletePage
)
```

外面那对圆括号只是为了**让长表达式能换行**，没有别的含义（Python 里括号内的内容可以自由换行）。

每一步的返回值是**下一个页面对象**，所以能一直点下去。最后 `complete` 拿到的是**下单成功页**。

**第 13 行 `assert complete.is_success(), "下单后没有出现成功页"`**

`assert 条件, "提示信息"` —— 如果条件为 False，测试失败并显示提示信息。

`is_success()` 定义在 `CheckoutCompletePage` 里，它内部会**等待成功页出现**（最多 5 秒），返回 True/False。

**第 14 行 `assert "thank you" in complete.success_message().lower()`**

拆解：

```python
complete.success_message()      # 取到成功页的标题文字，如 "Thank you for your order!"
                .lower()        # 转小写 → "thank you for your order!"
"thank you" in ...              # 判断 "thank you" 在不在这段文字里
```

### 这条用例为什么这么短？

因为它把细节全藏在 `pages/` 里了。对比一下如果不用 POM 要写多少：

```python
# 假如没有 POM（示意，不是项目里的代码）
page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
page.wait_for_selector('[data-test="remove-sauce-labs-backpack"]')
page.locator('[data-test="shopping-cart-link"]').click()
page.wait_for_url("**/cart.html")
page.locator('[data-test="checkout"]').click()
page.wait_for_url("**/checkout-step-one.html")
page.locator('[data-test="firstName"]').fill("测试")
page.locator('[data-test="lastName"]').fill("工程师")
page.locator('[data-test="postalCode"]').fill("200000")
page.locator('[data-test="continue"]').click()
page.locator('[data-test="finish"]').click()
page.wait_for_selector('[data-test="complete-header"]')
```

**用例从"一堆元素操作"变成"一句业务描述"，这就是分层的意义。**
页面改版时，上面那种写法要改 12 行；分层写法只改 `pages/` 里的定位符，用例一行不动。

---

## 第 11 章 · 接下来怎么练

### 阶段一：只改不改结构（1~2 天）

打开 `tests/test_cart.py`，做这些改动，然后跑 `uv run pytest` 看结果：

1. **改断言的值** —— 把 `assert inventory_page.cart_count() == 1` 改成 `== 2`，看它怎么失败
2. **看失败信息** —— 故意改错，观察 pytest 报的错长什么样
3. **加一条断言** —— 在现有用例里多断言一个商品名

> 这一步的目的：**建立"改代码 → 跑测试 → 看结果"的手感**。

### 阶段二：加一条新用例（3~5 天）

在 `test_cart.py` 里加：

```python
@pytest.mark.regression
def test_add_then_remove_multiple_times(inventory_page):
    """反复加购和移除，角标应该正确变化。"""
    inventory_page.add_to_cart(BACKPACK)
    inventory_page.remove_from_cart(BACKPACK)
    inventory_page.add_to_cart(BACKPACK)

    assert inventory_page.cart_count() == 1
```

用到的 `add_to_cart` / `remove_from_cart` / `cart_count` 都**已经存在**，你只是重新组合它们。

### 阶段三：模仿着写新用例（1~2 周）

参考 `test_login.py` 的 `parametrize` 写法，自己写一条参数化用例。

### 遇到不会的时候

| 想干什么 | 怎么查 |
|---|---|
| 某个方法能传什么参数 | 在 VS Code 里把鼠标悬停在方法名上 |
| 这个类还有哪些方法 | 敲 `对象名.` 看自动补全 |
| 某个方法是哪来的 | 在本类里搜不到 → 去 `pages/base_page.py` 找 |
| 这个 fixture 做了什么 | 去 `tests/conftest.py` 找同名函数 |

**别去背语法。** 你有 400 行代码可以随时查，比背规则管用得多。

---

## 附录 A · 速查表（读代码时对照用）

| 你会看到 | 含义 |
|---|---|
| `def foo(a, b):` | 定义一个函数 |
| `def foo(a, b=1):` | b 有默认值，可不传 |
| `class Foo(Bar):` | 定义类 Foo，继承自 Bar |
| `def __init__(self, x):` | 创建对象时自动执行 |
| `self.x = x` | 把值存到对象身上 |
| `self.foo()` | 调用本类（或父类）的另一个方法 |
| `return self` | 返回自己，支持链式调用 |
| `return Foo(...)` | 返回下一个页面对象 |
| `-> None` | 不返回东西 |
| `-> "Foo"` | 返回 Foo 类型（引号是因为还没定义完） |
| `a: str` | 提示 a 是字符串（不影响运行） |
| `f"文本{变量}"` | f-string，把变量嵌进字符串 |
| `x in y` | x 在不在 y 里面 |
| `a == b` | 判断相等 |
| `a = b` | 赋值 |
| `int(x)` | 把 x 转成整数 |
| `.lower()` | 转小写 |
| `@pytest.mark.smoke` | 给用例贴标签 |
| `@pytest.fixture` | 定义测试装置，用例写参数名即可用 |
| `@pytest.mark.parametrize` | 一条用例跑多组数据 |
| `assert 条件, "提示"` | 断言，失败时显示提示 |
| `try: ... except X: ...` | 试试看，出错时走 except |
| `if 条件:` | 如果……就……（记得缩进） |
| `for x in 列表:` | 挨个来一遍（记得缩进） |

## 附录 B · 三个最容易混的点

**① `=` 和 `==`**

```python
x = 5        # 赋值：把 5 存进 x
x == 5       # 比较：x 等于 5 吗？（返回 True/False）
```

**② 缩进必须一致**

```python
def foo(self):
    if True:
        print("在 if 里面")     # 缩进 4 个空格
    print("在 if 外面")         # 缩进 4 个空格，但不属于 if
```

同一个块里缩进必须一样。**建议统一用 4 个空格**，VS Code 会自动帮你对齐。

**③ `self` 只在类里面用**

```python
class LoginPage(BasePage):
    def login(self, ...):       # ← 括号里有 self
        self.fill(...)          # ← 用 self. 调用

def test_something(login_page): # ← 普通函数，没有 self
    login_page.login(...)       # ← 直接用参数名
```

**类的方法有 `self`，普通函数（比如用例）没有。**
