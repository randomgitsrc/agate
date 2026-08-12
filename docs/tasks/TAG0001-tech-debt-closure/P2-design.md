---
phase: P2
task_id: TAG0001-tech-debt-closure
type: design
parent: P1-requirements.md
trace_id: TAG0001-P2-20260812
status: draft
created: 2026-08-12
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 4                # 4 个决策点各 2 候选，正文 §1 D1-D4
packages: [agate]                 # 协议本体单一包（改 worktree 的 agate/）
domains: [backend, cli]           # backend=校验器/回退比对/check-gate.sh P8；cli=卡片/规则/工作区初始化
ui_affected: false                # 无 UI 面（P1 已确认）
---

# TAG0001 — agate 技术债登记闭环（Phase 1-3）+ tech-debt 归类修正：P2 方案设计

> 输入：P1-requirements.md（20 条 BDD）+ P1-review.md（4 条非阻塞观察 N1-N4）+ P0-brief.md（env_constraints / known_risks）+ docs/reviews/review-20260812-1204.md（任务内容来源，Phase 1-3 设计）+ docs/reviews/T001-retrospective-2026-08-10.md（回填 source）+ worktree `agate/` 现状代码（本设计前的读代码查证）。
> 角色：architect。
> 目标：把 20 条 BDD 转化为可实现的方案 + 实现导航；gate_commands 在 P2 固化（P4-P6 不得修改）。

---

## 0. 影响域分析（改 / 不改 / 风险）

### 0.1 改什么（本次显式变更面，均在 worktree `agate/` 内）

| # | 文件 | 改动 | 对应 BDD |
|---|---|---|---|
| 1 | `assets/templates/tech-debt-template.md`（**新增**） | DEBT 条目模板：用法/判据/字段表/三态/示例条目/回退强制 | BDD-5/9/19/20/11 |
| 2 | `scripts/agate-debt-check.py`（**新增**） | 多条目 schema 校验器（必填/枚举/evidence 非空/closed 准入/id 唯一） | BDD-5/6/7/8/9/10 |
| 3 | `scripts/check-debt.sh`（**新增**） | fail-closed 薄壳：`FILE` 模式=schema 校验；`--retreat-coverage` 模式=回退比对 WARNING | BDD-5..15 |
| 4 | `scripts/check-gate.sh` P8 分支（L413-471） | 增加 `debt_check:` 留痕检查（缺失 exit 1；内容不检） | BDD-16/17/18 |
| 5 | `phase-cards/P8-release.md` | 执行方式增加"确认债务清单"一步；产出规格增加 `debt_check` 字段 | BDD-16/17/18 |
| 6 | `rules/state-transitions.md`（回退规则节 L61-82） | 明确"回退落地后必须建 `source: retreat` DEBT 条目" | BDD-12/19 |
| 7 | `phase-cards/P6-acceptance.md`（L144）+ `phase-cards/P4-implementation.md`（L27） | 回退流程补 DEBT 强制提示 | BDD-12 |
| 8 | `scripts/agate-retreat-to.sh` | 回退完成后打印"须建 DEBT 条目"提醒（过程强制点） | BDD-12 |
| 9 | `assets/review-roles/plan-eng-review.md`（L19） | 追加"提债须用标准 DEBT 条目格式" | BDD-19/20 可发现性 |
| 10 | `WORKFLOW.md`（L79 + L81-91 目录图 + L85） | "固定 8 个子目录"→"9 个（含 debt/）"；目录图加 `debt/`；agents/ 注释去 tech-debt | BDD-1/4 |
| 11 | `orchestrator-template.md`（L102）/ `SETUP.md`（L114）/ `state-machine.md`（L40-41） | mkdir 8→9 子目录 + 文字表述同步（三处同一 9 集） | BDD-2/4 |
| 12 | `UPGRADING.md` | 新增 v0.43.0 变更节（debt/ 子目录、tech-debt 路径、P8 debt_check 字段、回退强制） | BDD-3 |
| 13 | `scripts/check-protocol-consistency.py` | CHECK 9 锚点表加 `check-debt.sh` 锚点；`scripts/README.md` 脚本清单补录 | [SCOPE+] #2 |
| 14 | `docs/tasks/TAG0003-workspace-architecture/P1-requirements.md`（BDD-1）+ `P6-acceptance.md`（BDD-1） | 追加 2026-08-12 修订注：口径 8→9（含 debt/） | BDD-4 |
| 15 | `tests/unit/check-gate.bats`（G8.2/3/4/6/7/8） | P8 fixture 的 P8-release.md 补 `debt_check:` 行 | BDD-16/17（[SCOPE+] #1） |
| 16 | `tests/unit/agate-debt-check.bats`（**新增**） | 校验器/回退覆盖/P8 留痕的 bats 用例 | BDD-5..18 |

### 0.2 不改什么（明确边界，降低风险）

- **`~/.agate`（v0.42.0 稳定版，指向主 checkout）禁止改动**——本任务只改 worktree `agate/`。
- **`agate-frontmatter-check.py` / `check-frontmatter.sh` 不动**——tech-debt 是多条目文件，不复用 frontmatter 单块解析；schema 校验器独立新增（见 §1 D2）。
- **`agate-retreat-to.sh` 的 retreat 提交格式不动**（`retreat: {old_p} -> {new_p}（诊断：...）`，L63 强制）——回退比对**零新增埋点**，只做只读比对（P1 §2.6）。
- **TAG0003 已验收的工作区机制主体（workspace 解析/迁移/roadmap/内容边界判据）不动**——仅 mkdir 子目录集加 debt/ 与 docs 表述同步（P0-brief known_risks[9]：增量不改已验收功能）。
- **`change_type: refactor` 机制（TAG0002）不动**——本任务不重复实现，仅基于含它的最新协议构建（P1 §1.2 决策 8）。
- **既有 654 用例的**语义**不动**——新增用例改变 count-tests 基线属预期；既有用例语义变更仅限 check-gate.bats P8 fixture 加字段（[SCOPE+] #1）。
- **债 vs 缺陷判据的 P7 人工核对（BDD-20）不新增脚本**——硬规则靠 P7 一致性评审，设计只提供判据文档锚点。

### 0.3 风险在哪（每个改动的副作用）

| 风险 | 来源 | 对策 |
|---|---|---|
| P8 `debt_check` 硬检查破坏既有 G8 测试（exit 2→1） | §1 D4 选 4A | 同步更新 6 处 fixture（[SCOPE+] #1），P3 先红后绿 |
| check-debt.sh 无 CHECK 9 锚点 → consistency WARNING | 新增 check-*.sh | P4 加锚点（[SCOPE+] #2）；WARNING 不阻断非 --strict |
| 模板示例 ```yaml 块被 CHECK 1 扫描，不合法会 ERROR | tech-debt-template.md 含 yaml 块 | 模板示例条目必须可被 yaml.safe_load（占位符用 `{...}` 会被 sanitize） |
| tech-debt.md 可能位于项目外工作区（`.agate.env` 指向外部） | 回退比对读 `{AGATE_WORKSPACE}/debt/tech-debt.md` | 复用 agate-workspace-resolve.sh 解析；文件不存在→按 BDD-13 判定（retreat 存在则 WARNING） |
| P8 确认退化成无脑打勾（Goodhart） | 机制固有 | 止损 4（连续 3 次空确认=移除强制），`debt_check: none` 可观测计数（BDD-18） |
| 回退比对召回低（样本 2） | 已知缺口（P0 known_risks[2]） | 诚实标注：触发器非排名工具，不承诺发现未爆雷债 |
| 归类修正漏同步某处 → 文档说 9 脚本建 8 | 多端面 | 三处 mkdir 同一字面量集（可 grep 校验）+ WORKFLOW 目录图 + BDD-4 重验 |

---

## 1. 候选方案与权衡（4 个决策点，candidate_count=4）

> 探索方法：本任务为常规功能 + 两处外部行为依赖（git log 提取、P8 分支对既有测试的影响）。先做了 §7 minimal_validation 确认关键假设，再据此收敛候选。

### 决策点 D1：DEBT 条目"机器校验块"的格式（YAML 块 + 正文混合的解析面）

**候选 1A：每条目一个 ` ```yaml ` fenced code block**
```
## DEBT0001

```yaml
id: DEBT0001
category: technical
...
```

正文补充（人读）……
```
解析：正则提取所有 ` ```yaml ` 块（复用 check-protocol-consistency.py:133-139 的 extract_code_blocks 模式），逐个 yaml.safe_load + 校验。

**候选 1B：每条目一个 `---` 分隔 frontmatter 块**（文件内多个 `---`...`---` 块，逐块解析）

| 维度 | 1A（fenced yaml） | 1B（--- 分隔块） |
|---|---|---|
| 与既有工具一致 | 强——CHECK 1 用同一 extract_code_blocks 正则；`known-failures-template.md` 单文件 Markdown 形态一致 | 弱——agate 既有 `_extract_frontmatter_block` 只认文件头块，需新写多块解析 |
| 与正文混合的边界 | 清晰（code fence 天然分界） | `---` 也是 Markdown 横线，正文含横线会误切 |
| 模板自校验 | 示例块被 CHECK 1 自动扫描（强制合法 YAML） | 无此自校验 |
| 解析鲁棒性 | 块内 `---` 少见，误判低 | 多文档分隔符语义模糊 |

**选择：1A。** 理由：① 与 CHECK 1 共用同一提取正则（复用既有机制，符合 review doc §6"不新造轮子"）；② fenced 块与正文边界无歧义；③ 模板示例被 CHECK 1 强制可解析，白送一层自校验。1B 的唯一优点（沿用 frontmatter 习惯）不足以抵消多块解析与横线歧义的实现成本。

### 决策点 D2：schema 校验器架构（复用 vs 独立）

**候选 2A：独立 `agate-debt-check.py` + `check-debt.sh` 薄壳**（check-frontmatter.sh / agate-frontmatter-check.py 的 fail-closed wrapper 模式：`[ ! -f "$FILE" ] && exit 0`；python exit≠0 → exit 1；stdout 非空 → exit 1）

**候选 2B：扩展 `agate-frontmatter-check.py`** 支持多 ` ```yaml ` 块

| 维度 | 2A（独立脚本） | 2B（扩展现有） |
|---|---|---|
| 上下文耦合 | 低——tech-debt 是"项目级多条目文件"，frontmatter 校验是"任务级单 frontmatter"，语义不同 | 高——SCHEMAS dict 按文件名路由，混入多块逻辑复杂化 P1/P2/P6/P7 校验 |
| BDD-10 兼容 | 清晰——无 yaml 块 → no-op | 需小心区分"无 frontmatter"与"无 yaml 块" |
| 回归风险 | 不触碰既有 4 类 frontmatter 校验 | 动既有校验器 → 654 用例回归面大 |
| 可测试性 | 独立 bats 文件 `agate-debt-check.bats`（P0-brief test_cmd 指向） | 需在 check-frontmatter.bats 加大量用例 |

**选择：2A。** 理由：tech-debt 的多条目块解析与 frontmatter 单块校验是两种数据形态，复用"薄壳 + stdout 错误行 + fail-closed"的模式（不是复用实现）；独立脚本把对既有 frontmatter 校验的回归风险降到零。P1 SUGGEST #3 同此。

### 决策点 D3：回退覆盖比对检查的形态

**候选 3A：`check-debt.sh --retreat-coverage` 子命令**（单脚本双命令：默认 FILE=schema 校验；`--retreat-coverage`=git log 比对）

**候选 3B：独立 `check-debt-retreat-coverage.sh` 脚本**

| 维度 | 3A（子命令） | 3B（独立脚本） |
|---|---|---|
| CHECK 9 锚点数 | 1 个（check-debt.sh） | 2 个（两个 check-*.sh 都要锚点） |
| 概念内聚 | "debt 检查"一个入口两种模式 | 拆成两个入口，调用方需知道哪个管什么 |
| 测试文件 | 一个 `agate-debt-check.bats` 覆盖两模式 | 需两个测试文件 |
| 复杂度 | check-debt.sh 内分支 | 每个脚本更短 |

**选择：3A。** 理由：schema 校验与回退比对都是"检查 debt 状态"的同一职责；单入口减少协议脚本数量与 CHECK 9 维护面；退出码语义分模式定义（schema 模式 exit 0/1，回退模式恒 exit 0 + WARNING）不冲突。P1 SUGGEST #4（回退比对只做 WARNING 不挂 gate）在 3A 中通过"回退模式恒 exit 0"落地。

### 决策点 D4：P8 债务确认留痕的检查强度

**候选 4A：`debt_check:` 字段缺失 → exit 1（硬强制留痕），字段存在但内容任意（含未关闭债务 / `none`）→ 通过**

**候选 4B：`debt_check:` 缺失 → WARNING（不阻断发布）**

| 维度 | 4A（缺失即拦） | 4B（WARNING） |
|---|---|---|
| 与设计意图 | 一致——review doc §5.4"P8 必须**看过**清单并留痕"是强制的；BDD-17"仅验证确认留痕存在"暗示 gate 会验存在 | 留痕从"必须"退化为"建议"，机制形同虚设 |
| 对既有测试 | 需更新 6 处 G8 fixture（[SCOPE+] #1） | 零影响（仍 exit 2，多一行 WARNING） |
| 与 bump_type 一致性 | 一致（bump_type 缺失即 exit 1） | 不一致——留痕比 bump_type 更宽松 |
| 防 Goodhart | 内容不检，无激励性 | 同左 |

**选择：4A。** 理由：Phase 3 的全部意义就是把"确认债务清单"从可选变成 P8 必做项；缺失不拦 = 没实现。BDD-17 的"不阻断"仅针对**内容**（未关闭债务/空确认），4A 恰好只查存在性、内容全放行。既有测试 fixture 更新是 BDD-16/17 的直接代价，P3/P4 同步即可。

---

## 2. 方案设计（选定方案的可实现细节）

### 2.1 tech-debt.md 条目格式与解析契约

下游项目文件：`{AGATE_WORKSPACE}/debt/tech-debt.md`（用户决策，修正 TAG0003 agents/ 归类）。每条 DEBT = 一个 ` ```yaml ` fenced block（机器校验）+ 可选正文（人读），`## DEBT0001` 标题按 id 编号。示例条目见 `assets/templates/tech-debt-template.md`（模板含该示例，须可被 yaml.safe_load——CHECK 1 扫描）。

解析契约（agate-debt-check.py）：
- 提取所有 ` ```yaml ` fenced blocks（正则同 CHECK 1 的 extract_code_blocks，语言仅 `yaml`）。
- 每个 block `yaml.safe_load`；结果非 dict → 报错"条目 {index} 的 YAML 块必须为 key: value 映射"。
- **无任何 yaml block → no-op exit 0**（BDD-10：文件不存在/为空/纯正文旧格式均不拦截，向后兼容）。

### 2.2 agate-debt-check.py schema 校验规则

逐条目校验，错误行输出到 stdout（格式 `{basename}:{entry_id}: {msg}`，无 id 用块序号），全部校验后一次性输出。

**必填字段**（缺失或 null → 拦截）：`id`、`category`、`title`、`status`、`priority`、`evidence`（须为非空 list）、`impact`、`recommendation`、`closure_criteria`（须为非空 list）、`source`、`created_at`。

**枚举校验**（BDD-7 + P1-review N2）：
- `category` ∈ {technical, management, protocol}
- `status` ∈ {open, in_progress, closed}
- `priority` ∈ {high, medium, low}
- `source` ∈ {retreat, review, retrospective}（N2：source 一并枚举校验）

**类型校验**：`task_id` 允许 null 或 str；`evidence`/`closure_criteria` 须为 list；`created_at` 须为 str；`status`/`priority`/`category`/`source`/`title`/`impact`/`recommendation`/`id` 须为 str。

**closed 准入**（BDD-8）：`status == closed` 时——
- `task_id` 非空（立项须有具体任务）；
- `evidence` 序列化文本（拼接所有 path/note/ref 值）**必须同时包含**该 `task_id` 与 `P5`/`P6` 标记（引用关联任务的 P5/P6 证据）。缺一 → 拦截。

**三态语义**（BDD-9）：schema 仅允许 open/in_progress/closed 三值（枚举校验）；`task_id` 非空即视为 in_progress，故 `status=open + task_id` 是**合法**条目（不要求额外的 accepted/planned 态，validator 不拦截此组合）——此语义写进模板与判据文档，P6 语义核对。

**id 唯一性**：同文件内重复 id → 拦截（登记簿 id 必须可唯一引用）。

### 2.3 check-debt.sh 薄壳（双命令）

- **默认 `check-debt.sh FILE`**：fail-closed schema 校验（完全复刻 check-frontmatter.sh 的 mktemp stderr + python exit≠0→exit 1 + ERRORS 非空→exit 1）；`[ ! -f "$FILE" ] && exit 0`。
- **`check-debt.sh --retreat-coverage`**（BDD-13/14/15）：
  1. source `agate-workspace-resolve.sh "$REPO_ROOT"` 解析 `AGATE_WORKSPACE`（同 pre-commit-gate.sh L30-32）；`REPO_ROOT` 取当前目录（或 `$2`）。
  2. `git log --all --format='%H%x09%s' --grep='^retreat:'` 提取 retreat 提交（§7 minimal_validation 已实测可提取 023b28b/29301ad）。无 retreat → exit 0。
  3. `agate-debt-check.py --covered-hashes {AGATE_WORKSPACE}/debt/tech-debt.md`：输出所有 `source: retreat` 条目中出现的 hex token（7-40 位 `[0-9a-f]`），去重，作为"已覆盖哈希集合"。
  4. 对每个 retreat 提交，其 short（前 7 位）或 full hash 不在覆盖集合 → stderr 打 `GATE DEBT WARNING: retreat 提交 {short}（{subject}）未登记为 source: retreat DEBT 条目（evidence 须引用该提交，文件 {path}）`。
  5. **恒 exit 0**（WARNING 不阻断——SUGGEST #4；BDD-13"不阻断 commit/发布"）。
  6. tech-debt.md 不存在时：retreat 存在 → 每条都打缺失 WARNING（这正是 BDD-13 的"无任何对应条目"情形，含未建文件）。

### 2.4 回退强制（Phase 2 唯一硬强制）

- `rules/state-transitions.md` 回退规则节（L61-82 之后）追加：**"回退落地后必须建 DEBT 条目（`source: retreat`，`evidence` 引用 retreat 提交哈希）——模板见 `assets/templates/tech-debt-template.md`"**（BDD-12 文档锚点）。
- `phase-cards/P6-acceptance.md` L144（FAIL>0 回退流程）与 `phase-cards/P4-implementation.md` L27（退回后重派）各补一句同一强制。
- `scripts/agate-retreat-to.sh`：多步回退全部 commit 后追加一行提醒 `GATE RETREAT: 回退已完成——请为本次回退建立 source: retreat 的 DEBT 条目（{AGATE_WORKSPACE}/debt/tech-debt.md）`（过程强制点，BDD-12"回退落地后"）。
- 事后兜底 = §2.3 的 `--retreat-coverage`（只读提醒，不挂任何 gate）。

### 2.5 P8 锚定（Phase 3）

- `phase-cards/P8-release.md`：
  - 执行方式第 4 步后新增一步：**"确认债务清单：读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（若存在），在 P8-release.md 写入 `debt_check:` 字段"**。
  - 产出规格新增：`debt_check: none`（本次无关注项，合法选项）或 `debt_check: reviewed`（已核对，正文附条目 id 清单）。（N3：显式字段，保证空确认可区分）
- `check-gate.sh` P8 分支（bump_type 检查之后、version 检查之前）新增：
  ```bash
  # 债务清单确认留痕检查（TAG0001 Phase 3）：只查留痕存在，不查内容达标、不阻断发布
  if ! grep -q 'debt_check:' "$TASK_DIR/P8-release.md" 2>/dev/null; then
      echo "GATE P8: P8-release.md 缺 debt_check 字段（须确认债务清单并留痕，可为 none）" >&2
      exit 1
  fi
  ```
  - 缺失 → exit 1（4A）；字段存在（值任意，含 none/未关闭债务）→ 通过 → BDD-17"不因内容拦截"。
  - BDD-18 可观测：跨 P8-release.md（git 历史）`grep 'debt_check: none'` 计数，即"连续 N 次空确认"的可执行判据。

### 2.6 归类修正同步面（多端，P1 §2.2 四项 + 新增）

- **WORKFLOW.md**：L79"固定 8 个子目录"→"固定 9 个子目录（含 debt/）"；L85 agents/ 注释 `# agent 输入知识（project.md / memory）`（去 tech-debt）；目录图（L83-90）加 `├── debt/  # 技术债登记（tech-debt.md）`。
- **mkdir 三处**（同一字面量 9 集 `{roadmap,tasks,agents,archived,reviews,decisions,plans,logs,debt}`）：orchestrator-template.md L102（含文字清单同步）、SETUP.md L114、state-machine.md L40-41（含注释"9 个子目录"）。
- **SETUP.md**：无其他 8 集表述（L22 `mkdir -p {AGATE_WORKSPACE}/agents` 保留——agents/ 仍在）；新项目接入说明在模板/目录图引用处点明 tech-debt 位于 `debt/`。
- **UPGRADING.md**：新增 v0.43.0 变更节：① 工作区子目录集 8→9（存量项目 `mkdir -p {AGATE_WORKSPACE}/debt` 可启用 tech-debt，可选）；② tech-debt.md 路径 `{AGATE_WORKSPACE}/debt/tech-debt.md`（不再指向 agents/）；③ P8-release.md 新增 `debt_check` 必填字段；④ 回退落地须建 DEBT 条目。既有 v0.41.0 节不改（N4 确认其未内嵌 mkdir 命令，无需修正命令本体）。
- **TAG0003 口径重验（BDD-4）**：在 TAG0003 `P1-requirements.md` BDD-1 与 `P6-acceptance.md` BDD-1 追加修订注"【2026-08-12】口径由 TAG0001 更新为 9 子目录（含 debt/）——WORKFLOW.md 目录规范已改，本记录保留原 8 子目录证据"，不重写历史证据；BDD-4 通过判据 = 修订注存在 + 三处 mkdir 与目录图一致为 9 + 全量 bats 回归无红。

### 2.7 review 角色卡可发现性

`assets/review-roles/plan-eng-review.md` L19"技术债有没有记录和计划"追加：**"若提出'后续应重构 / 存在架构债'，须用标准 DEBT 条目格式（模板 `assets/templates/tech-debt-template.md`，`evidence` 必填）——强制格式，不强制产出"**。（P1 §2.8 三处可见锚点：review 卡 / P8 卡 / 回退规则文档，本设计三处齐备。）

### 2.8 T001 回填验证（BDD-11 试金石）

- 回填 source：`docs/reviews/T001-retrospective-2026-08-10.md` 技术原因表 T1-T4（L119-122，各含问题/根因/影响）。按 SUGGEST 顺带回填协议原因 A5/A6（category: protocol），管理原因 M1-M5 不回填。
- 落点：**bats fixture + 模板示例条目**。P4 将 T1-T4(+A5/A6) 按 §2.1 格式写成 DEBT 条目，置于 `agate/tests/fixtures/tech-debt-backfill.md`（或 bats heredoc fixture），由 P6 对其实跑 `check-debt.sh` schema 校验。
- 无损判据：每条回填条目的 `title`（问题）、`evidence`（根因）、`impact`（影响）三字段必须可从复盘原文对应——回填失败（连既有条目都填不进模板）即止损条件 1 触发，模板重新设计。

---

## 3. BDD 覆盖映射（20/20 可验收路径）

| BDD | 设计落点 | 可验收路径 |
|---|---|---|
| BDD-1 | §2.6 WORKFLOW 目录图 | grep WORKFLOW.md：含 `debt/` 且 agents/ 注释不含 tech-debt |
| BDD-2 | §2.6 mkdir 三处 | grep 三文件同一 9 集字面量 + fixture 实跑 mkdir 建出 9 目录 |
| BDD-3 | §2.6 UPGRADING/SETUP | grep 无 `agents/tech-debt` 过期表述；UPGRADING v0.43.0 节含 debt/ 路径 |
| BDD-4 | §2.6 TAG0003 口径 | 修订注存在 + 三处一致 9 集 + 全量 bats 回归无红 |
| BDD-5 | §2.2 | 合法条目（含 closed 准入）过校验 exit 0 |
| BDD-6 | §2.2 | evidence 缺失/空 → 拦截 |
| BDD-7 | §2.2 | category/status/priority/source 枚举外值 → 拦截 |
| BDD-8 | §2.2 | closed 缺 task_id 或缺 P5/P6 证据引用 → 拦截 |
| BDD-9 | §2.2 | status 三值枚举 + open+task_id 合法（无需额外态） |
| BDD-10 | §2.2/2.3 | 无文件/空文件/无 yaml 块 → exit 0 无输出 |
| BDD-11 | §2.8 | fixture 回填 T1-T4 过校验 + 字段可对应原文 |
| BDD-12 | §2.4 | grep state-transitions + P6/P4 卡片 + retreat-to.sh 提醒含强制语 |
| BDD-13 | §2.3 | fixture git 仓库含 retreat 提交但无条目 → WARNING 缺失 + exit 0 |
| BDD-14 | §2.3 | 有 source: retreat 条目且 evidence 引用提交 → 无 WARNING |
| BDD-15 | §2.3 | 用 023b28b/29301ad 消息构造 fixture，正反两向可复现 |
| BDD-16 | §2.5 P8 卡片 | P8-release.md 产出规格含 debt_check + 卡片含确认步骤 |
| BDD-17 | §2.5 check-gate.sh | 有 debt_check（值任意含 none）+ 未关闭债务 → exit 2 通过 |
| BDD-18 | §2.5 | `debt_check: none` 标记可跨发布 grep 计数 |
| BDD-19 | §2.1 模板判据节 | 模板含三分法判据原文 + "都不影响→不登记"出口 |
| BDD-20 | §2.1 模板 + review 卡 | 判据含"登记 DEBT 不豁免当前任务"硬规则；P7 人工核对（无脚本） |

## 4. gate_commands（P2 固化，P4-P6 不得修改）

```yaml
gate_commands:
  P3: "bats agate/tests/unit/agate-debt-check.bats"          # 新增校验器/回退覆盖/P8 留痕用例（TDD 红→绿）
  P5: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/"  # 全量回归
```

> 其余验证命令遵循 AGENTS.md 标准流程（非 gate_commands，供 P5/P6 执行）：`python3 agate/scripts/check-protocol-consistency.py`（0 ERROR）、`shellcheck -S warning agate/scripts/*.sh`、`bash agate/tests/scripts/count-tests.sh`（基线核对，本次新增用例数须计入）。

## 5. files_to_read（P4 implementer 上下文地图）

```yaml
files_to_read:
  - path: agate/scripts/check-frontmatter.sh
    why: fail-closed 薄壳范式（check-debt.sh 照此写：mktemp stderr / python exit≠0→exit 1 / ERRORS 非空→exit 1 / 文件不存在 exit 0）
  - path: agate/scripts/agate-frontmatter-check.py
    why: schema 校验器范式（SCHEMAS/_check/main、从 FILE env 读路径、异常兜底）——agate-debt-check.py 复用其错误输出风格与 fail-closed 兜底
  - path: agate/scripts/check-gate.sh:413-471
    why: P8 分支，debt_check 检查插在 bump_type 之后 version 检查之前
  - path: agate/scripts/check-protocol-consistency.py:133-139,444-724
    why: extract_code_blocks 正则（agate-debt-check.py 复用）+ CHECK 9 锚点表（加 check-debt.sh 锚点）
  - path: agate/scripts/agate-retreat-to.sh:54-70
    why: retreat 提交格式（回退比对依据）+ 回退完成提醒注入点
  - path: agate/scripts/agate-workspace-resolve.sh
    why: --retreat-coverage 的 workspace 解析（source 模式，同 pre-commit-gate.sh:30-32）
  - path: agate/scripts/pre-commit-gate.sh:149-159
    why: frontmatter wiring 模式（参考；本设计 check-debt.sh 不接入 pre-commit，只读参考边界）
  - path: agate/WORKFLOW.md:77-91
    why: 目录规范（BDD-1）——目录图 + 8→9 表述
  - path: agate/SETUP.md:109-130, agate/orchestrator-template.md:99-103, agate/state-machine.md:33-45
    why: 三处 mkdir 同步为同一 9 集（BDD-2）
  - path: agate/phase-cards/P8-release.md
    why: 加"确认债务清单"步骤 + 产出规格 debt_check 字段（BDD-16/17/18）
  - path: agate/phase-cards/P6-acceptance.md:144, agate/phase-cards/P4-implementation.md:27
    why: 回退流程补 DEBT 强制（BDD-12）
  - path: agate/rules/state-transitions.md:61-82
    why: 回退规则节补"回退落地后必须建 DEBT 条目"（BDD-12）
  - path: agate/assets/review-roles/plan-eng-review.md:19
    why: 追加"提债须用标准 DEBT 条目格式"（BDD-19/20 可发现性）
  - path: agate/UPGRADING.md:92-121
    why: v0.41.0 节为参照，新增 v0.43.0 变更节（BDD-3）
  - path: agate/tests/unit/check-gate.bats:1140-1258
    why: P8 fixture 更新（G8.2/3/4/6/7/8 补 debt_check）+ 新增用例参照（[SCOPE+] #1）
  - path: agate/tests/helpers/load.bash, fixtures.bash, git-helper.bash
    why: bats helper（create_task_dir / git_init / git_commit——写 agate-debt-check.bats 用）
  - path: docs/reviews/T001-retrospective-2026-08-10.md:115-122
    why: 回填 source（T1-T4 技术原因表 + A5/A6 协议原因）
  - path: docs/tasks/TAG0003-workspace-architecture/P1-requirements.md:84-90
    why: TAG0003 BDD-1 口径（BDD-4 修订注落点）
```

## 6. env_constraints

```yaml
env_constraints:
  debug_env: "bash agate/scripts/check-state-yaml.sh docs/tasks/TAG0001-tech-debt-closure/.state.yaml"
  test_cmd: "bats agate/tests/unit/agate-debt-check.bats"
  workspace_path: "{AGATE_WORKSPACE}/debt/tech-debt.md（独立 debt/ 目录；协议侧模板 assets/templates/tech-debt-template.md 在 worktree agate/ 内）"
  isolation_check: |
    本任务为纯协议仓库内变更 + bats fixture 隔离。git 操作仅只读（git log 提取 retreat / 全量回归）；
    不写生产环境、不接触外部系统。retreat 提交读取用 --grep 只读查询，无写操作。
```

## 7. minimal_validation

```yaml
minimal_validation:
  - assumption: "git log --grep='^retreat:' 能提取全仓库 retreat 提交（回退比对的数据源）"
    method: "worktree 实跑：timeout 30 git log --format='%h %s' --all --grep='^retreat:'"
    result: "confirmed"
    note: "2026-08-12 实测返回 023b28b / 29301ad 两条，格式 'retreat: PX -> PY（诊断：...）' 与 agate-retreat-to.sh L63 一致——外部系统行为（git）假设成立，可为 BDD-13/14/15 提供 fixture 依据"
  - assumption: "mkdir 8→9 后原本依赖旧 8 子目录集的行为流向（T086 B1 教训）"
    method: "grep 全 worktree agate/ 查 'roadmap,tasks,agents,archived,reviews,decisions,plans,logs' 与 '8 个子目录'"
    result: "confirmed"
    note: "该字面量仅存在于 4 处文档（WORKFLOW.md:79 / orchestrator-template.md:102 / state-machine.md:40-41 / SETUP.md:114），无脚本/测试对子目录集做计数断言（P1-review N1 已核实）。改为 9 集是纯增量（多建 debt/），旧 8 集无任何代码分支依赖——无兜底分支被破坏。属'纯代码逻辑 + 落点已验'"
  - assumption: "P8 加 debt_check 缺失即 exit 1 对既有 check-gate.bats 的影响"
    method: "读 check-gate.bats:1140-1258 各 G8 fixture 的 P8-release.md 内容"
    result: "confirmed"
    note: "G8.2/3/4/6/7/8 的 P8-release.md 仅含 'bump_type: minor'，加硬检查后将从 exit 2 变 exit 1 → 设计要求同步更新这 6 处 fixture（[SCOPE+] #1）。G8.1（缺 bump_type）在 debt_check 检查置于 bump_type 之后时不受影响"
  - assumption: "```yaml fenced 块提取（agate-debt-check.py 的核心解析）"
    method: "复用 check-protocol-consistency.py:133-139 既有 extract_code_blocks 正则（已读核实）"
    result: "confirmed"
    note: "纯代码逻辑，无外部系统依赖——依赖内部函数 extract_code_blocks 的既有正则模式 + yaml.safe_load（pyyaml 已核实可用，agate-frontmatter-check.py 在用）"
```

## 8. 实现完成标志（P3/P5/P6 判定基准）

1. `assets/templates/tech-debt-template.md` 存在，含判据三分法 + "不登记"出口 + 三态 + 字段表 + 可解析示例条目。
2. `agate-debt-check.py` + `check-debt.sh`：§2.2 全部校验规则落地；BDD-5..10 各对应一条 bats 用例红→绿。
3. `check-debt.sh --retreat-coverage`：BDD-13/14/15 三向用例通过（含 023b28b/29301ad 消息 fixture）。
4. `check-gate.sh` P8 分支含 debt_check 检查；P8-release.md fixture 更新后 G8 全组绿；新增 debt_check 缺失=exit 1、内容任意=exit 2 用例。
5. `phase-cards/P8-release.md` + `rules/state-transitions.md` + P6/P4 卡片 + `agate-retreat-to.sh` 四处在位"确认债务清单 / 回退须建 DEBT"强制语。
6. WORKFLOW.md 目录图含 debt/、agents/ 注释去 tech-debt；三处 mkdir 为同一 9 集；UPGRADING v0.43.0 节存在。
7. TAG0003 P1/P6 BDD-1 修订注在案（BDD-4）。
8. `agate/tests/unit/agate-debt-check.bats` 全绿 + 全量 bats 回归无红 + consistency 0 ERROR + count-tests 基线已更新。
9. [SCOPE+] #1/#2 全部落地（G8 fixture 更新、CHECK9 锚点 + scripts README 补录）。

## 9. [SCOPE+] 声明

- [SCOPE+] #1：P8 gate 加 `debt_check` 缺失即 exit 1 要求同步更新 check-gate.bats 既有 6 处 G8 fixture（G8.2/3/4/6/7/8 的 P8-release.md 补 `debt_check:` 行），并新增 2 组用例（缺失→exit 1 / 内容任意→exit 2）。P1 未显式枚举该 fixture 同步面。
  必须做的理由：BDD-16/17 要求 P8 强制留痕，不更新 fixture 则既有用例从 exit 2 变 exit 1 全红，654 基线被破坏。
  影响：P3/P4 测试面 + count-tests 基线（用例数增加）。
- [SCOPE+] #2：`check-protocol-consistency.py` 的 SCRIPT_ALIGNMENT_ANCHORS 需为 `check-debt.sh` 加锚点，且 `scripts/README.md` 脚本清单补录 check-debt.sh/agate-debt-check.py。P1 改动面表未含这两处。
  必须做的理由：check_anchor_coverage（L694-724）对无锚点的 check-*.sh 报 CHECK9-coverage WARNING（--strict 阻断）；脚本清单缺失破坏可发现性。
  影响：check-protocol-consistency.py + scripts/README.md 文件改动（均触发 self-gate）。

## 10. 风险与开放项

- **回退比对召回局限**：全仓库仅 2 条 retreat（样本 1 起事件），信号只能发现已爆雷债，不承诺发现未爆雷债（P0 known_risks[2]、review doc §8.3 诚实标注）。
- **P8 确认退化成无脑打勾**：4A 硬检查 + `debt_check: none` 可观测；若连续 3 次空确认 → 按止损条件 4 移除强制（本设计已提供计数口径，移除动作属治理决策不在本任务）。
- **模板回填是试金石**：若 T1-T4 填不进模板 → 止损条件 1，模板重新设计（BDD-11 内嵌判据）。
- **三态是否够用**：无实证；若 Phase 3 需区分"已立项未开工/开工中"再加回一态（review doc §8.3 第 3 条，本次不预设计）。
- **check-debt.sh 不接入 pre-commit**：schema 校验靠"提债/建条目过程步骤 + P8 检查"执行，非每次 commit 拦截。若日后自愿通道死亡（止损 2），可评估接入 pre-commit 强化（本设计不预做，避免 BDD-10 兼容面扩大）。
- **开放项**：`debt_check` 字段值的取值集合是否要在 schema 层约束（当前设计只查存在性不查值，`none`/`reviewed` 为模板建议值而非硬枚举）——P3/P6 按"只查存在性"验收。
