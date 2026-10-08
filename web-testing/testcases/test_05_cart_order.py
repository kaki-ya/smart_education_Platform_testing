"""购物车与下单支付闭环 —— WEB_TC_055 ~ WEB_TC_068

被测页面：views/Cart.vue、views/order/OrderList.vue、OrderDetail.vue
页面对象：page/cartPage.py、orderListPage.py、orderDetailPage.py

每条用例都用 fresh_student_page（本轮新注册的学生）而不是 testS01：
购买是一次性的，第二次执行时那门课已经在「我的课程」里，
详情页按钮从「加入购物车」变成「开始学习」，用例就再也跑不通了。
"""

import allure
import pytest

from common.component import (o_empty, o_path, o_toast, o_wait_any, o_wait_path,
                              o_wait_path_prefix, o_wait_text)
from common.operation import (o_click, o_count, o_goto, o_select, o_text, o_uncheck,
                              o_value, o_visible)
from fixture.session import first_course
from page import cartPage, courseDetailPage, myCoursePage, orderDetailPage, orderListPage


@pytest.fixture
def paid_course():
    return first_course(is_free=0)


def _price_of(course):
    return float(course["price"])


def _money(course, qty=1):
    """购物车合计的展示格式，来自 Cart.vue:12 的 toFixed(2)。"""
    return f"¥{_price_of(course) * qty:.2f}"


def _add_to_cart(page, course):
    """详情页加购 → 停在购物车，且购物车里正好 1 件。

    路径变过去 ≠ 列表渲染好：购物车是 onMounted 里现拉接口的（Cart.vue:14），
    刚跳到 /cart 那一帧 items 还是空数组。o_count 取的是瞬时值、不会等，
    直接断言必然读到 0（偶尔接口快就碰巧过，是最难查的那种偶发）。
    """
    o_goto(page, f"/course/{course['id']}")
    o_click(courseDetailPage.locate_add_cart_btn(page))
    o_wait_path(page, "/cart")
    assert o_wait_any(cartPage.locate_item_names(page)) == 1, "加购后购物车里没有商品"


def _checkout(page):
    """点去结算 → 等落到 /order/<新建的 id>。

    订单 id 是下单那一刻才生成的，跳转前无从得知，所以只能等前缀。
    """
    o_click(cartPage.locate_checkout_btn(page))
    assert o_toast(page, "订单已创建") == "订单已创建"
    path = o_wait_path_prefix(page, "/order/")
    assert path.rsplit("/", 1)[-1].isdigit(), f"订单 id 不是数字：{path}"
    return path


def _buy_and_pay(page, course):
    """加购 → 结算 → 支付，停在已支付的订单详情页。"""
    _add_to_cart(page, course)
    _checkout(page)
    o_click(orderDetailPage.locate_pay_btn(page))
    assert o_toast(page, "支付成功") == "支付成功"
    o_wait_text(orderDetailPage.locate_status_tag(page), "已支付")


@allure.feature("购物车")
def test_WEB_TC_055_空购物车展示空态(fresh_student_page):
    o_goto(fresh_student_page, "/cart")
    assert o_empty(fresh_student_page) == "购物车还是空的，去挑几门课吧"


@allure.feature("购物车")
def test_WEB_TC_056_加入购物车后跳购物车(fresh_student_page, paid_course):
    """CourseDetail.vue:29 加购成功后直接 router.push('/cart')。"""
    _add_to_cart(fresh_student_page, paid_course)

    assert o_text(cartPage.locate_item_names(fresh_student_page)) == paid_course["courseName"]
    assert o_count(cartPage.locate_item_checkboxes(fresh_student_page)) == 1, \
        "购物车里那件商品没有勾选框，行结构不对"


@allure.feature("购物车")
def test_WEB_TC_057_未勾选商品结算被拦(fresh_student_page, paid_course):
    """Cart.vue:30 没勾选只提示，不发创建订单的请求。"""
    _add_to_cart(fresh_student_page, paid_course)
    o_uncheck(cartPage.locate_item_checkboxes(fresh_student_page).first)

    o_click(cartPage.locate_checkout_btn(fresh_student_page))

    assert o_toast(fresh_student_page, "请先勾选要结算的课程") == "请先勾选要结算的课程"
    assert o_path(fresh_student_page) == "/cart"


@allure.feature("购物车")
def test_WEB_TC_058_勾选后合计金额正确(fresh_student_page, paid_course):
    _add_to_cart(fresh_student_page, paid_course)

    assert o_text(cartPage.locate_checked_hint(fresh_student_page)) == "已选 1 件"
    assert o_text(cartPage.locate_total_amount(fresh_student_page)) == _money(paid_course)


@allure.feature("购物车")
def test_WEB_TC_059_数量加一后合计翻倍(fresh_student_page, paid_course):
    _add_to_cart(fresh_student_page, paid_course)

    o_click(cartPage.locate_qty_plus_btns(fresh_student_page).first)

    o_wait_text(cartPage.locate_qty_texts(fresh_student_page).first, "2")
    assert o_text(cartPage.locate_total_amount(fresh_student_page)) == _money(paid_course, 2)


@allure.feature("购物车")
def test_WEB_TC_060_数量减到1后不再减少(fresh_student_page, paid_course):
    """Cart.vue:21 用 Math.max(1, ...) 兜底，购物车里不会出现 0 件。"""
    _add_to_cart(fresh_student_page, paid_course)

    minus = cartPage.locate_qty_minus_btns(fresh_student_page).first
    o_click(minus)
    o_click(minus)

    assert o_text(cartPage.locate_qty_texts(fresh_student_page).first) == "1"


@allure.feature("购物车")
def test_WEB_TC_061_移除商品后回到空态(fresh_student_page, paid_course):
    _add_to_cart(fresh_student_page, paid_course)

    o_click(cartPage.locate_remove_btns(fresh_student_page).first)

    assert o_toast(fresh_student_page, "已移除") == "已移除"
    assert o_empty(fresh_student_page) == "购物车还是空的，去挑几门课吧"


@allure.feature("订单")
def test_WEB_TC_062_结算成功创建订单并跳详情(fresh_student_page, paid_course):
    _add_to_cart(fresh_student_page, paid_course)

    path = _checkout(fresh_student_page)

    assert path.startswith("/order/")


@allure.feature("订单")
def test_WEB_TC_063_订单详情展示订单号与待支付状态(fresh_student_page, paid_course):
    _add_to_cart(fresh_student_page, paid_course)
    _checkout(fresh_student_page)

    assert o_text(orderDetailPage.locate_order_no(fresh_student_page)).strip() != ""
    assert o_text(orderDetailPage.locate_status_tag(fresh_student_page)) == "待支付"
    assert o_visible(orderDetailPage.locate_pay_btn(fresh_student_page))
    assert o_visible(orderDetailPage.locate_cancel_btn(fresh_student_page))


@allure.feature("订单")
def test_WEB_TC_064_我的订单列表渲染(fresh_student_page, paid_course):
    _add_to_cart(fresh_student_page, paid_course)
    _checkout(fresh_student_page)

    o_goto(fresh_student_page, "/order")

    # 订单列表同样是进页面才拉的，等它渲染出来再数
    assert o_wait_any(orderListPage.locate_detail_btns(fresh_student_page)) == 1, \
        "刚下完单，我的订单列表里却没有这条订单"


@allure.feature("订单")
def test_WEB_TC_065_订单列表按状态筛选(fresh_student_page):
    """新账号没有订单；筛「已支付」时列表应为空。"""
    o_goto(fresh_student_page, "/order")
    select = orderListPage.locate_status_select(fresh_student_page)

    o_select(select, "1")

    assert o_value(select) == "1"
    assert o_empty(fresh_student_page, contains="还没有订单")


@allure.feature("订单")
def test_WEB_TC_066_立即支付成功(fresh_student_page, paid_course):
    _add_to_cart(fresh_student_page, paid_course)
    _checkout(fresh_student_page)

    o_click(orderDetailPage.locate_pay_btn(fresh_student_page))

    assert o_toast(fresh_student_page, "支付成功") == "支付成功"
    o_wait_text(orderDetailPage.locate_status_tag(fresh_student_page), "已支付")


@allure.feature("订单")
def test_WEB_TC_067_支付后订单详情出现去学习(fresh_student_page, paid_course):
    """OrderDetail.vue:45 只有 status===1 才渲染「去学习」按钮。"""
    _buy_and_pay(fresh_student_page, paid_course)

    assert o_wait_any(orderDetailPage.locate_study_btns(fresh_student_page)) == 1, \
        "订单已是「已支付」，详情页却没出现「去学习」（OrderDetail.vue:45 只在 status===1 时渲染）"


@allure.feature("订单")
def test_WEB_TC_068_支付后我的课程出现该课程(fresh_student_page, paid_course):
    """完整闭环：加购 → 结算 → 支付 → 我的课程里有它。"""
    _buy_and_pay(fresh_student_page, paid_course)

    o_goto(fresh_student_page, "/user/my-course")

    # 顺序不能反：先等课程卡出来，再断言没有空态。
    # 反过来的话加载中的那一帧显示的正好就是空态，断言会误判。
    assert o_wait_any(myCoursePage.locate_study_btns(fresh_student_page)) == 1, \
        "支付成功了，「我的课程」里却没有这门课"
    assert o_empty(fresh_student_page) is None, "有已购课程时不该再显示空态"
