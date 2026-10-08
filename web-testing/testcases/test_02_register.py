"""注册与表单校验 —— WEB_TC_013 ~ WEB_TC_026

被测页面：views/Register.vue      页面对象：page/registerPage.py

注册页输入框既没有 id/name，连 placeholder 都没有（Register.vue:34-43），
所以只能按 label 文案定位，registerPage.py 里已经这么写了。

前端校验是「短路」的（Register.vue:8-19），顺序为：
  用户名 → 用户名长度 → 用户名字符 → 密码 → 密码长度 → 昵称长度
  → 手机号为空 → 手机号格式 → 邮箱为空 → 邮箱格式
想触发后面某一条，前面每一条都必须是合法值。下面每条用例都标了它依赖什么。
"""

import time

import allure
import pytest

from common.component import o_path, o_toast, o_toast_type, o_wait_path
from common.operation import o_click, o_fill, o_goto, o_text, o_visible
from config.settings import ACCOUNTS
from page import registerPage


@pytest.fixture
def register_page(guest_page):
    o_goto(guest_page, "/register")
    return guest_page


def _unique():
    """每次运行都不撞库的一组注册信息。"""
    ts = str(int(time.time() * 1000))[-10:]
    return {
        "username": f"web{ts}",
        "password": "123456",
        "phone": f"1{ts}",
        "email": f"web{ts}@test.com",
    }


def _fill(page, **fields):
    """只填传进来的字段，没传的保持为空。

    校验短路，想测第 N 条就得把前 N-1 项都填成合法值，
    所以这里按需填，而不是「全填再清空」。
    """
    locators = {
        "username": registerPage.locate_username,
        "password": registerPage.locate_password,
        "email": registerPage.locate_email,
        "phone": registerPage.locate_phone,
        "nickname": registerPage.locate_nickname,
    }
    for name, value in fields.items():
        o_fill(locators[name](page), value)


def _submit(page):
    o_click(registerPage.locate_submit_btn(page))
    return o_toast(page)


@allure.feature("注册")
def test_WEB_TC_013_注册页渲染完整(register_page):
    assert o_text(registerPage.locate_title(register_page)) == "注册账号"
    assert "必填" in o_text(registerPage.locate_req_tip(register_page))
    for locate in (registerPage.locate_username, registerPage.locate_password,
                   registerPage.locate_email, registerPage.locate_phone,
                   registerPage.locate_role_select, registerPage.locate_nickname):
        assert o_visible(locate(register_page))
    assert o_visible(registerPage.locate_submit_btn(register_page))
    assert o_path(register_page) == "/register"


@allure.feature("注册")
def test_WEB_TC_014_全部为空提示用户名不能为空(register_page):
    assert _submit(register_page) == "用户名不能为空"
    assert o_toast_type(register_page) == "error"


@allure.feature("注册")
def test_WEB_TC_015_用户名少于3位被拦截(register_page):
    _fill(register_page, username="ab")
    assert _submit(register_page) == "用户名长度需在3-20个字符之间"


@allure.feature("注册")
def test_WEB_TC_016_用户名超过20位被拦截(register_page):
    _fill(register_page, username="w" * 21)
    assert _submit(register_page) == "用户名长度需在3-20个字符之间"


@allure.feature("注册")
def test_WEB_TC_017_用户名含非法字符被拦截(register_page):
    _fill(register_page, username="user-name")
    assert _submit(register_page) == "用户名只能包含字母、数字和下划线"


@allure.feature("注册")
def test_WEB_TC_018_密码为空被拦截(register_page):
    """依赖：用户名合法（13 位、全小写字母数字）。"""
    d = _unique()
    _fill(register_page, username=d["username"])
    assert _submit(register_page) == "密码不能为空"


@allure.feature("注册")
def test_WEB_TC_019_密码少于6位被拦截(register_page):
    d = _unique()
    _fill(register_page, username=d["username"], password="123")
    assert _submit(register_page) == "密码长度需在6-20个字符之间"


@allure.feature("注册")
def test_WEB_TC_020_昵称超过20字被拦截(register_page):
    """昵称是选填项，但一旦超过 20 字前端就拦（Register.vue:14）。

    注意校验顺序：昵称在手机号、邮箱之前，所以这两个可以留空。
    """
    d = _unique()
    _fill(register_page, username=d["username"], password=d["password"],
          nickname="昵" * 21)
    assert _submit(register_page) == "昵称不能超过20个字符"


@allure.feature("注册")
def test_WEB_TC_021_手机号为空被拦截(register_page):
    """依赖：用户名、密码合法；昵称留空（选填，空值不触发长度校验）。"""
    d = _unique()
    _fill(register_page, username=d["username"], password=d["password"])
    assert _submit(register_page) == "手机号不能为空"


@allure.feature("注册")
def test_WEB_TC_022_手机号位数不足被拦截(register_page):
    d = _unique()
    _fill(register_page, username=d["username"], password=d["password"], phone="12345")
    assert _submit(register_page) == "手机号必须为11位数字"


@allure.feature("注册")
def test_WEB_TC_023_邮箱为空被拦截(register_page):
    """依赖：用户名、密码、手机号都合法，校验才走到邮箱这一条。"""
    d = _unique()
    _fill(register_page, username=d["username"], password=d["password"],
          phone=d["phone"])
    assert _submit(register_page) == "邮箱不能为空"


@allure.feature("注册")
def test_WEB_TC_024_邮箱格式错误被拦截(register_page):
    d = _unique()
    _fill(register_page, **{**d, "email": "not-an-email"})
    assert _submit(register_page) == "邮箱格式不正确"


@allure.feature("注册")
def test_WEB_TC_025_注册成功提示并跳登录页(register_page):
    """昵称是选填项，只填 4 个必填项就应注册成功。

    后端 UserService.register 已把空昵称按未填写处理（空串不再参与查重），
    这里刻意不填昵称，顺带守住这个修复不再回归。
    """
    _fill(register_page, **_unique())
    o_click(registerPage.locate_submit_btn(register_page))

    assert o_toast(register_page, "注册成功，请登录") == "注册成功，请登录"
    o_wait_path(register_page, "/login")


@allure.feature("注册")
def test_WEB_TC_026_用户名已存在注册失败(register_page):
    """用户名重复由后端拒绝，提示后停留在注册页。

    用 testS01 —— 它在 accounts_ready 里保证存在。
    邮箱/手机号必须换成没被占用的，否则会先撞上「该邮箱已被注册」，
    拿到的提示就不是这条用例要测的了。
    """
    d = _unique()
    _fill(register_page,
          username=ACCOUNTS["student"]["username"],
          password=d["password"], phone=d["phone"], email=d["email"],
          nickname=d["username"])
    assert _submit(register_page) == "用户名已存在"
    assert o_path(register_page) == "/register", "注册失败不应跳转"
