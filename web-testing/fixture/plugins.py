"""运行日志的 hook，外加给 page 挂监听的 watch()。

写成 hook 而不是 fixture：hook 在 session 一开始就触发，fixture 要等第一条
用例才执行。前后端没起、用例一条都没跑的时候，恰恰最需要日志 ——
而那时 fixture 根本不会被执行。

web 测试比接口测试多一层网络，所以日志比 api-testing 那边多记两样：
  接口调用（xhr/fetch）—— 同一条断言失败，「后端返回 500」和「前端压根没发
                          请求」是两种完全不同的原因，不看请求分不清；
  前端 JS 报错       —— 页面白屏、按钮没反应，原因通常都在这。
静态资源（js/css/图片）不记：一屏几十条，只会把有用的淹掉。
"""

import platform
import re
import shutil
import sys
import time

import pytest

from common import logger
from config.settings import ALLURE_REPORT_DIR, API_BASE_URL, BASE_URL

# 只记接口调用，不记静态资源
_API_TYPES = ("xhr", "fetch")

# 响应体原样落盘会把密码哈希也抄进日志，纯属噪音，抹掉
_REDACT = re.compile(r'"password"\s*:\s*"[^"]*"')


# ------------------------------------------------------------------ 页面监听

def _short(url: str) -> str:
    """http://localhost:5173/api/course/list → /api/course/list，一行放得下。"""
    for prefix in (API_BASE_URL, BASE_URL.rstrip("/")):
        if url.startswith(prefix):
            return url[len(prefix):] or "/"
    return url


def _body(response):
    """尽量读一眼响应体 —— 报错原因（「原密码错误」之类）就在里面。

    读不出来（二进制、连接已关）就返回 None，绝不因为记日志把用例带崩。
    """
    try:
        text = response.text()
    except Exception:
        return None
    if not text:
        return None
    text = _REDACT.sub('"password":"***"', text)
    text = " ".join(text.split())          # 压成一行，别让 JSON 撑开几十行
    return text[:300] + ("…" if len(text) > 300 else "")


def watch(page, who: str = "") -> None:
    """给一个 page 挂上监听，把它这轮在页面上干的事写进运行日志。

    who 是给人看的标签（比如学生账号名），多角色同时跑时分得清是谁。
    """
    log = logger.get()
    tag = f"[{who}] " if who else ""
    pending: dict = {}
    seen = {"url": None}

    def on_request(request):
        if request.resource_type in _API_TYPES:
            pending[request] = time.perf_counter()

    def on_response(response):
        request = response.request
        if request.resource_type not in _API_TYPES:
            return
        started = pending.pop(request, None)
        cost = f"{(time.perf_counter() - started) * 1000:.0f}ms" if started else "?"
        # 先把响应体读完再落盘：读的过程要让出控制权，别的请求的 handler
        # 会趁机插进来，两行「→ / 返回」就被拆散了，对着日志得反应半天。
        body = _body(response)
        log.info("%s  → %s %s  %s  %s",
                 tag, request.method, _short(response.url), response.status, cost)
        if body:
            log.info("%s    返回 %s", tag, body)

    def on_navigated(frame):
        # 子 iframe 的跳转不记，只记主框架 —— 那才是用例真的换页了
        if frame != page.main_frame:
            return
        url = _short(frame.url)
        # 同一个地址会连着触发好几次（about:blank → 目标页 → history 回填），
        # 只记第一次，否则一次加购能刷出三行一样的「跳转 /course/2」
        if url == seen["url"]:
            return
        seen["url"] = url
        log.info("%s  ⇢ 跳转 %s", tag, url)

    def on_pageerror(exc):
        log.info("%s  ⚠ 前端 JS 报错：%s", tag, exc)

    page.on("request", on_request)
    page.on("response", on_response)
    page.on("framenavigated", on_navigated)
    page.on("pageerror", on_pageerror)


# ---------------------------------------------------------------------- hook

_STATS: dict = {}
_STARTED = {"at": 0.0}


def _clear_stale_report(log) -> None:
    """删掉上一轮生成的 allure HTML 报告。

    reports/allure-results/ 由 pytest.ini 的 --clean-alluredir 每轮清掉，
    但生成出来的 reports/allure-report/ 没人管。只跑 pytest 不出报告的话，
    那个目录里会一直躺着上一轮的 index.html，浏览器打开看着就像本轮结果。
    **没有报告是诚实的，过期的报告是误导。**

    删不掉也不该让整轮测试挂掉（比如文件被浏览器占着），记一行接着跑。
    """
    if not ALLURE_REPORT_DIR.exists():
        return
    try:
        shutil.rmtree(ALLURE_REPORT_DIR)
    except OSError as exc:
        log.warning("清不掉上一轮的 allure 报告（%s）：%s", ALLURE_REPORT_DIR, exc)
        return
    log.info("已清除上一轮的 allure 报告：%s", ALLURE_REPORT_DIR)


def pytest_configure(config):
    path = logger.setup()
    log = logger.get()
    _STARTED["at"] = time.perf_counter()

    _clear_stale_report(log)

    log.info("=" * 72)
    log.info("本轮测试开始")
    log.info("日志文件：%s", path)
    log.info("前端地址：%s（接口经 vite proxy 转到 %s）", BASE_URL, API_BASE_URL)
    log.info("运行环境：Python %s / pytest %s / %s",
             platform.python_version(), pytest.__version__, platform.platform())
    log.info("命令行：pytest %s", " ".join(sys.argv[1:]) or "（无额外参数）")
    log.info("=" * 72)


def pytest_runtest_logreport(report):
    """每条用例的结局写一行。

    watch() 记的是「页面上发生了什么」，这里记的是「判成什么」，
    两半拼起来才是完整的一轮。
    """
    if report.when == "call":
        _STATS[report.outcome] = _STATS.get(report.outcome, 0) + 1
        mark = "通过" if report.passed else "失败"
    elif report.failed:
        # fixture 挂了，用例体根本没跑起来。这种要和「断言失败」分开写，
        # 否则看日志的人会以为是页面本身的问题。
        _STATS["error"] = _STATS.get("error", 0) + 1
        mark = f"{report.when} 阶段出错"
    else:
        return                                  # setup / teardown 正常，不记

    log = logger.get()
    log.info("[%s] %s（%.0fms）", _case_id(report), mark, report.duration * 1000)

    if not report.failed:
        return
    # 只写失败的「位置 + 原因」，不用 longreprtext：它会把整个被调用函数的
    # 源码也抄一遍，一次失败就淹掉半屏，有用的却只有一句。
    crash = getattr(report.longrepr, "reprcrash", None)
    if crash is None:
        for line in report.longreprtext.splitlines():
            log.info("        %s", line)
        return
    log.info("        位置：%s:%s", crash.path, crash.lineno)
    for line in str(crash.message).splitlines():
        log.info("        %s", line)


def pytest_sessionfinish(session, exitstatus):
    log = logger.get()
    log.info("-" * 72)
    log.info("本轮结束：共 %d 条，通过 %d，失败 %d，出错 %d，耗时 %.2fs",
             sum(_STATS.values()),
             _STATS.get("passed", 0), _STATS.get("failed", 0),
             _STATS.get("error", 0),
             time.perf_counter() - _STARTED["at"])
    log.info("日志文件：%s", logger.path())
    log.info("=" * 72)


def _case_id(report) -> str:
    """'testcases/test_05_cart_order.py::test_WEB_TC_062_xxx[chromium]' → 'test_WEB_TC_062_xxx'。"""
    return report.nodeid.split("::")[-1].split("[")[0]
