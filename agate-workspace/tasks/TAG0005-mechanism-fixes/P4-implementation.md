---
phase: P4
task_id: TAG0005-mechanism-fixes
type: implementation
parent: P2-design.md
trace_id: TAG0005-mechanism-fixes-P4-20260813
status: draft
created: 2026-08-13
agent: implementer
---

# P4 实现说明 — agate 机制修复批（TAG0005）

> implementation_dir: `agate/`（协议文档 + scripts + templates + tests README）

## 改动清单（六处修复 + 同步更新）

### 1. RM-AG0010 — C8 表补 backend P2 评审（BDD-1/2）

三处 C8 表 backend 行补 `plan-eng-review（P2 方案评审）`，保留既有 `review（P4 后）`，并各补去重说明：

- `agate/role-system.md` C8 表 backend 行：`| backend | 任意 | review（P4 后）|` → `| backend | 任意 | plan-eng-review（P2 方案评审）+ review（P4 后）|`；表后补「**去重说明**：同一任务命中多行且触发同一评审角色时，去重只派发一次（如 backend + high 均命中 plan-eng-review，只派 1 个）」
- `agate/rules/review-mapping.md` C8 表：backend 行拆两行 `| backend | 任意 | plan-eng-review | P2 |` + `| backend | 任意 | review | P4 后 |`；表后补去重说明 blockquote
- `agate/phase-cards/P2-design.md` C8 表（评审派发节）：新增 `| backend | 任意 | plan-eng-review（P2 方案评审） |`；表后补去重说明
- `check-gate.sh` P2 分支**未动**（BDD-2 硬约束，P3 断言 G2 全绿验证无条件要求仍在）

### 2. RM-AG0011 — P5 主/辅计数（BDD-3/4/5/6）

- `agate/scripts/agate-gate-p5-count.py`：输出改单行双值 `"{main} {aux}"`——
  `main = len(re.findall(r"^  P5:", block))`（精确 `P5:`，不匹配 P5_*）；`aux` 为 `^  (P5_\w+):` 命中键中**排除 `_formatter` 键**；无 gate_commands 块输出 `0 0`。aux 排除语义与 `agate-read-p5-commands.py` L29-30 对齐（该文件未改，P5C.* 全绿守卫）
- `agate/scripts/check-gate.sh` P5 分支（L253-258）：读双值拆 `P5_MAIN`/`P5_AUX`，`P5_TOTAL=$((P5_MAIN + P5_AUX))`；`P5_TOTAL>1` 时输出 `GATE P5 WARNING: P2 声明了 ${P5_MAIN} 个主命令 + ${P5_AUX} 个辅助命令（共 ${P5_TOTAL} 条 gate_commands.P5 命令），请确认已全部执行（非子集）。`；T060 第二行保留
- 测试断言已由 P3 同步（GPC.1 `1 2` / GPC.2 `0 0` / GPC.3 `1 0`；G5_CMD.1/5 主/辅文案）——本阶段不改测试，自跑全绿

### 3. RM-AG0012① — Review 指令按角色类型条件注入（BDD-7/8/9）

- `agate/assets/templates/dispatch-prompt.md`：主代码块（L9-13）**移除**「## Review 角色特别指令」节；在 `## 阶段特定提示（按需追加到 prompt 末尾）` 下新增首个子节 `### Review 角色特别指令`（代码块含完整指令文本，status draft→approved/rejected/needs-revision 语义原样保留）
- `agate/scripts/agate-render-dispatch-prompt.sh`：新增 `review_appendix`——`ROLE_DIR="review-roles"` 时 `sed -n '/^### Review 角色特别指令$/,/^### /p' "$TEMPLATE" | sed '/^### /d' | extract_first_code_block`；组装顺序 main_block → review_appendix → 阶段 appendix（评审指令位于阶段追加之前）
- `agate/dispatch-protocol.md` 内联模板（「## 你的角色定义」后）：加备注「若派发评审角色（review-roles），须追加 assets/templates/dispatch-prompt.md 中评审角色专用节的 status 字段语义说明（产出 Header 初始 draft、完成后改 approved/rejected/needs-revision，gate 读 Header 非返回摘要）」。**避免出现「Review 角色特别指令」字面量**（BDD-9 断言 `grep -rl` 仅命中模板单文件，已绿）

### 4. RM-AG0012② — render 角色不存在 exit 2 回归（BDD-10/11）

v0.23.0 已修复（exit 2 + stderr 报错），**无脚本改动**。RP.17 测试已由 P3 添加，自跑绿（回归锁定）。

### 5. RM-AG0003 — 空返回自动重试（BDD-12/13/14）

`agate/dispatch-protocol.md` 空返回恢复策略「第 1 次空返回」小节改写为步骤 a-e：
- a. 自动重试一次（相同 prompt 原样重发，**不占用 retries[Pn] 槽位**）；会话时长 <1min → 输出「会话时长异常短」告警（复用下方派发耗时弱信号）并照常重试一次
- b-e. 自动重试仍空返回 → 计入 retries[Pn] → 分析原因 → 调整策略重派 → 更新 prompt_changed 记录
- 「禁止」段后补豁免说明：「自动重试一次」是「相同 prompt 直接重试」禁令的唯一豁免——仅限首次、单次、原样重发；失败后进入 b-e，此后仍禁止不调整直接重试
- **retry 上限 / PAUSED 段未改**（BDD-14，`MAX_RETRY` / `PAUSED 报告人工` 保留）

### 6. 同类扫描守卫 / check-debt.sh 依赖加载失败（BDD-15/16）

`agate/scripts/check-debt.sh` `--retreat-coverage` 模式：
- L26（source 失败）：`exit 0` → `exit 2`，消息保留「无法加载 agate-workspace-resolve.sh」
- L28（文件缺失）：消息改 `GATE DEBT: 缺少 agate-workspace-resolve.sh，无法解析工作区，回退覆盖比对无法执行`，`exit 0` → `exit 2`（删去「跳过回退覆盖比对」措辞——依赖失败不是有意跳过）
- 头部注释 L5/L6/L13 同步：覆盖模式「依赖加载失败 exit 2（需主 Agent 自判），无 retreat 提交等有意跳过分支仍 exit 0」
- 「有意跳过」分支（无 retreat 提交 → exit 0）保持不变（test_bdd_13/14/15 绿验证）

### 同步更新（P1 I4/I8 + P2-review NB-1）

- `agate/tests/README.md` L33：render 计数 16 → **20**（RP.17/18/19 新增 + 既有 1 漂移修正）
- `agate/scripts/README.md` L23：check-debt.sh `--retreat-coverage` 描述从「恒 exit 0」改为「依赖加载失败 exit 2（需主 Agent 自判），无 retreat 提交等有意跳过 exit 0」
- `agate/rules/state-transitions.md` L84 / `agate/UPGRADING.md` L120：核验后均无「恒 exit 0」表述（L84「不阻断 commit/发布」、L120「只读提醒，不挂 gate」仍与 exit 2 语义一致），**无需改动**
- `count-tests.sh` L22 陈旧引用**不改**（P1 I8 排除）

## 约束节

- 最小实现：仅上述改动清单，未加功能、未重构、未顺手改进。
- 测试纪律：P3 测试未改任何一行（16 条 BDD 契约原样）；RP.17 天然绿保持。
- 格式约束：本文件无行首 `- PASS`/`- FAIL` 格式。

## 自查结果（自查 ≠ P5 gate）

- `bats agate/tests/unit/agate-gate-p5-count.bats agate/tests/unit/check-gate.bats agate/tests/unit/agate-render-dispatch-prompt.bats agate/tests/unit/agate-debt-check.bats` → 全绿（GPC.1-3、G5_CMD.1-5、RP.17/18/19、BDD-1/2/9/12/13/14/15 文档断言、test_bdd_16 全过）
- 全量 bats 自查：unit 619 + regression 17 + integration 84 + sanity 6 = **726 全绿**（714 基线 + P3 新增 12 用例）
- `shellcheck -S warning`（check-gate.sh / check-debt.sh / agate-render-dispatch-prompt.sh）→ 0 error
- `python3 agate/scripts/check-protocol-consistency.py` → 0 ERROR
- `bash agate/tests/scripts/count-tests.sh` → 总计 720（不含顶层 sanity.bats 6 条，与 README 计数表口径一致）

## DESIGN_GAP / SCOPE+ / SCOPE_GAP

- 无 [DESIGN_GAP]（P2 设计对 6 处修复均无歧义，实现按设计逐条落地）。
- 无 [SCOPE+]（未发现 P1/P2 未覆盖的新隐含需求）。
- 无 [SCOPE_GAP]（prompt 派发指引覆盖 P2 设计全部声明改动）。
- 备注：`agate/tests/README.md` check-gate.bats 计数行已同步（100→124，含本任务 P3 新增 7 条 + 既有漂移修正）与 agate-gate-p5-count.bats 行已同步（2→3，本任务 GPC.3 新增）。

## 环境隔离

`[PROD_NOT_TOUCHED]`——本阶段全程仅在 worktree 内读写协议文件/脚本并运行本地 bats/shellcheck/consistency 自查，未接触生产环境。
