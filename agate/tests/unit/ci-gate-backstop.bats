#!/usr/bin/env bats
# tests/unit/ci-gate-backstop.bats — ci-gate-backstop.py 平台探测 + P3 兜底
# TAG0002 [SCOPE+]: 新增 change_type=refactor 任务跳过 check-tdd-red 用例（BDD-7/8）

load ../helpers/load.bash

# TAG0009 BDD-22/23/26：输出编码显式化——含中文输出（真红灯/绿灯/SKIP）的 python 工具
# 统一在文件级 export PYTHONIOENCODING=utf-8，保证中文关键词断言命中且不 UnicodeEncodeError 崩溃
setup() {
    export PYTHONIOENCODING=utf-8
    # Windows python 无法解析 MSYS /c/... 路径——经 py_path 转 C:/...（TAG0009）
    BACKSTOP_PY=$(py_path "$AGATE_SCRIPTS/ci-gate-backstop.py")
}

@test "detect_ci_platform: Gitea 优先于 GitHub 被识别" {
    local repo
    repo=$(git_init)
    cd "$repo"
    export GITEA_ACTIONS=true
    export GITHUB_ACTIONS=true
    run bash -c "$PYTHON $BACKSTOP_PY 2>/dev/null || true"
    [[ "$output" == *"gitea"* ]]
}

@test "detect_ci_platform: GitLab CI 正确识别" {
    local repo
    repo=$(git_init)
    cd "$repo"
    export GITLAB_CI=true
    unset GITEA_ACTIONS GITHUB_ACTIONS
    run bash -c "$PYTHON $BACKSTOP_PY 2>/dev/null || true"
    [[ "$output" == *"gitlab"* ]]
}

@test "detect_ci_platform: 无可识别平台时 SKIP 而非误判" {
    local repo
    repo=$(git_init)
    cd "$repo"
    unset GITEA_ACTIONS GITLAB_CI GITHUB_ACTIONS
    run bash -c "$PYTHON $BACKSTOP_PY 2>/dev/null || true"
    [[ "$output" == *"SKIP"* || "$output" == *"None"* ]]
}

# ========== P3 兜底测试 ==========

setup_git_repo_p3() {
    local repo="$1"
    git_init "$repo"
    mkdir -p "$repo/agate-workspace/tasks/T001"
    # 根 .state.yaml（ci-gate-backstop.py 读根目录的）
    cat > "$repo/.state.yaml" <<'EOF'
task_id: T001
phase: P3
status: active
retries: {}
EOF
    echo '## P3 test cases' > "$repo/agate-workspace/tasks/T001/P3-test-cases.md"
    git -C "$repo" add -A
    git -C "$repo" commit -qm "p3"
}

@test "backstop P3: 真红灯（exit 0）→ PASS" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-ok")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-ok"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 0' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "$PYTHON $BACKSTOP_PY 2>&1 || true"
    output=$(printf '%s' "$output" | tr -d '\r')
    [[ "$output" == *"真红灯"* ]]
}

@test "backstop P3: 绿灯（exit 2）→ FAIL" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-green")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-green"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 2' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "$PYTHON $BACKSTOP_PY 2>&1 || true"
    output=$(printf '%s' "$output" | tr -d '\r')
    [[ "$output" == *"FAIL"* ]]
    [[ "$output" == *"绿灯"* ]]
}

@test "backstop P3: 假红灯（exit 1）→ FAIL" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-afake")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-fake"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 1' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "$PYTHON $BACKSTOP_PY 2>&1 || true"
    output=$(printf '%s' "$output" | tr -d '\r')
    [[ "$output" == *"FAIL"* ]]
    [[ "$output" == *"假红灯"* ]]
}

@test "backstop P3: 无运行器（exit 3）→ WARN 不 FAIL" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-norunner")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-norunner"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 3' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "$PYTHON $BACKSTOP_PY 2>&1 || true"
    [[ "$output" == *"WARN"* ]]
    [[ "$output" != *"FAIL"* ]]
}

@test "backstop P3: 无 .gate-result.json（--no-verify）时仍执行 check-tdd-red.sh" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-noverify")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-ok2"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 0' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    # 不创建 .gate-result.json（模拟 --no-verify 场景）
    run bash -c "$PYTHON $BACKSTOP_PY 2>&1 || true"
    output=$(printf '%s' "$output" | tr -d '\r')
    [[ "$output" == *"真红灯"* ]]
}

# ========== TAG0002 [SCOPE+]: P3 分支 refactor 感知（BDD-7/8，ci-gate-backstop 不误杀 refactor 任务） ==========

@test "backstop P3: change_type=refactor 任务跳过 check-tdd-red（SKIP 而非 FAIL，即使 mock exit 2 绿灯）" {
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-refactor")
    setup_git_repo_p3 "$repo"
    # refactor 任务：P1-requirements.md 声明 change_type: refactor（TDD 红灯不适用）
    cat > "$repo/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
risk_level: medium
change_type: refactor
---
#### BDD-1: 关键路径行为不变
- Given 重构后的协议状态
- When 执行关键路径
- Then 行为与重构前一致
EOF
    git -C "$repo" add -A
    git -C "$repo" commit -qm "p3 refactor"
    cd "$repo"
    export GITHUB_ACTIONS=true
    # mock 返回 exit 2（绿灯）——若 backstop 不感知 refactor 会把合法任务误判 FAIL
    local mock="$BATS_TEST_TMPDIR/mock-tdd-refactor"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 2' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "$PYTHON $BACKSTOP_PY 2>&1 || true"
    [[ "$output" == *"SKIP"* ]]
    [[ "$output" == *"refactor"* ]]
    [[ "$output" != *"FAIL"* ]]
}

@test "backstop P3: 功能任务正文提及 change_type 关键字仍走 TDD 兜底（不 SKIP，BDD-2）" {
    # P4-review §2.1 BLOCKER 回归：功能任务 frontmatter 无 change_type，仅正文散文提及
    # `change_type: refactor` → backstop 不得误判为 refactor 跳过 check-tdd-red。
    # mock exit 2（绿灯）→ 正确行为是 FAIL；若误判 refactor 会输出 SKIP 且 exit 0。
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-body-mention")
    setup_git_repo_p3 "$repo"
    cat > "$repo/agate-workspace/tasks/T001/P1-requirements.md" <<'EOF'
---
agent: test
risk_level: medium
---
change_type: refactor 是可选字段，缺省为功能任务（本文档仅作说明，本任务不采用 refactor 口径）
EOF
    git -C "$repo" add -A
    git -C "$repo" commit -qm "p3 body mention"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-body-mention"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 2' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    run bash -c "$PYTHON $BACKSTOP_PY 2>&1 || true"
    output=$(printf '%s' "$output" | tr -d '\r')
    [[ "$output" == *"FAIL"* ]]
    [[ "$output" == *"绿灯"* ]]
    [[ "$output" != *"SKIP: refactor"* ]]
}

@test "backstop P3: cp1252 模拟——无 utf-8 导出崩溃、文件级导出兜底不崩溃（BDD-23/26）" {
    # 模拟 Windows 默认代码页 cp1252（中文"真红灯"在 cp1252 下不可表示）：
    #   ① 未显式设置 PYTHONIOENCODING 时工具 print 中文 → UnicodeEncodeError 崩溃（证明 cp1252 是风险源）
    #   ② 文件级 setup() export PYTHONIOENCODING=utf-8 → 工具以 utf-8 输出，无崩溃、中文关键词命中
    #     （BDD-23「显式设置 PYTHONIOENCODING」机制；cp1252 无法表示中文属 codec 保证，断言平台无关）
    local repo
    repo=$(git_init "$BATS_TEST_TMPDIR/repo-p3-cp1252")
    setup_git_repo_p3 "$repo"
    cd "$repo"
    export GITHUB_ACTIONS=true
    local mock="$BATS_TEST_TMPDIR/mock-tdd-cp1252"
    echo '#!/bin/bash' > "$mock"
    echo 'exit 0' >> "$mock"
    chmod +x "$mock"
    export AGATE_TDD_RED_SCRIPT="$mock"
    # ① 清除继承的 utf-8 导出 + 强制 cp1252 → 中文 print 崩溃
    run env -u PYTHONIOENCODING bash -c "PYTHONIOENCODING=cp1252 '$PYTHON' $BACKSTOP_PY 2>&1 || true"
    [[ "$output" == *"UnicodeEncodeError"* ]]
    # ② 文件级 utf-8 导出生效 → 无崩溃、中文关键词可断言
    run bash -c "'$PYTHON' $BACKSTOP_PY 2>&1 || true"
    output=$(printf '%s' "$output" | tr -d '\r')
    [[ "$output" != *"UnicodeEncodeError"* ]]
    [[ "$output" == *"真红灯"* ]]
}
