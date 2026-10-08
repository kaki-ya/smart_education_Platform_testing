"""后台管理模块（20 条），用例数据见 data/usercase_admin.yaml。

序号 08，排最后：前面的模块会造出用户、订单、课程、职位，
管理员用例正好在更完整的数据上跑。
"""

import allure
import pytest

from common.assert_util import verify
from common.read_yaml import load_cases

CASES = load_cases("admin")


@allure.feature("后台管理模块")
@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_admin(case, client_for):
    # 报告里的用例名默认只有 TC_admin_001 这样的编号，看不出这条在测什么，
    # 把 YAML 里的 title 拼上去，报告目录才能当清单读。
    allure.dynamic.title(f"{case['case_id']} {case['title']}")
    verify(client_for(case["role"]).request(case), case)
