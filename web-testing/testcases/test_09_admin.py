"""后台管理：审核、用户、课程、职位、订单 —— WEB_TC_107 ~ WEB_TC_121

被测页面：views/admin/*.vue
页面对象：page/adminLayoutPage.py、applyAuditPage.py、userManagePage.py、
          courseManagePage.py、jobManagePage.py、orderManagePage.py

后台不渲染站点页头（App.vue:16 用 v-if="!isAdmin" 挡掉了），用例 107 顺带守住这条。

凡是「改状态」的用例都设计成可重复运行：
  能改回去的一定改回去（上下架、禁用/启用），并且锁定同一行；
  改不回去的（审核）挑不到待审核数据就 skip，不硬造。

后台五个列表页都是 <div v-if="list.length">…<div v-else class="empty">，
请求回来之前显示的就是空态 —— 所以判断「有没有数据」一律用 o_wait_any
给表格行一段等待时间，不能看到 .empty 就当没有。
"""

import allure
import pytest

from common.component import o_toast, o_wait_any, o_wait_path, o_wait_text, o_wait_texts
from common.operation import (o_all_text, o_click, o_count, o_fill, o_goto, o_press,
                              o_select, o_text, o_value, o_visible, o_wait_visible)
from fixture.session import fresh_student
from page import (adminLayoutPage, applyAuditPage, courseManagePage, headerPage,
                  jobManagePage, orderManagePage, userManagePage)


@pytest.fixture
def pending_audit(admin_page):
    """确认有待审核申请，返回该页面；没有就 skip。

    待审核数据没法凭空造，也造不出一致的历史 —— 挑不到就如实跳过，
    比写一条「点了按钮没报错」的假用例诚实。
    test_08_teacher 每次运行都会提交两条待审核记录，正常跑不会缺。
    """
    o_goto(admin_page, "/admin/apply")
    if o_wait_any(applyAuditPage.locate_pass_btns(admin_page)) == 0:
        pytest.skip("当前没有待审核的申请，先跑 test_08_teacher 造一条")
    return admin_page


@allure.feature("后台")
def test_WEB_TC_107_后台侧栏渲染完整(admin_page):
    o_goto(admin_page, "/admin/apply")
    # 路由组件是异步 import 的，先等布局真的渲染出来再数菜单
    o_wait_text(adminLayoutPage.locate_page_title(admin_page), "申请审核")

    assert o_count(adminLayoutPage.locate_menu_links(admin_page)) == 5, \
        "后台侧栏应该是 5 个菜单项：申请审核 / 用户 / 课程 / 职位 / 订单"
    assert o_visible(adminLayoutPage.locate_side_logo(admin_page))
    assert o_visible(adminLayoutPage.locate_logout_btn(admin_page))
    # 后台没有站点页头，所以这里不该找得到 header 里的 logo
    assert o_count(headerPage.locate_logo(admin_page)) == 0, \
        "后台混进了站点页头（App.vue:16 用 v-if=!isAdmin 挡掉 site header）"


@allure.feature("后台")
def test_WEB_TC_108_进入后台默认落在申请审核(admin_page):
    """router/index.js:30 —— /admin 的 index 子路由 redirect 到 /admin/apply。"""
    o_goto(admin_page, "/admin")
    o_wait_path(admin_page, "/admin/apply")


@allure.feature("后台")
def test_WEB_TC_109_后台五个管理页面都能打开(admin_page):
    """侧栏 5 条路由逐个打开，标题对得上就算通。"""
    expected = {
        "/admin/apply": "申请审核",
        "/admin/users": "用户管理",
        "/admin/courses": "课程管理",
        "/admin/jobs": "职位管理",
        "/admin/orders": "订单管理",
    }
    for path, title in expected.items():
        o_goto(admin_page, path)
        o_wait_text(adminLayoutPage.locate_page_title(admin_page), title)


@allure.feature("后台")
def test_WEB_TC_110_点击侧栏菜单切换页面(admin_page):
    o_goto(admin_page, "/admin/apply")
    o_wait_text(adminLayoutPage.locate_page_title(admin_page), "申请审核")

    o_click(adminLayoutPage.locate_menu_user_manage(admin_page))

    o_wait_path(admin_page, "/admin/users")
    o_wait_text(adminLayoutPage.locate_page_title(admin_page), "用户管理")


@allure.feature("后台-审核")
def test_WEB_TC_111_切到已处理出现状态筛选(admin_page):
    """状态筛选框只在「已处理」tab 下渲染（ApplyAudit.vue:42）。"""
    o_goto(admin_page, "/admin/apply")
    o_click(applyAuditPage.locate_audited_tab(admin_page))

    select = applyAuditPage.locate_status_select(admin_page)
    o_wait_visible(select)

    o_select(select, "1")
    assert o_value(select) == "1"


@allure.feature("后台-审核")
def test_WEB_TC_112_待审核申请点通过(pending_audit):
    """审核不可逆，所以只断言提示，不要求状态回滚。

    toast 按文案过滤：通过/驳回是同屏连着点的，
    直接读第一条会读到上一条的文案。
    """
    o_click(applyAuditPage.locate_pass_btns(pending_audit).first)

    assert o_toast(pending_audit, "已通过") == "已通过"


@allure.feature("后台-审核")
def test_WEB_TC_113_待审核申请点驳回(pending_audit):
    o_click(applyAuditPage.locate_reject_btns(pending_audit).first)

    assert o_toast(pending_audit, "已驳回") == "已驳回"


@allure.feature("后台-用户")
def test_WEB_TC_114_用户管理渲染完整(admin_page):
    o_goto(admin_page, "/admin/users")
    o_wait_text(adminLayoutPage.locate_page_title(admin_page), "用户管理")

    assert o_visible(userManagePage.locate_search_input(admin_page))
    assert o_visible(userManagePage.locate_role_select(admin_page))
    assert o_visible(userManagePage.locate_status_select(admin_page))
    assert o_wait_any(userManagePage.locate_rows(admin_page)) >= 1, \
        "用户管理表格一行都没有——库里连 admin 都没有？"


@allure.feature("后台-用户")
def test_WEB_TC_115_用户管理关键字搜索(admin_page, fresh_student):
    o_goto(admin_page, "/admin/users")
    search = userManagePage.locate_search_input(admin_page)
    o_fill(search, fresh_student["username"])
    o_press(search, "Enter")

    # 搜索是发请求后重渲染的：等"表里只剩这一行"出现，而不是等"有一行"
    usernames = userManagePage.locate_username_texts(admin_page)
    assert o_wait_texts(usernames, {fresh_student["username"]}) == {fresh_student["username"]}


@allure.feature("后台-用户")
def test_WEB_TC_116_用户管理按身份筛选(admin_page):
    """筛「讲师/企业」再筛「学生」，两次都不该混进别的身份。

    先筛讲师是故意的：这一步必定让列表换一次内容，
    后面筛学生时才不会读到还没刷新的旧列表。
    testT01 由 fixture/session.py 的 accounts_ready 保证存在。
    """
    o_goto(admin_page, "/admin/users")
    select = userManagePage.locate_role_select(admin_page)
    roles = userManagePage.locate_role_texts(admin_page)

    o_select(select, "1")
    assert o_wait_texts(roles, {"讲师/企业"}) == {"讲师/企业"}, \
        f"按讲师筛选后混进了其他身份：{set(o_all_text(roles))}"

    o_select(select, "0")
    assert o_wait_texts(roles, {"学生"}) == {"学生"}, \
        f"按学生筛选后混进了其他身份：{set(o_all_text(roles))}"


@allure.feature("后台-用户")
def test_WEB_TC_117_禁用用户后可再启用(admin_page, fresh_student):
    """拿本轮临时注册的账号当靶子，改完再改回去 —— 不碰 testS01。

    utils/status.js：user 的 1 = 正常、0 = 已禁用；
    role=2 的账号不渲染这个按钮（UserManage.vue:53）。

    搜索没返回之前表里是全部用户，这时点 .first 会禁用到别人头上，
    所以必须先把「筛到只剩这一个账号」等出来。
    """
    o_goto(admin_page, "/admin/users")
    search = userManagePage.locate_search_input(admin_page)
    o_fill(search, fresh_student["username"])
    o_press(search, "Enter")

    usernames = userManagePage.locate_username_texts(admin_page)
    assert o_wait_texts(usernames, {fresh_student["username"]}) == {fresh_student["username"]}

    tags = userManagePage.locate_status_tags(admin_page)
    o_wait_text(tags, "正常")

    o_click(userManagePage.locate_disable_btns(admin_page).first)
    assert o_toast(admin_page, "已更新状态") == "已更新状态"
    o_wait_text(tags, "已禁用")

    # 收尾：改回正常，否则这个账号以后就登录不上了
    o_click(userManagePage.locate_enable_btns(admin_page).first)
    o_wait_text(tags, "正常")


@allure.feature("后台-课程")
def test_WEB_TC_118_课程管理渲染与状态筛选(admin_page):
    o_goto(admin_page, "/admin/courses")
    o_wait_text(adminLayoutPage.locate_page_title(admin_page), "课程管理")

    select = courseManagePage.locate_status_select(admin_page)
    o_wait_visible(select)

    o_select(select, "1")
    assert o_value(select) == "1"


@allure.feature("后台-课程")
def test_WEB_TC_119_课程下架后可重新上架(admin_page):
    """挑一门已上架的课程下架、再上架回去，全程锁定这一行。

    为什么要按名字锁行：库里本来就有别的已下架课程时，只点 .first 的话，
    第二步会上架到别人头上，自己那门留在下架态，用例却"通过"了。

    为什么还要 .first：课程名不保证唯一 —— test_08 每轮提交的
    「自动化测试课程」被 TC_112 审核通过后就多一门同名的，跑几轮就有好几条。
    但往返仍然是准的：下架后只有刚点的那一行会出现「上架」按钮，
    所以第二步按「名字 + 上架按钮」能唯一命中它。
    """
    o_goto(admin_page, "/admin/courses")
    offline_btns = courseManagePage.locate_offline_btns(admin_page)
    if o_wait_any(offline_btns) == 0:
        pytest.skip("库里没有已上架的课程，先上架一门再来跑")

    name = o_text(courseManagePage.locate_online_row_names(admin_page).first)

    o_click(courseManagePage.locate_row_offline_btn(admin_page, name).first)
    assert o_toast(admin_page, "已下架") == "已下架"

    online_btn = courseManagePage.locate_row_online_btn(admin_page, name)
    o_wait_text(online_btn, "上架")
    o_click(online_btn.first)
    assert o_toast(admin_page, "已上架") == "已上架"


@allure.feature("后台-职位")
def test_WEB_TC_120_职位上下架往返(admin_page):
    o_goto(admin_page, "/admin/jobs")
    o_wait_text(adminLayoutPage.locate_page_title(admin_page), "职位管理")

    offline_btns = jobManagePage.locate_offline_btns(admin_page)
    if o_wait_any(offline_btns) == 0:
        pytest.skip("库里没有已上架的职位，先上架一条再来跑")

    name = o_text(jobManagePage.locate_online_row_names(admin_page).first)

    o_click(jobManagePage.locate_row_offline_btn(admin_page, name).first)
    assert o_toast(admin_page, "已下架") == "已下架"

    online_btn = jobManagePage.locate_row_online_btn(admin_page, name)
    o_wait_text(online_btn, "上架")
    o_click(online_btn.first)
    assert o_toast(admin_page, "已上架") == "已上架"


@allure.feature("后台-订单")
def test_WEB_TC_121_订单管理渲染与状态筛选(admin_page):
    """订单由 test_05 的下单闭环产生；库里没有就只验证页面骨架。"""
    o_goto(admin_page, "/admin/orders")
    o_wait_text(adminLayoutPage.locate_page_title(admin_page), "订单管理")

    select = orderManagePage.locate_status_select(admin_page)
    o_wait_visible(select)

    o_select(select, "1")
    assert o_value(select) == "1"
