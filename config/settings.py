"""测试环境配置。

所有可变的东西（地址、账号、超时）都集中在这里，从 .env 读取，
用例和 Page Object 里不允许出现硬编码的 URL 或密码。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# 项目根目录（config/ 的上一级）
ROOT_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT_DIR / "reports" / "artifacts"

# 如果存在 .env 就加载，不存在则用下面的默认值（开箱即用）
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    """当前运行环境的配置。切换环境时改 .env 即可，不用动代码。"""

    base_url: str = os.getenv("BASE_URL", "https://www.saucedemo.com")

    # 测试账号
    standard_user: str = os.getenv("STANDARD_USER", "standard_user")
    locked_user: str = os.getenv("LOCKED_USER", "locked_out_user")
    password: str = os.getenv("PASSWORD", "secret_sauce")

    @property
    def is_remote(self) -> bool:
        """是否跑在非本地环境下（CI 上通常为 True）。"""
        return bool(os.getenv("CI"))


settings = Settings()
