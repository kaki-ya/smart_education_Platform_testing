import pytest

from common.operation import o_click, o_fill, o_goto
from common.yaml_util import clean_yaml, update_yaml
from config.settings import ACCOUNTS, BASE_URL
from fixture.plugins import watch
from page.loginPage import locate_login_btn, locate_password, locate_username

TOKEN_FILE = "getToken.yaml"
STORAGE_KEY = "smart_edu_token"


def _login(browser, role):
    account = ACCOUNTS[role]
    context = browser.new_context()
    page = context.new_page()
    watch(page, f"登录-{role}")      # 登录是最容易出问题的一步，它发的请求也要留痕
    try:
        try:
            o_goto(page, f"{BASE_URL}login")
        except Exception as e:
            raise AssertionError(f"打不开 {BASE_URL}login，前端起了吗？{e}") from e

        o_fill(locate_username(page), account["username"])
        o_fill(locate_password(page), account["password"])
        o_click(locate_login_btn(page))

        # 登录成功后是先写 localStorage 再跳转；失败则只弹 toast，2.6 秒后自己消失。
        # 所以两个条件一起等 —— 只等 token 的话，超时时 toast 早没了，只剩一句超时，
        # 看不出到底是密码错还是后端没起。
        try:
            page.wait_for_function(
                f"() => !!localStorage.getItem('{STORAGE_KEY}')"
                " || !!document.querySelector('.toast')",
                timeout=8000,
            )
        except Exception:
            raise AssertionError(
                f"{role}（{account['username']}）点了登录后 8 秒没有反应"
            ) from None

        token = page.evaluate(f"() => localStorage.getItem('{STORAGE_KEY}')")
        if not token:
            reason = page.locator(".toast").first.inner_text()
            raise AssertionError(f"{role}（{account['username']}）登录失败：{reason}")
        return token
    finally:
        context.close()


@pytest.fixture(scope="session")
def tokens(browser):
    """三个角色各登一次，token 写进 data/getToken.yaml。

    先清空再逐个写：上一轮的 token 不会漏进来，中途挂了也能一眼看出缺哪个角色。
    """
    clean_yaml(TOKEN_FILE)
    result = {}
    for role in ACCOUNTS:
        result[role] = _login(browser, role)
        update_yaml(TOKEN_FILE, **{role: result[role]})
    return result
