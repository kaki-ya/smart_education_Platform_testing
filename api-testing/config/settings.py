"""全局配置。

所有可调项都留了环境变量的口子：换环境时改环境变量比改代码合适，
代码和默认值一起进版本库，换机器不用动。
"""

import os
from pathlib import Path

# config/settings.py → 上两级才是项目根
ROOT_DIR = Path(__file__).resolve().parent.parent

BASE_URL = os.getenv("SEP_BASE_URL", "http://localhost:8080")
TIMEOUT = float(os.getenv("SEP_TIMEOUT", "10"))

DATA_DIR = ROOT_DIR / "data"
TESTCASE_DIR = ROOT_DIR / "testcases"
REPORTS_DIR = ROOT_DIR / "reports"
ALLURE_RESULTS_DIR = REPORTS_DIR / "allure-results"
ALLURE_REPORT_DIR = REPORTS_DIR / "allure-report"

# 每轮测试一个文件，文件名带时间戳，见 common/logger.py
LOGS_DIR = ROOT_DIR / "logs"

# 被测后端有一条贯穿全项目的约定：
# HTTP 状态码恒为 200，业务结果全部放在响应体的 code 字段里。
# 所以断言不能看状态码，必须解包。
HTTP_OK = 200
SUCCESS_CODE = 200

# 后端 ResultCode 的取值。放这里是为了让断言失败信息能直接说出是哪一类错误，
# 而不是甩一个数字。
CODE_MEANING = {
    200: "成功",
    400: "参数错误",
    401: "未登录或登录已过期",
    403: "无权限",
    500: "系统异常",
}
