def locate_logo(page):
    # 必须用 contains：router-link 渲染出的 <a> 会被 Vue Router 插上
    # router-link-active / router-link-exact-active，@class='logo' 精确匹配会落空。
    return page.locator("//header//a[contains(@class,'logo')]")


def locate_nav_links(page):
    return page.locator("//header//nav[@class='nav']/a")


def locate_nav_home(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='首页']")


def locate_nav_course(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='课程']")


def locate_nav_job(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='职位']")


def locate_nav_my_course(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='我的课程']")


def locate_nav_my_applications(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='我的投递']")


def locate_nav_cart(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='购物车']")


def locate_nav_order(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='我的订单']")


def locate_nav_course_apply(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='申请课程']")


def locate_nav_job_apply(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='申请职位']")


def locate_nav_applicants(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='候选人']")


def locate_nav_admin(page):
    return page.locator("//header//nav[@class='nav']/a[normalize-space(text())='后台管理']")


def locate_user_link(page):
    # 不能用 @class='user'：这个链接指向 /user，一旦当前就在 /user 上，
    # Vue Router 会把 active 类插到 class 最前面，精确匹配直接变 0 个。
    return page.locator("//header//div[@class='user-area']/a[contains(@class,'user')]")


def locate_role_tag(page):
    return page.locator("//header//div[@class='user-area']//span[contains(@class,'tag--')]")


def locate_logout_btn(page):
    return page.locator("//header//div[@class='user-area']//button[normalize-space(text())='退出']")


def locate_login_btn(page):
    return page.locator("//header//div[@class='user-area']//button[normalize-space(text())='登录']")


def locate_register_btn(page):
    return page.locator("//header//div[@class='user-area']//button[normalize-space(text())='注册']")
