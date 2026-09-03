---
phase: P7
task_id: TAG0028
type: consistency
parent: P2-design.md
trace_id: TAG0028-P7-20260903
status: approved
created: 2026-09-03
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0
deviation_count: 3
deviation_critical_count: 0
design_gap_count: 4
design_gap_reviewed_count: 4
code_map_new_files_count: 3
code_map_reviewed_count: 3
---

# P7 一致性审查 — TAG0028 subagent 存活可观测性与受控自主再派发（RM-AG0055）

> 阶段：P7（一致性交叉检查）· 角色：consistency-reviewer · 日期：2026-09-03
> 审查输入：P1-requirements.md（33 BDD + packages=[agate] + [NO_NEED_CONFIRM]）·
> P2-design.md（候选方案 A + packages=[agate] + gate_commands）· P4-implementation.md
> （4 条 DESIGN_GAP + 新增文件核对表）· P6-acceptance.md（33 PASS / 0 FAIL）·
> P6.5-judge-verdict.md（33/33 passed）· P0-brief.md（scope/env_constraints）·
> CODE-MAP.md（命令流检测族登记）
> 审查方法：逐条对照 P1-P6 产出做跨文件交叉检查，DESIGN_GAP 逐条配对 REVIEWED，
> SCOPE+ 闭环核对，未决项清零核对，CODE-MAP 与 P4 新增文件核对表逐条核对（实查 worktree）。

## 1. DESIGN_GAP 配对（P4 声明 4 条 → P7 逐条转抄 + REVIEWED）

### GAP-1：P3 test_bdd_3 断言结构性矛盾（P4-implementation.md 63-73 行，P4 已含 REVIEWED，P7 转抄）

[DESIGN_GAP: P3 test_bdd_3_opencode_adapter_parses_sqlite 断言结构性矛盾——测试用
`by_cmd = {r.command: r for r in records}` 按 command 建字典，而 fixture 中 call_demo_0002
与 call_demo_0003 命令同为 "make build-docs"（0002: exit=2/truncated=false；0003:
exit=0/truncated=true），字典同键只能保留一条记录，`by_cmd["make build-docs"].exit == 2`
与 `by_cmd["make build-docs"].truncated is True` 两条断言要求同一记录同时满足 exit==2 与
truncated==True，fixture 无此记录——任何适配器实现（任意返回顺序）都无法同时满足；属
P3 测试/fixture 设计问题，按 implementer 决策树不改测试，上报主 Agent 决策（P3 修复轮）]

[DESIGN_GAP_REVIEWED: 已确认——P3 测试设计缺陷（T075 类：断言与 fixture 数据矛盾），
非实现问题、非 P1 BDD 矛盾；已回派 test-designer fix1 修复（过滤式匹配），修复后
cmdstream 套件 42/42 全绿（4 长期不变量保持），主 Agent 2026-09-03 核验通过]

> P7 复核：GAP-1 属 P3 测试设计缺陷而非实现偏差，P4 决策树不改测试、回派 test-designer
> fix1 的处置路径与 P1 BDD-3 语义（opencode 适配器从 SQLite 解析、exit 取
> state.metadata.exit、truncated 取显式标记）无冲突；P6 验收 BDD-3 2 用例全绿 PASS，
> 缺陷已闭环。锚点：P4-implementation.md §Phase 1 测试结果 / P6-acceptance.md BDD-3。

### GAP-2：CommandRecord.ts_end 类型放宽 int|None（P4-implementation.md 270-272 行）

[DESIGN_GAP: P2-design §3.1 声明 ts_end 为 epoch 毫秒 int；CRITICAL-3 修复需未结束
call 记录携带 ts_end=None（评审 Fix A 明确推荐），故 CommandRecord.ts_end 类型放宽为
int|None（默认 None），from_dict 校验同步放宽；既有 BDD-1 断言（构造时传 int）不受影响]

[DESIGN_GAP_REVIEWED: 已确认——该放宽是 CRITICAL-3「未结束 call 通路可达」修复的必要
条件（无配对 result 的未结束 call 无结束时间，ts_end=None 是 IR 语义的自然扩展）；
P4-review 评审 Fix A 明确推荐，from_dict 校验放宽与 CRITICAL-6 类型契约校验（ts_end
int|None）一致；BDD-1 验收断言以 int 构造传值仍通过（P6 BDD-1 PASS），未破坏 P1 契约
「ts_start/ts_end 为 epoch 毫秒整数」的构造路径；IR 十字段字段集合不变，仅类型域放宽，
属实现级偏差、非需求级偏离，确认闭环]

> P7 复核锚点：P2-design.md §3.1（M1 IR 契约）/ P4-implementation.md CRITICAL-3 + CRITICAL-6 /
> P6-acceptance.md BDD-1（test_agate_cmdstream_ir.py 4 用例全绿，含 from_dict 坏类型拒绝）。

### GAP-3：DSH 截断双信号启发式（P4-implementation.md 274-277 行）

[DESIGN_GAP: 验证记录 Q6 仅确认 DSH「有截断标记（超大输出会被截断）」未给字段名；
CRITICAL-7 修复采用双信号启发式检测（tool-result dict 显式 truncated/isTruncated 布尔
字段 + 输出文本 "[truncated]"/"…[truncated]"/"Output truncated" 字面量），记录于此供
评审复核；若实机 DSH 截断标记为其他形态，适配器 _detect_truncated 为唯一修改点]

[DESIGN_GAP_REVIEWED: 已确认——Q6 未给字段名是上游数据源文档缺口而非设计偏离，双信号
启发式是当前信息下的合理落地（显式布尔字段优先 + 文本字面量兜底）；检测结果形态与
P1 BDD-17 语义一致（truncated 不参与无效重复哈希比对、仍参与冻结检测），且 P4 声明
「_detect_truncated 为唯一修改点」符合 BDD-6 适配器隔离契约（平台细节收敛在适配器内、
检测引擎零改动）；P6 验收 BDD-4（含截断标记 → truncated=True + output_hash=None）与
BDD-17 2 用例全绿 PASS，确认闭环]

> P7 复核锚点：P1-requirements.md BDD-17（截断排除）/ BDD-6（适配器隔离）/
> P4-implementation.md CRITICAL-7 / P6-acceptance.md BDD-4、BDD-17。

### GAP-4：expected 接入用 CLI --expected N 参数（P4-implementation.md 279-282 行）

[DESIGN_GAP: fix1 dispatch-context 授权「expected 声明接入 CLI 事件——具体接入方式自主
决策并在 P4-implementation.md 记录」；采用 CLI `--expected N` 参数（观察者声明，事件
元数据形态）而非读 maintainability.yaml——expected 是 RM-AG0023 timeout_seconds 的
per-command 语义，全局阈值配置节无对应键，per-command 由观察者传入最贴合语义]

[DESIGN_GAP_REVIEWED: 已确认——接入方式已在 fix1 dispatch-context 获授权自主决策，采用
CLI --expected N（观察者声明、per-command 元数据形态）与 expected 的 per-command 语义
吻合（maintainability.yaml cmdstream_detection 节实查无 expected 键，全局节无法承载
per-command 声明）；BDD-8 主信号语义（expected×2 且不低于 30s 下限）由
test_bdd_8_cli_detect_expected_signal 验证（--expected 200 → 阈值 400s → NORMAL），
P6 验收 BDD-8 2 用例全绿 PASS；CLI 参数属于 P2 M3「CLI 子命令」的实现细节扩展，不改变
detect 引擎核心语义，确认闭环]

> P7 复核锚点：P2-design.md M3（CLI 子命令）/ maintainability.yaml cmdstream_detection 节
> （实查无 expected 键）/ P4-implementation.md CRITICAL-3③ + GAP-4 / P6-acceptance.md BDD-8。

## 2. SCOPE+ 闭环

- P1-requirements.md 全文 grep：无实际 `[SCOPE+]` 增补条目（line 23「后续阶段发现的隐含
  需求（[SCOPE+]）由主 Agent 回写」仅为活基线机制说明，非增补声明），P1-P4 全程未产生
  SCOPE+ 增补，故无对应 [SCOPE_RESOLVED] 需求——**无 SCOPE+ 增补，闭环成立**。

## 3. 跨文件一致性检查（引用具体锚点）

| # | 检查项 | 锚点引用 | 结论 |
|---|--------|---------|------|
| 3.1 | P2 packages 与 P8 release bump 范围一致 | P2-design.md frontmatter `packages: [agate]` ↔ P1-requirements.md frontmatter `packages: [agate]`（两处一致）；P4 实现全部落在 `agate/scripts/`（3 新脚本）+ `agate/*.md`（dispatch-protocol/role-system/模板）+ `agate-workspace/maintainability.yaml`，均属 [agate] 包 + 其 workspace 配置面。P8 尚未产出（当前进度 P6.5），release bump 范围最终核对留 P8 阶段执行，P1/P2 声明已一致 | 一致（P8 待产出后最终核对） |
| 3.2 | P1 BDD 数量与 P6 验收结果数量匹配 | P1-requirements.md §4 BDD-1~33（`#### BDD-NN:` 33 条全局连续，fix1 后无跳号）↔ P6-acceptance.md frontmatter `pass: 33 / fail: 0` + 验收汇总「33/33 PASS, 0 FAIL」（pass+fail=33） | 匹配（33 ↔ 33） |
| 3.3 | P4 实现路径与 P2 方案设计吻合 | P2-design.md §2.1 候选方案 A（三脚本平铺 agate/scripts/ + 显式注册表 ADAPTERS）↔ P4-implementation.md implementation_dir `agate/scripts/` + 新增文件核对表 3 脚本（ir/adapters/detect）+ 显式注册表实现（P4 Phase 1 摘要）；git 实查：worktree agate/scripts/ 三脚本存在（ir 4657B / adapters 25978B / detect 17006B） | 吻合 |
| 3.4 | P6.5 judge verdict 与 P6 对照 | P6.5-judge-verdict.md frontmatter `status: passed / criteria_total: 33 / criteria_passed: 33`（逐条零挑验）↔ P6-acceptance.md「33/33 PASS, 0 FAIL」 | 一致（33/33 ↔ 33/33） |
| 3.5 | P2 gate_commands 与 P5 实跑对照 | P2-design.md §4 gate_commands（P5 全量 pytest 1434 passed 声明 + P5_cmdstream_verify 9 场景）↔ P5 commit 700f074（gate_commands.P5 全量 5 key PASS）↔ P6-acceptance.md 复用 P5-test-results/unit.md（1434 passed / 0 failed / 2 skipped） | 一致 |

## 4. 未决项清零

- P1-requirements.md grep `NEED_CONFIRM|BLOCKER|DEVIATION-CRITICAL`：仅 line 264
  `[NO_NEED_CONFIRM]` 正声明 + line 23 SCOPE+ 机制说明，无残留行首 NEED_CONFIRM /
  BLOCKER / DEVIATION-CRITICAL 标记——未决项清零成立。
- P6-acceptance.md：无 NEED_CONFIRM 中间态（BDD-1~33 全部按实跑二值 PASS 判定，
  无「调整/跳过/覆盖」），符合验收二值客观性。

## 5. CODE-MAP 核对（对照 CODE-MAP.md 与 P4 新增文件核对表）

| # | 新增文件（P4 核对表） | CODE-MAP.md 登记（line 33 命令流检测族） | worktree 实查 | 判定 |
|---|----------------------|------------------------------------------|--------------|------|
| 1 | agate/scripts/agate-cmdstream-ir.py | 已登记（CommandRecord 统一 IR：十字段字段契约 + JSON 序列化） | 存在（4657B） | [CODE_MAP_SYNC: agate-cmdstream-ir.py] |
| 2 | agate/scripts/agate-cmdstream-adapters.py | 已登记（三平台命令流适配器 + 显式注册表 ADAPTERS） | 存在（25978B） | [CODE_MAP_SYNC: agate-cmdstream-adapters.py] |
| 3 | agate/scripts/agate-cmdstream-detect.py | 已登记（检测引擎 FROZEN/SPIN/NORMAL + 心跳 helper + CLI） | 存在（17006B） | [CODE_MAP_SYNC: agate-cmdstream-detect.py] |

- CODE-MAP 核对结论：3/3 同步（[CODE_MAP_SYNC:]），无 [CODE_MAP_DRIFT:]。P4 核对表
  3 脚本均标 [CODE_MAP_UPDATED]，与 CODE-MAP.md line 33「命令流检测族（新增 TAG0028）」
  登记一致；依赖方向符合 CODE-MAP.md 既有声明（检测/解析输出平台无关、阈值配置走
  maintainability.yaml cmdstream_detection 节——maintainability.yaml 实查含该节，
  300/900/60/300/10/5 + repeat_unique_min=3 + expected ×2/30 与 P2/verify 锚同源数值一致）。

## 6. 环境隔离声明

[PROD_NOT_TOUCHED] 本审查全程只读（read/grep + worktree 实查 ls/git log），未写生产环境、
未改任何代码/进程/git 历史、未读取其他用户 DSH 会话；仅产出 P7-consistency.md 与
P7-progress.md 进度记录（任务工作区允许路径）。

## 7. 审查结论

- BLOCKER 计数：0（frontmatter blocker_count=0）
- DEVIATION-CRITICAL 计数：0（frontmatter deviation_critical_count=0）
- DEVIATION 计数：3（frontmatter deviation_count=3，口径 = P4 声明实现偏差 3 条
  GAP-2/3/4；GAP-1 为 P3 测试设计缺陷，计入 design_gap_count=4 但不计实现偏差）
- DESIGN_GAP 配对：4/4 全部 REVIEWED（design_gap_count=4，design_gap_reviewed_count=4）
- SCOPE+ 闭环：无 SCOPE+ 增补，闭环成立
- 跨文件一致性：全部检查项引用具体锚点通过（P2 packages ↔ P1 packages、P1 BDD 33 ↔ P6
  33 PASS、P4 impl 路径 ↔ P2 方案 A、P6.5 33/33 ↔ P6 33/33、P2 gate_commands ↔ P5 实跑）
- CODE-MAP：3/3 [CODE_MAP_SYNC:]（code_map_new_files_count=3，code_map_reviewed_count=3）
- 未决项：清零（P1 [NO_NEED_CONFIRM]，无残留 NEED_CONFIRM/BLOCKER/DEVIATION-CRITICAL）
- **结论：P7 一致性审查通过（status: approved），无阻塞项，可推进 P8**
