"""登录、登出、已登录态 —— WEB_TC_001 ~ WEB_TC_012

被测页面：views/Login.vue、components/AppHeader.vue、store/auth.js
页面对象：page/loginPage.py、headerPage.py

账号来源：fixture/session.py:accounts_ready 保证 testS01 / testT01 存在，
admin 由后端 DataInitializer 在启动时建好。
"""

import allure
import pytest

from common.component import o_eval, o_path, o_toast, o_toast_type, o_wait_path, o_wait_text
from common.operation import o_click, o_count, o_fill, o_goto, o_text, o_visible
from config.settings import ACCOUNTS
from fixture.login import STORAGE_KEY
from page import headerPage, loginPage


@pytest.fixture
def login_page(guest_page):
    o_goto(guest_page, "/login")
    return guest_page


def _login(page, role):
    """在登录页填表提交；返回时已经不保证停在 /login（成功会跳走）。"""
    acc = ACCOUNTS[role]
    o_fill(loginPage.locate_username(page), acc["username"])
    o_fill(loginPage.locate_password(page), acc["password"])
    o_click(loginPage.locate_login_btn(page))
    return acc


@allure.feature("登录")
def test_WEB_TC_001_登录页渲染完整(login_page):
    assert o_text(loginPage.locate_title(login_page)) == "欢迎登录"
    assert o_visible(loginPage.locate_username(login_page))
    assert o_visible(loginPage.locate_password(login_page))
    assert o_visible(loginPage.locate_login_btn(login_page))
    assert o_visible(loginPage.locate_forgot_link(login_page))
    assert o_visible(loginPage.locate_register_link(login_page))


@allure.feature("登录")
def test_WEB_TC_002_用户名密码为空被前端拦截(login_page):
    """Login.vue:10 前端先判空，这两个框都不发请求。"""
    o_click(loginPage.locate_login_btn(login_page))

    assert o_toast(login_page, "请输入用户名和密码") == "请输入用户名和密码"
    assert o_toast_type(login_page) == "error"
    assert o_path(login_page) == "/login"


@allure.feature("登录")
def test_WEB_TC_003_密码错误提示(login_page):
    o_fill(loginPage.locate_username(login_page), ACCOUNTS["student"]["username"])
    o_fill(loginPage.locate_password(login_page), "wrong-password")
    o_click(loginPage.locate_login_btn(login_page))

    assert o_toast(login_page, "用户名或密码错误") == "用户名或密码错误"
    assert o_path(login_page) == "/login", "登录失败不应跳转"


@allure.feature("登录")
def test_WEB_TC_004_用户名不存在也返回同一句提示(login_page):
    """安全断言：不暴露「这个用户名到底存不存在」。

    后端 UserService.login 对「用户不存在」和「密码错误」返回同一句话，
    这条用例就是防止以后有人把它改成两种提示。
    """
    o_fill(loginPage.locate_username(login_page), "no_such_user_2026")
    o_fill(loginPage.locate_password(login_page), "whatever123")
    o_click(loginPage.locate_login_btn(login_page))

    assert o_toast(login_page, "用户名或密码错误") == "用户名或密码错误"


@allure.feature("登录")
def test_WEB_TC_005_学生登录成功跳首页并显示身份(login_page):
    _login(login_page, "student")

    assert o_toast(login_page, "登录成功") == "登录成功"
    o_wait_path(login_page, "/")
    o_wait_text(headerPage.locate_role_tag(login_page), "学生")
    assert o_text(headerPage.locate_user_link(login_page)).strip() != ""


@allure.feature("登录")
def test_WEB_TC_006_讲师登录后页头出现讲师菜单(login_page):
    _login(login_page, "teacher")

    o_wait_path(login_page, "/")
    o_wait_text(headerPage.locate_role_tag(login_page), "讲师/企业")
    assert o_visible(headerPage.locate_nav_course_apply(login_page))
    assert o_visible(headerPage.locate_nav_job_apply(login_page))
    assert o_visible(headerPage.locate_nav_applicants(login_page))
    # 讲师不能买课，学生菜单一个都不该出现
    assert o_count(headerPage.locate_nav_cart(login_page)) == 0, \
        "讲师/企业页头出现了购物车——学生菜单漏给了非学生角色"


@allure.feature("登录")
def test_WEB_TC_007_管理员登录后页头出现后台管理(login_page):
    _login(login_page, "admin")

    o_wait_path(login_page, "/")
    o_wait_text(headerPage.locate_role_tag(login_page), "管理员")
    assert o_visible(headerPage.locate_nav_admin(login_page))


@allure.feature("登录")
def test_WEB_TC_008_登录成功后token写入localStorage(login_page):
    """utils/auth.js:2 的键名是 smart_edu_token，请求拦截器靠它带 Authorization。"""
    _login(login_page, "student")
    o_wait_path(login_page, "/")

    assert o_eval(login_page, f"() => localStorage.getItem('{STORAGE_KEY}')")


@allure.feature("登录")
def test_WEB_TC_009_已登录访问登录页被弹回首页(student_page):
    """router/index.js:48 —— 已登录不该再看到登录页。"""
    o_goto(student_page, "/login")
    o_wait_path(student_page, "/")


@allure.feature("登录")
def test_WEB_TC_010_已登录访问注册页被弹回首页(student_page):
    o_goto(student_page, "/register")
    o_wait_path(student_page, "/")


@allure.feature("登录")
def test_WEB_TC_011_退出登录后回到未登录态(login_page):
    """AppHeader.vue:8：退出后 push('/')，页头换成登录/注册按钮。"""
    _login(login_page, "student")
    o_wait_path(login_page, "/")
    o_wait_text(headerPage.locate_role_tag(login_page), "学生")

    o_click(headerPage.locate_logout_btn(login_page))

    o_wait_path(login_page, "/")
    o_wait_text(headerPage.locate_login_btn(login_page), "登录")
    assert o_count(headerPage.locate_role_tag(login_page)) == 0, \
        "退出登录后页头还挂着身份标签，登录态没清干净"
    assert o_eval(login_page, f"() => localStorage.getItem('{STORAGE_KEY}')") is None


@allure.feature("登录")
def test_WEB_TC_012_未登录页头显示登录注册按钮(guest_page):
    o_goto(guest_page, "/")

    assert o_visible(headerPage.locate_login_btn(guest_page))
    assert o_visible(headerPage.locate_register_btn(guest_page))
    assert o_count(headerPage.locate_user_link(guest_page)) == 0, \
        "未登录页头出现了用户链接，应该只显示「登录 / 注册」"
