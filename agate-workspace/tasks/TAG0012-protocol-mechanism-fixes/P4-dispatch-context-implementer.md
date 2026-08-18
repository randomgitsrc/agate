> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心输入源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P4
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0012
role: implementer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

把 P2-design.md 的方案（三类新增机制的具体规则文本 + follows_existing_pattern 的引用式落地）
实际写入 13 个协议文件，让 `test_protocol_mechanism_anchors.py` 的 28 条红灯用例全部转绿。
产出 `P4-implementation.md`（`implementation_dir: agate/`）。**参照先例**：
`{AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P4-implementation.md` 是同类协议文档
批量改动任务的已完成 P4 实现记录（单次 implementer 完成全部改动文件，未真正拆并行派发），本任务
按同一模式单次完成，不拆分成多个并行 subagent。

### 约束（硬约束，逐条遵守）

1. **P2-design.md 是你的主要内容来源，不是简单参考**——§1（候选方案 A/B/C 的采纳文本）、
   §3.1-3.4（具体条款）已经把三类新增机制的规则原文写好，你的工作是把这些文本**转写成协议文档
   正文**（补上小节标题、与既有文档风格衔接的过渡句），不是重新设计或简化这些规则。§2.1"改动
   落点表"是你的逐文件施工清单，最后一列"关键词锚点"是你**必须逐字包含**的字符串（不得意译/
   改写/加空格断开）——这些锚点已被 `agate/tests/unit/test_protocol_mechanism_anchors.py` 的 28
   条 parametrize 用例硬编码断言，用词不一致会导致测试仍红。
2. **BDD-5 特殊要求**：`agate/phase-cards/P1-requirements.md`（卡片文件，注意不是任务目录下的
   P1-requirements.md）需要同时包含 `verification_env` 和 `supplementable` 两个词（AND 语义，
   测试用例 `BDD-5` 要求两者都出现）——`supplementable` 该文件已有 2 处既有出现（不用你新增），
   你只需确保新增的判断树内容里出现 `verification_env` 这个词本身。
3. **CHECK3 硬约束（`check-protocol-consistency.py`）**：所有跨文件引用文本**禁止**写
   `xxx.md L123` 这种硬编码行号格式（正则 `([A-Za-z0-9_\-]+\.md)\s+L\d+`，命中即 ERROR）。
   引用别的协议文件的内容时用"见「节标题」"这种措辞（如"见 dispatch-protocol.md「派发编排机制」
   并行规则"）。P2-design.md §2.1/files_to_read 里出现的 `L123` 是**给你定位当前文件插入点用的
   坐标**，不是要你把这些行号抄进新写的正文。
4. **权威源 vs 引用副本同步（BDD-14）**：`dispatch-prompt.md` 文件头已声明"与 dispatch-protocol.md
   保持同步，协议文件为权威来源"——先落地 `dispatch-protocol.md` 的"命令超时兜底"新段落，再把
   同一段（可精简措辞但语义/关键词一致）同步进 `dispatch-prompt.md` 对应节，避免两处矛盾。
5. **引用式落地（"权威定义 + 卡片/角色文件引用"惯例）**：BDD-15b（architect.md）/BDD-17/18
   （P5-verification.md）/BDD-19（verifier.md）/BDD-20（P6-acceptance.md）都是"新增一句引用已有
   权威定义"，不要在这些文件里重复展开完整规则文本（P2-design.md §3.3/§3.5 已说明）。
6. **落地完成后自跑**：
   ```
   cd /home/kity/oclab/agate/.worktrees/agate-TAG0012
   python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v
   ```
   确认 28 条全部转绿（passed）。仍红的用例逐条核对该文件是否真的写入了对应关键词（原样，不是
   同义词）。**这是自查，不是 gate**——转绿后仍要等主 Agent 派 P5 verifier 做正式验证。
7. **不改测试文件本身**（`test_protocol_mechanism_anchors.py`）——测试红转绿只能靠改协议文件，
   不能靠放宽断言。
8. **不擅自扩大范围**：只改 P2-design.md §2.1 表列出的 13 个文件（见下方逐文件清单），不顺手
   "顺便改进"其他协议内容。发现范围外必须做的事 → 标 `[SCOPE+]`（行首声明格式），不要直接做。
9. **P0-brief 约束 2**：本环境是 Linux，涉及"Windows 兼容"的表述（如 `windows_smoke` 标记、
   CI matrix 兜底）只按现有文档惯例引用，不要新增"已实测 Windows"这类不实宣称。

### 逐文件改动清单（=P2-design.md §2.1 表，13 个文件 + 关键词锚点）

| 文件 | 改动内容 | 对应 BDD | 必须逐字含有的关键词 |
|------|---------|---------|-------------------|
| `agate/phase-cards/P0-orchestrator.md` | 新增"同类/影响面预判"节（`known_risks` 填写指引旁）；「推进条件」新增 P0-brief 时效性自检项（引用 P2-design.md §3.4 的漂移判据） | BDD-1, BDD-2 | `同类/影响面预判`、`[P0_STALE]` |
| `agate/state-machine.md` | L77 转移条件文本紧邻处新增说明段：四字段自查含时效性校验，覆盖任务重启场景，引用 P0 卡规则不重写全文 | BDD-3 | `时效性校验` |
| `agate/phase-cards/P1-requirements.md`（卡片） | 新增"同类扫描"强制节；新增 verification_env vs supplementable 边界判断树（含轮次预算占位声明位）；新增 `[P0_STALE: 具体漂移点]` 标记规则 + 阻塞/记录二选一说明 | BDD-4, BDD-5, BDD-6 | `同类扫描`、`verification_env`（须与既有 `supplementable` 共存于同一文件）、`[P0_STALE:` |
| `agate/assets/execution-roles/analyst.md` | 「隐含需求清单」新增"同类/影响面"维度；「三态判断规则」旁新增判断树；「输入」节新增 P0-brief 时效性质疑步骤 | BDD-7, BDD-8, BDD-9 | `同类/影响面`、`缺的是能力还是环境`、`[P0_STALE]` |
| `agate/dispatch-protocol.md`（verification_env 节，L952-957 现状） | 扩为"条件化 + 失败处理协议"：写入 P2-design.md §1 候选A 的完整规则文本（可/不可重试清单、批处理要求、止损轮次=2 独立计数、READY 后归属三判据）；新增"环境准备职责边界"子节（P2-design.md §3.3 三条条款） | BDD-10, BDD-11 | `可重试`、`不可重试`、`批处理`、`止损轮次`、`环境准备职责边界` |
| `agate/dispatch-protocol.md`（「派发编排机制」§4 并行规则，L691-695） | 新增第 4 条规则："资源密集型默认串行"（全量 pytest xdist / CDP-Playwright E2E 等默认串行），与「全阶段适用表」P5 行建立引用关系 | BDD-12 | `资源密集型默认串行` |
| `agate/dispatch-protocol.md`（「派发 prompt 模板」正文，L429-500） | 新增"命令超时兜底 + 命令前 progress"标准段（P2-design.md §1 候选B 关联决定：×1.5 倍规则 + 超时/非预期失败均停止返回 + 分阶段落盘粒度扩展），与 L790-879 既有「Playwright/长时操作」层级2 硬超时机制建立显式引用区分（标注"层级 4：bash 命令级超时兜底"） | BDD-13 | `命令超时兜底`、`层级 4`、`×1.5` |
| `agate/dispatch-protocol.md`（L521「非阶段产出的路径规范」示例块） | 判定该场景（self-gate/alignment-review，多为 grep/读取类短命令）不适用完整展开，加一句"为何不适用"说明，不重复展开 | BDD-13（条件性子句） | — |
| `agate/assets/templates/dispatch-prompt.md` | 同步 BDD-13 的"命令超时兜底 + 命令前 progress"段落到「分阶段落盘」/「执行顺序」节，文本与 dispatch-protocol.md 对应段落不矛盾 | BDD-14 | `命令超时兜底` |
| `agate/phase-cards/P2-design.md`（卡片） | 新增"影响面梳理"强制节；「gate_commands 声明」节新增 `{key}_timeout_seconds` 字段规则（P2-design.md §1 候选B 全部 4 点：per-key 声明/三档基准表/向后兼容/排除P3关系说明） | BDD-15, BDD-16 | `影响面梳理`、`timeout_seconds` |
| `agate/assets/execution-roles/architect.md`（「批次设计」节） | 新增检查项：引用 P2 卡「影响面梳理」要求（不重复展开）；同步 `timeout_seconds` 字段规则位（引用候选B，不重复展开三档基准表细节） | BDD-15b, BDD-16 | `影响面梳理`、`timeout_seconds` |
| `agate/phase-cards/P5-verification.md`（「按包拆分并行」节，L113-128） | 新增一句引用"资源密集型默认串行"（引用 dispatch-protocol.md BDD-12 规则，不重复展开）；新增一句"环境准备职责边界"落地引用 | BDD-17, BDD-18 | `资源密集型默认串行`、`环境准备职责边界` |
| `agate/assets/execution-roles/verifier.md`（L245-262「verification_env 条件化」节） | 改为引用 dispatch-protocol.md 权威定义（BDD-10/11），不重复展开完整内容 | BDD-19 | `环境准备职责边界`（引用式） |
| `agate/phase-cards/P6-acceptance.md` | 新增一句"P6 环境访问沿用 P5 已由主 Agent 准备的环境；需要新环境时同样遵循 dispatch-protocol.md verification_env 节统一准备规则" | BDD-20 | `环境准备职责边界`（引用式） |
| `agate/assets/templates/task-files.md`（L266 起 `gate_commands:` 样例块） | 新增 `timeout_seconds` 字段格式示例（含用途/缺省行为注释）；若样例中 P3 key 下也标注，须附引用指向候选B「排除P3」说明 | BDD-21 | `timeout_seconds` |

**明确不改**（P2-design.md §2.2 已定，不要顺手改）：`agate/scripts/check-gate.py`、
`agate/scripts/agate_common.py`、`agate/scripts/agate-frontmatter-check.py`、`.state.yaml` schema、
`agate/WORKFLOW.md`、`agate/adr.md`、`agate/loop-orchestration.md`、既有测试文件、`agate/scripts/*.sh`。

### 三类新增机制的具体规则原文（直接来源，转写进对应文件）

**规则文本已在 P2-design.md 写好，你需要读取该文件的以下三节获取逐字规则**（不要自己重新拟定
数值/判据，P2 已经过评审 approved，你的任务是"落地"不是"再设计"）：
- §1 候选方案 A（verification_env 失败处理协议）→ 落 dispatch-protocol.md verification_env 节
- §1 候选方案 B（timeout_seconds 与 AGATE_TDD_TIMEOUT 关系 + 三档基准表 + ×1.5 倍规则）→ 落
  P2-design.md 卡/architect.md/task-files.md（字段规则部分）+ dispatch-protocol.md（×1.5 倍
  命令超时兜底部分）
- §1 候选方案 C（P0-brief 漂移判据，3 条严重/2 条轻微）→ 落 P0-orchestrator.md/P1-requirements.md
  卡/state-machine.md
- §3.3（环境准备职责边界 3 条条款）→ 落 dispatch-protocol.md verification_env 子节，
  P5/P6/verifier.md 引用落地

### 上游关联

- P2-review.md 非阻塞发现 2 点：①批次表遗漏 L521 子句提及（不影响实现，已在上表补全）②
  verification_env 现状实际是"可判定门槛规范"大节下约 6 行的加粗段落（L952-957），不是独立
  `###` 子节——你落地时以实际内容为准，扩写为更完整的子节即可，不需要纠结"节"这个措辞本身。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P2-design.md（全文，尤其 §1/§2.1/§3.1-3.5/§6/files_to_read——主要内容来源）
- {AGATE_WORKSPACE}/tasks/TAG0012-protocol-mechanism-fixes/P1-requirements.md（23 条 BDD 原文，核对 Then 子句细节）
- agate/tests/unit/test_protocol_mechanism_anchors.py（28 条断言，关键词权威来源，逐字核对）
- {AGATE_WORKSPACE}/tasks/TAG0014-dispatch-orchestration/P4-implementation.md（同类任务已完成实现记录的格式参照）
- P2-design.md `files_to_read` 列出的全部文件行号区间（施工定位坐标）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P4

路径：phase-cards/P4-implementation.md
---
# P4 — 代码实现

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P4 且有合规理由（check-pruning.py 已检查）→ 跳过，读 P5 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.py $TASK_DIR`（自动捕获环境基线）。
   该步骤不会阻塞流程——任何 stderr 输出（含 WARNING）均可忽略，直接继续步骤 1，
   无需查看结果、无需判断、无需因为看到 WARNING 而停下来处理。
1. 派发 implementer subagent → 产出代码文件
   1.1 写 P4-dispatch-context-implementer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 P2 的 gate_commands 跑单元测试（非 gate，只是自查）
3. 按 C8 映射表派发评审（见下方）
4. 预跑 check-gate.py P4（确认暂存区有代码文件）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/ + 代码文件（含 .state.yaml，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P4，不要提前写 P5——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P4): {摘要}"（phase=P4，P4 产出含 P4-implementation.md + 代码文件）
7. P4 commit 完成后进入 P5：**phase 推进 P5 随 P5 产出 commit 一起**（P5-test-results/ 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（来自 gate 输出 / review rejected 理由）
→ 只修复失败项，不重做已通过的部分
→ 修复后重跑全量测试（T027 教训：修复可能引入回归）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P4 MAX=3）

**若这次是从 P6（或其他更后的阶段）退回来的**：`{AGATE_WORKSPACE}/tasks/{Txxx}/` 下不会再有旧的 P6-acceptance.md（已被归档），但当初具体是哪条 BDD 失败、失败原因是什么，会摘要在 `{AGATE_WORKSPACE}/tasks/{Txxx}/.retreat-history.md` 里——**重新派发 implementer 时，dispatch-context 必须引用这份摘要**，不能让 implementer 只看到"现有代码"却不知道具体要修哪里。已有代码不会被撤销、也不需要重新实现，是在已有实现基础上定向修复。**回退落地后必须建 DEBT 条目**（`source: retreat`，`evidence` 引用 retreat 提交哈希，模板 `assets/templates/tech-debt-template.md`——TAG0001 强制，见 `agate/rules/state-transitions.md` 回退规则节）。

## 前置条件

- [ ] P2-design.md 存在且 files_to_read 字段完整（导航清单）
- [ ] P2-review.md status: approved（P2 不可裁剪）
- [ ] P3-test-cases.md 存在（测试已设计）
- [ ] check-tdd-red.py 确认红灯（测试先于实现）
- [ ] 未跳过 P4（如有裁剪理由，见上方裁剪跳阶）

## 派发

- **角色**：implementer（`{agate_root}/assets/execution-roles/implementer.md`）
- **输入**：P2-design.md（files_to_read 导航 + gate_commands）+ P3-test-cases.md + P0-brief.md（env_constraints）
- **输出**：代码文件（在 P4-implementation.md 声明的 implementation_dir 下）
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md` + 以下阶段特定追加：

```
## 上下文控制
读取代码文件以 P2-design.md 的 files_to_read 清单为准，按需读取（标了行号范围的只读片段）。
不要在项目里盲目搜索或整目录全读。

## 自查≠gate
写完代码后应自跑测试确认基本功能（自查），但自查通过 ≠ P5 gate 通过。
P5 由主 Agent 派发 verifier subagent 执行 gate_commands.P5，主 Agent 验 gate（检查产出 + failed 计数 + N5 最小校验）。
不要在返回中声称"P5 已过"或"全部测试通过"——只返回路径 + 摘要。

## 生产环境隔离
任何写入生产环境/生产数据库/生产 API 的操作都必须先 PAUSED 报告人工。
```

## 产出规格

- P4-implementation.md 必须声明 `implementation_dir: {实际路径}`
- 代码文件在声明的目录下
- 遵守 P2-design.md 的方案设计 + 现有项目代码规范

## 评审派发（C8 机械映射）

**在 P4 实现完成后、gate 前**，按 P1 声明的 domains 和 risk_level 派评审。C8 映射表是机械规则，不靠判断"需不需要"：

| domain | 派哪些评审 | 产出 |
|--------|----------|------|
| backend | review | P4-review.md |
| frontend | design-review | P4-review.md |
| mcp | review（关注 MCP 接口契约）| P4-review.md |
| security | cso | P4-review.md |
| risk=high | P4 实现评审（按 domains 派 review/design-review/cso；P2 plan-eng-review 已审方案，P4 实现评审不可省）| P4-review.md |

多个评审角色 `专家组并行` → 所有返回后派组长汇总 → 统一 P4-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长产出：P4-review.md。**agent 字段必须非 main**（与 P2 评审同规则，check-gate.py 在 P2 分支硬拦截 agent=main 的 approved）
5. 组长规则：不发表新意见，只汇总；任何 BLOCKER → rejected；分歧 → 交人工；全票无 BLOCKER → approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P4-review.md。

review 不通过 → implementer 修改代码 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

## 按包拆分并行（条件触发，需额外约束）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。
> 并行上限 / 失败批 retry / 共享文件统一后处理见 dispatch-protocol「派发编排机制」并行规则。

当 P2 声明多个 packages 且包间无数据依赖时，P4 可拆分并行，但**有额外约束**：

1. 每个 package 派一个 implementer subagent
2. **各 implementer 只改自己 package 目录下的文件**——跨包的共享文件（类型定义、接口、配置）由主 Agent 在所有并行 implementer 返回后统一处理
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit
5. 主 Agent 在所有 implementer 返回后，统一处理共享文件改动（如果有）

**冲突预防**：
- dispatch-context 约束节必须写明：`只改动 {pkg}/ 目录下的文件。共享文件（{列出}）不在本次改动范围内`
- 如果某个 implementer 必须改共享文件 → 该包不能并行，改为串行（主 Agent 先派其他包并行，再串行处理含共享改动的包）
- 无法确定是否有共享改动 → 串行（安全默认值）

**基础设施隔离（并行时强制）**：
- debug server 端口：每个 implementer 的 dispatch-context 约束节分配不同端口（如 pkg-a: 3001, pkg-b: 3002）
- 测试数据库：每个 implementer 用独立数据库路径（如 `test-{pkg}.db`），不共享同一 test.db
- 环境变量：dispatch-context 写明各 subagent 独立的环境变量值（如 `PORT=3001` vs `PORT=3002`）
- 临时文件：各 subagent 写入 `P4-implementation/{pkg}/` 独立目录

主 Agent 在并行派发前**必须**为每个 subagent 的 dispatch-context 分配上述隔离参数。当前无 gate 脚本检查（已知缺口），但未分配导致运行时冲突（端口占用/数据库锁）时计为重试，不算环境问题。

## gate 规则（check-gate.py 会跑）

```bash
check-gate.py P4 $TASK_DIR
```

- **exit 0**：暂存区含非 md/yaml 代码文件（git diff --cached --name-only）
- **exit 1**：暂存区仅 .md/.yaml 文件（无实际代码变更）→ 不能推进

## 推进条件（全部满足才写 phase: P5）

- [ ] 暂存区含代码文件（非 .md/.yaml）
- [ ] 按 C8 映射表触发的评审全部完成：P4-review.md status: approved（所有任务都要求——risk=high 的 P2 plan-eng-review 审方案，P4 实现评审按 domains 另行派发，不可省）
- [ ] SCOPE+ 已处理（若本阶段产生）：P1-requirements.md 有 [SCOPE_RESOLVED]（行首声明格式）
- [ ] git commit 完成

## 常见错误

1. **不读 files_to_read，在项目里乱翻**：implementer 拿到 P2 的 files_to_read 清单后应按清单阅读，不要在项目里全文搜索或整目录全读——上下文会爆炸
2. **自行加范围外改动**：发现需要做但不在 P1 范围内的改动 → 标 [SCOPE+]（行首声明格式）而非直接做
3. **只跑单元测试不验证集成**：单元测试全绿 ≠ 功能可用。P5 会跑 gate_commands 做技术验证，但要确保实现时路径依赖的端点行为已验证
4. **先更新 .state.yaml 再 commit**：state 和产出在同一 commit 里——不要先 commit 产出再单独 commit state
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P5 验证依赖：P5 跑 gate_commands.P5 的命令（在 P2 声明），确保你的实现能通过
- P6 验收依赖：实现路径的端点行为必须可验证（确认 API 返回正确的 Content-Type、状态码等）
- 代码改动文件路径：P8 发布时确认版本文件变更需要知道你改动了哪些 package

> 完成 → 读 phase-cards/P5-verification.md

6. **修改 P1 文档**：P4 发现 BDD 矛盾时标 DESIGN_GAP，不直接改 P1-requirements.md。需变更 P1 时标 `[BASELINE_CHANGE: 理由]` 并经主 Agent 批准。
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree 基线（881 pytest 全绿 + 28 条新测试红灯）已在 P3 commit 131e575 落盘。
- gate_commands.P3（自查用）：`python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v`
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
