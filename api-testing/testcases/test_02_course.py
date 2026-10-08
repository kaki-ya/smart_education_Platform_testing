"""课程模块（30 条），用例数据见 data/usercase_course.yaml。"""

import allure
import pytest

from common.assert_util import verify
from common.read_yaml import load_cases

CASES = load_cases("course")


@allure.feature("课程模块")
@pytest.mark.parametrize("case", CASES, ids=[c["case_id"] for c in CASES])
def test_course(case, client_for):
    # 报告里的用例名默认只有 TC_course_001 这样的编号，看不出这条在测什么，
    # 把 YAML 里的 title 拼上去，报告目录才能当清单读。
    allure.dynamic.title(f"{case['case_id']} {case['title']}")
    verify(client_for(case["role"]).request(case), case)
