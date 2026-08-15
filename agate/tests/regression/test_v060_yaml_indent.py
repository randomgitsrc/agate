# tests/regression/test_v060_yaml_indent.py — 回归测试：task-files.md YAML 缩进
# （v060-yaml-indent.bats 3 用例迁移，TAG0011 批次 11）
# 触发：b028315 "feat(v0.6): 模型选择" 提交时多打空格，executor_env: 块从 2 空格变成 3 空格
# 影响：YAML 解析失败 → check-protocol-consistency.py CHECK 1 红 → CI 失败。
# 迁移：bats 经 `awk`/`grep -n`/`sed -n`/管道读 agate_root/assets/templates/task-files.md——
#   pytest 用 agate_root fixture + read_text(encoding="utf-8") 等价；R1.1 的 awk range
#   （/^executor_env:/,/^[a-z_]+:/，首行即同时匹配起止 → 块=单行）用同语义循环复刻。

import re

import pytest
import yaml


def _task_files_lines(agate_root):
    path = agate_root / "assets" / "templates" / "task-files.md"
    return path.read_text(encoding="utf-8").splitlines()


def _executor_env_block(lines):
    """bats `awk '/^executor_env:/,/^[a-z_]+:/' | head -10` 等价（含首行即终止的 range 语义）。"""
    block = []
    active = False
    for line in lines:
        if not active:
            if re.match(r"^executor_env:", line):
                active = True
            else:
                continue
        block.append(line)
        if re.match(r"^[a-z_]+:", line):
            active = False
        if len(block) >= 10:
            break
    return "\n".join(block)


@pytest.mark.windows_smoke
def test_r1_1_executor_env_yaml_parses(agate_root):
    block = _executor_env_block(_task_files_lines(agate_root))
    yaml.safe_load(block)


def test_r1_2_executor_env_no_leading_space(agate_root):
    lines = _task_files_lines(agate_root)
    assert not any(re.match(r"^ executor_env:", line) for line in lines)


def test_r1_3_executor_env_children_two_space_indent(agate_root):
    lines = _task_files_lines(agate_root)
    idx = next(i for i, line in enumerate(lines) if re.match(r"^executor_env:", line))
    for i in range(1, 6):
        line_idx = idx + i
        actual = lines[line_idx] if line_idx < len(lines) else ""
        assert re.match(r"^  [a-z_]+:", actual), f"第 {line_idx + 1} 行缩进异常: {actual}"
