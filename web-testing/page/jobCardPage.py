def locate_cards(page):
    return page.locator("//a[contains(@class,'specimen')]")


def locate_card_names(page):
    return page.locator("//a[contains(@class,'specimen')]//h3[contains(@class,'name')]")
