#!/usr/bin/env bats
# tests/unit/install-hook.bats — install-hook.sh .gitignore 检测

load ../helpers/load.bash

@test "install-hook: .gitignore 忽略 .state.yaml → WARNING 提醒" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-ig1")
    echo ".state.yaml" > "$repo/.gitignore"
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ "$output" == *".state.yaml"* ]]
    [[ "$output" == *"忽略"* ]]
}

@test "install-hook: 无 .gitignore → 无 WARNING" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-ig2")
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ "$output" != *".state.yaml"*"忽略"* ]]
}

@test "install-hook: pre-push 是软链指向 pre-push-gate.sh" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-pp1")
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ -L "$repo/.git/hooks/pre-push" ]]
    [[ "$(readlink "$repo/.git/hooks/pre-push")" == "$AGATE_SCRIPTS/pre-push-gate.sh" ]]
}

@test "install-hook: 已有非软链 pre-push → 备份并替换为软链" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-pp2")
    local hook="$repo/.git/hooks/pre-push"
    mkdir -p "$(dirname "$hook")"
    printf '#!/usr/bin/env bash\nexit 0\n' > "$hook"
    run bash -c "cd '$repo' && AGATE_ROOT='$AGATE_ROOT' bash '$AGATE_SCRIPTS/install-hook.sh' '$AGATE_ROOT'" 2>&1
    [[ "$output" == *"已备份现有 pre-push hook"* ]]
    [[ -L "$hook" ]]
    [[ "$(readlink "$hook")" == "$AGATE_SCRIPTS/pre-push-gate.sh" ]]
    [[ -n "$(ls "$(dirname "$hook")"/pre-push.bak.* 2>/dev/null | head -1)" ]]
}

@test "install-hook: ln 退化为复制时打印升级提醒（Windows 兼容）" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-ln")
    local agate_root
    agate_root="$BATS_TEST_TMPDIR/agate-fake"
    mkdir -p "$agate_root/scripts"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$agate_root/scripts/"
    cp "$AGATE_ROOT/scripts/commit-msg-self-gate.sh" "$agate_root/scripts/"
    cp "$AGATE_ROOT/scripts/pre-push-gate.sh" "$agate_root/scripts/"

    # mock ln：让它退化为 cp（模拟 Windows 无符号链接权限）
    local fakebin
    fakebin="$BATS_TEST_TMPDIR/fakebin"
    mkdir -p "$fakebin"
    cat > "$fakebin/ln" <<'LNEOF'
#!/usr/bin/env bash
cp -f "$2" "$3"
LNEOF
    chmod +x "$fakebin/ln"

    run bash -c "cd '$repo' && PATH='$fakebin:$PATH' bash '$AGATE_ROOT/scripts/install-hook.sh' '$agate_root'" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" == *"复制"* || "$output" == *"需重跑"* ]]
}

@test "install-hook: ln 复制模式下 pre-push hook 以复制安装并提示重跑（BDD-18/19）" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-ln-pp")
    local agate_root
    agate_root="$BATS_TEST_TMPDIR/agate-fake-pp"
    mkdir -p "$agate_root/scripts"
    cp "$AGATE_ROOT/scripts/pre-commit-gate.sh" "$agate_root/scripts/"
    cp "$AGATE_ROOT/scripts/commit-msg-self-gate.sh" "$agate_root/scripts/"
    cp "$AGATE_ROOT/scripts/pre-push-gate.sh" "$agate_root/scripts/"

    # mock ln：退化为 cp（模拟 Windows 无符号链接权限），复用 L43 先例
    local fakebin
    fakebin="$BATS_TEST_TMPDIR/fakebin-pp"
    mkdir -p "$fakebin"
    cat > "$fakebin/ln" <<'LNEOF'
#!/usr/bin/env bash
cp -f "$2" "$3"
LNEOF
    chmod +x "$fakebin/ln"

    run bash -c "cd '$repo' && PATH='$fakebin:$PATH' bash '$AGATE_ROOT/scripts/install-hook.sh' '$agate_root'" 2>&1
    [ "$status" -eq 0 ]
    [[ "$output" == *"复制"* || "$output" == *"需重跑"* ]]
    [ -f "$repo/.git/hooks/pre-push" ]
}
