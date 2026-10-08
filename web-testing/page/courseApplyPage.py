def locate_title(page):
    return page.locator("//h1[contains(@class,'page-title')]")


def locate_course_name(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'课程名称')]]/input")


def locate_price(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'价格')]]/input")


def locate_cover_image(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'封面图片地址')]]/input")


def locate_course_type_chips(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'课程类型')]]//button[contains(@class,'chip')]")


def locate_tech_system_chips(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'技术体系')]]//button[contains(@class,'chip')]")


def locate_tech_direction_chips(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'技术方向')]]//button[contains(@class,'chip')]")


def locate_course_level_chips(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'课程等级')]]//button[contains(@class,'chip')]")


def locate_free_chip(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'是否免费')]]//button[normalize-space(text())='免费']")


def locate_paid_chip(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'是否免费')]]//button[normalize-space(text())='付费']")


def locate_chapter_names(page):
    return page.locator("//input[@placeholder='章节名称']")


def locate_chapter_durations(page):
    return page.locator("//input[@placeholder='分钟']")


def locate_chapter_video_urls(page):
    return page.locator("//input[@placeholder='视频地址(可选)']")


def locate_chapter_delete_btns(page):
    return page.locator("//div[contains(@class,'chapter-row')]//button[normalize-space(text())='删除']")


def locate_add_chapter_btn(page):
    return page.locator("//button[normalize-space(text())='+ 添加章节']")


def locate_description(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'课程介绍')]]/textarea")


def locate_reason(page):
    return page.locator("//div[@class='field'][label[contains(normalize-space(.),'上架理由')]]/textarea")


def locate_submit_btn(page):
    return page.locator("//button[normalize-space(text())='提交申请']")
