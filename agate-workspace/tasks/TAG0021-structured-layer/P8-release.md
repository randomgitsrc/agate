---
phase: P8
task_id: TAG0021-structured-layer
type: release
parent: P7-consistency.md
trace_id: TAG0021-P8-20260822
status: draft
created: 2026-08-22
agent: implementer
---

# P8 发布准备 — TAG0021 协议结构化层（RM-AG0022）

> 状态标记：[PROD_NOT_TOUCHED]（本次发布准备全程只读 + 产出本文件与 P8-progress.md；未执行任何
> bump-version / git commit / git tag；README/CHANGELOG/version.txt/UPGRADING 文件本体零改动；
> ~/.agate 稳定版与主 checkout 未触碰）

## 1. 版本决策

- `bump_type: minor`（v0.59.0 → **v0.60.0**）
- 理由：本任务新增协议结构化层（`rules/` YAML 数据层 + S-1~S-6 双向一致性 gate + 脚本迁移读 YAML +
  卡片渲染化），属**加功能 + 内部行为变化但向后兼容**——既非破坏公共 API/数据格式的 major，也非纯
  缺陷修复的 patch，按语义化版本取 minor。

## 2. 版本现状核对（发布检查②/③依据）

| 版本引用文件 | 现状 | 核对结论 |
|---|---|---|
| README.md version badge | `v0.59.0`（L5） | 待主 Agent bump → v0.60.0（badge + 版本历史表新增行） |
| README.zh-CN.md version badge | `v0.59.0`（L5） | 待主 Agent bump → v0.60.0 |
| version.txt | **不存在**（worktree 全树 glob 无命中） | 不在版本引用清单，无需改动 |
| CHANGELOG.md | 头为 `## [0.59.0] - 2026-08-22`，**无 [Unreleased] 占位** | 待主 Agent 在 [0.59.0] 上方插入 [0.60.0] 小节（建议文本见 §5） |
| agate/UPGRADING.md | `### v0.60.0 — 协议结构化层` 节已在 **L92**（P4/M2-7 写入） | ✅ 已就位，与本次发布一致（① 三脚本切 YAML 权威源 ② 一致性 gate 提升阻断 ③ rules/ 纯增量） |
| 最新 git tag | `v0.59.0`（`git describe --tags --abbrev=0`） | 与 badge 一致；tag v0.60.0 待主 Agent 在 gate 验证后创建 |

**结论**：UPGRADING v0.60.0 节已由 P4 写入且内容与 M2 破坏性变更逐条一致（P7 §3.3 亦核验），其余
版本文件改动全部标「待主 Agent 执行」，本文件不落盘任何版本文件变更。

## 3. 发布检查命令结果（releaser 自查，不 gate；命令来自 P2-design.md gate_commands）

| # | 命令 | 结果 | 判定 |
|---|---|---|---|
| ① | `python3 -m pytest agate/tests/ -q --tb=no -p no:cacheprovider --basetemp=.../dist/` | **1198 passed, 2 failed, 2 skipped**（120s） | 2 failed 均为已登记环境假象（见下），1198+2+2=1202 与 count-tests 自洽 |
| ② | `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` | **0 ERROR**，318 WARNING（既有叙事文件死链基线，与本任务无关） | exit 0 ✅ |
| ③ | `python3 agate/scripts/check-structure-consistency.py` | S1-phases/S2-workflow/S3-cards/S4-scripts/S5-schema/S6-references/S0-numbers **全 OK** | exit 0 ✅ |
| ④ | `python3 agate/scripts/check-yaml-schema.py` | SCHEMA-phases / SCHEMA-dispatch / SCHEMA-roles **全 OK** | exit 0 ✅ |
| ⑤ | `bash agate/tests/scripts/count-tests.sh` | **1202**（pytest collect-only 口径）≥ 749 基线 | exit 0 ✅ |
| ⑥ | `python3 agate/scripts/check-platform-assumptions.py`（P2 gate_commands 完整面补充） | 0 命中 | exit 0 ✅ |
| ⑦ | `ruff check agate/scripts/ agate/tests/`（/home/kity/.local/bin/ruff，PATH 无 ruff） | **All checks passed** | exit 0 ✅ |

**① 的 2 failed 归因（环境假象，非回归，与 P5/P6/P6.5 记录一致，本 P8 独立复现证明）**：

- `test_check_routing.py::test_bdd_7_thin_score_anomaly_git_ok_false_exit_1`：测试在"非 git 上下文"
  （tmp 任务目录在 git 仓库外 → run_git 失败 → `git_ok: false` → exit 1）下断言。本地沙箱 /tmp 只读
  迫使 pytest `--basetemp=worktree 内 dist/`，tmp 目录在 git 仓库内，`git rev-parse` 上溯命中仓库 →
  `git_ok: true` → exit 0。**证明**：换 `--basetemp=/tmp/p8-proof/`（仓库外）复跑 → `1 passed`。
  属 [CAPABILITY_GAP] 沙箱 basetemp 固有项（P4 M0 已登记），与 TAG0021 改动零耦合（check-routing /
  agate-risk-score 未被触碰）。
- `test_env_adapt_docs.py::test_bdd_25_consistency_zero_error`：共享 basetemp 污染——同一次全量跑的
  test_bdd_11 残留 `dist/test_bdd_11_t001_backfill_entr0/tech-debt.md`（引用不存在的
  docs/reviews 文件）被 test_bdd_25 的 consistency 扫描扫入 → 12 ERROR。**证明**：清空 dist/ 根后
  换 `--basetemp=dist/p8-clean/` 复跑 → `1 passed`。CI 默认每测试独立 /tmp 目录，无此污染。

## 4. 债务清单核对（debt_check）

`debt_check: reviewed`

已核对 `{AGATE_WORKSPACE}/debt/tech-debt.md`（17 条 DEBT）。本任务相关债务 id 清单：

| DEBT id | 状态 | 与本任务关系 |
|---|---|---|
| DEBT0010 | closed（TAG0017） | **同根模式**：`_timeout_seconds` 键解析缺陷是"grep 解析 md 脆弱"的实证（P0-brief 引用）；本任务结构化层（dispatch.yaml `gate_commands_syntax` + `is_legal_gate_key` + S-4 登记）正是对该系统性模式的收敛，不重开 |
| DEBT0007 | open | check-pruning.py 是 M1/M2 三脚本之一（本任务已触碰），但该债的测试隔离缺口（依赖外层真实 git 暂存区）未被本任务修改；仍 open，不阻断发布 |
| DEBT0014 | open | pre-commit-gate.py 被 M2-4 追加结构一致性 step；该债（Windows Store python3 占位符探测）与 M2 改动无冲突，仍 open，不阻断发布 |
| DEBT0015 | open | env_constraints 声明性字段无执行绑定；本任务已通过 gate_commands 把 basetemp/命令落到实处（局部改善），债主体仍 open，不阻断发布 |

结论：无本任务引入的新债务；相关既有 open 债务均不影响本次发布（不阻断 BDD-17）。

## 5. CHANGELOG [Unreleased] → v0.60.0 建议变更摘要（releaser 整理，主 Agent 执行写入）

> ⚠️ 现状：CHANGELOG.md 头为 `## [0.59.0]`，**当前无 [Unreleased] 占位符**。建议主 Agent 在
> [0.59.0] 上方新增 `## [Unreleased]` 占位 + 本小节内容，版本固化时再改标题为 `[0.60.0]`（Keep a
> Changelog 惯例）；或直接插入下方 `[0.60.0]` 小节。M0-M3 变更要点如下（源自 P2-design §1.1 /
> P4-implementation M0-M3 改动清单 / P7 §3.3）：

```markdown
## [0.60.0] - 2026-08-22

### 新增（TAG0021：协议结构化层 rules/ + S-1~S-6 双向一致性，RM-AG0022）

- **结构化规则权威源 `agate/rules/`（M0，纯增量）**：`phases.yaml` / `dispatch.yaml` / `roles.yaml`
  承载可判定规则（阶段定义 / 派发三铁律 / 五模式编排 / gate_commands 语法 / 角色映射 / C8 机械映射），
  markdown 保留为人类叙事层；配套 `rules/schema/*.schema.json`（draft-07 子集）+ 手写校验器
  `check-yaml-schema.py`（不引入 jsonschema 依赖）。
- **双向一致性 gate `check-structure-consistency.py`（S-1~S-6 + S0）**：phases↔WORKFLOW 总览表双向
  对账（S-1/S-2）、YAML→卡片（S-3）、YAML→脚本登记（S-4）、schema 校验（S-5）、引用完整性（S-6）、
  S 编号自校验（S0）；ERROR 即 exit 1。
- **三脚本双跑对账模式（M1）**：`agate-read-gate-commands` / `check-pruning` / `check-gate`（P2 分支）
  grep↔YAML 结构化双读，差异输出 stderr `RECONCILE WARNING` + 汇总计数，退出码语义不变（告警不阻断，
  `AGATE_RECONCILE` 可关）；对账工具函数入 `agate_common`（reconcile_field / read_rules_yaml /
  is_legal_gate_key 等）。
- **切换权威源 + 阻断提升（M2）**：gate_commands 块解析 / 四字段计数迁至 `agate_common` 共享助手单点
  （parse_gate_commands_block / count_p2_declared_fields），删除消费脚本内联正则；协议规则读
  rules/*.yaml；S-1/S-2 漂移进 **pre-commit 独立 step + CI consistency job 追加步骤**（exit 1 阻断）——
  判定语义与 v0.59 逐字节等价（破坏性变更见 UPGRADING v0.60.0）。
- **卡片渲染化 + 稳定版隔离（M3）**：`agate-next-card.py` 内嵌渲染器 render_card()，卡片门槛 / 产出 /
  派发 / gate 规则 / retry 上限节由 phases.yaml 渲染（正式卡片字节稳定、sha256 契约保持，渲染仅对裸
  模板生效）；S-3 升级为全卡逐字段对账 + 孤儿卡片防护；渲染经 AGATE_ROOT 解析隔离（worktree 未发布
  YAML 不污染稳定版注入）。
- 新增 34 测试用例（count-tests 1168 → 1202，≥ 749 基线）；全量 pytest 1198 passed（2 环境假象已登记）。

### 破坏性变更

见 `agate/UPGRADING.md` v0.60.0 节（P4 已写入）：① 三脚本从 grep 解析 md 切为读 YAML 权威源 +
对账兜底（判定语义不变，旧正文格式任务靠对账可跑，会持续出 RECONCILE 差异告警）② 一致性 gate 提升为
pre-commit + CI 阻断（自定义 AGATE_ROOT 覆盖需含 rules/ 目录）③ rules/ 数据层纯增量，既有 rules/*.md
保留不动。
```

## 6. 临时资源清单（releaser → 主 Agent 交接；主 Agent P8 gate 后按此清理）

本任务执行期间产生的临时资源（含 P4/P5/P8）：

| 类型 | 资源 | 位置 | 清理动作 |
|---|---|---|---|
| pytest basetemp 根 | 全量/分片测试 basetemp | `agate-TAG0021/dist/`（P2 声明可写目录） | 主 Agent READY 收尾时整目录删除（含本次 P8 的 p8-clean / p8-isolate2 子目录与 pytest 残留） |
| pytest basetemp（仓库外证明用） | test_bdd_7 隔离复跑 basetemp | `/tmp/p8-proof/` | 删除 |
| 开发工具（非本任务安装） | ruff 二进制 | `/home/kity/.local/bin/ruff`（PATH 无 ruff，需绝对路径调用） | **不删除**（既有环境工具，非本任务安装）；仅记录依赖路径，README 收尾检查无需处理 |
| 临时服务/进程 | **无** | — | 纯脚本任务，全程未启动任何服务 / daemon / 网络监听 |
| 临时数据（任务产出，非清理项） | gate-events.jsonl | `tasks/TAG0021-structured-layer/gate-events.jsonl` | 属任务目录产物（append-only 事件账本），随任务提交，不删 |
| 缓存 | pytest cache | `-p no:cacheprovider` 全程禁用 | 无需处理 |

## 7. Lessons Learned（2-3 条关键教训，主 Agent 汇入 docs/notes/lessons.md）

1. **[测试] 环境假象要用可复现证据分类，而非凭记录放行**：P5/P6 记录的两个 pytest 环境假象
   （test_bdd_7 依赖"basetemp 在 git 仓库外"、test_bdd_25 共享 basetemp 污染）在 P8 全量重跑中
   原样复现。本次没有直接沿用"已知假象"结论，而是各自做了独立证明——test_bdd_7 换 `/tmp` 仓库外
   basetemp 转绿、test_bdd_25 清空 dist/ 根后转绿。结论：发布期重跑撞上已知假象时，必须换一个能
   复现"转绿"的环境条件（换 basetemp 位置 / 清共享根）证明后才可记为"非回归"，防止把真实回归误放行。
2. **[流程] `--basetemp` 指向 git 仓库内目录有双重副作用，测试设计应避免隐含"cwd 在 git 仓库外"假设**：
   为绕开 /tmp 只读，agate 自身任务把 pytest basetemp 放 worktree `dist/`，但 (a) git 解析会上溯命中
   仓库，破坏依赖"非 git 上下文"语义的测试（test_bdd_7）；(b) 共享根目录让早跑测试的 fixture 残留
   污染后跑测试的扫描面（test_bdd_11 → test_bdd_25）。该差异在 CI（Linux 默认 /tmp 可写且在仓库外）
   与本地沙箱间长期存在，建议在 P0/P2 env_constraints 显式声明"basetemp 位置影响 git 语义"，
   并在测试设计时避免 `git rev-parse` 隐含对 cwd 仓库归属的假设。
3. **[工具] 非交互 shell 不读 bashrc，工具路径要写绝对路径**：本环境 `ruff` 不在 PATH（需
   `/home/kity/.local/bin/ruff`），与 DEBT0014 的 python 探测同类——发布检查命令 / gate_commands
   应显式写解释器与工具的绝对路径或可执行性探测，避免 "command not found"（exit 127）被误判为回归。

## 8. 门槛自检（完成判定对照）

- [x] `bump_type: minor`（§1）
- [x] `debt_check: reviewed` + 相关债务 id 清单（§4）
- [x] 版本号变更确认：README badge / CHANGELOG / version.txt / UPGRADING v0.60.0 节——全部「待执行 /
  已就位」核对（§2）
- [x] CHANGELOG [Unreleased] → v0.60.0 建议变更摘要（§5）
- [x] 临时资源清单（§6）
- [x] Lessons Learned（§7）
- [x] 发布检查命令结果已记录（§3）
- [x] 未执行任何 git commit / tag（git status 无 bump 写入；§2 / 状态标记）
- [x] 状态标记 [PROD_NOT_TOUCHED]
