def locate_back_job_btn(page):
    return page.locator("//div[contains(@class,'result')]//button[normalize-space(text())='返回职位列表']")


def locate_answer_textareas(page):
    return page.locator("//div[contains(@class,'panel')]//div[@class='field']/textarea")


def locate_submit_btn(page):
    return page.locator("//button[normalize-space(text())='提交回答']")
