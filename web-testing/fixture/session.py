"""浏览器会话 fixture：环境探活 → 账号兜底 → 已登录 page → 前置数据。

自下而上依赖：
  _services_ready   前后端没起就别跑，给一句人话而不是几十个超时
  accounts_ready    testS01 / testT01 不在库里就按接口规则注册出来
  *_page            把 token 注入 context，用例拿到就是已登录状态
  fresh_student     购买/投递闭环专用：每次一个全新学生
  first_course      从接口挑数据，用例里不写死 id
"""

import time

import pytest
import requests

from config.settings import ACCOUNTS, API_BASE_URL, BASE_URL
from fixture import cleanup, plugins
from fixture.login import STORAGE_KEY


# ------------------------------------------------------------ 环境探活

def _require(url, name, hint):
    try:
        requests.get(url, timeout=5).raise_for_status()
    except requests.RequestException as e:
        pytest.exit(
            f"\n[web 自动化] {name} 未就绪，无法开始。\n"
            f"  地址：{url}\n  原因：{e}\n  {hint}\n",
            returncode=2,
        )


@pytest.fixture(scope="session", autouse=True)
def _services_ready():
    """开跑前确认前后端都在。

    不做这一步，前端没起时每条用例各自超时一次，
    真正的原因会被埋在几十个 TimeoutError 里。
    """
    _require(f"{API_BASE_URL}/api/course/list?page=1&size=1", "后端服务",
             "请先启动 Spring Boot 后端（端口 8080）。")
    _require(BASE_URL, "前端 dev server",
             "请在 Smart_education_platform_frontend 下执行 npm run dev（端口 5173）。")


# ------------------------------------------------------------ 账号兜底

def _login_ok(username, password):
    try:
        body = requests.post(f"{API_BASE_URL}/api/user/login",
                             json={"username": username, "password": password},
                             timeout=10).json()
    except requests.RequestException:
        return False
    return body.get("code") == 200


@pytest.fixture(scope="session", autouse=True)
def accounts_ready(_services_ready):
    """确保 student / teacher 账号存在，缺了就注册出来。

    数据库刚重建时 user 表是空的，而后端 DataInitializer 只建 admin
    （seb/config/DataInitializer.java），注册接口才是学生/讲师账号的唯一来源。
    没有这一步，「登录成功」这类用例会失败在「用户名或密码错误」上，
    看起来像密码写错了，实际是账号压根不存在。
    """
    for role, acc in ACCOUNTS.items():
        if role == "admin":
            continue                    # 后端启动时自建，注册接口也不放 role=2
        if _login_ok(acc["username"], acc["password"]):
            continue
        # 注册是幂等的：账号已存在只会返回 400「用户名已存在」，
        # 那种情况账号本身是好的，所以不在这里断言返回值，直接回读一次登录。
        requests.post(f"{API_BASE_URL}/api/user/register", json=acc, timeout=15)
        assert _login_ok(acc["username"], acc["password"]), \
            f"前置账号 {acc['username']} 不存在，且注册后仍登录不上，检查后端"
    return True


# --------------------------------------------------------- 已登录的 page

def _context(browser, token=None):
    """新建浏览器上下文；给了 token 就是已登录态。

    登录态用 storage_state 在 context 创建时注入，而不是登录后再写 localStorage：
    这样页面脚本执行前它就已经是对的，不存在「先按未登录渲染、再补 token」的
    中间态，也不会被路由守卫抢跑一步弹回登录页。
    """
    kwargs = {"base_url": BASE_URL}
    if token:
        kwargs["storage_state"] = {
            "cookies": [],
            "origins": [{
                "origin": BASE_URL.rstrip("/"),
                "localStorage": [{"name": STORAGE_KEY, "value": token}],
            }],
        }
    return browser.new_context(**kwargs)


def _page_for(browser, token=None, who=""):
    """每个用例一个独立 context，用完就关 —— 上一条的登录态不会漏给下一条。

    挂一次 plugins.watch：这个 page 上的跳转、接口调用、JS 报错都进运行日志。
    """
    context = _context(browser, token)
    try:
        page = context.new_page()
        plugins.watch(page, who)
        yield page
    finally:
        context.close()


@pytest.fixture
def guest_page(browser):
    """未登录的页面，只给专门验证登录/未登录行为的用例用。"""
    yield from _page_for(browser, who="未登录")


@pytest.fixture
def student_page(browser, tokens, accounts_ready):
    """已登录的学生页面。"""
    yield from _page_for(browser, tokens["student"], who=ACCOUNTS["student"]["username"])


@pytest.fixture
def teacher_page(browser, tokens, accounts_ready):
    """已登录的讲师/企业页面。"""
    yield from _page_for(browser, tokens["teacher"], who=ACCOUNTS["teacher"]["username"])


@pytest.fixture
def admin_page(browser, tokens, accounts_ready):
    """已登录的管理员页面。"""
    yield from _page_for(browser, tokens["admin"], who="admin")


# ------------------------------------------------------------ 前置数据

def _register(body):
    """按接口注册一个账号并返回它（含 token）。失败直接让用例挂掉。"""
    r = requests.post(f"{API_BASE_URL}/api/user/register", json=body, timeout=15).json()
    assert r.get("code") == 200, f"前置注册失败：{r}"
    r = requests.post(f"{API_BASE_URL}/api/user/login",
                      json={"username": body["username"],
                            "password": body["password"]}, timeout=10).json()
    assert r.get("code") == 200, f"前置登录失败：{r}"
    return {**body, "token": r["data"]["token"]}


def _new_student():
    ts = str(int(time.time() * 1000))[-10:]
    student = _register({
        "username": f"web{ts}",          # 3-20 位，仅字母数字下划线
        "password": "123456",
        "phone": f"1{ts}",               # 1 + 10 位 = 11 位
        "email": f"web{ts}@test.com",
        "role": 0,
        "nickname": f"web{ts}",
    })
    cleanup.register(student["token"])   # 收尾时按这个 token 清它名下的购物车/订单/简历
    return student


@pytest.fixture
def fresh_student(_services_ready):
    """全新的、没买过课、没投过简历的学生。

    购买/投递闭环必须用它而不是 testS01：
    testS01 第二次执行时那门课已经在「我的课程」里，
    详情页按钮从「加入购物车」变成「开始学习」，用例无法重复跑。
    代价是每轮运行会往 user 表留一个 web<时间戳> 账号 —— 账号本身删不掉
    （后端没有删除用户的接口），但它名下这轮产生的购物车、待支付订单、
    简历会由 fixture/cleanup.py 在收尾时清掉。
    """
    return _new_student()


@pytest.fixture
def fresh_student_page(browser, fresh_student):
    """用全新学生登录的页面。"""
    yield from _page_for(browser, fresh_student["token"], who=fresh_student["username"])


def first_course(is_free):
    """按是否免费挑一门在架课程，返回接口里的那一条。

    不写死 id=1 / id=2：库里数据一变，用例就集体失败，
    而报错只会说「按钮找不到」，看不出是数据问题。
    """
    body = requests.get(f"{API_BASE_URL}/api/course/list",
                        params={"page": 1, "size": 1, "isFree": is_free},
                        timeout=10).json()
    items = (body.get("data") or {}).get("list") or []
    if not items:
        pytest.skip(f"库里没有{'免费' if is_free else '付费'}课程，用例没法跑")
    return items[0]


def first_job():
    """挑一个在架职位。"""
    body = requests.get(f"{API_BASE_URL}/api/job/list",
                        params={"page": 1, "size": 1}, timeout=10).json()
    items = (body.get("data") or {}).get("list") or []
    if not items:
        pytest.skip("库里没有在架职位，用例没法跑")
    return items[0]


# ------------------------------------------------------------ 测试文件

@pytest.fixture
def pdf_file(tmp_path):
    """一个最小的 PDF。

    后端 ResumeService 两道校验：扩展名 .pdf + Content-Type 含 pdf
    （Playwright 按扩展名推断 type），内容不解析，占位内容也能过。
    """
    f = tmp_path / "resume.pdf"
    f.write_bytes(b"%PDF-1.4\n% test resume\n")
    return str(f)


@pytest.fixture
def not_pdf(tmp_path):
    """扩展名不对的文件，用来验证前端的 PDF 拦截。"""
    f = tmp_path / "resume.txt"
    f.write_text("not a pdf", encoding="utf-8")
    return str(f)
