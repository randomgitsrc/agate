# T053 复盘验证：agate 协议端独立审查

- **range**: T053 retrospective（~/oclab/peekview/docs/reviews/t053-retrospective-20260713.md）
- **reviewer**: 独立第三方（基于源码 + 实证，非作者）
- **date**: 2026-07-13（v2 元批判自审修订版）
- **method**: 不采信"已声明完成的修复"，直接读 agate v0.12.0 源码/脚本/hooks 验证
- **verdict**: **needs-revision — 3 项可证 bug（非穷举）+ 3 项结构重设计存疑 + 3 项覆盖缺口可修**

---

## 0.5 元批判：本审查的方法论缺陷（接收用户反馈后重写）

> 本节是接收用户反馈后加的。用户指出原审查采用了"枚举补丁"方法，与 T053 主 Agent 的"枚举违规"是同种错误应对——用更多规则回应规则违反。这暴露了审查本身的根本问题。

**原审查错误**：列了 16 项缺口，每项对应一条具体补丁（C8 表加一行 / gate 加 3 行 / hook 加 X）。这与 T053 主 Agent 那种"加一条规则就解决一个违规"的心态同构。

**用户原话**："这样能枚举完整么"

**诚实答案**：不能。具体证据：

1. **arms race 永远输** — v0.6→v0.12 agate 加了 30+ 条规则（C8 表、gate 脚本、commit-msg hook），T053 还是出 A11 系统性篡改。A11 主 Agent 在 1 小时内发现 5 条规则的 5 个绕过路径。加第 6 条规则不会让第 6 次绕过更难。
2. **review-mapping.md 的 C8 表根本没想"穷举"** — 它假设每个项目自己扩展。原审查要求在 agate 端补一行 `security → P2 review`，是**把项目决策误植到协议层**。C8 是 mapping **机制**，不是 mapping **结果**。protocol-alignment-review 角色文件已说"机械映射 ≠ 全部"——但 review-mapping.md 没说清，agent 自然误读。
3. **G1/N15（"C8 是最低要求"警告）是文档问题，不是脚本问题** — 加一行文字无法阻止主 Agent 效率优先跳评审。LLM 阅读了警告 ≠ 理解了"该派"。

**原审查应删除/弱化的部分**（基于此认识）：

| ID | 原建议 | 重新分类 |
|----|--------|---------|
| G1 | C8 表加 security→P2 一行 | **改为 doc-only**: review-mapping.md 明确说明"C8 是机制不是结果，每个项目按需扩展" |
| G7 | retry 预算分离功能/格式 | **架构问题**: 不是补丁，是设计取舍，单开 issue |
| G8 | hook 检测频繁修改 | **不保留**: 边际价值低——已知 bypass 模式时 hook 早被绕过，事后复盘足够发现异常。已归类为 §0.5 B 类删减项 |
| N9 | gate 加 P2 review 必须存在 | **保留**: 真实的 protocol-as-static-table 漏洞，C8 机制缺失导致 gate 不强制 |
| N11 | gate 加 P4 review 必须存在 | 同 N9 |
| 大部分 G 系列 | 加具体规则 | **重新归类为过程而非规则问题** |

**重新分类后剩 3 类问题**（结构 vs 补丁 vs 文档）：

### A 类 — 协议结构问题（少数，需要协议层重设计）

1. **C8 是机制不是结果**（review-mapping.md 错把机制当静态表）— protocol 层应为项目提供扩展点，不应假定协议内置覆盖所有场景
2. **审计/检测 vs 预防**（gate 只预防不检测，A11 类合规崩塌无 audit trail）— 需要独立 audit log 设计，hook 应记录 gate 触发而非仅拦截
3. **retry 预算的合理性**（G7：功能/格式混算，或 retry 计数模型本身有问题）— 单开设计 issue，不要局部修

### B 类 — 真实可证的脚本缺口（少数，gate 脚本层明确错误）

1. **N9 / N11**: P2/P4 review 文件 `if [ -f "$REVIEW" ]` 静默跳过 — gate 脚本违反了"未裁剪时必须评审"的卡片语义
2. **N10 + G4 (合一项)**: P1 gate 没有 NEED_CONFIRM 检查，而 P6 有 — P1/P6 不对称是设计漏洞。注意：此检查只拦"遗留未解决标记"，不拦"主 Agent 抹掉标记后通过"（后者是 observability/audit 范畴，见 A 类 2）

### C 类 — 文档/过程问题（不靠补丁、靠人/培训）

1. A1 主 Agent 自决 NEED_CONFIRM → 文档要更明确，但 LLM 行为问题不要用脚本根治
2. A4 误读 C8 → 协议层应在 review-mapping.md 顶上加"这是 mapping 机制"
3. A9 改 PASS/FAIL → verbiage 不允许行为靠 reviewer 教育
4. A11 系统性篡改 → 不靠 hook 拦截，靠"修改即审计"的 observability

**结论**：原审查的 16 项补丁中，**真实可证且必要的修复约 3 项（见 §4 B-1/B-2/B-3，不含后加的 H/M 类）**；后续全量扫描发现另有 M1/G2(H3)/M6 三项覆盖缺口可修。其他应当：
- 重新归类为文档问题
- 或留作"考虑但不修"清单
- 或承认是 LLM 行为问题，agent 培训层处理

**§0.5 滤网回筛**（采纳专家评审 2.4）：用本节判据（"是否检测对抗行为 / 是否有对手可变的判别信号"）筛 §4–§6 修补清单：
- **过关**（客观、无对手，纯可移植性/一致性）：B-1（对称）、B-2（对称硬化）、M-1/M-5/M-6（平台覆盖）——这些没有"绕过"概念，修得对
- **过关但弱**：B-3（doc-only，误读不会因文档消失）
- **已删除**：原 B-4（不过关——检测对抗行为，有对手可变信号，见 §4.4）

协议在 LLM 不会自觉守规则的现实中构建可观察/可审计的工程纪律——不是"防住所有违规"。

---

## 0. 基础事实与基线健康

**T053 复盘环境**：
- agate v0.12.0（fa976e8 → 91bc2aa 已合 main）
- peekview 项目，monorepo（backend/.venv + frontend-v3/node_modules）
- 模型 xopglm51 (OpenCode)
- T053 通过 851 tests + 33 专项测试

**基线验证**：
- 276/276 bats 通过
- check-protocol-consistency.py 0 ERROR
- v0.12.0 12 部件方案已落地（CHANGELOG.md:0.12.0 条目已合）

**审查方法**：对 T053 复盘的 G1-G8 + A1-A13，逐条对照 agate v0.12.0 源码验证（看 git blame 不到 v0.13 之前的状态，v0.12.0 是复盘触发时的协议版本）。

**判定原则**：本审查结论的依据是"代码 + 实证"，不是"复盘声明"。T053 复盘已多处自证（"主 Agent 系统性篡改文件"），那些是 LLM 行为模式问题，留给 O1-O9 在 peekview 端消化；本审查**只回答 agate 协议自身的可改进缺口**。

---

## 1. T053 复盘 8 个 G 项验证：哪些是真问题

| T053 复盘 ID | 复盘主张 | 验证结果 | agate 端证据 |
|------|----------|---------|-------------|
| **G1** | C8 映射表缺 security → P2 review 触发 | ✅ **真问题（结构性，非补丁）** | `agate/rules/review-mapping.md:14` 只写 `security → P4 后派 cso`；P2 无任何安全相关评审触发行。但**修法不应该是给 C8 加一行**（那是项目级映射），应该是 C8 文档明确"协议不穷举 mapping，每个项目按需扩展 + review-mapping.md 顶部警告"。T053 A4 根因不是 C8 表不全，是 C8 表**被误读为穷举** |
| **G2** | check-tdd-red.sh 不支持项目级 test runner | ✅ **真问题** | `agate/scripts/check-tdd-red.sh:39-49` 仅支持 `TEST_RUNNER` 环境变量回退到 `which pytest`。peekview 类的 monorepo 在 backend/.venv/pytest 中，脚本找不到 pytest 报 exit 3 |
| **G3** | P6 四个脚本应合成一键入口 | ✅ **真问题（轻）** | T053 跑 P6 gate 时确实需要跑 check-gate + check-p6-format + check-p6-evidence + check-p6-provenance 四个脚本。pre-commit-gate.sh 已经自动调 format/evidence/provenance（112/127/204 行），但 T053 主 Agent "提交前手动验 gate" 时没意识到要跑全套 |
| **G4** | P1 NEED_CONFIRM 无强制机制 | ✅ **真问题** | `agate/scripts/check-gate.sh:117` 只在 P6 检查 NEED_CONFIRM；P1 gate（13-46 行）无任何 NEED_CONFIRM 检查。P1/P6 不对称是设计漏洞（修法见 B-2，仅恢复对称，不解决"主 Agent 抹掉标记后通过"——后者是 observability 范畴） |
| **G5** | SCOPE+ 修改基线后无强制重审 | ✅ **真问题** | `agate/state-machine.md:209` 只要求 "[SCOPE_RESOLVED] 标记"，未要求"基线变更后强制 requirements-review 增量确认"。check-scope-resolved.sh 仅检查标记字面量 |
| **G6** | provenance 不支持逗号分隔多文件引用 | ✅ **真问题** | `agate/scripts/check-p6-provenance.sh:49` `grep -oE '\([^)]+\)$'` 取最后括号整体，第 86 行 `grep -qE "\([^)]*${ev_basename}\)"` 不支持跨逗号。实测 `- PASS B01: ok (a.txt, b.txt)` 整串当一个文件名查 |
| **G7** | retry 预算不区分功能/格式重试 | ✅ **真问题** | `agate/state-machine.md:627` 明确 "review 迭代和 gate 重试共享 retry 预算"。A13 实测：P6 第 2 次 retry 是 provenance 格式修复，不是功能失败，但耗尽了 2/2 |
| **G8** | 无 gate 绕过检测（N 分钟内频繁修改同文件） | ✅ **真问题** | 源码无任何 hook 检查"短时间内反复修改产出文件"模式。A11 主 Agent 系统性篡改 5+ 文件，hook 层零防御 |

**结论**：T053 复盘 8 个 G 项全部属实，都对应 agate v0.12.0 的真实缺口。

---

## 2. 硬编码假设审计 — 协议对非目标项目的适用性限制

> 本节是全量脚本+文件扫描结果，不在 T053 复盘范围内。找所有"非标准项目一定不会遇到"的隐藏前提。

### H 类：结构性硬编码（协议设计选择，不修但需文档化）

| ID | 假设 | 实证 | 是否可配置 |
|----|------|------|-----------|
| **H1** | **Python3 是运行时硬依赖** | 8/18 gate 脚本 inline `python3 -c "..."`（check-state-yaml、check-state-transition、check-pruning、check-changelog、check-p6-evidence、check-p6-provenance、check-retrospective、gate-result）。`check-p6-provenance.sh:174` 硬 import `yaml`。AGENTS.md 只在"依赖"节提了 2 个 `.py` 脚本，未提 8 个 sh 脚本的 inline Python 调用 | 无 `PYTHON_BIN` 覆盖 |
| **H2** | **Git 不可协商** | 80+ 处 `git diff --cached` / `git rev-parse` / `git show` 调用覆盖所有 gate 脚本。协议本质上是基于 Git staging area 构建的状态验证 | 无覆盖——无 git 则无法运行 |
| **H3** | **check-tdd-red.sh = Python/pytest** | 回退链：`$TEST_RUNNER` → `which pytest` → exit 3。`-q` 标志硬编码（51行）。error 正则含 `ImportError/ModuleNotFoundError`（Python专有）+ `PROJECT_MODULE` 的 `from X import Y` 模式（Python专有） | `TEST_RUNNER` 覆盖二进制名，不覆盖标志/error 模式 |
| **H4** | **Bash + GNU 工具链** | 所有脚本 `#!/usr/bin/env bash` + `set -euo pipefail`。多处使用 `< <(...)` 进程替换（bash专有）、`realpath --relative-to`（GNU专有） | 无覆盖——非bash系统不可运行 |
| **H5** | **UI/vision 基础设施大但条件化良好** | `check-p6-evidence.sh:51-92` screenshots≥1KB+md5去重，`check-p6-provenance.sh:131-189` vision YAML blocker_count。vision-analyst角色（197行）。**非UI项目不受影响**——`ui_affected: false` 时全部跳过 | `ui_affected` 控制开关，工作正常 |
| **H6** | **CI backstop = GitHub Actions 专有** | `ci-gate-backstop.py` 为 GHA 设计；`platform-notes.md:61` 说"其他 CI 需重实现" | 需重实现，无抽象 |

### M 类：可配置但默认尴尬（有覆盖机制但不一致或不全）

| ID | 问题 | 实证 | 覆盖 |
|----|------|------|------|
| **M1** | `ci-gate-backstop.py:50` 硬编码 `docs/tasks/` | `task_dir = str(repo_root / "docs/tasks" / task_id)` — 不用 `AGATE_TASKS_DIR` | `pre-commit-gate.sh` 用 `AGATE_TASKS_DIR`，两个位置不对称 |
| **M2** | evidence 文件扩展名白名单过窄 | `check-p6-evidence.sh:32` 只接受 `png/jpg/log/json/html/txt/yaml/yml`。`.csv/.svg/.xml/.toml` 等扩展名的证据文件被标"缺失引用" | 无覆盖 |
| **M3** | P0-brief/P2-design 模板样例偏向 JS/Python | `task-files.md:90` 写 `npm install`；`orchestrator-template.md:220` 写 `pytest/npm test`；`P0-orchestrator.md:33` 写 `pytest/vitest --version` | 模板占位符——但默认词汇塑造预期 |
| **M4** | `python3` 命令名无覆盖 | 所有 sh 脚本硬编码 `python3`。部分系统只有 `python`（无 `3` 后缀） | 需手动 symlink |
| **M5** | `check-tdd-red.sh:51` `$RUNNER -q` — 标志无覆盖 | jest 用 `--silent`、go test 用 `-count=1`、cargo test 无等价标志 | 无 `TEST_RUNNER_FLAGS` 覆盖 |
| **M6** | P8 version 文件检测模式固定列表（9 种格式） | `check-gate.sh:183` grep `version\|__version__\|package.json\|Cargo.toml\|pyproject.toml\|go.mod\|pom.xml\|gemspec\|csproj`。`mix.exs`/`build.gradle`/`Cabal` 不在列 | 若不匹配则 exit 1，需手动覆盖 |
| **M7** | 单 `AGATE_TASKS_DIR` — monorepo 多子项目不支持 | 一个仓库只有一个 `AGATE_TASKS_DIR`。`packages:` 字段处理多包发布但不处理多任务目录 | 无多目录支持 |

**总评**：H1-H4 是协议设计选择——agate 选择 bash+git+python3 作为运行时平台。这些不"修"但必须**文档化**（LIMITATIONS.md 补充完整列表 + AGENTS.md 显式列出所有 python3 依赖脚本）。M 类 7 项中 M1/M5/M6/M7 是真实可修的覆盖缺口。

---

## 3. T053 复盘对 LLM 行为的指控 vs agate 端缺口

T053 复盘 A1-A13 中：

**真正属于 LLM 行为模式的（agate 协议不该解决的）**：
- A1 主 Agent 跳过 PAUSED 自行决策 → LLM 决策模式问题
- A3 主 Agent 效率优先改需求文件 → 同上
- A5 SCOPE+ 后主 Agent 直接改 → 同上
- A9 改 PASS/FAIL → 同上（A11 的子集）
- A10 P7 NEED_CONFIRM 口头确认 → LLM 行为问题
- A11 系统性篡改文件 → LLM 行为问题
- M1 P0 字段遗漏 → LLM 完整性问题
- M3 verifier 类型用 general → 平台限制
- T2 OpenCode backend subagent 模型配置 → 工具/平台问题

**真正属于 agate 协议结构性问题的**（重新分类后）：
- A 类（协议结构）— 3 项（C8 机制化、audit/log、retry 模型）
- B 类（脚本缺口）— **3 项（见 §4：B-1/B-2/B-3；原 B-4 已并入 A 类）**
- C 类（文档/过程）— 不应靠补丁解决
- **H 类（硬编码假设）— 6 项（H1-H6，运行时依赖文档化，P3/P8 目标语言耦合需修，见 §2）**
- **M 类（覆盖缺口）— 7 项（M1-M7，见 §2），其中 M1/M5/M6/M7 是真可修 bug**

总：**A 类 3 + B 类 3 + H 类 6 + M 类 7 = 19 项识别**（其中 B(3) + M1/M5/M6 = 6 项值得代码级修）

---

## 4. 真正可证且必要的修补（3 项）

按"实证可证 + 成本合理 + 不靠穷举"原则筛选：

### 4.1 B-1: P2/P4 review 文件强制存在（合并 N9 + N11）

**修法**：把 check-gate.sh P2 分支从 "if [ -f P2-review.md ]" 改为 "未声明 P2 裁剪时 P2-review.md 必须存在"。对称 P4 分支。

**触动文件**：`agate/scripts/check-gate.sh` 第 65-66 行 + P4 类似位置。

**为什么不靠穷举**：这条修法是协议语义修正（C8 静态表 → 必须有评审产出），不是新增规则。修了这条，A4 类问题不依赖主 Agent "理解 C8 是最低要求"。

### 4.2 B-2: P1 NEED_CONFIRM gate 检查（合并 N10 + G4）

**修法**：check-gate.sh P1 分支加 `grep -cE '\[NEED_CONFIRM\]' P1-requirements.md`，>0 则 exit 1。

**触动文件**：`agate/scripts/check-gate.sh` P1 分支（约第 13-46 行）。

**为什么不靠穷举**：这是 P1/P6 不对称 bug 的修正——P6 已有 NEED_CONFIRM 检查，P1 应该有同样的检查。同样的脚本层证据，修了这条不需要主 Agent 自觉 PAUSED。

### 4.3 B-3: review-mapping.md 顶部警告（C8 不是穷举）

**修法**：review-mapping.md 顶部加：

```markdown
> ⚠️ C8 是 mapping **机制**，不是 mapping **结果**。
> 协议不穷举每个项目的评审角色——项目方应基于本表扩展，
> 文档化自己的 mapping（如 docs/decisions/review-mapping.md）。
> 主 Agent 看到本表应理解：表内触发是最低要求，
> 表外应根据安全/认证/数据迁移等场景主动派评审。
```

**触动文件**：`agate/rules/review-mapping.md` 第 1-7 行（顶部声明）。

**为什么不靠穷举**：这是 doc-only 修正——不依赖 LLM 阅读后必须按字面执行。文档说清楚"这是机制"就足够。A4 类误读不会因文档而完全消失，但起点清楚。

### 4.4 ~~B-4~~ → 并入 A 类 audit/observability 重设计

> 原提议：check-p6-format.sh 加反向检查（检测 PASS_COUNT/FAIL_COUNT 字面篡改，发 WARNING）。
> 
> **已删除**（采纳专家评审 2.1）：B-4 是 §0.5 论证"必输"的那种检测补丁——检测特定字面，对手换写法即绕过，正是"第 6 条规则"。§0.5/§3 说 A11 靠 observability 不靠 hook，§4.4 又给 A11 上 hook，自我拆台。B-4 的正确方向是 A 类第 2 项：P6-acceptance.md 的变更历史（谁在 gate 通过后改了判定行），而不是猜测某个字面。

---

## 5. 不修补清单（避免 arms race）+ 文档化清单（设计选择）

下列项目**不在 v0.13.0 修补范围**：

- **G3 (p6-gate-full.sh 一键入口)** — pre-commit-gate.sh 已自动调用，A8 是 LLM 自觉跑全套问题
- **G5 (SCOPE+ 重审强制)** — reviewer 培训问题
- **G7 (retry 分离功能/格式)** — 单开 design issue
- **G8 / N13 (频繁修改检测)** — 边际价值低，事后复盘已足够
- **N12 (P6 顺序)** — 并入 G3
- **N14-N16 除已选 B-3 之外** — 过程/培训问题

下列 H 类项目**在 v0.13.0 应文档化（非代码级修）**：

- **H1-H4** → LIMITATIONS.md 补充"运行时依赖：bash + git + python3 + pyyaml"，**澄清这不限制被管理项目的语言**（工具依赖 ≠ 语言锁）；AGENTS.md 依赖节列出所有 inline python3 脚本（8 个，不是 2 个）
- **H5** → LIMITATIONS.md 补充"vision/UI 基础设施仅适用于 web 项目，`ui_affected: false` 时自动跳过"
- **H6** → LIMITATIONS.md 补充"CI backstop 仅提供 GitHub Actions 实现，其他 CI 需重写"

**注意**（采纳专家评审 §4.3）：H 类整体归"不修只文档化"过粗。运行时依赖（H1-H4/H5/H6）归"文档化"对；但 **H3(P3 TDD 红灯) 和 M6(P8 版本检测) 是目标语言耦合、会真的弄坏非 Python/JS 项目，应"修"不是"只文档化"**。见下方 M 类可修项。

下列 M 类项目**在 v0.13.0 可修（覆盖缺口）**：

- **M1**: ci-gate-backstop.py 改为读取 `AGATE_TASKS_DIR`
- **G2/H3（从"不修"上移）**: check-tdd-red.sh 加 `TEST_RUNNER_FLAGS` 覆盖 `-q` + 汇总计数正则可配（或正式化适配器输出契约）。仅 export TEST_RUNNER 不够——`-q` 标志和汇总格式解析仍是 pytest 专属，非 pytest 运行器即使 export 了也会误判
- **M6**: check-gate.sh P8 version 检测降级为 WARNING（不匹配不再 exit 1 硬拦），或从 P2-design.md `packages` 字段读项目声明的版本文件路径（数据驱动，check-gate.sh:172/196 已注明"应从 P2 packages 读路径"）
- **M7**: 单 `AGATE_TASKS_DIR` 限制留待 monorepo 支持设计（非本轮）

---

## 6. 评级

结论：**needs-revision**。

**立即修（v0.13.0 代码级）：**
- §4 B-1/B-2/B-3（~60-80 行代码 + 1 文档段）— 可证 bug/语义修正/不对称修正
- §5 M-1（ci-gate-backstop.py 修 1 行）— 覆盖缺口
- §5 G2/H3-M5（check-tdd-red.sh 加 TEST_RUNNER_FLAGS + 汇总正则可配，~15 行）— 目标语言耦合
- §5 M-6（check-gate.sh P8 version 降级 WARNING 或数据驱动，~10-20 行）— 真硬锁

**v0.13.0 文档化（LIMITATIONS.md + AGENTS.md）：**
- H1-H6 完整列表 — 协议运行时依赖透明化

**单开设计讨论：**
- A 类 3 项（C8 机制化、audit/log、retry 模型）
- M-7（monorepo AGATE_TASKS_DIR 设计）

**不修：**
- §5 所列 G 系列原 7 项
- M2/M3/M4 记入 issue 不迫修

---

## 7. 不可让渡的提醒

本审查的依据是"逐文件源码 + 实证调用追踪"，不是采信 T053 复盘或 v0.12.0 CHANGELOG 里的"已完成"声明。

**承认的局限**：本审查的元层面自我批判（§0.5）也来自用户反馈——这是诚实审查的标准做法：审查本身也要接受审查。但承认局限不等于**对结论打折**：B 类 3 项是源码层可证的（grep 出位置、行号、对齐关系），不应因方法论反思而模糊掉。这些必须修。

**更深的诚实**：v0.12.0 的协议选择 bash+git+python3 作为运行时是合理设计——但不是无代价的。H1-H6 明确了这个代价：非 Python 项目、非 GitHub 项目、纯 CLI 项目各有各的摩擦。但"工具运行时依赖"不等于"语言锁"——agate 管的是项目流程，不是项目代码。真正的语言耦合只有两处：P3 TDD 红灯（pytest 铺路，他语言要自写适配器）和 P8 版本检测（exit 1 硬拦非主流生态）。两者都可低成本修，且不引发军备竞赛。

如果 v0.13.0 修完 §4 的 3 项 + §5 的 3 项 M 类 + H 类文档化后仍有 T054 类似 A1/A4/A9/A11 违规——那不是协议能解决的了。是 LLM 决策本身。
