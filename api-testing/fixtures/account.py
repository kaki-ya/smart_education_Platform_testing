"""测试账号引导。

跑测试之前，测试库里可能一个非管理员账号都没有：reset_test_db.sql 里有一句
`DELETE FROM user WHERE role <> 2`，会把 student01 / teacher01 / apitest01
全删掉且不重建，留一个只剩 admin 的基线。

所以这三条账号每轮都得重新建。**这不是数据库重置**（那一步由使用者在
Navicat 里手工执行），这里只是走后端已有的 /api/user/register 接口把账号补齐，
不执行任何 SQL。
"""

from common.request_util import ApiClient
from config.accounts import ACCOUNTS, EXTRA_ACCOUNTS, Account


class AccountBootstrapError(RuntimeError):
    """账号既登不上、也建不出来。"""


def _login(client: ApiClient, account: Account) -> str | None:
    """登录成功返回 token，失败返回 None。"""
    resp = client.post(
        "/api/user/login",
        json={"username": account.username, "password": account.password},
        label=f"账号引导·{account.username}",
    )
    if resp.code == 200:
        return (resp.data or {}).get("token")
    return None


def _register(client: ApiClient, account: Account) -> None:
    client.post("/api/user/register", json=account.register_body,
                label=f"账号引导·{account.username}")


def ensure_account(client: ApiClient, account: Account, label: str) -> str:
    """保证账号可登录，返回 token。

    顺序是「先登录，登不上才注册」而不是直接注册 ——
    直接注册的话，账号已存在会返回 400，而且重置不跑就一直是 400。
    """
    token = _login(client, account)
    if token:
        return token

    if not account.auto_create:
        raise AccountBootstrapError(
            f"{label}（{account.username}）登录失败，而这个账号不由测试创建。\n"
            f"  它由后端 DataInitializer 在 Spring 启动时建出来。\n"
            f"  请确认后端已启动，且测试库里没有把它删掉。"
        )

    _register(client, account)
    token = _login(client, account)
    if token:
        return token

    raise AccountBootstrapError(
        f"{label}（{account.username}）登录失败，注册之后仍然登录失败。\n"
        f"  最常见的原因：库里已存在同名账号，但密码不是 {account.password!r}。\n"
        f"  处理办法二选一：手工执行一次 reset_test_db.sql，"
        f"或者直接删掉这个账号让框架重建。"
    )


def bootstrap(client: ApiClient) -> dict[str, str]:
    """把 ACCOUNTS 和 EXTRA_ACCOUNTS 全部引导成可登录状态。

    返回 {用户名: token}。key 用用户名而不是 role：role 只是用例侧的书写习惯，
    而 apitest01 这种账号在 YAML 里是直接写用户名登录的，不对应任何 role。
    """
    tokens = {}
    for role, account in ACCOUNTS.items():
        tokens[account.username] = ensure_account(client, account, f"role={role}")
    for account in EXTRA_ACCOUNTS:
        tokens[account.username] = ensure_account(client, account, "用例直接登录用的账号")
    return tokens
