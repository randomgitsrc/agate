#!/usr/bin/env bats
# tests/unit/check-changelog.bats — 5 用例覆盖 check-changelog.sh
# 计划：5.8 / 实际 5 行 / 与附录 A 一致

load ../helpers/load.bash

setup() {
    # TAG0009 BDD-16/17：harness shim——产品脚本内部裸 python3 在"仅 python 可解析"环境解析到真解释器
    local shim
    shim=$(create_python_shim_bin) || return 1
    export PATH="$shim:$PATH"
}

@test "CL.1 check-changelog.sh 无 CHANGELOG 文件 期望 exit 0" {
    local repo
    repo=$(git_init)
    cd "$repo"
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    [ "$status" -eq 0 ]
}

@test "CL.2 check-changelog.sh CHANGELOG 无 [Unreleased] 区域 期望 exit 1" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [v0.5.0] - 2026-01-01
- 已发布
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    [ "$status" -eq 1 ]
    [[ "$output" == *"无 [Unreleased]"* ]]
}

@test "CL.3 check-changelog.sh [Unreleased] 无 task_id 期望 exit 1" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [Unreleased]
- 其他内容
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    [ "$status" -eq 1 ]
    [[ "$output" == *"未找到 T001"* ]]
}

@test "CL.4 check-changelog.sh [Unreleased] 含 task_id 期望 exit 0" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [Unreleased]
- T001 任务完成
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    [ "$status" -eq 0 ]
}

@test "CL.5 check-changelog.sh task_id 在历史版本 期望 exit 1" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [v0.5.0]
- T001 旧版本

## [Unreleased]
- 新内容
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" T001
    # task_id 在历史版本不算在 [Unreleased] → exit 1
    [ "$status" -eq 1 ]
}

# ========== T001 v2.0 流 D（BDD-27）：check-changelog 直接匹配完整 task_id ==========
# 旧版 check-changelog.sh:14 用 grep -oE 'T[0-9]+' 提取短前缀（T060-xxx → T060），
# 新格式 TAG0001（无数字紧邻 T）用该正则会提取为空，CHANGELOG 无法记录 —— F17。
# 改造后直接匹配完整 task_id（去掉短前缀截断），CL.6/CL.7/CL.8 改测新格式行为。

@test "CL.6 BDD-27: CHANGELOG 含完整新格式 task_id TAG0001 → 直接匹配成功" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [Unreleased]

### Fixed
- TAG0001: 完成 v2.0 结构化改造
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" TAG0001
    [ "$status" -eq 0 ]
}

@test "CL.7 BDD-27: CHANGELOG 只含 TAG00012（另一任务的更长编号）时 TAG0001 不误匹配" {
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [Unreleased]

### Fixed
- TAG00012: 其他任务条目
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" TAG0001
    [ "$status" -eq 1 ]
    [[ "$output" == *"未找到"* ]]
}

@test "CL.8 BDD-27: 旧版短前缀提取（grep -oE 'T[0-9]+'）对新格式 TAG0001 提取为空——直接匹配已消除该摩擦" {
    # F17 核心场景：旧实现 TASK_ID_SHORT=$(echo "$TASK_ID" | grep -oE 'T[0-9]+' | head -1)
    # 对 "TAG0001"（T 后紧跟字母 AG，非数字）提取不到任何匹配 → TASK_ID_SHORT 为空 →
    # 下游 grep 用空变量匹配必然失败，即使 CHANGELOG 已正确记录 TAG0001 也会误报未找到。
    local repo
    repo=$(git_init)
    cd "$repo"
    cat > CHANGELOG.md <<'EOF'
## [Unreleased]

### Fixed
- TAG0001: 消除 check-changelog 短前缀提取摩擦
EOF
    run bash "$AGATE_SCRIPTS/check-changelog.sh" TAG0001
    [ "$status" -eq 0 ]
}
