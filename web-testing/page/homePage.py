def locate_explore_btn(page):
    return page.locator("//section[contains(@class,'hero')]//button[normalize-space(text())='开始探索']")


def locate_find_job_btn(page):
    return page.locator("//section[contains(@class,'hero')]//button[normalize-space(text())='寻找职位']")


def locate_rank_links(page):
    return page.locator("//ol[contains(@class,'rank')]/li//a[contains(@class,'rank-main')]")


def locate_job_rows(page):
    return page.locator("//ul[contains(@class,'jobs')]/li/a[contains(@class,'job-row')]")


def locate_more_course_link(page):
    return page.locator("//a[contains(@class,'more')][normalize-space(text())='查看全部课程']")


def locate_more_job_link(page):
    return page.locator("//a[contains(@class,'more')][normalize-space(text())='查看全部职位']")
