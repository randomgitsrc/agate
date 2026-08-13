#!/usr/bin/env bats
# tests/integration/pre-push-hook.bats — pre-push hook 集成测试（指向真实 pre-push-gate.sh）

load ../helpers/load.bash

@test "pre-push hook: 新分支首次推送提示跳过检测" {
    local repo
    repo=$(git_init)

    ( cd "$repo" && bash "$AGATE_ROOT/scripts/install-hook.sh" "$AGATE_ROOT" >/dev/null 2>&1 )
    # 平台分支：Linux 断言软链语义（readlink 指向 pre-push-gate.sh，无 -L 字面满足 R3 零命中）；
    # Windows 复制模式断言文件已安装（软链语义由 Linux 分支 + mock ln 用例覆盖）
    if [[ "$(uname -s)" == *MINGW* || "$(uname -s)" == *MSYS* ]]; then
        [ -f "$repo/.git/hooks/pre-push" ] || fail "pre-push 应已安装"
    else
        [[ "$(readlink "$repo/.git/hooks/pre-push")" == "$AGATE_ROOT/scripts/pre-push-gate.sh" ]] || fail "pre-push 应为软链"
    fi

    cd "$repo"
    echo "test" > file.txt
    git add file.txt
    git commit -m "init" --no-gpg-sign --no-verify

    run bash -c "echo 'refs/heads/main $(git rev-parse HEAD) refs/heads/main 0000000000000000000000000000000000000000' | bash '$AGATE_ROOT/scripts/pre-push-gate.sh' 2>&1 || true"

    [[ "$output" == *"新分支"* ]]
}

@test "pre-push hook: ln 复制模式下安装输出升级提醒且不要求软链（Windows 兼容，BDD-18/19）" {
    local repo
    repo=$(git_init)
    local agate_root
    agate_root="$BATS_TEST_TMPDIR/agate-fake"
    mkdir -p "$agate_root/scripts"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$agate_root/scripts/"
    cp "$AGATE_ROOT/scripts/commit-msg-self-gate.sh" "$agate_root/scripts/"
    cp "$AGATE_ROOT/scripts/pre-push-gate.sh" "$agate_root/scripts/"

    # mock ln：退化为 cp（模拟 Windows 无符号链接权限）
    local fakebin
    fakebin="$BATS_TEST_TMPDIR/fakebin"
    mkdir -p "$fakebin"
    cat > "$fakebin/ln" <<'LNEOF'
#!/usr/bin/env bash
cp -f "$2" "$3"
LNEOF
    chmod +x "$fakebin/ln"

    run bash -c "cd '$repo' && PATH='$fakebin:$PATH' bash '$AGATE_ROOT/scripts/install-hook.sh' '$agate_root'" 2>&1
    [[ "$output" == *"复制"* || "$output" == *"需重跑"* ]]
    [ -f "$repo/.git/hooks/pre-push" ]
}

@test "pre-push hook: 大改动触发提示" {
    local repo
    repo=$(git_init)

    ( cd "$repo" && bash "$AGATE_ROOT/scripts/install-hook.sh" "$AGATE_ROOT" >/dev/null 2>&1 )

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

    run bash -c "echo 'refs/heads/main $current_sha refs/heads/main $prev_sha' | AGATE_ALIGNMENT_REVIEW_THRESHOLD=2 bash '$AGATE_ROOT/scripts/pre-push-gate.sh' 2>&1 || true"

    [[ "$output" == *"改动"* ]]
}

@test "pre-push hook: 无 agate/*.md 改动时零匹配 → 不报整数表达式错误（T086 回归）" {
    local repo
    repo=$(git_init)

    ( cd "$repo" && bash "$AGATE_ROOT/scripts/install-hook.sh" "$AGATE_ROOT" >/dev/null 2>&1 )

    cd "$repo"
    echo "test" > file.txt
    git add file.txt
    git commit -m "init" --no-gpg-sign --no-verify
    local prev_sha
    prev_sha=$(git rev-parse HEAD)

    echo "test2" > file.txt
    git add file.txt
    git commit -m "change" --no-gpg-sign --no-verify
    local current_sha
    current_sha=$(git rev-parse HEAD)

    run bash -c "echo 'refs/heads/main $current_sha refs/heads/main $prev_sha' | bash '$AGATE_ROOT/scripts/pre-push-gate.sh' 2>&1 || true"

    [[ "$output" != *"整数表达式"* ]]
    [[ "$output" != *"integer expression"* ]]
    [[ "$status" -eq 0 ]]
}
