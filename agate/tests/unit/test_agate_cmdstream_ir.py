# tests/unit/test_agate_cmdstream_ir.py — 命令流日志 CommandRecord IR 契约（TAG0028 P3，RM-AG0055）
# 被测（P4 才新建，本文件当前必须全红）：
#   - agate/scripts/agate-cmdstream-ir.py   （CommandRecord 统一中间表示：dataclass 十字段 +
#                                             字段契约校验 + JSON 序列化，P2-design.md §3.1 M1）
#
# 覆盖 P1-requirements.md BDD-1（统一 CommandRecord IR 字段完整性 + 序列化）。
#
# 接口假设（P4 实现须提供，均有 P2-design.md §3.1 明文依据，非杜撰）：
#   - 模块顶层 `CommandRecord` dataclass，十字段字段：
#     platform / session_id / tool / command / ts_start / ts_end / exit / exit_signal /
#     output_hash / truncated
#   - 类型契约（BDD-1）：ts_start/ts_end 为 epoch 毫秒 int、exit 为 int|None、truncated 为 bool
#   - 模块提供 `CommandRecord.to_json()` 与模块级 `from_json(s)`（P2 §3.1 "提供 to_json()/from_json()
#     供 CLI 中间传递与测试断言"）
#
# 红灯性质：被测脚本当前不存在——_load_script 检查文件存在性后 pytest.fail（failed 计数，
# B 类红灯：被测模块未实现；不传播 FileNotFoundError，避免 check-tdd-red 按 error/import 误判 A 类）。

import importlib.util

import pytest


def _load_ir(agate_scripts):
    """importlib 加载 agate-cmdstream-ir.py（连字符文件名不能直接 import，同 test_agate_md_field_set
    惯例）。被测脚本缺失时 pytest.fail（B 类红灯），不抛裸异常。"""
    path = agate_scripts / "agate-cmdstream-ir.py"
    if not path.is_file():
        pytest.fail(f"被测模块未实现: {path}（TDD 红灯，P4 实现后转绿）")
    spec = importlib.util.spec_from_file_location("agate_cmdstream_ir", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ================= BDD-1: 统一 CommandRecord IR 字段完整性 =================


def test_bdd_1_ir_field_contract(agate_scripts):
    """BDD-1：任一平台适配器产出的 CommandRecord 必含十字段十个字段，类型符合 IR 契约。"""
    ir = _load_ir(agate_scripts)
    CommandRecord = ir.CommandRecord

    rec = CommandRecord(
        platform="dsh",
        session_id="ses_demo",
        tool="bash",
        command="ls -la",
        ts_start=1787883650309,
        ts_end=1787883650312,
        exit=0,
        exit_signal="",
        output_hash="h_demo",
        truncated=False,
    )

    # 十字段字段完整性（BDD-1 Then：必含十字段）
    for field in (
        "platform", "session_id", "tool", "command",
        "ts_start", "ts_end", "exit", "exit_signal", "output_hash", "truncated",
    ):
        assert hasattr(rec, field), f"CommandRecord 缺少字段: {field}"

    # 类型契约（BDD-1 Then：ts_start/ts_end epoch 毫秒 int、exit int|None、truncated bool）
    assert isinstance(rec.ts_start, int)
    assert isinstance(rec.ts_end, int)
    assert rec.exit is None or isinstance(rec.exit, int)
    assert isinstance(rec.truncated, bool)


def test_bdd_1_ir_exit_none_truncated_true(agate_scripts):
    """BDD-1 边界：exit 可为 None（未结束 call）、truncated 可为 True（截断输出）。"""
    ir = _load_ir(agate_scripts)
    CommandRecord = ir.CommandRecord

    rec = CommandRecord(
        platform="claude-code",
        session_id="ses_demo",
        tool="Bash",
        command="python3 -m pytest",
        ts_start=1787883650400,
        ts_end=1787883650900,
        exit=None,
        exit_signal="pending",
        output_hash=None,
        truncated=True,
    )
    assert rec.exit is None
    assert rec.truncated is True


def test_bdd_1_ir_json_roundtrip(agate_scripts):
    """BDD-1 序列化：to_json()/from_json() 往返保真（P2 §3.1 十字段契约 + 序列化）。"""
    ir = _load_ir(agate_scripts)
    CommandRecord = ir.CommandRecord

    rec = CommandRecord(
        platform="opencode",
        session_id="ses_demo",
        tool="bash",
        command="make build",
        ts_start=1788245301014,
        ts_end=1788245301028,
        exit=2,
        exit_signal="",
        output_hash="h_demo",
        truncated=False,
    )
    restored = ir.from_json(rec.to_json())
    for field in (
        "platform", "session_id", "tool", "command",
        "ts_start", "ts_end", "exit", "exit_signal", "output_hash", "truncated",
    ):
        assert getattr(restored, field) == getattr(rec, field), f"序列化往返字段漂移: {field}"


# ================= BDD-1 补充（fix1，P4-review CRITICAL-6）：from_dict 类型契约校验 =================


def test_bdd_1_ir_from_dict_rejects_bad_types(agate_scripts):
    """BDD-1 Then「类型符合 IR 契约」直接落点（CRITICAL-6）：from_json 喂入坏类型
    （ts_start="abc" / exit="x" / truncated="yes"）必须抛 ValueError 带字段名——
    坏数据不得静默流入 detect（age=now-"abc" 崩溃或判定失真）。"""
    ir = _load_ir(agate_scripts)

    base = {
        "platform": "dsh",
        "session_id": "ses_demo",
        "tool": "bash",
        "command": "ls -la",
        "ts_start": 1787883650309,
        "ts_end": 1787883650312,
        "exit": 0,
        "exit_signal": "",
        "output_hash": "h_demo",
        "truncated": False,
    }

    # ts_start 非 int
    bad_ts = dict(base, ts_start="abc")
    with pytest.raises(ValueError) as ei:
        ir.CommandRecord.from_dict(bad_ts)
    assert "ts_start" in str(ei.value)

    # exit 非 int|None
    bad_exit = dict(base, exit="x")
    with pytest.raises(ValueError) as ei:
        ir.CommandRecord.from_dict(bad_exit)
    assert "exit" in str(ei.value)

    # truncated 非 bool
    bad_trunc = dict(base, truncated="yes")
    with pytest.raises(ValueError) as ei:
        ir.CommandRecord.from_dict(bad_trunc)
    assert "truncated" in str(ei.value)

    # ts_end 非 int|None
    bad_ts_end = dict(base, ts_end="later")
    with pytest.raises(ValueError) as ei:
        ir.CommandRecord.from_dict(bad_ts_end)
    assert "ts_end" in str(ei.value)

    # 合法边界（exit=None + ts_end=None，CRITICAL-3 未结束 call 形态）不抛
    ok = dict(base, exit=None, ts_end=None, output_hash=None)
    rec = ir.CommandRecord.from_dict(ok)
    assert rec.exit is None and rec.ts_end is None

    # bool 是 int 子类，不得被当作合法 ts/exit（类型契约防坍缩）
    bad_bool_ts = dict(base, ts_start=True)
    with pytest.raises(ValueError):
        ir.CommandRecord.from_dict(bad_bool_ts)
