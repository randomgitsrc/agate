---
phase: P8
task_id: TAG0026
type: release
parent: P7-consistency.md
trace_id: TAG0026-P8-20260830
created: '2026-08-30'
status: draft
agent: implementer
bump_type: minor
debt_check: reviewed
---
# P8-release — TAG0026 维护性反模式 gate（RM-AG0046）发布准备

> parent: P7-consistency.md（P7 通过：blocker=0，deviation=1 WARNING 级非阻断）
> 本文件由 releaser subagent（implementer P8 模式）产出，只做发布准备，**不执行 git commit / git tag / 不改 README / pyproject / CHANGELOG / UPGRADING 正文**——bump 与版本文件改动由主 Agent 在 gate 验证通过后亲自执行。

[PROD_NOT_TOUCHED]

## 1. bump_type 建议与理由

**bump_type: minor**（v0.64.0 → v0.65.0）

理由（逐条）：

1. **新增协议功能**：本任务新增 `agate/scripts/check-maintainability.py` 检测器 + `check-gate.py` gate_p4 三重门槛挂载 + `agate/assets/templates/known-violations-template.md` 模板 + P4/P6 phase-cards 机制条目 + `agate-workspace/maintainability.yaml` 示例配置——属 semver 语义的 "new backwards-compatible functionality" → minor。
2. **无破坏性变更**：不改既有协议语义/数据格式。唯一行为扩展是 gate_p4 新增一步，且 violations 为空 / 检测未部署（ImportError）/ git 通道不可用三场景下行为与改动前完全一致（P4-review 已核，P7 §3.3 第一手复核）；新步骤只产生 `return 1` 或继续向下，不新增 `return 2`；既有 ①②③④ 步语义与顺序不变（P2 §1.2 锁定，P4 落实）。
3. **单仓单版本**：pyproject.toml 无 version 字段（单包文档型项目），版本以 README badge + CHANGELOG 为准，无逐包出号。

版本号变更确认（供主 Agent 执行时核对）：

| 项 | 现状 | 目标 |
|---|---|---|
| 最新 git tag | v0.64.0（2026-08-26） | v0.65.0（待主 Agent 创建并推送） |
| README.md version badge（:12 附近） | v0.64.0 | v0.65.0 |
| pyproject.toml | 无 version 字段 | 不动（单包文档型项目，版本以 badge + CHANGELOG 为准） |

多包说明：P2 frontmatter `packages: [agate-scripts, agate-tests, agate-phase-cards, agate-templates]` 是**影响面分组**而非独立可发包——单仓单版本下四包同随 v0.65.0 一次发布，P8 卡「多包发布拆批」不触发，无需合并 subagent。

## 2. debt_check

**debt_check: reviewed**

已读 `agate-workspace/debt/tech-debt.md`（2026-08-30 实测），当前 **open 条目共 11 条**：

| id | priority | 简述 | 与本任务关系 |
|---|---|---|---|
| DEBT0002 | medium | 离线包 compute_sha256 双实现漂移 | 无关 |
| DEBT0003 | medium | 离线 manifest 未签名 | 无关 |
| DEBT0004 | medium | 卸载引用保护扫描限流漏扫旧引用 | 无关 |
| DEBT0007 | medium | test_check_pruning.py 部分用例依赖真实暂存区 | 无关 |
| DEBT0008 | low | agate-feedback 匿名化正则误伤中文散文 | 无关 |
| DEBT0014 | medium | Windows Store python3 占位符命中 hook 探测 | 无关 |
| DEBT0015 | medium | env_constraints 声明性字段无执行绑定 | 无关 |
| DEBT0016 | low | gate_p4 CODE-MAP 路径本地推导未用 resolve_workspace | 相邻（同在 gate_p4），本任务未触碰该路径逻辑 |
| DEBT0017 | low | gate_p4 新增文件核对表子串判定假阴性 | 相邻（同在 gate_p4），本任务未触碰该判定 |
| DEBT0018 | low | agate_common import 降级 stub 呈 false-PASS 方向 | 相邻（import 兜底先例同源），本任务未改变降级语义 |
| **DEBT0023** | **low** | **gate_commands 的 P3* 前缀键被静默收集为 TDD 测试命令执行** | **本任务 P2 登记**（tech-debt.md:814-841，source: review，task_id: TAG0026） |

- **DEBT0023 确认在案**：status: open / priority: low / task_id: TAG0026——本任务通过「gate_commands 禁止声明任何 `P3_xxx` 检测命令键」约定规避（P2 §4 声明说明第 1 条 + P7 §3.6 逐键核对一致），协议层缺口留待后续任务收口，**不阻断发布**。
- 其余 10 条 open 债务与本任务改动面无交集，均不阻断发布。
- 本任务未新增 DEBT（P4-review「无非阻塞 DEBT 新增」结论维持，P7 §1 确认）。

## 3. CHANGELOG 条目草案（主 Agent 定稿）

放 `[Unreleased]` 段下（对齐既有条目风格：加粗开头 + 一句话机制描述；建议分「新增」子节，对齐 0.63.0 章节先例）：

```markdown
### 新增（TAG0026：维护性反模式 gate，RM-AG0046）

- **`check-maintainability.py` 维护性反模式检测器（RM-AG0046）**：新增 diff 驱动的两类反模式
  检测——god-file 跨越（before < 阈值 ≤ after，默认 1000 行）与 fuzzy-boundary（裸 `except:` /
  `# type: ignore` / `: any` 等，按扩展名路由正则）；阈值与正则集经 `agate-workspace/maintainability.yaml`
  可配置（默认值仅供参考），配置缺失/损坏全部兜底为默认值，不报错。
- **`check-gate.py` gate_p4 新增三重门槛（RM-AG0046）**：检测 violations 非空时，要求
  known-violations.md 登记（新模板 `agate/assets/templates/known-violations-template.md`）+
  登记条目数 ≥ violation 数 + P4 评审 approve 三者齐全才放行——登记本身不构成放行依据，
  "是否接受该反模式"的判断权在评审角色；violations 为空 / 检测未部署 / git 通道不可用三场景
  行为与旧版完全一致（零回归面）。
- **P4/P6 卡片机制条目**：P4 卡新增评审 checklist（approve 前必须读过登记理由）与 gate 规则
  exit 1 条目；P6 卡「自查≠gate」节新增非阻断复跑提醒（挂载在 P4，P6 暂存区通常无代码 diff）。
- **一致性配套**：check-protocol-consistency.py 锚点登记 + agate-summary.py `_DRIFT_SCRIPTS`
  同步；新增 27 个单测（count-tests 1308 → 1335，只增不减）。
```

> 注：以上为草案文本，主 Agent 可按定稿口径合并/拆分条目；**只追加本任务条目，不动 [Unreleased] 既有 8 条**。

### 版本段切分建议（标注：主 Agent 定夺）

- **建议 A（推荐）：[Unreleased] 整体切为 [v0.65.0] - 2026-08-30**。现有 8 条（TAG0025 收尾）已逐一核验属 v0.64.0 tag 之后合入（归属结论见 §8），与本任务条目同属一个发布周期，整体成段一次发布，避免 Unreleased 积压、也避免 0.64.0「其他」段的补充口径问题。
- 建议 B：仅本任务条目入 [v0.65.0] 新段，TAG0025 收尾 8 条留在 Unreleased。不推荐：这 8 条改动已在 main 合入、会随 v0.65.0 tag 一起发布，若不随段则「已发布内容无版本段归属」，与 git 历史脱节，下次发布才会被带出。
- 无论 A/B：新版本号 v0.65.0、日期由主 Agent 按实际发布日填写。

## 4. UPGRADING 新章节要点草案（主 Agent 亲自执行）

**checklist 项（v0.62.0 教训）**：新版本**必须在 `agate/UPGRADING.md` §3 新增 v0.65.0 章节——无破坏性变更也要写，标题下首行标注「（无破坏性变更，零迁移动作）」**；CHECK 13（CHANGELOG↔UPGRADING 章节对应性）会机械校验漏写。

章节要点草案（对齐 v0.63.0/v0.64.0 章节结构）：

1. **总标注**：本版本无破坏性变更，零迁移动作。
2. **① 新增检测器与 P4 三重门槛——对已有任务的兼容性说明（TAG0026 要点）**：
   - 新增 `check-maintainability.py` 与 gate_p4 三重门槛对**已有任务零影响**：既有任务
     无 `known-violations.md` 时，三重门槛仅在 violations 非空时触发；violations 为空 /
     检测未部署 / git 通道不可用三场景 gate_p4 行为与旧版完全一致（空场景零行为变化）。
   - 新模板 `known-violations-template.md` 仅 violations 非空的任务需要使用，对无 violation
     任务不产生任何要求。
3. **② 可选配置**：`agate-workspace/maintainability.yaml` 为可选配置（默认阈值 + 正则集，
   文件内注释注明「默认值仅供参考可配置」）——不创建则使用内置默认值，无强制、无升级动作。
4. **③ 升级动作**：`git pull` 即完成（软链布局自动生效）；复制模式（Windows）需重跑
   SETUP.md 步骤 2 的 `cp`（对齐 0.63.0 章节先例）。本版本未改 3 个 hook 薄壳
   （P7 §3.2 改动清单核对：改动面仅 4 个 scripts + templates + phase-cards + tests，
   无 `.sh`），无需重跑 `install-hook.py`。
5. **④ gate 行为收紧说明（合法数据无影响）**：gate_p4 新增的阻断仅针对「本次 diff 引入
   反模式且未登记」场景——历史合规任务（无 staged 代码 violation）不受影响。

## 5. roadmap 回写 checklist（RM-AG0043 硬校验，主 Agent 执行）

- [ ] `agate-workspace/roadmap/roadmap.md` :51 **RM-AG0046** 行：「状态」列 `scheduled` → `done`（P8 gate 硬校验 RM-AG0043：关联任务 TAG0026 的 RM 条目未回写 done 即阻断）。
- [ ] 回写时核对 9 列精确结构（DEBT0019 修复后 `_check_roadmap_done()` 按精确 9 列解析，列数不齐整行跳过 + WARNING）；建议同步补「完成日期」列（表内既有 done 行惯例为回写当日）。
- [ ] 回写属于 .state.yaml phase=P8 的同一 commit 产出面（hook 按 phase 校验暂存产出）。
- [ ] 本任务关联 RM 仅 RM-AG0046 一条（roadmap.md 全文按 task_id 反查 TAG0026 实测仅 :51 一处）。

## 6. 版本引用文件 checklist（Agateon 仓库特有，主 Agent 逐项执行）

| # | 文件 | 动作 | 现状锚点 |
|---|------|------|---------|
| 1 | `README.md` | version badge v0.64.0 → v0.65.0（:12 附近，badge 行） | objective_info 已核 |
| 2 | `README.zh-CN.md` | 中文镜像 badge 同步（0.64.0 发布时两 README badge 同批更新先例）；bump 时 `grep -n "v0.64" README*.md` 复核无遗漏 | CHANGELOG 0.64.0 先例 |
| 3 | `CHANGELOG.md` | [Unreleased] → 新版本段（§3 切分建议，主 Agent 定夺）+ 追加本任务条目 | §3 草案 |
| 4 | `agate/UPGRADING.md` | §3 新增 v0.65.0 章节（无破坏性变更也写；CHECK 13 对应性校验） | §4 要点草案 |
| 5 | 其余硬编码版本 | **无**——文档优先写「稳定版」不写死版本号（AGENTS.md 版本引用文件清单口径）；pyproject.toml 无 version 字段，不动 | objective_info 已核 |

## 7. AUDIT7 验证计划（主 Agent 执行，本文件不含结果预判）

命令（worktree 根执行）：

```bash
python3 agate/scripts/check-p6-provenance.py --audit7-only agate-workspace/tasks/TAG0026-maintainability-gate
```

判定方式：读 stdout 的 `AUDIT7_RESULT: <...>` 行（配合 exit code）：

| 分支 | 判定 | 动作 |
|------|------|------|
| 分支 1 | `AUDIT7_RESULT: reuse_allowed`（exit 0） | **复用** P5 阶段同一份 `P5-test-results/`，不重新执行 `gate_commands.P5` |
| 分支 2 | `AUDIT7_RESULT: reuse_blocked`（exit 1），或 `AUDIT7_RESULT: no_reuse_claim_possible`（exit 0 但结果非 reuse_allowed） | **完整重跑** `gate_commands.P5` 全部 5 键（P2 §4：P5 全量 pytest / P5_consistency / P5_count_tests / P5_ruff / P5_shellcheck），要求各命令 exit 0 且 pytest failed==0；重跑结果写入任务目录留痕 |

**DEBT0013 时序注意（分支 2 触发时必须遵守）**：`gate_commands.P5` 链路含
`check-protocol-consistency.py --strict-errors-only`，其 CHECK 7 校验「README version badge 与最新 git tag 一致」。P5 重跑应安排在 **commit + 创建 git tag v0.65.0 之后**，而非 bump 版本文件后立即重跑——「bump 已完成、tag 尚未创建」的中间态下 CHECK 7 必然报 `badge v0.65.0 != tag v0.64.0` ERROR，这是设计使然（校验的是发布完成态），不是回归；先 tag 后重跑即 0 ERROR。（DEBT0013 已 closed，教训已沉淀为 P8 卡条文。）

发布检查命令全清单（P2 §4 gate_commands 原文，主 Agent 按 AUDIT7 分支决定复用或重跑）：

```yaml
P5: "python3 -m pytest agate/tests/ -q --tb=no"            # timeout 600s
P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"  # 120s，必须 worktree 版
P5_count_tests: "bash agate/tests/scripts/count-tests.sh"   # 60s
P5_ruff: "~/.venvs/agate-dev/bin/ruff check agate/scripts/ agate/tests/unit/"  # 60s
P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh"   # 60s
```

## 8. git log v0.64.0..HEAD 对照结论

命令：`git log v0.64.0..HEAD --oneline`（2026-08-30 实测，60+ commit 含 merge）。

1. **任务主流程链齐整**：f3290f2（RM-AG0046 计划 v3）→ 立项/交接（5710209/1aeff7c）→ P1 7625f5b → P2 8a1fbce（+ DEBT0023 登记）→ P3 2225634 → P4 f7e7b9f（self-gate-review 6 文件）→ P5 acf0cb2 → P6 7af1e72 → P6.5 5d828c9 → P7 1053472。
2. **[Unreleased] 既有 8 条归属全部正确**：逐条反查归属 commit 均在 v0.64.0 tag 之后——品牌文案统一（0ad801f）、DSH preset 显示名（0ad801f，`agate/assets/templates/dsh/preset.yml` + `agent.cordis.yml`，message grep 不显、按文件路径追踪定位）、测试并行化文档（7347a1b）、agate-summary DSH 校验（8550448）、TAG0025 复盘措施 + DEBT0021/22 关闭（34e6f0b）、删假想版本锚点（8f171e0）、HANDOFF-TAG0024/0025 归档（0ad801f，`archived/` 新增实测）。无一条属 v0.64.0 之前，Unreleased 归属无需修正。
3. **TAG0026 本任务改动未入 CHANGELOG**（P1-P7 共 9 commit + 立项 2 commit）——由本次 P8 补录，草案见 §3。
4. **区间内其余未入 [Unreleased] 的 commit**：site/ 博客系列（003d3de 起约 15 个，产品 Web 层非协议面）、整仓导航地图与文档保鲜指南（c96880b）、CI docs-only 快路径修复（9628ccb）等。是否补录 [Unreleased] 或归入版本段「其他」子节，按 CHANGELOG 0.64.0「其他」段口径由**主 Agent 定夺**——本任务草案（§3）只覆盖 TAG0026 范围。
5. 对照结论：**无遗漏的本任务机制性变更**——P2 §1.1 M1-M10 改动面（4 scripts + 模板 + 2 卡片 + 配置 + 2 测试文件）与 commit f7e7b9f / 8a1fbce 内容一一对应，无 commit message 与实际改动脱节项。

## 9. 临时资源清单（releaser → 主 Agent READY 收尾交接）

| 类别 | 内容 |
|------|------|
| 临时服务/进程 | **无**——本任务全程未启动任何服务、daemon、调试进程 |
| 临时端口 | **无** |
| 开发安装 | **无**——未做 editable install / 全局包安装（ruff 用既有 `~/.venvs/agate-dev/bin/ruff`，pyyaml 为既有系统依赖） |
| 临时数据 | P6 验收用的 tmp 场景脚本与临时 git 仓库位于 `/tmp`（系统临时区，重启自动清理，无需主动清理动作）；pytest 临时目录由 pytest 自管理；P6-evidence 13 份证据已随任务目录入库，非临时资源 |
| 本 P8 阶段 | 无新增资源（只读分析 + 产出本文件与 P8-progress.md） |

READY 收尾按 P8 卡逐项实际执行检查命令（如 `git status` 确认工作区干净），不得仅凭本清单打勾。

## 10. Lessons Learned（主 Agent 汇入 docs/notes/lessons.md）

1. **架构 / Python 模块系统**：模块名标识符不能含连字符——`from check_maintainability import` 对 `check-maintainability.py` 必然 ImportError，连字符文件必须走 `importlib.util.spec_from_file_location` 按路径加载（TAG0026 DESIGN_GAP 实证；单源先例 `agate-risk-score.py` `_load_script`）。「文件存在 = import 成功」是错觉，P2 伪代码层就要写对兜底形态。（来源任务 TAG0026，2026-08-30）
2. **流程 / 派发信息质量**：dispatch-context 的「客观查证信息」逐条实测注入（版本现状/RM 行号/DEBT 状态/主流程 SHA 链），subagent 直接复用即与仓库实测一致，零信息过期返工——派发前主 Agent 做一轮客观查证比让每个 subagent 重复考证省一个数量级上下文。（来源任务 TAG0026，2026-08-30）
3. **流程 / CHANGELOG 归属核对**：[Unreleased] 条目归属用 `git log v{tag}..HEAD -- <files>` 按文件路径反查，比按 commit message 关键词 grep 更准——本例「DSH preset 显示名」与「HANDOFF 归档」同属 0ad801f 一个 commit，message grep 只能命中其一。（来源任务 TAG0026，2026-08-30）
