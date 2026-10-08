def locate_job_select(page):
    return page.locator("//label[normalize-space(text())='选择职位']/following-sibling::select")


def locate_status_selects(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr//select")


def locate_resume_links(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr//a[contains(@class,'link')]")
