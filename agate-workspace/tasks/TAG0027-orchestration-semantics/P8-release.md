---
phase: P8
task_id: TAG0027
type: release
parent: P7-consistency.md
trace_id: TAG0027-P8-20260903
created: '2026-09-03'
status: draft
agent: implementer
bump_type: minor
debt_check: reviewed
---
# P8-release — TAG0027 编排语义统一落地（RM-AG0054）发布准备

> parent: P7-consistency.md（approved：blocker=0 / deviation=0 / design_gap 2/2 配对 REVIEWED /
> CODE_MAP_DRIFT 1 条 WARNING 级非阻断）
> 本文件由 releaser subagent（implementer P8 模式）产出，只做发布准备——**不执行 git commit /
> git tag / 不改 README / CHANGELOG / UPGRADING / roadmap 正文**（bump 与版本文件改动由主 Agent
> 在 gate 验证通过后亲自执行）。环境隔离：[PROD_NOT_TOUCHED]（全程只读分析 + 产出本文件与
> P8-progress.md，未触碰协议本体/生产面）。

## 1. bump_type 建议与理由

**bump_type: minor**（v0.65.0 → v0.66.0）

理由（逐条）：

1. **新增向后兼容的协议功能（semver minor 主判据）**：本任务新增 3 个协议 CLI——
   `agate/scripts/agate-next.py`（推进侧状态机 CLI，pass_set 三态判定 + P6 条件式推进 +
   exit2-resolution 真暂停落盘）、`agate-advance.py`（手动/多阶回退引导）、`agate-dispatch.py`
   （渲染时注入单命令）；`rules/phases.yaml` 主线条目新增 `next` / `retreat` / `gate_pass_exit`
   三键 + P6.5 条目新增 `gate_subphase`（schema 同步声明四新属性，值域枚举锁定）——
   属 "new backwards-compatible functionality" → minor。
2. **新增一致性护栏**：`check-protocol-consistency.py` 新增 CHECK 14（md 叙述段落平台名扫描，
   实现注记段落级豁免 + 结构豁免）/ CHECK 15（数据面平台名词边界扫描 + 豁免词典机械生成）。
3. **向后兼容性已客观验证**：`check-gate.py` 返回约定（exit 0/1/2）与
   `check-state-transition.py` / `agate-retreat-to.py` 语义**未改**——新 CLI 全部以"新增消费方"
   形态复用既有资产（BDD-13 硬边界，P7 §3 核对）；P6.5 复核谓词 Fix C 收窄为"只校验经真暂停
   分支落盘的 resolution 文件"，健康任务不误拦（P6 26/26 PASS）。→ 非 major。
4. **无 bugfix 批次 / 非 hotfix**：本任务是功能落地（RM-AG0054），不是 patch 级修复 → 非 patch。
5. **单仓单版本**：pyproject.toml 无 version 字段（单包文档型项目），版本以 README badge +
   CHANGELOG 为准；P2 frontmatter `packages: [agate-protocol]` 为影响面声明（worktree `agate/`
   唯一改造对象），P8 卡「多包发布拆批」不触发，无需合并 subagent。

版本号变更确认（供主 Agent bump 时核对）：

| 项 | 现状（实测） | 目标 |
|---|---|---|
| 最新 git tag | v0.65.0（ba25de3，2026-09-01） | v0.66.0（待主 Agent 创建并推送） |
| README.md version badge（:12） | v0.65.0 | v0.66.0 |
| README.zh-CN.md version badge（:12） | v0.65.0 | v0.66.0 |
| pyproject.toml | 无 version 字段 | 不动 |

## 2. debt_check

**debt_check: reviewed**

已读 `agate-workspace/debt/tech-debt.md`（2026-09-03 实读，23 条 DEBT），当前 **open 共 11 条**，
逐条核对与本任务关系：

| id | priority | 简述 | 与本任务关系 |
|---|---|---|---|
| DEBT0002 | medium | 离线包 compute_sha256 双实现漂移 | 无关（版本管理面） |
| DEBT0003 | medium | 离线 manifest 未签名 | 无关 |
| DEBT0004 | medium | 卸载引用保护扫描限流漏扫旧引用 | 无关 |
| DEBT0007 | medium | test_check_pruning.py 部分用例依赖真实 git 暂存区 | 无关（本任务 P5 全量 pytest 通过未触发误报） |
| DEBT0008 | low | agate-feedback 匿名化正则误伤中文散文 | 无关 |
| DEBT0014 | medium | Windows Store python3 占位符命中 hook 探测 | 无关（未改 hook 薄壳；P7 改动清单核对无 `.sh`） |
| DEBT0015 | medium | env_constraints 声明性字段无执行绑定 | 无关 |
| DEBT0016 | low | gate_p4 CODE-MAP 路径本地推导 | 相邻（P7 CODE_MAP_DRIFT 同域），本任务未触碰该路径逻辑 |
| DEBT0017 | low | gate_p4 新增文件核对表子串判定假阴性 | 无关 |
| DEBT0018 | low | agate_common import 降级 stub | 无关 |
| DEBT0023 | low | gate_commands 的 P3* 前缀键被静默收集为 TDD 测试命令 | 无关（TAG0026 登记；本任务 P2 §4 未声明任何 P3_xxx 键，规避约定持续有效） |

- **本任务未新增 DEBT**：tech-debt.md 全文反查 `task_id` 无 TAG0027 登记（TAG0026 P2 曾登记
  DEBT0023——本任务未产生同类新债；P2 review / exit2fix 轮的 P4 review 结论"无新增债务"与
  P7 §1/§2 核对一致）。DESIGN_GAP 2 条（schema 层 if/then 约束改数据面承载、CHECK 14 扫描面
  不含 assets/）均已按 P4 review 记录为**范围决策**（非未登记债），P7 配对 REVIEWED。
- 其余 10 条 open 债务与本任务改动面无交集，均不阻断发布。

## 3. CHANGELOG 条目建议（草案，主 Agent 定稿）

CHANGELOG `[Unreleased]` 段当前为空（仅占位），本版本段 = 仅本任务条目。建议 `[Unreleased]` →
`[0.66.0] - <发布日>`，分「新增」「变更」子节（对齐 0.65.0 / 0.63.0 章节先例）：

```markdown
### 新增（TAG0027：编排语义统一落地，RM-AG0054）

- **推进侧状态机 CLI：`agate next` / `agate advance`**：推进决策从 orchestrator 临场判断改为
  查表推进——消费 `phases.yaml` 新声明的 `next` / `retreat` / `gate_pass_exit`（逐 phase「检查
  通过」出口码）+ `check-gate.py` exit 三态（exit ∈ gate_pass_exit → 直推 next / P6 条件式推进
  前置 gate_p65；exit 1 → 按 retreat 表值委托 `agate-retreat-to.py` 逐阶回退；真暂停 → 落盘
  `{phase}-exit2-resolution.md` 转主 Agent）；推进只 git add 不自行 commit（跳变合法性仍由
  pre-commit 的 check-state-transition 校验）；档位 C 自动推进改走 `agate next`（可观测层，
  事件留痕 gate-events.jsonl）。
- **`agate dispatch` 渲染时注入单命令（方案 A）**：派发 = 单命令自动渲染 dispatch-context
  （Lazy Injection——渲染时拼装阶段卡片 + 块外 `CARD-SOURCE` 来源标记），主 Agent 不再直接调用
  `agate-inject-card.py`；`agate-inject-card.py` / `agate-card-inject.py` 手工兜底路径保留兼容。
- **`phases.yaml` 转移表结构化字段**：主线 P0-P8 条目新增 `next` / `retreat` / `gate_pass_exit`
  键（值域枚举 + null，schema 同步声明），P6.5 条目新增 `gate_subphase`（hosted_on/forward_to/
  needs_revision_to，非独立转移边口径保持）。
- **护栏 1 机械化（CHECK 14/15）**：`check-protocol-consistency.py` 新增 md 叙述段落平台名扫描
  （段落级「实现注记」豁免 + 结构豁免：platform-notes/SETUP/已知适用环境表/dsh 平台食谱目录）与
  数据面平台名词边界扫描（豁免词典从 schema + rules 机械生成，不手抄文件名单）。
- **审计 2 双锚点剥离**：`check-p6-provenance.py` 审计 2 卡片块剥离 = CARD-SOURCE 行起物理块优先
  + START..END 兜底（渲染产物与手工注入两路并存覆盖）；`check-judge-verdict.py` `_strip_card`
  同步 + P6.5 复核谓词 Fix C（只校验经真暂停分支落盘的 resolution 文件，健康任务不误拦）。
- 新增 48 个 pytest 用例（tag0027 批 9 新测试文件，P5 实测 1381 passed + 2 skipped，只增不减）。

### 变更

- **S-1/S-2 加列比对**：`check-structure-consistency.py` S-1 扩展比对 YAML `next`/`retreat` ↔
  WORKFLOW.md 阶段总览表第 4/5 列（P6.5 行走 gate_subphase 形态特判；加列不锚行尾，
  `_TABLE_ROW_RE` 兼容既有解析）。
- **编排心智统一文档化**：协议文档平台名三分类清理（语义段清理 / 「实现注记」标记 /
  结构豁免）；loop-orchestration.md 档位 C 推进点改走 `agate next`；dispatch-protocol.md /
  模板 / 角色文件平台适配说明挂实现注记。
- **check-gate.py 头注释补 exit 2 语义说明**（exit 2 = 多数 phase 正常通过码，非暂停——
  「exit 2 = 需主 Agent 自判」是信号语义；返回逻辑与约定未改）。
```

> 注：以上为草案文本，主 Agent 按定稿口径合并/拆分；区间内 main 侧非任务 commit（设计笔记 v2/v3
> 评审闭环 7a7300a/ec8f6d8、第三轮元评审存档 7138927、platform-notes/SETUP 文档更新
> e9a2c9f/6ca5cc5、site 首页改版 9e893d3 等——均在 v0.65.0 tag 之后合入）是否补录本版本段
> 「其他」子节（对齐 0.64.0「其他」段先例），由主 Agent 定夺；本草案只覆盖 TAG0027 范围。

## 4. UPGRADING 章节建议（主 Agent 亲自执行）

**checklist 项（v0.62.0 教训）**：新版本**必须在 `agate/UPGRADING.md` §3 新增 v0.66.0 章节——
无破坏性变更也要写，标题下首行标注「（无破坏性变更，零迁移动作）」；CHECK 13（CHANGELOG↔
UPGRADING 章节对应性）会机械校验漏写。

章节要点草案（对齐 v0.65.0 章节结构）：

1. **总标注**：本版本无破坏性变更，零迁移动作——未改 `.state.yaml` schema / 既有任务文件格式 /
   3 个 hook 薄壳（P7 改动清单核对无 `.sh` 改动），无需重跑 `install-hook.py`（软链布局 `git pull`
   即生效；Windows 复制模式重跑 SETUP.md 步骤 2 的 `cp`）。
2. **① 新增推进侧 CLI 与转移表字段——对已有任务零影响**：`agate next` / `agate advance` /
   `agate dispatch` 为新增消费方，不改变既有手动推进/手工 dispatch-context 路径；存量任务
   dispatch-context（物理占位符注入）由审计 2 文件版逻辑继续覆盖；`phases.yaml` 新键只被新 CLI
   消费，既有 check-gate / check-state-transition 语义不变。
3. **② 编排心智标记约定（护栏 1）**：协议文档叙述段若提平台名（OpenCode / Claude Code / DSH /
   workflow / ralph / goal / task 词边界），须挂 `> 实现注记：` 标记或落入豁免结构——新增/改写
   协议 md 文档时注意（CHECK 14/15 CI 硬校验）。此条只约束协议维护者，不约束协议使用者。
4. **③ 升级动作**：`git pull` 即完成；无迁移动作。

## 5. roadmap 回写 checklist（RM-AG0043 硬校验，主 Agent 执行）

- [ ] `agate-workspace/roadmap/roadmap.md` :59 **RM-AG0054** 行：「状态」列 `scheduled` → `done`
  （P8 gate 硬校验 RM-AG0043：关联任务 TAG0027 的 RM 条目未回写 done 即阻断）。已实测：
  roadmap.md 全文按 task_id 反查 TAG0027 仅 :59 一处（`| RM-AG0054 | … | scheduled | … | TAG0027 |`）。
- [ ] 回写时核对 9 列精确结构（DEBT0019 修复后 `_check_roadmap_done()` 精确 9 列解析，列数不齐整行
  跳过 + WARNING）；按表内 done 行惯例同步补「完成日期」列（回写当日）。
- [ ] 回写与 P8 阶段 commit 同批（.state.yaml phase=P8 的同一 commit 产出面）。

## 6. 版本引用文件 checklist（Agateon 仓库特有，主 Agent 逐项执行）

| # | 文件 | 动作 | 现状锚点（实测） |
|---|------|------|---------|
| 1 | `README.md` | version badge v0.65.0 → v0.66.0 | :12 badge 行 |
| 2 | `README.zh-CN.md` | 中文镜像 badge 同步（0.65.0 发布先例两 README 同批更新）；bump 时 `grep -n "v0.65" README*.md` 复核无遗漏 | :12 badge 行 |
| 3 | `CHANGELOG.md` | [Unreleased] → [0.66.0]（§3 草案）+ 追加本任务条目 | §3 草案 |
| 4 | `agate/UPGRADING.md` | §3 新增 v0.66.0 章节（无破坏性变更也写；CHECK 13 对应性校验） | §4 要点草案 |
| 5 | 其余硬编码版本 | **无**——文档优先写「稳定版」不写死版本号；pyproject.toml 无 version 字段，不动 | 已核 |

## 7. AUDIT7 验证计划（主 Agent 执行，本文件不含结果预判）

命令（worktree 根执行）：

```bash
python3 agate/scripts/check-p6-provenance.py --audit7-only agate-workspace/tasks/TAG0027-orchestration-semantics
```

判定：读 stdout 的 `AUDIT7_RESULT: <reuse_allowed|reuse_blocked|no_reuse_claim_possible>` 行
（配合 exit code）：

| 分支 | 判定 | 动作 |
|------|------|------|
| reuse_allowed（exit 0） | 复用 | 复用 P5 阶段同一份 `P5-test-results/`，不重新执行 gate_commands.P5 |
| reuse_blocked（exit 1）或 no_reuse_claim_possible（exit 0 但非 reuse_allowed） | 完整重跑 | 重跑 P2 §4.1 gate_commands 全部键，要求各命令 exit 0 且 pytest failed==0，结果写入任务目录留痕 |

**DEBT0013 时序注意（重跑分支触发时必须遵守）**：`gate_commands.P5` 链路含
`check-protocol-consistency.py --strict-errors-only`，其 CHECK 7 校验「README version badge 与
最新 git tag 一致」——P5 重跑应安排在 **commit + 创建 git tag v0.66.0 之后**，而非 bump 版本文件后
立即重跑（bump 完成、tag 未建的中间态 CHECK 7 必报 `badge v0.66.0 != tag v0.65.0` ERROR，这是设计
使然，非回归；先 tag 后重跑即 0 ERROR）。

发布检查命令全清单（P2 §4.1 gate_commands 原文，主 Agent 按 AUDIT7 分支决定复用或重跑）：

```yaml
P5: "python3 -m pytest agate/tests/ -q --tb=no --reruns 1 -n auto"   # timeout 600s（worktree 根跑）
P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"  # 120s，worktree 版
P5_structure: "python3 agate/scripts/check-structure-consistency.py"                        # 120s，worktree 版
P5_schema: "python3 agate/scripts/check-yaml-schema.py agate/rules/phases.yaml"             # 60s，worktree 版
P5_shellcheck: "shellcheck agate/scripts/*.sh"                                              # 60s
P5_counttests: "bash agate/tests/scripts/count-tests.sh"                                    # 60s
P5_selfgate: "python3 ~/.agate/scripts/check-protocol-consistency.py --strict-errors-only"  # 120s，稳定版（验证稳定版不被破坏）
```

## 8. git log v0.65.0..HEAD 对照结论

命令：`git log v0.65.0..HEAD --oneline`（2026-09-03 实测；merge-base(v0.65.0, HEAD) = ba25de3 =
v0.65.0 tag commit 本身）。

1. **任务主流程链齐整**：377ad05（RM-AG0054 立项 scheduled）→ 3d73de3（范围更新 Phase 4 全量）
   → 91a6c3b（交接单入 main）→ P1 5ebf75d → P2 5dcfb8b → P3 2f8df01 → P4 57e5f1c/15505bf/
   fcf3fd2 → P5 bc93c67 → P6 b8c3ef1 → P6.5 cb8aa76 → P7 0a34bf1。改动面全部落在 `agate/`
   （3 新脚本 + 7 修改脚本 + rules/phases.yaml + phases.schema.json + WORKFLOW.md +
   loop-orchestration.md + dispatch-protocol.md + 6 顶层 md/assets 模板角色注记 + 9 新测试文件）
   与 `agate-workspace/tasks/TAG0027-*/`——与 P2 §1.1 Modify 表逐文件吻合，无跨包改动（P7 §3 同核）。
2. **v0.65.0 发布于 2026-09-01（ba25de3）**，本任务 commit 全部在其后——本任务改动未入
   CHANGELOG，由本次 P8 补录（§3 草案）；TAG0027 机制性改动与 commit 内容一一对应，无 commit
   message 与实际改动脱节项。
3. **区间内 main 侧非任务 commit**：设计笔记 v2/v3 + 元评审存档 + platform-notes/SETUP 文档 +
   site 首页改版等（§3 注），是否随本版本段发布由主 Agent 定夺（属 v0.65.0 之后合入内容）。
4. **记录级备注（不阻断，P7 §3 已记录待 P8 留意）**：P6-acceptance.md frontmatter
   `parent: P5-verification.md` 指向文件在本任务目录不存在（本任务 P5 实际产出 = P5-test-results/
   unit.md + fail-list.txt）——parent 指针语义偏差，不影响 P6 验收内容；**建议 P8 commit 时顺带
   修正为实际 P5 产出路径**（一处 frontmatter 一行改动，主 Agent 定夺）。
5. **CODE-MAP 登记（P7 [CODE_MAP_DRIFT] WARNING 级建议）**：`agate-workspace/agents/CODE-MAP.md`
   未登记本任务新增 3 协议脚本（agate-next/advance/dispatch）——P8 commit 时同步登记（主 Agent
   执行清单 §9-9）。

## 9. 主 Agent 动作清单（P8 gate 通过后按序执行）

| # | 动作 | 依据 |
|---|------|------|
| 1 | `check-gate.py P8 $TASK_DIR` 跑 gate（bump_type/debt_check 字段 + roadmap done + tag 检查面） | P8 卡 gate 规则 |
| 2 | AUDIT7 判定 P5 证据（§7）：reuse_allowed → 复用；否则重跑 gate_commands 全键（DEBT0013：先 tag 后重跑） | P8 卡 gate 规则 |
| 3 | README.md:12 + README.zh-CN.md:12 badge v0.65.0 → v0.66.0 | §6 |
| 4 | CHANGELOG [Unreleased] → [0.66.0]（§3 草案 + 定夺 main 侧非任务 commit 是否补录「其他」） | §3 |
| 5 | UPGRADING.md §3 新增 v0.66.0 章节（无破坏性变更也写，CHECK 13） | §4 |
| 6 | roadmap.md:59 RM-AG0054 scheduled → done（9 列精确结构 + 完成日期） | §5（RM-AG0043） |
| 7 | `git tag v0.66.0 && git push origin v0.66.0` + `git ls-remote --tags origin v0.66.0` 验证远端到达（git push 默认不推 tag） | AGENTS.md 版本发布清单 |
| 8 | release PR **普通 merge（--no-ff）禁止 squash**（CHECK 7 / G-5 describe 依赖 tag 与 main 同轨） | AGENTS.md（v0.31.0 事故） |
| 9 | CODE-MAP.md 登记 3 新协议脚本（agate-next/advance/dispatch） | P7 CODE_MAP_DRIFT |
| 10 | 顺带修正 P6-acceptance.md frontmatter parent 指针（指向实际 P5 产出，可选） | §8-4 |
| 11 | G-5 最终验证：`git fetch origin && git describe --tags origin/main` == v0.66.0；`git merge-base --is-ancestor v0.66.0 origin/main` exit 0；合并后 CI 全绿 | AGENTS.md |
| 12 | READY 收尾检查（§10 临时资源清单清理 + 干净 checkout 跑 consistency 0 ERROR + 无 PROD_TOUCHED + 复盘判断） | P8 卡 READY 清单 |

## 10. 临时资源清单（releaser → 主 Agent READY 收尾交接）

| 类别 | 内容 |
|------|------|
| 临时服务/进程 | **无**——本任务全程未启动任何服务 / daemon / 调试进程（P0 env_constraints：pytest 仅本地跑） |
| 临时端口 | **无** |
| 开发安装 | **无**——未做 editable install / 全局包安装（pytest-xdist / pyyaml / ruff 均用既有环境） |
| 临时数据 | pytest 临时目录由 pytest 自管理；P6-evidence/ 9 份证据已随任务目录入库（非临时资源）；本 P8 阶段只读分析 + 产出本文件与 P8-progress.md，无新增临时资源 |
| 残留进程核查 | READY 收尾按 P8 卡逐项实际执行检查命令（`ps aux` 确认无 debug 进程 / `git status` 确认工作区干净），不得仅凭本清单打勾 |

## 11. Lessons Learned（主 Agent 汇入 docs/notes/lessons.md）

1. **架构 / exit code 语义与「账本常态」**：Agateon gate 的"检查通过"出口码多数 phase 是 **exit 2
   而非 exit 0**（gate_p0/p1/p2/p3/p5/p6/p8 均 return 2 实证），把 exit 2 一律当"暂停待解决"会
   把健康任务的正常推进误判为暂停并落盘假 resolution、死锁主线（CRITICAL-1）。消费方必须按
   phases.yaml `gate_pass_exit`（逐 phase 声明的 pass_set）判定，不能按 exit code 绝对值猜语义。
   （来源任务 TAG0027，2026-09-03）
2. **流程 / 测试夹具与实现语义矛盾时先查夹具**：P3 测试夹具无法构造真实 gate exit 场景（P5 夹具
   恒 exit 2、P3 夹具恒 exit 1），暴露的是"夹具可构造性"缺口而非实现缺陷——正确动作是修夹具
   （补 baseline+fail-list 造 exit 1 等）让测试覆盖真实语义，而不是改测试断言迁就实现或标实现
   缺陷（本任务 DESIGN_GAP 2 条均以此闭环）。"测试红"先归因：实现错 / 断言与 BDD 矛盾 /
   夹具不可构造，三者处理路径不同。（来源任务 TAG0027，2026-09-03）
3. **流程 / P4 新增协议脚本须同步登记 CODE-MAP.md**：本任务新增 3 个脚本（agate-next/advance/
   dispatch）依赖方向合规（均为既有 check-gate/retreat-to/next-card 资产的消费方），但 P4 未按
   CODE-MAP.md 头部约定更新登记，P7 只能以 [CODE_MAP_DRIFT] WARNING 级记录放行——记录层面欠账
   留给 P8 补。新增文件在 P4 阶段就要同步登记，别让一致性审查替你发现。（来源任务 TAG0027，
   2026-09-03）
