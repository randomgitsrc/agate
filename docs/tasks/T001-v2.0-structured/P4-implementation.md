---
phase: P4
task_id: T001
type: implementation
parent: P2-design.md
agent: implementer
implementation_dir: agate/scripts/
---

# P4 实现记录

> 本文件按流分节追加。流 B/C/D 派发时会在本文件下追加对应小节，不覆盖已有小节。

## 流 A

### 目标

P1/P2 frontmatter 字段迁移 + 双读工具改造 + 新增 frontmatter schema 校验器 + pre-commit 挂载 +
CHECK 9 锚点表校准（P2-design.md §3.1，P3-test-cases.md §2 流 A 验收清单）。

### 改动文件清单

1. **`agate/scripts/agate-md-field-get.py`（改造）**
   - 新增 `_read_frontmatter` / `_get`（字段级 presence 检测，FIND-1 判别契约）：字段在
     frontmatter 中存在（key 存在且值非 null）→ 取 frontmatter；否则正则回退。
   - 新增 `_format_value`：bool 字段（`ui_affected`/`internal_only`/`design_trivial`）统一
     `str(v).lower()`，输出恰好 `"true"`/`"false"`（FIND-4 归一化落地）；list 字段空格连接；
     int 字段 `str(int)`。
   - 保留原有 3 个 op（`risk_level`/`ui_affected`/`phases`）的正则回退逻辑字节级不变（回归安全）。
   - 新增 op：`candidate_count`（int）、`packages`/`domains`/`coupling_checklist`/
     `follows_existing_pattern`（list）、`override`/`internal_only_reason`/`跳过风险`（presence
     字符串）、`internal_only`/`design_trivial`（bool）。
   - 5 个既有调用点（check-pruning.sh:16,18 / check-p6-provenance.sh:25,152 /
     check-p6-evidence.sh:61）未改动，仍传 `FILE` env + op 名，接口不变。
   - 对应：BDD-1（MDF.1/MDF.5/MDF.6）、BDD-3（MDF.4）、BDD-9（MDF.2）、BDD-10（MDF.3）。

2. **`agate/scripts/agate-frontmatter-check.py`（新建）**
   - 范式仿 `agate-state-yaml-check.py`：`FILE` env 读文件，输出错误行（一行一条），无错误输出空。
   - `SCHEMAS` 字典按文件名（`P1-requirements.md`/`P2-design.md`/`P6-acceptance.md`/
     `P7-consistency.md`）分类，含 `migrated_keys`（该文件 schema 的迁移字段子集，供文件级新旧格式
     判定）、`required`（必填）、`enums`（枚举）、`types`（类型）、`min_values`（最小值）。
   - 判定链：文件名不在 4 类目标内 → 不校验；无 `---` frontmatter 块 → 旧格式 exit 0（BDD-9）；
     `yaml.safe_load` 抛 `YAMLError` → 打印 `str(e)`（含行号/上下文，BDD-2/4/7）；解析结果非 dict
     （FIND-5，如单行全角冒号纯量，无异常但非 dict）→ 硬拦截"必须为 key: value 映射"；解析结果 dict
     但不含该 schema 的 `migrated_keys` 任意一个 → 旧格式 exit 0（FIND-1 核心：P7 文件只有
     `blocker_count` 等自身字段时仍按 P7 schema 校验，不被误判整文件旧格式）；否则走必填/枚举/
     类型/嵌套深度（`_value_depth`，>3 报错，BDD-12）校验。
   - 对应：BDD-2/4/5/6/7/8/12（CF.1-CF.10）+ FIND-1（CF.6）+ FIND-5（CF.9）。

3. **`agate/scripts/check-frontmatter.sh`（新建）**
   - 薄壳，完全仿照 `check-state-yaml.sh`：`FILE=... python3 agate-frontmatter-check.py`，
     非空输出 → 打印到 stderr + exit 1；空输出 → exit 0；文件不存在 → exit 0。
   - 对应：BDD-8（CF.10）。

4. **`agate/scripts/pre-commit-gate.sh`（仅新增挂载点）**
   - 在既有 STATE_FILE 循环内新增步骤 "2g.2"（紧邻 2g.1 PROD_TOUCHED 检测之后，此时
     `TASK_DIR`/`TASK_REL` 均已就绪）：扫描本任务暂存的 `P1-requirements.md`/`P2-design.md`/
     `P6-acceptance.md`/`P7-consistency.md`，逐个跑 `check-frontmatter.sh`，非空输出 → exit 1
     拦截 commit。
   - 用 `[ -x "$AGATE_ROOT/scripts/check-frontmatter.sh" ]` 做存在性守卫（与既有 2p 步骤对
     `agate-next-card.sh` 的守卫同惯例）——`dispatch-context-warning.bats` 的 `B3-warning`
     用例构造了一个仅含旧脚本子集的"精简 fake AGATE_ROOT"（未拷贝 `check-frontmatter.sh`），
     不加此守卫会导致 `bash: 找不到该脚本` 提前 `exit 1`，掩盖该用例本应验证的
     dispatch-context 缺失 WARNING。加守卫后不影响真实 AGATE_ROOT（脚本必然存在）。
   - 对应：BDD-8 挂载点（无独立 P3 阶段可执行断言，由 P5/P6 结合真实 hook 验证；本次自查已跑
     `integration/pre-commit-hook.bats`（42 用例全绿）+ `dispatch-context-warning.bats` 确认无回归）。

5. **`agate/scripts/check-protocol-consistency.py`（CHECK 9 锚点表）**
   - `SCRIPT_ALIGNMENT_ANCHORS` 追加第 38 条：`desc="frontmatter schema 校验"`,
     `script="agate/scripts/check-frontmatter.sh"`, `keywords=["frontmatter"]`,
     `callers=["agate/scripts/pre-commit-gate.sh"]`。
   - 实测锚点总数 37→38；`check_anchor_coverage` 反向覆盖检查不再对 `check-frontmatter.sh`
     输出 WARNING（脚本已在锚点表中登记，`pre-commit-gate.sh` 已引用，caller 检查同步通过）。
   - 对应：BDD-13（`CON.8`，integration/，由 P5/P6 验证；自查已跑 `consistency.bats` 11 用例全绿）。

### 未改动文件（确认，非遗漏）

[DESIGN_GAP: check-gate.sh 的 P2 分支未按 P2-design.md §3.1.2 迁移到双读工具——现有 grep 对顶格 frontmatter 字段巧合兼容，已用 git stash 验证行为一致，但设计明确要求"为统一解析可靠性仍需迁移"]
- **`agate/scripts/check-gate.sh`**：约束允许改 P2 分支，但空跑自查确认 `G_BDD1.1`/`G_BDD9.1`/
  `G_BDD10.1`（BDD-1/9/10 在 check-gate.sh 侧的覆盖用例）在改造前已是绿灯——P2 分支现有实现用
  `grep -E '^candidate_count:'`/`grep -cE '^(packages|domains|ui_affected|gate_commands):'`
  对整文件取值，frontmatter 块内容本身顶格书写、且总在正文之前，`grep`/`head -1` 天然优先命中
  frontmatter（P3-test-cases.md §2 已标注为 "characterization：文件首现优先 grep 巧合正确"）。
  最小实现原则下不做无必要改动；已用 `git stash` 方式验证这些用例在改造前后行为一致（均为绿）。

[DESIGN_GAP: check-pruning.sh 的 8 个 P1 字段读取点同理未迁移，理由同上]
- **`agate/scripts/check-pruning.sh`**：同理，`P2.6c`/`P2.7a`/`R4.2`/`R4.3`/`R3.2` 等 BDD-1 相关
  用例在改造前已绿（`risk_level`/`phases` 走 `agate-md-field-get.py` 双读点未改接口；其余 8 个
  P1 字段读取点用 `grep -qE '^field:'` 对整文件取值，同上"顶格 grep 天然兼容 frontmatter"原因）。
  未做修改，自查全绿确认无需改动。

### 594 配平（BDD-11）

`check-frontmatter.bats` 新增 10 个 `@test`（CF.1-CF.10），由 P3 test-designer 在受影响文件内
移减/合并 10 条重复覆盖的既有断言配平（详见 P3-test-cases.md §1 594 配平表），本阶段未改动测试
文件本身，仅确认红灯转绿。

### 自查结果（非 P5 gate，仅确认未做错）

```
bats agate/tests/unit/check-frontmatter.bats agate/tests/unit/agate-md-field-get.bats \
     agate/tests/unit/check-gate.bats agate/tests/unit/check-pruning.bats \
     agate/tests/regression/v060-p8-internal-only.bats agate/tests/regression/v060-r4-cached.bats \
     agate/tests/unit/check-tdd-red.bats
```
184/185 通过；唯一失败 `G_BDD16.1`（流 B 范围，本次不处理，符合派发指引第 7 条预期）。

补充自查（超出指定命令范围，用于确认无越界回归）：
- `bats agate/tests/unit/ agate/tests/regression/`：516 用例，10 个失败，均为派发指引第 7 条
  明确列出的流 B/C/D 预期红灯（`G_BDD16.1`/`F_BDD18.1`/`PV_BDD19.1`/`PV_BDD20.1`/`RT_BDD21.1`/
  `SC_BDD22.1`/`SY.1`/`CL.6`/`CL.7`/`CL.8`），无新增失败。
- `bats agate/tests/integration/pre-commit-hook.bats agate/tests/integration/consistency.bats`：
  53 用例全绿（含 `CON.8` BDD-13 锚点表 37→38 校验、`B3-warning` 回归确认）。
- 过程中发现并修复一处自引入回归：`pre-commit-gate.sh` 挂载点最初无脚本存在性守卫，导致
  `dispatch-context-warning.bats` 的 `B3-warning`（该用例用精简 fake AGATE_ROOT 模拟旧脚本
  集）提前因"找不到 check-frontmatter.sh"而 exit 1，掩盖了它本应验证的 WARNING 输出；已加
  `-x` 守卫修复，见上文改动清单第 4 条。

以上均为自查，不代表 P5 gate 已过。
