# tests/unit/test_check_protocol_consistency.py — CHECK 9 锚点断言
# （check-protocol-consistency.bats 3 用例迁移，TAG0011 批次 10b）
# 被测：agate/scripts/check-protocol-consistency.py 的 SCRIPT_ALIGNMENT_ANCHORS 锚点表。
# bats 用 py_path（Windows 路径转换）+ 独立 python 进程加载模块；pytest 在测试进程内 importlib
#   等价加载（模块仅依赖 stdlib，无需 sys.path 注入；Windows 原生 Path 已是本机格式，
#   py_path 转换不再需要）。

import importlib.util
import os

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
