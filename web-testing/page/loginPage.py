def locate_title(page):
    return page.locator("//div[contains(@class,'auth-card')]//h1[contains(@class,'auth-title')]")


def locate_username(page):
    return page.locator("//input[@placeholder='用户名']")


def locate_password(page):
    return page.locator("//input[@placeholder='密码']")


def locate_login_btn(page):
    return page.locator("//div[contains(@class,'auth-card')]//button[normalize-space(text())='登录']")


def locate_forgot_link(page):
    return page.locator("//div[contains(@class,'auth-card')]//a[normalize-space(text())='忘记密码']")


def locate_register_link(page):
    return page.locator("//div[contains(@class,'auth-card')]//a[normalize-space(text())='注册账号']")
