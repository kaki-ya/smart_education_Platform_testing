"""requests 请求封装。

用例层不该出现 `requests.get` / `requests.post` —— 一条用例就是一次请求，
method / path / params / body 全部来自 YAML，所以这里给出去的是
「按用例发一次请求」，而不是把 requests 再转包一层。
"""

import json
import time

import requests

from common import logger
from config.settings import BASE_URL, TIMEOUT


class ApiError(RuntimeError):
    """请求没能正常收发（连不上、超时、响应不是 JSON）。"""


def _brief(params, body, limit: int = 300) -> str:
    """把 params / body 压成一行塞进日志。

    截断到 limit：日志是给人顺着时间轴翻的，一条请求占掉半屏就失去意义了。
    完整内容在 allure 的用例详情里，那边本来就该是全文。
    """
    parts = []
    if params:
        parts.append(f"params={json.dumps(params, ensure_ascii=False, default=str)}")
    if body:
        parts.append(f"body={json.dumps(body, ensure_ascii=False, default=str)}")
    if not parts:
        return ""
    text = "  ".join(parts)
    if len(text) > limit:
        text = f"{text[:limit]}…（已截断，共 {len(text)} 字符）"
    return f"  {text}"


class ApiResponse:
    """解包后的响应。用例和断言只跟它打交道。

    直接返回 requests.Response 的话，每条用例都得自己写一遍
    `.json()["code"]`，等于把「响应长什么样」这件事散到 182 个地方。
    """

    __slots__ = ("status_code", "body", "code", "message", "data", "raw")

    def __init__(self, resp: requests.Response, request_desc: str):
        self.raw = resp
        self.status_code = resp.status_code
        try:
            self.body = resp.json()
        except ValueError:
            # 打到了别的服务（前端 dev server、Spring 的 404 页面……），
            # 返回的是 HTML。此时再取 code 毫无意义，这里直接给可读的错误。
            raise ApiError(
                f"{request_desc} 的响应不是 JSON（HTTP {resp.status_code}）：\n"
                f"{resp.text[:300]}"
            ) from None
        self.code = self.body.get("code")
        self.message = self.body.get("message")
        self.data = self.body.get("data")

    def __repr__(self) -> str:
        return (
            f"<ApiResponse HTTP {self.status_code} "
            f"code={self.code} message={self.message!r}>"
        )


class ApiClient:
    """一个身份的 HTTP 客户端：拼 BASE_URL、注入 Bearer、统一超时。

    token 存在实例上，不往 Session 的 header 里塞全局值 ——
    **一个 role 一个实例**，匿名客户端的 token 恒为 None。
    共用 Session 的话，匿名用例会被上一条的登录态污染，期望的
    「未登录」会变成「登录已过期」，报错原因和实际原因完全不同。
    """

    def __init__(self, token: str | None = None, base_url: str = BASE_URL,
                 timeout: float = TIMEOUT):
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def request(self, case: dict) -> ApiResponse:
        """按一条 YAML 用例发请求。用例层调的就是这一个方法。"""
        return self.call(
            case["method"],
            case["path"],
            params=case.get("params"),
            json=case.get("body"),
            label=case["case_id"],       # 日志里靠它把请求和用例对上
        )

    def call(self, method: str, path: str, *, params=None, json=None,
             label: str | None = None) -> ApiResponse:
        """底层出入口。fixtures 里的登录注册走这里。

        label 只影响日志——传 case_id 或「账号引导」这类短标签，
        不传也能跑。日志里没有它的话，几十条请求连成一片，分不清谁是谁。
        """
        url = self.base_url + path
        desc = f"{method.upper()} {path}"
        log = logger.get()
        tag = f"[{label}] " if label else ""

        log.info("%s→ %s %s%s", tag, method.upper(), path, _brief(params, json))

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else None
        started = time.perf_counter()
        try:
            resp = self.session.request(
                method.upper(), url,
                params=params, json=json, headers=headers, timeout=self.timeout,
            )
        except requests.RequestException as exc:
            log.error("%s✗ 请求失败：%s（目标 %s）", tag, exc, url)
            raise ApiError(
                f"{desc} 请求失败：{exc}\n  目标地址：{url}"
                "\n  后端起了吗？"
            ) from exc
        elapsed_ms = (time.perf_counter() - started) * 1000

        try:
            parsed = ApiResponse(resp, desc)
        except ApiError as exc:
            log.error("%s✗ %s", tag, exc)
            raise

        log.info("%s← HTTP %s code=%s message=%s（%.0fms）",
                 tag, parsed.status_code, parsed.code, parsed.message, elapsed_ms)
        return parsed

    def get(self, path: str, **kw) -> ApiResponse:
        return self.call("GET", path, **kw)

    def post(self, path: str, **kw) -> ApiResponse:
        return self.call("POST", path, **kw)

    def put(self, path: str, **kw) -> ApiResponse:
        return self.call("PUT", path, **kw)

    def delete(self, path: str, **kw) -> ApiResponse:
        return self.call("DELETE", path, **kw)

    def close(self) -> None:
        self.session.close()
