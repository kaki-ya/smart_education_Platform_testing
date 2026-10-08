def locate_title(page):
    return page.locator("//h1[contains(@class,'page-title')]")


def locate_search_input(page):
    return page.locator("//input[@placeholder='搜索课程或讲师']")


def locate_sort_select(page):
    return page.locator("//div[contains(@class,'filter')]//select")


def locate_type_chips(page):
    return page.locator("(//div[contains(@class,'chips')])[1]//button[contains(@class,'chip')]")


def locate_level_chips(page):
    return page.locator("(//div[contains(@class,'chips')])[2]//button[contains(@class,'chip')]")


def locate_price_chips(page):
    return page.locator("(//div[contains(@class,'chips')])[3]//button[contains(@class,'chip')]")


def locate_free_chip(page):
    return page.locator("(//div[contains(@class,'chips')])[3]//button[normalize-space(text())='免费']")


def locate_paid_chip(page):
    return page.locator("(//div[contains(@class,'chips')])[3]//button[normalize-space(text())='付费']")
