"""测试账号表。

YAML 用例里的 `role` 是字符串（none / student / teacher / admin），
这里把它映射到具体账号。用例侧永远只写 role 字符串，账号细节封死在这个文件里。

role 的数值映射来自后端：0=学生，1=讲师/企业，2=管理员。
"""

from dataclasses import dataclass

# YAML 里 role 取这个值表示不带 token 的匿名请求
ANONYMOUS = "none"


@dataclass(frozen=True)
class Account:
    username: str
    password: str
    role: int
    phone: str = ""
    email: str = ""
    auto_create: bool = True

    @property
    def register_body(self) -> dict:
        """POST /api/user/register 的请求体。

        phone / email 只在首次注册时用得上，而注册是幂等的
        （账号已存在会返回 400「用户名已存在」），所以不需要额外判重。
        """
        return {
            "username": self.username,
            "password": self.password,
            "phone": self.phone,
            "email": self.email,
            "role": self.role,
        }


# 手机号和邮箱不是随便挑的，几条用例死死依赖这里的取值：
#   TC_user_050  用 13800000001 调忘记密码，注释写着「student01」
#   TC_user_015  用 student01@test.com 注册，期望「该邮箱已被注册」
#   TC_user_045  用 13800000000 调忘记密码，期望「该手机号未注册」
#                —— 所以 13800000000 这个号必须留给它，不能被谁占用
# 改这里之前先搜一遍 data/*.yaml。
ACCOUNTS = {
    "student": Account(
        username="student01",
        password="123456",
        role=0,
        phone="13800000001",
        email="student01@test.com",
    ),
    "teacher": Account(
        username="teacher01",
        password="123456",
        role=1,
        phone="13800000002",
        email="teacher01@test.com",
    ),
    # admin 是后端 DataInitializer 在 Spring 启动时建的，测试不动它。
    # 也建不出来：注册接口只放 role 0 和 1。
    "admin": Account(
        username="admin",
        password="admin123",
        role=2,
        auto_create=False,
    ),
}


# 用例里直接用用户名登录、但不对应任何 role 的账号。
# 见 data/usercase_user.yaml 的登录段：那一段的 role 都是 none，
# 而登录接口本身是公开的，所以这条账号不属于任何 role 客户端。
EXTRA_ACCOUNTS = [
    Account(
        username="apitest01",
        password="1234567",
        role=0,
        phone="13800000003",
        email="apitest01@test.com",
    ),
]
