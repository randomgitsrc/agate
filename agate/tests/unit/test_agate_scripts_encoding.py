# tests/unit/test_agate_scripts_encoding.py — 测试代码 encoding 守卫 + ASCII 回归
# （agate-scripts-encoding.bats 2 用例迁移，TAG0011 批次 5）
# BDD-5：所有文本 open()/read_text() 必须带 encoding=utf-8（Image.open 与二进制除外）。
#   迁移目标（P2 §3.5 / P3 批次 5）：守卫扫 agate/tests/**/*.py——本文件及全部 test_*.py
#   自身受检（BDD-7）。扫描逻辑用 Python 实现（不调 python3 子进程，避免 R2 命中）。
# bdd-8：agate-state-get.py Linux 纯 ASCII .state.yaml 读取行为不变（S3 回归）。

import re

import pytest


@pytest.mark.windows_smoke
def test_bdd_5_all_test_py_text_io_explicit_encoding(agate_root):
    violations = []
    for f in sorted((agate_root / "tests").rglob("*.py")):
        with open(f, encoding="utf-8", errors="replace") as fh:
            lines = fh.readlines()
        for i, line in enumerate(lines, 1):
            s = line.strip()
            if s.startswith("#") or s.startswith('"""') or s.startswith("'''"):
                continue
            if re.search(r"(?<!Image\.)\bopen\(", line) and "encoding=" not in line and '"rb"' not in line and '"wb"' not in line:
                violations.append(f"{f}:{i}")
            if re.search(r"\.read_text\(", line) and "encoding=" not in line:
                violations.append(f"{f}:{i}")
    assert not violations, "text I/O 缺 encoding: " + "、".join(violations[:30])


def test_bdd_8_state_get_ascii_state_yaml_read(agate_scripts, python_exe, run_cli, tmp_path):
    state_file = tmp_path / ".state.yaml"
    state_file.write_text("task_id: T001\nphase: P1\nstatus: active\nretries: {}\n", encoding="utf-8")

    result = run_cli(
        python_exe,
        str(agate_scripts / "agate-state-get.py"),
        "phase",
        env={"STATE_FILE": str(state_file)},
    )
    assert result.returncode == 0
    assert result.output.strip() == "P1"
