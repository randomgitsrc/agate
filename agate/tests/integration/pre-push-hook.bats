#!/usr/bin/env bats
# tests/integration/pre-push-hook.bats — pre-push hook 集成测试

load ../helpers/load.bash

@test "pre-push hook: 新分支首次推送提示跳过检测" {
    local repo
    repo=$(git_init)

    # 安装 pre-push hook
    cat > "$repo/.git/hooks/pre-push" <<'HOOK'
#!/usr/bin/env bash
THRESHOLD="${AGATE_ALIGNMENT_REVIEW_THRESHOLD:-5}"
ZERO_SHA="0000000000000000000000000000000000000000"

while read -r local_ref local_sha remote_ref remote_sha; do
    [ -z "$local_sha" ] && continue
    if [ "$remote_sha" = "$ZERO_SHA" ]; then
        echo "SKIP: 新分支首次推送，跳过检测"
        continue
    fi
    CHANGED_LINES=$(git diff "$remote_sha".."$local_sha" -- 'agate/*.md' 2>/dev/null | grep -cE '^[+-]' || echo 0)
    if [ "$CHANGED_LINES" -gt "$THRESHOLD" ]; then
        echo "WARNING: 改动 ${CHANGED_LINES} 行，建议 alignment-review"
    fi
done
exit 0
HOOK
    chmod +x "$repo/.git/hooks/pre-push"

    cd "$repo"
    echo "test" > file.txt
    git add file.txt
    git commit -m "init" --no-gpg-sign --no-verify

    # 模拟新分支首次 push：remote_sha 全零
    run bash -c "echo 'refs/heads/main $(git rev-parse HEAD) refs/heads/main 0000000000000000000000000000000000000000' | bash '$repo/.git/hooks/pre-push' 2>&1 || true"

    [[ "$output" == *"SKIP"* || "$output" == *"新分支"* ]]
}

@test "pre-push hook: 大改动触发提示" {
    local repo
    repo=$(git_init)

    cat > "$repo/.git/hooks/pre-push" <<'HOOK'
#!/usr/bin/env bash
THRESHOLD="${AGATE_ALIGNMENT_REVIEW_THRESHOLD:-2}"
ZERO_SHA="0000000000000000000000000000000000000000"

while read -r local_ref local_sha remote_ref remote_sha; do
    [ -z "$local_sha" ] && continue
    if [ "$remote_sha" = "$ZERO_SHA" ]; then
        continue
    fi
    CHANGED_LINES=$(git diff "$remote_sha".."$local_sha" -- 'agate/*.md' 2>/dev/null | grep -cE '^[+-]' || echo 0)
    if [ "$CHANGED_LINES" -gt "$THRESHOLD" ]; then
        echo "WARNING: 改动 ${CHANGED_LINES} 行，建议 alignment-review"
    fi
done
exit 0
HOOK
    chmod +x "$repo/.git/hooks/pre-push"

    cd "$repo"
    mkdir -p agate
    cat > "agate/test.md" <<'EOF'
line1
line2
line3
line4
EOF
    git add agate/test.md
    git commit -m "add agate file" --no-gpg-sign --no-verify

    local prev_sha
    prev_sha=$(git rev-parse HEAD)

    cat > "agate/test.md" <<'EOF'
line1-new
line2-new
line3-new
line4-new
line5-new
EOF
    git add agate/test.md
    git commit -m "big change" --no-gpg-sign --no-verify

    local current_sha
    current_sha=$(git rev-parse HEAD)

    run bash -c "echo 'refs/heads/main $current_sha refs/heads/main $prev_sha' | bash '$repo/.git/hooks/pre-push' 2>&1 || true"

    [[ "$output" == *"WARNING"* ]]
}
