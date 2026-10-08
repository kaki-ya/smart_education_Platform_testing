def locate_item_checkboxes(page):
    return page.locator("//li[contains(@class,'cart-item')]//input[@type='checkbox']")


def locate_item_names(page):
    return page.locator("//li[contains(@class,'cart-item')]//p[contains(@class,'name')]")


def locate_qty_texts(page):
    return page.locator("//li[contains(@class,'cart-item')]//div[contains(@class,'qty')]/span")


def locate_qty_minus_btns(page):
    return page.locator("//li[contains(@class,'cart-item')]//div[contains(@class,'qty')]/button[1]")


def locate_qty_plus_btns(page):
    return page.locator("//li[contains(@class,'cart-item')]//div[contains(@class,'qty')]/button[2]")


def locate_remove_btns(page):
    return page.locator("//li[contains(@class,'cart-item')]//button[normalize-space(text())='移除']")


def locate_checked_hint(page):
    return page.locator("//div[contains(@class,'checkout')]//p[contains(@class,'text-muted')]")


def locate_total_amount(page):
    return page.locator("//div[contains(@class,'checkout')]//strong")


def locate_checkout_btn(page):
    return page.locator("//div[contains(@class,'checkout')]//button[normalize-space(text())='去结算']")
