#!/usr/bin/env bats
# tests/unit/check-protocol-consistency.bats — CHECK 9 锚点断言

load ../helpers/load.bash

# $AGATE_SCRIPTS 在 Git Bash 是 /c/...（MSYS），Windows 原生 python 无法解析——
# 统一经 py_path 转成 C:/...（TAG0009 Windows 修复）
@test "CHECK 9: EXIT_CODE 锚点存在且关键词匹配" {
    local scripts
    scripts=$(py_path "$AGATE_SCRIPTS")
    run $PYTHON -c "
import sys; sys.path.insert(0, '$scripts')
from importlib import util
spec = util.spec_from_file_location('cpc', '$scripts/check-protocol-consistency.py')
cpc = util.module_from_spec(spec)
spec.loader.exec_module(cpc)
anchors = cpc.SCRIPT_ALIGNMENT_ANCHORS
exit_code_anchors = [a for a in anchors if 'EXIT_CODE' in a.get('keywords', [])]
assert len(exit_code_anchors) >= 2, f'Expected >=2 EXIT_CODE anchors, got {len(exit_code_anchors)}'
"
    [ "$status" -eq 0 ]
}

@test "CHECK 9: AGATE_ALIGNMENT_REVIEW_THRESHOLD 锚点存在" {
    local scripts
    scripts=$(py_path "$AGATE_SCRIPTS")
    run $PYTHON -c "
import sys; sys.path.insert(0, '$scripts')
from importlib import util
spec = util.spec_from_file_location('cpc', '$scripts/check-protocol-consistency.py')
cpc = util.module_from_spec(spec)
spec.loader.exec_module(cpc)
anchors = cpc.SCRIPT_ALIGNMENT_ANCHORS
threshold_anchors = [a for a in anchors if 'AGATE_ALIGNMENT_REVIEW_THRESHOLD' in a.get('keywords', [])]
assert len(threshold_anchors) >= 1, f'Expected >=1 threshold anchor, got {len(threshold_anchors)}'
"
    [ "$status" -eq 0 ]
}

@test "CHECK 9: ci-gate-backstop.py 被纳入 anchor coverage 扫描范围" {
    local scripts
    scripts=$(py_path "$AGATE_SCRIPTS")
    run $PYTHON -c "
import sys; sys.path.insert(0, '$scripts')
from importlib import util
spec = util.spec_from_file_location('cpc', '$scripts/check-protocol-consistency.py')
cpc = util.module_from_spec(spec)
spec.loader.exec_module(cpc)
# check_anchor_coverage uses get_gate_scripts — check internal logic
# At minimum, verify anchors exist for ci-gate-backstop.py
anchors = cpc.SCRIPT_ALIGNMENT_ANCHORS
cb_anchors = [a for a in anchors if 'ci-gate-backstop.py' in a.get('script', '')]
assert len(cb_anchors) >= 1, f'Expected >=1 ci-gate-backstop.py anchor, got {len(cb_anchors)}'
"
    [ "$status" -eq 0 ]
}
