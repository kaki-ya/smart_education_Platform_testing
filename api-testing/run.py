"""一键跑测试并生成 allure 报告。

    python run.py                 跑全部用例，然后出报告
    python run.py -k TC_cart_003  额外参数原样透传给 pytest

退出码透传自 pytest，所以 4 条已知缺陷会让它非零 —— 这是预期行为。
"""

import os
import shutil
import subprocess
import sys

from config.settings import ALLURE_REPORT_DIR, ALLURE_RESULTS_DIR, ROOT_DIR


def main(argv: list[str]) -> int:
    # 断言信息全是中文，cp936 控制台上会 UnicodeEncodeError，先钉住编码
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}

    # 用 sys.executable 而不是裸 pytest：没激活 venv 也能跑
    code = subprocess.call(
        [sys.executable, "-m", "pytest", *argv], cwd=ROOT_DIR, env=env
    )

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
