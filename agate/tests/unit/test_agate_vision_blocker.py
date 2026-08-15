# tests/unit/test_agate_vision_blocker.py — vision YAML blocker_count 读取（agate-vision-blocker.py）
# （agate-vision-blocker.bats 2 用例迁移，TAG0011 批次 9c）
# 被测：agate/scripts/agate-vision-blocker.py，读 YAML_PATH env 指定文件，stdout 输出
#   vision_analysis.summary.blocker_count；无该字段/解析失败输出 -1。
# 流语义（P2 BLOCKER-1）：脚本 stdout print → 精确等值断言统一 .strip()（subprocess 保留尾部
#   换行 vs bats $output 剥离，P2 §3.2 精确等值注意）。

import pytest


def _run_blocker(agate_scripts, python_exe, run_cli, yaml_path):
    return run_cli(
        python_exe,
        str(agate_scripts / "agate-vision-blocker.py"),
        env={"YAML_PATH": str(yaml_path)},
    )


@pytest.mark.windows_smoke
def test_vb_1_read_blocker_count(tmp_path, agate_scripts, python_exe, run_cli):
    yaml_file = tmp_path / "vision.yaml"
    yaml_file.write_text(
        "vision_analysis:\n  summary:\n    blocker_count: 2\n", encoding="utf-8"
    )
    result = _run_blocker(agate_scripts, python_exe, run_cli, yaml_file)
    assert result.returncode == 0
    assert result.output.strip() == "2"


def test_vb_2_missing_blocker_count_minus_1(
    tmp_path, agate_scripts, python_exe, run_cli
):
    yaml_file = tmp_path / "vision.yaml"
    yaml_file.write_text("vision_analysis: {}\n", encoding="utf-8")
    result = _run_blocker(agate_scripts, python_exe, run_cli, yaml_file)
    assert result.returncode == 0
    assert result.output.strip() == "-1"
