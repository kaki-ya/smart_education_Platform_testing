"""读取用例 YAML。"""

from pathlib import Path

import yaml

from config.accounts import ANONYMOUS
from config.settings import DATA_DIR

# 每条用例必须有的字段。缺了在加载期就报，不要拖到断言阶段 ——
# 到那时会伪装成「接口返回的字段不存在」，看的人第一反应是接口坏了，
# 而不是用例写错了，排查方向完全相反。
_REQUIRED = ("case_id", "title", "path", "except_code")


def read_yaml(file_path: str | Path) -> dict:
    """读一个 YAML 文件，返回解析后的字典。"""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _case_lines(path: Path) -> list[int]:
    """每条用例在文件里的起始行号（从 1 数）。

    用 yaml.compose 取节点位置，而不是把文件再读一遍去数行 ——
    注释、空行、多行字符串都会让「数行」错位，而用例文件里注释很多
    （每段前面都有 # ===== 分隔），数行必错。

    拿不到就返回空列表，调用方退化成只写文件名。这条路径不影响用例执行，
    所以不值得为它抛异常。
    """
    try:
        root = yaml.compose(path.read_text(encoding="utf-8"))
        top = {key.value: value for key, value in root.value}
        nodes = top["cases"].value
    except (yaml.YAMLError, AttributeError, KeyError, TypeError):
        return []
    return [node.start_mark.line + 1 for node in nodes]


def load_cases(module: str) -> list[dict]:
    """读 `data/usercase_<module>.yaml`，把文件级 defaults 合并进每条用例。

    文件结构是：

        defaults:          # 该文件的默认值，每条用例可各自覆盖
          method: POST
          role: none
        cases:
          - case_id: TC_cart_003
            ...

    合并之后每条用例字段都是齐的，用例层不用再关心 defaults 写没写。

    **顺序保持文件里的书写顺序，不做任何排序。** 用例之间有依赖
    （TC_cart_003 → TC_cart_004、TC_job_009 → TC_job_010），
    而且依赖顺序不等于 case_id 的数字顺序 —— TC_job_021 就写在 TC_job_027 前面。
    """
    path = DATA_DIR / f"usercase_{module}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"找不到用例文件：{path}")

    raw = read_yaml(path) or {}
    defaults = raw.get("defaults") or {}
    lines = _case_lines(path)

    cases = []
    seen = {}
    for index, case in enumerate(raw.get("cases") or [], start=1):
        where = f"{path.name} 第 {index} 条"
        merged = {**defaults, **case}
        merged.setdefault("method", "POST")
        merged.setdefault("role", ANONYMOUS)

        # 失败信息里的「来源」。用例写错了要回去改的时候，这一行省掉一次全局搜索。
        merged["_source"] = (
            f"data/{path.name}:{lines[index - 1]}"
            if index <= len(lines) else f"data/{path.name}（第 {index} 条）"
        )

        missing = [key for key in _REQUIRED if merged.get(key) is None]
        if missing:
            raise ValueError(f"{where} 缺少必填字段 {'、'.join(missing)}：{merged}")
        if merged["case_id"] in seen:
            raise ValueError(
                f"{where} 的 case_id 与第 {seen[merged['case_id']]} 条重复："
                f"{merged['case_id']}"
            )
        seen[merged["case_id"]] = index

        cases.append(merged)
    return cases
