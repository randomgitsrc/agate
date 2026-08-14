#!/usr/bin/env bats
# tests/unit/dispatch-context-warning.bats — B3 dispatch-context 缺失 WARNING

load ../helpers/load.bash

@test "B3-warning: 产出暂存缺 dispatch-context → WARNING" {
    local repo
    repo=$(mktemp -d "$BATS_TEST_TMPDIR/repo-XXXXXX")
    git init "$repo" > /dev/null 2>&1
    git -C "$repo" config user.email "test@test.local"
    git -C "$repo" config user.name "Test"
    git -C "$repo" config commit.gpgsign false

    echo "init" > "$repo/README.md"
    git -C "$repo" add README.md
    git -C "$repo" commit -m "init" > /dev/null 2>&1

    # task_id 须为合法格式（T + 2 大写 + 数字，如 TAG0001）——py 流程对 .state.yaml 校验
    # 是 fail-closed（旧 sh 的 check-state-yaml.sh 在 fake root 缺校验器时 fail-open 放行）
    mkdir -p "$repo/agate-workspace/tasks/TAG0001"
    echo "content" > "$repo/agate-workspace/tasks/TAG0001/P2-design.md"
    cat > "$repo/agate-workspace/tasks/TAG0001/.state.yaml" <<'EOF'
task_id: TAG0001
phase: P2
status: active
retries: {}
EOF
    git -C "$repo" add agate-workspace/tasks/TAG0001/

    AGATE_ROOT_FAKE=$(mktemp -d "$BATS_TEST_TMPDIR/agate-fake-XXXXXX")
    mkdir -p "$AGATE_ROOT_FAKE/scripts"
    # 薄壳只 exec py：复制 py 依赖（pre-commit-gate.py + agate_common.py + 被调用的 py，含 transitive 依赖）
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate_common.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-state-get.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-json-get.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-state-yaml-check.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-frontmatter-check.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-md-field-get.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-gate-missing-cmds.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-gate-p5-count.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-vision-blocker.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-evidence-consistency.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-image-check.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/agate-changelog-unreleased.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-state-yaml.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-state-transition.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-frontmatter.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-p6-format.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-gate.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-p6-provenance.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-pruning.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-scope-resolved.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-retrospective.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-changelog.py" "$AGATE_ROOT_FAKE/scripts/"
    cp "$AGATE_ROOT/scripts/check-p6-evidence.py" "$AGATE_ROOT_FAKE/scripts/"
    cp -r "$AGATE_ROOT/assets" "$AGATE_ROOT_FAKE/"
    # Do NOT copy agate-next-card.py — simulates it being unavailable (B3 WARNING 路径)

    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT_FAKE' bash '$AGATE_ROOT_FAKE/scripts/pre-commit-gate.sh'" 2>&1 || true
    [[ "$output" == *"dispatch-context"* ]]
}
