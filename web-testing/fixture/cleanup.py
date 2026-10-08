"""跑完把现场收回来 —— 能撤的按接口撤掉，撤不掉的打一份清单。

web 用例靠「一次性账号」做隔离：买课、下单、传简历都用当轮新注册的
web<时间戳> 学生，跑完就再没人登它。但账号本身和它名下的数据都留在了库里，
而且 test_08 提交的申请被 test_09 审核通过之后，会**真的**多出一门课和一个
职位，直接出现在前台的课程 / 职位列表里。

后端的 controller 里没有任何「删除用户 / 课程 / 职位 / 申请」的接口，
只有 status 类的 PUT（AdminController.java），所以这里能做的边界很清楚：

  能删的     —— 一次性账号名下的购物车、待支付订单、简历，逐条删干净；
  只能改状态 —— 审核通过后生成的那几条「自动化测试课程 / 自动化测试工程师」，
               收尾时下架，前台列表里就看不见了；
  删不掉的   —— 注册出来的一次性账号本身、apply 表里的申请记录、
               已支付的订单（OrderService.cancel 只认 status=0）。
               这些收尾时列出来，要彻底干净只能重置数据库。

清理全程 best-effort：哪一步没成功都只记一笔，绝不让收尾反过来把用例结果搅乱。
"""

import pytest
import requests

from common import logger
from config.settings import ACCOUNTS, API_BASE_URL

# test_08 每轮用的固定名字，审核通过后它们就是库里的真实课程 / 职位
AUTO_COURSE_NAME = "自动化测试课程"
AUTO_JOB_NAME = "自动化测试工程师"

# 本轮注册的一次性账号（fixture/session.py 建号时登记进来）
_fresh_tokens: list = []


def register(token):
    """session.py 每建一个一次性学生就登记一次，收尾时按 token 清它名下的数据。"""
    _fresh_tokens.append(token)


# ---------------------------------------------------------------- HTTP

def _headers(token=None):
    return {"Authorization": f"Bearer {token}"} if token else None


def _call(method, path, token=None, **kwargs):
    """发一次请求，成功（code==200）返回 True。

    收尾阶段一律不抛异常 —— 清理失败不该冒出来盖掉真正的用例结果。
    """
    try:
        body = requests.request(method, f"{API_BASE_URL}{path}",
                                headers=_headers(token), timeout=10, **kwargs).json()
    except Exception:
        return False
    return body.get("code") == 200


def _get(path, token=None, **kwargs):
    """发一次 GET 并返回 data；失败返回 None。"""
    try:
        body = requests.get(f"{API_BASE_URL}{path}",
                            headers=_headers(token), timeout=10, **kwargs).json()
    except Exception:
        return None
    return body.get("data") if body.get("code") == 200 else None


# ------------------------------------------------------------ 一次性账号

def _tidy_student(token):
    """清空这个账号名下的购物车、未支付订单和简历，返回各类销掉的条数。

    只碰 status=0 的订单：OrderService.cancel 对已支付订单会抛
    「仅待支付订单可取消」，那是设计如此，不是要绕过去的东西。
    """
    done = {"购物车": 0, "待支付订单": 0, "简历": 0}

    for row in _get("/api/cart/list", token) or []:
        if _call("DELETE", f"/api/cart/{row['cartId']}", token):
            done["购物车"] += 1

    orders = (_get("/api/order/list", token, params={"status": 0}) or {}).get("list") or []
    for row in orders:
        if _call("POST", f"/api/order/cancel/{row['id']}", token):
            done["待支付订单"] += 1

    for row in _get("/api/resume/list", token) or []:
        if _call("DELETE", f"/api/resume/{row['id']}", token):
            done["简历"] += 1

    return done


# ------------------------------------------------- 审核通过生成的课程 / 职位

def _admin_token():
    acc = ACCOUNTS["admin"]
    try:
        body = requests.post(f"{API_BASE_URL}/api/user/login",
                             json={"username": acc["username"],
                                   "password": acc["password"]}, timeout=10).json()
    except Exception:
        return None
    return (body.get("data") or {}).get("token")


def _retire_audited(kind):
    """把测试申请审核通过后生成的在架课程 / 职位下架。

    没有删除接口，下架是能做到的最接近「回复现场」的动作 —— 下架后前台
    课程中心、职位中心就看不到它们了。
    名字精确匹配，不会碰到库里原有的数据。
    """
    conf = {
        "course": ("/api/admin/course/list", "/api/admin/course/status",
                   "courseName", AUTO_COURSE_NAME),
        "job": ("/api/admin/job/list", "/api/admin/job/status",
                "jobName", AUTO_JOB_NAME),
    }[kind]
    list_path, status_path, field, name = conf

    token = _admin_token()
    if not token:
        return 0

    rows = (_get(list_path, token, params={"keyword": name, "size": 100}) or {}).get("list") or []
    n = 0
    for row in rows:
        if row.get(field) == name and row.get("status") == 1:
            if _call("PUT", f"{status_path}/{row['id']}", token, params={"status": 0}):
                n += 1
    return n


# ---------------------------------------------------------------- 收尾

def _say(text, *args):
    """同一句话写两处：终端上看得见，运行日志里也留一份。"""
    print(text % args if args else text)
    logger.get().info(text, *args)


def _run():
    done = {"购物车": 0, "待支付订单": 0, "简历": 0}
    for token in _fresh_tokens:
        for key, value in _tidy_student(token).items():
            done[key] += value

    courses = _retire_audited("course")
    jobs = _retire_audited("job")

    if not _fresh_tokens and not courses and not jobs:
        return                      # 这轮没产出什么，不刷屏

    line = "=" * 60
    _say(line)
    _say("数据后置清理（回复现场）")
    _say(line)
    _say("  本轮一次性账号     %d 个", len(_fresh_tokens))
    _say("  已清购物车         %d 条", done["购物车"])
    _say("  已取消待支付订单   %d 条", done["待支付订单"])
    _say("  已删简历           %d 份", done["简历"])
    _say("  已下架测试课程     %d 门（%s）", courses, AUTO_COURSE_NAME)
    _say("  已下架测试职位     %d 个（%s）", jobs, AUTO_JOB_NAME)
    _say("-" * 60)
    _say("撤不掉的（后端没有对应接口），要彻底干净只能重置数据库：")
    _say("  · %d 个 web<时间戳> 账号 —— 没有删除用户的接口", len(_fresh_tokens))
    _say("  · apply 表里每轮新增的申请记录 —— 没有删除申请的接口")
    _say("  · 一次性账号名下已支付的订单 —— cancel 只对 status=0 生效")
    _say(line)


@pytest.fixture(scope="session", autouse=True)
def restore_scene():
    """所有用例跑完（不管过没过）执行一次清理。

    这个 fixture 不依赖任何东西，所以最后才拆 —— 拆的时候别的 session
    fixture 都已经收工，不会和它们抢后端。
    """
    yield
    _run()
