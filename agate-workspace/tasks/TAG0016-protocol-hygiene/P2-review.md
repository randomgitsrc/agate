---
phase: P2
task_id: TAG0016
type: review
parent: P2-design.md
trace_id: TAG0016-P2-20260819
status: approved
created: 2026-08-19
agent: plan-eng-review
---

[PROD_NOT_TOUCHED]

# P2 评审 — 工程经理（plan-eng-review） — TAG0016（第 2 轮复审）

这是第 2 轮复审，范围收窄为核查 4 处修订（§1.3 新增 R9 / §3.2 边界条件段 / §5 批次论证订正 /
§0-§11 口径统一 / DEBT0009 登记），不重新审全部内容。候选方案真实性（约束 1/2）、CHECK 12/
BDD-12/13 的候选选择、整体路线方案 A、serial 批次划分本身，第 1 轮已通过，本轮沿用，不复议。

## 逐项核查（本轮复审范围）

### 1. 阻塞项核查：§1.3 R9 + §3.2 边界条件段

已读 §1.3 风险表新增行 R9（"P5 commit 混入非产出文件改动会破坏 §3.2 等价性论证前提"）与
§3.2 新增段落"边界条件与残余风险（修复轮补充，回应 plan-eng-review 阻塞项）"，逐点核对上一轮
要求的三点：

- **(a) 承认前提边界条件**：§3.2 原文——"上述等价性依赖一个前提——'P5 commit 本身只改产出
  文件'。该前提**并非无条件成立**：本仓库真实历史中，`5bdcd90`（`wf(TAG0001-P5):` commit）
  除产出文件外，还混入了对 `agate/scripts/agate-debt-check.py`（`serialize_evidence()` 函数
  YAML int 边界修复）的真实改动……若某次 P5 commit 重演此模式，父提交哈希与该 P5 commit 自身
  哈希在 diff exclusion 判定上**不再等价**"——明确承认，且引用的是本轮 review 指出的同一个
  真实反例（`5bdcd90`），未回避、未弱化为假设场景。**满足。**
- **(b) 失败方向保守/安全**：§3.2——"失败方向是**保守/安全**的：这不会产生'应重跑却被误判为
  可复用、从而跳过应有验证'的安全漏洞——多出来的那份'改动'只会让审计 7（§3.5）判定 `changed`
  非空，进而拦截'引用 P5 证据、不重跑'的声明，强制走完整重跑。唯一代价是该本可复用的场景被
  误判为需要重跑，即多跑一次，不会少跑该跑的验证，不威胁 BDD-17 回归底线"——推导链路完整
  （审计 7 拦截逻辑 → `changed` 非空 → 强制重跑 → 代价是"多跑"而非"漏跑"），与 §3.5 审计 7
  的实际代码逻辑（`if changed: ... error(...)`）一致，不是空泛断言。**满足。**
- **(c) 轻量缓解**：§3.2 结尾 + §1.3 R9「缓解措施」列 + §1.1 M20 落点三处一致地写明——
  `P5-verification.md`「如果是首次进入本阶段」步骤 4-5 之间要求"P5 commit 不得混入非产出文件
  改动，若发现顺手修复的必要性，应先回 P4 走正常流程，不要混入 P5 commit"。这是操作纪律层面
  的缓解（不改机制本身），落点具体（明确文件+插入位置），三处表述一致、无矛盾。**满足。**

**结论：阻塞项已充分回应，问题本身解决——承认了边界条件、说清了失败方向的安全性、给出了可
执行的轻量缓解，不是空洞表述。此前阻塞项解除。**

### 2. §5 批次论证订正核查

§5「为何整体选 `serial`」段落已重写：原文"文件不重叠、理论上可并行"的表述已删除，替换为——
"`test-evidence-provenance` 批次与 `doc-dedup` 批次**实际存在文件重叠**——`doc-dedup` 批次的
M7（`dispatch-protocol.md` 文件头新增职责边界声明行）与 `test-evidence-provenance` 批次的
M16（同一文件 `dispatch-protocol.md` 新增小节「## 全量重跑点审计」）都改动 `dispatch-protocol.md`。
若这两批并行派发，两个 subagent 会同时编辑同一份文件，产生合并冲突/相互覆盖的真实风险——这本身
就是选择 serial 而非'两批并行+一批串行'方案的**更硬理由**"。这与上一轮 review 指出的事实
（M7/M16 均改 `dispatch-protocol.md`）完全对应，措辞不再声称"不重叠"，且把重叠改写为支持
serial 的更硬理由，符合修复方向要求。serial 决策本身第 1 轮已认同，未变。**结论：已订正到位，
通过。**

### 3. §0/§11 口径统一核查

- §0 职责声明表新增声明："下表全部 7 类文档的职责边界均受本表约束，但**显式新增一行**
  `> 职责边界：…` 的具体落地范围只有 4 份（BDD-1/BDD-19 落地点，对应 §1.1 M3/M7/M10/M12）：
  `WORKFLOW.md` / `dispatch-protocol.md` / `state-machine.md` / `platform-notes.md`"，并逐一
  说明 `rules/state-transitions.md`（M11）/`dispatch-prompt.md`（M8）/`phase-cards/*.md`（M13）
  各自落地形式不同、不计入"职责边界"声明行计数。
- §11 完成标志对应改为："4 份协议文档文件头均含'职责边界'声明行……`WORKFLOW.md`（M3）/
  `dispatch-protocol.md`（M7）/ `state-machine.md`（M10）/ `platform-notes.md`（M12）——这是
  '职责边界'声明行这一具体格式在本任务中落地的完整范围（口径统一，修复轮订正，与 §1.1 M-表
  一致）"，并同样注明 M11/M8 不纳入本条计数。

两处表述完全对齐（同一份 4 文件清单、同一 M 编号引用、同一"不纳入计数"说明），不再出现"8 份"
或"6 个文件名对不上 8 这个数字"的矛盾。**结论：口径已统一，通过。**

### 4. DEBT 记录核查

§3.4 选择理由第 2 点原文保留"记录为技术债"式表述——"已按标准格式登记为 `DEBT0009`
（`{AGATE_WORKSPACE}/debt/tech-debt.md`，category: protocol，priority: low，source: review），
不在本任务展开"，采用的是选项 (a)（补登记标准 DEBT 条目）。核查
`agate-workspace/debt/tech-debt.md`「## DEBT0009」条目：字段包含
`id`/`category`/`title`/`status`/`priority`/`evidence`/`impact`/`recommendation`/
`closure_criteria`/`source`/`created_at`/`task_id`，`evidence.path` 指向
`P2-design.md`（§3.3/§3.4 权衡内容），`category: protocol`、`priority: low`、`source: review`、
`created_at: 2026-08-19`、`task_id: TAG0016` 均按 dispatch-context 要求填写，字段与模板
（`assets/templates/tech-debt-template.md`）必填项一一对应，无缺字段。

另跑机器校验复核未引入新问题：`python3 agate/scripts/check-debt.py agate-workspace/debt/tech-debt.md`
输出的三条错误（`DEBT0005`/`DEBT0006` 相关）均为既存条目问题，与本次新增的 `DEBT0009` 无关，
`DEBT0009` 本身未被校验器报错。**结论：已落地为标准 DEBT 条目，格式合规，通过。**

---

## 架构问题（阻塞级）

无。上一轮唯一阻塞项（§3.2 自指悖论等价性论证的边界条件缺失）已在本轮核查中确认充分回应，
解除。

## 架构问题（非阻塞）

无遗留。上一轮 3 项非阻塞建议（§5 论证文本事实错误 / §0-§11 计数口径不一致 / §3.4 DEBT 未
落地）均已在本轮逐一核查确认处理到位，不再重复登记。

## 测试缺口

- （沿用第 1 轮记录，非本轮判定范围，供 P3/P4 参考）`test_protocol_dedup_audit.py` 未覆盖
  BDD-1/BDD-19（M3/M7/M10/M12 四处"职责边界"声明行的存在性 + 内容与 §0 表一致性校验）——
  该计数口径本轮已统一为"4 份"，建议 P3 测试设计据此范围补断言，不影响本轮 approve 判定
  （dispatch-context 已明确本项不影响本轮判定）。
- BDD-8（P6 抽查"职责定位混乱"段落是否与职责声明表相符）的具体落点建议 P4/P6 阶段显式引用，
  同上，非阻塞。

## 锁定决策

- CHECK 12 采用**候选 2（结构化权威锚点扫描）**——第 1 轮已通过，本轮未变动，维持锁定。
- BDD-12/13 存储位置采用**候选 A（`.state.yaml` 新增可选字段 `p5_pass_commit`）**——第 1 轮
  权衡已认同，其正确性依赖的等价性论证边界条件本轮已补齐（R9 + §3.2），**阻塞解除，正式锁定**。
- 整体路线**选方案 A**（结构化锚点 + serial 三批 + `.state.yaml` provenance 字段 + CI-only
  xdist 观测），serial 批次拆分论证文本已订正（M7/M16 文件重叠改写为支持 serial 的更硬理由），
  最终决策与第 1 轮一致，**锁定**。
- §0/§11"职责边界"声明行落地范围锁定为 4 份文件：`WORKFLOW.md`（M3）/`dispatch-protocol.md`
  （M7）/`state-machine.md`（M10）/`platform-notes.md`（M12），后续 P3/P4/P6 按此口径执行，
  不再有 4/6/8 份的歧义。
- DEBT0009 已登记（候选 C commit message 派生方案的重新评估留待未来 commit message 格式被
  gate 强校验后），本任务不展开候选 C。

**本轮结论：approved。** 阻塞项已充分回应，3 项非阻塞订正均已处理到位，可进入 P3。
