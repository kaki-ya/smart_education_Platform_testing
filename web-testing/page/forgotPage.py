def locate_phone(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'手机号')]]/input")


def locate_new_password(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'新密码')]]/input")


def locate_submit_btn(page):
    return page.locator("//div[contains(@class,'auth-card')]//button[normalize-space(text())='重置密码']")


def locate_login_link(page):
    return page.locator("//div[contains(@class,'auth-card')]//a[normalize-space(text())='返回登录']")
