"""运行日志：一轮测试一个文件，落在 logs/ 下，文件名带时间戳。

和 allure 报告是两回事，各管一头，不互相替代：

  - allure 报告是给「看」的 —— 用例树、通过率、失败截图，适合当交付物
  - 这个文件是给「查」的 —— 页面跳转、接口调用、JS 报错、用例结局按时间
    顺序排下来，出问题时对着时间轴就能还原这一轮到底发生了什么；
    allure 里翻 121 条用例找一次没发出去的请求，不如直接在这个文件里搜。

**必须用独立的 logger（propagate=False）。** 挂到 root logger 上的话，
会被 pytest 自带的 logging 插件接管、重定向进它自己的 caplog，
文件里反而什么都看不到 —— 这是 api-testing 踩过的坑，不是理论风险。
"""

import logging
from datetime import datetime
from pathlib import Path

from config.settings import LOGS_DIR

_LOGGER_NAME = "sep-web"
_log_path: Path | None = None


def setup() -> Path:
    """建好本轮日志文件并返回路径。重复调用返回同一个文件，不会开第二个。"""
    global _log_path
    if _log_path is not None:
        return _log_path

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    _log_path = LOGS_DIR / f"run_{datetime.now():%Y%m%d_%H%M%S}.log"

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False        # 见模块文档：不走 root，否则被 pytest 吞掉
    logger.handlers.clear()         # 重跑同一进程时不挂第二个 handler，免得一行写两遍

    handler = logging.FileHandler(_log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(handler)
    return _log_path


def get() -> logging.Logger:
    """拿到 logger。setup() 之前调也安全 —— 没有 handler，写进去等于丢弃。"""
    return logging.getLogger(_LOGGER_NAME)


def path() -> Path | None:
    """本轮日志文件的路径；还没 setup 时返回 None。"""
    return _log_path
