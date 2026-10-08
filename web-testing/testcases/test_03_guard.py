"""路由守卫 —— WEB_TC_027 ~ WEB_TC_040

被测对象：router/index.js:43-49
  requiresAuth 且未登录                 → /login
  roles 不含当前角色                    → /（首页，不是 403 页面）
  已登录访问 /login /register /forgot   → /

不需要页面对象：断言的全是路由落点，o_path / o_wait_path 就够。

这里刻意不写 parametrize：每条用例的编号要能和测试用例表的行号一一对上，
parametrize 展开后一条变十条，统计口径就乱了。
"""

import allure

from common.component import o_wait_path
from common.operation import o_goto


def _expect_redirect(page, path, target):
    """打开 path，断言最终落在 target。

    必须等而不是断言一次：守卫是异步的（要等 fetchInfo 回来才知道角色），
    点完立刻取 o_path 常常还停在旧地址，是最典型的偶发失败。
    """
    o_goto(page, path)
    o_wait_path(page, target)


@allure.feature("路由守卫")
def test_WEB_TC_027_未登录访问购物车跳登录(guest_page):
    _expect_redirect(guest_page, "/cart", "/login")


@allure.feature("路由守卫")
def test_WEB_TC_028_未登录访问我的订单跳登录(guest_page):
    _expect_redirect(guest_page, "/order", "/login")


@allure.feature("路由守卫")
def test_WEB_TC_029_未登录访问个人中心跳登录(guest_page):
    _expect_redirect(guest_page, "/user", "/login")


@allure.feature("路由守卫")
def test_WEB_TC_030_未登录访问我的简历跳登录(guest_page):
    _expect_redirect(guest_page, "/user/resume", "/login")


@allure.feature("路由守卫")
def test_WEB_TC_031_未登录访问申请课程跳登录(guest_page):
    _expect_redirect(guest_page, "/course/apply", "/login")


@allure.feature("路由守卫")
def test_WEB_TC_032_未登录访问申请职位跳登录(guest_page):
    _expect_redirect(guest_page, "/job/apply", "/login")


@allure.feature("路由守卫")
def test_WEB_TC_033_未登录访问我的投递跳登录(guest_page):
    _expect_redirect(guest_page, "/job/my-applications", "/login")


@allure.feature("路由守卫")
def test_WEB_TC_034_未登录访问后台跳登录(guest_page):
    _expect_redirect(guest_page, "/admin", "/login")


@allure.feature("路由守卫")
def test_WEB_TC_035_未登录访问AI面试跳登录(guest_page):
    _expect_redirect(guest_page, "/job/interview/1", "/login")


@allure.feature("路由守卫")
def test_WEB_TC_036_学生访问申请课程页回首页(student_page):
    """/course/apply 的 roles 是 [1]，学生进去应被弹回首页。"""
    _expect_redirect(student_page, "/course/apply", "/")


@allure.feature("路由守卫")
def test_WEB_TC_037_学生访问候选人页回首页(student_page):
    _expect_redirect(student_page, "/job/applicants", "/")


@allure.feature("路由守卫")
def test_WEB_TC_038_学生访问后台用户管理回首页(student_page):
    """后台是嵌套路由，父级 meta 上的 roles 对子路由同样生效。"""
    _expect_redirect(student_page, "/admin/users", "/")


@allure.feature("路由守卫")
def test_WEB_TC_039_讲师访问购物车回首页(teacher_page):
    """/cart 的 roles 是 [0]，讲师不该能进。"""
    _expect_redirect(teacher_page, "/cart", "/")


@allure.feature("路由守卫")
def test_WEB_TC_040_已登录访问忘记密码页回首页(student_page):
    """router/index.js:48 —— 已登录就没必要再走一遍找回密码。"""
    _expect_redirect(student_page, "/forgot", "/")
