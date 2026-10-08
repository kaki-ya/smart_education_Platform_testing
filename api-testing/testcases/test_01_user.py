"""用户模块（52 条），用例数据见 data/usercase_user.yaml。

序号 01：必须最先跑 —— 登录注册是一切的前置，而且 user 模块内部
TC_user_013 → TC_user_014 有依赖（先注册 register013，才能测「账号已存在」）。
"""

import allure
import pytest

from common.assert_util import verify
from common.read_yaml import load_cases

CASES = load_cases("user")


@allure.feature("用户模块")
@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_user(case, client_for):
    # 报告里的用例名默认只有 TC_user_001 这样的编号，看不出这条在测什么，
    # 把 YAML 里的 title 拼上去，报告目录才能当清单读。
    allure.dynamic.title(f"{case['case_id']} {case['title']}")
    verify(client_for(case["role"]).request(case), case)
