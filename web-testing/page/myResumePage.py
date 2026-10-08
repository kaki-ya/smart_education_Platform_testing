def locate_upload_input(page):
    return page.locator("//label[contains(@class,'upload-zone')]//input[@type='file']")


def locate_preview_links(page):
    return page.locator("//li[contains(@class,'resume-item')]//a[normalize-space(text())='预览']")


def locate_delete_btns(page):
    return page.locator("//li[contains(@class,'resume-item')]//button[normalize-space(text())='删除']")
