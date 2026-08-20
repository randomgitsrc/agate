---
task_id: TAG0007
mechanism_issues:
  - "P8/READY 检查清单只要求'git tag 已创建'，未区分本地/远端，导致 tag 未随分支一起 push，PR 首轮 CI 因 CHECK 7（version badge 与 git tag 一致性）误判失败"
  - "check-gate.py gate_p4 的『## 新增文件核对表』用子串包含判定，在自指/dogfooding 场景（任务自己描述机制实现细节的文字里恰好出现该标题字符串）产生假阴性，WARNING 该触发未触发（DEBT0017）"
execution_issues:
  - "P4 commit（1e9d74e）触发 self-gate（改了 check-gate.py/多张 phase-cards）但提交时未先做 protocol-alignment-review，事后补做才发现 5 处真实文档传播缺口"
feedback_ready: true
---

# TAG0007 复盘 — agate 项目结构管理机制（RM-AG0008 骨架脚手架 + RM-AG0009 CODE-MAP 架构演进纪律）

## 一、事实基线

- 任务周期：2026-08-13 立项（P0）→ 2026-08-20 全流程完成合并（P1-P8 + READY），P0-P1 之间有跨会话间隔
- 走完整 P0-P8，无阶段裁剪（`phases: [P1..P8]`，`risk_level: high`）
- 阶段重试：P1 needs-revision 1 轮（同类扫描漏 1 处命中 + 边界维度遗漏并发场景 + BDD-4/7 关系未声明）；P2 rejected 1 轮（`gate_p7` pairing 字段对应关系写反，plan-eng-review 首轮打回）；P4/P5/P6/P7 均一次通过
- BDD：11 条（RM-AG0008 组 5 条 + RM-AG0009 组 6 条），P6 验收 11/11 PASS
- 测试：新增 17 个测试用例（12 个 `test_check_gate.py` + 3 个骨架模板 + 2 个 CODE-MAP 模板），全量回归 1011 → 1028 passed（0 新增失败）
- P4 实现按 `dispatch_plan` 拆 4 批并行（skeleton-docs/code-map-docs/gate-script-both/dogfood-bootstrap），无跨批文件冲突
- 登记 2 条新技术债：DEBT0016（CODE-MAP 路径解析简化推导，low）、DEBT0017（gate_p4 子串判定假阴性 + 自我应用缺口，low），均 open
- self-gate：P4 commit 事后补做审查，发现 5 处 MISALIGNED（均文档传播缺口，非逻辑错误），修复后复评全 ALIGNED
- PR #175：77 个文件改动，+8985/-10 行；CI 首轮因 tag 未推送导致 pytest（ubuntu+windows）失败，push tag 后复评全绿（跨平台 matrix 全过）
- 无 PROD_TOUCHED、无 SCOPE+ 实际触发、无遗留 NEED_CONFIRM

## 二、做得好的 + 可复用模式

- **主动核实 subagent 声称的"预存失败"**：P3 test-designer 曾把 2 个测试失败误判为"改动前已存在的基线失败"，主 Agent 用 `git stash` 隔离验证发现实际根因是本任务自己 P2-design.md 的 YAML 转义 bug（未转义 ASCII 双引号）。**去向：回馈 agate**——`git stash` 隔离验证法可作为"主 Agent 复核 subagent 归因结论"的标准动作，尤其当 subagent 把新问题误判为"预存"时，这类判断错误代价高（会掩盖真实回归）。
- **P2 review 迭代真正抓住了字段写反的实质错误**：plan-eng-review 首轮没有停留在"看起来实现了"，而是逐行核对 `check-gate.py` 现有 DESIGN_GAP pairing 源码，发现 CODE-MAP pairing 提案漏了内部一致性层且转抄核对层字段对应关系写反。复评时同一 reviewer 被要求"独立重新核实源码字段对应关系，不要被表面修复蒙混"，确实抓住了这条修复路径的正确性。**去向：回馈 agate**——`review.md`/`plan-eng-review.md` 里"逐行核对现有类似机制源码"这一检查方式对"复用既有 pairing/gate 模板"类任务价值很高，可考虑在角色文件里显式提示。
- **P7 一致性检查主动发现 gate 判定的自指假阴性**：主 Agent 在准备 P7 dispatch-context 时自己先做了一次独立验证（`grep` 实测 `gate_p4` 的字符串判定条件），发现 TAG0007 自己的 P4-implementation.md 触发了它自己新增的 WARNING 条件的 OR 前提（`agents/CODE-MAP.md` 已创建），但 WARNING 没有触发；把这个具体发现交给 consistency-reviewer 独立核实，最终确认为真实假阴性并合理处理（登记技术债而非打回已 approved 的 P4/P6）。**去向：回馈 agate**——"新增的 gate 检查在任务自己身上是否也应该触发"这条 self-referential 检查，值得写进 `consistency-reviewer.md` 或 `P7-consistency.md` 卡片作为通用检查提示（不止 CODE-MAP 这一次）。

## 三、发现的问题

- 问题：P8/READY 阶段创建了本地 git tag（`v0.56.0`），但未随 feature branch 一起 `git push`，导致 PR 首轮 CI 的 `pytest`（ubuntu + windows 两个 matrix）因 `check-protocol-consistency.py` CHECK 7（version badge 与 git tag 一致性）在远端看不到该 tag 而失败，需要事后补 `git push origin v0.56.0` + 重跑 CI
  归因层面: 机制缺口
  说明：`agate/phase-cards/P8-release.md`「READY 收尾检查」清单只写"[ ] git tag 已创建"，未显式区分"本地已创建"与"已推送到远端"，也未提及"PR 的 CI 是在远端 checkout 上跑，本地 tag 对远端 CI 不可见"这一因果关系。主 Agent 按字面完成了"创建 tag"这一项，但协议本身没有提示这一步需要额外 push。

- 问题：`check-gate.py` 的 `gate_p4` 新增的「## 新增文件核对表」判定用简单子串包含（`"## 新增文件核对表" not in text`），在自指/dogfooding 场景下（任务自己在描述"这个机制怎么实现"的说明性文字里，恰好逐字提到这个标题字符串）会被误判为"已满足"，导致 WARNING 该触发未触发；TAG0007 自己也没有为自己新增的文件（`skeleton-template.md`/`code-map-template.md`/`agate-workspace/agents/CODE-MAP.md`/3 个测试文件）打标准 CODE-MAP 标记
  归因层面: 机制缺口
  说明：设计阶段（P2）已经论证过"依赖方向偏离检测走人工判断，不做自动化静态依赖分析"（ADR-003 合规考量），但没有预见到"检测本身的字符串匹配判据"在自指场景下会失真——这是新增 gate 检查逻辑普遍会踩的坑（子串包含 vs 结构化/整行匹配），不是本任务独有，值得作为通用经验记录。

- 问题：P4 commit（`1e9d74e`）改了 `check-gate.py` 三处判定分支和多张 phase-cards，触发了 self-gate 触发面，但 commit 时未先做 `protocol-alignment-review`，commit-msg hook 只给出 WARNING（不阻断）就直接提交成功了；事后补做审查才发现 5 处真实的文档传播缺口（`task-files.md`/`scripts/README.md`/`state-machine.md`/两张 phase-cards 的 gate 规则小节均未同步新字段/新分支）
  归因层面: 执行错误
  说明：`SELF-GATE.md` 已明确"改 agate 协议/脚本准备 commit 时必须走本流程"，主 Agent 在派发 P4 实现批次时优先关注了功能正确性验证（测试是否变绿），漏了在 commit 前先派发 self-gate 审查这一步。协议本身有定义（`SELF-GATE.md` 检查清单第 2 条明确写"派发 protocol-alignment-review subagent"），是执行时没有遵守，不是协议缺失。好在 self-gate 补做成功且发现的问题都被修复，未造成实质损害。

## 四、改进措施

1. **`agate/phase-cards/P8-release.md`「READY 收尾检查」清单**：把"[ ] git tag 已创建"改为"[ ] git tag 已创建**并已推送到远端**（`git push origin {tag}`）——CI 在远端 checkout 上运行，本地 tag 对 CI 不可见，若涉及 PR 流程且 gate_commands.P5 包含 `check-protocol-consistency.py` 的 CHECK 7，务必先推送 tag 再触发/等待 CI"。可考虑登记为新 roadmap 条目（RM-AG00XX），由后续任务落地。
2. **`agate/scripts/check-gate.py` `gate_p4` 的「## 新增文件核对表」判定**：改用整行匹配（如 `re.search(r"^## 新增文件核对表\s*$", text, re.MULTILINE)`）替代子串包含，消除自指场景假阴性——已登记 `DEBT0017`，closure_criteria 已包含此项。
3. **`agate/assets/execution-roles/consistency-reviewer.md` 或 `phase-cards/P7-consistency.md`**：补充一条通用检查提示——"若本次改动新增了 gate/WARNING 检测逻辑，应额外核查该检测逻辑对本任务自身产出是否也正确触发（self-referential 检查），不止关注检测对象是否符合语义"。
4. **实践纪律层面**（不改协议，仅提醒自己）：派发 P4 实现类批次前，主 Agent 应在 dispatch 清单里显式包含"完成后是否需要 self-gate-review"这一判断，而不是等 commit-msg hook WARNING 提醒后才想起。

## 技术债登记核对清单

| 机制 | 应该触发？ | 实际触发？ | 未触发后果 | 原因 |
|------|-----------|-----------|-----------|------|
| retry 记录 | 是 | ✅ | — | P1/P2 各 1 次 retry，均已记入 `.state.yaml` `retries` 字段 |
| PAUSED | 否 | — | — | 无 retry 超限/跨阶段回退/不可逆操作确认场景 |
| PROD_TOUCHED | 否 | — | — | 全程 `[PROD_NOT_TOUCHED]`，纯协议脚本/文档改动 |
| SCOPE+ | 否 | — | — | 全仓 grep 核实无实际 `[SCOPE+]` 声明 |
| SCOPE_RESOLVED | 否 | — | — | 无 SCOPE+ 需要闭环 |
| DESIGN_GAP | 是 | ✅ | — | P4 gate-script-both 批次标注 2 条，均转抄至 P7 |
| DESIGN_GAP_REVIEWED | 是 | ✅ | — | P7 逐条转抄 + REVIEWED 配对，check-gate.py P7 校验通过 |
| NEED_CONFIRM | 否 | — | — | 全程 `[NO_NEED_CONFIRM]` |
| CAPABILITY_GAP | 否 | — | — | P1 声明 `capability_requirements: []`，无特殊能力需求 |
| gate 验证（每阶段） | 是 | ✅ | — | P1-P8/READY 每阶段均预跑 check-gate.py |
| 阶段产出文件（每阶段） | 是 | ✅ | — | 全部阶段产出齐全 |
| .state.yaml phase 同步 | 是 | ✅ | — | 每次 commit 前同步更新，与产出同一 commit |
| 裁剪条件 + override | 否 | — | — | 无阶段裁剪（`phases: [P1..P8]`） |
| capability_requirements | 是 | ✅ | — | P1 声明 `[]` 并给出理由 |
| 分阶段落盘（防 subagent 空返回） | 是 | ✅ | — | 每次派发均要求 progress.md 追加，无空返回事故 |
| phase-产出一致性 | 是 | ✅ | — | 每次 commit 的 phase 字段与产出一致 |
| P6 evidence（含截图 + 引用 + vision YAML） | 是 | ✅ | — | 非 UI 任务，evidence 为 test-output.log + 内容核对文件，均被 PASS 行引用 |
| P2 候选方案 + 权衡（≥2） | 是 | ✅ | — | 4 决策组各 2 候选方案 |
| P8 internal_only_reason | 否 | — | — | 未裁剪 P8 |
| dispatch-context.md | 是 | ✅ | — | 每次派发均先写 dispatch-context，含客观查证信息 |
| pre-commit hook（gate / 状态转移 / 裁剪） | 是 | ✅ | — | 每次 commit 均触发 hook，无 --no-verify 绕过 |
| CI backstop | 是 | ✅ | — | PR CI 首轮因 tag 未推送失败，push tag 后复评全绿，backstop 机制本身正常工作（见「发现的问题」第一条） |
| **技术债登记** | 是 | ✅ | — | DEBT0016（P4 阶段登记）+ DEBT0017（P7 阶段登记），均含 evidence/impact/recommendation/closure_criteria |

## agate 反馈

> `feedback_ready: true`，以下条目归因到 agate 机制/执行层面，值得反馈给 agate 项目组：

1. **机制缺口**：P8/READY 检查清单"git tag 已创建"未区分本地/远端，PR 流程下会导致 CI 首轮误判失败（远端看不到本地 tag，CHECK 7 版本一致性检查失败）。建议清单措辞补充"并已推送到远端"+ 因果关系说明。
2. **机制缺口**：新增 gate/WARNING 检测逻辑时，容易忽略"该检测逻辑对本任务自身产出是否也应该正确触发"这一自指/dogfooding 场景的假阴性风险（本次是子串包含判定被自己的说明性文字误伤）。建议在 consistency-reviewer 角色文件或 P7 卡片补一条通用检查提示。
3. **执行错误（非机制缺口，但值得记录作为案例）**：P4 commit 忘记先做 self-gate-review，事后补做发现 5 处真实文档传播缺口——说明 self-gate 机制本身有效（补做审查确实抓到了真问题），但"事前"比"事后补救"成本更低，值得作为反面案例提醒后续任务养成"commit 前先做"的习惯。
