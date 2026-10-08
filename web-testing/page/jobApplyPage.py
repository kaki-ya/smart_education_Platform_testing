def locate_title(page):
    return page.locator("//h1[contains(@class,'page-title')]")


def locate_job_name(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'职位名称')]]/input")


def locate_company_name(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'公司名称')]]/input")


def locate_city(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'城市')]]/input")


def locate_salary_min(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'薪资下限')]]/input")


def locate_salary_max(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'薪资上限')]]/input")


def locate_category_chips(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'职位类别')]]//button[contains(@class,'chip')]")


def locate_education_chips(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'学历要求')]]//button[contains(@class,'chip')]")


def locate_experience_chips(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'经验要求')]]//button[contains(@class,'chip')]")


def locate_duty_inputs(page):
    return page.locator("//input[contains(@placeholder,'负责系统后端开发')]")


def locate_duty_delete_btns(page):
    return page.locator("//div[contains(@class,'duty-row')]//button[normalize-space(text())='删除']")


def locate_add_duty_btn(page):
    return page.locator("//button[normalize-space(text())='+ 添加一条']")


def locate_description(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'职位描述')]]/textarea")


def locate_reason(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'上架理由')]]/textarea")


def locate_submit_btn(page):
    return page.locator("//button[normalize-space(text())='提交申请']")
