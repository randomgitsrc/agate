---
phase: P8
task_id: TAG0028
type: release
parent: P7-consistency.md
trace_id: TAG0028-P8-20260903
status: draft
created: '2026-09-03'
agent: implementer
bump_type: minor
---
# P8-release — TAG0028 subagent 存活可观测性与受控自主再派发（RM-AG0055）发布准备

> parent: P7-consistency.md（approved：blocker_count=0 / deviation_count=3（0 critical）/ DESIGN_GAP
> 4/4 配对 REVIEWED / CODE-MAP 3/3 SYNC）
> 本文件由 releaser subagent（implementer P8 模式）产出，只做发布准备——**不执行 git commit /
> git tag / 不改 README / CHANGELOG / UPGRADING / roadmap 正文**（bump 与版本文件改动由主 Agent
> 在 gate 验证通过后亲自执行）。
> 环境隔离：[PROD_NOT_TOUCHED]（全程只读分析 + 产出本文件与 P8-progress.md，未触碰协议本体/生产面）。

## 1. bump_type 建议与理由

**bump_type: minor**（v0.66.0 → v0.67.0）

理由（逐条，对齐 dispatch-context 判定规则）：

1. **新增向后兼容的协议功能（semver minor 主判据）**：本任务新增 3 个协议脚本
   `agate/scripts/agate-cmdstream-ir.py`（CommandRecord 统一 IR：十字段字段契约 + JSON 往返）/
   `agate-cmdstream-adapters.py`（适配器基类契约 + 三平台适配器 + 显式注册表 ADAPTERS）/
   `agate-cmdstream-detect.py`（检测引擎 FROZEN/SPIN/NORMAL + 阈值全兜底 + CLI 三子命令）；
   协议文档新增/改写（dispatch-protocol.md 存活检查节 + 心跳生命周期 + 自主再派发节、
   role-system.md 子派发权限边界节、dispatch-context 模板声明位）——
   属 "new backwards-compatible functionality" → minor。
2. **向后兼容性已客观验证（非 major）**：`check-gate.py` / `check-state-transition.py` 返回约定
   （exit 0/1/2 三态）**未改**（P2 N1/N2 不改声明 + BDD-33）；`.state.yaml` schema 未动；
   3 个 hook 薄壳未动（P7 改动清单无 `.sh`）；dispatch-context 模板只补节不改骨架（S-6）；
   心跳判定与 gate 判定是两套独立信号（P0 out-of-scope：不改变既有 gate 返回约定）→ 非 major。
3. **非 bugfix 批次 / 非 hotfix**：本任务是协议机制升级（RM-AG0055 功能落地），不是 patch 级
   修复 → 非 patch。
4. **测试缺陷不影响版本号决策**：P3 test_bdd_3 断言结构性矛盾（DESIGN_GAP-1）为测试设计缺陷，
   已由 test-designer fix1 修复闭环，不纳入版本号考量。
5. **单仓单版本**：pyproject.toml 无 version 字段（单包文档型项目），版本以 README badge +
   CHANGELOG 为准；P2 frontmatter `packages: [agate]` 单包，P8 卡「多包发布拆批」不触发，
   无需合并 subagent。

版本号变更确认（供主 Agent bump 时核对）：

| 项 | 现状（实测，2026-09-03） | 目标 |
|---|---|---|
| 最新 git tag | v0.66.0（`git describe --tags --abbrev=0` 实测） | v0.67.0（待主 Agent 创建并推送） |
| README.md version badge（:12） | v0.66.0 | v0.67.0 |
| README.zh-CN.md version badge（:12） | v0.66.0 | v0.67.0 |
| CHANGELOG.md | [Unreleased] 空段（仅占位分隔线） | [0.67.0] - <发布日> |
| pyproject.toml | 无 version 字段 | 不动 |

## 2. debt_check

**debt_check: reviewed**

已读 `agate-workspace/debt/tech-debt.md`（2026-09-03 实读，908 行，含 DEBT0024/0025/0026，
均为 TAG0027 复盘登记，status: open / priority: medium）。本任务改动面无新增 DEBT 登记
（tech-debt.md 按 task_id 反查无 TAG0028 条目）。与本次发布直接相关的关联 DEBT：

| id | priority | 简述 | 与本任务关系 |
|---|---|---|---|
| DEBT0024 | medium | P3 TDD 测试夹具构造"假 gate exit"，未用真实 check-gate 实测 | 无交集（本任务 P3 夹具走真实 verify 锚 + 真实 gate_commands；GAP-1 为断言结构性矛盾，已 fix1 闭环） |
| DEBT0025 | medium | 新增 CHECK 上线前未先全量扫描存量命中 | 无交集（本任务未新增 CHECK；新脚本入 CHECK 10 脚本名漂移检测面由平铺方案天然覆盖，P2 候选 A 论证） |
| DEBT0026 | medium | 单 agent 大任务上下文耗尽（>5 文件/大文档清理类） | **直接相关**——本任务 Phase 4「受控自主再派发」正是 DEBT0026 closure_criteria 所指根治方向（subagent 内部自主拆批）；本任务落地机制后按后续任务评估关闭，本次不关闭 |

- 结论：`debt_check: reviewed`——已核对关联 DEBT0024/0025/0026（可引用、不必关闭）；
  其余 open 债务与本任务改动面无交集，均不阻断发布。

## 3. CHANGELOG 条目建议（草案，主 Agent 定稿）

CHANGELOG `[Unreleased]` 段当前为空（仅占位分隔线，实测），本版本段 = 仅本任务条目。
建议 `[Unreleased]` → `[0.67.0] - <发布日>`，分「新增」「变更」子节（对齐 0.66.0 / 0.65.0
章节先例）：

```markdown
### 新增（TAG0028：subagent 存活可观测性与受控自主再派发，RM-AG0055）

- **命令流检测三脚本**：`agate-cmdstream-ir.py`（CommandRecord 统一 IR：十字段字段契约 +
  JSON 往返）/ `agate-cmdstream-adapters.py`（CommandStreamAdapter 基类契约 + 三平台适配器
  ——Claude Code JSONL / OpenCode SQLite / DSH JSONL.zstd（spawn node 解压隔离）+ 显式注册表
  ADAPTERS + 子 agent 会话定位）/ `agate-cmdstream-detect.py`（检测引擎：调用冻结
  expected×2 + 兜底 300/900s、活动冻结 60/300s、无效重复窗口 10 内 ≥5、REPEAT_UNIQUE_MIN=3
  信息级、截断排除、轮询误报标注；阈值可配置 maintainability.yaml 节，缺失/损坏全兜底；
  CLI 子命令 list-sessions / read-commands / detect）。
- **存活/卡死判定职责改由命令流日志承担**：dispatch-protocol.md「Subagent 安全 → 硬超时保护 →
  存活检查」节改写——命令流日志（平台会话记录外部活动信号）承担存活/卡死判定，progress.md
  保留"语义进展"职责不变，两套信号分工明确。
- **心跳文件生命周期**：`.heartbeat` / `.heartbeat.child-{n}` 命名规范 + 审计豁免显式登记
  （check-p6-provenance.py `_find_files` 隐藏文件过滤天然跳过，注释级登记确认）+ 清理时机
  （任务结束由产生方清理，异常遗留由派发前置检查清空，复用 agate-archive-stale-outputs 模式）。
- **受控自主再派发**：role-system.md「子派发权限边界」节——执行角色（analyst/architect/
  implementer/verifier）可被授予子派发权限，两条硬边界（子任务不写 .state.yaml / 写权限是父
  权限严格子集）；judge 类角色例外（不开放 Agent/subagent_fork，信息隔离冲突）；dispatch-context
  模板补「不启用子派发能力」显式声明位。
- **maintainability.yaml 新增 cmdstream_detection 节**：检测阈值（300/900/60/300/10/5 +
  repeat_unique_min=3 + expected ×2/30s），缺失/损坏兜底协议默认值，不报错。
- 新增 pytest 用例（tag0028 批，P5 实测 1434 passed + 0 failed + 2 skipped，count-tests 不漂移）。

### 变更

- **dispatch-protocol.md 存活检查节改写**（见上「新增」第 2 条，属协议文档职责重定义——
  存活判定信号源切换，既有 progress.md 语义不变，不破坏既有 gate 返回约定）。
```

> 注：以上为草案文本，主 Agent 按定稿口径合并/拆分。区间内 main 侧非任务 commit（设计文档 v5
> 系列 + DEBT0024-26 登记 + site 博客 post-06 + publish-checklist，见 §8）是否补录本版本段
> 「其他」子节（对齐 0.64.0「其他」段先例），由主 Agent 定夺；本草案只覆盖 TAG0028 范围。

## 4. UPGRADING 章节建议（主 Agent 亲自执行）

**checklist 项（v0.62.0 教训）**：新版本**必须在 `agate/UPGRADING.md` §3 新增 v0.67.0 章节——
无破坏性变更也要写，标题下首行标注「（无破坏性变更，零迁移动作）」；CHECK 13（CHANGELOG↔
UPGRADING 章节对应性）会机械校验漏写。

章节要点草案（对齐 v0.66.0 章节结构，插入位置 = v0.66.0 章节上方）：

1. **总标注**：本版本无破坏性变更，零迁移动作——未改 `.state.yaml` schema / 既有任务文件
   格式 / 3 个 hook 薄壳（P7 改动清单核对无 `.sh` 改动），无需重跑 `install-hook.py`
   （软链布局 `git pull` 即生效；Windows 复制模式重跑 SETUP.md 步骤 2 的 `cp`）。
2. **① 新增命令流检测机制——对已有任务零影响**：三个新脚本（ir/adapters/detect）为纯新增
   消费方；检测输出定位"证据 + 触发核查"（不自动判死），不改变既有存活机制（progress.md
   语义进展职责不变）；`maintainability.yaml` 新增 `cmdstream_detection:` 节为可选配置，
   缺失/损坏兜底默认值，无强制、无升级动作。
3. **② 受控自主再派发——对已有 subagent 零影响**：子派发权限为"可被授予"而非默认开放，
   未授权 subagent 行为不变；judge 类角色不适用；dispatch-context 模板新增「不启用子派发
   能力」声明位为可选字段。
4. **③ 升级动作**：`git pull` 即完成；无迁移动作。

## 5. roadmap 回写 checklist（RM-AG0043 硬校验，主 Agent 执行）

- [ ] `agate-workspace/roadmap/roadmap.md` :61 **RM-AG0055** 行：「状态」列 `scheduled` → `done`
  （P8 gate 硬校验 RM-AG0043：关联任务 TAG0028 的 RM 条目未回写 done 即阻断）。已实测：
  roadmap.md 全文按 task_id 反查 TAG0028 仅 :61 一处
  （`| RM-AG0055 | … | scheduled | … | TAG0028 | 2026-09-03 | 2026-09-03 |`）。
- [ ] 回写时核对列结构：表头 7 列（id/标题/状态/来源/关联任务/创建/更新），按表内 done 行惯例
  同步「更新」列日期为回写当日（参照 RM-AG0054 done 行口径）。
- [ ] 回写与 P8 阶段 commit 同批（.state.yaml phase 与本次产出一致的同一 commit 产出面）。

## 6. 版本引用文件 checklist（Agateon 仓库特有，主 Agent 逐项执行）

| # | 文件 | 动作 | 现状锚点（实测） |
|---|------|------|---------|
| 1 | `README.md` | version badge v0.66.0 → v0.67.0 | :12 badge 行 |
| 2 | `README.zh-CN.md` | 中文镜像 badge 同步（v0.65.0/v0.66.0 先例两 README 同批更新）；bump 时 `grep -n "v0.66" README*.md` 复核无遗漏 | :12 badge 行 |
| 3 | `CHANGELOG.md` | [Unreleased] → [0.67.0]（§3 草案）+ 追加本任务条目 | §3 草案 |
| 4 | `agate/UPGRADING.md` | §3 新增 v0.67.0 章节（无破坏性变更也写；CHECK 13 对应性校验） | §4 要点草案 |
| 5 | 其余硬编码版本 | **无**——文档优先写「稳定版」不写死版本号；pyproject.toml 无 version 字段，不动；docs/design-notes 内 v0.66.0 引用为设计文档历史叙事（非版本引用面），不改 | 已核 |

## 7. AUDIT7 验证计划（主 Agent 执行，本文件不含结果预判）

命令（worktree 根执行）：

```bash
python3 agate/scripts/check-p6-provenance.py --audit7-only agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch
```

判定：读 stdout 的 `AUDIT7_RESULT: <reuse_allowed|reuse_blocked|no_reuse_claim_possible>` 行
（配合 exit code）：

| 分支 | 判定 | 动作 |
|------|------|------|
| reuse_allowed（exit 0） | 复用 | 复用 P5 阶段同一份 `P5-test-results/`（unit.md + fail-list.txt），不重新执行 gate_commands.P5 |
| reuse_blocked（exit 1）或 no_reuse_claim_possible（exit 0 但非 reuse_allowed） | 完整重跑 | 重跑 P2 §4 gate_commands 全部键，要求各命令 exit 0 且 pytest failed==0，结果写入任务目录留痕 |

**DEBT0013 时序注意（重跑分支触发时必须遵守）**：`gate_commands.P5_consistency`（
`check-protocol-consistency.py --strict-errors-only`）含 CHECK 7（README version badge 与最新
git tag 一致性）——P5 重跑应安排在 **commit + 创建 git tag v0.67.0 之后**，而非 bump 版本文件
后立即重跑（bump 完成、tag 未建的中间态 CHECK 7 必报 `badge v0.67.0 != tag v0.66.0` ERROR，
这是设计使然，非回归；先 tag 后重跑即 0 ERROR）。

发布检查命令全清单（P2 §4 gate_commands 原文，主 Agent 按 AUDIT7 分支决定复用或重跑）：

```yaml
P5: "python3 -m pytest agate/tests/ -q --tb=no -n auto"   # timeout 600s（worktree 根跑）
P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"  # 120s，worktree 版
P5_cmdstream_verify: "python3 docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verify-heartbeat-cmdstream/verify_cmdstream_detection.py"  # 120s
P5_shellcheck: "shellcheck -S warning agate/scripts/pre-commit-gate.sh agate/scripts/commit-msg-self-gate.sh agate/scripts/pre-push-gate.sh"  # 120s
P5_count_tests: "bash agate/tests/scripts/count-tests.sh"  # 120s
```

## 8. git log v0.66.0..HEAD 对照结论

命令：`git log v0.66.0..HEAD --oneline`（2026-09-03 实测）。

1. **任务主流程链齐整**：999c672（RM-AG0055 立项 P0）→ 20843d0（交接单 PR #261 合并）→
   P1 b6581e3 → P2 d120453 / 2f1d887（fix1/fix2）→ P3 50d48c6 → P4 6964dbf / 34366ab
   （fix3 R2 回归修复）→ P5 700f074 → P6 58569fa → P6.5 6fd4e2b → P7 6aba3e4（HEAD）。
   改动面全部落在 `agate/scripts/`（3 新脚本 + check-p6-provenance.py 登记）、`agate/`
   （dispatch-protocol.md / role-system.md / dispatch-context.md 模板）、
   `agate-workspace/maintainability.yaml`、`agate/tests/`（新测试）与任务目录——与 P2 §1.1
   Modify 表（M1-M10）逐文件吻合，无跨包改动（P7 §3 同核）。
2. **v0.66.0 发布于 2026-09-03（tag 实测）**，本任务 commit 全部在其后——本任务改动未入
   CHANGELOG，由本次 P8 补录（§3 草案）；机制性改动与 commit 内容一一对应（P4 commit 6964dbf
   已含 self-gate-review: 声明，P7 §3 核对）。
3. **区间内 main 侧非任务 commit**：设计文档 v5 系列（7e3dc4e / ddd6a00 / 43e5081 / d796d16 /
   6695c42 / 077d978）+ TAG0027 清理与 DEBT 登记（7750a23 / 365b211 / 527ce48）+ site 博客
   post-06（6731fad / 595aafc）——是否随本版本段发布补录「其他」子节由主 Agent 定夺
   （属 v0.66.0 之后合入内容；site 为产品 Web 层，在协议 gate 治理之外）。
4. **记录级备注（不阻断）**：P4 commit 6964dbf message 中 self-gate-review 清单与 P0-brief
   env_constraints 一致；三脚本 CODE-MAP 登记已在 P4 完成（P7 §5 3/3 [CODE_MAP_SYNC:]，与
   TAG0027 的 [CODE_MAP_DRIFT] 教训不同，本次无遗留登记欠账）。

## 9. 主 Agent 动作清单（P8 gate 通过后按序执行）

| # | 动作 | 依据 |
|---|------|------|
| 1 | `check-gate.py P8 $TASK_DIR` 跑 gate（bump_type/debt_check 字段 + roadmap done + tag 检查面） | P8 卡 gate 规则 |
| 2 | AUDIT7 判定 P5 证据（§7）：reuse_allowed → 复用；否则重跑 gate_commands 全键（DEBT0013：先 tag 后重跑） | P8 卡 gate 规则 |
| 3 | README.md:12 + README.zh-CN.md:12 badge v0.66.0 → v0.67.0 | §6 |
| 4 | CHANGELOG [Unreleased] → [0.67.0]（§3 草案 + 定夺 main 侧非任务 commit 是否补录「其他」） | §3 |
| 5 | UPGRADING.md §3 新增 v0.67.0 章节（无破坏性变更也写，CHECK 13） | §4 |
| 6 | roadmap.md:61 RM-AG0055 scheduled → done（7 列结构 + 更新日期回写当日） | §5（RM-AG0043） |
| 7 | `git tag v0.67.0 && git push origin v0.67.0` + `git ls-remote --tags origin v0.67.0` 验证远端到达（git push 默认不推 tag） | AGENTS.md 版本发布清单 |
| 8 | release PR **普通 merge（--no-ff）禁止 squash**（CHECK 7 / G-5 describe 依赖 tag 与 main 同轨） | AGENTS.md（v0.31.0 事故） |
| 9 | P8 commit message 须含 `self-gate-review:`（触发面：agate/scripts/agate-cmdstream-*.py 新增 + check-p6-provenance.py 修改 + dispatch-protocol.md/role-system.md/dispatch-context.md 协议改写） | P0 env_constraints / §12 |
| 10 | G-5 最终验证：`git fetch origin && git describe --tags origin/main` == v0.67.0；`git merge-base --is-ancestor v0.67.0 origin/main` exit 0；合并后 CI 全绿 | AGENTS.md |
| 11 | READY 收尾检查（§10 临时资源清单清理 + 干净 checkout 跑 consistency 0 ERROR + 无 PROD_TOUCHED + 复盘判断） | P8 卡 READY 清单 |

## 10. 临时资源清单（releaser → 主 Agent READY 收尾交接）

| 类别 | 内容 |
|------|------|
| 临时服务/进程 | **无**——本任务全程未启动任何服务 / daemon / 调试进程（P2 env_constraints：pytest 仅本地跑；P5 无 debug server） |
| 临时端口 | **无**（DSH zstd 解压 spawn node 为进程内子进程，命令结束即回收，无常驻端口） |
| 开发安装 | **无**——未做 editable install / 全局包安装（pytest / pyyaml / ruff / pytest-xdist 均用既有环境） |
| 临时数据 | pytest 临时目录由 pytest 自管理；P5-test-results/（unit.md + fail-list.txt）已随任务目录入库（非临时资源）；`.heartbeat*` 心跳文件按协议由产生方清理、异常遗留由派发前置检查清空（本任务为纯协议层开发，实查任务目录无 .heartbeat* 残留） |
| 残留进程核查 | READY 收尾按 P8 卡逐项实际执行检查命令（`ps aux` 确认无 debug 进程 / `git status` 确认工作区干净），不得仅凭本清单打勾 |

## 11. Lessons Learned（主 Agent 汇入 docs/notes/lessons.md）

1. **架构 / 外部数据源脆弱性须收敛在适配器内**：三平台命令流格式完全不同（JSONL / SQLite /
   JSONL.zstd）且 Claude Code 与 DSH 无数字 exit code（靠文本前缀 "Exit code N" / "Error:"），
   平台改输出格式则解析规则需跟随更新——统一 CommandRecord IR + 每平台一个适配器 + 显式注册表
   （新增平台只写适配器，检测引擎零改动），差异点沉淀在验证记录文档 + 脱敏 fixture 回归锁定。
   （来源任务 TAG0028，2026-09-03）
2. **架构 / 两套信号职责必须显式分工**：存活/卡死判定（命令流日志）与语义进展（progress.md）
   是两套独立信号，改写协议节时须明确边界表述（命令流=存活判定、progress=语义进展），避免
   职责漂移导致存活判定回归不可验证（RM-AG0023 关系边界）。心跳文件命名进协议命名空间后，
   审计豁免靠隐藏文件过滤天然覆盖，但须**显式登记确认**（check-p6-provenance.py 注释级）而非
   默认假设。 （来源任务 TAG0028，2026-09-03）
3. **流程 / 测试断言与 fixture 数据矛盾时先归因再动**：P3 test_bdd_3 用 command 建字典，
   fixture 两条记录同 command 不同 exit/truncated，断言要求单条记录同时满足矛盾条件——任何
   实现都无法通过，属测试设计缺陷而非实现缺陷；正确动作是回派 test-designer 修复（过滤式
   匹配），不改测试断言迁就实现、不标实现缺陷。 （来源任务 TAG0028，2026-09-03）

## 12. SELF-GATE 注记（触发面声明）

本任务触发 SELF-GATE（P0-brief env_constraints + P2 §1.1 R9）：

- 触发文件面：`agate/scripts/agate-cmdstream-ir.py` / `agate-cmdstream-adapters.py` /
  `agate-cmdstream-detect.py`（新增）、`agate/scripts/check-p6-provenance.py`（心跳豁免登记）、
  `agate/dispatch-protocol.md` / `agate/role-system.md` / `agate/assets/templates/dispatch-context.md`
  （协议改写）。
- **P8 commit（主 Agent 执行）message 必须含 `self-gate-review:`**（P4 commit 6964dbf 已含，
  P8 属协议本体最终发布 commit，同触发面）；协议文档改动已由 P5_consistency
  （--strict-errors-only）0 ERROR 验证。
