def locate_home_btn(page):
    return page.locator("//div[contains(@class,'empty')]//button[normalize-space(text())='回到首页']")
