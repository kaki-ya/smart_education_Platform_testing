"""简历模块（5 条），用例数据见 data/usercase_resume.yaml。

后端的简历上传接口是 multipart，而用例 YAML 的请求描述只有 params 和 body
两个字段，表达不了文件字段 —— 所以那一个接口没有被覆盖，如实记在 README 里。
"""

import allure
import pytest

from common.assert_util import verify
from common.read_yaml import load_cases

CASES = load_cases("resume")


@allure.feature("简历模块")
@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_resume(case, client_for):
    # 报告里的用例名默认只有 TC_resume_001 这样的编号，看不出这条在测什么，
    # 把 YAML 里的 title 拼上去，报告目录才能当清单读。
    allure.dynamic.title(f"{case['case_id']} {case['title']}")
    verify(client_for(case["role"]).request(case), case)
