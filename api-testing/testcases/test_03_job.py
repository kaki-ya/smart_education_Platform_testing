"""职位模块（37 条），用例数据见 data/usercase_job.yaml。

序号 03：必须排在 apply（07）前面 —— TC_job_027 提交的申请会被
TC_apply_001 回读，这是全项目唯一一条真正的跨模块硬依赖。

模块内保持 YAML 的书写顺序，不要按 case_id 编号排序：
TC_job_021 在文件里就写在 TC_job_027 前面。
"""

import allure
import pytest

from common.assert_util import verify
from common.read_yaml import load_cases

CASES = load_cases("job")


@allure.feature("职位模块")
@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_job(case, client_for):
    # 报告里的用例名默认只有 TC_job_001 这样的编号，看不出这条在测什么，
    # 把 YAML 里的 title 拼上去，报告目录才能当清单读。
    allure.dynamic.title(f"{case['case_id']} {case['title']}")
    verify(client_for(case["role"]).request(case), case)
