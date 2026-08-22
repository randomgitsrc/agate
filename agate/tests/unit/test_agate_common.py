# tests/unit/test_agate_common.py — agate_common 公共函数单测
# （TAG0017/DEBT0010 新增：is_gate_meta_key 判据直接单测；TAG0020 增补：
#   append_event / read_judge_verdict / GENESIS_HASH，BDD-7 写侧 + BDD-5 读取侧）
# 被测：agate/scripts/agate_common.py 的 is_gate_meta_key（P2 候选方案 A，拟插入点
# probe_python() 附近，见 P2-design.md §1.1）。语义：
#   key.endswith(("_formatter", "_timeout_seconds")) —— 仅排除这两个已知固定后缀，
#   不做通配/正则宽松匹配（P1 R3 风险条目：防止把 DEBT0010 修复做成"所有非常规 key 都忽略"，
#   连真正需要核实/计入的 key 也一并放宽）。
#
# 当前 agate_common.py 尚不存在该函数 → `from agate_common import is_gate_meta_key`
# 直接触发 ImportError（真实的项目内 import 失败 = B 类红灯语义），非测试代码自身语法错误。
#
# 复用项目既有 subprocess -c 调用惯例（test_helpers_python.py `_probe_code` 同款），
# 不在 pytest 自身进程内直接 `import agate_common`（避免与其他用例共享/污染 sys.path）。

import hashlib

import pytest


def _check_code(key):
    return (
        "from agate_common import is_gate_meta_key; "
        f"print(is_gate_meta_key({key!r}))"
    )


@pytest.mark.parametrize(
    "key",
    ["P3_formatter", "P5_formatter", "P3_html_formatter", "P5_js_formatter"],
)
def test_bdd_4_is_gate_meta_key_formatter_suffix_true(python_exe, run_cli, agate_scripts, key):
    """`_formatter` 后缀键（既有排除逻辑，未受 DEBT0010 影响）应仍判定为元信息 key。"""
    result = run_cli(python_exe, "-c", _check_code(key), env={"PYTHONPATH": str(agate_scripts)})
    assert result.returncode == 0
    assert result.output.strip() == "True"


@pytest.mark.parametrize(
    "key",
    ["P3_timeout_seconds", "P5_timeout_seconds", "P3_html_timeout_seconds"],
)
def test_bdd_1_is_gate_meta_key_timeout_seconds_suffix_true(python_exe, run_cli, agate_scripts, key):
    """`_timeout_seconds` 后缀键（DEBT0010 核心目标）必须判定为元信息 key，不被当作待核实命令。"""
    result = run_cli(python_exe, "-c", _check_code(key), env={"PYTHONPATH": str(agate_scripts)})
    assert result.returncode == 0
    assert result.output.strip() == "True"


@pytest.mark.parametrize(
    "key",
    ["P3", "P5", "P3_html", "project_module", "P3_timeout"],
)
def test_bdd_2_is_gate_meta_key_ordinary_key_false(python_exe, run_cli, agate_scripts, key):
    """普通命令 key（含前缀相似但非完整 `_timeout_seconds` 后缀的 `P3_timeout`）不得被误排除——
    R3 护栏：防止修复把判据放宽为通配匹配，导致真实命令 key 被静默吞掉。"""
    result = run_cli(python_exe, "-c", _check_code(key), env={"PYTHONPATH": str(agate_scripts)})
    assert result.returncode == 0
    assert result.output.strip() == "False"


# ─────────────────────────────────────────────
# TAG0020 增补：append_event / read_judge_verdict（BDD-7 写侧 + BDD-5 读取侧）
#   append_event(task_dir, event)：自动补 ts + prev_hash，首行 prev_hash=GENESIS_HASH，
#     行尾追加、ts 单调兜底（P2-design §3.2）；read_judge_verdict(task_dir)：frontmatter
#     解析返回 dict / 缺失返回 None。
# 未实现 → `from agate_common import append_event/read_judge_verdict/GENESIS_HASH`
#   触发 ImportError（真实 B 类红灯）。

_APPEND_FIRST = (
    "import json, sys; "
    "from agate_common import append_event, GENESIS_HASH; "
    "td = sys.argv[1]; "
    "append_event(td, {'event': 'gate_run', 'phase': 'P6', 'cmd': 'check-gate.py P6', 'exit': 0, 'runner': 'test'}); "
    "line = open(td + '/gate-events.jsonl', encoding='utf-8').readline().rstrip('\\n'); "
    "obj = json.loads(line); "
    "print(obj['prev_hash']); print(GENESIS_HASH); print(bool(obj['ts']))"
)

_APPEND_TWO = (
    "import hashlib, json, sys; "
    "from agate_common import append_event; "
    "td = sys.argv[1]; "
    "append_event(td, {'event': 'gate_run', 'phase': 'P6', 'cmd': 'check-gate.py P6', 'exit': 0, 'runner': 'test'}); "
    "append_event(td, {'event': 'state_transition', 'phase': 'P6.5', 'from': 'P6', 'to': 'P7'}); "
    "lines = open(td + '/gate-events.jsonl', encoding='utf-8').readlines(); "
    "second = json.loads(lines[1]); "
    "raw_first = lines[0].rstrip('\\n'); "
    "print(second['prev_hash'] == hashlib.sha256(raw_first.encode('utf-8')).hexdigest()); "
    "print(len(lines))"
)

_APPEND_TS_FALLBACK = (
    "import hashlib, json, sys; "
    "from agate_common import append_event; "
    "td = sys.argv[1]; "
    "tail = {'ts': '2099-01-01T00:00:00.000000Z', 'event': 'gate_run', 'phase': 'P6', 'cmd': 'x', 'exit': 0, 'runner': 'test', 'prev_hash': hashlib.sha256(b'').hexdigest()}; "
    "open(td + '/gate-events.jsonl', 'w', encoding='utf-8').write(json.dumps(tail, sort_keys=True) + '\\n'); "
    "append_event(td, {'event': 'state_transition', 'phase': 'P6.5', 'from': 'P6', 'to': 'P7'}); "
    "lines = open(td + '/gate-events.jsonl', encoding='utf-8').readlines(); "
    "second = json.loads(lines[1]); "
    "print(second['ts'] >= tail['ts']); "
    "print(second['prev_hash'] == hashlib.sha256(lines[0].rstrip('\\n').encode('utf-8')).hexdigest())"
)

_READ_VERDICT = (
    "import sys; "
    "from agate_common import read_judge_verdict; "
    "v = read_judge_verdict(sys.argv[1]); "
    "print(v['status']); print(v['criteria_total']); print(v['criteria_passed']); print(bool(v['verdict_evidence'])); print(v['partial'])"
)

_READ_MISSING = (
    "import sys; "
    "from agate_common import read_judge_verdict; "
    "print(read_judge_verdict(sys.argv[1]))"
)


@pytest.mark.windows_smoke
def test_bdd_7_append_event_first_line_genesis_ts(
    tmp_path, python_exe, run_cli, agate_scripts
):
    """BDD-7 写侧：append_event 首行 prev_hash==GENESIS_HASH、ts 自动补、GENESIS_HASH 常量可用。"""
    td = tmp_path / "task"
    td.mkdir()

    result = run_cli(
        python_exe, "-c", _APPEND_FIRST, str(td), env={"PYTHONPATH": str(agate_scripts)}
    )
    assert result.returncode == 0
    lines = result.output.splitlines()
    assert len(lines) == 3
    assert lines[0] == hashlib.sha256(b"").hexdigest()  # 写入事件的 prev_hash == GENESIS
    assert lines[1] == hashlib.sha256(b"").hexdigest()  # 模块级 GENESIS_HASH 常量
    assert lines[2] == "True"                            # ts 已自动补齐


def test_bdd_7_append_event_second_line_chains(
    tmp_path, python_exe, run_cli, agate_scripts
):
    """BDD-7 写侧：第二次 append 的 prev_hash == sha256(首行原始文本)（行间链续接）。"""
    td = tmp_path / "task"
    td.mkdir()

    result = run_cli(
        python_exe, "-c", _APPEND_TWO, str(td), env={"PYTHONPATH": str(agate_scripts)}
    )
    assert result.returncode == 0
    lines = result.output.splitlines()
    assert lines[0] == "True"  # 链续接成功
    assert lines[1] == "2"     # 仅行尾追加，共 2 行


def test_bdd_7_append_event_ts_monotonic_fallback(
    tmp_path, python_exe, run_cli, agate_scripts
):
    """BDD-7 写侧：尾行 ts 在时钟之后（2099）时 append_event 做 ts 单调兜底（>= 尾行），且链续接。"""
    td = tmp_path / "task"
    td.mkdir()

    result = run_cli(
        python_exe, "-c", _APPEND_TS_FALLBACK, str(td), env={"PYTHONPATH": str(agate_scripts)}
    )
    assert result.returncode == 0
    lines = result.output.splitlines()
    assert lines[0] == "True"  # ts >= 尾行 ts（单调兜底）
    assert lines[1] == "True"  # prev_hash 链续接


def test_bdd_5_read_judge_verdict_parses_frontmatter(
    tmp_path, python_exe, run_cli, agate_scripts
):
    """BDD-5 读取侧：read_judge_verdict 解析 verdict frontmatter 返回字段 dict。"""
    td = tmp_path / "task"
    td.mkdir()
    (td / "P6.5-judge-verdict.md").write_text(
        "---\nstatus: passed\ncriteria_total: 2\ncriteria_passed: 2\n"
        'verdict_evidence: ["a.json", "b.json"]\npartial: false\n---\n'
        "- PASS BDD-1: verified (a.json)\n- PASS BDD-2: verified (b.json)\n",
        encoding="utf-8",
    )

    result = run_cli(
        python_exe, "-c", _READ_VERDICT, str(td), env={"PYTHONPATH": str(agate_scripts)}
    )
    assert result.returncode == 0
    lines = result.output.splitlines()
    assert lines[0] == "passed"
    assert lines[1] == "2"
    assert lines[2] == "2"
    assert lines[3] == "True"   # verdict_evidence 存在
    assert lines[4] == "False"  # partial 为 false


def test_bdd_5_read_judge_verdict_missing_returns_none(
    tmp_path, python_exe, run_cli, agate_scripts
):
    """BDD-5 读取侧：verdict 文件缺失 → read_judge_verdict 返回 None。"""
    td = tmp_path / "task"
    td.mkdir()

    result = run_cli(
        python_exe, "-c", _READ_MISSING, str(td), env={"PYTHONPATH": str(agate_scripts)}
    )
    assert result.returncode == 0
    assert result.output.strip() == "None"
