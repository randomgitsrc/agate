# v0.23.0 通用化兼容修复 + dispatch-prompt 持久化自动化

> 起草日期：2026-07-25
> 触发来源：T070 迭代复盘（mcp-server 项目，peek.gsis.top/bmwiz5）指出的两个 agate 问题，经我独立实测复现/证伪后重新诊断
> 编号延续：v0.22.0 用到 P2.44，本计划为 P2.45、P2.46

---

## 零、诊断方法说明（先说清楚"怎么查实的"，再说方案）

T070 复盘对两个问题的**症状描述基本准确**，但**根因诊断都不够准确**——这决定了直接照抄复盘的修复建议会走偏。以下是我的复核过程：

### 0.1 check-tdd-red.sh 不适配 vitest

复盘诊断：vitest 汇总行格式 `Tests  11 failed`（两空格）与脚本的 `[0-9]+ failed` 正则不匹配。

**实测证伪**：
```bash
$ echo "Tests  11 failed | 6 passed" | grep -oE "[0-9]+ failed"
11 failed
```
正则匹配没问题——`grep -oE` 是子串匹配，不要求整行格式对齐，双空格不影响。复盘这个诊断是错的。

**实测找到真根因**：装了真实 vitest（`npm install vitest`），发现问题出在脚本默认值：
```bash
RUNNER_FLAGS="${TEST_RUNNER_FLAGS:--q}"
```
`${VAR:-default}` 在 VAR **未设置或为空字符串**时都会取 default。脚本注释教用户"设置 TEST_RUNNER_FLAGS 覆盖默认值"，但用户最直觉的用法——设成空字符串 `""`——会被 `:-` 悄悄吃掉，照样落回 pytest 专属的 `-q`。而 vitest 根本不认识 `-q`：
```bash
$ npx vitest run -q
CACError: Unknown option `-q`   # 直接崩溃，测试压根没跑起来
```
这不是"正则不匹配"，是"脚本自己文档化的逃生舱不生效"，问题更本质。

**进一步实测发现复盘没提到的第二个缺口**：即使修好 flags 问题，vitest 的 collection-error（import 失败等）输出里没有 `[0-9]+ error` 这种文本（vitest 用 `Failed Suites N` 表达），导致脚本默认的 `ERROR_PATTERN` 永远匹配不到，A/B 分类逻辑对 vitest 项目形同虚设——不光是"漏报 B 类"，我还实测出一个更严重的场景：**A 类错误也会被放过**。

```bash
# 场景：测试文件 import 了一个根本不存在的第三方包（拼写错误，属于 A 类：测试代码自身有问题）
$ import { nope } from 'totally-nonexistent-npm-package-xyz'
$ TEST_RUNNER="npx vitest run" TEST_RUNNER_FLAGS="--reporter=default" PROJECT_MODULE="src/bar" bash check-tdd-red.sh
TDD_CHECK: classic red-light (assertion failures only)
SCRIPT EXIT: 0    # 应该是 1（A 类错误应拦截），实际放行了
```
根因：`ERROR_PATTERN` 匹配不到，脚本走进"无 collection error → 经典红灯"分支，PROJECT_MODULE 的 A/B 判定代码根本没被执行到。

**验证过的可用信号**：vitest 在真正的 collection/import 错误时会输出 `Failed Suites N` 这一行（纯 assertion 失败时不会有这行，实测对比确认），可以作为 `TEST_ERROR_PATTERN` 的 vitest 专属覆盖值。

### 0.2 dispatch-context 模板占比高

复盘诊断：dispatch-context 文件里 77% 是重复模板文本（项目约定/环境隔离/执行顺序/返回格式），建议自动注入进 dispatch-context 文件本身。

**核对协议现有设计**（`dispatch-protocol.md:285`）：
> "主 Agent 在派发前必须为每个 subagent 写好 dispatch-context——这是 subagent 的核心信息源，包含目标、约束、上游关联和输入文件。**dispatch-prompt 只提供跨阶段通用执行纪律，任务特定信息全部在 dispatch-context 中。**"

这一条已经明确把"通用纪律"和"任务特定信息"分成两个不同的载体：**通用纪律该放在 Task 工具调用的 prompt 文本里，不该抄进 dispatch-context 文件**。如果 T070 的 dispatch-context 文件里真的塞了 77% 的通用纪律，那是主 Agent **执行时没有遵守协议已有规定**，而不是协议本身缺一道机制。

但我认为**不能简单归为"执行纪律问题，加一句提醒就完事"**，因为这里有一个协议设计本身确实存在的空当：**Task 工具调用的 prompt 文本不落盘、不进 git、事后不可审计**。而 agate 的核心设计哲学（`LIMITATIONS.md` 反复强调）就是"一切经过校验的事实都要有可追溯的书面记录"。主 Agent 在 T070 里把通用纪律抄进文件，很可能不是不懂协议，而是本能地想要一份可审计的留痕——协议目前没有提供这份留痕的正规渠道，逼得主 Agent 用"文件里全量复制"这种笨办法自己造一个，代价是每次手打。

**结论**：真正该修的不是"dispatch-context 文件该不该塞模板"（协议已经说清楚不该），而是"**通用纪律需要一份持久化、可审计的记录，但这份记录不该占用 dispatch-context 文件的语义**"。方案见下方 P2.46。

---

## P2.45：check-tdd-red.sh 通用化兼容修复

### 改动 1：修复 RUNNER_FLAGS 默认值吞掉空覆盖的 bug

```diff
- RUNNER_FLAGS="${TEST_RUNNER_FLAGS:--q}"
+ RUNNER_FLAGS="${TEST_RUNNER_FLAGS--q}"
```
去掉冒号：只在变量**完全未设置**时才用默认值 `-q`；显式设成空字符串会被尊重。不影响现有 pytest 项目行为（这些项目通常压根不设置 TEST_RUNNER_FLAGS，变量是"完全未设置"状态，走的还是默认值分支）。

### 改动 2：补充 vitest 适配示例到脚本头部注释

在现有"=== 通用性说明 ===" 注释块里，追加一段"已验证的非 pytest runner 适配示例"，给出 vitest 的具体配置（实测验证过，不是理论推测）：
```bash
# vitest 项目示例（已验证）：
#   TEST_RUNNER="npx vitest run"
#   TEST_RUNNER_FLAGS="--reporter=default"   # 必须显式设置为非 -q 值，vitest 不识别 -q
#   TEST_ERROR_PATTERN="Failed Suites [0-9]+"  # vitest 的 collection-error 摘要不含 "N error" 文本
#   PROJECT_MODULE="{项目内模块前缀}"
```
不改脚本核心逻辑去"硬编码支持 vitest"——这违反"通用协议不为某个技术栈定制"的初衷。只是把验证过的适配参数记录下来，供其他非 pytest 项目参考同样的思路自己配置。

### 改动 3：新增 bats 测试，用固定文本 fixture 覆盖三个此前未测的场景

不真实调用 npx vitest（拖慢测试、引入网络依赖），用固定文本模拟 vitest 的三种真实输出（均来自本次实测截获的真实输出，不是编造）：

| 测试 | 场景 | 断言 |
|------|------|------|
| TDD.N1 | `TEST_RUNNER_FLAGS=""` 时不落回 `-q` | 复用现有 `make_fake_pytest` 模式，改造成会把收到的完整参数列表写入哨兵文件的 mock runner（用 `printf '%s\n' "$@"` 记录参数，避免 word splitting）；断言哨兵文件内容不含 `-q`。另加一条对照用例：完全不设置 `TEST_RUNNER_FLAGS`（不是设空，是不设）时哨兵文件里仍然有 `-q`——确认没改坏现有 pytest 项目的默认行为 |
| TDD.N2 | vitest 纯 assertion 失败（无 Failed Suites 行）| exit 0，经典红灯 |
| TDD.N3 | vitest B 类（import 目标是 PROJECT_MODULE 内） | 设置 `TEST_ERROR_PATTERN="Failed Suites [0-9]+"` 后，exit 0，B 类红灯 |
| TDD.N4 | vitest A 类（import 目标不是 PROJECT_MODULE 内，如拼错的第三方包名）| 设置 `TEST_ERROR_PATTERN` 后，exit 1，A 类错误 |

TDD.N4 尤其重要——这是本次实测发现的、复盘完全没提到的"漏报"场景，必须有测试锁定，防止以后回归。

### 测试计划
- P2.45：改脚本 + 4 条新 bats（TDD.N1-N4）+ 全量 bats/consistency/shellcheck 回归

---

## P2.46：dispatch-prompt 持久化自动生成（不改动 dispatch-context 文件语义）

### 设计原则

1. **不把通用纪律塞进 dispatch-context 文件**——维持 `dispatch-protocol.md:285` 现有的"dispatch-context 只放任务特定信息"的边界，避免这次修复反而把边界搞模糊
2. **新增一个独立文件类型**，专门承载"本次派发实际发给 subagent 的完整 prompt 文本"的持久化副本，与 dispatch-context 语义上分开
3. **一份内容，两处使用**：渲染出来的文本，既是主 Agent 调 Task 工具时实际传的 prompt，也是落盘存档的记录——不是"先手写 prompt，再誊抄一份存档"，避免二次输入和两份内容漂移的风险

### 命名说明（避免与现有 `dispatch-prompt.md` 混淆）

`agate/assets/templates/dispatch-prompt.md` 是**协议模板文件**（一份，全局共用，本次不改动其内容）；新增的 `P{N}-dispatch-prompt-{role}.md` 是**某一次具体派发的渲染实例**（每次派发一份，落盘在任务目录下）。两者名字相似但不是一回事——这个命名相似容易造成误解，实现时必须做到：
1. 脚本注释和文档里明确写清楚这个区别
2. 渲染产物文件头部自动插入区分性注释行：`> 本文件是 agate-render-dispatch-prompt.sh 的渲染产物，不是协议模板。修改本文件不会影响模板。`

### 新文件：`P{N}-dispatch-prompt-{role}.md`

- 由新脚本 `agate-render-dispatch-prompt.sh P{N} {role} TASK_DIR [--rollback]` 生成
- 输入：读取 `dispatch-prompt.md` 模板的通用纪律块 + 该阶段对应的"阶段特定提示"追加块
- **追加块选择逻辑（按阶段名 ≠ 一一对应，需要额外判断）**：`dispatch-prompt.md` 里的追加块不是单纯按 `P{N}` 数字选择的——"P4 派发追加"和"P4 回退派发追加（P5/P6 失败回退时使用）"是两个互斥的独立小节，都挂在 P4 下，选哪个取决于"这次派发是不是从 P5/P6 失败回退回来的"，不是 PHASE 参数本身能区分的。脚本必须接受一个显式的 `--rollback` 标志：`PHASE=P4` 且不带 `--rollback` → 选"P4 派发追加"；`PHASE=P4` 且带 `--rollback` → 选"P4 回退派发追加"。其余阶段（P2/P5-P6/P8）没有这个分叉，`--rollback` 对它们无效果（忽略即可）
- 占位符替换：`{Txxx}`（从 TASK_DIR 目录名取）、`{Pn}`（PHASE 参数）、`{角色名}`（role 参数）、`created` 日期等
- 输出：渲染后的完整文本，同时：
  - 写入 `docs/tasks/{Txxx}/P{N}-dispatch-prompt-{role}.md`（持久化存档）
  - 打印到 stdout（主 Agent 直接复制这段文本作为 Task 工具调用的 prompt，不再手打）
- **可选，非强制**：这是效率工具，不新增 gate 硬约束。不用这个脚本、继续手写 prompt 也完全合法——避免给现有工作流引入新的阻塞点。**已知残余风险**：不用脚本时 prompt 文本仍不落盘、不可审计，这是当前协议的既有局限，本次不解决

### 上下游影响范围排查（逐项核实，非假设）

新增的 `P{N}-dispatch-prompt-{role}.md` 文件名匹配现有 `P[0-8]-*.md` 通配模式，会被以下**已存在**的脚本扫描到，需要同步处理，否则会产生噪音或误判：

| 脚本 | 现状行为 | 需要的改动 |
|------|----------|-----------|
| `check-p6-provenance.sh:240-246` | 扫描所有 `P[0-8]-*.md` 检查 `agent:` 字段是否存在，缺失则 WARNING（exit 2，不阻塞）。现有排除列表含 `*-dispatch-context.md\|*-dispatch-context-*.md\|*-progress.md\|*-paused-resolution.md` | 排除列表追加 `*-dispatch-prompt-*.md`——这是主 Agent 生成的编排文件，不是 subagent 产出，不该被要求有 `agent:` 字段 |
| `check-retrospective.sh:37` | `basename "$f" \| grep -q 'dispatch-context'` 跳过编排类文件 | 改成 `grep -qE 'dispatch-context\|dispatch-prompt'`，否则复盘检查会把这个新文件当成阶段产出误扫 |
| `check-scope-resolved.sh:19` | 同上，同样的 `grep -q 'dispatch-context'` 排除逻辑 | 同上改法，否则 SCOPE+ 扫描会把模板文本误当成阶段产出（虽然模板文本本身不含 `[SCOPE+]` 字面量，实际触发概率低，但排除逻辑本该覆盖到，不留隐患） |
| `check-pruning.sh:131` | 检查被声明裁剪的阶段是否仍有 `${phase}-*.md` 产出，矛盾则报错 | **不需要改**——新文件只在阶段被实际执行、派发 subagent 时才会生成，与"该阶段被裁剪"互斥，不会触发误判，核实过不需要动 |
| `pre-commit-gate.sh` 的 phase-span 检测（97-103/260/308-339 行，按文件名 `P[0-8]` 前缀识别文件属于哪个阶段）| 按前缀识别阶段归属，用于检测跨阶段混提交 | **不需要改**——新文件名前缀正确带 `P{N}`，会被正确识别为该阶段的文件，行为本身是对的 |
| `agate-extract-context.sh` / `agate-inject-card.sh` | 只认 `*-dispatch-context-*.md` | **不需要改**——两者职责不同，不应该处理 dispatch-prompt 文件 |
| `check-gate.sh:142` | P4 gate 用 `grep -qvE '(^|/)P[0-8]-.*\.md$|(^|/)\.state\.yaml$'` 检查暂存区是否有非 md/yaml 代码文件 | **不需要改**——新文件 `P4-dispatch-prompt-*.md` 匹配 `P[0-8]-.*\.md$`，会被正确排除，不影响 P4 gate 的代码文件检测 |

### 测试计划
- P2.46：新脚本 `agate-render-dispatch-prompt.sh` 本身的 bats，覆盖：
  - 占位符替换正确（`{Txxx}`/`{Pn}`/`{角色名}`/日期）
  - P2/P5-P6/P8 按 PHASE 正确选中对应追加块（注：P5/P6 共享同一个追加块，不存在"按 PHASE 选中不同追加块"的逻辑）
  - **P4 不带 `--rollback` 选"P4 派发追加"（正向测试，锁定默认行为），带 `--rollback` 选"P4 回退派发追加"，两者互斥、内容不混入**（这是本轮自评审发现的机理缺口，必须有测试锁定，防止选错追加块导致回退派发缺失"强制先诊断根因"这条关键纪律）
  - role 含特殊字符时的文件名安全性
- 3 处排除列表改动各补 1 条回归测试（构造一个 `P4-dispatch-prompt-implementer.md` 文件，验证 `check-p6-provenance.sh`/`check-retrospective.sh`/`check-scope-resolved.sh` 都不会对它做出阶段产出类的判定）

---

## 不做的事

| 事项 | 理由 |
|------|------|
| 把 vitest（或其他任何非 pytest runner）硬编码进 check-tdd-red.sh 核心逻辑 | 违反"通用协议不为技术栈定制"的初衷，脚本仍然只是 pytest 参考实现 + 可配置契约，vitest 只作为验证过的配置示例出现在注释里 |
| 让 `P{N}-dispatch-prompt-{role}.md` 成为新的强制 gate 项 | 这是效率/审计留痕工具，不是协议正确性的必要条件；强制会把一个可选改进变成新的阻塞风险点，且目前只有 T070 一个复盘样本支持这个需求，先做成可选工具观察实际使用情况再决定是否升级为强制 |
| 修改 dispatch-context 文件本身的既有语义或格式 | 协议现有边界（dispatch-context 只放任务特定信息）本身是对的，问题出在"通用纪律没有持久化渠道"，不该通过混淆 dispatch-context 的语义来解决 |
| 重构 check-tdd-red.sh 的 A/B 分类核心算法 | 本次只补 vitest 场景下 ERROR_PATTERN 不匹配这一个具体缺口，不是要重新设计整个 A/B 判定机制 |

---

## 验收标准

- P2.45：4 条新 bats 全过，尤其 TDD.N4（此前完全没有测试覆盖的漏报场景）；改动前用真实 vitest fixture 复现过的 bug（flags 崩溃、A 类漏判）改动后不再复现
- P2.46：新脚本渲染出的 prompt 文本与 `dispatch-prompt.md` 模板手工替换占位符后的结果逐字节一致（防止渲染逻辑引入内容漂移）；3 个排除列表改动均有回归测试锁定
- 全量 bats + consistency + shellcheck 通过
