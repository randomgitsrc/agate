# evidence 类型检查 + office-hours 清理

> 2026-08-04 | 来源：roadmap 待处理项

## Task 1: evidence 类型检查（gate 层硬约束）

**来源**：`docs/archived/plans/agate-evidence-diagnosis-v2-2026-07-02.md`（已有完整论证）
**必要性**：`ui_affected: true` 时 evidence 全是 .md/.txt（源码分析充数）无法被现有 gate 拦截。agent 回退读源码写成 .txt 当证据 → PASS 通过 → 真实 UI 问题被掩盖。
**不绑定工具**：不检查是否用了 vision-engine/playwright-cdp，只检查"有没有运行时数据文件"（.json/.log/.png/.yaml 等非纯文本）。

### 改动

**`agate/scripts/check-p6-evidence.sh`**：在现有 UI 检查块中追加 evidence 类型检查。

当 `ui_affected: true` 且 evidence 目录存在时：
```bash
NON_TEXT_COUNT=$(find "$EVIDENCE_DIR" -type f -not -name '.*' \
    ! -name '*.md' ! -name '*.txt' 2>/dev/null | wc -l)
if [ "$NON_TEXT_COUNT" -eq 0 ]; then
    echo "GATE P6-EVIDENCE: ui_affected=true 但 evidence 全是纯文本（.md/.txt），缺少运行时数据（.json/.log/.png/.yaml 等）" >&2
    exit 1
fi
```

### 测试

```bash
@test "E.15 ui_affected=true + evidence 全是 .md/.txt → exit 1" {
    # ui_affected: true, P6-evidence/ 只有 .md 和 .txt → exit 1
}

@test "E.16 ui_affected=true + evidence 含 .json → exit 0" {
    # ui_affected: true, P6-evidence/ 含 .json → exit 0
}
```

## Task 2: office-hours 角色清理 + 六问内化 P0

**必要性**：触发条件"大任务"无客观定义、从未被触发、非门槛评审零约束力。死代码增加 agent 认知负担。但 office-hours 的"Startup Mode 六问"对 P0 立项有实际价值——T078 教训：P0-brief 肤浅导致重写。
**方案**：删除角色文件 + 清理所有引用 + 六问内化到 P0 卡片作为 P0-brief 质量自检清单。不增加派发开销，主 Agent 对照自检即可。

### Step 1: P0 卡片内化六问

在 `agate/phase-cards/P0-orchestrator.md` 的"任务类型提示"节后追加：

```markdown
## P0-brief 质量自检（源自 office-hours 六问）

写完 P0-brief 后对照自检（非门槛，但跳过可能导致 P1 需求不完整）：
1. 需求真实性：有没有人真的需要这个（不是假设性需求）
2. 现状：用户现在怎么解决这个问题
3. 绝望的具体性：最痛的那个人是谁
4. 最窄切入点：最小可交付版本是什么
5. 亲眼观察：有没有看过实际使用场景
6. 未来契合：这个方向长期是否成立
```

### Step 2: 删除角色文件

删除 `agate/assets/review-roles/office-hours.md`。

### Step 3: 清理引用

清理 9 处引用：
- `agate/rules/review-mapping.md` L23, L46
- `agate/dispatch-protocol.md` L1005
- `agate/WORKFLOW.md` L56, L217
- `agate/role-system.md` L48, L62, L114
- `agate/AGENTS.md` L68
- `agate/phase-cards/P2-design.md` L74

每处删除 office-hours 相关行/选项，保留其他角色不变。

### 测试

无脚本测试（纯文件删除+内化）。consistency checker 确认无断引用。

## Task 3: roadmap + 验证

### Step 1: roadmap 更新

两项从"待处理/待论证"改为"已实施"。

### Step 2: 验证

```bash
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
python3 agate/scripts/check-protocol-consistency.py
shellcheck -S warning agate/scripts/*.sh
```

## Self-Review

### 不增加 agent 负担

- Task 1: gate 自动检查，agent 无感。evidence 类型检查只在 `ui_affected: true` 时触发，非 UI 任务不受影响
- Task 2: 删角色减少 agent 认知负担（少一个可选角色要理解）。六问内化为 P0 自检清单，不派 subagent，零开销

### 向后兼容

- Task 1: 新检查只拦截"全是纯文本"的极端情况。已有 .json/.log/.png 的正常任务不受影响
- Task 2: office-hours 从未触发过，删除无实际影响。六问内容保留在 P0 卡片，智慧不丢

### 风险

- Task 1: 某些非 UI 任务可能也产生纯 .md evidence → 只在 `ui_affected: true` 时检查，非 UI 任务不受影响
- Task 2: 删除后如有外部项目引用 office-hours 角色 → 降级为"角色不存在"提示，不影响流程
