def locate_account_text(page):
    return page.locator("//section[contains(@class,'user-card')]//p[contains(@class,'u-sub')]")


def locate_role_badge(page):
    return page.locator("//section[contains(@class,'user-card')]//span[contains(@class,'role-badge')]")


def locate_nickname_text(page):
    return page.locator("//section[contains(@class,'user-card')]//p[contains(@class,'name')]")


def locate_my_apply_link(page):
    return page.locator("//section[contains(@class,'user-card')]//a[normalize-space(text())='我的申请']")


def locate_my_resume_link(page):
    return page.locator("//section[contains(@class,'user-card')]//a[normalize-space(text())='我的简历']")


def locate_my_course_link(page):
    return page.locator("//div[contains(@class,'list-card')]//a[contains(@class,'link')][contains(text(),'全部')]")


def locate_enrolled_card(page):
    return page.locator("//div[contains(@class,'list-card')][.//h3[normalize-space(text())='报名课程']]")


def locate_order_card(page):
    return page.locator("//div[contains(@class,'list-card')][.//h3[normalize-space(text())='订单记录']]")


def locate_enrolled_items(page):
    return page.locator("//div[contains(@class,'list-card')][.//h3[normalize-space(text())='报名课程']]//ul[contains(@class,'list')]/li")


def locate_order_items(page):
    return page.locator("//div[contains(@class,'list-card')][.//h3[normalize-space(text())='订单记录']]//ul[contains(@class,'list')]/li")


def locate_nickname(page):
    return page.locator("//label[normalize-space(text())='昵称']/parent::div/input")


def locate_real_name(page):
    return page.locator("//label[normalize-space(text())='真实姓名']/parent::div/input")


def locate_avatar_input(page):
    return page.locator("//label[normalize-space(text())='头像地址']/parent::div/input")


def locate_save_info_btn(page):
    return page.locator("//button[normalize-space(text())='保存资料']")


def locate_old_password(page):
    return page.locator("//label[normalize-space(text())='原密码']/parent::div/input")


def locate_new_password(page):
    return page.locator("//label[normalize-space(text())='新密码']/parent::div/input")


def locate_save_pwd_btn(page):
    return page.locator("//button[normalize-space(text())='更新密码']")
