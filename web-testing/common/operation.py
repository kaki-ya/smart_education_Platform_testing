from datetime import datetime
from pathlib import Path

SHOT_DIR = Path(__file__).resolve().parent.parent / "reports" / "screenshots"


# —— 页面 ——

def o_goto(page, url):
    page.goto(url)


def o_reload(page):
    page.reload()


def o_back(page):
    page.go_back()


def o_forward(page):
    page.go_forward()


def o_url(page):
    return page.url


def o_title(page):
    return page.title()


# —— 鼠标 ——

def o_click(sth):
    sth.click()


def o_dblclick(sth):
    sth.dblclick()


def o_right_click(sth):
    sth.click(button="right")


def o_hover(sth):
    sth.hover()


def o_focus(sth):
    sth.focus()


def o_scroll(sth):
    sth.scroll_into_view_if_needed()


# —— 输入 ——

def o_file(sth, context):
    sth.fill(context)


def o_fill(sth, text):
    sth.fill(text)


def o_type(sth, text):
    sth.type(text)


def o_press(sth, key):
    sth.press(key)


def o_clear(sth):
    sth.fill("")


def o_upload(sth, path):
    sth.set_input_files(path)


# —— 下拉 ——

def o_select(sth, value):
    sth.select_option(value)


def o_select_text(sth, label):
    sth.select_option(label=label)


# —— 勾选 ——

def o_check(sth):
    sth.check()


def o_uncheck(sth):
    sth.uncheck()


# —— 取值 ——

def o_text(sth):
    return sth.inner_text()


def o_all_text(sth):
    return sth.all_inner_texts()


def o_value(sth):
    return sth.input_value()


def o_attr(sth, name):
    return sth.get_attribute(name)


def o_count(sth):
    return sth.count()


def o_visible(sth):
    return sth.is_visible()


def o_enabled(sth):
    return sth.is_enabled()


def o_checked(sth):
    return sth.is_checked()


# —— 等待 ——

def o_wait(sth):
    sth.wait_for()


def o_wait_visible(sth):
    sth.wait_for(state="visible")


def o_wait_hidden(sth):
    sth.wait_for(state="hidden")


def o_wait_url(page, url):
    page.wait_for_url(url)


# —— 新标签页 ——

def o_new_page(sth):
    with sth.page.context.expect_page() as p:
        sth.click()
    return p.value


# —— 截图 ——

def o_shot(page, name):
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SHOT_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_{name}.png"
    page.screenshot(path=path, full_page=True)
    return path


def o_error_shot(page, name):
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SHOT_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_ERROR_{name}.png"
    try:
        page.screenshot(path=path, full_page=True)
    except Exception:
        return None
    return path
