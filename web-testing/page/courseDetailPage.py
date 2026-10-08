def locate_title(page):
    return page.locator("//main//h1[contains(@class,'title')]")


def locate_tags(page):
    return page.locator("//main//div[contains(@class,'tags')]/span[contains(@class,'tag')]")


def locate_study_btn(page):
    return page.locator("//aside//button[normalize-space(text())='开始学习']")


def locate_add_cart_btn(page):
    return page.locator("//aside//button[normalize-space(text())='加入购物车']")


def locate_collect_btn(page):
    return page.locator("//aside//button[normalize-space(text())='收藏']")
