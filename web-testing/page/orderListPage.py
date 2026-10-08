def locate_status_select(page):
    return page.locator("//select[contains(@class,'select')]")


def locate_detail_btns(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr//button[normalize-space(text())='详情']")


def locate_pay_btns(page):
    return page.locator(
        "//table[contains(@class,'table')]/tbody/tr"
        "[.//span[contains(@class,'tag--')][normalize-space(text())='待支付']]"
        "//button[normalize-space(text())='支付']"
    )


def locate_cancel_btns(page):
    return page.locator(
        "//table[contains(@class,'table')]/tbody/tr"
        "[.//span[contains(@class,'tag--')][normalize-space(text())='待支付']]"
        "//button[normalize-space(text())='取消']"
    )
