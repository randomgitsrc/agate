# agate v2.0 结构化改造 — 交接文档

> **给新会话 agent**：本文档让你在无上下文的情况下接手「agate v2.0 结构化数据改造」。请先完整读本文件，再按步骤执行。
> 交接时间：2026-08-09（基于 main = v0.35.0）
> 前置：可行性评估已完成并发布（https://peek.gsis.top/mpifxr ），本文件是它的可执行交接。

---

## 1. 任务一句话

用 **agate 完整 P0-P8 流程**（dogfooding，用 agate 改造 agate 自己），把 agate 协议里的机器读取字段从"正文内嵌 YAML + 正则提取"重构为"YAML frontmatter + pyyaml 解析"，消除持续性的"正则摩擦补丁税"（v0.30.2 → v0.35.0 连续 5 版都在打同类补丁）。

**最终目标**：agate v0.40.0（本次改造世代代号 "v2.0"，即 worktree/分支名 `feat/v2.0`，非实际 semver）。附带收益：为全 py 化 + Windows 原生适配铺路（无 Git Bash 依赖）。

---

## 2. 你在哪、为什么在 worktree

- **本项目**：agate 软件工程协议仓库（`agate/` 子目录是协议本体，`~/.agate` 软链指向它）
- **你在**：隔离 worktree（`.worktrees/v2.0`，分支 `feat/v2.0`）
- **为什么**：v2.0 改造会改 gate 本身（check-gate.sh、pre-commit-gate.sh 等）。若在主 checkout 直接做，`~/.agate` 指向的协议本体（本机所有项目在用，v0.35.0 稳定版）会被污染。worktree 隔离实验，不碰主 checkout。

## 3. 两个工作区（务必分清）

| 工作区 | 路径 | 分支 | 用途 |
|--------|------|------|------|
| **主 checkout**（`~/.agate` 指向它，**勿动**） | `/home/kity/oclab/agate` | `main` | 本机项目用的协议本体 = **v0.35.0 稳定版**，也是你跑 agate 流程的**开发工具** |
| **worktree**（**你在这做**） | `/home/kity/oclab/agate/.worktrees/v2.0` | `feat/v2.0` | v2.0 改造对象 |

**铁律**：
- ✅ 所有改造在 worktree：`cd /home/kity/oclab/agate/.worktrees/v2.0`
- ✅ 跑测试：`cd .worktrees/v2.0 && bats agate/tests/...`（bats 环境里 `load.bash` 自动反推 AGATE_ROOT 到 worktree 本体）
- ✅ 读协议/阶段卡片：`~/.agate/...`（v0.35 稳定版，作为开发工具的规范）
- ❌ **不要**手动 `source agate/tests/helpers/load.bash`——`load.bash` 依赖 bats 的 `BATS_TEST_DIRNAME`，手动 source 时该变量未定义会**死循环卡住**（已踩过）。它只能被 bats `load "tests/helpers/load.bash"` 调用。
- ❌ 不要在主 checkout 改任何东西

## 4. 当前状态（已核实）

- worktree 分支 `feat/v2.0` = `e5540fc`（= main = v0.35.0），**干净**
- 主 checkout `main` = `e5540fc`，`~/.agate` 指向它
- 工作区干净（仅本交接文档未跟踪）
- worktree 里 `bats agate/tests/sanity.bats` 通过（基线 OK）
- 测试基线：count-tests.sh 输出 593（sanity 6 另算，共 599）

---

## 5. 任务核心：v2.0 结构化改造

### 5.1 现状（可行性评估已核实）

机器字段分布在三层：
1. **真 YAML frontmatter**（`---` 块）：`P*-review.md` 的 `status`/`agent`、通用 Header
2. **正文内嵌 YAML**（"半结构化"）：P1 的 `risk_level`/`phases`/`internal_only` 等、P2 的 `candidate_count`/`packages`/`domains`/`ui_affected`/`gate_commands`——靠**正则**从全文 grep 提取（`agate-md-field-get.py` 用正则，`check-gate.sh` 用 `grep -E '^key:'`）
3. **纯散文标记**：`- PASS/FAIL` 行、`[NEED_CONFIRM]`/`[SUGGEST:]`/`[DESIGN_GAP]`/`[BLOCKER]`/`[PROD_TOUCHED]`/`[SCOPE+]`、`#### BDD-NN:` 标题

`.state.yaml` 已是**完全结构化**（pyyaml 校验），是唯一"干净"范例。

### 5.2 方案（评估结论：Option A）

**Option A（强化 frontmatter）**：机器字段并入产出物已有的 frontmatter 块，gate 用 pyyaml 读。**优于 Option B（独立 .yaml / metadata.yaml）**——LLM subagent 写两个文件并同步漂移的风险远高于写一个文件 frontmatter；集中 metadata.yaml 引入多包并发写冲突。

**关键机制**（防"主 Agent 造假"）：仿照 `.state.yaml` 的 `agate-state-yaml-check.py`，做一个 **frontmatter schema 校验器**（如 `agate-frontmatter-check.py`），在 pre-commit 时用 pyyaml 校验 P1/P2 frontmatter 字段类型/必填。subagent 写坏格式 → gate 直接拦，**不靠主 Agent 判断**。指引（角色卡/模板）只负责告诉 subagent 字段写哪，机器校验确保写错就拦。

### 5.3 分阶段路线（评估建议，一个 v2.0 发布，内部分流）

- **流 A（P1/P2 格式迁移 + schema 校验器）**——最小爆炸半径，先做
- **流 B（P6/P7 结果结构化）**——依赖流 A 的校验器
- **流 C（标记状态收尾）**——最后

**scope 决策（已定）**：`gate_commands` **暂留正文**（`agate-read-gate-commands.py`/`agate-gate-missing-cmds.py`/`agate-read-p5-commands.py` 三个工具仍从正文正则读，移入 frontmatter 会失配）。只迁移候选数/裁剪类字段（risk_level/phases/candidate_count/packages/domains/ui_affected）。gate_commands 的 frontmatter 迁移留到后续。

### 5.4 硬约束（评估 §6.3）

1. `count-tests.sh` 数字**不能漂移**
2. frontmatter 禁止 >3 层嵌套
3. 角色卡必须贴可复制模板
4. 在途任务：**双读**（frontmatter 优先 + 旧正则回退）兼容旧格式——`agate-md-field-get.py` 先 pyyaml 读 frontmatter，无 key 回退正则
5. CHECK 9 锚点表（`check-protocol-consistency.py` 33 条）全量过一遍
6. **v2.0 设计文档必须写明"结构化不解决语义真实性"**——gate 强度不升不降，只提高解析可靠性。BDD-8 单侧/双侧歧义、candidate_count 虚报在结构化后依旧

### 5.5 语义真实性边界（诚实声明）

结构化解决的是"格式摩擦"（全角冒号、PROD_TOUCHED 误报、DESIGN_GAP 0-vs-0），**不解决"内容真实性"**（BDD-8 单侧/双侧歧义、权衡关键词）。后者靠 subagent 独立上下文 + review 角色。`[SCOPE+]`/`[PROD_TOUCHED]`/`[DESIGN_GAP]` 是"运行时意外发现"，**保持散文标记**，只结构化其"已解决"状态。

---

## 6. 执行流程（关键：用 agate 完整 P0-P8 改造 agate 自身）

### 6.1 为什么用完整 P0-P8（而不是轻量 self-gate）

这是**用 agate 改造 agate**（dogfooding）。改造对象是 worktree 里的 `agate/` 协议本体；跑流程的工具是 `~/.agate`（v0.35 稳定版）。用完整流程获得纪律：P1 需求分析系统性列清摩擦清单、P2 设计做方案、P3 测试设计先行。

### 6.2 编排方式

- 任务目录：worktree 里的 `docs/tasks/{Txxx}-v2.0-structured/`
- 每阶段派 subagent + 阶段评审（requirements-review / plan-design-review）
- **阶段产出物按当前格式（v0.35）写**，能过当前 gate；"新格式的读取/校验正确性"由 P3 测试设计 + P5 验证阶段专门构造新格式 fixture 覆盖
- P8 发布时仍带 `self-gate-review:`（改了协议本身，两个流程都要过）

### 6.3 流程步骤

1. **P0 立项**：写 P0-brief.md（本交接文档 + 评估报告 mpifxr 是主要输入）
2. **P1 需求分析**（analyst）：系统性列 v2.0 摩擦清单（40+ 字段的现状、每处正则摩擦史）→ requirements-review 独立评审
3. **P2 设计**（architect）：frontmatter 方案细化（字段 schema、校验器设计、双读回退）→ plan-design-review
4. **P3 测试设计**（test-designer）：新格式 fixture + 校验器测试先行
5. **P4 实现**（implementer）：改 `agate-md-field-get.py`、新增校验器、改模板/角色卡/fixtures
6. **P5 验证**：全量 bats + shellcheck + consistency
7. **P6 验收**：对照 P1 BDD 逐条验证
8. **P7 一致性**：双向检查设计 vs 实现
9. **P8 发布**：v0.40.0 badge + CHANGELOG + tag + **普通 merge（--no-ff）**（release PR 禁止 squash）
   > 命名提醒："v2.0" 是本次改造的世代代号（worktree/分支名），实际 semver 是 **v0.40.0**（agate 走 v0.x 版本线），二者不要混用。

---

## 7. 验证命令（worktree 里跑）

```bash
cd /home/kity/oclab/agate/.worktrees/v2.0

# 全量测试
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# 一致性检查（0 ERROR 才行）
python3 agate/scripts/check-protocol-consistency.py

# 测试计数（不能漂移）
bash agate/tests/scripts/count-tests.sh
```

---

## 8. 关键背景与已踩坑记录（避免重复）

- **`load.bash` 不能手动 source**（BATS_TEST_DIRNAME 未定义 → 死循环卡住）。它只能被 bats `load "tests/helpers/load.bash"` 调用。
- **v0.34.0 已把 46 处内联 python 抽离成 14 个 .py 工具**——这是净帮助：解析逻辑集中在 `agate-md-field-get.py` 等，结构化重构时只需改 1 个 py 工具 + 薄壳，而不是 N 处内联正则。
- **`.state.yaml` 是机器校验的范式**：`agate-state-yaml-check.py`（pyyaml 校验）+ `check-state-yaml.sh`（pre-commit 拦截）。frontmatter 校验器仿照它。
- **release PR 必须普通 merge（--no-ff）**，禁止 squash（v0.31.0 tag 分叉事故）。tag 打在版本 commit 上，合并后 `describe` 正常。
- **本机历史**：v0.34.0 的 py-extraction worktree 已清理；v0.35.0 是当前 main。
- **Windows 适配是最终目标**：全 py 化后 Windows 只需 Python + Git，无需 Git Bash。结构化是 py 化的第一步（消除"bash 正则解析"存在的理由）。

---

## 9. 新会话 agent 角色配置（关键：跑起 P0-P8 的前提）

### 9.1 你的角色 = orchestrator（编排者，不是实现者）

用完整 P0-P8 流程改造 agate，意味着**你（新会话主 Agent）是 orchestrator**：

| 你做 | 你不做 |
|------|--------|
| 读状态（`.state.yaml`、阶段产出） | 亲自写阶段产出（需求/设计/代码/测试） |
| 派发 subagent——含任务分解 + 输入导航 | 亲自实现 |
| 跑 gate 验证（check-gate.sh 等） | 信 subagent 的自我报告 |
| 更新 `.state.yaml` + active-tasks.md | 跳过 gate 直接推进 |
| 写 P0-brief.md | —— |

**核心纪律（来自 orchestrator-template.md + dispatch-protocol.md）**：
1. **用 task 工具派发**，动词是"派发"不是"执行"——你不自己产出阶段文件
2. **上下文隔离**：不让 subagent 把文件全文返回给你；subagent 只返回"路径 + 一句话摘要"
3. **不信自我报告**：subagent 返回后，你亲自跑 gate 脚本验证（不能凭 subagent 说"过了"）
4. **你不是 gate**：只跑脚本让它判，不要手动 grep 文件验证 gate 条件

### 9.2 本平台（OpenCode）的派发方式：方法 B

`agate/platform-notes.md` 明确：**OpenCode 的 task 工具派发 subagent 可用，但 `--custom-role` 不可用**（issue #29616）。所以：

**方法 B（推荐）**：派发时在 subagent 的 prompt 里**直接写入角色定义文件路径**，让 subagent 自己读取并遵循。示例：

```
你是本次 P1 阶段的 analyst。请先读角色定义：
  {agate_root}/assets/execution-roles/analyst.md
然后按该角色定义执行，产出 docs/tasks/{Txxx}/P1-requirements.md。
{agate_root} = ~/.agate（v0.35 稳定版协议本体）
任务上下文见 docs/tasks/{Txxx}/P0-brief.md。
```

角色文件清单（`~/.agate/assets/` 下）：
- **execution-roles/**：analyst（P1）、architect（P2）、test-designer（P3）、implementer（P4/P8）、verifier（P5/P6）、consistency-reviewer（P7）
- **review-roles/**：requirements-review（P1 评审）、plan-design-review（P2 评审）等

### 9.3 派发 subagent 的三条铁律（dispatch-protocol.md）

1. **铁律 1**：用 task 工具派发，不自己产出
2. **铁律 2**：给路径不给全文——把输入文件路径给 subagent，让它自己读（上下文隔离）
3. **铁律 3**：subagent 只返回"路径 + 一句话摘要"，主 Agent 拿摘要做门槛判断

### 9.4 阶段卡片驱动（不必全读 8 个协议文件）

按 `agate/AGENTS.md` 指引：每阶段只读对应阶段卡片，卡片自包含：

| phase | 读 |
|-------|-----|
| 启动 | `~/.agate/phase-cards/P0-orchestrator.md` |
| P1 | `~/.agate/phase-cards/P1-requirements.md` |
| P2 | `~/.agate/phase-cards/P2-design.md` |
| P3 | `~/.agate/phase-cards/P3-tdd.md` |
| P4 | `~/.agate/phase-cards/P4-implementation.md` |
| P5 | `~/.agate/phase-cards/P5-verification.md` |
| P6 | `~/.agate/phase-cards/P6-acceptance.md` |
| P7 | `~/.agate/phase-cards/P7-consistency.md` |
| P8 | `~/.agate/phase-cards/P8-release.md` |

卡片查不到的，回退完整协议文件（`~/.agate/WORKFLOW.md`、`dispatch-protocol.md` 等）。

### 9.5 阶段推进的机械动作（每阶段）

1. 写/更新 `.state.yaml`（`phase:` 字段反映刚完成的阶段，**只有下一阶段产出物就绪才推进**）
2. 派发 subagent（方法 B）→ 收"路径+摘要"
3. **亲自跑 gate**：`bash ~/.agate/scripts/check-gate.sh P{n} docs/tasks/{Txxx}`
4. 派发 review subagent（评审角色）→ approved 才推进
5. commit（带 `self-gate-review:`，因改的是协议本体）
6. 更新 active-tasks.md

### 9.6 关键：开发工具用 ~/.agate（v0.35），改造对象是 worktree

- 跑 gate、读卡片、读协议文档：**用 `~/.agate`**（v0.35 稳定版，你的开发工具）
- 改造（改脚本/模板/角色卡）：**改 worktree 里的 `agate/`**
- 跑测试：**worktree 里 `bats`**（自动用 worktree 本体的新代码）
- 阶段产出物（P1-requirements.md 等）：**写在 worktree 的 `docs/tasks/`**，按 v0.35 当前格式写，能过当前 gate

> ⚠️ 注意：P4 实现改的是 worktree 的 `agate/scripts/`（gate 本身）。改完后，你跑 `~/.agate/scripts/check-gate.sh`（v0.35 版）校验阶段产出物——**这正是"用稳定版工具校验改造期产出物"的正确隔离**。新 gate 逻辑的验证由 P3/P5 阶段的 bats fixture 覆盖（在 worktree 里跑）。

---

## 10. 第一步行动清单

1. `cd /home/kity/oclab/agate/.worktrees/v2.0`
2. 确认 `git status` 干净、`git log --oneline -1` = `e5540fc`
3. **确立 orchestrator 角色**（§9）——你是编排者不是实现者：读 §9 的角色配置、派发方式（方法 B）、三铁律、阶段卡片映射
4. 读 `~/.agate/AGENTS.md`（协议本体入口）+ `AGENTS.md`（本仓库开发指引，含 SELF-GATE.md 引用）+ `SELF-GATE.md`
5. 读可行性评估全文：https://peek.gsis.top/mpifxr （完整字段清单在 §1）
6. 按 §6 走 P0 → 写 P0-brief.md → 进 P1
7. 每个阶段产出物按 v0.35 当前格式写，走 gate + 独立评审
8. 阶段间用 task 工具派发 subagent（方法 B，见 §9.2），主 Agent 只写 P0-brief/.state.yaml/active-tasks.md

---

## 11. 参考资料

- 可行性评估全文：https://peek.gsis.top/mpifxr
- 既有 v2.0 Phase1 plan（对象库 `857a5d0`，已过时但含字段清单，`git cat-file -p 857a5d0:docs/plans/agate-v2.0-structured-phase1-20260809.md` 可读）
- `~/.agate/scripts/agate-md-field-get.py` —— 核心改造点（正则 → pyyaml frontmatter + 回退）
- `~/.agate/scripts/agate-state-yaml-check.py` —— frontmatter 校验器范式
- `~/.agate/assets/templates/task-files.md` —— P1/P2 模板（frontmatter 并入点）
