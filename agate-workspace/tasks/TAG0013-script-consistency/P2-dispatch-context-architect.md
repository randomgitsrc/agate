---
phase: P2
generated_by: 主 Agent
task_id: TAG0013-script-consistency
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。执行优先级：派发指引 > 客观查证信息 > 阶段卡片。
> 你是 TAG0013（agate 脚本一致性批）的 P2 方案架构师。**只产出 P2-design.md，不修改代码/测试。**

### 目标

产出 P2-design.md（方案设计），覆盖三条子需求的实现方案：
1. **RM-AG0015**：`check-protocol-consistency.py` 新增 CHECK 10（协议文档面脚本名引用漂移 gate）+ phase-cards/rules 纳入 PROTOCOL 严格检查。
2. **RM-AG0017**：`commit-msg-self-gate.py` 的 `_SELF_GATE_RE` 扩展匹配 README.md / AGENTS.md（CHANGELOG 豁免）。
3. **RM-AG0018 剩余**：`check-retrospective.py` 输出加"复盘发现的新缺口请登记 DEBT/roadmap"提醒行。

### 约束

- 只产出 P2-design.md；不修改代码/测试/需求文件；不 commit
- **范围锁定**：P1-requirements.md 的 11 条 BDD 是验收基线，方案必须能全部覆盖；不扩范围
- **CHECK 10 设计要点（P1 已锁定，直接采用）**：
  - 扫描范围 = 协议文档面（PROTOCOL_FILES + PROTOCOL_DIRS + phase-cards/rules + README/AGENTS + agate/AGENTS.md + UPGRADING + scripts/README.md + CHANGELOG 叙事降级；不含 docs/ 与 agate-workspace/）
  - 豁免 5 类：① UPGRADING.md 整文件 ② formatters 名（assets/formatters/ 下）③ 3 hook 薄壳 ④ count-tests.sh ⑤ scripts/README.md 退役名 3 个
  - 叙事文件（NARRATIVE_DIRS 覆盖集）至多 WARNING
  - 增量性：当前协议文档面 0 漂移（378 处引用），落地后不能产生新的 ERROR
  - SUGGEST 已采纳：CHECK 10 留在 check-protocol-consistency.py 内作为第 10 个 CHECK 函数（与现有 CHECK 1-9 同构，改动最小）——若你认为拆独立脚本更好，给出权衡后推翻，但需明确理由
- **phase-cards/rules 入 PROTOCOL_DIRS**：`check_internal_refs`（CHECK 2）/`check_line_refs`（CHECK 3）会对它们按协议文件严格检查——P1 已实测无 `.md L\d+` 引用、`scripts/` 前缀引用均存在，不新增 ERROR。设计中需把 PROTOCOL_DIRS 从 `("agate/assets/",)` 扩展为含 `agate/phase-cards/`、`agate/rules/`
- **NARRATIVE_DIRS 重组评估（RM-AG0015 修复方向 4）**：P0-brief 提到"按文件性质分严格/宽松（debt/进行中 task 应严格）"——P1 影响面分析后评估：CHECK 10 对叙事文件至多 WARNING 是否已足够覆盖（debt/进行中 task 的漂移是未来新增引用，由 CHECK 10 的 ERROR 级对协议面兜底）。**若实现复杂度高（需读 .state.yaml 区分进行中/已完成），P2 评估后可在设计中声明本任务不做、保持现状**（记入 design 决策，不扩范围）
- **`_SELF_GATE_RE` 扩展**：P1 建议用 `^(README\.md|AGENTS\.md|...)` 锚定根级精确名（CHANGELOG 天然不在其列，无需额外逻辑）；若用宽松 glob 则需显式排除 CHANGELOG。architect 定方案
- **check-retrospective.py**：提醒行只能在 warnings 存在时输出（不违反 RT.1 空输出约束），含 "DEBT" 与 "roadmap" 两词，exit 0 不变
- 平台无关：纯 Python + 文件系统改动，不引入 Unix 假设
- 自查≠gate：不声称"P2 已过"

### 上游关联

- P1-requirements.md：11 条 BDD（BDD-1..11），approved（P1-review.md status: approved）
- 影响面表：协议文档面 378 处引用（58 phase-cards/rules + 104 协议 md + 22 README/AGENTS + 86 UPGRADING + 61 scripts/README + 47 assets/**）；含 CHANGELOG 595
- 当前 0 漂移（增量性前提）

### 输入文件

1. `{AGATE_WORKSPACE}/tasks/TAG0013-script-consistency/P1-requirements.md`（需求基线 + 11 BDD + 影响面表）
2. `{AGATE_WORKSPACE}/tasks/TAG0013-script-consistency/P1-review.md`（评审 approved + §4 非阻塞观察 2 点建议 P2 处理）
3. `{AGATE_WORKSPACE}/tasks/TAG0013-script-consistency/P0-brief.md`（环境约束 + known_risks）
4. 角色定义：`agate/assets/execution-roles/architect.md`
5. 被测脚本（worktree 内，方案对象）：
   - `agate/scripts/check-protocol-consistency.py`（重点：L52-65 PROTOCOL_FILES/PROTOCOL_DIRS、L74 NARRATIVE_DIRS、L238 REF_RE、L766-790 CHECKS 列表 + run_all_checks）
   - `agate/scripts/commit-msg-self-gate.py`（重点：L38-40 _SELF_GATE_RE）
   - `agate/scripts/check-retrospective.py`（重点：main() warnings 输出块）
6. 现有测试（评估改动影响）：
   - `agate/tests/unit/test_check_protocol_consistency.py`
   - `agate/tests/unit/test_commit_msg_self_gate.py`
   - `agate/tests/unit/test_check_retrospective.py`
7. 参照：`agate/tests/conftest.py`（fixture：git_repo / task_dir / run_cli 等）

### 客观查证信息（已核实，供设计直接采用）

- `check-protocol-consistency.py`：
  - L52-64 `PROTOCOL_FILES`：11 文件 set
  - L65 `PROTOCOL_DIRS = ("agate/assets/",)`
  - L74 `NARRATIVE_DIRS = ("docs/plans/", "docs/reviews/", "docs/design-notes/", "docs/tasks/", "archived/", "agate-workspace/tasks/", "CHANGELOG.md")`
  - L77-90 `PATH_IGNORE_SUBSTRINGS`：含 "..." / "xxx" / "{" / "agate-workspace/" / "docs/agents/" 等
  - L238 `REF_RE = re.compile(r"(?<![\w/])((?:docs|assets|scripts)/[A-Za-z0-9_./\-]+\.(?:md|sh|ya?ml|py))")`
  - L240 `check_internal_refs()`：`iter_md_files(root)` 遍历 + `is_narrative_file(relpath)` 降级 + `PATH_IGNORE_SUBSTRINGS` 过滤 + `root/agate/ref` 兼容查找
  - L766-770 `CHECKS` 列表（1,2,3,4,6,7,8,9）+ `run_all_checks()` 对 CHECK 9 拆分正向/反向
  - `iter_md_files` / `rel` / `is_narrative_file` 工具函数存在（供复用）
- `commit-msg-self-gate.py`：L38-40 `_SELF_GATE_RE = re.compile(r"^(agate/scripts/.*\.(sh|py)|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$")`；L53 run_git diff --cached --name-only；L57 match
- `check-retrospective.py`：main() 收集 3 类 warnings，`if warnings:` 才写 stderr；L95 sys.exit(0)
- 测试：test_commit_msg_self_gate.py 恰好 4 用例（test_cmsg_1..4）；test_check_retrospective.py 有 RT.1 空输出断言

### 产出要求（P2 卡 §产出规格）

**frontmatter 必填**：candidate_count / packages / domains / ui_affected（false）

**正文必须包含**：
1. **候选方案 ≥2 + 权衡 + 选择理由**（每处改动一个方案节：CHECK 10 实现方式 / _SELF_GATE_RE 扩展模式 / 提醒行位置）
2. **四字段**：packages / domains / ui_affected / gate_commands（P3/P5 命令）
3. **files_to_read**：P4 implementer 需要参考的文件清单（控制上下文，只列确实需要的）
4. **env_constraints**：确认/细化 P0-brief 环境约束
5. **minimal_validation**：纯代码逻辑 → 声明 `纯代码逻辑，无外部系统依赖`（写明依赖了哪些内部函数/数据转换）或给出最小验证结果
6. **评审非阻塞观察处理**：P1-review.md §4 注 1（my-runner.sh 措辞）、注 2（PROTOCOL_FILES 11 笔误）——P2 顺手修正（改 P1-requirements.md 需主 Agent 批准；若仅设计文档内措辞则直接处理）
7. **design 决策记录**：NARRATIVE_DIRS 是否重组（debt/进行中 task 严格）的评估结论

### 返回给我

- P2-design.md 路径
- 候选方案数 + 选择摘要
- 任何评审非阻塞观察处理情况
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P2

路径：phase-cards/P2-design.md
---
# P2 — 方案设计

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → P2 不可裁剪。design_trivial / follows_existing_pattern 可简化（1 个候选方案），不可省略。

## 如果是首次进入本阶段

1. 派发 architect subagent → 产出 P2-design.md
   1.1 写 P2-dispatch-context-architect.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 C8 映射表派评审（见下方）
3. 评审通过 → P2-review.md status: approved
4. 预跑 check-gate.py P2（脚本化检查）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P2，不要提前写 P3——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P2): {摘要}"（phase=P2，P2 产出含 P2-design.md + P2-review.md）
7. P2 commit 完成后进入 P3：**phase 推进 P3 随 P3 产出 commit 一起**（P3-test-cases.md 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（方案选择有误 / 候选方案不足 / 评审 rejected）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P2 MAX=3）

## 前置条件

- [ ] P1-requirements.md 含 domains / risk_level / phases 声明
- [ ] P0-brief.md env_constraints 可查阅

## 派发

- **角色**：architect（`{agate_root}/assets/execution-roles/architect.md`）
- **输入**：P1-requirements.md + P0-brief.md
- **输出**：P2-design.md
- **派发 prompt 追加**：

```
## P2 最小验证
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。
- 方案依赖浏览器行为/安全模型/外部系统行为 → 必须做最小验证
- 纯代码逻辑 → 须在 minimal_validation 字段声明 `纯代码逻辑，无外部系统依赖`（须写明依赖了哪些内部函数/数据转换）
```

## 产出规格

P2-design.md 必须包含：
- **候选方案 ≥2** + 权衡 + 选择理由（design_trivial / follows_existing_pattern 时可只写 1 个，见下方）
- **`candidate_count: N` 必填**：本方案候选方案数（≥2，design_trivial/follows_existing_pattern 时可 1），gate 按此字段校验，不再解析标题。你写几个候选就填几个，与正文一致。
- **四字段**：`packages:` `domains:` `ui_affected:` `gate_commands:`
- **files_to_read**：实现时需要参考的文件清单（控制 P4 implementer 上下文）
- **env_constraints**：确认/细化 P0-brief 的环境约束
- **minimal_validation**：验证结果 或 声明"纯代码逻辑，无外部系统依赖"（声明时须附理由）

`candidate_count`/`packages`/`domains`/`ui_affected` 写在文件头 **frontmatter**（`---` 分隔块），
不写正文；`gate_commands:`/`files_to_read:`/`env_constraints:`/`minimal_validation:` 留正文。
**可直接复制的完整样例**：
```yaml
---
phase: P2
task_id: TAG0001           # 替换为实际任务编号
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260101 # {task_id}-P2-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2                # int ≥1，必填
packages: [pkg-a]                 # list，必填
domains: [backend, cli]           # list，必填
ui_affected: false                # bool，必填
---
```

候选方案简化（须附理由，无理由视为无效声明，要求 ≥2 候选方案）：
- `design_trivial: true` + 理由（为什么 trivial）→ 可只写 1 个候选方案（P2 仍不可省略）
- `follows_existing_pattern: [src/foo.py]`（列出参照文件路径）→ 可只写 1 个候选方案，参照已有模式（P2 仍不可省略）

## gate_commands 声明

gate_commands 在 P2 固化，后续阶段按此执行：

```yaml
gate_commands:
  P3: "pytest"                  # 可选：测试运行器（verbose 输出，供 check-tdd-red.py 自动读取）
  P5: "pytest -q --tb=no"       # 紧凑输出模式
  P5_e2e: "playwright test --reporter=line tests/e2e/"  # ui_affected: true 时必填
```

## 评审派发（C8 机械映射）

按 P1 声明的 domains + risk_level 机械映射评审：

| domain | risk_level | 必须派的评审 |
|--------|------------|------------|
| backend | 任意 | plan-eng-review（P2 方案评审） |
| frontend | 任意 | plan-design-review |
| 任意 | high | plan-eng-review（硬规则，必须派独立 subagent） |
| P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向 | 任意 | plan-ceo-review |

> **去重说明**：同一任务命中多行且触发同一评审角色时，去重只派发一次（如 backend + high 均命中 plan-eng-review，只派 1 个 plan-eng-review，不重复派发）。

多个评审角色 `专家组并行` → 组长汇总 → P2-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件（示例非穷举，按 C8 映射表触发）：
   - plan-eng-review → P2-review-eng.md
   - plan-design-review → P2-review-design.md
   - plan-ceo-review → P2-review-ceo.md
   - cso → P2-review-cso.md
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长输入：所有评审文件路径
5. 组长产出：P2-review.md（统一 status: approved / rejected）。**组长 subagent 产出的 P2-review.md 的 Header agent 字段必须是组长角色名（非 main）——check-gate.py P2 硬拦截 agent=main 的 approved**
6. 组长规则：
   - 不发表新意见，只汇总
   - 任何专家标 BLOCKER → status: rejected
   - 多位专家分歧 → 标「专家组分歧」交人工
   - 全票无 BLOCKER → status: approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P2-review.md。

review 不通过 → architect 修改方案 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

**UI 测试选择器**：涉及前端时，P2 design 建议声明 UI 组件的稳定测试标识清单（如 `data-testid`，而非 class 命名）。P3 test-designer 用稳定标识定位元素，P4 implementer 按清单实现--class 命名可重构，稳定标识不变。具体方案由 P2 architect 决定。

## gate 规则

```bash
check-gate.py P2 $TASK_DIR
```

- 候选方案数 ≥2（design_trivial / follows_existing_pattern 时可只写 1 个）
- P2-review.md 存在且 status: approved（agent≠main）— 不存在 → gate exit 1
- 四字段齐全（packages/domains/ui_affected/gate_commands）
- gate_commands.P3 可选（非 pytest 项目建议声明，供 check-tdd-red.py 自动读取测试运行器）
- 候选方案 ≥2 时含权衡/选择理由

## 推进条件（全部满足才写 phase: P3）

- [ ] P2-design.md 候选方案 ≥2（或 design_trivial/follows_existing_pattern 须附理由时可只写 1 个）+ 四字段齐全
- [ ] P2-review.md 存在且 status: approved（agent≠main）
- [ ] gate_commands.P5_e2e 已声明（ui_affected: true 时）

## 常见错误

1. **忘了最小验证**：方案依赖外部系统行为（API MIME 类型、浏览器 CSP 等）但直接假设前提成立 → 到 P6 才发现不可行。跑一个 curl / 10 行 HTML 就能 5 分钟发现
2. **gate_commands.P5 只列单元测试**：UI 任务时缺少 P5_e2e → P5 不会跑端到端验证
3. **files_to_read 列太多文件**：把所有相关文件都列上 → P4 implementer 上下文爆炸。只列确实需要参考的
4. **忘了派评审**：按 C8 映射机械执行，不靠"觉得不需要"
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P4 依赖 files_to_read 导航代码阅读范围
- P5 依赖 gate_commands 执行验证命令
- P6 依赖 ui_affected 判断是否需要 vision-helper
- gate_commands 在 P2 固化后 P4-P6 不能改——设计阶段是声明验证契约的唯一窗口

> 完成 → 读 phase-cards/P3-tdd.md
<!-- AGATE_CARD_END -->
