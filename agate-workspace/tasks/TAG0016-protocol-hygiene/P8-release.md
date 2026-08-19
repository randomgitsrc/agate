---
phase: P8
task_id: TAG0016
type: release
parent: P7-consistency.md
trace_id: TAG0016-P8-20260819
status: draft
created: 2026-08-19
agent: implementer
---

[PROD_NOT_TOUCHED]

# P8 发布准备 — agate 协议卫生与测试效率（TAG0016）

> 本任务是 agate 协议自身的单一版本发布（不是多包各自独立版本的项目）。P2-design.md frontmatter
> 声明的 8 个 `packages`（workflow/dispatch-protocol/state-machine/platform-notes/
> state-transitions/phase-cards/dispatch-prompt-template/gate-scripts）是 P7 一致性检查用的
> "受影响范围分类"，不是 8 个独立可发布单元——agate 整体只有一个版本号。本文件不走"多包拆批"
> 流程，产出单一 P8-release.md。

## bump_type: minor

**独立核实过程**（未直接采信 dispatch-context 结论文字，实跑 grep 核对判据文本）：

1. 权威判据文本已随 M6/M8（本任务自身的去重改动）迁移：`grep -n "^## 版本 bump 判定"
   agate/dispatch-protocol.md` 在本 worktree 内**无命中**——该节已收窄为指针（M6），完整判据表
   现位于 `agate/assets/templates/dispatch-prompt.md`（L235-240，权威源）：
   - 公共 API 行为变化 / 破坏性变更 → major
   - 加功能 / 内部重构改 API（向后兼容）→ minor
   - 修 bug / 不改 API 行为 → patch
2. 逐项核对本任务改动是否落在"向后兼容新增"象限：
   - **CHECK 12**（`check-protocol-consistency.py` 新增 `AUTHORITATIVE_VALUE_ANCHORS` +
     `check_authoritative_values()`，并列注册进 `CHECKS` 列表）——`grep -n "def check_authoritative_values\|CHECK 12"` 已核实为新函数、新注册项，未修改 CHECK 1-11 的既有逻辑/签名/返回值。
   - **审计 7 + `--audit7-only`**（`check-p6-provenance.py` 新增 `audit7_p5_evidence_reuse()`
     + 新 CLI 模式）——`grep -n "def audit7_p5_evidence_reuse"` 已核实为新函数，未改动既有审计
     1-6 的判定逻辑；`--audit7-only` 是新增可选 CLI flag，不改变无此 flag 时的既有默认行为。
   - **ADR-010**（`agate/adr.md` 新增 48 行）——纯新增记录，未修改/废弃既有 ADR-001~009。
   - **`.state.yaml` 新增可选字段 `p5_pass_commit`**——P2-design.md §1.3 R3 已用代码核实
     `check-state-yaml.py`/`agate-state-yaml-check.py` 不做 unknown-field 拒绝，字段声明为
     可选、缺失时审计 7 回退强制重跑，存量任务（TAG0001~TAG0015）无此字段仍可正常通过 gate——
     不构成 schema 破坏性变更。
   - **协议文档去重（M1-M12，8 类文档职责边界 + 指针替代重复段落）**——P7-consistency.md §3.3
     已逐条核实 M1-M23 全部落地，性质是内容重组（指针 + 权威源），消费方最终读取到的可判定值
     （如"重试上限=N"、"MAX=N"）语义不变，无行为破坏。
   - **DEVIATION（`verifier.md`/`adr.md` 超出 P2 声明的 8 个 packages）**——P7 §3.2 已判定为
     非核心、纯新增内容（10 行新增 + 48 行新增 ADR），不改变任何既有文件的既有行为。
3. 综合判定：本任务全部改动（含 P7 已识别的 1 处非核心 DEVIATION）落在"向后兼容新增能力/内部
   重构"象限，无任何一处修改既有 gate 脚本对老任务的判定行为、无破坏性 API/schema 变更。
   **独立结论：bump_type = minor 成立**，与 dispatch-context 约束 2 的结论一致（核实过程独立
   完成，非照抄）。

当前版本 v0.53.0（TAG0015），bump 后为 **v0.54.0**。

## debt_check: reviewed

已读 `{AGATE_WORKSPACE}/debt/tech-debt.md` 全部 12 条 DEBT 条目，逐条核对 `task_id` 字段。

本任务相关（`task_id: TAG0016`）4 条，均为本任务新增/扩充，均 `status: open`（不要求本次关闭，
登记本身即目的——可见可追踪）：

| DEBT id | 标题（摘） | status | priority |
|---------|-----------|--------|----------|
| DEBT0009 | BDD-12 provenance 存储候选 C（commit message 派生）本次未采纳，记录权衡供未来重估 | open | low |
| DEBT0010 | 至少 4 个 gate_commands 键解析脚本未排除 `_timeout_seconds` 后缀，误判为待执行命令（系统性模式） | open | medium |
| DEBT0011 | SELF-GATE.md 审查成果文件按纯日期命名，跨任务同日复用会静默覆盖历史记录 | open | medium |
| DEBT0012 | `check-protocol-consistency.py --strict` 在 WARNING-only 时 exit 2，与 `&&` 串联的 gate_commands.P5 组合会因存量 WARNING 债务永久短路 | open | medium |

其余历史 DEBT（DEBT0001~0008）`task_id` 均非 TAG0016（含 TAG0006/TAG0008/TAG0013/`null`），与本
任务无直接关联，不在本次核对范围内变更其状态。

## 版本号变更确认（v0.53.0 → v0.54.0）

> 以下改动位置由主 Agent 后续亲自执行（bump-version + gate 验证通过后），本节仅确认应改哪里。

独立核实（`grep -rln "0\.53\.0"` 全仓库排除 `agate-workspace/tasks/**` 产出文件与
`.worktrees` 后），版本号物理落点共 **3 处**（未发现 `pyproject.toml`/`setup.py`/`VERSION` 等
额外版本文件）：

1. `README.md` L5：`[![version](https://img.shields.io/badge/version-v0.53.0-blue)]` → 改为
   `v0.54.0`
2. `README.zh-CN.md` L5：同样的版本徽章 → 改为 `v0.54.0`
   **[独立发现，非 dispatch-context 原文]**：dispatch-context 约束 2 只提到"README.md badge"，
   遗漏了中文 README。核查 `git log --oneline -- README.zh-CN.md` 发现 **TAG0015 的 P8 releaser
   提案同样遗漏了这一处**（commit `d310b61` 提交信息明确记录："README.md + README.zh-CN.md
   badge bump（releaser 提案遗漏中文 README，主 Agent 独立核实补上）"）——本次是同一类遗漏的
   第二次复现，特此显式标注，避免主 Agent 再次漏改。
3. `CHANGELOG.md` L11：新增 `## [0.54.0] - 2026-08-19` 节（当前顶部为
   `## [0.53.0] - 2026-08-19`），格式沿用既有节的"### 新增（TAGxxxx：任务名，RM-AGxxxx）"
   分组小标题风格，正文按 M1-M23 改动清单重新组织（不建议照抄同类任务模板，需逐条回查 P4/P7
   实际改动，参考 P2-design.md §1.1 M1-M23 表 + P7-consistency.md §3.3 落地核对表）。

## 临时资源清单

**无临时资源。**

本任务执行期间（P1-P7 全流程）未启动任何临时服务/进程（无 debug server、无临时 daemon）、未创建
任何临时数据（无测试数据库、无临时文件目录）、未做任何开发安装（无 editable install、无全局包
安装）——全部改动为协议文档编辑 + Python 脚本改动 + `pytest` 验证，独立核实与 dispatch-context
约束 4 结论一致。READY 收尾检查的"测试环境已清理"/"开发环境已还原"两节无需执行清理动作。

## Lessons Learned

| 类别 | 教训 | 来源任务 | 日期 |
|------|------|---------|------|
| 流程 | P8 releaser 对"版本文件位置"的核实不能只看 dispatch-context 给出的清单，须独立 grep 全仓库确认——本任务与 TAG0015 均出现"遗漏 README.zh-CN.md"的同一类问题，说明"双语 README 徽章各自独立、无单一权威源"本身是待改进点，未来可考虑 CHECK 12 式锚点表把两处徽章也纳入一致性守护范围，而非每次都靠人工 grep 补漏 | TAG0016 | 2026-08-19 |
| 架构 | "结构化权威锚点扫描"（CHECK 12 候选 2）相比"相似度阈值"（候选 1）更契合 `check-protocol-consistency.py` 既有"只做结构一致性、不碰语义一致性"的设计哲学——本任务的候选权衡过程本身可作为未来同类"要不要引入模糊/启发式判定"决策的参考案例：白名单式结构判定虽覆盖面窄于通用扫描，但可测试性与误报可控性显著更优，且与既有 CHECK 4/9/11 代码骨架复用 | TAG0016 | 2026-08-19 |
| 测试 | DEBT0010 揭示的" `_timeout_seconds` 后缀未被排除"问题是本任务自身在 P2/P3/P5 阶段实测复现的——协议自我改造类任务在自己的 P2-design.md 里声明新字段（`gate_commands.P3_timeout_seconds`）时，最容易第一时间踩中协议工具链对新字段的解析盲区；这类"用自己的新设计验证协议工具链健壮性"的 dogfooding 过程本身就是有效的缺陷发现手段，值得作为协议自身改造任务的常规副产物预期，而非意外 | TAG0016 | 2026-08-19 |

## 主 Agent 后续动作提醒（不由本文件执行）

- bump-version：README.md + README.zh-CN.md 徽章 v0.53.0 → v0.54.0；CHANGELOG.md 新增
  `[0.54.0]` 节
- bump 后重跑 `gate_commands.P5`（exit 0 + failed==0）
- `git log v0.53.0..HEAD --oneline` 对照新 CHANGELOG 节核对无遗漏
- git commit + git tag（本文件不执行）
- READY 收尾检查（含"协议一致性"节的干净 checkout 跑 `check-protocol-consistency.py` 0 ERROR）
