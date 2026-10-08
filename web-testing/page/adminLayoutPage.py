def locate_side_logo(page):
    return page.locator("//aside[contains(@class,'side')]//a[contains(@class,'logo')]")


def locate_page_title(page):
    return page.locator("//main[contains(@class,'main')]//h1[contains(@class,'page-title')]")


def locate_menu_links(page):
    return page.locator("//aside[contains(@class,'side')]//nav/a[contains(@class,'link')]")


def locate_menu_apply_audit(page):
    return page.locator("//aside[contains(@class,'side')]//nav/a[normalize-space(text())='申请审核']")


def locate_menu_user_manage(page):
    return page.locator("//aside[contains(@class,'side')]//nav/a[normalize-space(text())='用户管理']")


def locate_menu_course_manage(page):
    return page.locator("//aside[contains(@class,'side')]//nav/a[normalize-space(text())='课程管理']")


def locate_menu_job_manage(page):
    return page.locator("//aside[contains(@class,'side')]//nav/a[normalize-space(text())='职位管理']")


def locate_menu_order_manage(page):
    return page.locator("//aside[contains(@class,'side')]//nav/a[normalize-space(text())='订单管理']")


def locate_logout_btn(page):
    return page.locator("//aside[contains(@class,'side')]//button[normalize-space(text())='退出']")
