def locate_search_input(page):
    return page.locator("//input[@placeholder='搜索订单号']")


def locate_status_select(page):
    return page.locator("//select[contains(@class,'select')]")
