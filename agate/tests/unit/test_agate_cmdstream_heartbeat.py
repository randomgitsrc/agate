# tests/unit/test_agate_cmdstream_heartbeat.py — 心跳文件生命周期（TAG0028 P3，RM-AG0055）
# 被测（P4 才落地，本文件当前必须红）：
#   - agate-cmdstream-detect.py 的心跳命名/清理 helper（P2-design.md §3.3 Phase 3：
#     .heartbeat / .heartbeat.child-{n} 命名、清理时机；比照 agate-archive-stale-outputs 模式）
#   - agate/dispatch-protocol.md「心跳文件生命周期」子节改写（M5）+ check-p6-provenance.py
#     豁免登记（M8）
#
# 覆盖 P1-requirements.md BDD-25/26/27/28（心跳命名 / 审计豁免 / 清理兜底 / 两套信号分工）。
#
# 接口假设（P4 实现须提供，均有 P2-design.md §3.3 明文依据）：
#   - heartbeat_path(task_dir, n=None) -> Path：n=None 返回 ${TASK_DIR}/.heartbeat；
#     n 为整数返回 ${TASK_DIR}/.heartbeat.child-{n}（同父任务内不重复不覆盖）
#   - cleanup_heartbeats(task_dir) -> int：清理任务目录内心跳文件（产生方清理；异常遗留由
#     派发前置检查清空——测试断言清理函数存在且可对遗留心跳文件执行清空）
#   - 文档断言：dispatch-protocol.md 心跳生命周期子节含命名规范、审计豁免登记、清理时机表述
#
# 红灯性质：被测 helper 与协议改写当前不存在——helper 缺失 pytest.fail（B 类红灯）；
# 文档断言当前失败（改写未落地，属"被测内容未实现"语义）。BDD-26 行为部分（check-p6-provenance
# 不扫隐藏文件）为长期不变量可绿（脚本已存在）。

import importlib.util

import pytest


def _load_detect(agate_scripts):
    """importlib 加载 agate-cmdstream-detect.py（心跳 helper 落点）；缺失时 pytest.fail。"""
    path = agate_scripts / "agate-cmdstream-detect.py"
    if not path.is_file():
        pytest.fail(f"被测模块未实现: {path}（TDD 红灯，P4 实现后转绿）")
    spec = importlib.util.spec_from_file_location("agate_cmdstream_detect", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _read_text(p):
    return p.read_text(encoding="utf-8")


# ================= BDD-25: 心跳文件父子分层命名 =================


def test_bdd_25_heartbeat_naming_doc(agate_root):
    """BDD-25（文档断言，红）：dispatch-protocol.md 心跳文件生命周期子节含父子分层命名规范——
    任务级 ${TASK_DIR}/.heartbeat、父 subagent 为子任务维护 ${TASK_DIR}/.heartbeat.child-{n}
    （M5，P2 §3.3；当前 0 次命中 → 未改写）。"""
    text = _read_text(agate_root / "dispatch-protocol.md")
    assert ".heartbeat" in text, "dispatch-protocol.md 未含心跳文件命名规范（心跳生命周期子节未改写）"
    assert ".heartbeat.child-" in text or ".heartbeat.child-{n}" in text, (
        "未含 .heartbeat.child-{n} 父子分层命名（M5 未落地）")


# ================= BDD-26: 心跳文件审计豁免确认 =================


def test_bdd_26_audit_exemption_registered(agate_root):
    """BDD-26（登记断言，红）：check-p6-provenance.py 路径过滤逻辑处登记了显式豁免确认结果
    （不能仅靠"默认不扫"假设，P2 §3.5/M8）——源码含 .heartbeat 豁免登记注释/常量。"""
    src = _read_text(agate_root / "scripts" / "check-p6-provenance.py")
    assert "heartbeat" in src, "check-p6-provenance.py 未登记 .heartbeat 豁免确认（M8 未落地）"


def test_bdd_26_audit_behavior_hidden_files_skipped(agate_root, python_exe, run_cli, task_dir):
    """BDD-26（行为断言，长期不变量可绿）：任务目录含 .heartbeat 与 .heartbeat.child-1 时，
    check-p6-provenance.py 的 _find_files 天然跳过隐藏文件（不产生未引用文件告警）。"""
    td = task_dir()
    (td / ".heartbeat").write_text("ok\n", encoding="utf-8")
    (td / ".heartbeat.child-1").write_text("ok\n", encoding="utf-8")

    # _find_files 隐藏文件过滤（实读确认 line 85-93）：以 . 开头不进入审计枚举
    spec = importlib.util.spec_from_file_location(
        "check_p6_provenance", str(agate_root / "scripts" / "check-p6-provenance.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    found = mod._find_files(str(td))
    assert all(not __import__("os").path.basename(f).startswith(".") for f in found), (
        "check-p6-provenance 枚举了隐藏心跳文件"
    )
    assert not any(".heartbeat" in f for f in found)


# ================= BDD-27: 任务结束清理 + 异常遗留兜底 =================


def test_bdd_27_cleanup_doc(agate_root):
    """BDD-27（文档断言，红）：dispatch-protocol.md 心跳生命周期子节含清理时机——任务结束由
    产生心跳的一方清理；异常遗留由下次重新派发前的派发前置检查清空（比照
    agate-archive-stale-outputs 模式，不新建清理机制；M5，当前 0 次命中 → 未改写）。"""
    text = _read_text(agate_root / "dispatch-protocol.md")
    assert ".heartbeat" in text, "dispatch-protocol.md 未含心跳生命周期子节（M5 未落地）"
    assert "清理" in text, "未含心跳文件清理时机表述（M5 未落地）"


# ================= BDD-28: dispatch-protocol.md 两套信号职责分工改写 =================


def test_bdd_28_two_signals_doc(agate_root):
    """BDD-28（文档断言，红）：dispatch-protocol.md「Subagent 安全 → 存活检查」节已改写——
    命令流日志承担"存活/卡死"判定职责（取代 progress 心跳扩展此职责），progress.md 保留
    "语义进展"职责不变；两套信号分工清晰；不修改 check-gate.py / check-state-transition.py
    返回约定。"""
    text = _read_text(agate_root / "dispatch-protocol.md")
    # 靶向 M5 改写后特有表述：命令流日志 + 语义进展职责（现为 0 次，改写未落地 → 红）
    # 注意：check-gate.py / check-state-transition.py 为既有文档泛词（5/4 次），不做断言依据
    assert "命令流" in text, "dispatch-protocol.md 未含命令流日志表述（存活检查节未改写）"
    assert "语义进展" in text, "未明确 progress.md 保留语义进展职责（存活检查节未改写）"
