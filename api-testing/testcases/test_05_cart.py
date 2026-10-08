"""购物车模块（9 条），用例数据见 data/usercase_cart.yaml。

序号 05：必须排在 order（06）前面 —— TC_cart_003 建出的购物车项
会被 TC_order_004 引用。
"""

import allure
import pytest

from common.assert_util import verify
from common.read_yaml import load_cases

CASES = load_cases("cart")


@allure.feature("购物车模块")
@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_cart(case, client_for):
    # 报告里的用例名默认只有 TC_cart_001 这样的编号，看不出这条在测什么，
    # 把 YAML 里的 title 拼上去，报告目录才能当清单读。
    allure.dynamic.title(f"{case['case_id']} {case['title']}")
    verify(client_for(case["role"]).request(case), case)
