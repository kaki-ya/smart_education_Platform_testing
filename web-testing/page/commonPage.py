def locate_prev_page_btn(page):
    return page.locator("//div[@class='pagination']//button[normalize-space(text())='上一页']")


def locate_next_page_btn(page):
    return page.locator("//div[@class='pagination']//button[normalize-space(text())='下一页']")


def locate_back_btn(page):
    return page.locator("//div[contains(@class,'backbar')]//button[contains(@class,'back-btn')]")
