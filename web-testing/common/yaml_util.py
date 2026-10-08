from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _resolve(file_path):
    # 只写文件名时按 data/ 找，写全路径就按全路径走
    path = Path(file_path)
    return path if path.is_absolute() else DATA_DIR / path


def read_yaml(file_path):
    path = _resolve(file_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    return loaded if isinstance(loaded, dict) else {}


def write_yaml(file_path, data):
    path = _resolve(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    return path


def update_yaml(file_path, **kwargs):
    data = read_yaml(file_path)
    data.update(kwargs)
    return write_yaml(file_path, data)


def clean_yaml(file_path):
    return write_yaml(file_path, {})
