"""课程中心与课程详情 —— WEB_TC_041 ~ WEB_TC_054

被测页面：views/course/CourseList.vue、CourseDetail.vue
页面对象：page/courseListPage.py、courseCardPage.py、courseDetailPage.py

课程数据从接口挑（fixture/session.py:first_course），不写死 id。
未登录的用例统一用 guest_page：登录态会影响详情页主按钮的文案
（已购是「开始学习」、未购是「加入购物车」），不控制住这条断言就不稳。
"""

from urllib.parse import urlparse

import allure
import pytest

from common.component import o_empty, o_path, o_toast, o_wait_path, o_wait_text
from common.operation import (o_all_text, o_attr, o_click, o_count, o_fill, o_goto,
                              o_press, o_select, o_text, o_value, o_visible)
from fixture.session import first_course
from page import courseCardPage, courseDetailPage, courseListPage


@pytest.fixture
def paid_course():
    return first_course(is_free=0)


@pytest.fixture
def course_list(guest_page):
    o_goto(guest_page, "/course")
    return guest_page


def _assert_filtered(page, tags, expected):
    """筛选后要么有结果且全都符合，要么是空态 —— 不能是上一次的列表残留。"""
    texts = o_all_text(tags)
    if not texts:
        assert o_empty(page) == "还没有课程，换个条件试试"
    else:
        assert set(texts) == {expected}, f"筛选后仍有不符合的课程：{set(texts)}"


@allure.feature("课程")
def test_WEB_TC_041_课程中心渲染完整(course_list):
    assert o_text(courseListPage.locate_title(course_list)) == "课程中心"
    assert o_visible(courseListPage.locate_search_input(course_list))
    assert o_visible(courseListPage.locate_sort_select(course_list))
    # 三组筛选：类型（全部 + COURSE_TYPES 8 项）、等级（全部 + 5 项）、价格（3 项）
    assert o_count(courseListPage.locate_type_chips(course_list)) == 9, \
        "类型筛选应是 9 项（「全部」+ options.js COURSE_TYPES 的 8 项）"
    assert o_count(courseListPage.locate_level_chips(course_list)) == 6, \
        "等级筛选应是 6 项（「全部」+ 5 个等级）"
    assert o_count(courseListPage.locate_price_chips(course_list)) == 3, \
        "价格筛选应是 3 项（全部 / 免费 / 付费）"


@allure.feature("课程")
def test_WEB_TC_042_关键字搜索命中课程(course_list, paid_course):
    """搜索框绑的是 @keyup.enter（CourseList.vue:26），要回车而不是点按钮。"""
    o_fill(courseListPage.locate_search_input(course_list), paid_course["courseName"])
    o_press(courseListPage.locate_search_input(course_list), "Enter")

    o_wait_text(courseCardPage.locate_card_names(course_list).first,
                paid_course["courseName"])


@allure.feature("课程")
def test_WEB_TC_043_搜索无结果展示空态(course_list):
    o_fill(courseListPage.locate_search_input(course_list), "不存在的课程名xyz")
    o_press(courseListPage.locate_search_input(course_list), "Enter")

    assert o_empty(course_list) == "还没有课程，换个条件试试"


@allure.feature("课程")
def test_WEB_TC_044_按课程类型筛选(course_list):
    """类型 chips：第 1 个是「全部类型」，第 2 个是「理论」。"""
    chips = courseListPage.locate_type_chips(course_list)
    o_click(chips.nth(1))
    assert "active" in (o_attr(chips.nth(1), "class") or "")

    _assert_filtered(course_list,
                     courseCardPage.locate_card_type_tags(course_list), "理论")


@allure.feature("课程")
def test_WEB_TC_045_按课程等级筛选(course_list):
    """等级 chips：全部等级 / 入门 / 初级 / 中级 / 高级 / 专家。

    这条只断言 chip 进入激活态且列表刷新出结果（有卡片或空态），
    因为卡片上的等级混在 meta 文本里（讲师名 · 等级），不好直接取。
    """
    chips = courseListPage.locate_level_chips(course_list)
    o_click(chips.nth(2))
    assert "active" in (o_attr(chips.nth(2), "class") or "")
    assert o_count(courseCardPage.locate_cards(course_list)) or o_empty(course_list), \
        "课程列表既没有卡片也没有空态提示，页面没渲染出来"


@allure.feature("课程")
def test_WEB_TC_046_免费筛选结果全部免费(course_list):
    o_click(courseListPage.locate_free_chip(course_list))
    _assert_filtered(course_list,
                     courseCardPage.locate_card_prices(course_list), "免费")


@allure.feature("课程")
def test_WEB_TC_047_切换排序方式(course_list):
    """下拉的 change 直接触发 load（CourseList.vue:27）。"""
    select = courseListPage.locate_sort_select(course_list)
    o_select(select, "enroll")

    assert o_value(select) == "enroll"
    assert o_count(courseCardPage.locate_cards(course_list)) >= 1, \
        "切成「按报名人数排序」后课程列表空了"


@allure.feature("课程")
def test_WEB_TC_048_点击课程卡片进入详情(course_list):
    """卡片 href 指向 /course/<id>，点进去应落到同一个路径。"""
    card = courseCardPage.locate_cards(course_list).first
    target = urlparse(o_attr(card, "href")).path      # DOM 里 href 已被解析成绝对地址

    o_click(card)

    o_wait_path(course_list, target)
    assert target.startswith("/course/")


@allure.feature("课程")
def test_WEB_TC_049_课程详情页展示标题与购买入口(course_list, paid_course):
    o_goto(course_list, f"/course/{paid_course['id']}")

    assert o_text(courseDetailPage.locate_title(course_list)) == paid_course["courseName"]
    assert o_count(courseDetailPage.locate_tags(course_list)) == 3, \
        "详情页应挂 3 个标签：类型 / 等级 / 价格"
    assert o_visible(courseDetailPage.locate_collect_btn(course_list))
    # 未登录拿不到 purchased=true，主按钮固定是「加入购物车」
    assert o_visible(courseDetailPage.locate_add_cart_btn(course_list))


@allure.feature("课程")
def test_WEB_TC_050_未登录点收藏跳登录页(course_list, paid_course):
    """CourseDetail.vue:15 没登录直接 router.push('/login')。"""
    o_goto(course_list, f"/course/{paid_course['id']}")
    o_click(courseDetailPage.locate_collect_btn(course_list))

    o_wait_path(course_list, "/login")


@allure.feature("课程")
def test_WEB_TC_051_未登录点加入购物车跳登录页(course_list, paid_course):
    o_goto(course_list, f"/course/{paid_course['id']}")
    o_click(courseDetailPage.locate_add_cart_btn(course_list))

    o_wait_path(course_list, "/login")


@allure.feature("课程")
def test_WEB_TC_052_讲师点加入购物车被拒(teacher_page, paid_course):
    """只有学生能买课；讲师点了要被拦下，而且不离开当前页。"""
    o_goto(teacher_page, f"/course/{paid_course['id']}")
    o_click(courseDetailPage.locate_add_cart_btn(teacher_page))

    assert o_toast(teacher_page, "仅学生可购买课程") == "仅学生可购买课程"
    assert o_path(teacher_page) == f"/course/{paid_course['id']}"


@allure.feature("课程")
def test_WEB_TC_053_学生点收藏成功(student_page, paid_course):
    o_goto(student_page, f"/course/{paid_course['id']}")
    o_click(courseDetailPage.locate_collect_btn(student_page))

    assert o_toast(student_page, "已收藏") == "已收藏"


@allure.feature("课程")
def test_WEB_TC_054_价格筛选切回全部恢复列表(course_list):
    chips = courseListPage.locate_price_chips(course_list)

    o_click(courseListPage.locate_paid_chip(course_list))
    assert "active" in (o_attr(courseListPage.locate_paid_chip(course_list), "class") or "")

    o_click(chips.first)
    assert "active" in (o_attr(chips.first, "class") or "")
    assert o_count(courseCardPage.locate_cards(course_list)) >= 1, \
        "按价格区间筛完一门课都不剩（先确认库里这个价位确实有课）"
