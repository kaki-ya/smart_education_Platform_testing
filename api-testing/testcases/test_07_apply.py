"""上架申请模块（14 条），用例数据见 data/usercase_apply.yaml。

序号 07：必须排在 job（03）后面 —— TC_apply_001 读的是
TC_job_027 提交的那条职位上架申请。
"""

import allure
import pytest

from common.assert_util import verify
from common.read_yaml import load_cases

CASES = load_cases("apply")


@allure.feature("上架申请模块")
@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_apply(case, client_for):
    # 报告里的用例名默认只有 TC_apply_001 这样的编号，看不出这条在测什么，
    # 把 YAML 里的 title 拼上去，报告目录才能当清单读。
    allure.dynamic.title(f"{case['case_id']} {case['title']}")
    verify(client_for(case["role"]).request(case), case)
