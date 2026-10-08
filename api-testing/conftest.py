"""项目根 conftest。

pytest 只自动加载 rootdir 和测试文件所在目录链上的 conftest.py。
`fixtures/` 不在 `testcases/` 的父链上，所以必须在这里显式挂载。

用 `pytest_plugins` 挂整个模块，而不是逐个 import fixture 名字：
逐个重导出时漏掉一个名字，整套会以「fixture not found」全挂，
而报错指向用例，看不出是 conftest 漏了一行。

注意 `pytest_plugins` 只允许出现在根 conftest，写进 `fixtures/conftest.py`
pytest 会直接报错 —— 所以只能走这一条路。
"""

pytest_plugins = ["fixtures.plugins"]
