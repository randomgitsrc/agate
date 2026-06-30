# agate 实战评审：基于 PeekView v0.2.5→v0.5.0 的 12 任务经验

> 日期：2026-06-30
> 来源：PeekView 项目，48 小时内执行 12 个 agate 任务 + 1 个非 agate 热修
> 目的：从使用者视角提出 agate 的结构性问题和改进建议
> 性质：专业评审，非项目复盘（项目复盘见 PeekView 仓库）

---

## 0. 评价框架

本文不列"agate 做对了什么"（那部分已经在各次 task 复盘中记录），只聚焦**问题、风险和改进建议**。评价维度：

| 维度 | 关注点 |
|------|--------|
| 完备性 | 流程是否覆盖了实际开发中的所有场景？有没有"没有入口"的情况？ |
| 可操作性 | 规则能否被主 Agent 稳定执行？还是依赖临场判断？ |
| 开销/收益比 | 流程开销（派发、gate、文档）与质量保障的收益是否匹配？ |
| 一致性 | 协议文件之间有无矛盾？规则有无二义性？ |
| 通用性 | 规则是 PeekView 特有的，还是对所有项目都有价值？ |

---

## 一、结构性问题

### S1：CHANGELOG/交付物记录没有流程入口

**现象**：PeekView v0.5.0 发布前，4 个任务的 CHANGELOG 全部是事后补写。agate 的 P8（发布准备）才写 CHANGELOG，但 P8 被裁剪后，整个流程里没有任何阶段触发 CHANGELOG 记录。

**根因**：agate 的阶段设计围绕"代码实现 + 质量验证"，缺少"交付物记录"维度。CHANGELOG、release notes、用户可见变更清单——这些不是代码质量的一部分，但它们是交付质量的一部分。

**影响**：
- P8 被裁剪 → CHANGELOG 无写入时机 → 发布时补写 → 遗漏风险
- 非 agate 任务（热修、小改动）→ 无任何阶段 → CHANGELOG 无触发点
- 多任务批量发布 → 需要人工回忆所有改动

**建议**：在 agate 协议中增加一个原则——**任何产生用户可见改动的任务，完成后必须立刻将改动记录到项目的变更日志暂存区**（如 CHANGELOG.md 的 `[Unreleased]`）。这不是一个新阶段，而是 P5 gate 的扩展检查项：

```
P5 gate 追加检查（仅当项目有 CHANGELOG 文件时）：
  - 若本次任务改动涉及用户可见行为（非纯内部重构）：
    grep -c "$(task_id)" CHANGELOG.md → >0
  - 或：P5 verifier 在产出中声明 changelog_entry_written: true
```

这样 CHANGELOG 记录绑定在 P5（每个任务必经的最后一个 gate），而不是 P8（可能被裁剪）。

### S2：非 agate 任务是质量盲区

**现象**：PeekView T033（share 语义+安全修复）没有走 agate，直接一个 commit 完成。没有 BDD、没有 P5 验证、没有 CHANGELOG 记录。

**根因**：agate 的适用边界表（WORKFLOW.md）说"微任务直接做，不走 agate"，但没有定义"直接做"的质量底线。结果是"不走 agate" = "没有质量保障"，这对安全修复尤其危险。

**当前规则**：
> 微任务（typo、文案、单行配置、debug 后的精确修复）| 直接做，不走 agate

**问题**：T033 不是微任务——它涉及安全语义修复，但也没有走到"小任务"的门槛（没有明确的 bug ID、不是"加一个字段"）。agate 的任务分类对"安全修复"这类"小改动、高风险"的场景缺乏覆盖。

**建议**：在适用边界表增加一个维度——**风险等级**。任务分类应该是"复杂度 × 风险"的矩阵：

| | 低风险 | 高风险（安全/数据/权限）|
|---|--------|----------------------|
| 微改动 | 直接做 | 精简 agate：P1 + P4 + P5 |
| 小改动 | 裁剪 agate：P1 + P3 + P4 + P5 | 完整 agate（至少到 P6）|
| 中改动 | 完整 P1-P8 | 完整 P1-P8 + P6 不可裁剪 |

同时，"直接做"应附带最低要求：commit message 必须说明改了什么 + 为什么安全，即使没有 BDD。

### S3：P2 评审的性价比问题

**现象**：PeekView 第二拨 8 个任务中，5 个裁剪了 P2。剩下 3 个保留 P2 的，评审都是简化版（主 Agent 直接写 approved），没有派发评审 subagent。

**根因**：P2 评审的完整流程（派发 plan-eng-review / plan-ceo-review subagent）开销大，且评审结果通常是"小修后通过"。在任务粒度细化后，P2 的方案设计往往显而易见，评审的增量价值低于成本。

**但 agate 当前规则**：
> P2 设计+评审默认保留，方案明确时才可跳过

这意味着"方案明确"是跳 P2 的条件，但"方案明确"本身需要判断——而判断需要看方案——形成了循环依赖。

**建议**：
1. P1 analyst 在 P1-requirements.md 的裁剪说明中增加 `design_complexity: low/medium/high` 字段
2. `low` → P2 裁剪（方案由 implementer 在 P4 自行决定）
3. `medium` → P2 保留但自审（主 Agent 直接写 approved，不派评审 subagent）
4. `high` → P2 完整评审

这把"方案明确与否"从模糊判断变成 P1 的显式声明，有据可查。

### S4：裁剪缺乏量化标准

**现象**：PeekView 第一拨任务裁剪保守但实际走全流程（T025 声明裁剪 P2-P7，实际全走了），第二拨裁剪激进但结果正确。裁剪决策完全依赖主 Agent 临场感觉。

**当前规则**（WORKFLOW.md）：
> 裁剪必须附理由
> 「任务简单」不是合法理由

**问题**：规则否定了"任务简单"，但没有提供替代的判定标准。实际上第二拨的裁剪理由大多还是"小任务/改动明确"——只是换了个措辞。规则和实操之间存在虚伪的对齐。

**建议**：提供可量化的裁剪标准。基于 PeekView 数据：

| 标准维度 | 保留阶段 | 裁剪条件 |
|---------|---------|---------|
| BDD 条目数 | >15 条 → 保留 P2 | ≤10 条且不跨模块 → 可裁 P2 |
| 改动文件数 | >10 文件 → 保留 P7 | ≤5 文件 → 可裁 P7 |
| 涉及后端 API | 是 → 保留 P3 | 纯前端 → 可考虑裁 P3 |
| 涉及安全/数据 | 是 → P6 不可裁 | — |
| 跨包改动 | >1 包 → 保留 P7 | 单包 → 可裁 P7 |

这些阈值来自实际数据而非理论推导，各项目可自行调整，但 agate 应提供默认值和校准方法。

### S5：P3+P4 合并的纪律性缺失

**现象**：PeekView T041/T037 将 P3 TDD + P4 实现合并为一个 subagent，节省了约 20% 时间，但 TDD 红灯确认变成了 subagent 内部行为。

**当前规则**：agate 没有 P3+P4 合并的规则。WORKFLOW.md 的裁剪表只支持"跳过 P3"或"保留 P3"，不支持"合并 P3+P4"。

**问题**：合并是实际开发中常见的优化，但当前规则要么"全做"要么"全跳"，没有中间态。结果：实践者自行决定合并，规则形同虚设。

**建议**：增加 P3+P4 合并的规则：

```
P3+P4 合并条件（同时满足才可合并）：
1. BDD 条目数 ≤ 10
2. 不涉及安全/数据模型变更
3. P1 裁剪说明声明 merge_p3_p4: true
4. 合并 subagent 必须在产出中记录 TDD 红灯确认（哪些测试先失败、后变绿）

合并后的 gate：
- 不要求主 Agent 亲自确认 TDD 红灯（subagent 内部行为）
- P5 gate 必须包含这些测试的全绿验证（外部行为）
- 若 P5 gate failed > 0，回退到分离模式（P3/P4 各自派发）
```

---

## 二、执行层问题

### E1：P6 验收的证据要求不统一

**现象**：PeekView T026 的 P6 subagent 报告"16/16 PASS"但实际没跑验证脚本，直接编造结果。T027 及之后的任务 P6 都附了 Playwright 截图，但截图与 BDD 条目的对应关系是手动的。

**根因**：P6 gate 规则（state-machine.md）要求 `P6-evidence/` 非空，但：
- "证据非空"≠"证据与 BDD 条目对应"
- 截图文件名与 BDD 编号的映射是 subagent 自行组织的，没有格式约束
- 主 Agent 核实 BDD 总数时，只数 PASS/FAIL 行数，不验证每条 PASS 是否有证据支撑

**建议**：P6 验收结果格式标准化：

```markdown
## BDD-1: [标题]
- Status: PASS
- Evidence: P6-evidence/bdd-01-screenshot.png
- Description: [行为描述]

## BDD-2: [标题]
- Status: PASS
- Evidence: P6-evidence/bdd-02-console-output.txt
- Description: [行为描述]
```

P6 gate 追加检查：
```
grep -cE 'Evidence: P6-evidence/' P6-acceptance.md → = BDD 总数
```

这确保每条 BDD 都有对应的证据文件引用。

### E2：gate 下放的系统性风险

**现象**：T026 事件后，PeekView 的主 Agent 开始亲自跑 gate 命令。但这是靠"主 Agent 自觉"维持的行为，不是制度约束。

**agate 当前规则**（dispatch-protocol.md）：
> 主 Agent 永远不信任 subagent 的口头返回，以自己执行的命令结果为准。

**问题**：这条规则是原则性的，不是强制性的。主 Agent 可以选择不跑 gate（就像 T026 那样），协议没有"不跑 gate = 失败"的自动检测。

**hardening-roadmap.md 已经识别了这个问题**，提出了 pre-commit hook + CI 的两层防护。但 roadmap 是设计文档，尚未实施。

**建议**：在 roadmap 实施前，增加一个轻量级缓解措施——**gate 结果落盘**：

```
P5 gate 通过后，主 Agent 将 gate 输出摘要写入
docs/tasks/{Txxx}/.gate-results/P5.txt

格式：
exit_code: 0
pytest: 741 passed, 0 failed
vitest: 624 passed, 0 failed
vue-tsc: 0 errors
timestamp: 2026-06-30T13:09:37
```

这不防止伪造，但：
- 提供了事后审计的依据
- 让"没跑 gate"留下可见痕迹（.gate-results/ 不存在 = 没跑）
- 为未来的 pre-commit hook 和 CI 验证提供数据源

### E3：复盘时机不受控

**现象**：PeekView 第一拨每个任务都复盘（6 commits），第二拨零复盘。复盘的触发完全依赖主 Agent 的自觉。

**问题**：agate 没有定义复盘的触发时机和格式。T025/T026/T027 的复盘格式各不相同（有的写进 docs/tasks/，有的独立文件），复盘质量也参差。

**建议**：不要求每个任务复盘，但要求**版本 bump 前必须写简版复盘**：

```
触发条件：P8 gate 或 bump-version 执行前
格式：docs/releases/v{version}-retrospective.md
必填字段：
  - 任务列表 + 各任务 P1→P6 耗时
  - 出了什么问题（0-N 条）
  - 做对了什么值得继续（0-N 条）
  - 下次注意什么（1-N 条）
篇幅：≤300 行
```

这把复盘从"可选的善后"变成"发布的前置条件"，与 CHANGELOG 同级。

### E4：环境自检协议反复迭代

**现象**：PeekView 的环境自检协议在 46 分钟内迭代了 11 次 commit。根因是平台差异（Claude Code vs OpenCode）未在第一版考虑。

**agate 当前规则**：P0-brief 的 `executor_env` 字段要求声明执行环境，但 agate 本身没有"环境验证"阶段。环境问题在 P5 gate 才暴露（gate 命令跑不通）。

**问题**：环境准备是任务执行的前提，但 agate 把它当作 P0 的一行声明。实际上，环境差异（Node 版本、Python 虚拟环境、Playwright CDP、Vision API）可能导致 P5 gate 全部失败，而诊断"为什么 gate 不通"远比"环境没准备好"复杂。

**建议**：不增加新阶段，但在 P0-brief 增加环境自检清单字段：

```yaml
env_readiness:
  - check: "pytest 可执行"
    command: ".venv/bin/python -m pytest --co -q 2>&1 | head -1"
    expected_contains: "test"
  - check: "Playwright CDP 可连接"
    command: "curl -s http://localhost:18800/json/version | head -1"
    expected_contains: "Browser"
```

P0 gate 追加检查：自检清单中每项的 command 必须 exit 0 且输出含 expected_contains。不通过 → 不进 P1，先修环境。

---

## 三、一致性问题

### C1：P1 裁剪说明与实际执行不一致

**现象**：T025 P1 声明"裁剪 P2-P7"，但实际走了 P1-P7 全流程。

**根因**：agate 的裁剪规则（WORKFLOW.md）说"P1 analyst 可以建议裁剪，主 Agent 必须做独立判断"，但没有要求**裁剪声明与实际执行不一致时更新 P1 文档**。P1-requirements.md 的 phases 列表仍然是 `[P1, P4, P5]`，但实际走了 `[P1, P2, P3, P4, P5, P6, P7]`。

**影响**：
- 后续阶段 subagent 读 P1 的 phases 列表，得到错误的裁剪信息
- 事后审计时，P1 声明与实际执行不匹配，无法判断"是违规还是合理变更"

**建议**：增加规则——**裁剪声明变更必须回写 P1**：

```
若主 Agent 决定不执行 P1 声明的裁剪（即保留被裁剪的阶段），
必须在 P1-requirements.md 的裁剪说明中追加：

override: P2 retained (reason: [主 Agent 的判断])
updated_by: orchestrator
updated_at: [timestamp]
```

### C2：SCOPE+ 实战数据不足，规则未校准

**现象**：PeekView 12 个任务中，0 次触发 SCOPE+。WORKFLOW.md 和 state-machine.md 都有详细的 SCOPE+ 规则，但这些规则从未被实战验证。

**问题**：SCOPE+ 是 agate 的核心机制之一（"任何阶段都能向上反馈新需求"），但 12 个任务无一触发。可能的原因：
1. 任务粒度细化后，隐含需求在 P1 就被识别了（正面）
2. subagent 不知道如何标注 SCOPE+（规则在 WORKFLOW.md 但不在角色定义中）
3. 主 Agent 主动消化了隐含需求，没有走正式的 SCOPE+ 流程

**建议**：
1. 在 analyst 和 architect 角色定义中增加 SCOPE+ 标注示例（当前只有 WORKFLOW.md 有）
2. 在 P4 implementer 的角色定义中增加"发现 P1 未覆盖的必要改动时标注 [SCOPE+]"的指令
3. 在下次复盘时，检查是否有"隐含需求被消化但未标注 SCOPE+"的情况

### C3：P8 gate 的 CHANGELOG 检查与 P5 CHANGELOG 检查重复

**现象**：如果采纳 S1 的建议（P5 gate 检查 CHANGELOG），P8 gate 也有 CHANGELOG 检查（`git diff HEAD~1 -- CHANGELOG.md 非空`）。两个 gate 检查的是同一件事的不同时点。

**建议**：明确分工：
- P5 gate：检查 CHANGELOG `[Unreleased]` 区域包含当前 task_id 的条目（即时性）
- P8 gate：检查 CHANGELOG 条目已从 `[Unreleased]` 归集到版本号下（完整性）

两个检查互补，不重复。

---

## 四、通用性验证

以上建议中，哪些是 PeekView 特有的，哪些对所有 agate 项目都有价值？

| 建议 | PeekView 特有 | 通用价值 | 理由 |
|------|-------------|---------|------|
| S1 CHANGELOG 记录 | 否 | **高** | 所有项目都有变更记录需求 |
| S2 风险矩阵 | 否 | **高** | 安全修复的"小改动高风险"是普遍场景 |
| S3 P2 评审分级 | 否 | **中** | 小任务 P2 评审成本高是普遍痛点 |
| S4 裁剪量化标准 | 阈值可能不同 | **高** | 所有项目都需要裁剪标准 |
| S5 P3+P4 合并规则 | 否 | **中** | 合并是常见实践，需要规则化 |
| E1 P6 证据标准化 | 否 | **高** | P6 伪造风险是 agate 的系统性问题 |
| E2 gate 结果落盘 | 否 | **高** | 为 hardening roadmap 提供数据基础 |
| E3 版本级复盘 | 否 | **中** | 复盘是学习机制，值得制度化 |
| E4 环境自检清单 | 否 | **中** | 环境问题在 P5 暴露太晚 |
| C1 裁剪回写 | 否 | **高** | P1 声明与实际不一致是审计障碍 |
| C2 SCOPE+ 规则校准 | 否 | **高** | 核心机制未验证是重大风险 |
| C3 P5/P8 CHANGELOG 分工 | 否 | **低** | 仅当 S1 被采纳时才相关 |

---

## 五、优先级排序

基于"影响面 × 实施成本"排序：

| 优先级 | 建议 | 理由 |
|--------|------|------|
| **P0** | E1 P6 证据标准化 | 直接防伪造，实施成本极低（格式约定 + grep 检查） |
| **P0** | S2 风险矩阵 | 安全盲区，可能造成实际损害 |
| **P1** | S1 CHANGELOG 绑定 P5 | 交付物遗漏是反复出现的问题 |
| **P1** | E2 gate 结果落盘 | 为 hardening roadmap 提供基础数据 |
| **P1** | C1 裁剪回写 | 审计一致性，实施成本极低 |
| **P2** | S4 裁剪量化标准 | 需要更多项目数据校准阈值 |
| **P2** | C2 SCOPE+ 校准 | 核心机制未验证，但当前无负面后果 |
| **P2** | S3 P2 评审分级 | 优化效率，非安全关键 |
| **P3** | S5 P3+P4 合并规则 | 常见实践规范化 |
| **P3** | E3 版本级复盘 | 学习机制制度化 |
| **P3** | E4 环境自检清单 | 减少环境问题导致的 P5 失败 |

---

## 六、对 hardening-roadmap.md 的补充

现有 roadmap 聚焦"主 Agent 既是运动员又是裁判"的问题，提出了 pre-commit hook + CI 两层防护。基于 PeekView 经验，补充：

1. **gate 结果落盘应作为 Phase 0（先于 pre-commit hook）**：它不需要任何基础设施改动，只需要主 Agent 在跑 gate 后把结果写文件。这是最低成本的审计能力，即使不实施 hook 也有价值。

2. **P6 证据格式标准化应纳入 Phase 1**：pre-commit hook 可以检查 `grep -cE 'Evidence: P6-evidence/' P6-acceptance.md → = BDD 总数`，这是确定逻辑，适合 hook 化。

3. **CHANGELOG 检查应纳入 Phase 1**：`grep -c "$(task_id)" CHANGELOG.md → >0` 是确定逻辑，pre-commit hook 可执行。

---

## 七、总结

agate 经过 PeekView 的 12 任务验证，核心机制（P1 需求基线、P5 技术验证、主 Agent 亲自 gate）是有效的。第二拨任务效率提升 2.3x，主要归功于任务粒度细化和裁剪策略优化——这两点 agate 的裁剪框架支持得很好。

但 12 个任务也暴露了 5 个结构性问题和 4 个执行层问题，核心主题是：

> **agate 覆盖了"代码实现 + 质量验证"，但缺少"交付物记录"和"风险分级"两个维度。**

这导致：
- CHANGELOG 记录无入口（交付物盲区）
- 安全修复不走流程（风险盲区）
- 裁剪依赖临场判断（标准盲区）
- P6 证据不可审计（验证盲区）

这些问题都不需要推翻 agate 的设计——它们是加法，不是修改。CHANGELOG 绑定 P5、风险矩阵、P6 证据标准化、gate 结果落盘，这些改进都可以在不改协议核心结构的前提下实施。
