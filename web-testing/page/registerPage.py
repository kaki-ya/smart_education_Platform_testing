def locate_title(page):
    return page.locator("//div[contains(@class,'auth-card')]//h1[contains(@class,'auth-title')]")


def locate_req_tip(page):
    return page.locator("//p[contains(@class,'req-tip')]")


def locate_username(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'用户名')]]/input")


def locate_password(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'密码')]]/input")


def locate_email(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'邮箱')]]/input")


def locate_phone(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'手机号')]]/input")


def locate_role_select(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'身份')]]/select")


def locate_nickname(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'昵称')]]/input")


def locate_submit_btn(page):
    return page.locator("//div[contains(@class,'auth-card')]//button[normalize-space(text())='注册']")


def locate_login_link(page):
    return page.locator("//div[contains(@class,'auth-card')]//a[normalize-space(text())='去登录']")
