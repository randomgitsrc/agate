# 复盘：TAG0010 + TAG0011 + 文档体系更新全过程分析

日期：2026-08-15
依据：本会话 session 记录 + 各 subagent 会话记录 + git 历史（v0.45.0..HEAD 共 136 commit）
范围：TAG0010（产品逻辑 Python 化，v0.46.0）、TAG0011（测试框架迁移，v0.47.0）、之后的文档体系更新与归档

---

## 0. 事实基线

| 项 | 数据 |
|----|------|
| 交付版本 | v0.46.0（TAG0010）+ v0.47.0（TAG0011）|
| 总 commit | 136（TAG0010 36 + TAG0011 47 + 文档/归档/杂项）|
| 产品迁移 | 30 个 .sh → py（3 hook 保留 sh 薄壳），删档 27 个 .sh |
| 测试迁移 | 60 个 .bats（749 用例）→ pytest（750 collected），删档 60 .bats + 3 helpers |
| 文档更新 | README 英文门面 + 中文镜像 + AGENTS/SELF-GATE/SETUP/UPGRADING 等 12+ 文件重写/核对 |
| 历史归档 | 197 个文件 → archived/docs-2026-08/ |
| subagent 空返回 | 7 次（migrate-workspace×3、check-platform-assumptions×1、check-tdd-red×1、pre-commit-hook×2）|
| 批验证发现缺陷 | 测试/代码缺陷 6 处（bdd-5×2、inject-card、install-hook mock、pre-commit mkdir×12、R4 注释字面）+ check-gate 补遗 4 用例；文档类另由独立评审发现 phase-cards 26 处过时引用 |

---

## 1. 管理原因分析

### 1.1 任务粒度过大导致 subagent 卡死（早期核心矛盾）

- **事实**：会话开始时，用户中止了一个 subagent（TAG0010 批次 0），反馈"任务过重、很长时间没进展、卡死"。批次 0 的范围是"agate_common.py 整库（11 个函数）+ ci-gate-backstop 改造 + 3 个 bats 改造"——一次派发。
- **根因**：给单 subagent 的任务包含过多文件/过长上下文，subagent 在"读文件→消化→实现→自查"长链条中失速（模型上下文窗口压力 + 工具调用累积）。
- **后果**：批次 0 由主 Agent 收尾验证后才提交；后续采用拆批策略。

### 1.2 拆批策略是本次会话最有效的管理措施

- **事实**：TAG0011 P4 拆 19 批 + 子批（check-gate 146 用例拆 8 子批每次 ≤32、pre-commit 56 拆 3 子批、check-tdd-red 43 单文件），**拆批后无再卡死**。
- **量化**：TAG0011 的 47 个 commit 中 P4 占 36 个（批次 0-18），绝大多数批次 1 轮完成、0 空返回（除 check-tdd-red / pre-commit-hook 初试）。
- **结论**：任务粒度"1 轮 subagent 可完成"是管理基线，P2 批次设计（表 E 批次划分）为此提供了结构基础。

### 1.3 会话超长带来的上下文管理

- **事实**：本会话横跨 2 个完整任务 + 文档体系更新，累计 136 commit。主 Agent 上下文持续增长。
- **处理**：每批"验证→commit"闭环，状态全部落盘（P4-progress / .state.yaml / active-tasks），中断可恢复。
- **风险**：主 Agent 上下文接近上限时判断力下降（agate 已知局限 3 的单点风险在长会话放大）。

### 1.4 文档体系更新范围逐步扩大（需求蔓延）

- **事实**：用户从"重写 README"扩展到"连同 AGENTS/SETUP/UPGRADING 等一套全部更新"，又补充"不对的内容该改也要改掉"（推翻历史记录保留原则），再到"过时文件移除或归档"。
- **处理**：通过 brainstorming（受众/目标/结构/范围四轮确认）+ 设计文档落盘，把蔓延转化为受控扩展。
- **结论**：文档类任务的需求边界模糊，主动呈现范围方案 + 用户确认是控制蔓延的正确方式。

---

## 2. 技术原因分析

### 2.1 第三方模型（GLM）偶发空返回，与任务复杂度正相关

- **事实**：空返回集中在**复杂任务**（migrate-workspace 涉及 git mv/hook 语义、pre-commit-hook 48 用例 hook 触发、check-platform-assumptions 正则状态机、check-tdd-red 43 用例 formatter 逻辑），**简单任务**（纯工具 5 文件 15 用例等）0 空返回。check-gate（488→748 行，复杂度最高）经拆 8 子批后 **0 空返回**——佐证拆批有效性。
- **特征**：空返回 subagent 无任何落盘痕迹（文件都没建），说明在早期阶段（读文件/规划）就失速，非实现中途崩溃。
- **处理**："只写代码不跑测试"策略 + 拆小 + 主 Agent 批验证，三者组合后空返回消失。

### 2.2 subagent 上下文爆炸（files_to_read 失控）

- **事实**：TAG0010 批次 0 的 dispatch-context 范围过大（agate_common.py 整库 11 函数 + ci-gate-backstop 改造 + 3 个 bats 改造，派发清单含 12 项参考文件），subagent 需消化大量迁移源与调用面后才开始实现。
- **根因**：dispatch-context 给了范围但没给"读什么、不读什么"的精确边界；subagent 倾向全文通读。
- **处理**：后续 dispatch-context 明确"必读清单 + 控制输入规模 + 用 grep 定位不整目录搜索"；TAG0011 的 P2 files_to_read 精度是设计级要求。

### 2.3 bats 测试的 fixture 复杂度是特定卡死诱因

- **事实**：空返回集中在**依赖 git 仓库 fixture / hook 触发**的任务（migrate-workspace 的 git mv、pre-commit-hook 的真 commit 触发）——subagent 在复现/理解 fixture 时失速。check-gate 的复杂 task_dir 构建虽复杂度高，但经拆 8 子批后 0 空返回（见 2.1）。
- **对照**：纯 stdin/stdout 工具（json-get/md-field 等）全部顺利迁移。
- **结论**：测试代码迁移类任务中，fixture 密集型文件的迁移应默认拆小 + 主 Agent 验证。

### 2.4 迁移暴露的既有测试/代码缺陷（6 处 + 迁移遗漏 + 环境敏感 + 文档类）

- bdd-5 检查器漏豁免二进制 open（`"rb"`）——与自身注释"二进制除外"矛盾（TAG0004 遗留）
- bdd-5 read_text 误判自定义函数 `_read_text(`（TAG0004 遗留）
- inject-card.py 占位符缺失时错误消息未透传（py 化迁移 bug）
- install-hook 复制模式测试 mock ln 失效（py 化语义差异：os.symlink 不经 PATH）
- pre-commit-hook 测试 task_dir mkdir 顺序（subagent 代码缺陷，批验证发现）
- test_check_tdd_red_formatter.py 注释含 R4 字面命中（扫描器干净树契约，批验证发现）
- 迁移遗漏：check-gate 4 用例（PG.P2REVIEW/bdd-14/28/29，8h 按"非穷举分区"遗漏，补遗迁移）
- 环境敏感项：check-pruning 测试依赖"运行时 git 暂存区干净"（删档时误触发，非代码缺陷，见 2.5）
- 文档类：phase-cards 26 处过时 .sh 引用（v0.46.0/v0.47.0 破坏性变更未同步到必读卡，独立评审发现）

**共性**：大规模迁移是测试缺陷的"显影剂"——迁移把隐含假设（bats 语义、工具行为、环境状态）暴露为显式冲突。**批验证（主 Agent 亲自跑测试）是发现测试/代码缺陷的关键机制**——6 处测试/代码缺陷全部在批验证阶段被发现，而非 subagent 自查；文档类缺陷（phase-cards 26 处）由独立文档评审发现，两条路径互补。

### 2.5 git 环境敏感测试（check-pruning 源码计数）

- **事实**：check-pruning 的 `_staged_source_count` 用 `git diff --cached` 统计源码数，测试运行时**当前仓库的暂存区状态**影响结果。删档（git rm 暂存 27 个 .sh）导致测试误失败。
- **处理**：commit 清空暂存区后恢复。
- **教训**：测试应隔离于"运行时的仓库暂存区状态"（bats 时代同样存在，只是环境恰好干净）。

---

## 3. agate 原因分析

### 3.1 agate 机制原因（协议/脚本层面）

| 机制 | 表现 | 评价 |
|------|------|------|
| P2 批次设计（表 E） | TAG0010 批次 0-4、TAG0011 批次 0-18 的批次划分在 P2 就定好，P4 按批执行 | **有效**：为拆批提供结构基础，避免 P4 临时拍脑袋 |
| gate 客观验证（check-gate/check-p6-evidence/provenance） | 每阶段主 Agent 跑 gate，不信 subagent 自报 | **有效**：P5/P6/P7/P8 的推进全部有客观证据 |
| C8 评审映射 | P4 review（backend）| **有效**：批次 0 评审发现 0 BLOCKER 但确认了合并流语义等关键点 |
| refactor 回归口径（P6） | 两个任务都走"行为不变 + 全量回归 + 关键 BDD"三段式 | **有效**：P6 验收与"重构不改行为"语义匹配 |
| self-gate 触发面 | 仓库根文档（SELF-GATE.md、README）不在触发面，文档更新未强制 self-gate | **缺口**：本次文档体系更新（改 agate/*.md）触发了 self-gate WARNING，但仓库根级文档（SELF-GATE.md 自身）不在自检范围 |
| consistency CHECK 9 锚点表 | 只覆盖脚本结构对齐，**不检查文档中的脚本名引用** | **缺口**：phase-cards 26 处过时引用、SELF-GATE.md 的 check-gate.sh 残留、AGENTS.md 的 install-hook.sh 残留，一致性检查均未抓到——文档名引用漂移无 gate 兜底 |
| P1 表 B（文档引用映射） | 列了 15 个 in-scope 文档，**phase-cards/rules/assets 不在表 B** | **缺口**：导致 v0.46.0/v0.47.0 破坏性变更后 phase-cards 等必读卡 26 处过时引用漏网（评审才发现）|

### 3.2 agent 执行 agate 遵循情况（主 Agent 与 subagent）

**遵循良好**：
- 每批"验证→commit"闭环，状态落盘（P4-progress 每批记录）
- 不信 subagent 自报，主 Agent 亲自跑测试（批验证）
- gate 全过才推进（P1-P8 无跳过）
- dispatch-context 先写后派（TAG0011 全部批次）
- 空返回处理符合 dispatch-protocol 精神（拆小重试，不静默绕过）

**偏离/不足**：
- **批次 0 派发过大**（TAG0010）：违背 P2 批次 0 的"公共库"设计意图（一次做整库 + 3 bats），未按"1 轮可完成"校准——用户中止后才修正
- **inject-card 顺序错误一次**（TAG0011 批次 2a）：dispatch-context 写后未及时 inject 就派发（虽未造成实质影响）
- **P5 补 N5 签名**（TAG0011）：verifier 产出 unit.md 缺标准签名行，主 Agent 补写——verifier 未完全遵循 N5 校验格式
- **bdd-5 检查器缺陷未在 TAG0004 后立即修复**：两个 bdd-5 缺陷在 TAG0010 才暴露修复，说明"测试缺陷"登记闭环（TAG0001 债务机制）未覆盖测试代码自身缺陷

---

## 4. 问题清单 + 可行性处理措施

| # | 问题 | 维度 | 处理措施（可行性）|
|---|------|------|------------------|
| 1 | 单 subagent 任务过大导致卡死 | 管理 | **派发前校准"1 轮可完成"**：默认 ≤4 文件/≤40 用例/单脚本；fixture 密集任务默认拆小（可写入 dispatch-protocol 派发模板约束）|
| 2 | subagent 空返回无落盘痕迹 | 技术 | 已有缓解（分阶段落盘指令）；可增强：dispatch-context 强制"读完 X 先写一行 progress"（SELF-GATE 留痕机制可推广到所有 subagent）|
| 3 | 上下文爆炸 | 技术 | files_to_read 精度进 P2 设计评审关注点（TAG0011 已实践，可写入 architect.md 强制项）|
| 4 | 文档脚本名引用漂移无 gate 兜底 | agate 机制 | **新增一致性检查项**：check-protocol-consistency.py 增加"文档中脚本名引用 vs scripts/ 实际文件"扫描（CHECK 10），防止 v0.46.0 类破坏性变更后文档漂移（本会话 phase-cards 26 处就是此类）。**豁免**：UPGRADING 迁移对照表（旧→新命令对照写旧名是有意保留）、hook 薄壳（pre-commit-gate.sh 等仍为 sh）、formatter（assets/formatters/ 仍为 sh）、count-tests.sh（tests/scripts/ 仍为 sh）|
| 5 | P1 表 B 未覆盖 phase-cards/rules | agate 机制 | 破坏性变更（脚本改名/删档）的文档同步清单应含 phase-cards/rules/assets 全量，而非仅表 B 15 个 |
| 6 | 测试缺陷无登记闭环 | agate 机制 | 测试代码缺陷（bdd-5 等）应可登记 tech-debt（TAG0001 机制扩展到测试代码）|
| 7 | 长会话主 Agent 上下文压力 | 管理 | 任务间显式"会话 checkpoint"（提交 + 状态落盘 + 汇报），必要时分段会话 |
| 8 | 环境敏感测试（git 暂存区依赖）| 技术 | check-pruning 类测试隔离暂存区（专用 git 仓库或 env 控制），防运行时状态误触发 |

---

## 5. 亮点总结

1. **"不跑 bats/只写代码"策略**：针对空返回的精准外科手术——把"subagent 自查"从任务中剥离、由主 Agent 批验证承担，空返回立即消失（migrate-workspace 3 次空返回 → 策略切换后 1 次成功）。这是对 agate"自查≠gate"原则的**强化执行**（自查本来就该主 Agent 验）。
2. **批次拆小到极致**：check-gate 146 用例拆 8 子批（每批 ≤32）、pre-commit 56 拆 3 子批——TAG0011 拆批后零卡死，证明"粒度 1 轮可完成"是可靠基线。
3. **批验证发现 6 处测试/代码缺陷**：主 Agent 每批亲自跑 pytest + 对照 bats，6 处测试/代码缺陷全部由此发现（非 subagent 自查）——"不信自报"原则的实证价值。文档类缺陷（phase-cards 26 处）则由独立文档评审发现，两条发现路径互补。
4. **双跑对照（迁移期）**：TAG0011 每批 pytest 绿 + 原 bats 对照绿，迁移正确性有双重证据。
5. **文档体系门面化 + 独立评审闭环**：README 从 215 行中英混杂 → 108 行英文门面 + 中文镜像；独立评审发现 5 问题全部修复；全仓库过时引用终扫清零。
6. **历史归档**：197 个历史文件归档到 archived/docs-2026-08/，仓库只剩活跃文档——"过时即归档"让仓库保持可信。
7. **P7 一致性检查真实有效**：TAG0010 的 SCOPE+ 闭环 BLOCKER、TAG0011 的 dispatch-protocol 残留，都是 P7 reviewer 独立发现——评审角色独立性有实际产出。

---

## 6. 结论

本次会话完成两个大型迁移任务（30 脚本 py 化 + 60 bats pytest 化）+ 文档体系重建，交付 v0.46.0/v0.47.0。核心成功因素：**批次拆小 + 主 Agent 批验证 + 状态落盘**。核心教训：**给 subagent 的任务必须"1 轮可完成"，自查责任在批验证而非 subagent**。agate 机制的主要改进点：文档脚本名引用的 gate 兜底（CHECK 10）与破坏性变更文档同步清单（phase-cards 全量）——这两项能系统性防止 v0.46.0/v0.47.0 暴露的文档漂移问题。

---

（本报告基于本会话 session 记录 + subagent 会话记录 + git 历史，事实可追溯；建议作为新任务（如 CHECK 10 实现、派发模板约束强化）的立项依据。）
