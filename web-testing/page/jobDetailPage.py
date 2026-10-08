def locate_title(page):
    return page.locator("//main//h1[contains(@class,'title')]")


def locate_interview_btn(page):
    return page.locator("//aside//button[normalize-space(text())='参加 AI 面试']")


def locate_apply_btn(page):
    return page.locator("//aside//button[normalize-space(text())='投递简历']")


def locate_collect_btn(page):
    return page.locator("//aside//button[normalize-space(text())='收藏']")


def locate_modal_title(page):
    return page.locator("//div[contains(@class,'modal-head')]/h3")


def locate_modal_tip(page):
    return page.locator("//p[contains(@class,'modal-tip')]")


def locate_modal_empty(page):
    return page.locator("//p[contains(@class,'modal-empty')]")


def locate_modal_close_btn(page):
    return page.locator("//div[contains(@class,'modal-head')]//button[contains(@class,'close')]")


def locate_resume_opts(page):
    return page.locator("//div[contains(@class,'resume-opts')]//label[contains(@class,'opt')]")


def locate_resume_preview_links(page):
    return page.locator("//div[contains(@class,'resume-opts')]//a[contains(@class,'opt-preview')]")


def locate_upload_input(page):
    return page.locator("//label[contains(@class,'upload-inline')]//input[@type='file']")


def locate_modal_cancel_btn(page):
    return page.locator("//div[contains(@class,'modal-foot')]//button[normalize-space(text())='取消']")


def locate_confirm_apply_btn(page):
    return page.locator("//div[contains(@class,'modal-foot')]//button[normalize-space(text())='确认投递']")
