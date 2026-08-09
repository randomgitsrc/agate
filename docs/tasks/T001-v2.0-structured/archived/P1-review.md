---
phase: P1
task_id: T091
type: review
parent: P1-requirements.md
trace_id: T091-P1-20260809
status: approved
created: 2026-08-09
agent: requirements-review
---

# T091 — P1 需求基线评审（requirements-review · 复审轮）

> 被评审对象：`docs/tasks/T091-v2.0-structured/P1-requirements.md`（FIND-1/2/3/4 修复后版本）
> 评审输入：P0-brief.md、P1-dispatch-context-requirements-review.md、P1-dispatch-context-analyst-fix.md、P1-review.md（上轮）、P1-progress.md（修复轮落盘）、HANDOFF-V2.0.md
> 评审方式：逐项复核上轮 FIND 闭环 + 全量重审（worktree 只读客观查证）

## 1. 评审摘要

上轮 4 项 FIND（1 主要 + 2 次要 + 1 建议）**全部闭环**，客观查证与文档声明一致。全量重审未发现新的 BDD 矛盾、语义真实性越界或 scope 越界。**结论：approved**。

- FIND-1（判别契约）：§3 隐含需求 1 补入判别契约 + BDD-6 Given 收紧 ✓
- FIND-2（37 条）：全文"33 条"清除，BDD-13/F10/§3-3 均改为 37 条，AST 实测锚点表=37 ✓
- FIND-3（第 4 工具）：BDD-15 与 §1 不迁移清单均补 `agate-gate-p5-count.py`（4 个），实测该工具含 `^gate_commands:` 正则 ✓
- FIND-4（验证载体）：隐含需求 9/10/11 均注明验证载体 ✓

## 2. 上轮 FIND 闭环复核

| FIND | 修改落点（line） | 客观复核 | 判定 |
|------|----------------|---------|------|
| FIND-1 判别契约 | §3 隐含需求 1（L58-60）+ BDD-6 Given（L122） | 契约两分支互斥："含任意迁移字段→新格式严格校验；不含→旧格式回退不触发必填校验"；BDD-9 Given（L139"frontmatter 无这些字段"）与契约"旧格式"分支一致，BDD-10（frontmatter 有字段→优先）与"新格式"分支一致；同一文件不再同时命中 BDD-6 与 BDD-9 | 闭环 |
| FIND-2 37 条 | F10（L50）/ §3 隐含需求 3（L63）/ BDD-13 Then（L163） | grep 全文无"33 条"；AST 解析 `SCRIPT_ALIGNMENT_ANCHORS` 实际 37 条 | 闭环 |
| FIND-3 第 4 工具 | BDD-15 When（L174）/ §1 不迁移清单（L30） | `agate-gate-p5-count.py:14` 含 `^gate_commands:` 正则；grep 确认从正文正则读 gate_commands 的 .py 工具恰 4 个 | 闭环 |
| FIND-4 验证载体 | 隐含需求 9（L77）/ 10（L80）/ 11（L83） | 9→P4/P5 实现验证 + CHANGELOG；10→P8 流程（badge/tag/merge）；11→P0 env_constraints。均声明"无对应 BDD"理由，防 P6 误判漏覆盖 | 闭环 |

## 3. BDD 评审（逐条判定 + 覆盖维度）

> 覆盖维度标注：数据 / 前端 / 多端 / 边界 / 兼容（前端、多端本任务不适用，见 §4）。

| BDD | 判定 | 可二值判定 | 单 GWT | 覆盖维度 |
|-----|------|-----------|--------|---------|
| BDD-1 | 通过 | 是（门禁判定结果 vs frontmatter 声明值可比对） | 是 | 数据✓ 兼容✓（统一读取路径） |
| BDD-2 | 通过 | 是（校验失败 + 报错含字段位置） | 是 | 数据✓ 边界✓（全角冒号） |
| BDD-3 | 通过 | 是（解析结果 vs 声明一致） | 是 | 数据✓（phases 双格式归一） |
| BDD-4 | 通过 | 是（校验失败 + 错误含字段名/行号） | 是 | 数据✓ 边界✓（缩进错误） |
| BDD-5 | 通过 | 是（校验失败 + 提示合法值） | 是 | 数据✓ 边界✓（枚举非法值） |
| BDD-6 | 通过（FIND-1 修复后） | 是（Given 收紧为"新格式文件（frontmatter 含迁移字段集）缺必填"，与 BDD-9 不再重叠；拦截与否可二值判定） | 是 | 数据✓ 边界✓ 兼容✓（判别契约显式化） |
| BDD-7 | 通过 | 是（错误信息含字段名/行号） | 是 | 数据✓（错误可定位） |
| BDD-8 | 通过 | 是（pre-commit 拦截发生与否） | 是 | 数据✓ 兼容✓（同 .state.yaml 机制） |
| BDD-9 | 通过（FIND-1 修复后） | 是（回退读到字段、行为与 v0.35 一致，可比对） | 是 | 兼容✓（旧格式回退） |
| BDD-10 | 通过 | 是（返回 frontmatter 值 vs 正文值可断言） | 是 | 数据✓ 兼容✓（优先序） |
| BDD-11 | 通过 | 是（count-tests.sh = 594，实测相符） | 是 | 兼容✓（测试基线不漂移） |
| BDD-12 | 通过 | 是（schema 定义最大嵌套层数可检查） | 是 | 数据✓（3 层嵌套硬约束） |
| BDD-13 | 通过（FIND-2 修复后） | 是（0 ERROR，含 CHECK 9 全量） | 是 | 兼容✓（CHECK 9 锚点表 37 条） |
| BDD-14 | 通过 | 是（P2-design.md 存在明确声明与否） | 是 | 数据✓（语义真实性边界落文档） |
| BDD-15 | 通过（FIND-3 修复后） | 是（4 个工具各按旧正则仍可读） | 是 | 兼容✓（gate_commands 不迁移无回归） |

**编号检查**：BDD-1..15 连续不跳号；格式均为 `#### BDD-NN:`（gate 锚点格式可匹配）；每条单一 Given-When-Then（15/15）。✓

**跨条一致性**：判别契约显式化后，BDD-6/9/10 三者 Given 互斥、无矛盾。BDD-2/4/5（新格式严格校验）与 BDD-9/10（旧格式回退、frontmatter 优先）优先级语义清晰。其余 BDD 无 Then 冲突。✓

## 4. 隐含需求覆盖（五维度）

- **数据维度**：覆盖 ✓（BDD-1/3 字段读取、BDD-12 嵌套深度；摩擦 F1-F6 均有 BDD）
- **前端维度**：不适用 ✓（§7 domains=[backend, cli]、§8 ui_affected=false，非 UI 任务——已显式声明，无遗漏）
- **多端维度**：不适用 ✓（单包无前后端契约；"多端"退化为多读取工具一致性，由 BDD-1/9/10/15 覆盖）
- **边界维度**：覆盖 ✓（BDD-2 全角冒号、BDD-4 缩进、BDD-5 枚举非法值、BDD-6 必填缺失）
- **兼容维度**：覆盖 ✓（BDD-9 旧格式回退、BDD-10 frontmatter 优先、BDD-11 测试基线、BDD-13 一致性、BDD-15 gate_commands 不迁移）

**隐含需求条目映射**（P1-requirements.md §3 的 11 条）：

| # | 隐含需求 | BDD 覆盖 | 判定 |
|---|---------|---------|------|
| 1 | 在途任务双读 | BDD-9/10 | 覆盖 ✓（FIND-1 判别契约已补） |
| 2 | frontmatter schema 校验器 | BDD-2/4/5/6/7/8 | 覆盖 ✓ |
| 3 | CHECK 9 锚点表重新校准 | BDD-13 | 覆盖 ✓（FIND-2 已改 37 条） |
| 4 | 测试 fixture 重写不漂移 | BDD-11 | 覆盖 ✓ |
| 5 | 角色卡可复制模板 | BDD-12（隐含）+ 摩擦 F2 修复机制 | 覆盖 ✓ |
| 6 | frontmatter 禁 >3 层嵌套 | BDD-12 | 覆盖 ✓ |
| 7 | 语义真实性边界入文档 | BDD-14 | 覆盖 ✓ |
| 8 | agate-md-field-get.py 核心改造点 | BDD-1（隐含） | 覆盖 ✓ |
| 9 | P5_DATA CACHE_KEY 验证 | 无 BDD（验证载体已注明：P4/P5 + changelog） | 覆盖 ✓（FIND-4） |
| 10 | 版本发布 v2.0.0 | 无 BDD（验证载体已注明：P8 流程） | 覆盖 ✓（FIND-4） |
| 11 | 双工作区隔离 | 无 BDD（验证载体已注明：P0 env_constraints） | 覆盖 ✓（FIND-4） |

## 5. 裁剪评审

- **跳过阶段**：无（P1-P8 全流程）。理由充分：协议级重构（约 25-30 文档/角色卡/模板 + 14 脚本 + 15 测试文件），P2 设计、P3 测试先行、P4 实现、P5 验证、P6 验收、P7 双向一致性、P8 发布（含 --no-ff 铁律）均不可省。✓
- **risk_level**: high —— 与实际风险匹配（数据格式变更 + gate 自我改造 + 355 测试换血，占 594 的 60%）。✓
- **capability_requirements**: 无 GAP；pyyaml（agate-state-yaml-check.py 在用）、bats 1.10.0、shellcheck 三态均 available，判定正确。✓

## 6. 特别检查（本任务上下文）

### 6.1 语义真实性边界（BDD 只断言解析可靠性，不声称 gate 变强）

**通过。** 15 条 BDD 全部只断言"字段被可靠读取 / 坏格式被拦截 / 硬约束保持"，无任何一条断言"gate 能发现内容造假"：BDD-2/4/5/6/7（格式校验行为）、BDD-9/10（读取路径优先级）、BDD-1/3（读取一致性）。§9 显式声明"结构化不解决内容真实性（BDD-8 单侧/双侧歧义、candidate_count 虚报依旧）"，且 §9 末行"BDD 不得声称 gate 变强"与本基线实际内容一致。✓

### 6.2 scope 边界

**通过。** 与 P0-brief/HANDOFF §5.3 已定决策一致：`gate_commands` 不在迁移集（§1 明确 + BDD-15 防回归，工具清单 4 个已补全）；迁移集 = 候选数/裁剪类字段（P1 12 项 + P2 4 项），与可行性评估 §6.2 一致；流 B/C 不在本任务（§1 + §3 记录流 B 风险由后续任务承接）。✓

### 6.3 P1 纯净性

**通过。** 无方案设计混入：BDD 均为"系统应做什么"（字段被读取/坏格式被拦截），不含具体 API/类/实现细节；校验器命名等仅以 [SUGGEST] 倾向项形式出现（L187-188），不阻塞。✓

## 7. 观察项（非阻断，不改变结论）

- **P0-brief.md:24/57 仍写"CHECK 9 锚点表（33 条）"**——P0 父文档的旧数字，不在本任务（只改 P1-requirements.md）范围内；P1 基线已用正确值 37（与实测一致）。建议主 Agent 在后续阶段顺手修正 P0-brief，避免 P7/P8 误引旧数字。

## 8. 结论

**Status: approved**

上轮 FIND-1/2/3/4 全部闭环且经客观查证一致；全量重审确认：BDD-1..15 连续、格式合规、每条单 GWT、均可二值判定；隐含需求 11 条全覆盖（含 FIND-4 验证载体）；语义真实性边界、scope 边界、P1 纯净性均达标。无新的阻塞项。观察项（P0-brief 旧数字）不构成修订理由。
