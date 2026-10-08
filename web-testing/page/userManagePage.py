def locate_search_input(page):
    return page.locator("//input[@placeholder='搜索用户名/昵称']")


def locate_role_select(page):
    return page.locator("//select[.//option[normalize-space(text())='全部身份']]")


def locate_status_select(page):
    return page.locator("//select[.//option[normalize-space(text())='已禁用']]")


def locate_rows(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr")


def locate_username_texts(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr/td[1]")


def locate_role_texts(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr/td[3]")


def locate_status_tags(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr/td[6]//span[contains(@class,'tag--')]")


def locate_disable_btns(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr//button[normalize-space(text())='禁用']")


def locate_enable_btns(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr//button[normalize-space(text())='启用']")
