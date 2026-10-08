"""全站公共组件：Toast、空态、路由跳转。

为什么单独开一个文件、而不是并进 common/operation.py：
  operation.py 管的是「怎么操作一个元素」——点、填、取值、等待；
  这里管的是「怎么等这个应用」——Toast（components/Toast.vue）、
  列表空态（.empty）、Vue Router 的异步跳转。
  两者变化的理由不一样，混在一起 operation.py 只会越来越杂。

命名沿用 o_ 前缀，用例里两种 import 一眼能分清来源。
"""

import re
import time
from urllib.parse import urlparse

from config.settings import TIMEOUT


def o_toast(page, text=None, timeout=3000):
    """等 toast 出现并返回文案；超时返回 None。

    等的是「变成可见」而不是「元素存在」：toast 出现前 count 就是 0，
    用 count 判断会立刻返回 0，等于没等。

    传 text 时等的是「出现含这段文案的 toast」而不是「出现任意 toast」：
    同屏 toast 会叠加（Toast.vue 用数组渲染），
    2.6 秒内连做两个操作时，直接读 .toast 第一条会读到上一条的文案，
    断言看起来会莫名其妙地失败。
    """
    toasts = page.locator(".toast")
    target = toasts.filter(has_text=text) if text else toasts
    first = target.first
    try:
        first.wait_for(state="visible", timeout=timeout)
    except Exception:
        return None
    return first.inner_text()


def o_toast_type(page, text=None):
    """toast 的语义类型：success / error / info（类名 .toast--<type>）。"""
    toasts = page.locator(".toast")
    first = (toasts.filter(has_text=text) if text else toasts).first
    cls = first.get_attribute("class") or ""
    for t in ("success", "error", "info"):
        if f"toast--{t}" in cls:
            return t
    return ""


def o_empty(page, contains=None, timeout=3000):
    """列表页空态文案；没有空态返回 None。

    传 contains 时等的是「含这段文案的空态」：
    MyApplications 这类页面会先渲染一帧
    <div class="empty">加载中…</div>，不指定就会读到它。
    """
    empty = page.locator(".empty")
    if contains:
        empty = empty.filter(has_text=contains)
    first = empty.first
    try:
        first.wait_for(state="visible", timeout=timeout)
    except Exception:
        return None
    return first.inner_text()


def o_path(page):
    """当前路径，不含域名和查询串。

    断言跳转目标时用它，而不是比整个 URL：
    "http://localhost:5173/login" 和 "/login" 表达的是同一件事，
    但前者换个端口、换个访问前缀就集体挂。
    """
    return urlparse(page.url).path


def o_wait_path(page, path, timeout=TIMEOUT):
    """等路由落到指定 path。

    不用 page.wait_for_url：那个比的是完整 URL 且带 glob 语义，
    而用例的意图只是「路由跳没跳到这一条」。
    路由跳转是异步的，必须等 —— 点完立刻取一次 o_path 就断言，
    是这套用例最常见的偶发失败来源。
    """
    page.wait_for_function(
        "p => new URL(location.href).pathname === p", arg=path, timeout=timeout
    )


def o_wait_path_prefix(page, prefix, timeout=TIMEOUT):
    """等路由落到某个前缀下，返回完整 path。

    用在「目标地址带 id、跳之前不知道 id」的场景：
    下单成功后是 /order/<新建的 id>，只能等前缀，不能等一个写死的地址。
    """
    page.wait_for_function(
        "p => new URL(location.href).pathname.startsWith(p)", arg=prefix, timeout=timeout
    )
    return o_path(page)


def o_wait_text(sth, text, timeout=TIMEOUT):
    """等元素出现、且文案正好等于 text。

    页头是「先按 token 判定已登录、再异步补用户信息」的，
    直接读 nav 文案会在角色还没拉回来时读到未登录菜单。
    """
    sth.filter(has_text=re.compile(rf"^{re.escape(text)}$")).first.wait_for(
        state="visible", timeout=timeout
    )


def o_wait_any(sth, timeout=3000):
    """等 sth 至少匹配到一个元素，返回个数；等不到返回 0。

    不要用「看到空态」来判断「确实没有数据」：后台列表的空态是 v-else
    渲染的，请求还没回来的第一帧它就已经写着「暂无课程」了。
    想知道到底有没有数据，只能给表格行一段等待时间 —— 这就是那段等待。
    """
    deadline = time.monotonic() + timeout / 1000
    while True:
        n = sth.count()
        if n or time.monotonic() >= deadline:
            return n
        time.sleep(0.1)


def o_wait_texts(sth, texts, timeout=TIMEOUT):
    """等 sth 里所有元素的文案正好构成 texts 这个集合，返回实际集合。

    筛选/搜索是「发请求 → 重渲染」的，选完下拉立刻 all_inner_texts()
    拿到的还是上一轮列表 —— 断言"筛完只剩学生"必须等结果回来。
    """
    wanted = set(texts)
    deadline = time.monotonic() + timeout / 1000
    while True:
        actual = set(sth.all_inner_texts())
        if actual == wanted or time.monotonic() >= deadline:
            return actual
        time.sleep(0.1)


def o_accept_dialog(page):
    """接受下一个弹出的原生 confirm/alert。

    Playwright 默认把原生弹窗自动 dismiss 掉，confirm 会返回 false，
    删除逻辑整段跳过 —— 表现成「点了删除、什么都没发生」。
    """
    page.once("dialog", lambda dialog: dialog.accept())


def o_eval(page, script):
    """在页面里跑一段 JS 取返回值（例如读 localStorage 验证登录态）。"""
    return page.evaluate(script)
