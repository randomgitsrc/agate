---
task_id: agate-phase-cards
agent: main
date: 2026-07-05
status: 实施计划
来源: docs/reviews/agate-cognitive-load-progressive-disclosure-2026-07-05.md
评审记录:
  - docs/reviews/agate-cognitive-load-progressive-disclosure-review-2026-07-05.md（6攻击点评审）
  - docs/reviews/agate-cognitive-load-progressive-disclosure-meta-review-2026-07-05.md（再评审，收敛方向）
  - docs/reviews/agate-phase-cards-implementation-plan-review-2026-07-05.md（计划评审，6 发现→7 修复）
---

# 渐进披露：Phase Card 实施计划

## 目标

把 agate 主 Agent 的单次加载量从 ~2900 行（8 个协议文件）降到 ~80 行（1 张阶段卡片 + mapping 表），每次只持有当前阶段的执行信息。

## 实施范围

### 前置修复（独立 bug，不影响卡片架构）

**Issue #001**：P0 commit 被 pre-commit hook 误拦截。两层根因：

**根因 1**：`check-gate.sh` 无 `P0)` 分支，P0 落到 `*)` → 输出"未知阶段"，且每次写 `.gate-history.jsonl` 审计轨迹（P0 是协议标准阶段，不应谎报"未知"）。

**根因 2**：`pre-commit-gate.sh` 用 `check-pruning.sh || exit 1` 把 exit 2（P1 文件不存在 → 跳过）当 exit 1（硬拦截）处理。

修复（两处都做，非二选一）：

```bash
# 修复 1: check-gate.sh 加 P0 分支（停止谎报）
P0)
    echo "GATE P0: 立项阶段无需脚本 gate（仅 P0-brief.md）。主 Agent 确认 P0-brief 五字段齐全即可推进 P1。" >&2
    exit 2 ;;

# 修复 2: pre-commit-gate.sh 2j/2k 节改为捕获退出码（与 2i 节对齐）
if [ "$GATE_EXIT" != "1" ]; then
    PRUNE_EXIT=0
    bash "$AGATE_ROOT/scripts/check-pruning.sh" "$TASK_DIR" || PRUNE_EXIT=$?
    if [ "$PRUNE_EXIT" -eq 1 ]; then
        exit 1
    fi
fi
# 2k 节 check-scope-resolved.sh 同款处理
```

来源：`~/.agate/docs/issues/issue-001-pre-commit-p0-block.md` + 评审 `docs/reviews/agate-issue-001-p0-hook-fix-review-2026-07-05.md`

### 新增文件（12 个）

```
agate/phase-cards/                   # 阶段执行卡片（执行层 single source of truth）
├── README.md                        # 卡片索引 + 快速导航
├── P0-orchestrator.md               # 任务启动：P0-brief / 环境自检 / 任务粒度 / 容器/loop 模式
├── P1-requirements.md               # 需求基线：BDD / packages/domains / 能力声明 / 裁剪声明
├── P2-design.md                     # 方案设计：候选方案 / files_to_read / gate_commands / 最小验证 / 评审派发
├── P3-tdd.md                        # TDD 红灯：测试设计 / check-tdd-red / 测试代码目录
├── P4-implementation.md             # 实现：代码目录 / 评审派发 / 常见返工原因
├── P5-verification.md               # 技术验证：gate_commands 执行 / 结果判定 / E2E 命令
├── P6-acceptance.md                 # 验收：BDD 对照 / 证据要求 / vision-helper 结论绑定 / 常见凑格式陷阱
├── P7-consistency.md               # 一致性：DESIGN_GAP / SCOPE+ / [BLOCKER] / 跨文件交叉检查
├── P8-release.md                   # 发布：bump_type / 版本文件 / CHANGELOG / 临时资源清理

agate/rules/                         # 跨阶段规则（按需查阅，不上膛）
├── state-transitions.md             # 从 state-machine.md 提取：转移条件 / retry 上限 / 中断恢复步骤
└── review-mapping.md               # 从 role-system.md 提取：C8 机械映射表
```

### 修改文件（2 个）

| 文件 | 改动 |
|------|------|
| `agate/orchestrator-template.md` | mapping 表替代"8 个要读的文件"列表；保留项目配置段（agate_root/project_root） |
| `agate/AGENTS.md` | 索引指向 phase-cards/README.md；旧文件标记为 reference |

### 不变文件（8 个协议文件全部保留）

`WORKFLOW.md` / `dispatch-protocol.md` / `state-machine.md` / `role-system.md` / `loop-orchestration.md` / `git-integration.md` / `LIMITATIONS.md` / `platform-notes.md` 全部保留，在 AGENTS.md 标记为 reference。Agent 按需查阅——不是每轮必读。

### 非范围

- gate 脚本/测试不变
- subagent 角色文件不变
- pre-commit hook 不变
- gate 硬化计划（`agate-cognitive-overload-gate-hardening`）不受影响，独立推进

## 卡片模板（8 节统一结构）

```markdown
# P{N} — {阶段名}

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]

## 如果是首次进入本阶段
完整流程（派发 subagent → 产出 → gate → 推进）

## 如果是重试
确认失败原因 → 只修复失败项 → 读 rules/state-transitions.md 确认 retry 上限

## 如果是裁剪跳阶
确认 P1 phases 不含 P{N} + 裁剪理由合规 → 跳过，读下一张卡片

## 前置条件
进入本阶段前必须满足的条件（gate 会检查的）

## 派发
- 角色：{角色名}（路径: {角色文件路径}）
- 输入：{上游产出文件列表}
- 输出：{本阶段产出文件列表}
- 派发 prompt 模板：（从 dispatch-prompt.md 提取对应段）

## 产出规格
产出文件的要求（Header 字段、必需小节、格式约束）

## gate 规则
gate 脚本会检查什么 + 判定逻辑（exit 0/1/2 的含义）

## 推进条件
全部满足才写 phase: P{N+1}

## 常见错误
本阶段最容易犯的错误 + 正确做法

## 下游影响
P{N+1} 需要... / P6 验收要求... / 本阶段输出错误会导致哪些后续阶段 fail
```

## 实施步骤

### 步骤 1：写 rules/ 文件（跨阶段规则）

- [ ] **`agate/rules/state-transitions.md`**：从 state-machine.md 提取
  - 转移条件表（P1→P2→...→P8 每个阶段需要什么文件 + 什么 gate 结果）
  - retry 上限表（每个阶段 MAX retries）
  - 中断恢复步骤（读 .state.yaml → 确认 phase → 查 mapping → 读卡片）
  - 状态标记绑定规则（状态不能先于 gate 通过）

- [ ] **`agate/rules/review-mapping.md`**：从 role-system.md 提取 C8 机械映射表
  - domain × risk_level → 评审角色矩阵
  - 各评审角色产出文件路径 + status 字段要求
  - 专家组并行 + 组长汇总机制

### 步骤 2：写 10 张卡片（P0-P8 + README）

**架构决策：内联 vs 引用的混合模式**

卡片内容分两类：
- **流程骨架**（"本阶段做什么"——派发谁/产出什么/前置条件/常见错误）→ **内联**。这部分稳定，改动频率低。
- **规则细节**（gate 判定逻辑/裁剪条件具体阈值/C8 映射的完整矩阵）→ **引用协议文件精确行范围**。这部分仍在高速迭代（v0.8 后 3 天 18 commits，含 4 个 feat:），内联会导致频繁漂移。

引用格式：`见 dispatch-protocol.md:420-445`。Agent 只读那个片段而非整个文件。

注意：meta-review 的"稳定期"论断基于虚构的版本统计（实际 v0.6.0 tag 不存在、v0.3→v0.8 仅 4 天、18 commits/3 天），不能作为内联决策的依据。

#### P0-orchestrator.md
- 来源：orchestrator-template.md（除项目配置外）+ loop-orchestration.md 启动段
- 关键内容：P0-brief 五字段、任务粒度判断、环境自检、项目配置模板、loop 模式说明

#### P1-requirements.md
- 来源：dispatch-protocol.md P1 节 + task-files.md P1 结构
- 关键内容：BDD 格式、packages/domains 声明、capability_requirements 三态、裁剪声明 phases/risk_level、[NEED_CONFIRM] 规则
- 评审：暂无（已知缺口，见 review §四）

#### P2-design.md
- 来源：WORKFLOW.md P2 + dispatch-protocol.md P2 节 + task-files.md P2 结构
- 关键内容：候选方案 ≥2、权衡+选择理由、四字段（packages/domains/ui_affected/gate_commands）、files_to_read、最小验证触发条件、评审派发（C8 映射内联 + rules/review-mapping.md 引用）
- 下游影响：P4 依赖 files_to_read 导航、P5 依赖 gate_commands 执行命令、P6 依赖 ui_affected 判断是否需要 vision

#### P3-tdd.md
- 来源：WORKFLOW.md P3 + dispatch-protocol.md P3 节 + task-files.md P3 结构
- 关键内容：check-tdd-red 判定规则（红灯 vs 绿/第三方 import 失败/SyntaxError 的区别）、test_code_dir 声明、E2E 用例（ui_affected: true 时必含）
- 下游影响：P4 用测试驱动实现、P5 跑同一套测试

#### P4-implementation.md
- 来源：WORKFLOW.md P4 + dispatch-protocol.md P4 节 + task-files.md P4 结构
- 关键内容：implementation_dir 声明、按 files_to_read 导航阅读（不乱翻项目）、PROD_TOUCHED 禁止、评审派发（C8 映射内联）
- 常见错误：自行加范围外改动（SCOPE+ 必须走流程）、不读 files_to_read 在项目里乱翻
- 下游影响：P5 验证实现正确性、P6 验收用户可见结果——确认实现路径的端点行为已验证

#### P5-verification.md
- 来源：WORKFLOW.md P5 + dispatch-protocol.md P5 节
- 关键内容：逐条执行 gate_commands.P5（含 P5_e2e）、ui_affected 时实跑 E2E、紧凑输出模式、只判断过没过不看 traceback、FAIL ≠ 阻塞（主 Agent 判定是否真错误）
- 常见错误：不跑 E2E（只跑单元测试）、把测试绿了当作功能正确

#### P6-acceptance.md
- 来源：WORKFLOW.md P6 + dispatch-protocol.md P6 节 + task-files.md P6 结构
- 关键内容：BDD 逐条对照（只允许 PASS/FAIL）、证据引用格式、vision-helper 结论绑定（blocker>0 不能仅用程序化指标反驳）、evidence 文件内容质量要求
- **关键的避免 T046 型失败部分**：先验证功能（用户视角），再满足 gate 格式。收到视觉否定 → 先追查不要反驳。gate 格式凑满了但功能不对 → 等于没验收
- 常见错误：凑 PASS 数量（deferred BDD 标 PASS）、用 1 行文本文件充证据、DOM 属性替代视觉验证

#### P7-consistency.md
- 来源：WORKFLOW.md P7 + dispatch-protocol.md P7 节
- 关键内容：DESIGN_GAP 配对（P4 出现 → P7 必须转抄 + REVIEWED）、SCOPE+ 闭环（P1 有 [SCOPE_RESOLVED]）、[BLOCKER] 检查、源码文件数 ≤5（裁剪条件）

#### P8-release.md
- 来源：WORKFLOW.md P8 + dispatch-protocol.md P8 节 + task-files.md P8 结构
- 关键内容：bump_type 选择、version 文件变更确认、CHANGELOG [Unreleased] → 版本号、临时资源清单、发布检查命令

#### README.md（卡片索引）
- 9 张卡片路径 + 一句话描述
- rules/ 文件索引
- 旧 protocol 文件索引（reference）
- 快速参考表：card → 对应旧文件

### 步骤 3：改 orchestrator-template.md

**不删**"8 个要读的协议文件"列表（删除会触发 CHECK 5 FILE_COUNT_ANCHORS ERROR）。mapping 表叠加在列表之上——改动为：

1. 保留现有 8 文件列表不动
2. 在列表之后新增 mapping 表：

```markdown
### 按阶段渐进加载（Mapping 表）

每轮不必全读 8 个文件。根据当前任务阶段，优先只读一张卡片：

| 当前阶段 | 优先读 |
|---------|-------|
| 启动/无任务 | `{agate_root}/phase-cards/P0-orchestrator.md` |
| P1-P8 | `{agate_root}/phase-cards/P{N}-*.md` |
| 跨阶段规则 | `{agate_root}/rules/` 按需查阅 |

卡片查不到的信息，回退到上方完整文件列表。
```

3. **同步改 `state-machine.md:506`**：当前写的是「重读 orchestrator-template 列出的 8 个协议文件」，改为「重读 orchestrator-template 的 mapping 表查当前阶段卡片，然后按卡片指引加载对应协议文件」。注意：这行改动落在 self-gate 触发条件里（`agate/*.md`），需要走 self-gate 流程。

### 步骤 4：改 AGENTS.md

简化入口索引——指向卡片体系：

```markdown
## 给 Agent 的快速指令

1. 读 `orchestrator-template.md`（项目侧拷贝）→ 按 mapping 表加载当前阶段卡片
2. 阶段卡片自包含（前置条件 / 派发 / 产出 / gate / 推进 / 常见错误 / 下游影响）
3. 跨阶段规则（retry/转移/评审映射）在 `rules/` 下按需查阅
4. 旧协议文件在 `agate/*.md`（reference，非必读）
```

### 步骤 5：更新相关追踪

- [ ] `docs/issues/003-main-agent-cognitive-overload.md` 状态：记录实施方向
- [ ] `SELF-GATE.md` 触发条件文档补充说明：`agate/.+/.*\.md` 通配已覆盖 phase-cards/ 和 rules/ 目录，无需追加正则（`commit-msg-self-gate.sh:26` 已实测覆盖）
- [ ] 若因其他原因需动 `commit-msg-self-gate.sh`，顺手给 `self-gate-review:` 和 `self-gate-skip:` 检查加 `^` 行锚（当前缺锚导致 commit body 任意位置提一句即绕过，已知假阴性）

### 步骤 6：验证

**实施前预检**（确认 baseline，防止实施后才发现自造 ERROR）：
- [ ] `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR — 记录当前 baseline 的 CHECK 5 FILE_COUNT_ANCHORS 和 CHECK 9 锚点覆盖状态
- [ ] `grep -n '8 个协议文件' agate/state-machine.md` 确认 state-machine.md:506 引用行，实施时须同步改

**实施后全量验证**：
- [ ] `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` 全绿
- [ ] `python3 agate/scripts/check-protocol-consistency.py` 0 ERROR（重点关注 CHECK 5 + CHECK 9，新增文件可能影响计数锚点和锚点覆盖）
- [ ] 手动验证：在 peekview 下一个任务实际使用卡片模式，观察认知负担和正确率

## 实施节奏

| 步骤 | 预计 | 交付 |
|------|------|------|
| 0a. 前置修复：P0 hook 误拦截 | 3 行改动（独立 bug）| pre-commit-gate.sh 2j/2k 节 |
| 0b. 基准验证 | 先跑（10min）| CHECK 5/9 baseline + state-machine.md:506 定位 |
| 1. rules/ 文件 | 提取+精简现有内容 | 2 个 rules 文件 |
| 2a. 先抽 P4 卡片实测行数 | 用实际数据校正模板 | 1 张卡片 |
| 2b. 其余 9 张卡片 | 依次写 | 8 张卡片 + README |
| 3. orchestrator-template.md | mapping 表叠加 | 1 处改动 |
| 4. state-machine.md:506 | 同步改中断恢复语义 | 1 处改动 |
| 5. AGENTS.md | 改写索引 | 1 处改动 |
| 6. 追踪文件更新 | SELF-GATE + issue | 2 处 |
| 7. 全量验证 | CHECK 5/9 + bats | 全绿 + 0 ERROR |

建议顺序：0a → 0b → 1 → 2a → 2b → 3 → 4 → 5 → 6 → 7。

## 依赖和前置

- 不需要等 gate 硬化计划（`agate-cognitive-overload-gate-hardening`）——卡片和 gate 硬化互不依赖，可以并行
- 不需要改角色文件——卡片只改变主 Agent 读到什么，不改变 subagent 的行为
- 不需要改 gate 脚本——卡片描述 gate 规则，但不替代 gate 脚本执行

## 风险

| 风险 | 缓解 |
|------|------|
| 卡片遗漏关键规则 → Agent 信息不全 | 写卡片时对照 source 文件逐段检查；先在 peekview 试跑再广推 |
| 卡片和协议文件漂移 | 混合模式：规则细节用引用（行范围），协议文件改了立刻反映到卡片引用里；流程骨架内联，漂移概率低 |
| Agent 即使只读 80 行也能跳步 | 真相——此方向的价值需要实验验证。不会比现状更差 |
| 旧文件被 Agent 忽略 → 漏信息 | 卡片末尾放一条"查不到的信息见 reference 文件列表"；保留 AGENTS.md 里的完整文件索引 |
| CHECK 5/9 新增冲突 | 实施前先跑 baseline 验证（新增步骤 0），不靠 step 7 才发现 |
