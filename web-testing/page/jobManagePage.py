def locate_search_input(page):
    return page.locator("//input[@placeholder='搜索职位/公司']")


def locate_status_select(page):
    return page.locator("//select[contains(@class,'select')]")


def locate_online_row_names(page):
    return page.locator(
        "//table[contains(@class,'table')]/tbody/tr"
        "[.//span[contains(@class,'tag--')][normalize-space(text())='已上架']]/td[1]"
    )


def locate_offline_btns(page):
    return page.locator(
        "//table[contains(@class,'table')]/tbody/tr"
        "[.//span[contains(@class,'tag--')][normalize-space(text())='已上架']]"
        "//button[normalize-space(text())='下架']"
    )


def locate_online_btns(page):
    return page.locator(
        "//table[contains(@class,'table')]/tbody/tr"
        "[.//span[contains(@class,'tag--')][normalize-space(text())='已下架']]"
        "//button[normalize-space(text())='上架']"
    )


def locate_row_offline_btn(page, job_name):
    """指定职位那一行的「下架」按钮，理由同 courseManagePage。"""
    return page.locator(
        "//table[contains(@class,'table')]/tbody/tr"
        f"[.//td[normalize-space(text())='{job_name}']]"
        "//button[normalize-space(text())='下架']"
    )


def locate_row_online_btn(page, job_name):
    return page.locator(
        "//table[contains(@class,'table')]/tbody/tr"
        f"[.//td[normalize-space(text())='{job_name}']]"
        "//button[normalize-space(text())='上架']"
    )
