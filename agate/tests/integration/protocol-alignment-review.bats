#!/usr/bin/env bats
# tests/integration/protocol-alignment-review.bats — self-gate 机制测试
load ../helpers/load.bash

@test "SG.1 角色文件 protocol-alignment-review.md 存在且含必需 frontmatter" {
    local role_file="$AGATE_ASSETS/review-roles/protocol-alignment-review.md"
    [ -f "$role_file" ]
    grep -q '^role_id: protocol-alignment-review' "$role_file"
    grep -q '^type: review' "$role_file"
    grep -q '^phases:' "$role_file"
    grep -q '^agent:' "$role_file"
}

@test "SG.2 角色文件含 A1-A6 审查清单" {
    local role_file="$AGATE_ASSETS/review-roles/protocol-alignment-review.md"
    grep -q 'A1' "$role_file"
    grep -q 'A2' "$role_file"
    grep -q 'A3' "$role_file"
    grep -q 'A4' "$role_file"
    grep -q 'A5' "$role_file"
    grep -q 'A6' "$role_file"
}

@test "SG.3 角色文件含 NEEDS_HUMAN_REVIEW 闭环规则 + HUMAN_CONFIRMED 标记" {
    local role_file="$AGATE_ASSETS/review-roles/protocol-alignment-review.md"
    grep -q 'NEEDS_HUMAN_REVIEW' "$role_file"
    grep -q 'HUMAN_CONFIRMED' "$role_file"
}

@test "SG.4 SELF-GATE.md 含派发模板" {
    local selfgate_file="$BATS_TEST_DIRNAME/../../../SELF-GATE.md"
    [ -f "$selfgate_file" ]
    grep -q 'protocol-alignment-review' "$selfgate_file"
    grep -q '审查清单' "$selfgate_file"
    grep -q '配套文件提示' "$selfgate_file"
}

@test "SG.5 SELF-GATE.md 含检查清单" {
    local selfgate_file="$BATS_TEST_DIRNAME/../../../SELF-GATE.md"
    [ -f "$selfgate_file" ]
    grep -q 'protocol-alignment-review' "$selfgate_file"
    grep -q 'CHECK 1-9' "$selfgate_file"
    grep -q 'HUMAN_CONFIRMED' "$selfgate_file"
}

@test "SG.6 CHECK 9 锚点表覆盖全部 11 个 gate 脚本" {
    # 从 check-protocol-consistency.py 提取锚点表中的脚本路径
    local consistency_script="$AGATE_SCRIPTS/check-protocol-consistency.py"
    [ -f "$consistency_script" ]

    # 仓库中所有 check-*.sh + pre-commit-gate.sh
    local all_scripts
    all_scripts=$(find "$AGATE_SCRIPTS" -name 'check-*.sh' -o -name 'pre-commit-gate.sh' | sort)

    # 每个脚本都应出现在锚点表中
    for script in $all_scripts; do
        local basename
        basename=$(basename "$script")
        grep -q "$basename" "$consistency_script" || {
            echo "FAIL: $basename 不在 CHECK 9 锚点表中" >&2
            false
        }
    done
}

@test "SG.7 commit-msg-self-gate.sh 存在且可执行" {
    local hook_script="$AGATE_SCRIPTS/commit-msg-self-gate.sh"
    [ -f "$hook_script" ]
    [ -x "$hook_script" ]
}

@test "SG.8 SELF-GATE.md 含递归终止条件" {
    local selfgate_file="$BATS_TEST_DIRNAME/../../../SELF-GATE.md"
    [ -f "$selfgate_file" ]
    grep -q '递归终止' "$selfgate_file"
    grep -q 'ALIGNED' "$selfgate_file"
}
