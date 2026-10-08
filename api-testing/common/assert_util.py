"""自定义断言：拿一个响应去核对 YAML 里写的预期。

用例的期望值全部写在 data/*.yaml 里（except_code / except_message /
except_field），这个模块负责把它们逐层核对掉。用例层只需要调 verify()。

校验用平铺的 assert 写，一条一段，从上往下读就是校验顺序本身。
不用 `if 不成立: raise AssertionError(...)` 那种分支：两者对 pytest 完全等价
（都被当成失败、都带消息），而分支写法要跳到别处才知道失败信息长什么样。
"""

import json

import allure
import yaml

from config.settings import CODE_MEANING, HTTP_OK

_MISSING = object()
"""路径不存在的哨兵。

和 None 分开是为了让失败信息能说清是哪种情况：
「响应里没有 data.purchased 这个字段」和「data.purchased 是 null」
是两回事 —— 前者多半是用例把路径写错了，后者才是接口的真实行为。
"""


# --------------------------------------------------------------------------
# 路径取值
# --------------------------------------------------------------------------

def _resolve(body, dotted: str):
    """'data.list' → body['data']['list']；任一层缺失返回 _MISSING。

    除了字典键，也认列表下标（'data.list.0.id'），免得将来出现列表路径时
    再改一遍。下标越界同样算缺失。
    """
    cur = body
    for seg in dotted.split("."):
        if isinstance(cur, dict):
            if seg not in cur:
                return _MISSING
            cur = cur[seg]
        elif isinstance(cur, list):
            if not seg.lstrip("-").isdigit():
                return _MISSING
            index = int(seg)
            if not -len(cur) <= index < len(cur):
                return _MISSING
            cur = cur[index]
        else:
            return _MISSING
    return cur


# --------------------------------------------------------------------------
# 操作符
# --------------------------------------------------------------------------

def _op_not_null(actual, expected) -> bool:
    """存在且不是 null。空数组、空对象都算通过 ——
    用例 TC_job_021 的注释里明确写了这一点。"""
    return actual is not _MISSING and actual is not None


def _op_not_empty(actual, expected) -> bool:
    if actual is _MISSING or actual is None:
        return False
    try:
        return len(actual) > 0
    except TypeError:
        # int / bool 这类标量没有长度，非 null 就算「非空」
        return True


def _op_eq(actual, expected) -> bool:
    """不加 str() 归一化：那会把 1 和 "1" 混为一谈，反而掩盖真正的类型缺陷。"""
    return actual is not _MISSING and actual == expected


OPERATORS = {
    "not_null": _op_not_null,
    "not_empty": _op_not_empty,
    "==": _op_eq,
}


# --------------------------------------------------------------------------
# except_field 表达式的解析
# --------------------------------------------------------------------------

def _as_list(spec) -> list[str]:
    """except_field 允许写成空格分隔的单个字符串，也允许写成字符串列表。"""
    if spec is None:
        return []
    return [spec] if isinstance(spec, str) else list(spec)


def _parse_expected(text: str):
    """期望值字符串 → Python 值。

    必须用 yaml.safe_load，不能用 ast.literal_eval：用例文件本身是 YAML，
    作者是按 YAML 语义写的 true / false，而 literal_eval("true") 会直接抛
    ValueError（Python 的字面量是 True）。用和文件同一个解析器读，
    才不会出现「YAML 里写 true、断言里当字符串比」这种认知偏差。
    """
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        return text


def _split_expr(expr: str) -> tuple[str, str, object]:
    """切分 `<点号路径> <操作符> [期望值]`。

    用 split(None, 2) 而不是 split(" ")：后者会把连续空格切出空串，
    而且 maxsplit=2 能让第三段原样保留含空格的期望值。

    这里的三处 raise 是「用例文件写错了」的报错，不是断言失败，
    所以照常用 if + raise，不套成 assert。
    """
    parts = expr.split(None, 2)
    if len(parts) < 2:
        raise AssertionError(
            f"except_field 写法不对：{expr!r}\n"
            f"  应为「<点号路径> <操作符> [期望值]」，"
            f"操作符支持 {'、'.join(OPERATORS)}"
        )

    path, op = parts[0], parts[1]
    if op not in OPERATORS:
        raise AssertionError(
            f"except_field 用了不认识的操作符 {op!r}：{expr!r}\n"
            f"  支持的操作符：{'、'.join(OPERATORS)}"
        )
    if op != "==":
        return path, op, None
    if len(parts) < 3:
        raise AssertionError(f"except_field 的 == 少了期望值：{expr!r}")
    return path, op, _parse_expected(parts[2])


# --------------------------------------------------------------------------
# 断言本体
# --------------------------------------------------------------------------

def _short(value, limit: int = 1200) -> str:
    text = json.dumps(value, ensure_ascii=False, default=str)
    if len(text) <= limit:
        return text
    return f"{text[:limit]}…（已截断，完整长度 {len(text)} 字符）"


def _request_lines(case: dict) -> list[str]:
    """把这条用例实际发出去的东西列出来。

    params / body 没写的时候显式写「无」，不留空、也不省略这一行 ——
    TC_course_027 测的就是「缺 courseId」，它失败时「无」本身就是答案。
    省掉这个信息，看的人反而要回去翻 YAML 才知道请求里到底有什么。
    """
    lines = [f"{case['method'].upper()} {case['path']}   [role={case.get('role', 'none')}]"]
    for key in ("params", "body"):
        value = case.get(key)
        lines.append(
            f"{key} = {json.dumps(value, ensure_ascii=False, default=str)}"
            if value else f"{key} = 无"
        )
    return lines


def _expect_text(case: dict) -> str:
    """这条用例在 YAML 里写的预期，原样列出来。

    和 _request_lines 一样，没写的键也要占一行 —— 「没写 except_field」
    本身就解释了「为什么这条用例没比字段」。
    """
    lines = [f"except_code    = {case['except_code']}"]
    lines.append(
        f"except_message = {case['except_message']!r}"
        if case.get("except_message") is not None else "except_message = （未写，不校验）"
    )
    fields = _as_list(case.get("except_field"))
    if fields:
        lines.append("except_field   =")
        lines += [f"  {expr}" for expr in fields]
    else:
        lines.append("except_field   = （未写，不校验）")
    return "\n".join(lines)


def _response_text(resp) -> str:
    """完整响应，缩进后挂成 allure 附件，**不截断**。

    失败信息里那份是 _short() 截过的 —— 控制台要一口气吃下 182 条的失败输出，
    不截会刷屏。附件是点开才看的，没有理由再截。
    """
    return json.dumps(resp.body, ensure_ascii=False, indent=2, default=str)


def _report(case: dict, resp, expect: str, actual: str) -> str:
    """把一次失败整理成分段文本。

    用 `===== xxx =====` 分段，而不是靠缩进对齐：这段文字会同时出现在
    控制台、allure 的失败详情和 logs/ 里，后两处会把首尾空白和缩进吃掉一部分，
    只有显式的分隔线在哪儿都还在。

    段落顺序就是排查顺序：先确认发的是什么，再看预期和实际差在哪，
    最后才需要翻完整响应。
    """
    def section(name: str, body: str | list[str]) -> list[str]:
        rows = [body] if isinstance(body, str) else body
        return [f"===== {name} =====", *rows]

    return "\n".join([
        f"===== {case['case_id']} {case['title']} =====",
        *section("来源", case.get("_source", "（未知）")),
        *section("请求", _request_lines(case)),
        *section("预期", expect),
        *section("实际", actual),
        *section("响应", f"HTTP {resp.status_code}｜{_short(resp.body)}"),
    ])


def _check_field(case: dict, resp, expr: str):
    """核对一条 except_field 表达式，不成立就失败。"""
    path, op, expected = _split_expr(expr)
    actual = _resolve(resp.body, path)
    shown = "响应里没有这个路径" if actual is _MISSING else _short(actual)

    expect_text = f"{path} == {expected!r}" if op == "==" else f"{path} 满足 {op}"
    assert OPERATORS[op](actual, expected), _report(
        case, resp, expect_text, f"{path} 实际是 {shown}")


def verify(resp, case: dict):
    """一条 YAML 用例对应的三层校验。用例层只需要调这一个。

    顺序不能反：
      1. HTTP 必须还是 200 —— 不是的话请求根本没进业务代码（端口占错、
         打到了前端 dev server），此时响应体是 HTML，再去比 code 毫无意义
      2. 业务 code
      3. message / field —— 只在用例写了的时候才比。很多 400 有多个合法
         来源，用例没写就不该比

    整段切成 allure 的两个 step：请求和响应挂成附件，校验单独一个 step。
    报告里因此能点开看这条用例到底发了什么、后端回了什么 —— 光靠失败信息里
    那段截断过的文字是不够定位的。
    """
    with allure.step(f"请求 {case['method'].upper()} {case['path']}"):
        allure.attach("\n".join(_request_lines(case)),
                      "请求", allure.attachment_type.TEXT)
        allure.attach(_expect_text(case), "预期", allure.attachment_type.TEXT)
        allure.attach(_response_text(resp), "响应", allure.attachment_type.JSON)

    with allure.step("校验响应"):
        assert resp.status_code == HTTP_OK, _report(case, resp,
            f"HTTP {HTTP_OK}",
            f"HTTP {resp.status_code}"
            "\n请求没进业务代码，先确认后端地址和端口")

        want, got = case["except_code"], resp.code
        assert got == want, _report(case, resp,
            f"code == {want}（{CODE_MEANING.get(want, '未知')}）",
            f"code == {got}（{CODE_MEANING.get(got, '未知')}）"
            f"\n后端 message：{resp.message}")

        if case.get("except_message") is not None:
            assert resp.message == case["except_message"], _report(case, resp,
                f"message == {case['except_message']!r}",
                f"message == {resp.message!r}")

        for expr in _as_list(case.get("except_field")):
            _check_field(case, resp, expr)
