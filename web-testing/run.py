"""一键跑 Web 端用例并生成 allure 报告。

    python run.py                 跑全部用例，然后出报告
    python run.py -k TC_119       额外参数原样透传给 pytest
    python run.py -m smoke        只跑标记为冒烟的用例

跑之前前端 dev server 和后端都要起着：
    前端 http://localhost:5173/   后端 http://localhost:8080
fixture/session.py 会先探一遍这两个地址，没起来直接退出（returncode=2），
省得对着满屏的 goto 超时发懵。

一轮跑完留下两样东西，分工不同：
    reports/allure-report/     给「看」的 —— 用例树、通过率、失败截图
    logs/run_<时间戳>.log      给「查」的 —— 页面跳转、接口调用、JS 报错的时间轴

退出码透传自 pytest，所以已知缺陷或失败用例会让它非零 —— 这是预期行为。
"""

import os
import shutil
import subprocess
import sys

from config.settings import ALLURE_REPORT_DIR, ALLURE_RESULTS_DIR, LOGS_DIR, ROOT_DIR


def _print_latest_log() -> None:
    """报出本轮日志文件的路径。

    不调 logger.path()：pytest 是 subprocess 跑的，日志文件是在那个进程里
    建的，这边拿不到它的模块状态 —— 按修改时间挑最新的那个才准。
    """
    if not LOGS_DIR.exists():
        return
    logs = sorted(LOGS_DIR.glob("run_*.log"), key=lambda p: p.stat().st_mtime)
    if logs:
        print(f"运行日志：{logs[-1]}")


def main(argv: list[str]) -> int:
    # 断言信息全是中文，cp936 控制台上会 UnicodeEncodeError，先钉住编码
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    # 上面那个只管子进程。本进程自己的 print 走系统代码页，和 pytest 的 UTF-8
    # 输出混在同一屏里，中文会一半正常一半乱码 —— 这里一并钉成 UTF-8。
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass

    # 用 sys.executable 而不是裸 pytest：没激活 venv 也能跑
    code = subprocess.call(
        [sys.executable, "-m", "pytest", *argv], cwd=ROOT_DIR, env=env
    )

    _print_latest_log()

    if not shutil.which("allure"):
        print("\n没找到 allure 命令，跳过报告生成。测试结果见上面的输出。")
        return code

    # allure 在 Windows 上是 .bat，subprocess 传列表形式起不来，必须走 shell
    subprocess.call(
        f'allure generate "{ALLURE_RESULTS_DIR}" -o "{ALLURE_REPORT_DIR}" --clean',
        cwd=ROOT_DIR,
        shell=True,
    )
    print(f"\n报告已生成：{ALLURE_REPORT_DIR / 'index.html'}")
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
