def locate_title(page):
    return page.locator("//h1[contains(@class,'page-title')]")


def locate_search_input(page):
    return page.locator("//input[@placeholder='搜索职位或公司']")


def locate_category_chips(page):
    return page.locator("//div[contains(@class,'chips')]//button[contains(@class,'chip')]")
