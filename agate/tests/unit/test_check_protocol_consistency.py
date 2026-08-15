# tests/unit/test_check_protocol_consistency.py — CHECK 9 锚点断言
# （check-protocol-consistency.bats 3 用例迁移，TAG0011 批次 10b）
# 被测：agate/scripts/check-protocol-consistency.py 的 SCRIPT_ALIGNMENT_ANCHORS 锚点表。
# bats 用 py_path（Windows 路径转换）+ 独立 python 进程加载模块；pytest 在测试进程内 importlib
#   等价加载（模块仅依赖 stdlib，无需 sys.path 注入；Windows 原生 Path 已是本机格式，
#   py_path 转换不再需要）。

import importlib.util
import os
from pathlib import Path

import pytest


def _load_cpc(agate_scripts):
    path = os.path.join(str(agate_scripts), "check-protocol-consistency.py")
    spec = importlib.util.spec_from_file_location("cpc", path)
    cpc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cpc)
    return cpc


@pytest.mark.windows_smoke
def test_check_9_exit_code_anchor_exists(agate_scripts):
    cpc = _load_cpc(agate_scripts)
    anchors = cpc.SCRIPT_ALIGNMENT_ANCHORS
    exit_code_anchors = [a for a in anchors if "EXIT_CODE" in a.get("keywords", [])]
    assert len(exit_code_anchors) >= 2, f"Expected >=2 EXIT_CODE anchors, got {len(exit_code_anchors)}"


def test_check_9_agate_alignment_review_threshold_anchor_exists(agate_scripts):
    cpc = _load_cpc(agate_scripts)
    anchors = cpc.SCRIPT_ALIGNMENT_ANCHORS
    threshold_anchors = [
        a for a in anchors if "AGATE_ALIGNMENT_REVIEW_THRESHOLD" in a.get("keywords", [])
    ]
    assert len(threshold_anchors) >= 1, (
        f"Expected >=1 threshold anchor, got {len(threshold_anchors)}"
    )


def test_check_9_ci_gate_backstop_anchor_in_scan(agate_scripts):
    cpc = _load_cpc(agate_scripts)
    anchors = cpc.SCRIPT_ALIGNMENT_ANCHORS
    cb_anchors = [a for a in anchors if "ci-gate-backstop.py" in a.get("script", "")]
    assert len(cb_anchors) >= 1, f"Expected >=1 ci-gate-backstop.py anchor, got {len(cb_anchors)}"


# ── CHECK 10（协议文档脚本名引用漂移）新增用例，TAG0013（追加，不改既有） ──────
# 夹具：最小假协议树（pytest tmp_path 下 agate/scripts/ 假脚本 + 协议文档面扫描文件），
#   直接调 check_script_name_refs(root, rep) 断言 rep.errors / rep.ok。
# 平台无关：不用 /tmp、不创建软链、文本 I/O 显式 utf-8。

_FAKE_SCAN_FILES = [
    "agate/WORKFLOW.md",
    "agate/dispatch-protocol.md",
    "agate/state-machine.md",
    "agate/role-system.md",
    "agate/loop-orchestration.md",
    "agate/git-integration.md",
    "agate/platform-notes.md",
    "agate/LIMITATIONS.md",
    "README.md",
    "agate/orchestrator-template.md",
    "agate/SETUP.md",
    "AGENTS.md",
    "agate/AGENTS.md",
    "agate/CONTEXT.md",
    "agate/UPGRADING.md",
    "agate/scripts/README.md",
    "CHANGELOG.md",
]

_FAKE_SCRIPT_FILES = [
    "agate/scripts/check-gate.py",
    "agate/scripts/agate_common.py",
    "agate/scripts/check-tdd-red.py",
    "agate/scripts/check-protocol-consistency.py",
    "agate/tests/scripts/count-tests.sh",
]


def _make_fake_protocol_tree(tmp_path):
    """构造最小假协议树：agate/scripts/ 假脚本 + 协议文档面扫描文件（默认空内容）。"""
    root = Path(tmp_path)
    for rel in _FAKE_SCAN_FILES + _FAKE_SCRIPT_FILES:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("", encoding="utf-8")
    return root


def _check10_errors(rep):
    return [e for e in rep.errors if e["check"] == "CHECK10-scriptref"]


def _check10_warnings(rep):
    return [w for w in rep.warnings if w["check"] == "CHECK10-scriptref"]


def test_bdd_1_checks_list_registers_check10(agate_scripts):
    cpc = _load_cpc(agate_scripts)
    assert any(name.startswith("CHECK 10") for name, _ in cpc.CHECKS), (
        "CHECKS 未注册 CHECK 10（check_script_name_refs）"
    )


def test_bdd_1_check10_zero_drift_passes(agate_scripts, tmp_path):
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    (root / "agate" / "WORKFLOW.md").write_text(
        "主 Agent 调用 check-gate.py 与 check-tdd-red.py 确认阶段推进。\n",
        encoding="utf-8",
    )

    rep = cpc.Report()
    cpc.check_script_name_refs(root, rep)

    assert _check10_errors(rep) == []
    assert "CHECK10-scriptref" in rep.passed


def test_bdd_2_check10_drift_error(agate_scripts, tmp_path):
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    phase_card = root / "agate" / "phase-cards" / "P3-tdd.md"
    phase_card.parent.mkdir(parents=True, exist_ok=True)
    phase_card.write_text("派发 check-nonexistent-script.py 确认红灯。\n", encoding="utf-8")

    rep = cpc.Report()
    cpc.check_script_name_refs(root, rep)

    drift = _check10_errors(rep)
    assert len(drift) == 1, f"Expected 1 CHECK10 drift, got {len(drift)}"
    assert "check-nonexistent-script.py" in drift[0]["msg"]
    assert "P3-tdd.md" in drift[0]["loc"]


def test_bdd_2_blocker_check1_independent_when_check10_error(
    agate_scripts, tmp_path, monkeypatch, capsys
):
    """驱动 real main()：CHECK 10 报 ERROR 时 CHECK 1 状态行仍 ✅（BLOCKER-1，P2-review 缺口 8）。"""
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    monkeypatch.setattr(cpc, "CHECKS", [
        ("CHECK 1  YAML 代码块可解析", lambda r, rep: None),
        ("CHECK 10 协议文档脚本名引用漂移", lambda r, rep: None),
    ])

    def _fake_run(root_, rep):
        rep.error(
            "CHECK10-scriptref",
            "引用了不存在的脚本: check-nonexistent-script.py",
            "agate/WORKFLOW.md:1",
        )

    monkeypatch.setattr(cpc, "run_all_checks", _fake_run)
    monkeypatch.setattr("sys.argv", ["check-protocol-consistency.py", "--root", str(root)])
    code = cpc.main()
    out = capsys.readouterr().out

    assert code == 1
    assert "✅ PASS  CHECK 1" in out
    assert "❌ FAIL  CHECK 10" in out
    # 回归根因锁定：旧逻辑 startswith("CHECK1") 会把 CHECK10-scriptref 误判给 CHECK 1
    assert "CHECK10-scriptref".startswith("CHECK1") is True


def test_bdd_2_blocker_check1_independent_when_check10_warning(
    agate_scripts, tmp_path, monkeypatch, capsys
):
    """驱动 real main()：CHECK 10 报 WARNING 时 CHECK 1 状态行仍 ✅（BLOCKER-1 双场景）。"""
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    monkeypatch.setattr(cpc, "CHECKS", [
        ("CHECK 1  YAML 代码块可解析", lambda r, rep: None),
        ("CHECK 10 协议文档脚本名引用漂移", lambda r, rep: None),
    ])

    def _fake_run(root_, rep):
        rep.warn("CHECK10-scriptref", "CHANGELOG 历史脚本名（聚合提醒）", "CHANGELOG.md")

    monkeypatch.setattr(cpc, "run_all_checks", _fake_run)
    monkeypatch.setattr("sys.argv", ["check-protocol-consistency.py", "--root", str(root)])
    code = cpc.main()
    out = capsys.readouterr().out

    assert code == 0
    assert "✅ PASS  CHECK 1" in out
    assert "⚠️  WARN  CHECK 10" in out


def test_bdd_3_exempt_upgrading_whole_file(agate_scripts, tmp_path):
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    (root / "agate" / "UPGRADING.md").write_text(
        "迁移：check-gate.sh → check-gate.py（对照表行）\n散文行含遗留 check-tdd-red.sh。\n",
        encoding="utf-8",
    )

    rep = cpc.Report()
    cpc.check_script_name_refs(root, rep)

    assert _check10_errors(rep) == []


def test_bdd_3_exempt_formatter_names_natural(agate_scripts, tmp_path):
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    (root / "agate" / "WORKFLOW.md").write_text(
        "formatter 候选：pytest.sh / go-test.sh / my-runner.sh\n",
        encoding="utf-8",
    )

    rep = cpc.Report()
    cpc.check_script_name_refs(root, rep)

    assert _check10_errors(rep) == []


def test_bdd_3_exempt_hook_shells(agate_scripts, tmp_path):
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    (root / "agate" / "WORKFLOW.md").write_text(
        "pre-commit-gate.sh 以软链方式安装。\n",
        encoding="utf-8",
    )

    rep = cpc.Report()
    cpc.check_script_name_refs(root, rep)

    assert _check10_errors(rep) == []


def test_bdd_3_exempt_count_tests_sh(agate_scripts, tmp_path):
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    (root / "agate" / "WORKFLOW.md").write_text(
        "跑 bash agate/tests/scripts/count-tests.sh 防计数漂移。\n",
        encoding="utf-8",
    )

    rep = cpc.Report()
    cpc.check_script_name_refs(root, rep)

    assert _check10_errors(rep) == []


def test_bdd_3_exempt_scripts_readme_retired_names(agate_scripts, tmp_path):
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    (root / "agate" / "scripts" / "README.md").write_text(
        "退役：gate-result.sh / agate-workspace-resolve.sh / check-windows-smoke.sh\n",
        encoding="utf-8",
    )

    rep = cpc.Report()
    cpc.check_script_name_refs(root, rep)

    assert _check10_errors(rep) == []


def test_bdd_4_protocol_dirs_includes_phase_cards_rules(agate_scripts):
    cpc = _load_cpc(agate_scripts)
    assert cpc.PROTOCOL_DIRS == (
        "agate/assets/",
        "agate/phase-cards/",
        "agate/rules/",
    )


def test_bdd_5_changelog_drift_aggregated_warning(agate_scripts, tmp_path):
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    (root / "CHANGELOG.md").write_text(
        "v0.30.0: 引入 check-gate.sh 统一 gate。\n",
        encoding="utf-8",
    )

    rep = cpc.Report()
    cpc.check_script_name_refs(root, rep)

    assert _check10_errors(rep) == []
    assert len(_check10_warnings(rep)) == 1


def test_bdd_5_docs_dir_not_scanned(agate_scripts, tmp_path):
    cpc = _load_cpc(agate_scripts)
    root = _make_fake_protocol_tree(tmp_path)
    docs_file = root / "docs" / "superpowers" / "guide.md"
    docs_file.parent.mkdir(parents=True, exist_ok=True)
    docs_file.write_text("check-nonexistent-script.py 引用\n", encoding="utf-8")

    rep = cpc.Report()
    cpc.check_script_name_refs(root, rep)

    assert _check10_errors(rep) == []
    assert _check10_warnings(rep) == []
