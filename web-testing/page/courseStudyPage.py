def locate_mark_done_btn(page):
    return page.locator("//main//button[normalize-space(text())='标记完成']")


def locate_side_chapters(page):
    return page.locator("//aside//ol[contains(@class,'chapters')]/li")
