import os
from pathlib import Path

from playwright.sync_api import sync_playwright

# config/settings.py → 上两级才是项目根
ROOT_DIR = Path(__file__).resolve().parent.parent

BASE_URL = "http://localhost:5173/"

# 只在「准备前置数据」时直连后端（注册账号、查课程），不走 UI
API_BASE_URL = "http://localhost:8080"

# 默认等待上限；dev 模式首次编译较慢，给足 10 秒
TIMEOUT = int(os.getenv("SEP_TIMEOUT", "10000"))

#默认测试账号：角色 → 账号密码
# role/phone/email 是账号不存在时按注册接口补建用的
ACCOUNTS = {
    "student": {"username": "testS01", "password": "testpassword", "role": 0,
                "phone": "13900000001", "email": "testS01@test.com"},
    "teacher": {"username": "testT01", "password": "testpassword", "role": 1,
                "phone": "13900000002", "email": "testT01@test.com"},
    "admin": {"username": "admin", "password": "admin123", "role": 2},
}


# —— 运行开关 ——
# 要不要弹出浏览器窗口。改这一行就行：
#   True  = 不弹窗，跑得快，平时用这个
#   False = 弹出窗口，能看着它一步步点
# 临时想看一次不用改这里，命令行加 --headed 就盖过它了。
HEADLESS = False

# 每步操作之间停多久（毫秒），方便肉眼看清动作；0 就是不停。
# 只在上面是 False（有窗口）时才有意义。
SLOW_MO = 0

# 运行日志目录；每轮一个 run_<时间戳>.log（common/logger.py 负责建）
LOGS_DIR = ROOT_DIR / "logs"

REPORTS_DIR = ROOT_DIR / "reports"
# pytest.ini 里 --alluredir 写的是相对路径，落点就是这里的 ALLURE_RESULTS_DIR；
# 原始结果进 allure-results，run.py 再把 HTML 生成到 allure-report
ALLURE_RESULTS_DIR = REPORTS_DIR / "allure-results"
ALLURE_REPORT_DIR = REPORTS_DIR / "allure-report"


#启动playwright
def pwr_start():
    return sync_playwright().start()
