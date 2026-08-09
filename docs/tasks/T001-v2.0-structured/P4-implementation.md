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
