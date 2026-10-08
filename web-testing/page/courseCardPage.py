def locate_cards(page):
    return page.locator("//a[contains(@class,'specimen')]")


def locate_card_names(page):
    return page.locator("//a[contains(@class,'specimen')]//h3[contains(@class,'name')]")


def locate_card_prices(page):
    return page.locator("//a[contains(@class,'specimen')]//p[contains(@class,'price')]")


def locate_card_type_tags(page):
    return page.locator("//a[contains(@class,'specimen')]//div[contains(@class,'plate')]//span[contains(@class,'tag--')]")
