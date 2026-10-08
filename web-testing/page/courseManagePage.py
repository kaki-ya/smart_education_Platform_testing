def locate_search_input(page):
    return page.locator("//input[@placeholder='搜索课程/讲师']")


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


def locate_row_offline_btn(page, course_name):
    """指定课程那一行的「下架」按钮。

    上下架往返必须锁定同一行：只点 .first 的话，
    库里本来就有别的已下架课程时，第二步会上架到别人头上，
    自己的那门课留在下架态，用例却"成功"了。
    """
    return page.locator(
        "//table[contains(@class,'table')]/tbody/tr"
        f"[.//td[normalize-space(text())='{course_name}']]"
        "//button[normalize-space(text())='下架']"
    )


def locate_row_online_btn(page, course_name):
    return page.locator(
        "//table[contains(@class,'table')]/tbody/tr"
        f"[.//td[normalize-space(text())='{course_name}']]"
        "//button[normalize-space(text())='上架']"
    )
