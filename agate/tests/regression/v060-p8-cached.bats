#!/usr/bin/env bats
# tests/regression/v060-p8-cached.bats — 回归测试：P8 gate 用 --cached 不是 HEAD~1
# 触发：7f4648d "fix: P8 gate HEAD~1 chicken-and-egg bug"
# 教训：v0.6 hardening R4 修了 P4/P7，但漏了 P8 → 本次评审发现并修复

load ../helpers/load.bash

@test "R5.1 P8 gate 暂存区有 version + CHANGELOG → exit 2（脚本化通过）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    echo "## [Unreleased]" > "$repo/CHANGELOG.md"
    git -C "$repo" add package.json CHANGELOG.md
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 2 ]
    [[ "$output" == *"脚本化检查通过"* ]]
}

@test "R5.2 P8 gate 暂存区无 version 文件 → WARNING（P1-6: 降级非阻断）" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "doc" > "$repo/some.md"
    echo "## [Unreleased]" > "$repo/CHANGELOG.md"
    git -C "$repo" add some.md CHANGELOG.md
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    # P1-6: version 不匹配降为 WARNING → RC 不设 1 → CHANGELOG OK → exit 2
    [ "$status" -eq 2 ]
    [[ "$output" == *"WARNING"*"version"* ]]
}

@test "R5.3 P8 gate 暂存区有 version 但 CHANGELOG 无变更 → exit 2 (WARNING)" {
    local dir
    dir=$(create_task_dir)
    cat > "$dir/P8-release.md" <<'EOF'
bump_type: minor
EOF
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    cp -r "$dir" "$repo/task"
    echo "v0.1.0" > "$repo/package.json"
    # CHANGELOG 没改 → WARNING（不阻断）
    git -C "$repo" add package.json
    run bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' P8 'task'"
    [ "$status" -eq 2 ]
    [[ "$output" == *"CHANGELOG"* ]]
}
