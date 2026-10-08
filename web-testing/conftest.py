import allure
import pytest
from playwright.sync_api import Page

from common import logger
from config.settings import BASE_URL, HEADLESS, SLOW_MO

# 顺序有讲究：session / login 会 import cleanup 和 plugins（登记一次性账号、
# 给 page 挂监听），被 import 的必须先注册成插件，否则 pytest 会警告
# 「Module already imported so cannot be rewritten」。
# 反过来 plugins 和 cleanup 谁都不 import fixture 里的东西，放最前面就是安全的。
pytest_plugins = ["fixture.cleanup", "fixture.plugins", "fixture.login", "fixture.session"]


@pytest.fixture(scope="session")
def base_url():
    """pytest-base-url 的 page fixture 用它做相对跳转。

    直接读 settings，避免同一份地址在 pytest.ini 和 settings.py 里写两遍。
    """
    return BASE_URL


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """有头/无头、慢放统一看 config/settings.py 的 HEADLESS / SLOW_MO 两行。

    pytest-playwright 只在命令行真给了 --headed / --slowmo 时才往这个字典里放键，
    没给就不放。所以用 setdefault：命令行表态了听命令行的，没表态才回落到 config。
    这样平时改配置那两行就够，`run.py --headed` 还能临时盖过一次。
    """
    args = dict(browser_type_launch_args)
    args.setdefault("headless", HEADLESS)
    if SLOW_MO:
        args.setdefault("slow_mo", SLOW_MO)
    return args


# ------------------------------------------------------ 失败现场（给报告看）

def _page_of(item):
    """从这条用例已经解析出来的 fixture 里挑出那个 Page。

    不按名字找：student_page / admin_page / fresh_student_page / guest_page 都是
    Page，isinstance 认得出，也就不用给每条用例多挂一个参数。
    """
    for value in item.funcargs.values():
        if isinstance(value, Page):
            return value
    return None


def _attach(name, produce, kind=allure.attachment_type.TEXT):
    """读一次现场并挂进报告；读不到就算了，不能掩盖原始失败。"""
    try:
        body = produce()
        allure.attach(body if body is not None else "(空)", name, kind)
    except Exception:
        pass


def _log_scene(page):
    """失败现场在运行日志里也留一行 —— 翻 logs/ 的时候不用再回头开报告。"""
    try:
        logger.get().info("        失败时页面：%s", page.url)
        toasts = page.locator(".toast").all_inner_texts()
        if toasts:
            logger.get().info("        屏幕上的 toast：%s", " / ".join(toasts))
    except Exception:
        pass


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    """失败时把「当时屏幕上是什么」一起写进 allure。

    报告里默认只有一行 assert 0 == 1，看的人只能回去翻代码猜是哪一步断的、
    页面到底渲染成什么样。这里在失败当场补四样 —— 整页截图、页面地址、
    屏幕上的 toast、页面正文 —— 报告里点开就能看到现场，不用重跑一遍。

    截图由这里自己截（full_page），所以 pytest.ini 里不用再开
    --screenshot，否则同一张图会在报告里出现两次。
    """
    report = yield
    if report.when == "call" and report.failed:
        page = _page_of(item)
        if page is not None:
            _log_scene(page)
            _attach("① 失败时的整页截图", lambda: page.screenshot(full_page=True),
                    allure.attachment_type.PNG)
            _attach("② 失败时的页面地址", lambda: page.url)
            _attach("③ 失败时的 toast",
                    lambda: "\n".join(page.locator(".toast").all_inner_texts())
                    or "(屏幕上没有 toast)")
            _attach("④ 失败时的页面正文",
                    lambda: page.locator("body").inner_text()[:3000])
    return report
