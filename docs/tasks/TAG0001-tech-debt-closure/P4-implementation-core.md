---
phase: P4
task_id: TAG0001-tech-debt-closure
type: implementation
parent: P2-design.md
trace_id: TAG0001-P4-20260812
status: draft
created: 2026-08-12
agent: implementer
---

# TAG0001 — P4 实现记录（implementer-core：核心脚本/模板）

> 角色：implementer-core。范围：仅 5 个文件（新增 3 + 改造 2），不触碰 docs 组文件集。
> 输入：P4-dispatch-context-implementer-core.md + P2-design.md（D1-D4）+ P3-test-cases.md + 测试代码。

## 改动清单（5 个文件，均落 worktree `agate/`）

### 新增

1. `agate/assets/templates/tech-debt-template.md`
   - 用法 / 登记判据（三分法，含 BDD-19「验收声明」判据 + 「不登记」合法出口）/ 字段表 / 三态语义表 / 三个示例条目（open / closed / retreat）/ 回退强制说明。
   - 示例条目可被 yaml.safe_load（consistency CHECK 1 通过）；示例 evidence 引用真实存在的文件（`docs/reviews/review-20260812-1204.md`、`docs/tasks/TAG0003-workspace-architecture/P6-acceptance.md`），避免 CHECK 2 死链 ERROR。
   - 含「登记 DEBT 不豁免当前任务」硬规则（BDD-20）。

2. `agate/scripts/agate-debt-check.py`
   - 两种模式：默认（`FILE` env）= tech-debt.md 多条目 schema 校验；`--covered-hashes FILE` = 提取 `source: retreat` 条目 evidence 中的 hex token（7-40 位），去重逐行输出。
   - 解析契约（D1）：` ```yaml ` fenced 块提取（正则同 check-protocol-consistency.py extract_code_blocks），逐块 yaml.safe_load，非 dict 报错；无 yaml 块 → no-op（BDD-10）。
   - schema 规则（D2，P2 §2.2）：必填（id/category/title/status/priority/evidence/impact/recommendation/closure_criteria/source/created_at）、枚举（category=technical|management|protocol、status=open|in_progress|closed、priority=high|medium|low、source=retreat|review|retrospective）、类型（task_id null|str；evidence/closure_criteria list；created_at 及 str 字段须 str）、closed 准入（task_id 非空 + evidence 序列化文本同时含 task_id 与 P5/P6）、id 唯一。
   - 错误输出格式 `{basename}:{entry_id}: {msg}`（无 id 用块序号），fail-closed 兜底（异常转错误行）。

3. `agate/scripts/check-debt.sh`
   - 双命令薄壳（D3）：默认 `FILE` = schema 校验（复刻 check-frontmatter.sh：`[ ! -f ] && exit 0`、mktemp stderr、python exit≠0 → exit 1、ERRORS 非空 → exit 1）；`--retreat-coverage` = 回退比对（恒 exit 0 + WARNING）。
   - `--retreat-coverage`：source agate-workspace-resolve.sh 解析 `{AGATE_WORKSPACE}`；`git log --all --grep='^retreat:'` 提取 retreat 提交；与 `--covered-hashes` 集合比对（short 前 7 位或 full hash）；缺失 → stderr `GATE DEBT WARNING: ...`；tech-debt.md 不存在 → 每条都打缺失 WARNING（BDD-13）。

### 改造

4. `agate/scripts/check-gate.sh` P8 分支
   - 在 bump_type 检查之后、version 检查之前插入 `debt_check:` 留痕检查（D4 / P2 §2.5）：`grep -q 'debt_check:' "$TASK_DIR/P8-release.md"` 缺失 → exit 1 + 提示（值任意含 none 均放行，BDD-17）。

5. `agate/scripts/agate-retreat-to.sh`
   - 回退全部 commit 完成后追加一行提醒：`GATE RETREAT: 回退已完成——请为本次回退建立 source: retreat 的 DEBT 条目（{AGATE_WORKSPACE}/debt/tech-debt.md...）`（过程强制点，BDD-12）。

## 自查结果（≠ P5 gate）

- `bats agate/tests/unit/agate-debt-check.bats`：**18/20 绿**。红色 2 条均不在本角色文件集：
  - `test_bdd_2`：P3 测试 fixture 的 `mkdir -p "$dir/{roadmap,...}"` 引号包裹导致大括号不展开，只建 1 个目录（实测 n=1）——测试代码缺陷，非实现问题。
  - `test_bdd_3`：断言 `SETUP.md` 含 `debt/`（docs 组文件，并行修改中，当前为 0 处）。
  - 其余 18 条（含 BDD-5..15 全部脚本行为 + BDD-17/19/20 模板/脚本锚点）全绿。
- `bats --filter "P8" agate/tests/unit/check-gate.bats`：**10/10 绿**。G8.9（缺 debt_check → exit 1）红转绿；G8.10（debt_check 内容任意 → exit 2 守卫）保持绿；G8.1-8.8 fixture 同步后无回归。
- `bats agate/tests/unit/agate-retreat-to.bats`：**5/5 绿**（DEBT 提醒行不破坏既有断言）。
- `bats agate/tests/unit/check-gate.bats`（全文件 113 用例）：0 not ok。
- `python3 agate/scripts/check-protocol-consistency.py`：全部 CHECK PASS，0 ERROR。
- `shellcheck -S warning` check-debt.sh / check-gate.sh / agate-retreat-to.sh：0 告警。

## [DESIGN_GAP] 声明

[DESIGN_GAP: P3 测试 fixture test_bdd_2 的 mkdir -p 大括号被引号包裹不展开，仅建 1 目录（应为 9）——测试代码缺陷不在本角色文件集，已如实标注，交由主 Agent/docs 组处理（改测试 fixture 或评估断言），本次未改动测试文件]
[DESIGN_GAP_REVIEWED: 已确认——主 Agent 2026-08-13 修复测试 fixture：mkdir -p 改为显式参数（"$dir/roadmap" "$dir/tasks" ... "$dir/debt"），大括号不再被引号包裹，test_bdd_2 转绿；另修复 test_bdd_3 SETUP 断言（grep 'debt/' → grep 'debt'）与 R5.1-3 fixture 补 debt_check: none（SCOPE+ #1 同步面延伸）。全量 676 用例绿。]

## [SCOPE+] 声明

- [SCOPE+] #1（G8 fixture 同步）/ #2（consistency 锚点 + scripts README）已在 P3/P2 声明，不属于本次新增；本实现未触碰 check-protocol-consistency.py 与 scripts/README.md（docs 组范围）。

## 边界确认

- 未改动本角色文件集之外的任何文档/卡片/规则/测试 fixture。
- 未改动 `~/.agate`（稳定版开发工具）。
- 测试用 worktree 本体（load.bash 反推 AGATE_ROOT 到 worktree agate/）。
- 状态标记：本次实现全部在 worktree 的协议仓库内，未触达生产环境/外部系统，`[PROD_NOT_TOUCHED]`。
