"""讲师端：提交课程上架申请、职位发布申请 —— WEB_TC_095 ~ WEB_TC_106

被测页面：views/course/CourseApply.vue、views/job/JobApply.vue
页面对象：page/courseApplyPage.py、jobApplyPage.py

两条成功的用例会往 apply 表里留一条 status=0 的待审核记录，
正好是 test_09_admin 里审核用例的数据来源（pytest 按文件名先后执行，
test_08 先于 test_09）。

后端校验来自 seb/dto/CourseApplyDTO.java、JobApplyDTO.java：
  courseName @NotBlank；price ≥ 0 且 ≤ 30000（免费课不填价，为 null 也放行）
  jobName @NotBlank；salaryMin/Max ≥ 2500 且 salaryMin < salaryMax（@AssertTrue）
"""

import allure
import pytest

from common.component import o_toast
from common.operation import o_click, o_count, o_fill, o_goto, o_text, o_value, o_visible
from page import courseApplyPage, jobApplyPage


@pytest.fixture
def course_apply_page(teacher_page):
    o_goto(teacher_page, "/course/apply")
    return teacher_page


@pytest.fixture
def job_apply_page(teacher_page):
    o_goto(teacher_page, "/job/apply")
    return teacher_page


@allure.feature("讲师-课程申请")
def test_WEB_TC_095_课程申请页渲染完整(course_apply_page):
    assert o_text(courseApplyPage.locate_title(course_apply_page)) == "申请课程上架"

    assert o_visible(courseApplyPage.locate_course_name(course_apply_page))
    assert o_visible(courseApplyPage.locate_tech_system_chips(course_apply_page).first)
    assert o_visible(courseApplyPage.locate_tech_direction_chips(course_apply_page).first)
    assert o_visible(courseApplyPage.locate_submit_btn(course_apply_page))
    # 这里没有「全部类型」这一项，正好是 options.js 里 COURSE_TYPES 的 8 项
    assert o_count(courseApplyPage.locate_course_type_chips(course_apply_page)) == 8, \
        "技术体系应是 8 项（options.js 的 COURSE_TYPES）"
    # 默认 isFree = 0，价格框可见
    assert o_visible(courseApplyPage.locate_price(course_apply_page))


@allure.feature("讲师-课程申请")
def test_WEB_TC_096_课程名称未填被拦截(course_apply_page):
    o_click(courseApplyPage.locate_submit_btn(course_apply_page))
    assert o_toast(course_apply_page, "请填写课程名称") == "请填写课程名称"


@allure.feature("讲师-课程申请")
def test_WEB_TC_097_未选技术体系被拦截(course_apply_page):
    o_fill(courseApplyPage.locate_course_name(course_apply_page), "自动化测试课程")
    o_click(courseApplyPage.locate_submit_btn(course_apply_page))

    assert o_toast(course_apply_page, "请选择技术体系") == "请选择技术体系"


@allure.feature("讲师-课程申请")
def test_WEB_TC_098_未选技术方向被拦截(course_apply_page):
    o_fill(courseApplyPage.locate_course_name(course_apply_page), "自动化测试课程")
    o_click(courseApplyPage.locate_tech_system_chips(course_apply_page).first)
    o_click(courseApplyPage.locate_submit_btn(course_apply_page))

    assert o_toast(course_apply_page, "请选择技术方向") == "请选择技术方向"


@allure.feature("讲师-课程申请")
def test_WEB_TC_099_添加章节行(course_apply_page):
    """CourseApply.vue:13 新增一章默认时长 20。"""
    o_click(courseApplyPage.locate_add_chapter_btn(course_apply_page))

    assert o_count(courseApplyPage.locate_chapter_names(course_apply_page)) == 1, \
        "点了「添加章节」却没出现章节行"
    assert o_value(courseApplyPage.locate_chapter_durations(course_apply_page).first) == "20"


@allure.feature("讲师-课程申请")
def test_WEB_TC_100_删除章节行(course_apply_page):
    o_click(courseApplyPage.locate_add_chapter_btn(course_apply_page))
    o_click(courseApplyPage.locate_add_chapter_btn(course_apply_page))
    assert o_count(courseApplyPage.locate_chapter_names(course_apply_page)) == 2, \
        "点了两次「添加章节」，应该有 2 行"

    o_click(courseApplyPage.locate_chapter_delete_btns(course_apply_page).first)

    assert o_count(courseApplyPage.locate_chapter_names(course_apply_page)) == 1, \
        "删掉一行后剩下的行数不对，期望 1 行"


@allure.feature("讲师-课程申请")
def test_WEB_TC_101_提交课程上架申请成功(course_apply_page):
    """勾「免费」绕开价格填写，其余用表单默认值。

    提交成功后表单会被重置（CourseApply.vue:23），顺带把这一点也断言掉。
    """
    o_fill(courseApplyPage.locate_course_name(course_apply_page), "自动化测试课程")
    o_click(courseApplyPage.locate_tech_system_chips(course_apply_page).first)
    o_click(courseApplyPage.locate_tech_direction_chips(course_apply_page).first)
    o_click(courseApplyPage.locate_free_chip(course_apply_page))

    o_click(courseApplyPage.locate_submit_btn(course_apply_page))

    assert o_toast(course_apply_page, "申请已提交，等待审核") == "申请已提交，等待审核"
    assert o_value(courseApplyPage.locate_course_name(course_apply_page)) == ""


@allure.feature("讲师-职位申请")
def test_WEB_TC_102_职位申请页渲染完整(job_apply_page):
    assert o_text(jobApplyPage.locate_title(job_apply_page)) == "申请职位上架"

    for locate in (jobApplyPage.locate_job_name,
                   jobApplyPage.locate_company_name,
                   jobApplyPage.locate_city,
                   jobApplyPage.locate_salary_min,
                   jobApplyPage.locate_salary_max,
                   jobApplyPage.locate_submit_btn):
        assert o_visible(locate(job_apply_page))
    assert o_count(jobApplyPage.locate_category_chips(job_apply_page)) == 15, \
        "职位类别应是 15 项（options.js 的 JOB_CATEGORIES）"


@allure.feature("讲师-职位申请")
def test_WEB_TC_103_职位名称未填被拦截(job_apply_page):
    o_click(jobApplyPage.locate_submit_btn(job_apply_page))
    assert o_toast(job_apply_page, "请填写职位名称") == "请填写职位名称"


@allure.feature("讲师-职位申请")
def test_WEB_TC_104_未选职位类别被拦截(job_apply_page):
    o_fill(jobApplyPage.locate_job_name(job_apply_page), "自动化测试工程师")
    o_click(jobApplyPage.locate_submit_btn(job_apply_page))

    assert o_toast(job_apply_page, "请选择职位类别") == "请选择职位类别"


@allure.feature("讲师-职位申请")
def test_WEB_TC_105_最低薪资不小于最高薪资被拦截(job_apply_page):
    """前端先拦一次（JobApply.vue:20），后端 JobApplyDTO 的 @AssertTrue 还会再拦一次。"""
    o_fill(jobApplyPage.locate_job_name(job_apply_page), "自动化测试工程师")
    o_click(jobApplyPage.locate_category_chips(job_apply_page).first)
    o_fill(jobApplyPage.locate_salary_min(job_apply_page), "20000")
    o_fill(jobApplyPage.locate_salary_max(job_apply_page), "10000")

    o_click(jobApplyPage.locate_submit_btn(job_apply_page))

    assert o_toast(job_apply_page, "最低薪资必须小于最高薪资") == "最低薪资必须小于最高薪资"


@allure.feature("讲师-职位申请")
def test_WEB_TC_106_提交职位发布申请成功(job_apply_page):
    o_fill(jobApplyPage.locate_job_name(job_apply_page), "自动化测试工程师")
    o_click(jobApplyPage.locate_category_chips(job_apply_page).first)
    o_fill(jobApplyPage.locate_salary_min(job_apply_page), "10000")
    o_fill(jobApplyPage.locate_salary_max(job_apply_page), "20000")

    o_click(jobApplyPage.locate_submit_btn(job_apply_page))

    assert o_toast(job_apply_page, "申请已提交，等待审核") == "申请已提交，等待审核"
    assert o_value(jobApplyPage.locate_job_name(job_apply_page)) == ""
