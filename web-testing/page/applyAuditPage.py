def locate_pending_tab(page):
    return page.locator("//button[normalize-space(text())='待审核']")


def locate_audited_tab(page):
    return page.locator("//button[normalize-space(text())='已处理']")


def locate_status_select(page):
    return page.locator("//select[contains(@class,'select')]")


def locate_rows(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr")


def locate_comment_inputs(page):
    return page.locator("//input[@placeholder='审核意见(可选)']")


def locate_pass_btns(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr//button[normalize-space(text())='通过']")


def locate_reject_btns(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr//button[normalize-space(text())='驳回']")
