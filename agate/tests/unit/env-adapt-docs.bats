#!/usr/bin/env bats
# tests/unit/env-adapt-docs.bats — TAG0004 文档/CI/全局层 BDD 断言
# Q2（BDD-23/24/25）、Q5（BDD-26/27）、CI（BDD-33）、shellcheck（BDD-34）、M6 .gitattributes（BDD-16）。
# BDD-23/26/27/33 在修复实现前应红；其余为回归守卫（当前即绿）。

load ../helpers/load.bash

@test "bdd-23 7 张阶段卡片与 git-integration.md 规则 2 对齐（无先更新 phase=N→N+1 旧写法，Q2）" {
    local card
    for card in P1-requirements P2-design P3-tdd P4-implementation P6-acceptance P7-consistency P8-release; do
        run grep -q '更新 .state.yaml phase=' "$AGATE_ROOT/phase-cards/$card.md"
        if [ "$status" -eq 0 ]; then
            echo "FAIL: $card.md 残留 mode B 旧写法（先更新 phase=N→N+1 再 commit）" >&2
            return 1
        fi
    done
}

@test "bdd-24 git-integration.md 规则 2 语义不变（commit 顺序/gate 判定逻辑无改动，Q2）" {
    run grep -q '不得提前写下一阶段' "$AGATE_ROOT/git-integration.md"
    [ "$status" -eq 0 ]
}

@test "bdd-25 修复后协议一致性检查 0 ERROR（worktree 自己的脚本，Q2）" {
    local p
    p=$(py_path "$AGATE_ROOT/scripts/check-protocol-consistency.py")
    echo "B25-DIAG: PYTHON=$PYTHON py_path=$p raw=$AGATE_ROOT/scripts/check-protocol-consistency.py cygpath=$(command -v cygpath || echo NONE)" >&2
    run $PYTHON "$p"
    printf 'B25-OUT: %s\n' "$output" | grep -iE 'error|FAIL|not found|无法|No such' | head -3 >&2
    [ "$status" -eq 0 ]
}

@test "bdd-16 .gitattributes 不含强制 *.md eol 规则（历史 CRLF review 文件不被改写，M6）" {
    local ga="$AGATE_ROOT/../.gitattributes"
    [ -f "$ga" ]
    run grep -E '^\s*[*]*\.md\s' "$ga"
    [ "$status" -ne 0 ]
}

@test "bdd-26 SETUP.md 含 Windows 章节覆盖 PYTHONUTF8（Q5）" {
    run grep -q 'PYTHONUTF8' "$AGATE_ROOT/SETUP.md"
    [ "$status" -eq 0 ]
}

@test "bdd-27 仓库 .gitignore 模板预设 version.txt/dist 白名单（Q5）" {
    local gitignore="$AGATE_ROOT/../.gitignore"
    [ -f "$gitignore" ]
    run grep -E 'version\.txt|dist/' "$gitignore"
    [ "$status" -eq 0 ]
}

@test "bdd-33 protocol-tests.yml 含 windows-latest matrix（Windows 唯一兜底验证）" {
    run grep -q 'windows-latest' "$AGATE_ROOT/../.github/workflows/protocol-tests.yml"
    [ "$status" -eq 0 ]
}

@test "bdd-34 shellcheck -S warning agate/scripts/*.sh 0 error（修复不引入 shellcheck 问题）" {
    run bash -c "${SHELLCHECK:-shellcheck} -S warning '$AGATE_ROOT'/scripts/*.sh 2>&1"
    [ "$status" -eq 0 ]
}

@test "bdd-32 全量 bats 测试文件可被 bats 解析（P5 全量回归前提，BDD-32）" {
    run bash -c "for f in '$AGATE_ROOT'/tests/unit/*.bats '$AGATE_ROOT'/tests/regression/*.bats '$AGATE_ROOT'/tests/integration/*.bats '$AGATE_ROOT'/tests/sanity.bats; do bats -c \"\$f\" >/dev/null 2>&1 || exit 1; done"
    [ "$status" -eq 0 ]
}
