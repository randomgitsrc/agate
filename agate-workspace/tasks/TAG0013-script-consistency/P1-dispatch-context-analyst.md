---
phase: P1
generated_by: 主 Agent
task_id: TAG0013-script-consistency
role: analyst
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令。执行优先级：派发指引 > 客观查证信息 > 阶段卡片。
> 你是 TAG0013（agate 脚本一致性批）的 P1 需求分析师。**只产出 P1-requirements.md，不修改代码/测试。**

### 目标

产出 P1-requirements.md（需求基线），覆盖三条子需求：
1. **RM-AG0015**：新增 CHECK 10——协议文档脚本名引用漂移 gate（扫描协议文件对 `agate/scripts/` 脚本名的引用，对照实际存在的脚本文件，找出"文档引用了不存在的脚本"的漂移）。
2. **RM-AG0017**：self-gate 触发面扩展——`commit-msg-self-gate.py` 的 `_SELF_GATE_RE` 补上仓库根级 `README.md` / `AGENTS.md`（CHANGELOG 豁免）。
3. **RM-AG0018 剩余**：`check-retrospective.py` 输出加一行"复盘发现的新缺口请登记 DEBT/roadmap"提醒（纯提醒不拦截）。

### 约束

- 只产出 P1-requirements.md；不修改代码/测试/其他文档；不 commit
- **P0-brief known_risks 强制要求**：P1 必须全仓 grep 脚本名引用（裸名 + 相对路径）建影响面表；grep self-gate 触发面相关测试。用户明确：不愿意一轮一轮来回改——影响面要在 P1 一次摸清
- **CHECK 10 必须是增量检查**：只报新漂移，不误伤现有合法引用。豁免清单已锁定：UPGRADING 对照表 / formatters / 3 个 hook 薄壳（pre-commit-gate.sh、commit-msg-self-gate.sh、pre-push-gate.sh）/ count-tests.sh——豁免设计要精确，P1 先画"哪些文档引用哪些脚本名"影响面表
- **不破坏已有协议语义**：Linux 现状 749 pytest 全绿是回归底线；consistency 0 ERROR 基线已锁定（2026-08-15）
- 范围锁定：P0-brief 三条 issue（RM-0015/0017/0018）是全部范围。若分析发现需要超出此范围，标 `[NEED_CONFIRM]` 停下交主 Agent
- 自查≠gate：不声称"P1 已过"

### 上游关联

- P0-brief.md 已锁定三条 issue + known_risks（全有代码证据）
- DEBT0001 已登记（source: retrospective，关联 RM-AG0015）
- 复盘原文称"SELF-GATE.md 不在触发面"是错误——实测 `_SELF_GATE_RE` 包含它，只补 README/AGENTS

### 输入文件

1. `{AGATE_WORKSPACE}/tasks/TAG0013-script-consistency/P0-brief.md`（主 Agent 任务简报与风险声明——P1 主要输入）
2. 角色定义：`agate/assets/execution-roles/analyst.md`（派发 prompt 已注入 P1 阶段卡片，冲突以派发指引为准）
3. 被测脚本（worktree 内，客观查证信息已给关键行号，需自行精读）：
   - `agate/scripts/check-protocol-consistency.py`（CHECK 10 新增对象 + PROTOCOL_FILES/NARRATIVE_DIRS/REF_RE 改造对象）
   - `agate/scripts/commit-msg-self-gate.py`（_SELF_GATE_RE 扩展对象）
   - `agate/scripts/check-retrospective.py`（提醒行添加对象）
4. 现有测试（评估改动影响 + self-gate 触发面测试现状）：
   - `agate/tests/unit/test_check_protocol_consistency.py`
   - `agate/tests/unit/test_commit_msg_self_gate.py`
   - `agate/tests/unit/test_check_retrospective.py`
5. 协议文档（影响面扫描对象）：`agate/phase-cards/`、`agate/rules/`、`agate/WORKFLOW.md`、`agate/dispatch-protocol.md`、`agate/git-integration.md`、`agate/UPGRADING.md`、`agate/SETUP.md`、`README.md`、`AGENTS.md`、`agate/AGENTS.md`
6. 项目约定：`AGENTS.md`（worktree 根）

### 客观查证信息（已核实，2026-08-15）

- **check-protocol-consistency.py 现状**：
  - L52-64 `PROTOCOL_FILES`（set）：含 `agate/WORKFLOW.md`、`agate/dispatch-protocol.md`、`agate/state-machine.md`、`agate/role-system.md`、`agate/loop-orchestration.md`、`agate/git-integration.md`、`agate/platform-notes.md`、`agate/LIMITATIONS.md`、`README.md`、`agate/orchestrator-template.md`、`agate/SETUP.md`——**不含 `agate/phase-cards/`、`agate/rules/`**（必读卡引用检查降级 WARNING 的根因）
  - L65 `PROTOCOL_DIRS = ("agate/assets/",)`——phase-cards/rules 未列入
  - L74 `NARRATIVE_DIRS = ("docs/plans/", "docs/reviews/", "docs/design-notes/", "docs/tasks/", "archived/", "agate-workspace/tasks/", "CHANGELOG.md")`——按目录粗分，未按文件性质分（2026-08-15 数据：archived 62.7% 漂移 / 已完成 task 42.7% 是历史常态；debt/进行中 task 应严格）
  - L238 `REF_RE = re.compile(r"(?<![\w/])((?:docs|assets|scripts)/[A-Za-z0-9_./\-]+\.(?:md|sh|ya?ml|py))")`——**只匹配 docs/assets/scripts 前缀引用**，裸脚本名（phase-cards/rules 全是，如 `check-tdd-red.py`）完全漏检
  - CHECK 编号现状：1,2,3,4,6,7,8,9（CHECK 5 已删除）→ 新检查应编号 **CHECK 10**
  - `check_internal_refs()`（CHECK 2）逻辑：`for m in REF_RE.finditer(line)` + `PATH_IGNORE_SUBSTRINGS` 过滤 + 叙事文件死链降级 WARNING + 协议文件 ERROR
  - CHECK 9 已有锚点表机制（`SCRIPT_ALIGNMENT_ANCHORS` + `check_anchor_coverage()` 反向兜底）——新增 CHECK 10 若含脚本，需评估是否纳入锚点
- **commit-msg-self-gate.py 现状**：L38-40 `_SELF_GATE_RE = re.compile(r"^(agate/scripts/.*\.(sh|py)|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$")`——**不含 README.md/AGENTS.md**
- **check-retrospective.py 现状**：main() 收集 retries_over / SCOPE+ / override 三类 warnings，stderr 输出 `GATE RETRO: 建议复盘...`，exit 0 不拦截——提醒行加在这里
- **脚本目录**：`agate/scripts/` 下 check-*.py / agate-*.py / 3 个 .sh 薄壳（pre-commit-gate.sh、commit-msg-self-gate.sh、pre-push-gate.sh）
- **phase-cards 脚本名引用密度**：`grep -rn "check-*.\(sh\|py\)\|agate-*.\(sh\|py\)" agate/phase-cards/` ≈ 32 处（全部是裸名引用，REF_RE 现行正则匹配不上——待 P1 影响面表精确化）

### 产出要求（P1 卡 §产出规格）

**frontmatter 必填**：risk_level / phases / packages / domains

**正文必须包含**（结合 P0-brief known_risks 强制项）：
1. **需求复述**：三条子需求各自"现状 → 缺陷 → 期望行为"
2. **影响面表（强制）**：全仓 grep 脚本名引用（裸名 + 相对路径），列出"哪些文档引用哪些脚本名"，标注是否在豁免清单（UPGRADING 对照表/formatters/3 hook 薄壳/count-tests.sh）——这是 CHECK 10 豁免设计的输入
3. **self-gate 触发面现状表**：grep 现有 self-gate 测试（test_commit_msg_self_gate.py），确认 README/AGENTS 加入后需要补哪些测试
4. **BDD 验收条件**（≥1 条，Given/When/Then，二值可判）：建议覆盖 CHECK 10 增量性（合法引用不误报 + 漂移引用必报）、phase-cards/rules 入 PROTOCOL 严格检查、README/AGENTS 触发 self-gate、CHANGELOG 豁免、check-retrospective 提醒行
5. **裁剪说明**：phases 列表 + 跳过阶段理由
6. **capability_requirements**（三态）+ **NEED_CONFIRM 处理**（无待确认写 `[NO_NEED_CONFIRM]`）

### 返回给我

- P1-requirements.md 路径
- BDD 条数
- 影响面表摘要（几类引用、几处豁免）
- 任何 `[NEED_CONFIRM]` 项（如有）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P1

路径：phase-cards/P1-requirements.md
---
# P1 — 需求基线

> 当前状态：[首次 / 重试 #N]
> P1 不可裁剪（核心阶段）

## 如果是首次进入本阶段

1. 派发 analyst subagent → 产出 P1-requirements.md
   1.1 写 P1-dispatch-context-analyst.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 主 Agent 确认：BDD 验收条件 ≥1 条 + 无未决 NEED_CONFIRM
2.5 派发 requirements-review subagent（角色文件：{agate_root}/assets/review-roles/requirements-review.md）
     2.5.1 写 P1-dispatch-context-requirements-review.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
    输入：P1-requirements.md
    产出：P1-review.md（agent≠main，含 BDD 编号引用 + 覆盖维度标注）
    review 不通过 → analyst 修改 → 再 review → … → approved（⑩迭代循环）
3. 预跑 check-gate.py P1（exit 2，主 Agent 自判）
4. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P1，不要提前写 P2——phase = 本 commit 的产出阶段
5. git commit -m "wf({Txxx}-P1): {摘要}"（phase=P1，P1 产出含 P1-requirements.md + P1-review.md）
6. P1 commit 完成后进入 P2：**phase 推进 P2 随 P2 产出 commit 一起**（P2-design.md + P2-review.md 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（BDD 不完整 / domains 声明错 / NEED_CONFIRM 未处理）
→ review 不通过时：analyst 修改需求 → 重派 requirements-review → 共享 retry 预算
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P1 MAX=3）

## 前置条件

- [ ] P0-brief.md 完成（四字段齐全）

## 派发

- **角色**：analyst（`{agate_root}/assets/execution-roles/analyst.md`）
- **输入**：P0-brief.md（env_constraints / known_risks / executor_env）
- **输出**：P1-requirements.md
- **派发 prompt 模板**：`{agate_root}/assets/templates/dispatch-prompt.md`

## 产出规格

P1-requirements.md 必须包含：
- BDD 验收条件（至少 1 条，Given/When/Then 格式）
- `domains:` 声明（backend / frontend / mcp / security）
- `packages:` 声明（受影响的包/模块）
- `risk_level:` 声明（low / medium / high）→ 决定 P2 评审强度
- `phases:` 裁剪声明（跳过哪些阶段 + 理由）
- `capability_requirements:` 能力需求声明（available / supplementable / GAP 三态）
- 无未决 `[NEED_CONFIRM]`（有则 PAUSED）；无待确认项时写 `[NO_NEED_CONFIRM]`

`risk_level`/`phases`/`packages`/`domains` 写在文件头 **frontmatter**（`---` 分隔块），不写正文。
**可直接复制的完整样例**：
```yaml
---
phase: P1
task_id: TAG0001           # 替换为实际任务编号
type: problems
parent: P0-brief.md
trace_id: T001-P1-20260101 # {task_id}-P1-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: analyst
# ── v2.0 机器字段 ──
risk_level: low             # low / medium / high，必填
phases: [P1, P4, P5, P6, P8]   # list of P\d+，必填
packages: [pkg-a]           # list，必填
domains: [backend, frontend]  # list，必填
# 可选字段：override / implicit_coupling / coupling_checklist / internal_only /
# internal_only_reason / 跳过风险 / design_trivial / follows_existing_pattern
# ── v2.0 refactor 任务类型声明（可选，缺省 = 功能任务）──
# change_type: refactor   # 当前仅支持 refactor；枚举非法值由 frontmatter schema 拦截
# ── v2.0 标记"已解决/已确认"状态（可选，仅标记存在时写）──
# need_confirm_resolved: []   # list[str]：已解决的 NEED_CONFIRM 项描述（逐条匹配正文）
# suggest_resolved: []        # list[str]：已采纳的 SUGGEST 项描述
# scope_resolved: []          # list[str]：已解决的 SCOPE+ 项描述
---
```

**NEED_CONFIRM 分级**：
- `[SUGGEST: 推荐 X，理由 Y]` - 有倾向但求确认。主 Agent 可自行采纳倾向（除非涉及破坏性变更/业务方向），不必问用户
- `[NEED_CONFIRM]` - 真无方向需人定夺。阻塞推进，主 Agent 问用户

## gate 规则

check-gate.py P1 → P1-review.md 存在 + status:approved + agent≠main + 含 BDD 编号锚点 → exit 2（BDD 编号格式为 `#### BDD-NN:`）；缺 P1-review.md / agent=main / 无锚点 → exit 1
P1 评审不可裁——所有任务都走独立 requirements-review，无例外

## 推进条件（全部满足才写 phase: P2）

- [ ] P1-requirements.md 含 BDD ≥1 条
- [ ] domains / packages / risk_level / phases 已声明
- [ ] 无 [NEED_CONFIRM] 标记
- [ ] 无 status: GAP（supplementable 不阻，GAP 阻）
- [ ] P1-review.md status: approved（agent≠main，含 BDD 编号锚点）

## 常见错误

1. **BDD 写成技术实现而非用户行为**：BDD 应该描述"用户能看到什么/系统应该做什么"，不是"调用哪个 API"
2. **domains 声明不全**：漏了某个受影响域 → P2 不派该域的评审 → 实现方向错误
3. **capability_requirements 漏声明**：P6 验收时才发现需要但不可用的能力 → 返工
4. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P2 设计依赖 domains + risk_level 决定评审角色
- P6 验收逐条对照 P1 的 BDD（PASS/FAIL 总数必须 ≥ P1 BDD 总数）
- P7 一致性检查依赖 packages 声明做跨文件交叉核对

## 评审

P1 评审通用必有（所有任务都走 requirements-review），P2/P4 评审是 C8 域触发（见 review-mapping.md）——二者在"是否通用"上不对称，仅在"独立 subagent、agent≠main"上类比。P1 评审不可裁剪。
review 不通过 → analyst 修改需求 → 再 review（⑩迭代循环），直至 approved。

> 完成 → 读 phase-cards/P2-design.md


## P1 基线保护

P1-requirements.md 是需求基线，后续阶段（P2-P8）不应直接修改。如需变更（如 P4 发现 BDD 矛盾需补充注释），必须：
1. 主 Agent 显式批准
2. 在变更处标注 `[BASELINE_CHANGE: 理由]`
3. 不改 BDD 的 Given/When/Then 语义（只补充注释/优先级说明）
<!-- AGATE_CARD_END -->

