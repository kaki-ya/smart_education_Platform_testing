"""个人中心、改资料、改密码、简历 —— WEB_TC_083 ~ WEB_TC_094

被测页面：views/user/Profile.vue、MyResume.vue、MyApply.vue、course/MyCourse.vue
页面对象：page/profilePage.py、myResumePage.py、myApplyPage.py、myCoursePage.py

凡是会改账号状态的（改昵称、改密码、传/删简历）一律用 fresh_student_page，
跑完就丢，testS01 / testT01 的数据不被污染。
只读的渲染类断言才用 student_page。
"""

import allure
import pytest

from common.component import (o_accept_dialog, o_empty, o_toast, o_wait_any, o_wait_path,
                              o_wait_text)
from common.operation import o_click, o_fill, o_goto, o_text, o_upload, o_value, o_visible
from config.settings import ACCOUNTS
from fixture.session import not_pdf, pdf_file
from page import headerPage, myResumePage, profilePage


@allure.feature("个人中心")
def test_WEB_TC_083_个人中心信息卡渲染(student_page):
    o_goto(student_page, "/user")

    assert o_text(profilePage.locate_account_text(student_page)) == \
        f"@{ACCOUNTS['student']['username']}"
    assert o_text(profilePage.locate_role_badge(student_page)) == "学生"
    assert o_visible(profilePage.locate_my_apply_link(student_page))
    assert o_visible(profilePage.locate_my_resume_link(student_page))
    # 学生才有「学习与订单」分区，讲师/管理员这块是不渲染的
    assert o_visible(profilePage.locate_enrolled_card(student_page))
    assert o_visible(profilePage.locate_order_card(student_page))
    assert o_visible(profilePage.locate_nickname(student_page))


@allure.feature("个人中心")
def test_WEB_TC_084_修改昵称保存后页头同步(fresh_student_page, fresh_student):
    """Profile.vue:32-36 保存成功后重新拉一次用户信息，页头昵称随之更新。"""
    o_goto(fresh_student_page, "/user")
    new_name = f"昵称{fresh_student['username']}"

    o_fill(profilePage.locate_nickname(fresh_student_page), new_name)
    o_click(profilePage.locate_save_info_btn(fresh_student_page))

    assert o_toast(fresh_student_page, "资料已更新") == "资料已更新"
    o_wait_text(headerPage.locate_user_link(fresh_student_page), new_name)


@allure.feature("个人中心")
def test_WEB_TC_085_原密码错误提示(fresh_student_page):
    o_goto(fresh_student_page, "/user")

    o_fill(profilePage.locate_old_password(fresh_student_page), "wrong-password")
    o_fill(profilePage.locate_new_password(fresh_student_page), "newpass123")
    o_click(profilePage.locate_save_pwd_btn(fresh_student_page))

    assert o_toast(fresh_student_page, "原密码错误") == "原密码错误"


@allure.feature("个人中心")
def test_WEB_TC_086_改密码两项为空被前端拦截(fresh_student_page):
    """Profile.vue:38 前端先判空，不发请求。"""
    o_goto(fresh_student_page, "/user")

    o_click(profilePage.locate_save_pwd_btn(fresh_student_page))

    assert o_toast(fresh_student_page, "请填写原密码和新密码") == "请填写原密码和新密码"


@allure.feature("个人中心")
def test_WEB_TC_087_修改密码成功(fresh_student_page, fresh_student):
    """改的是本轮临时注册的账号，改完不影响任何别的用例。"""
    o_goto(fresh_student_page, "/user")

    o_fill(profilePage.locate_old_password(fresh_student_page), fresh_student["password"])
    o_fill(profilePage.locate_new_password(fresh_student_page), "newpass123")
    o_click(profilePage.locate_save_pwd_btn(fresh_student_page))

    assert o_toast(fresh_student_page, "密码已修改") == "密码已修改"
    assert o_value(profilePage.locate_old_password(fresh_student_page)) == "", \
        "成功后表单应被清空（Profile.vue:40）"


@allure.feature("简历")
def test_WEB_TC_088_我的简历空态(fresh_student_page):
    o_goto(fresh_student_page, "/user/resume")
    assert o_empty(fresh_student_page, contains="还没有简历") == "还没有简历，先上传一份吧"


@allure.feature("简历")
def test_WEB_TC_089_上传PDF简历成功(fresh_student_page, pdf_file):
    o_goto(fresh_student_page, "/user/resume")

    o_upload(myResumePage.locate_upload_input(fresh_student_page), pdf_file)

    assert o_toast(fresh_student_page, "简历上传成功") == "简历上传成功"
    # toast 是在重新拉列表之前弹的（MyResume.vue:19-20），所以等 toast 不等于等列表
    assert o_wait_any(myResumePage.locate_preview_links(fresh_student_page)) == 1, \
        "提示上传成功了，简历列表里却没有这一条"


@allure.feature("简历")
def test_WEB_TC_090_上传非PDF被前端拦截(fresh_student_page, not_pdf):
    o_goto(fresh_student_page, "/user/resume")

    o_upload(myResumePage.locate_upload_input(fresh_student_page), not_pdf)

    assert o_toast(fresh_student_page, "仅支持 PDF 简历") == "仅支持 PDF 简历"
    assert o_empty(fresh_student_page) == "还没有简历，先上传一份吧"


@allure.feature("简历")
def test_WEB_TC_091_删除简历需先确认(fresh_student_page, pdf_file):
    """MyResume.vue:28 用的是原生 confirm。

    Playwright 默认自动 dismiss 掉原生弹窗，confirm 返回 false，
    删除逻辑整段跳过、界面毫无反应 —— 所以必须先注册接受回调。
    """
    o_goto(fresh_student_page, "/user/resume")
    o_upload(myResumePage.locate_upload_input(fresh_student_page), pdf_file)
    # 上传成功后 onPick 里还会 await load() 再拉一次列表，等它渲染出来
    assert o_wait_any(myResumePage.locate_delete_btns(fresh_student_page)) == 1, \
        "上传成功了，列表里却没有可删除的简历"

    o_accept_dialog(fresh_student_page)
    o_click(myResumePage.locate_delete_btns(fresh_student_page).first)

    assert o_toast(fresh_student_page, "简历已删除") == "简历已删除"
    assert o_empty(fresh_student_page) == "还没有简历，先上传一份吧"


@allure.feature("个人中心")
def test_WEB_TC_092_我的申请空态(fresh_student_page):
    o_goto(fresh_student_page, "/user/my-apply")
    assert o_empty(fresh_student_page, contains="你还没有提交过申请") == "你还没有提交过申请"


@allure.feature("个人中心")
def test_WEB_TC_093_我的课程空态(fresh_student_page):
    o_goto(fresh_student_page, "/user/my-course")
    assert o_empty(fresh_student_page, contains="还没有已购课程") == "还没有已购课程，去挑一门吧"


@allure.feature("个人中心")
def test_WEB_TC_094_个人中心入口跳转正常(student_page):
    o_goto(student_page, "/user")
    o_click(profilePage.locate_my_resume_link(student_page))
    o_wait_path(student_page, "/user/resume")

    o_goto(student_page, "/user")
    o_click(profilePage.locate_my_apply_link(student_page))
    o_wait_path(student_page, "/user/my-apply")
