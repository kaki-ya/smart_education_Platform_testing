def locate_study_btns(page):
    return page.locator("//li[contains(@class,'course-item')]//button[normalize-space(text())='去学习']")
