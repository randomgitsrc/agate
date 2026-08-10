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

## 流 B

### 目标

P6/P7 结果结构化（BDD-16..20，P2-design.md §3.2）：P6 pass/fail 汇总入 frontmatter +
逐条行格式从严校验；P7 BLOCKER/DEVIATION/DESIGN_GAP 状态计数结构化入 frontmatter；
FIND-6 交叉校验 WARNING（frontmatter 汇总 vs 正文逐条行数不一致时提示复核，非阻断）。
本流在流 A 交付的 `agate-md-field-get.py`（`_read_frontmatter`/`_get`/`_format_value`/
`KNOWN_OPS`）与 `agate-frontmatter-check.py`（P6/P7 schema 已含必填字段/类型规则）基础上
追加，不重新发明。

### 改动文件清单

1. **`agate/scripts/agate-md-field-get.py`（追加）**
   - 新增 `NO_FALLBACK_INT_FIELDS` 常量集合：`pass`/`fail`/`blocker_count`/
     `deviation_count`/`deviation_critical_count`/`design_gap_count`/
     `design_gap_reviewed_count` 共 7 个流 B 字段。
   - 这 7 个字段在 v0.35 正文里从来不是单行声明（旧格式靠 grep 计数行数/关键词数，不是
     读一个字段）——`_get` 对这些字段在 frontmatter 无该 key 时**直接返回空字符串**，不
     调用 `_regex_fallback` 模拟正则计数；"回退到旧格式计数逻辑"的责任交给调用方
     （`check-gate.sh`/`check-p6-provenance.sh`），二者不混在一个函数里（约束 3）。
   - `_format_value` / `KNOWN_OPS` 同步纳入这 7 个字段（int 格式化 `str(int)`，逻辑与既有
     `INT_FIELDS` 一致，但作为独立集合以承载"无回退"语义标注）。
   - 对应：BDD-16（`G_BDD16.1`）、BDD-19（`PV_BDD19.1`）、BDD-20（`PV_BDD20.1`）的读取层
     基础设施。

2. **`agate/scripts/check-gate.sh`（只改 P6/P7 分支）**
   - **P6 分支**：先读 frontmatter `pass`/`fail`（新 op）；两者均非空 → `TOTAL=pass+fail`，
     `FAIL=fail`，基于该结构化汇总判定（BDD-16）；否则回退正文 grep，但计数口径从
     `^\s*- (PASS|FAIL)` 收紧为 `^\s*- (PASS|FAIL)\b.*BDD-[0-9]`（要求行内含 BDD 编号才计
     入，消除总结行如 `- PASS: 16` 的误判，BDD-18）——沿用大小写不敏感（保留
     `G6.7`"小写 fail: 计为 FAIL"的既有行为，用 `\b.*BDD-[0-9]` 而非严格锚定"PASS 后紧跟
     BDD"，兼容 `- fail: BDD-2 broken` 这类历史写法）。证据目录检查等下游逻辑不变。
   - **P7 分支**：BLOCKER/DEVIATION-CRITICAL 先读 frontmatter `blocker_count`/
     `deviation_critical_count`，两者均非空 → 直接用于判定（BDD-19），不再用
     `grep -cvE '\[BLOCKER\][:：]?[0-9]+条?$'` 排除总结行；否则回退既有正文 grep 逻辑。
     DESIGN_GAP 配对同理：先读 `design_gap_count`/`design_gap_reviewed_count`，两者均非空
     → `reviewed_count < count` 才拦截（BDD-20，消除 F14 数量相减 0-vs-0 歧义）；否则回退
     既有正文 grep 数量相减逻辑。P4 `[DESIGN_GAP:]` 转抄核对（R2.3）**不改**——仍从
     P4-implementation.md 正文 grep，与最终得到的 `DESIGN_GAP_COUNT`（无论来自 frontmatter
     还是正文回退）比较，逻辑与既有代码一致。启发式 WARNING / N3 WARNING 均保留，使用同一
     组 `DESIGN_GAP_COUNT`/`DESIGN_GAP_REVIEWED` 变量。
   - 对应：BDD-16/18/19/20 全部落点。

3. **`agate/scripts/check-p6-format.sh`（升级为 --check/--fix 双模式）**
   - `--check` 模式重写为独立的"行格式校验"，不再靠"和 --fix 输出 diff"判定：逐行用
     `grep -qiE '^\s*-\s+(pass|fail)\b'`（大小写不敏感 + 词边界，排除 "failure" 等非目标
     词）识别"疑似 PASS/FAIL 逐条声明"候选行，候选行若不满足严格形式
     `^\s*-\s+(PASS|FAIL)\s+BDD-[0-9]+`（大写、紧跟一个空格、带 BDD 编号）即计入
     `INVALID`；`INVALID>0` → exit 1 提示用 `--fix`；否则 exit 0（BDD-17/18）。
   - `--fix` 模式：v0.35 归一化 sed 三段逻辑（小写→大写、缩进裁剪、总结行→
     `**Summary**:`）原样保留，字节级未改动实现，仅删除了原先"--check 靠 diff 判定"的尾部
     死代码（因为 --check 已在文件靠前的独立分支处理并 `exit`，不会再执行到该处）。
   - 对应：BDD-17（`F_BDD17.1`，characterization 保持绿）、BDD-18（`F_BDD18.1`，本次转绿，
     虽然 BDD-18 的验收对象实为 check-gate.sh P6 分支，但依赖本文件行格式校验就位）。

4. **`agate/scripts/check-p6-provenance.sh`（只改审计 3 + 审计 2 排除范围）**
   - **审计 3**（P1 BDD 数 vs P6 结果数）：`P6_BODY_STRICT` 改用从严 grep
     `^\s*- (PASS|FAIL) BDD-[0-9]`（大小写敏感、紧邻 BDD 编号，对齐 P2-design.md §3.2.1
     原文口径，与 check-gate.sh P6 分支的宽松兼容口径**有意不同**——一个是"面向旧格式全部
     历史写法兼容"，一个是"面向新格式行格式已从严的场景"）；若 frontmatter `pass`+`fail`
     均非空 → `P6_TOTAL = pass+fail`（新格式优先），否则 `P6_TOTAL = P6_BODY_STRICT`（旧格式
     回退）。P1_BDD 判定逻辑不变。
   - **FIND-6 交叉校验 WARNING（新增）**：仅在新格式路径下（frontmatter 汇总存在时），若
     `P6_TOTAL ≠ P6_BODY_STRICT` → 输出 `GATE PROVENANCE WARNING: ...请复核`，**`exit` 不受
     影响**（沿脚本既有控制流继续往下走，不 `exit 1`）——纯 nudge，不提升 gate 强度。
   - **审计 2**（dispatch-context 预判扫描）：排除范围从"仅 AGATE_CARD 块"扩展为"AGATE_CARD
     块 + 文件顶部第一对 `^---$` 定界的 frontmatter 块"，用 `sed '/^---$/,/^---$/d'` 追加在
     AGATE_CARD 剔除之后（AGATE_CARD 块内如含独立的 `---` markdown 分隔线，已被前一步剔除，
     不会误触发本步骤的 frontmatter 块匹配）。对应 P2-design.md §3.2.3。
   - 对应：BDD-17/18（审计 3 从严）、FIND-6（§13，决定"加"）、P1 隐含需求 #11（§3.2.3 审计 2
     白名单同步）。

### DESIGN_GAP 声明

[DESIGN_GAP: check-gate.sh P6 分支旧格式回退的正文 grep 计数正则，未采用 P2-design.md §3.2.1 给出的严格锚定形式 `^\s*- (PASS|FAIL) BDD-[0-9]`（PASS/FAIL 后紧跟空格再接 BDD 编号），而是用更宽松的 `^\s*- (PASS|FAIL)\b.*BDD-[0-9]`（只要求行内含 BDD 编号，不要求紧邻）。原因：check-gate.bats 既有用例 G6.7（"小写 fail: 被计为 FAIL"）body 是 `- fail: BDD-2 broken`——FAIL 与 BDD 编号之间隔着一个冒号，严格锚定形式无法匹配，若照抄设计给出的正则会导致该既有绿灯用例回归为红灯。check-p6-provenance.sh 审计 3 的 `P6_BODY_STRICT` 计数已严格照抄设计原文正则（未做此放宽），两处口径故意不同——前者面向"check-gate.sh P6 分支需兼容全部历史正文写法"，后者面向"provenance 审计已按 BDD-17 从严格式的场景"。]

[DESIGN_GAP: check-gate.sh P6/P7 分支判断"是否走新格式（读 frontmatter）"时，采用"该判定所需的全部字段皆非空"作为切换条件（P6：pass 与 fail 都非空才用汇总；P7：blocker_count 与 deviation_critical_count 都非空才用该判定，design_gap_count 与 design_gap_reviewed_count 都非空才用该判定），而非"任一字段非空即可"。P2-design.md §3.2.1/§3.2.2 原文表述为"frontmatter 无这些字段（旧格式）→ 回退"，未明确"这些字段"是指"任一缺失"还是"全部缺失"才算旧格式。选择"全部非空才算新格式"是因为 agate-frontmatter-check.py 的 P6/P7 schema 本身把这些字段声明为必须成组出现的 required 元组（P6: pass+fail+ui_affected 三者一起必填；P7: 五个计数字段一起必填），pre-commit 层已保证新格式文件不会出现"只填一半"的中间态，故本次判定选择更严格的"AND"语义，避免半填字段被误判为新格式而只用部分字段判定。]

### 未改动文件（确认，非遗漏）

按约束仅改动上述 4 个文件；`check-scope-resolved.sh`/`check-changelog.sh`/
`agate-state-yaml-check.py`/`agate-frontmatter-check.py`/`check-frontmatter.sh`/
`pre-commit-gate.sh`/模板与角色卡文件/`agate/tests/**` 均未触碰，符合派发指引范围锁定。

### 594 配平说明

本流不涉及新增测试文件，`agate/tests/**` 未改动（测试已由 P3 test-designer 写好并
commit），594 配平口径无变化。

### 自查结果（非 P5 gate，仅确认未做错）

指定自查命令（派发指引第 12 条）：
```
bats agate/tests/unit/check-gate.bats agate/tests/unit/check-p6-format.bats \
     agate/tests/unit/check-p6-provenance.bats agate/tests/regression/v060-design-gap.bats \
     agate/tests/unit/check-frontmatter.bats agate/tests/unit/agate-md-field-get.bats
```
163/163 通过，0 失败。目标红转绿：`G_BDD16.1`/`F_BDD18.1`/`PV_BDD19.1`/`PV_BDD20.1` 全部转
绿；回归绿灯保持：`F_BDD17.1`、`v060-design-gap.bats` 4 条（R2.1/R2.2/R2.3/R2.3b）、流 A 的
`CF.*`（10 条）/`MDF.*`（6 条）均未变红。

补充自查（超出指定命令范围，用于确认无越界回归）：
- `bats agate/tests/unit/ agate/tests/regression/`：516 用例，510 通过，6 失败——全部是派发
  指引第 11 条明确列出的流 C/D 预期红灯（`RT_BDD21.1`/`SC_BDD22.1`/`SY.1`/`CL.6`/`CL.7`/
  `CL.8`），相较流 A 交付时的 10 个预期红灯，本次流 B 覆盖的 4 个（`G_BDD16.1`/
  `F_BDD18.1`/`PV_BDD19.1`/`PV_BDD20.1`）已转绿，无新增失败、无意外崩溃。
- `bats agate/tests/integration/pre-commit-hook.bats agate/tests/integration/consistency.bats`：
  53 用例全绿（含 `CON.8` BDD-13 锚点表校验），确认 check-gate.sh 改动未影响 pre-commit 挂载
  流程。

以上均为自查，不代表 P5 gate 已过。

## 流 C

### 目标

P1 标记"已解决/已确认"状态结构化（BDD-21/22）+ 发现性标记边界确认（BDD-23，不改）+
角色卡/模板可复制 frontmatter 样例（BDD-24），P2-design.md §3.3 全节。在流 A 交付的
`agate-md-field-get.py`（`_read_frontmatter`/`_get`/`_format_value`/`KNOWN_OPS`）基础上
追加 3 个 op，不重新发明。

### 改动文件清单

1. **`agate/scripts/agate-md-field-get.py`（追加）**
   - 新增 `NO_FALLBACK_LIST_FIELDS` 常量集合：`need_confirm_resolved`/`suggest_resolved`/
     `scope_resolved` 共 3 个流 C 字段。与流 B 的 `NO_FALLBACK_INT_FIELDS` 同理——
     v0.35 正文没有这些字段的单行声明形式，frontmatter 无该字段时直接输出空字符串，
     不做正则回退（调用方自行执行旧格式判定/回退逻辑）。
   - `_format_value` 对这 3 个字段用**换行连接**（而非其余 `LIST_FIELDS` 的空格连接）：
     元素是含空格的散文描述（如"z 的边界条件需确认"），空格连接会让调用方无法区分元素
     边界；换行连接使调用方可用 `grep -qF -- "$desc"` 逐条子串匹配（BDD-21 逐条匹配
     要求）。
   - `KNOWN_OPS` 同步纳入这 3 个字段。
   - 对应：BDD-21（`RT_BDD21.1`）、BDD-22（`SC_BDD22.1`）的读取层基础设施。

2. **`agate/scripts/check-gate.sh`（只改 P1 分支）**
   - **NEED_CONFIRM 逐条匹配**（BDD-21）：新增 `NC_UNRESOLVED` 变量，默认等于原有的
     `NC_BLOCKING`（整段行数计数，格式校验仍用这个原始值，见下）。frontmatter 含
     `need_confirm_resolved:` 字段（用 `sed -n '/^---$/,/^---$/p' | grep -c` 检测该
     key 是否出现在文件头 frontmatter 块内，presence 判定不依赖 op 的空字符串输出，
     因为空列表和字段缺失都会让 op 输出空字符串，两者需要区分）→ 逐条提取正文每条
     `[NEED_CONFIRM]` 的描述文本（`grep -E '^\s*-?\s*\[NEED_CONFIRM\]' | sed -E
     's/^\s*-?\s*\[NEED_CONFIRM\][[:space:]]*//'`），对每条用 `grep -qF` 检查是否
     出现在 `need_confirm_resolved` 列表（op 输出，换行连接）中，未匹配的计入
     `NC_UNRESOLVED`。字段不存在（旧格式）→ `NC_UNRESOLVED` 保持等于整段行数（回退
     v0.35 行为）。用 `NC_UNRESOLVED`（而非 `NC_BLOCKING`）判定是否阻塞——**逐条匹配，
     不是数量相减**（F14 教训：避免 5 项对 5 项但内容对不上的 0-vs-0 歧义）。
   - **格式校验保留用原始 `NC_BLOCKING`**：typo 兜底 2（"不合规的 NEED_CONFIRM 标记
     格式"）的判定条件 `grep -qE '\[NEED_CONFIRM\]' && [ "$NC_BLOCKING" -eq 0 ]` 未改，
     仍用未经"已解决"过滤的原始整段计数——否则一个格式合规但已全部解决的 NEED_CONFIRM
     会被误判为"格式不合规"（`NC_UNRESOLVED` 降到 0 后触发该分支）。
   - **SUGGEST WARNING 去重**（约束 4）：同构实现 `NC_SUGGEST_UNACKED`，frontmatter
     含 `suggest_resolved:` 字段时逐条匹配正文 `[SUGGEST: ...]` 描述（提取时同时剥离
     开头 `[SUGGEST: ` 和结尾 `]`），已采纳（匹配上）的项不计入 WARNING 数。此分支
     P3 无独立可执行断言（P3-test-cases.md §4 流 C 表未列 SUGGEST 去重的红灯用例），
     按派发指引约束 4 的文字要求直接实现，用 `G_SUGGEST.*` 系列既有绿灯用例（无
     `suggest_resolved` 字段场景）验证未回归。
   - 对应：BDD-21（`RT_BDD21.1` 转绿）+ 约束 4（SUGGEST 去重，无独立测试）。

3. **`agate/scripts/check-scope-resolved.sh`（追加，新增 `SCRIPT_DIR` 变量）**
   - 在原有"有 SCOPE+ 但 P1 无 [SCOPE_RESOLVED]"grep 判定**之前**插入新格式短路
     判定：读 frontmatter `scope_resolved`（新 op，换行连接）→ 非空字符串（列表非空）
     → 直接 `echo ... && exit 0`（已解决，不再扫描正文 `[SCOPE_RESOLVED]` 散文标记）。
     op 输出为空（字段不存在 **或** 字段存在但为空列表，两种情况本工具不做区分，
     见下方 DESIGN_GAP）→ 落入原有正文 grep 回退判定（`RESOLVED_COUNT` 逻辑，字节级
     未改动）。
   - 跨文件 `[SCOPE+]` 散文扫描逻辑（`for f in "$TASK_DIR"/*.md; do ...`）**未改动**
     （BDD-23，发现性标记本体保持散文）。
   - 对应：BDD-22（`SC_BDD22.1` 转绿）；SC.2/SC.3/SC.4/SC.6/SC.7 回归绿灯保持
     （均为 `scope_resolved` op 输出空字符串 → 落入原有回退路径，行为与改造前一致）。

4. **`agate/assets/templates/task-files.md`（BDD-24）**
   - P1/P2/P6/P7 产出规格节各新增一段"**可直接复制的完整 frontmatter 样例**"
     YAML 代码块，字段/格式照抄 P2-design.md §3.1.1（P1/P2）+ §3.2.1（P6，P7 字段
     取自 §3.2.2）。P1 样例额外含流 C 的 `need_confirm_resolved`/`suggest_resolved`/
     `scope_resolved` 三个可选字段（含注释说明用途）。
   - 正文原先直接写 `risk_level:`/`phases:`/`packages:`/`domains:`/`candidate_count:`
     等字段的示例段落（P1 结构"5. 裁剪说明"/"6. 范围声明"、P2 结构"0. 候选方案数"/
     "2. 范围声明"）改为"↑ 已迁移至文件头 frontmatter"的指引文字，避免与上方
     frontmatter 样例重复且互相矛盾（一份文档同时给出"写正文"和"写 frontmatter"
     两种示例会误导 subagent）。
   - P1 结构"4. 待确认清单"/"SCOPE+ 增补区"追加一句话说明：已解决/已采纳时不删除
     散文标记，而是在 frontmatter 对应列表中追加描述。
   - P6-acceptance.md 结构原有的正文示例（`- PASS 创建 entry 不填过期 → ...`，未带
     `BDD-N:` 前缀）不符合流 B 已落地的从严格式（`^\s*-\s+(PASS|FAIL)\s+BDD-\d+`），
     顺带订正为 `- PASS BDD-1: ...` 形式（本节本就要改，顺手修正明显过时的示例，
     未扩大改动文件范围）。
   - 新增"## P7-consistency.md 结构"小节（此前该文件不存在 P7 章节）：frontmatter
     样例 + 简要正文结构（DESIGN_GAP 配对 / 跨文件一致性 / 结论）。
   - 全部新增 YAML 样例已用 `yaml.safe_load`（剥离 frontmatter 分隔符后，模拟
     `agate-md-field-get.py` 的 `_read_frontmatter` 实际解析方式）逐块验证可解析。

5. **`agate/assets/execution-roles/analyst.md`（BDD-24）**
   - "5. 裁剪说明"一节原先给的是**正文内嵌 YAML**示例（v0.35 遗留写法，流 A/B 均
     未触碰此文件）。改为"机器字段写入文件头 frontmatter"的完整可复制样例（P1
     全字段 + 流 C 三个可选字段），旧的"仅在适用时声明以下可选字段"body 段落并入
     同一个 frontmatter 样例块。
   - "6. 范围声明"改为指向上方样例（不再单独给 `packages:`/`domains:` 正文写法）。

6. **`agate/assets/execution-roles/architect.md`（BDD-24）**
   - P2 输出说明的 `candidate_count`/`packages`/`domains`/`ui_affected` 四条 bullet
     之后追加一个整合的可复制 frontmatter 样例块（此前四个字段只有分散的行内
     `key: value` 提示，没有一个可直接复制粘贴的完整块）。`gate_commands:`/
     `files_to_read:`/`env_constraints:`/`minimal_validation:` 明确标注"留正文"。

7. **`agate/assets/execution-roles/verifier.md`（BDD-24）**
   - P6 模式"输出"一节追加 P6 frontmatter 可复制样例（`pass`/`fail`/`ui_affected`）+
     一句从严行格式提醒（承接流 B 已落地的 `- PASS BDD-NN:` 格式要求，verifier.md
     此前只在"质量门槛"段提过一次格式规范，未给出独立可复制的 frontmatter 块）。
   - 未改动 P7（consistency-reviewer 角色卡不在派发指引允许改动清单内，P7 样例
     只落在 task-files.md + phase-cards/P7-consistency.md）。

8. **`agate/phase-cards/{P1-requirements,P2-design,P6-acceptance,P7-consistency}.md`
   （BDD-24，产出规格节同步）**
   - 各自"产出规格"节追加对应的可复制 frontmatter 样例块，与 task-files.md /
     角色卡的同一份字段集保持一致（同一来源 P2-design.md §3.1.1/§3.2.1/§3.2.2，
     未重新设计字段名或格式）。

### DESIGN_GAP 声明

[DESIGN_GAP: check-scope-resolved.sh 对 P1 frontmatter scope_resolved 字段"存在但为空列表"与"字段完全不存在"两种情况未做区分处理——两者都落入下方原有正文 [SCOPE_RESOLVED] grep 回退判定，而不是把"字段存在但空"直接判定为拦截。P2-design.md §3.3.1 原文表述为"非空列表即已解决 → 通过；有 SCOPE+ 无 resolved → 拦截；旧格式（frontmatter 无该字段）→ 回退现有正文 grep 判定"，字面上"有 SCOPE+ 无 resolved"（可解读为"字段存在但空"）应立即拦截，与"旧格式（无该字段）才回退"是两条不同的路径。选择合并处理的理由：① `agate-md-field-get.py` 的 `scope_resolved` op 对"字段不存在"和"字段存在但值为空列表"这两种情况都会输出空字符串（`NO_FALLBACK_LIST_FIELDS` 的既定格式化规则——空列表 `"\n".join([])` 结果就是空字符串），仅凭 op 输出无法区分两种情况，需要额外读 frontmatter 块做 presence 检测才能区分（如 P1 分支对 need_confirm_resolved 采用的 `sed -n '/^---$/,/^---$/p' | grep -c '^scope_resolved:'` 方案）；② P3-test-cases.md 给出的唯一流 C 测试用例 SC_BDD22.1 只覆盖"字段存在且非空"（通过）与既有 SC.2/3/4/6/7（字段完全不存在）两种场景，未覆盖"字段存在但显式声明为空列表"这一中间态，测试断言无法反推该场景的确切期望；③ 功能后果上二者等价——"字段存在但空列表"回退到正文 grep 后，只要正文没有遗留的 `[SCOPE_RESOLVED]` 散文标记（新格式任务通常不会再写散文标记），依然会被拦截，与"立即拦截"效果相同，唯一差异是拦截信息的措辞（"无 P1 frontmatter scope_resolved"vs"P1 无 [SCOPE_RESOLVED] 标记"）。风险：若某任务显式声明 `scope_resolved: []` 但正文恰好残留一条旧式 `[SCOPE_RESOLVED]` 散文标记（如从旧格式手动迁移时未清理），会被误判为已解决通过，而非因空列表被拦截——这是本简化相对于字面设计的唯一行为差异，且概率极低（结构化字段和散文标记同时存在但语义相反的场景）。]

### 594 配平说明

本流不涉及新增测试文件，`agate/tests/**` 未改动（测试已由 P3 test-designer 写好并
commit），594 配平口径无变化。

### 未改动文件（确认，非遗漏）

按约束仅改动上述文件；`agate/scripts/check-changelog.sh`、`agate/scripts/agate-state-yaml-check.py`
（流 D）、`agate/scripts/agate-frontmatter-check.py`（流 A 已把三个流 C 字段登记为
P1 schema 可选迁移字段，无需再改）、`agate/scripts/check-gate.sh` 的 P2/P6/P7 分支
（流 A/B 已完成）、`agate/assets/execution-roles/consistency-reviewer.md`（不在允许
改动清单内，P7 样例落在 task-files.md + phase-cards）、`agate/tests/**` 均未触碰，
符合派发指引范围锁定。

### 自查结果（非 P5 gate，仅确认未做错）

指定自查命令（派发指引第 10 条）：
```
bats agate/tests/unit/check-gate.bats agate/tests/unit/check-scope-resolved.bats \
     agate/tests/unit/check-retrospective.bats agate/tests/unit/check-gate-p1-review.bats \
     agate/tests/integration/pre-commit-hook.bats agate/tests/unit/check-frontmatter.bats \
     agate/tests/unit/agate-md-field-get.bats
```
184/184 通过，0 失败。目标红转绿：`RT_BDD21.1`/`SC_BDD22.1` 全部转绿；回归绿灯保持：
`check-gate-p1-review.bats` 的"P1: BDD-21 边界（未结构化解决时仍阻塞）"反面回归用例、
`check-scope-resolved.bats` 的 SC.2/SC.3/SC.4/SC.6/SC.7、`integration/pre-commit-hook.bats`
的 IT_PT_\*/IT_PT_T6.\* 系列、流 A 的 `CF.*`（10 条）/`MDF.*`（6 条）、流 B 的
`G_BDD16.1`/`F_BDD18.1`/`PV_BDD19.1`/`PV_BDD20.1` 均未变红。

补充自查（超出指定命令范围，用于确认无越界回归）：
- `bats agate/tests/unit/ agate/tests/regression/`：516 用例，4 个失败——全部是流 D
  预期红灯（`SY.1`/`CL.6`/`CL.7`/`CL.8`），相较流 B 交付时的 6 个预期红灯，本次流 C
  覆盖的 2 个（`RT_BDD21.1`/`SC_BDD22.1`）已转绿，无新增失败、无意外崩溃。
- `bash agate/tests/scripts/count-tests.sh`：594（不漂移，BDD-11 保持达标）。
- `python3 agate/scripts/check-protocol-consistency.py`：全部 CHECK 1-9 PASS（含 CHECK 9
  锚点表 38 条对齐，未因本流改动产生新漂移）。
- `shellcheck -S warning agate/scripts/check-gate.sh agate/scripts/check-scope-resolved.sh`：
  0 警告。
- `bats agate/tests/integration/ agate/tests/sanity.bats`：全量 integration + sanity
  套件全绿，无回归。
- 全部新增/改动的 frontmatter YAML 样例块（task-files.md 4 处 + analyst.md/architect.md/
  verifier.md 各 1 处 + 4 个 phase-cards 各 1 处）已用 `yaml.safe_load`（按
  `_read_frontmatter` 同等方式剥离首尾 `---` 分隔符后解析）逐块验证可解析，无一失败。

以上均为自查，不代表 P5 gate 已过。

## 流 D

### 目标

任务编号规则硬切（BDD-25..27）：`agate-state-yaml-check.py` 的 task_id 正则从 `^T\d+$`
硬切为 `^T[A-Z]{2}\d+$`（新格式如 `TAG0001`，不兼容旧格式 `T001`）；`check-changelog.sh`
去短前缀提取，直接匹配完整 task_id；文档/模板 task_id 示例同步为新格式（P2-design.md §3.4
全节）。

### 改动文件清单

1. **`agate/scripts/agate-state-yaml-check.py`**（约第 39 行）
   - `re.match(r"^T\d+$", ...)` → `re.match(r"^T[A-Z]{2}\d+$", ...)`
   - 报错信息同步为"应为 T + 2 个大写字母项目代号 + 数字，如 TAG0001"
   - 硬切，未做双格式兼容（F19，P0-brief 已定）

2. **`agate/scripts/check-changelog.sh`**（约第 11-15 行、33-40 行）
   - `TASK_ID_SHORT=$(echo "$TASK_ID" | grep -oE 'T[0-9]+' | head -1)` + 空值回退 →
     直接 `TASK_ID_SHORT="$TASK_ID"`（不再截取短前缀）
   - **额外调整（超出 P2 §3.4.2 字面描述，见下方 DESIGN_GAP）**：移除了原有的
     `grep -qF "$TASK_ID"` 固定字符串 fallback 分支。原因：`TASK_ID_SHORT` 现已恒等于
     `TASK_ID`，若保留该 fallback，会对同一字符串做一次无单词边界保护的子串匹配——
     导致 `TAG0001` 被 `TAG00012`（另一个更长编号任务的条目）误判为已匹配，直接违反
     `CL.7`（BDD-27 明确要求的"不误匹配"用例）。移除后 `CL.6`/`CL.7`/`CL.8` 全部转绿，
     `CL.1`-`CL.5` 回归用例未受影响（均由前面的单词边界正则或 `[Unreleased]` 抽取逻辑
     覆盖，不依赖该 fallback）。

3. **全库 grep 核对下游消费点**（约束 1 第 3 条）：确认全仓库范围内除
   `check-changelog.sh` 外，无其他脚本使用 `grep -oE 'T[0-9]+'` 或等价正则"提取任务
   短号"模式（已排查 `agate-summary.sh`、`active-tasks.md` 相关脚本及全部
   `agate/scripts/*.sh`/`*.py`）。命中的唯一位置就是已处理的 `check-changelog.sh:14`，
   无需额外同步改动。

4. **`agate/assets/templates/active-tasks-template.md`**（第 4 条规则，仅改该条文字）
   - "新任务编号 = 当前最大编号 + 1" → "新任务编号 = `T{项目代号}{编号}`（项目代号 2
     个大写字母，对齐 Jira 风格 `[A-Z][A-Z]+`；编号为动态 `\d+`，3 位起步可扩至 6 位，
     如 `TAG0001`）；项目局部命名空间内按项目代号 + 动态编号递增，不复用已取消任务的
     编号"

5. **`agate/state-machine.md` / `dispatch-protocol.md` / `role-system.md`**（仅改举例
   文本中的 task_id 示例值，不改其他内容）
   - `state-machine.md`：任务看板示例行、"创建第一个任务"举例、两处 `.state.yaml`/
     frontmatter YAML 样例（`task_id`/`trace_id`）、恢复流程举例，共 5 处 `T001` →
     `TAG0001`
   - `dispatch-protocol.md`：`task_id: {完整 task_id，如 T002-fix-db-migration}` →
     `TAG0002-fix-db-migration`；"完整派发示例（T001 P2 阶段）"整段举例（含小节标题）
     6 处 `T001` → `TAG0001`；"任务完成小结"下方的 `[T001] DONE` 输出格式示例 → `[TAG0001] DONE`
   - `role-system.md`：评审派发举例的 `docs/tasks/T002/P2-design.md`、
     `docs/tasks/T002/P2-review.md` → `TAG0002`
   - 未改动的 `T005`/`T006`/`T016`/`T019`/`T020`/`T027`/`T048`/`T075`/`T080`/`T090`/
     `T004`（含"T001 教训：主 Agent 完成任务后未向 PM 汇报"一处）等——这些是三份文档
     里大量存在的"历史教训引用"（引用项目实际发生过的具体历史任务编号作为经验来源），
     不是"task_id 字段格式举例"，按约束"只改举例文本，不改其他内容"未触碰

### DESIGN_GAP 声明

[DESIGN_GAP: check-changelog.sh 移除了 P2-design.md §3.4.2 明确要求"保留"的 `grep -qF "$TASK_ID"` fallback 分支。P2 原文写"fallback `grep -qF "$TASK_ID"` 保留"，但 `TASK_ID_SHORT` 去短前缀提取后已恒等于 `TASK_ID`，保留该 fallback 会用无边界保护的固定字符串子串匹配对同一字符串再匹配一次，导致 `TAG0001` 被 `TAG00012` 误判为已匹配（CL.7 用例实测复现：`[ "$status" -eq 1 ]` 断言失败，因为 fallback 让 exit 0）。判断依据：P3-test-cases.md §5 明确把 CL.7 列为 BDD-27 的验收断言，测试断言与 P2 设计字面表述矛盾时按 implementer 决策树"不改测试、标记偏离"处理；由于同一字符串对自身做无边界子串匹配在语义上不可能提供比上面带边界的正则更严格的匹配（只会更宽松、只会引入误判），判断"移除 fallback"是唯一能同时满足 BDD-27 三个用例（CL.6/CL.7/CL.8）的实现方式，未发现移除后有回归（CL.1-CL.5 及全部既有 check-changelog 相关用例仍绿）。]

[DESIGN_GAP: 硬切 `agate-state-yaml-check.py` 的 task_id 正则后，除 P3-test-cases.md §5 声明的 4 个预期红灯（SY.1/CL.6/CL.7/CL.8）外，额外触发了 33 个此前未被列入流 D 红灯清单、此前一直是绿灯的既有测试失败：单元测试 `agate/tests/unit/check-state-yaml.bats` 的 `SY.8`（1 个，`task_id: T001` 视为"全合规"场景现被新正则拒绝）；集成测试 `agate/tests/integration/pre-commit-hook.bats`（26 个，如 IT.2/IT.3/IT.5/IT.6/IT.8/IT.9/IT.10/IT.11/IT_PT_BINARY.1/2/4/5/6/7/IT_PHASE_SPAN.5/IT_PT_MENTION.1/IT_P6_CODE.2/5/IT_RETREAT.1/2/IT_PT_T6.2/3/IT_CHANGELOG_P54b/IT_GATE_REAL.1/HOOK_EVIDENCE_WARNING 等）与 `agate/tests/integration/dispatch-context-card.bats`（6 个，DC.2-DC.7）。根因相同：这些测试在真实 git 仓库里跑真实 pre-commit hook，fixture 里的 `.state.yaml` 用旧格式 task_id（`T001`/`T999` 等），hook 内部调用 `check-state-yaml.sh`→`agate-state-yaml-check.py` 校验，新正则把这些 fixture 判为格式错误直接拦截 commit（`git commit` 本身失败），导致测试要验证的真正行为（PROD_TOUCHED 扫描、phase span 校验、dispatch-context hash 等）根本没机会被断言到。已用 `git stash` 验证：stash 掉本流全部改动后重跑同一批文件，0 个 not ok（这些测试在流 C 交付时是全绿的，回归确系本流引入，非环境问题）。P2-design.md §3.4 及 P3-test-cases.md §5/§6 的"流 D 红灯只依赖两处局部改动，与流 A/B/C 完全独立"表述，只核对了 `agate-state-yaml-check.bats`/`check-changelog.bats` 两个专项文件，未核对代码库里其他"经由真实 pre-commit hook 间接调用 `agate-state-yaml-check.py`"的集成测试 fixture 是否也用了旧格式 task_id——这是 P1/P2/P3 三阶段均未覆盖到的连带影响面，不是本流"允许改动的文件"清单能修复的（`agate/tests/**` 明确禁止我改，这些 fixture 的 task_id 需要 P3 test-designer 或经批准后由 implementer 批量迁移为新格式）。未做任何自行降级处理（未放宽正则、未加兼容分支），原样保留硬切实现，仅如实呈报，交由主 Agent/P7 裁决：是否需要追加一轮定向派发把这 33 个 fixture 的 task_id 迁移为 `TAG` 格式。]

### 未改动文件（确认，非遗漏）

按约束仅改动上述文件；`agate/scripts/agate-md-field-get.py`、`agate/scripts/agate-frontmatter-check.py`、
`check-frontmatter.sh`、`check-gate.sh`、`check-p6-*.sh`、`check-scope-resolved.sh`（流
A/B/C 已完成，与流 D 无关）、`agate/tests/**`（含上方 DESIGN_GAP 提到的失败用例，均未
改动测试文件本身）均未触碰，符合派发指引范围锁定。

### 594 配平说明

本流不涉及新增测试文件，`agate/tests/**` 未改动，594 配平口径无变化（`count-tests.sh`
自查结果仍为 594，见下）。

### 自查结果（非 P5 gate，仅确认未做错）

指定自查命令（派发指引第 6 条）：
```
bats agate/tests/unit/agate-state-yaml-check.bats agate/tests/unit/check-changelog.bats
```
11/11 通过。目标红转绿：`SY.1`（BDD-25/26 双向：TAG0001 通过 + T001 硬切拒绝）、
`CL.6`/`CL.7`/`CL.8`（BDD-27，含误匹配边界用例）全部转绿。

补充自查（超出指定命令范围，用于确认无越界回归）：
- `bats agate/tests/unit/ agate/tests/regression/`：516 个用例，**515 通过 / 1 失败**——
  `SY.8`（`agate/tests/unit/check-state-yaml.bats`），失败原因见上方 DESIGN_GAP。这是
  本流唯一一处**未能清零的红灯**，不满足派发指引第 6 条"完成后本地全量测试应该
  594/594（516/516 该子集）全绿"的目标。
- `bash agate/tests/scripts/count-tests.sh`：594（不漂移，BDD-11 保持达标）。
- `python3 agate/scripts/check-protocol-consistency.py`：全部 CHECK 1-9 PASS（含 CHECK 9
  锚点表对齐，`agate-state-yaml-check.py` 的 `task_id` 锚点、`check-changelog.sh` 的
  `CHANGELOG` 锚点关键词均未因本流改动消失）。
- `shellcheck -S warning agate/scripts/check-changelog.sh`：0 警告。
- `bats agate/tests/integration/ agate/tests/sanity.bats`：**52 通过 / 32 失败**（详见上方
  DESIGN_GAP 第二条）——`consistency.bats`/`commit-msg-self-gate.bats`/`pre-push-hook.bats`/
  `protocol-alignment-review.bats`/`sanity.bats` 5 个文件全绿；`pre-commit-hook.bats`
  （26 失败）与 `dispatch-context-card.bats`（6 失败）不绿，根因同上。这是派发指引
  第 6 条自查命令范围之外的补充验证，超出范围但按"发现即报"原则一并呈报，不隐瞒。

本流是唯一交付了**未清零红灯**的流：`SY.1`/`CL.6`/`CL.7`/`CL.8` 四个目标红灯已全部转绿，
但连带触发了 33 个此前未被识别的既有用例失败（1 单元 + 32 集成）。以上均为自查，不代表
P5 gate 已过，也不代表流 D "完成后全绿"的目标已达成——已如实呈报未达成的部分，交主
Agent/P7 裁决后续处理方式。

## Review 修复

针对 `P4-review.md`（status: rejected）Pass 1 的 1 个 CRITICAL + Pass 2 前两条低风险
INFO 的定向修复（P4 review 修复轮，第 2 次派发——第 1 次因主 Agent 账号 API 花费上限
失败未做任何改动，本次是干净重试）。范围锁定 4 个文件：
`agate/scripts/agate-frontmatter-check.py`、`agate/scripts/check-frontmatter.sh`、
`agate/scripts/agate-md-field-get.py`、`agate/scripts/check-gate.sh`。未碰
`agate/tests/**`（含用于验证的 3 个 bats 文件，均未修改，仅用来跑）。

### CRITICAL（P4-review.md Pass 1）：agate-frontmatter-check.py 异常处理不完整

**问题**：`main()` 只捕获 `yaml.YAMLError`，深嵌套 `risk_level` 触发 `RecursionError`
（`RuntimeError` 子类，非 `yaml.YAMLError` 子类）时未被捕获，Python 进程崩溃、traceback
打到 stderr；调用方 `check-frontmatter.sh` 用 `python3 ... 2>/dev/null || true` 把
stderr 和非零 exit code 一并吞掉，`ERRORS` 变量因崩溃发生在任何 `print()` 之前而为空
字符串 → gate 误判"无错误" → exit 0 放行本应拦截的坏格式 frontmatter。

**Fix A**（`agate-frontmatter-check.py`）：把 `main()` 里 `open()` 调用及其后全部逻辑
（含 `yaml.safe_load()`、`_check()` 及其内部 `_value_depth()` 的无保护递归）包进一层
`try: ... except Exception as e: print(...)`。`RecursionError`/`UnicodeDecodeError` 均是
`Exception` 子类，单层兜底即可覆盖三处约束点（safe_load 递归、`_check`/`_value_depth`
递归、非 UTF-8 文件读取），内层原有的 `except yaml.YAMLError` 分支保留（更具体的错误
信息优先）。错误输出格式沿用现有 `print(str(e))` 风格，加文件名前缀：
`"{}: frontmatter 处理异常（{}）".format(basename, e)`。

**Fix B**（`check-frontmatter.sh`，纵深防御，review 建议"A+B 都做"，已按建议同时实施）：
不再用 `python3 ... 2>/dev/null || true` 把 stderr 和非零 exit code 一起吞掉。改为
`set +e` 捕获调用的 exit code（stdout 进 `ERRORS`，stderr 重定向到临时文件），区分两种
情况：exit 0 且 stdout 为空 → 真的没错误，继续走原有 `ERRORS` 非空判断；exit 非 0 →
校验器自己崩了，fail-closed，打印 stderr 内容后 `exit 1`，不再静默放行。

**验证**：复现 P4-review.md 第 46-63 行给出的深嵌套场景（`risk_level` 用
`"[" * 2000 + "1" + "]" * 2000` 构造），修复前 `bash check-frontmatter.sh` 返回 exit 0
（放行），修复后返回 **exit 1**，错误输出为
`P1-requirements.md: frontmatter 处理异常（maximum recursion depth exceeded while
calling a Python object）`。额外验证了 Fix A 对 `UnicodeDecodeError`（非 UTF-8 文件内容）
同样生效，以及 Fix B 的 fail-closed 分支（模拟 python 脚本以 exit 1 崩溃时，shell 层正确
打印 stderr 并 `exit 1`，不再吞掉）。

### INFO：agate-md-field-get.py `_format_value` bool 分支死代码清理

`if isinstance(value, bool) else` 两个分支返回值完全相同，简化为
`return str(value).lower()`。纯重构，不改变行为。`bats agate/tests/unit/
agate-md-field-get.bats` 6/6 全绿（MDF.1-6，无回归）。

### INFO：check-gate.sh NEED_CONFIRM/SUGGEST 已解决匹配收紧为整行精确匹配

`grep -qF`（子串匹配）→ `grep -qFx`（整行精确匹配），`check-gate.sh` 两处（约 L86
NEED_CONFIRM 分支、L106 SUGGEST 分支）均已改。已排查 `check-gate.bats` /
`check-retrospective.bats` / `check-gate-p1-review.bats` 三份验证用测试文件，唯一使用
`need_confirm_resolved` 字段的 fixture（`check-retrospective.bats` 的
`RT_BDD21.1`）用的是精确匹配场景（`need_confirm_resolved: ["z 的边界条件需确认"]`
对应正文 `[NEED_CONFIRM] z 的边界条件需确认`，二者字面完全相等），不存在依赖子串匹配
语义的 fixture，无冲突，按 INFO 建议直接应用整行精确匹配，未触发 DESIGN_GAP。
`bats agate/tests/unit/check-gate.bats agate/tests/unit/check-retrospective.bats
agate/tests/unit/check-gate-p1-review.bats` 三文件合计全绿，无回归。

### 未处理范围（按派发指引明确排除，不在本次范围）

- `check-changelog.sh` 分隔符集合扩展——review 明确标注"不属于本次 CRITICAL，可与其他
  INFO 一起排期"，未碰该文件。
- 流 D 硬切上线迁移计划——review 明确标注"不是本角色评审范围"，是给主 Agent 在
  P7/P8 阶段的提醒，非代码修复项，未处理。

### 自查结果（非 P5 gate，仅确认未做错）

验收标准命令（派发指引第 5 条）：
```
bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ agate/tests/sanity.bats
```
结果：**600/600 全绿**，无新增失败、无回归。`bash agate/tests/scripts/count-tests.sh`
仍为 594（不漂移）。CRITICAL 复现步骤（约束 1 末尾）手动验证：exit 0 → **exit 1**，
符合预期。以上为自查，不代表最终 gate 已过，也不代表"review 已过"——重新评审由主
Agent 另行派发。

## Self-gate 文档修复

依据 `docs/reviews/agate-alignment-review-2026-08-10.md`"待闭环事项清单"表，定向修复 4 个
MISALIGNED 文档滞后项（均为纯文档编辑，不涉及脚本逻辑改动）：

1. **`agate/scripts/README.md:68`**（对应 A2）：`agate-md-field-get.py` 工具清单行原文只写
   "P1/P2 提取 risk_level/ui_affected/phases"，未反映流 A/B/C 新增的 17 个 op 及双读语义。
   已改为概述"frontmatter 优先 + 正则回退的双读字段提取，覆盖 P1/P2/P6/P7 共 20 个 op"，
   列出原有 3 个 + 新增的 candidate_count/packages/domains/override/internal_only/
   internal_only_reason/design_trivial/follows_existing_pattern/pass/fail/blocker_count/
   deviation_count/deviation_critical_count/design_gap_count/design_gap_reviewed_count/
   need_confirm_resolved/suggest_resolved/scope_resolved，并注明"详见脚本内 docstring"，
   依赖列由"无"改为"pyyaml"（与脚本实际 import 一致）。

2. **`agate/WORKFLOW.md:78-79`**（对应 A3b 第 1 项）：任务目录命名约定的两个示例
   `docs/tasks/T001-mcp-namespace-map/` / `docs/tasks/T002-fix-db-migration/` 用的是流 D
   硬切前的旧格式（`T\d{3}`，无 2 字母项目代号），在 `agate-state-yaml-check.py:39`
   的新正则 `^T[A-Z]{2}\d+$` 下会被拒绝。已改为 `docs/tasks/TAG0001-mcp-namespace-map/` /
   `docs/tasks/TAG0002-fix-db-migration/`，与 `state-machine.md`/`dispatch-protocol.md`/
   `role-system.md`/`active-tasks-template.md` 已同步的新格式示例保持一致。

3. **`agate/dispatch-protocol.md:537-553`**（对应 A3b 第 2 项）："P5/P6 派发时追加"模板块
   全文件此前零处提及 "frontmatter"，遗漏了 BDD-16 要求的 `pass:`/`fail:`/`ui_affected:`
   frontmatter 汇总字段要求。已在"P6 BDD 结果格式"小节（行首 `- PASS`/`- FAIL` 那段）
   后追加一句：P6-acceptance.md 除正文逐条结果外，还必须在文件头 frontmatter 声明
   `pass:`/`fail:`/`ui_affected:` 三个机器汇总字段（int/int/bool），gate 优先读取该汇总、
   正文格式仅作旧格式回退，并指向 `agate/assets/execution-roles/verifier.md` 的可复制样例。

4. **`agate/tests/README.md:28-64`**（对应 A5 新增细节 1）：覆盖度表缺少新增校验器
   `check-frontmatter.sh` 一行（对应 `unit/check-frontmatter.bats`，11 个 `@test`）。
   已在 `check-scope-resolved.sh` 行后补一行：
   `| check-frontmatter.sh | unit/check-frontmatter.bats | 11 |`。

**范围确认**：本次未改动 `agate/CONTEXT.md`、`agate/LIMITATIONS.md`（self-gate 报告明确
标注"建议非阻断"，不在派发范围）；未改动任何 `agate/scripts/*.sh`/`*.py` 或
`agate/tests/**` 实际测试代码，仅编辑上述 4 个文档文件本身。

**自查**（非最终 gate）：`python3 agate/scripts/check-protocol-consistency.py` 重跑，
CHECK 1-9 全部 PASS，0 ERROR（含 CHECK 1 对新增文本中 YAML 片段的可解析性校验、
CHECK 2 对文件引用存在性的校验）。

## ADR-007 补充

依据 `docs/reviews/agate-alignment-review-2026-08-10.md` A7 节的 self-gate 发现：P2 设计阶段
（`P2-design.md` §1）对比方案 A（frontmatter 强化 + 单工具双读扩展，选定）与方案 B（拆分独立
facts 工具 + 独立 `.yaml` 元数据文件）的完整权衡矩阵与选择理由，未沉淀进 `agate/adr.md`。

在 `agate/adr.md` 末尾（`ADR-006` 之后）新增 **ADR-007："机器字段并入 frontmatter——单工具
双读，不拆分独立事实文件"**，格式仿照现有 6 条（状态/语境/决策/理由/后果），内容从
`P2-design.md` §1 的候选方案对比、权衡矩阵、选择理由提炼而成（非照抄，正文指引读者查阅
`P2-design.md` §1 获取完整矩阵）。未改动 ADR-001 至 ADR-006 任何已有内容，纯追加。

**自查**：`python3 agate/scripts/check-protocol-consistency.py` 重跑，0 ERROR。

## P6 回退修复：check-p6-format.sh frontmatter 破坏 bug

**问题**（详见 `P6-gate-diagnosis.md`）：`check-p6-format.sh` 的 `--fix` 分支此前对整个
文件内容跑 5 条归一化 sed，没有排除 frontmatter 块。BDD-16 要求的 `P6-acceptance.md`
frontmatter 里合法的 `pass: 28` / `fail: 0` 字段，会被这几条 sed 误判为"待归一化的正文
散文 pass/fail 行"，改写成 `**Summary**: PASS: 28` / `**Summary**: FAIL: 0`，导致
frontmatter 从合法 YAML 变成非法 YAML（`yaml.safe_load` 报错）。这是 v0.35 时代就存在、
此前从未被触发的潜伏缺陷——旧版 `P6-acceptance.md` 不会在文件头出现裸 `pass:`/`fail:`
字段，直到本任务流 B 引入 frontmatter 汇总字段才与这段老代码产生冲突，且 P3/P4/P5 的
既有测试用例均未构造过这个组合场景。

**修复方式**：在 `--fix` 分支写入文件前，先按 `agate-frontmatter-check.py` 里
`_extract_frontmatter_block` 的同款边界判定语义，把文件切成 frontmatter 部分（含首尾
`---` 分隔符）+ 正文部分：
- 判定语义对齐：文件须以恰好一行 `---` 开头（`FIRST_LINE == "---"`），再找其后第一条
  以 `---` 起始的行作为闭合边界（`awk 'NR>1 && index($0,"---")==1'`，对应 Python 版
  `text.find("\n---", 4)` 的语义——只要求行以 `---` 为前缀，不要求整行恰好是 `---`）；
  找不到闭合边界 → 视为无 frontmatter 块，全文本按正文处理（BDD-9 旧格式兼容，行为
  与修复前完全一致）。
- 5 条归一化 sed（小写 pass/fail 归一化、缩进修正、总结行改写）改为只作用于切分出的
  正文部分（`BODY_PART`），frontmatter 部分（`FM_PART`）原样保留，不经过任何 sed。
- 写文件前把 `FM_PART` + `\n` + 处理后的 `BODY_PART` 拼回一个完整内容再写入
  （无 frontmatter 场景下 `FM_PART` 为空，等价于原有全文本处理逻辑，未改变行为）。

**未重新发明逻辑**：未在 bash 里独立造一套边界判定规则，而是逐条对照
`agate-frontmatter-check.py::_extract_frontmatter_block` 的判定条件（起始行硬性要求
`"---\n"` 前缀、`find(..., 4)` 的搜索起点）用等价的 `head`/`awk`/`sed` 复刻，避免与该
校验器出现"同一文件两种边界判定"的新不一致。

**新增回归测试**（`agate/tests/unit/check-p6-format.bats`，新增 3 条）：
- `F_P6FMFIX.1`：本次 bug 的直接复现场景——frontmatter 含 `pass: 28`/`fail: 0`，正文含
  一行小写 `- pass BDD-2`。`--fix` 后用 `python3 -c "import yaml; yaml.safe_load(...)"`
  验证 frontmatter 依然是合法 YAML 且数值不变，同时确认正文的 `- pass BDD-2` 仍按既有
  行为被归一化为 `- PASS BDD-2`（新修复没有连带破坏旧功能）。
- `F_P6FMFIX.2`：frontmatter 存在的前提下，正文总结行（`- PASS：2` 全角冒号）仍被正确
  归一化为 `**Summary**: PASS: 2` 格式，且 frontmatter 不受影响。
- `F_P6FMFIX.3`：畸形边界场景——首行是 `---` 但全文找不到第二条以 `---` 起始的行（未
  闭合），验证此时不误判为"已切分出 frontmatter"，而是整份文件按正文处理，既有的
  `--fix` 归一化行为在这种输入下仍对全文生效（覆盖"找不到闭合边界"分支）。

**自查结果**（非最终 gate）：
- 手动复现验证：构造与 `P6-gate-diagnosis.md` 独立复现步骤完全一致的 fixture
  （frontmatter 含 `pass: 28`/`fail: 0` + 正文一行 `- pass BDD-2`），跑
  `bash agate/scripts/check-p6-format.sh --fix` 后，`python3 -c "import yaml;
  yaml.safe_load(...)"` 确认 frontmatter 解析成功、`pass`/`fail` 数值原样保留；正文的
  `- pass BDD-2` 确认被归一化为 `- PASS BDD-2`。
- 自动化测试：`bats agate/tests/unit/check-p6-format.bats` 单文件 13/13 全绿（10 条既有
  + 3 条新增）；`bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
  agate/tests/sanity.bats` 全量 603/603 全绿（600 基线 + 3 条本次新增回归用例，无回归）；
  `shellcheck -S warning agate/scripts/check-p6-format.sh` 无输出（exit 0）。
- 以上为自查，不代表最终 gate 已过，最终验证由主 Agent 独立重跑并亲自复现原始 bug
  场景确认。

**范围确认**：本次仅改动 `agate/scripts/check-p6-format.sh`（`--fix` 分支）与
`agate/tests/unit/check-p6-format.bats`（新增 3 条用例），未触碰 `--check` 分支逻辑
（该分支本身不受此 bug 影响——`--check` 的正则要求行首有 `-`，frontmatter 的
`pass: 28` 无行首 `-` 前缀，从未被误判），未触碰其他任何脚本或协议文档。
