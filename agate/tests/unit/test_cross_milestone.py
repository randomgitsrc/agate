# agate/tests/unit/test_cross_milestone.py — BDD-16(M0-M3) 测试平台无关
#
# 被测契约（P1 BDD-16 / P2-design R9 + gate_commands.P5_platform）：
#   任务新增脚本（check-yaml-schema.py / check-structure-consistency.py）不得含裸
#   解释器 / 硬编码 PATH= / `-L` 软链假设 / 临时目录字面量等单平台假设；
#   平台差异场景按分支断言或模拟环境覆盖（check-platform-assumptions.py 扫描兜底）。
#   P3 当下两脚本未实现 → 存在性断言失败 = 真红灯 B 类。
#
# BDD-15 count-tests 只增不减 → 声明（无新 pytest 用例）：由既有 agate/tests/scripts/
# count-tests.sh 机制 + gate_commands.P5_count（每个里程碑血糖）履行——本任务新增测试文件
# 被 pytest collect-only 自动纳入计数，用例数单调不减天然成立，无需重实现计数断言。
#
# 平台无关（本文件自身）：无临时目录字面量、无软链、无裸解释器字面量；文本 I/O 显式 utf-8。

import pytest

_NEW_SCRIPTS = ("check-yaml-schema.py", "check-structure-consistency.py")


@pytest.mark.windows_smoke
def test_bdd_16_new_scripts_exist_and_platform_clean(agate_scripts, python_exe, run_cli):
    """新脚本存在且过 check-platform-assumptions 扫描（R1-R5 零命中）。"""
    for name in _NEW_SCRIPTS:
        script = agate_scripts / name
        assert script.is_file(), f"{name} 未实现（P4 M0 交付）——TDD 红灯锚点"
        result = run_cli(
            python_exe,
            str(agate_scripts / "check-platform-assumptions.py"),
            str(script),
        )
        assert result.returncode == 0, f"{name} 含平台假设（BDD-16 违规）：{result.output}"
