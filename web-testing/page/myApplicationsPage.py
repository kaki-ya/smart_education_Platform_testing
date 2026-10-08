def locate_detail_links(page):
    return page.locator("//article[contains(@class,'app-card')]//a[contains(@class,'link')]")


def locate_go_job_btn(page):
    return page.locator("//div[@class='empty']//button[normalize-space(text())='去逛一逛职位']")
