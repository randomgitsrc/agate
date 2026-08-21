# tests/unit/test_docs_assertions.py — 协议文档静态条文断言（TAG0019，BDD-11/12/14）
# 断言 ceremony 新机制的文档条文可 grep（P4 实现落协议文档后应存在；当前未实现 → 红）。
# 平台无关：读文件经 pathlib（agate_root fixture），无 shell / 无硬编码临时目录字面 / 无裸 python3。

import re
from pathlib import Path


def _read(agate_root, rel):
    return (Path(agate_root) / rel).read_text(encoding="utf-8")


def test_bdd_11_requirements_review_audits_declaration_vs_diff(
    agate_root
):
    """BDD-11：requirements-review 清单含「风险分级/裁剪声明 vs 暂存区 diff 证据」核对项（审声明职责显式化）。"""
    text = _read(agate_root, "assets/review-roles/requirements-review.md")
    assert re.search(r"diff\s*证据|声明.*证据|证据.*声明", text), \
        "requirements-review 缺「声明 vs diff 证据」核对项"


def test_bdd_12_m3_acceptance_anchor_four_elements(agate_root):
    """BDD-12：P1 卡 ceremony 机制文档可提取 M3 验收锚四要素（评审轮数 / 真实发现数 / TAG0018 基线 / 回滚 standard 决策）。"""
    text = _read(agate_root, "phase-cards/P1-requirements.md")
    for kw in ("评审轮数", "真实发现数", "TAG0018", "回滚 standard"):
        assert kw in text, f"M3 验收锚缺要素：{kw}"


def test_bdd_14_full_ceremony_p7_not_prunable_sync(agate_root):
    """BDD-14：full 档 P7 不可裁四处同步声明（role-system / review-mapping / P2 卡 / P4 卡）均含 ceremony full 消费。"""
    files = [
        "role-system.md",
        "rules/review-mapping.md",
        "phase-cards/P2-design.md",
        "phase-cards/P4-implementation.md",
    ]
    for rel in files:
        text = _read(agate_root, rel)
        assert "ceremony" in text or re.search(r"tier.*full|full.*tier", text), \
            f"{rel} 缺 full 档（ceremony full / tier full）消费声明"


def test_bdd_14_full_requires_p7_phase_in_review(agate_root):
    """BDD-14 评审层保证：requirements-review 补「声明 ceremony: full → phases 含 P7」核对项（缺则需回退/拒）。"""
    text = _read(agate_root, "assets/review-roles/requirements-review.md")
    assert "ceremony" in text and "P7" in text, \
        "requirements-review 缺 full→P7 核对项（BDD-14 评审层保证）"
