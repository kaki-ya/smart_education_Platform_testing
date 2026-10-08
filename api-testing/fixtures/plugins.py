"""把 fixtures/ 接成 pytest fixture，外加运行日志的几个 hook。

本模块通过根 conftest.py 的 pytest_plugins 挂载，所以这里的 hook
和 fixture 都是活的。
"""

import platform
import shutil
import sys
import time

import pytest

from common import logger
from common.request_util import ApiClient, ApiError
from config.accounts import ACCOUNTS, ANONYMOUS
from config.settings import ALLURE_REPORT_DIR, BASE_URL
from fixtures.account import AccountBootstrapError, bootstrap


@pytest.fixture(scope="session")
def backend_alive(anon_client):
    """跑之前先确认后端在。

    不做这一步的话，后端没起时 182 条会各自报一次 ConnectionError，
    真正的原因被埋在 182 个 traceback 里。
    """
    try:
        anon_client.get("/api/course/list", params={"page": 1, "size": 1},
                        label="后端探活")
    except ApiError as exc:
        pytest.exit(f"后端连不上，用例没法跑：\n{exc}", returncode=2)


@pytest.fixture(scope="session")
def anon_client():
    """不带 token 的客户端。role: none 的用例走它。"""
    client = ApiClient(token=None)
    yield client
    client.close()


@pytest.fixture(scope="session")
def tokens(anon_client, backend_alive):
    """登录所有测试账号，返回 {用户名: token}。

    session 级：182 条用例不该登 182 次。
    """
    try:
        return bootstrap(anon_client)
    except AccountBootstrapError as exc:
        pytest.exit(f"测试账号引导失败，用例没法跑：\n{exc}", returncode=2)


@pytest.fixture(scope="session")
def client_for(tokens):
    """role 字符串 → 对应身份的 ApiClient。

    显式声明依赖 tokens，不指望 pytest 的 fixture 解析顺序恰好正确。

    每个 role 一个独立实例。共用 Session 并在上面塞 Authorization 头的话，
    匿名用例会被前一条的登录态污染：期望的 message 是「未登录」，
    实际会变成「登录已过期」，报出来的原因和真实原因完全不是一回事。
    """
    clients = {role: ApiClient(token=tokens[account.username])
               for role, account in ACCOUNTS.items()}
    clients[ANONYMOUS] = ApiClient(token=None)

    def _pick(role: str) -> ApiClient:
        if role not in clients:
            pytest.fail(
                f"用例里写了 role={role!r}，但没有对应的账号。\n"
                f"  可选值：{'、'.join(sorted(clients))}\n"
                f"  要加新身份请改 config/accounts.py"
            )
        return clients[role]

    yield _pick

    for client in clients.values():
        client.close()


# --------------------------------------------------------------------------
# 运行日志（logs/run_<时间戳>.log）
#
# 写成 hook 而不是 fixture：hook 在 session 一开始就触发，fixture 要等第一条
# 用例才执行。后端连不上时用例一条都没跑，日志反而不会生成 ——
# 而那恰恰是最需要日志的时候。
# --------------------------------------------------------------------------

_STATS: dict[str, int] = {}
_STARTED = {"at": 0.0}


def _clear_stale_report(log) -> None:
    """删掉上一轮生成的 allure HTML 报告。

    reports/allure-results/ 由 pytest.ini 的 --clean-alluredir 每轮清掉，
    但生成出来的 reports/allure-report/ 没人管。只跑 pytest 不出报告的话，
    那个目录里会一直躺着上一轮的 index.html，浏览器打开看着就像本轮结果 ——
    所以在这里抹掉。**没有报告是诚实的，过期的报告是误导。**

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
    log.info("后端地址：%s", BASE_URL)
    log.info("运行环境：Python %s / pytest %s / %s",
             platform.python_version(), pytest.__version__, platform.platform())
    log.info("命令行：pytest %s", " ".join(sys.argv[1:]) or "（无额外参数）")
    log.info("=" * 72)


def pytest_runtest_logreport(report):
    """每条用例的结局写一行。

    request_util 记的是「发了什么、回了什么」，这里记的是「判成什么」，
    两半拼起来才是完整的一轮。
    """
    if report.when == "call":
        _STATS[report.outcome] = _STATS.get(report.outcome, 0) + 1
        mark = "通过" if report.passed else "失败"
    elif report.failed:
        # fixture 挂了，用例体根本没跑起来。这种要和「断言失败」分开写，
        # 否则看日志的人会以为是接口的问题。
        _STATS["error"] = _STATS.get("error", 0) + 1
        mark = f"{report.when} 阶段出错"
    else:
        return                                    # setup / teardown 正常，不记

    log = logger.get()
    log.info("[%s] %s（%.0fms）", _case_id(report), mark, report.duration * 1000)

    if not report.failed:
        return
    # 只写失败的「位置 + 原因」，不用 longreprtext：那里面会把整个被调用函数的
    # 源码也抄一遍（verify() 有二十多行），一次失败就淹掉半屏，而有用的一句没有。
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
    """'testcases/test_01_user.py::test_user[TC_user_013]' → 'TC_user_013'。"""
    nodeid = report.nodeid
    if "[" in nodeid:
        return nodeid.rsplit("[", 1)[1].rstrip("]")
    return nodeid
