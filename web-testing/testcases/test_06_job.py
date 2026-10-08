"""职位中心、投递与 AI 面试 —— WEB_TC_069 ~ WEB_TC_082

被测页面：views/job/JobList.vue、JobDetail.vue、MyApplications.vue
页面对象：page/jobListPage.py、jobCardPage.py、jobDetailPage.py、myApplicationsPage.py

投递相关用例全部用 fresh_student_page：testS01 投过一次之后，
后端会以「您已投递过该职位，请勿重复投递」拒绝第二次，
用固定账号就变成只能跑一次。
"""

from urllib.parse import urlparse

import allure
import pytest

from common.component import o_empty, o_path, o_toast, o_wait_path, o_wait_text
from common.operation import (o_attr, o_click, o_count, o_fill, o_goto, o_press, o_text,
                              o_upload, o_visible)
from fixture.session import first_job
from page import jobCardPage, jobDetailPage, jobListPage, myApplicationsPage


@pytest.fixture
def job():
    return first_job()


@pytest.fixture
def job_list(guest_page):
    o_goto(guest_page, "/job")
    return guest_page


def _open_apply_modal(page, job):
    """进详情页 → 点「投递简历」→ 等弹窗标题出现。"""
    o_goto(page, f"/job/{job['id']}")
    o_click(jobDetailPage.locate_apply_btn(page))
    o_wait_text(jobDetailPage.locate_modal_title(page), "投递简历")


@allure.feature("职位")
def test_WEB_TC_069_职位中心渲染完整(job_list):
    assert o_text(jobListPage.locate_title(job_list)) == "职位中心"
    assert o_visible(jobListPage.locate_search_input(job_list))
    # 全部类别 + JOB_CATEGORIES 的 15 项
    assert o_count(jobListPage.locate_category_chips(job_list)) == 16, \
        "职位类别应是 16 项（「全部类别」+ options.js JOB_CATEGORIES 的 15 项）"


@allure.feature("职位")
def test_WEB_TC_070_关键字搜索命中职位(job_list, job):
    o_fill(jobListPage.locate_search_input(job_list), job["jobName"])
    o_press(jobListPage.locate_search_input(job_list), "Enter")

    o_wait_text(jobCardPage.locate_card_names(job_list).first, job["jobName"])


@allure.feature("职位")
def test_WEB_TC_071_搜索无结果展示空态(job_list):
    o_fill(jobListPage.locate_search_input(job_list), "不存在的职位名xyz")
    o_press(jobListPage.locate_search_input(job_list), "Enter")

    assert o_empty(job_list) == "暂无职位，换个条件试试"


@allure.feature("职位")
def test_WEB_TC_072_按职位类别筛选(job_list):
    """类别 chips：第 1 个是「全部类别」，第 2 个是「前端」。"""
    chips = jobListPage.locate_category_chips(job_list)
    o_click(chips.nth(1))

    assert "active" in (o_attr(chips.nth(1), "class") or "")
    assert o_count(jobCardPage.locate_cards(job_list)) or o_empty(job_list), \
        "职位列表既没有卡片也没有空态提示，页面没渲染出来"


@allure.feature("职位")
def test_WEB_TC_073_点击职位卡片进入详情(job_list):
    """卡片 href 指向 /job/<id>，点进去应落到同一个路径。"""
    card = jobCardPage.locate_cards(job_list).first
    target = urlparse(o_attr(card, "href")).path

    o_click(card)

    o_wait_path(job_list, target)
    assert target.startswith("/job/")


@allure.feature("职位")
def test_WEB_TC_074_未登录点投递跳登录页(job_list, job):
    """JobDetail.vue:25 needLogin() 没登录直接送去 /login。"""
    o_goto(job_list, f"/job/{job['id']}")
    o_click(jobDetailPage.locate_apply_btn(job_list))

    o_wait_path(job_list, "/login")


@allure.feature("职位")
def test_WEB_TC_075_未登录点AI面试跳登录页(job_list, job):
    o_goto(job_list, f"/job/{job['id']}")
    o_click(jobDetailPage.locate_interview_btn(job_list))

    o_wait_path(job_list, "/login")


@allure.feature("职位")
def test_WEB_TC_076_讲师点投递被拒(teacher_page, job):
    """只有学生能投递；讲师被拦下且不离开当前页。"""
    o_goto(teacher_page, f"/job/{job['id']}")
    o_click(jobDetailPage.locate_apply_btn(teacher_page))

    assert o_toast(teacher_page, "仅学生可投递职位") == "仅学生可投递职位"
    assert o_path(teacher_page) == f"/job/{job['id']}"


@allure.feature("职位")
def test_WEB_TC_077_讲师点AI面试被拒(teacher_page, job):
    o_goto(teacher_page, f"/job/{job['id']}")
    o_click(jobDetailPage.locate_interview_btn(teacher_page))

    assert o_toast(teacher_page, "仅学生可参加 AI 面试") == "仅学生可参加 AI 面试"
    assert o_path(teacher_page) == f"/job/{job['id']}"


@allure.feature("职位")
def test_WEB_TC_078_学生点投递弹出简历弹窗(fresh_student_page, job):
    _open_apply_modal(fresh_student_page, job)

    assert o_text(jobDetailPage.locate_modal_tip(fresh_student_page)) == \
        f"为「{job['jobName']}」选择一份简历"


@allure.feature("职位")
def test_WEB_TC_079_没有简历时确认投递被拦(fresh_student_page, job):
    """JobDetail.vue:32 没选中简历时只提示，不发投递请求。"""
    _open_apply_modal(fresh_student_page, job)
    assert o_text(jobDetailPage.locate_modal_empty(fresh_student_page)) == "还没有简历，请先上传一份"

    o_click(jobDetailPage.locate_confirm_apply_btn(fresh_student_page))

    assert o_toast(fresh_student_page, "请先上传并选择一份简历") == "请先上传并选择一份简历"
    assert o_path(fresh_student_page) == f"/job/{job['id']}", "弹窗内报错不应跳走"


@allure.feature("职位")
def test_WEB_TC_080_上传非PDF简历被前端拦截(fresh_student_page, job, not_pdf):
    """JobDetail.vue:40 只认 .pdf 结尾的文件名，不是就 toast，不发请求。"""
    _open_apply_modal(fresh_student_page, job)

    o_upload(jobDetailPage.locate_upload_input(fresh_student_page), not_pdf)

    assert o_toast(fresh_student_page, "仅支持 PDF 简历") == "仅支持 PDF 简历"


@allure.feature("职位")
def test_WEB_TC_081_取消按钮关闭投递弹窗(fresh_student_page, job):
    _open_apply_modal(fresh_student_page, job)

    o_click(jobDetailPage.locate_modal_cancel_btn(fresh_student_page))

    assert o_count(jobDetailPage.locate_modal_title(fresh_student_page)) == 0, \
        "点了「取消」，投递弹窗还开着"


@allure.feature("职位")
def test_WEB_TC_082_我的投递空态并跳职位列表(fresh_student_page):
    o_goto(fresh_student_page, "/job/my-applications")

    # 这个页面先渲染一帧「加载中…」的空态，所以要按文案等，而不是等任意 .empty
    assert o_empty(fresh_student_page, contains="你还没有投递过职位")

    o_click(myApplicationsPage.locate_go_job_btn(fresh_student_page))
    o_wait_path(fresh_student_page, "/job")
