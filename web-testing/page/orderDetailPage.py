def locate_order_no(page):
    return page.locator("//p[contains(@class,'order-no')]")


def locate_status_tag(page):
    return page.locator("//div[contains(@class,'panel')]//span[contains(@class,'tag--')]").first


def locate_study_btns(page):
    return page.locator("//table[contains(@class,'table')]/tbody/tr//button[normalize-space(text())='去学习']")


def locate_pay_btn(page):
    return page.locator("//button[normalize-space(text())='立即支付']")


def locate_cancel_btn(page):
    return page.locator("//button[normalize-space(text())='取消订单']")
