#!/usr/bin/env bats
# tests/unit/agate-debt-check.bats — agate-debt-check.py / check-debt.py（TAG0001 技术债登记闭环）
#
# 新增交付物（P2-design.md §2.1-2.5 + gate_commands.P3，P2 固化）：
#   - check-debt.py FILE        = 默认 FILE 模式：tech-debt.md schema 校验（fail-closed）
#   - check-debt.py --retreat-coverage = 回退覆盖比对（只读 WARNING；依赖加载失败 exit 2，无 retreat 提交等有意跳过 exit 0）
#   - agate-debt-check.py       = 多条目 schema 校验器（` ```yaml ` fenced 块解析）
#
# 覆盖 P1-requirements.md 的 20 条 BDD（1:1：test_bdd_N_* 命名，N = BDD 编号）。
# 当前全部红灯（TDD）：check-debt.py / agate-debt-check.py 尚未实现（P4 交付）；
# BDD-1..4 / 12 / 16 / 18 / 19 / 20 为协议文档锚点（P4 同步修改），红灯因"被测模块未改"。
# check-gate.sh P8 的 debt_check 行为用例见 tests/unit/check-gate.bats 的 G8.9 / G8.10。

load ../helpers/load.bash

setup() {
    # TAG0009 BDD-16/17：harness shim——产品脚本内部裸 python3 在"仅 python 可解析"环境解析到真解释器
    local shim
    shim=$(create_python_shim_bin) || return 1
    if [ -n "$shim" ]; then
        export PATH="$shim:$PATH"
    fi
}

# ========== 功能组 A：debt/ 归类修正（工作区目录，BDD-1..4） ==========

@test "test_bdd_1_workflow_directory_diagram_has_debt_dir" {
    # WORKFLOW.md 目录图含 debt/ 子目录，且 agents/ 注释不再包含 tech-debt（BDD-1）
    run grep -q 'debt/' "$AGATE_ROOT/WORKFLOW.md"
    [ "$status" -eq 0 ]
    run grep -E 'agents/.*tech-debt' "$AGATE_ROOT/WORKFLOW.md"
    [ "$status" -eq 1 ]
}

@test "test_bdd_2_mkdir_nine_subdirs_synced_across_three_files" {
    # 三处 mkdir 同步为同一 9 子目录集（含 debt/），且该集可实际建出 9 个目录（BDD-2）
    local ws_dirs="roadmap,tasks,agents,archived,reviews,decisions,plans,logs,debt"
    run grep -qF "$ws_dirs" "$AGATE_ROOT/SETUP.md"
    [ "$status" -eq 0 ]
    run grep -qF "$ws_dirs" "$AGATE_ROOT/orchestrator-template.md"
    [ "$status" -eq 0 ]
    run grep -qF "$ws_dirs" "$AGATE_ROOT/state-machine.md"
    [ "$status" -eq 0 ]
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/ws-XXXXXX")
    mkdir -p "$dir/roadmap" "$dir/tasks" "$dir/agents" "$dir/archived" "$dir/reviews" "$dir/decisions" "$dir/plans" "$dir/logs" "$dir/debt"
    local n
    n=$(ls -1 "$dir" | wc -l | tr -d ' ')
    [ "$n" -eq 9 ]
}

@test "test_bdd_3_setup_upgrading_debt_path_consistent" {
    # SETUP/UPGRADING 指向 {AGATE_WORKSPACE}/debt/tech-debt.md，无指向 agents/ 的过期路径（BDD-3）
    run grep -q 'debt/tech-debt.md' "$AGATE_ROOT/UPGRADING.md"
    [ "$status" -eq 0 ]
    run grep -q 'debt' "$AGATE_ROOT/SETUP.md"
    [ "$status" -eq 0 ]
    run grep -E 'agents/tech-debt' "$AGATE_ROOT/UPGRADING.md"
    [ "$status" -eq 1 ]
}

@test "test_bdd_4_tag0003_scope_rechecked_to_nine" {
    # TAG0003 已验收工作区口径随本次修正重验（8→9，修订注在案，BDD-4）
    local tag3_p1="$AGATE_ROOT/../agate-workspace/tasks/TAG0003-workspace-architecture/P1-requirements.md"
    local tag3_p6="$AGATE_ROOT/../agate-workspace/tasks/TAG0003-workspace-architecture/P6-acceptance.md"
    [ -f "$tag3_p1" ]
    [ -f "$tag3_p6" ]
    run grep -q '9 子目录' "$tag3_p1"
    [ "$status" -eq 0 ]
    run grep -q '9 子目录' "$tag3_p6"
    [ "$status" -eq 0 ]
}

# ========== 功能组 B：DEBT 条目 schema 校验（Phase 1，BDD-5..10） ==========

@test "test_bdd_5_valid_entry_passes_schema" {
    # 合法条目（open 无 task_id + closed 含 task_id 与 P5/P6 证据引用）→ exit 0 无输出（BDD-5）
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/debt-XXXXXX")
    cat > "$dir/tech-debt.md" <<'EOF'
# 技术债登记

## DEBT0001

```yaml
id: DEBT0001
category: technical
title: 模块耦合
status: open
priority: high
evidence:
  - path: docs/reviews/review-20260812-1204.md
impact: 未来变更更贵
recommendation: 拆分模块
closure_criteria:
  - 拆分完成
source: review
created_at: 2026-08-12
```

## DEBT0002

```yaml
id: DEBT0002
category: management
title: 验收流程遗留
status: closed
priority: medium
task_id: TAG0002
evidence:
  - path: docs/tasks/TAG0002/P6-acceptance.md
impact: 影响后续验收
recommendation: 补登记
closure_criteria:
  - 验收通过
source: review
created_at: 2026-08-12
```
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/tech-debt.md"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

@test "test_bdd_6_evidence_missing_intercepted" {
    # evidence 字段缺失（或为空）→ 拦截并报 evidence（BDD-6）
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/debt-XXXXXX")
    cat > "$dir/tech-debt.md" <<'EOF'
# 技术债登记

## DEBT0001

```yaml
id: DEBT0001
category: technical
title: 无证据债
status: open
priority: high
impact: 未来变更更贵
recommendation: 补证据
closure_criteria:
  - 补证据
source: review
created_at: 2026-08-12
```
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/tech-debt.md"
    [ "$status" -eq 1 ]
    [[ "$output" == *"evidence"* ]]
}

@test "test_bdd_7_invalid_enum_values_intercepted" {
    # category/status/priority 枚举外值 → 拦截并报非法值（category 限 technical|management|protocol）（BDD-7）
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/debt-XXXXXX")
    cat > "$dir/tech-debt.md" <<'EOF'
# 技术债登记

## DEBT0001

```yaml
id: DEBT0001
category: bug
title: 非法枚举
status: open
priority: high
evidence:
  - path: docs/reviews/x.md
impact: 未来变更更贵
recommendation: 修正枚举
closure_criteria:
  - 枚举修正
source: review
created_at: 2026-08-12
```
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/tech-debt.md"
    [ "$status" -eq 1 ]
    [[ "$output" == *"category"* ]]
}

@test "test_bdd_8_closed_missing_task_id_or_p5p6_intercepted" {
    # closed 缺 task_id 或缺 P5/P6 证据引用 → 拦截（准入 = task_id + 证据引用，缺一不可）（BDD-8）
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/debt-XXXXXX")
    # 子场景 1：closed 缺 task_id
    cat > "$dir/closed-no-task.md" <<'EOF'
# 技术债登记

## DEBT0001

```yaml
id: DEBT0001
category: management
title: 已关闭债
status: closed
priority: medium
evidence:
  - path: docs/tasks/TAG0002/P6-acceptance.md
impact: 影响验收
recommendation: 补 task_id
closure_criteria:
  - 补 task_id
source: review
created_at: 2026-08-12
```
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/closed-no-task.md"
    [ "$status" -eq 1 ]
    [[ "$output" == *"task_id"* ]]
    # 子场景 2：closed 有 task_id 但 evidence 未引用 P5/P6
    cat > "$dir/closed-no-evidence-ref.md" <<'EOF'
# 技术债登记

## DEBT0001

```yaml
id: DEBT0001
category: management
title: 已关闭债
status: closed
priority: medium
task_id: TAG0002
evidence:
  - path: docs/tasks/TAG0002/meeting.md
impact: 影响验收
recommendation: 补证据引用
closure_criteria:
  - 补证据引用
source: review
created_at: 2026-08-12
```
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/closed-no-evidence-ref.md"
    [ "$status" -eq 1 ]
    [[ "$output" == *"P5"* || "$output" == *"P6"* || "$output" == *"evidence"* ]]
}

@test "test_bdd_9_three_state_and_open_with_task_id_legal" {
    # 三态状态机：open + task_id 视为 in_progress（合法）；schema 仅允许 open/in_progress/closed 三值（BDD-9）
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/debt-XXXXXX")
    cat > "$dir/open-with-task.md" <<'EOF'
# 技术债登记

## DEBT0001

```yaml
id: DEBT0001
category: technical
title: 已立项债
status: open
priority: high
task_id: TAG0009
evidence:
  - path: docs/reviews/x.md
impact: 未来变更更贵
recommendation: 处理
closure_criteria:
  - 处理完成
source: review
created_at: 2026-08-12
```
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/open-with-task.md"
    [ "$status" -eq 0 ]
    cat > "$dir/fourth-state.md" <<'EOF'
# 技术债登记

## DEBT0001

```yaml
id: DEBT0001
category: technical
title: 额外态
status: accepted
priority: high
evidence:
  - path: docs/reviews/x.md
impact: 未来变更更贵
recommendation: 修正
closure_criteria:
  - 修正
source: review
created_at: 2026-08-12
```
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/fourth-state.md"
    [ "$status" -eq 1 ]
    [[ "$output" == *"status"* ]]
}

@test "test_bdd_10_no_file_or_no_yaml_block_is_noop" {
    # 无文件 / 空文件 / 无 yaml 块（旧格式纯正文）→ exit 0 无输出（向后兼容，BDD-10）
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/debt-XXXXXX")
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/not-exist.md"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
    : > "$dir/empty.md"
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/empty.md"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
    cat > "$dir/prose-only.md" <<'EOF'
# 技术债登记
旧格式纯正文，无 yaml 块。
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/tech-debt.md"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

# ========== 功能组 C：T001 回填验证模板（Phase 1 试金石，BDD-11） ==========

@test "test_bdd_11_t001_backfill_entries_pass_schema" {
    # T001 复盘 T1-T4（+协议原因 A5）回填为 DEBT 条目并通过校验（止损条件 1 的可观测判据，BDD-11）
    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/debt-XXXXXX")
    cat > "$dir/tech-debt.md" <<'EOF'
# 技术债登记（T001 回填）

## DEBT-T1

```yaml
id: DEBT-T1
category: technical
title: T1 问题
status: open
priority: high
evidence:
  - path: docs/reviews/T001-retrospective-2026-08-10.md
  - note: 根因：T1 根因
impact: T1 影响
recommendation: T1 建议
closure_criteria:
  - T1 判据
source: retrospective
created_at: 2026-08-12
```

## DEBT-T2

```yaml
id: DEBT-T2
category: technical
title: T2 问题
status: open
priority: high
evidence:
  - path: docs/reviews/T001-retrospective-2026-08-10.md
  - note: 根因：T2 根因
impact: T2 影响
recommendation: T2 建议
closure_criteria:
  - T2 判据
source: retrospective
created_at: 2026-08-12
```

## DEBT-T3

```yaml
id: DEBT-T3
category: technical
title: T3 问题
status: open
priority: medium
evidence:
  - path: docs/reviews/T001-retrospective-2026-08-10.md
  - note: 根因：T3 根因
impact: T3 影响
recommendation: T3 建议
closure_criteria:
  - T3 判据
source: retrospective
created_at: 2026-08-12
```

## DEBT-T4

```yaml
id: DEBT-T4
category: technical
title: T4 问题
status: open
priority: medium
evidence:
  - path: docs/reviews/T001-retrospective-2026-08-10.md
  - note: 根因：T4 根因
impact: T4 影响
recommendation: T4 建议
closure_criteria:
  - T4 判据
source: retrospective
created_at: 2026-08-12
```

## DEBT-A5

```yaml
id: DEBT-A5
category: protocol
title: A5 协议原因
status: open
priority: low
evidence:
  - path: docs/reviews/T001-retrospective-2026-08-10.md
  - note: 根因：A5 根因
impact: A5 影响
recommendation: A5 建议
closure_criteria:
  - A5 判据
source: retrospective
created_at: 2026-08-12
```
EOF
    run "$PYTHON" "$AGATE_SCRIPTS/check-debt.py" "$dir/tech-debt.md"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
}

# ========== 功能组 D：回退事件强制登记（Phase 2，BDD-12..15） ==========

@test "test_bdd_12_retreat_requires_debt_entry_documented" {
    # 回退相关协议文档明确"回退落地后必须建 DEBT 条目"（BDD-12）
    run grep -q 'DEBT' "$AGATE_ROOT/rules/state-transitions.md"
    [ "$status" -eq 0 ]
    run grep -q 'DEBT' "$AGATE_ROOT/phase-cards/P6-acceptance.md"
    [ "$status" -eq 0 ]
    run grep -q 'DEBT' "$AGATE_ROOT/phase-cards/P4-implementation.md"
    [ "$status" -eq 0 ]
    run grep -q 'DEBT' "$AGATE_ROOT/scripts/agate-retreat-to.sh"
    [ "$status" -eq 0 ]
}

@test "test_bdd_13_retreat_commit_without_entry_warns" {
    # git 历史含 retreat 提交但无对应条目 → WARNING（exit 0，不阻断 commit/发布）（BDD-13）
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    git -C "$repo" commit -qm "retreat: P6 -> P4（诊断：测试回退）" --allow-empty
    run bash -c "cd '$repo' && "$PYTHON" '$AGATE_SCRIPTS/check-debt.py' --retreat-coverage"
    [ "$status" -eq 0 ]
    [[ "$output" == *"GATE DEBT WARNING"* ]]
}

@test "test_bdd_14_retreat_entry_present_no_warning" {
    # 已建 source: retreat 条目且 evidence 引用该提交 → 无缺失提示（BDD-14）
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    git -C "$repo" commit -qm "retreat: P5 -> P4（诊断：测试回退）" --allow-empty
    local short
    short=$(git -C "$repo" rev-parse --short HEAD)
    mkdir -p "$repo/agate-workspace/debt"
    cat > "$repo/agate-workspace/debt/tech-debt.md" <<'EOF'
# 技术债登记

## DEBT-R1

```yaml
id: DEBT-R1
category: management
title: 回退债
status: open
priority: medium
evidence:
  - path: @HASH@
impact: 影响未来变更
recommendation: 补登记
closure_criteria:
  - 补登记完成
source: retreat
created_at: 2026-08-12
```
EOF
    sed -i "s/@HASH@/$short/" "$repo/agate-workspace/debt/tech-debt.md"
    run bash -c "cd '$repo' && "$PYTHON" '$AGATE_SCRIPTS/check-debt.py' --retreat-coverage"
    [ "$status" -eq 0 ]
    [[ "$output" != *"GATE DEBT WARNING"* ]]
}

@test "test_bdd_15_real_retreat_records_fixture_reproducible" {
    # 用真实 retreat 提交消息格式（023b28b P5->P4 / 29301ad P6->P5）构造 fixture，两个方向可复现（BDD-15）
    local repo
    repo=$(git_init)
    echo "init" > "$repo/README.md" && git_commit "$repo" "init"
    git -C "$repo" commit -qm "retreat: P5 -> P4（诊断：BDD-17: check-p6-format.sh --fix 破坏 frontmatter pass/fail 字段，需修复（用户已批准 2026-08-10））" --allow-empty
    git -C "$repo" commit -qm "retreat: P6 -> P5（诊断：BDD-17: check-p6-format.sh --fix 破坏 frontmatter pass/fail 字段，需修复（用户已批准 2026-08-10））" --allow-empty
    # 方向 A：未建条目 → 报缺失 WARNING
    run bash -c "cd '$repo' && "$PYTHON" '$AGATE_SCRIPTS/check-debt.py' --retreat-coverage"
    [ "$status" -eq 0 ]
    [[ "$output" == *"GATE DEBT WARNING"* ]]
    # 方向 B：已建条目且 evidence 引用两个提交 → 通过
    local s1 s2
    s1=$(git -C "$repo" rev-parse --short HEAD)
    s2=$(git -C "$repo" rev-parse --short HEAD~1)
    mkdir -p "$repo/agate-workspace/debt"
    cat > "$repo/agate-workspace/debt/tech-debt.md" <<'EOF'
# 技术债登记

## DEBT-R1

```yaml
id: DEBT-R1
category: management
title: 回退债一
status: open
priority: medium
evidence:
  - path: @HASH1@
impact: 影响未来变更
recommendation: 补登记
closure_criteria:
  - 补登记完成
source: retreat
created_at: 2026-08-12
```

## DEBT-R2

```yaml
id: DEBT-R2
category: management
title: 回退债二
status: open
priority: medium
evidence:
  - path: @HASH2@
impact: 影响未来变更
recommendation: 补登记
closure_criteria:
  - 补登记完成
source: retreat
created_at: 2026-08-12
```
EOF
    sed -i "s/@HASH1@/$s1/; s/@HASH2@/$s2/" "$repo/agate-workspace/debt/tech-debt.md"
    run bash -c "cd '$repo' && "$PYTHON" '$AGATE_SCRIPTS/check-debt.py' --retreat-coverage"
    [ "$status" -eq 0 ]
    [[ "$output" != *"GATE DEBT WARNING"* ]]
}

@test "test_bdd_16 check-debt.py --retreat-coverage 缺 agate-workspace-resolve.sh -> exit 2 + stderr 报错（BDD-16）" {
    # 依赖加载失败属硬失败，不静默当作成功跳过（同类扫描守卫 BDD-16）
    local sdir
    sdir=$(mktemp -d "$BATS_TEST_TMPDIR/debt-XXXXXX")
    cp "$AGATE_SCRIPTS/check-debt.py" "$sdir/check-debt.py"
    run "$PYTHON" "$sdir/check-debt.py" --retreat-coverage
    [ "$status" -eq 2 ]
    [[ "$output" == *"缺少 agate-workspace-resolve.sh"* ]]
}

# ========== 功能组 E：P8 锚定留痕（Phase 3，BDD-16..18） ==========

@test "test_bdd_16_p8_card_requires_debt_confirm_and_field" {
    # P8 阶段指引要求确认债务清单，且产出规格含 debt_check 字段（BDD-16）
    run grep -q '确认债务清单' "$AGATE_ROOT/phase-cards/P8-release.md"
    [ "$status" -eq 0 ]
    run grep -q 'debt_check' "$AGATE_ROOT/phase-cards/P8-release.md"
    [ "$status" -eq 0 ]
}

@test "test_bdd_17_p8_gate_checks_debt_check_existence_only" {
    # check-gate.sh P8 分支含 debt_check 留痕检查（只查存在，不查内容；行为用例见 check-gate.bats G8.9/G8.10）（BDD-17）
    run grep -q 'debt_check:' "$AGATE_ROOT/scripts/check-gate.sh"
    [ "$status" -eq 0 ]
}

@test "test_bdd_18_empty_confirmation_observable" {
    # "本次无关注项"（debt_check: none）是 P8 卡片明示的合法选项，可跨发布 grep 计数（BDD-18 止损条件 4 数据形态）
    run grep -q 'debt_check: none' "$AGATE_ROOT/phase-cards/P8-release.md"
    [ "$status" -eq 0 ]
}

# ========== 功能组 F：债 vs 缺陷判据（cross-cutting，BDD-19..20） ==========

@test "test_bdd_19_criteria_documented_with_no_registration_outlet" {
    # 模板判据含三分法，且"都不影响→不登记"是合法出口（防垃圾场）（BDD-19）
    local tmpl="$AGATE_ASSETS/templates/tech-debt-template.md"
    [ -f "$tmpl" ]
    run grep -q '验收声明' "$tmpl"
    [ "$status" -eq 0 ]
    run grep -q '不登记' "$tmpl"
    [ "$status" -eq 0 ]
}

@test "test_bdd_20_registration_does_not_exempt_current_task" {
    # 登记 DEBT 不得豁免当前任务（模板硬规则）+ review 卡强制标准 DEBT 条目格式（BDD-20）
    local tmpl="$AGATE_ASSETS/templates/tech-debt-template.md"
    [ -f "$tmpl" ]
    run grep -q '豁免' "$tmpl"
    [ "$status" -eq 0 ]
    run grep -q 'DEBT 条目格式' "$AGATE_ROOT/assets/review-roles/plan-eng-review.md"
    [ "$status" -eq 0 ]
}
