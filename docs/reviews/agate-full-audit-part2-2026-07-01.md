# 协议-脚本对齐全量审查（第二批：gate 脚本）

审查日期：2026-07-01
审查范围：check-gate.sh / check-p6-evidence.sh / check-p6-provenance.sh / check-scope-resolved.sh / check-retrospective.sh / check-changelog.sh / check-state-yaml.sh / check-tdd-red.sh / pre-commit-gate.sh

## 协议文档关键规则索引

### 门槛表（dispatch-protocol.md:568-577）
- P1→P2: P1-requirements.md 存在 + Header + ≥1 条 BDD + NEED_CONFIRM=0 + status:GAP=0 + risk_level 命中
- P2→P3: status: approved + packages/domains/ui_affected/gate_commands 四字段
- P3→P4: check-tdd-red.sh exit 0（UI 额外确认 Playwright 用例存在）
- P4→P5: P4-implementation/ 非空 + git log 含 P4
- P5→P6: gate_commands.P5 exit 0 AND failed==0 + PROD_TOUCHED 无命中 + UI E2E exit 0
- P6→P7: check-gate.sh P6 exit 2 + check-p6-evidence.sh + check-p6-provenance.sh + BDD 总数
- P7→P8: BLOCKER=0 + DEVIATION-CRITICAL=0 + DESIGN_GAP 配对
- P8→READY: check-gate.sh P8 + 发布检查 + bump-version + CHANGELOG + version 文件

### Pre-commit 检查全景（dispatch-protocol.md:588-604）
- P1.1 check-gate.sh: 各阶段门控
- P1.6 check-changelog.sh: [Unreleased] 含 task_id（提醒级）
- P1.7 check-p6-evidence.sh: P6/P7 证据目录非空 + BDD 行数≥1
- P2.1/P2.10 check-p6-provenance.sh: 证据-结论对应 + dispatch-context + BDD 总数
- P2.11 check-scope-resolved.sh: [SCOPE+] 标记追踪
- P2.12 check-retrospective.sh: 异常模式提醒（不拦截）
- P2.15 check-state-yaml.sh: .state.yaml 格式校验


---

## 1. check-gate.sh

### 文件概要
- 路径：agate/scripts/check-gate.sh
- 功能：各阶段门控（P1-P8）
- exit 约定：0=通过, 1=未通过, 2=需主 Agent 自判
- 可脚本化（exit 0/1）：P3/P4/P7
- 需主 Agent 自判（exit 2）：P1/P2/P5/P6/P8
- 关键逻辑：
  - P1: 直接 exit 2（"BDD 编号格式不固定"）
  - P2: 检查候选方案数≥2（v0.6 多方案探索），再 exit 2
  - P3: exec check-tdd-red.sh
  - P4: git diff --cached 检查暂存区有非 md/yaml 文件（N1 修复：不用 git log）
  - P5: 直接 exit 2
  - P6: FAIL=0 + NC=0 + TOTAL>0 + 证据目录非空 → exit 2
  - P7: BLOCKER=0 + DEVIATION-CRITICAL=0 + DESIGN_GAP 配对 + P4/P7 交叉核对 → exit 0
  - P8: bump_type + version 文件 + CHANGELOG → exit 2

### 对比：P1 门槛
- 文档（dispatch-protocol.md:570）：P1-requirements.md 存在 + Header + ≥1 BDD + `grep -cE '\[NEED_CONFIRM\]' → =0` + `grep -cE 'status:.*GAP\b' → =0` + `grep -qE 'risk_level:\s*(low|medium|high)' → 命中`
- 脚本（check-gate.sh:18-20）：直接 exit 2，"BDD 编号格式不固定，需主 Agent 自行判定"，未执行任何 grep 检查
- 结论：MISALIGNED — 文档明确列出了可脚本化的 grep 命令（NEED_CONFIRM=0、status:GAP=0、risk_level 命中），脚本却完全交给主 Agent 自判。BDD 编号格式不固定确实难脚本化，但其余三项 grep 完全可执行。脚本以"BDD 编号不固定"为由放弃所有检查，是过度保守。

### 对比：P2 门槛
- 文档（dispatch-protocol.md:571）：`grep 'status: approved' P2-review.md → 命中` + `grep -cE '^(packages|domains|ui_affected|gate_commands):' P2-design.md → =4`
- 脚本（check-gate.sh:24-34）：检查候选方案数≥2（`^###?\s*候选方案|^###?\s*方案[ABC123]`），未检查 status:approved，未检查四字段计数
- 结论：MISALIGNED — 脚本检查了文档门槛表未明确列出的"候选方案数≥2"（v0.6 多方案探索），却遗漏了文档明确列出的 status:approved 和四字段计数检查。检查项与文档门槛表错位。

### 对比：P3 门槛
- 文档（dispatch-protocol.md:572）：scripts/check-tdd-red.sh exit 0（UI 任务额外确认 Playwright 用例存在）
- 脚本（check-gate.sh:36）：`exec "$SCRIPT_DIR/check-tdd-red.sh"`
- 结论：ALIGNED — 脚本转发到 check-tdd-red.sh，与文档一致。UI 任务 Playwright 检查文档注明"额外确认"，属主 Agent 职责，脚本不含合理。

### 对比：P4 门槛
- 文档（dispatch-protocol.md:573）：P4-implementation/ 下文件非空 + `git log --oneline -1` 含 "P4" 或 "wf(Txxx-P4)"
- 脚本（check-gate.sh:38-40）：`git diff --cached --name-only | grep -qvE '\.(md|yaml)$|^\.state' && exit 0 || exit 1`（N1 修复：pre-commit 时 commit 还没创建，改用 git diff --cached）
- 结论：MISALIGNED — 脚本用 git diff --cached 替代 git log 是 pre-commit 场景的合理修复（AGENTS.md 明确要求"所有 git diff 用 --cached"），但存在两处偏差：① 文档门槛表仍写 git log，未同步更新；② 脚本未检查"P4-implementation/ 下文件非空"，只检查暂存区有非 md/yaml 文件，无法区分 P4 产出文件在哪个目录。

### 对比：P5 门槛
- 文档（dispatch-protocol.md:574）：gate_commands.P5 exit 0 AND failed==0 + `grep -rl '\[PROD_TOUCHED\]' {task}/` 无命中 + UI E2E
- 脚本（check-gate.sh:41-43）：直接 exit 2，未执行任何检查
- 结论：NEEDS_HUMAN_REVIEW — gate_commands 动态读取无法脚本化是合理的（exit 2 符合预期），但 PROD_TOUCHED 的 grep 检查可脚本化却未做。文档门槛表明确写了 `grep -rl '\[PROD_TOUCHED\]'`，脚本应至少执行这一项。

### 对比：P6 门槛
- 文档（dispatch-protocol.md:575）：check-gate.sh P6 → exit 2（FAIL=0/NC=0/证据非空已验）
- 脚本（check-gate.sh:44-64）：检查 FAIL=0（`^\s*- FAIL\b`）+ NC=0（`\[NEED_CONFIRM\]`）+ TOTAL>0（`^\s*- (PASS|FAIL)`）+ 证据目录非空 → exit 2
- 结论：ALIGNED — 脚本逻辑与文档描述完全一致，exit 2 让主 Agent 核实 BDD 总数符合预期。

### 对比：P7 门槛
- 文档（dispatch-protocol.md:576）：`grep -cE '^\s*-?\s*\[BLOCKER\]' → =0` + `grep -cE '^\s*-?\s*\[DEVIATION-CRITICAL\]' → =0` + DESIGN_GAP 配对
- 脚本（check-gate.sh:65-96）：BLOCKER 检查 + DEVIATION-CRITICAL 检查 + DESIGN_GAP/DESIGN_GAP_REVIEWED 配对 + P4/P7 DESIGN_GAP 交叉核对 → exit 0
- 结论：ALIGNED — 脚本完整实现文档要求，且额外做了 P4/P7 交叉核对（R2.3 修复），是合理的增强。

### 对比：P8 门槛
- 文档（dispatch-protocol.md:577）：check-gate.sh P8 → exit 2 + bump_type + version 文件 + CHANGELOG 非空
- 脚本（check-gate.sh:97-125）：检查 bump_type 字段 + version 文件变更（通用匹配）+ CHANGELOG 变更（支持 CHANGELOG_FILE 环境变量）→ exit 2
- 结论：ALIGNED — 脚本逻辑与文档一致，exit 2 让主 Agent 做发布检查命令和 P5 重跑符合预期。CHANGELOG_FILE 环境变量支持是文档明确要求的。

### check-gate.sh 总结
- ALIGNED: P3/P6/P7/P8
- MISALIGNED: P1（未做可脚本化的 grep）/ P2（检查项错位）/ P4（文档未同步 git diff --cached 修复）
- NEEDS_HUMAN_REVIEW: P5（PROD_TOUCHED 检查可脚本化未做）

---

## 2. check-p6-evidence.sh

### 文件概要
- 路径：agate/scripts/check-p6-evidence.sh
- 功能：P6 证据格式检查（P1.7）
- exit 约定：0=通过, 1=证据缺失, 2=无 P6 文件
- 关键逻辑：
  - P6-acceptance.md 不存在 → exit 2
  - BDD_COUNT=0（`^\s*- (PASS|FAIL)`）→ exit 1
  - 每条 PASS 行必须含文件引用（括号内路径，支持 png/jpg/log/json/html/txt/yaml/yml）→ 缺引用 exit 1
  - P6-evidence/ 目录非空检查 → exit 1
  - UI 截图实质检查（R1a）：从 P2-design.md 读 ui_affected，若 true 且 PASS 引用 screenshots/，检查目录非空 + 每个文件 >1KB

### 对比：P1.7 证据目录非空 + BDD 行数≥1
- 文档（dispatch-protocol.md:597）：P6/P7 阶段：证据目录非空 + BDD 行数 ≥ 1
- 脚本（check-p6-evidence.sh:15-45）：BDD_COUNT 检查 + P6-evidence/ 目录非空检查
- 结论：ALIGNED — 脚本完整实现文档要求。

### 对比：R1a UI 截图 >1KB
- 文档（dispatch-protocol.md:575）：check-p6-evidence.sh UI 截图 > 1KB（R1a 客观证据 barrier）
- 脚本（check-p6-evidence.sh:63-85）：从 P2-design.md 读 ui_affected，若 true 且 PASS 引用 screenshots/，检查每个截图文件 >1KB
- 结论：ALIGNED — 脚本实现文档要求，且仅在 PASS 引用截图时才检查（兼容查询类 BDD 可不截图规则），设计合理。

### 对比：操作类 BDD 截图 md5 去重
- 文档（dispatch-protocol.md:354）：操作类 BDD 截图必须互不相同（md5 去重），查询类 BDD 可不截图但须有断言记录文件
- 脚本（check-p6-evidence.sh:全文件）：未实现 md5 去重检查
- 结论：MISALIGNED — 文档明确要求"操作类 BDD 截图必须互不相同（md5 去重）"，脚本未实现此检查。脚本检查了文件大小 >1KB（防空 png 充数），但未检查截图内容是否重复。

### 对比：查询类 BDD 断言记录文件
- 文档（dispatch-protocol.md:354）：查询类 BDD 可不截图但须有断言记录文件（response.json / assert.log 等，hook 强制）
- 脚本（check-p6-evidence.sh:30-40）：每条 PASS 行必须含文件引用（括号内路径，支持 log/json/txt/yaml 等非截图格式）
- 结论：ALIGNED — 脚本通过"每条 PASS 必须含文件引用"覆盖了"须有断言记录文件"的要求，且文件类型不限于截图（支持 log/json/txt），兼容查询类 BDD。

### check-p6-evidence.sh 总结
- ALIGNED: 证据目录非空/BDD行数、R1a 截图大小、查询类断言记录
- MISALIGNED: md5 去重未实现

---

## 3. check-p6-provenance.sh

### 文件概要
- 路径：agate/scripts/check-p6-provenance.sh
- 功能：P6 验收客观行为审计（P2.1/P2.10）
- exit 约定：0=通过, 1=审计不通过（拦截）, 2=WARNING（不阻塞）
- 四道审计 + 协作规范：
  - 审计1：证据-结论对应（1a 路径存在 + 1b PASS≤证据数 + 1c 证据被引用）
  - 审计2：dispatch-context 不含验收结论预判
  - 审计3：BDD 总数对照（P6 PASS+FAIL ≥ P1 Given 行数）
  - 审计4：UI vision YAML 引用（R1b）+ blocker_count==0
  - 协作规范：agent 字段缺失 → WARNING（exit 2）

### 对比：审计1 证据-结论对应
- 文档（dispatch-protocol.md:575, 597）：证据-结论对应 + 三道客观审计失败 → exit 1 拦截
- 脚本（check-p6-provenance.sh:38-100）：1a PASS 引用路径必须存在 + 1b PASS 数≤证据文件数 + 1c 证据文件必须被 PASS 行引用
- 结论：ALIGNED — 脚本实现三层防护（路径存在/数量对应/无充数文件），比文档描述更细致，是合理的增强。

### 对比：审计2 dispatch-context 审计
- 文档（dispatch-protocol.md:575, 597）：dispatch-context 审计
- 脚本（check-p6-provenance.sh:105-113）：检查 P6-dispatch-context.md 不含 `- PASS`/`- FAIL` 验收结论预判
- 结论：ALIGNED — 脚本检查 dispatch-context 不含验收结论，防止主 Agent 在派发时预设结论。

### 对比：审计3 BDD 总数对照
- 文档（dispatch-protocol.md:363, 575）：P1 有 N 条 BDD → P6 必须有 N 条验收结果（含 SCOPE+ 增补）
- 脚本（check-p6-provenance.sh:118-134）：P6 PASS+FAIL 数 ≥ P1 Given 行数；P1 无 Given 行 → exit 2 让主 Agent 手动核实
- 结论：ALIGNED — 用 ≥ 而非 = 是正确的（允许 SCOPE+ 增补）。P1 BDD 格式非标准时 exit 2 兜底，符合文档"BDD 编号格式不固定"的说明。但用 Given 行计数是启发式，若 BDD 用其他关键词（如 Scenario/用例）会漏检——exit 2 兜底缓解了此风险。

### 对比：审计4 UI vision YAML（R1b）
- 文档（dispatch-protocol.md:575）：UI vision YAML 审计 [R1b hook 化]
- 脚本（check-p6-provenance.sh:141-195）：ui_affected=true 时，含截图的 PASS 行必须含 (vision: ...) 引用 + YAML 文件存在 + summary.blocker_count==0
- 结论：ALIGNED — 脚本完整实现 R1b 要求。但文档 dispatch-protocol.md:597 仍写"三道客观审计"，未更新为四道（R1b 是后加的），文档描述滞后。

### 对比：agent 字段协作规范
- 文档（state-machine.md:216）：agent 字段/BDD 非标 → exit 2 警告
- 脚本（check-p6-provenance.sh:201-240）：P6/P2-review/所有阶段产出文件缺 agent 字段 → exit 2；risk=high + agent=main → exit 2
- 结论：ALIGNED — 脚本实现文档要求，且额外检查 risk=high+agent=main 的自审风险，是合理增强。

### 对比：FAIL 行证据未检查
- 文档（dispatch-protocol.md:366）：每条 BDD 验收结果必须有对应证据文件（未区分 PASS/FAIL）
- 脚本（check-p6-provenance.sh:39, 58, 91）：仅检查 PASS 行的证据引用，未检查 FAIL 行
- 结论：NEEDS_HUMAN_REVIEW — 文档说"每条 BDD 验收结果"应有证据，脚本只查 PASS 行。FAIL 行也应 有证据（错误日志/截图）。但 FAIL 会回 P4 重做，影响较小，且 FAIL 证据可能是错误堆栈而非文件引用，格式难以统一检查。

### check-p6-provenance.sh 总结
- ALIGNED: 审计1/2/3/4 + agent 字段规范
- NEEDS_HUMAN_REVIEW: FAIL 行证据未检查（影响小，FAIL 回 P4）
- 文档滞后：dispatch-protocol.md:597 仍写"三道客观审计"，应为四道（R1b 已 hook 化）

---

## 4. check-scope-resolved.sh

### 文件概要
- 路径：agate/scripts/check-scope-resolved.sh
- 功能：SCOPE+ 处理追踪（P2.11）
- exit 约定：0=通过, 1=SCOPE+ 未处理, 2=无 task 目录
- 关键逻辑：
  - 扫描 task 目录所有 .md 文件找 [SCOPE+]
  - 无 SCOPE+ → exit 0
  - 有 SCOPE+ 但无 P1-requirements.md → exit 1
  - 有 SCOPE+ 但 P1 无 [SCOPE_RESOLVED] → exit 1

### 对比：SCOPE+ 追踪规则
- 文档（dispatch-protocol.md:628-633）：产出含 [SCOPE+] 时，主 Agent 必须在 P1-requirements.md 增补对应条目并标记 [SCOPE_RESOLVED: 来源文件]。未标记 → gate 不通过
- 脚本（check-scope-resolved.sh:14-42）：扫描所有 .md 找 [SCOPE+]，有则检查 P1 是否有 [SCOPE_RESOLVED]
- 结论：ALIGNED — 脚本逻辑与文档一致。

### 对比：[SCOPE_RESOLVED] 格式匹配
- 文档（dispatch-protocol.md:633）：格式 `[SCOPE_RESOLVED: from P4-implementation.md] 新需求已增补为 AC-N，影响范围已评估`
- 脚本（check-scope-resolved.sh:34）：`grep -cE '\[SCOPE_RESOLVED($|[^a-z])'`（匹配 [SCOPE_RESOLVED: 或 [SCOPE_RESOLVED]）
- 结论：ALIGNED — 正则匹配文档定义的格式，兼容冒号和独立出现两种情况。但脚本只检查"有/无"，不检查"来源文件是否对得上"——即不验证 [SCOPE_RESOLVED: from X] 的 X 是否真实存在。这是已知局限（来源追溯需主 Agent 人工核实），可接受。

### 对比：SCOPE+ 扫描范围
- 文档（dispatch-protocol.md:628）：每次 subagent 返回后，主 Agent 扫描产出是否含 [SCOPE+]
- 脚本（check-scope-resolved.sh:15）：`for f in "$TASK_DIR"/*.md`（扫描 task 目录所有 .md 文件）
- 结论：ALIGNED — M2 修复后扫描所有 .md（包括 dispatch-context.md 等非 P 前缀文件），覆盖范围正确。

### check-scope-resolved.sh 总结
- ALIGNED: SCOPE+ 追踪 / [SCOPE_RESOLVED] 格式匹配 / 扫描范围
- 局限（可接受）：不验证来源文件是否存在，靠主 Agent 人工核实

---

## 5. check-retrospective.sh

### 文件概要
- 路径：agate/scripts/check-retrospective.sh
- 功能：复盘异常触发（P2.12）
- exit 约定：0=总是通过（只提醒不拦截）
- 关键逻辑：
  - 检测三类异常模式：
    1. gate 重试超限（.state.yaml 中某阶段 retries ≥3）
    2. SCOPE+ 触发（task 目录 .md 含 [SCOPE+]）
    3. 裁剪 override 触发（P1-requirements.md 含 `^override:`）
  - 检测到异常 → 输出复盘提醒到 stderr，但 exit 0

### 对比：提醒级不拦截
- 文档（dispatch-protocol.md:601, state-machine.md:220）：P2.12 复盘提醒 | gate 任何结果 | 检测异常模式 → 提醒写复盘（exit 0 不拦截）
- 脚本（check-retrospective.sh:4, 57）：注释"exit 0 = 总是通过（只提醒不拦截）"，末尾无条件 `exit 0`
- 结论：ALIGNED — 脚本严格遵守"不拦截"约定，所有异常只输出到 stderr。

### 对比：异常模式检测
- 文档（dispatch-protocol.md:601）：检测异常模式（未列举具体模式）
- 脚本（check-retrospective.sh:14-47）：检测三类：重试超限/SCOPE+/裁剪 override
- 结论：ALIGNED — 文档未明确列举异常模式，脚本选择的三类是合理的（对应协议中的关键异常场景）。

### 对比：重试超限阈值
- 文档（state-machine.md:428-437 重试上限表）：MAX_RETRY 因阶段而异（P1/P2/P4=3, P3/P5/P6/P7/P8=2）
- 脚本（check-retrospective.sh:23）：`len(attempts) >= 3` 统一阈值
- 结论：NEEDS_HUMAN_REVIEW — 脚本用 ≥3 统一阈值，对 MAX=2 的阶段（P3/P5/P6/P7/P8），retries=2 已超限但脚本不提醒；对 MAX=3 的阶段（P1/P2/P4），retries=3 是最后一次允许的重试（==MAX），不算超限但脚本会提醒。作为"提醒"而非"拦截"，阈值偏差可接受，但不精确。

### check-retrospective.sh 总结
- ALIGNED: 提醒级不拦截 / 异常模式检测
- NEEDS_HUMAN_REVIEW: 重试超限阈值不精确（统一 ≥3 vs 阶段差异化的 MAX_RETRY）

---

## 6. check-changelog.sh

### 文件概要
- 路径：agate/scripts/check-changelog.sh
- 功能：CHANGELOG [Unreleased] 含 task_id 检查（P1.6）
- exit 约定：0=通过, 1=未记录, 无 CHANGELOG 文件时 exit 0
- 关键逻辑：
  - CHANGELOG_FILE 不存在 → exit 0（跳过）
  - 用 python3 提取 [Unreleased] 区域内容
  - [Unreleased] 区域为空 → exit 1
  - [Unreleased] 区域不含 task_id → exit 1
  - 含 task_id → exit 0
  - 支持 CHANGELOG_FILE 环境变量覆盖路径

### 对比：[Unreleased] 含 task_id 检查
- 文档（dispatch-protocol.md:602）：提醒级 P1.6 | scripts/check-changelog.sh | [Unreleased] 含 task_id
- 脚本（check-changelog.sh:21-30）：提取 [Unreleased] 区域，检查是否含 task_id
- 结论：ALIGNED — 检查逻辑与文档描述一致。

### 对比：缺 [Unreleased] 的行为
- 文档（state-machine.md:214）：P1.6 CHANGELOG | gate 通过后 | 缺 [Unreleased] → 警告不拦截
- 脚本（check-changelog.sh:21-24）：[Unreleased] 区域为空 → `exit 1`（拦截）
- 结论：MISALIGNED — 文档明确写"缺 [Unreleased] → 警告不拦截"，但脚本用 exit 1 拦截了 commit。文档分类为"提醒级"（与 check-retrospective.sh 同级），但脚本行为是"拦截级"。需确认：是文档描述有误（本应拦截），还是脚本行为有误（本应只警告）。

### 对比：CHANGELOG_FILE 环境变量
- 文档（dispatch-protocol.md:577, state-machine.md:405）：默认 CHANGELOG.md，CHANGELOG_FILE 环境变量可覆盖
- 脚本（check-changelog.sh:8）：`CHANGELOG_FILE="${CHANGELOG_FILE:-CHANGELOG.md}"`
- 结论：ALIGNED — 与 P8 gate 的 CHANGELOG_FILE 约定一致。

### check-changelog.sh 总结
- ALIGNED: [Unreleased] 含 task_id 检查 / CHANGELOG_FILE 环境变量
- MISALIGNED: 缺 [Unreleased] 时文档说"警告不拦截"，脚本 exit 1 拦截

---

## 7. check-state-yaml.sh

### 文件概要
- 路径：agate/scripts/check-state-yaml.sh
- 功能：.state.yaml 格式校验（P2.15）
- exit 约定：0=格式正确, 1=格式错误, 2=无 .state.yaml
- 关键逻辑：
  - 文件不存在 → exit 2
  - YAML 解析 → 必填字段（task_id/phase/status）→ task_id 格式（T+数字）→ phase 合法值（P0-P8/PAUSED/READY/DONE）→ retries 结构（dict + key=P+数字 + value=列表）

### 对比：P2.15 格式校验
- 文档（dispatch-protocol.md:594, state-machine.md:221）：P2.15 check-state-yaml.sh | .state.yaml 暂存变更 | 格式错误 → exit 1 拦截
- 脚本（check-state-yaml.sh:14-72）：YAML 解析 + 必填字段 + task_id 格式 + phase 合法值 + retries 结构
- 结论：ALIGNED — 脚本实现文档要求的格式校验，exit 1 拦截格式错误。

### 对比：必填字段
- 文档（state-machine.md:449-480 模板）：task_id / phase / status / retries / retry_count / review_scores / updated
- 脚本（check-state-yaml.sh:36-38）：只检查 task_id / phase / status
- 结论：ALIGNED — 脚本只检查三个核心必填字段，retry_count 是派生字段（从 retries 计算），review_scores/updated 是可选字段。不检查可选字段是合理的简化。

### 对比：phase 合法值
- 文档（state-machine.md:69）：状态集合 { P0, P1, P2, P3, P4, P5, P6, P7, P8, READY, DONE, PAUSED }
- 脚本（check-state-yaml.sh:18）：`valid_phases = 'P0 P1 P2 P3 P4 P5 P6 P7 P8 PAUSED READY DONE'.split()`
- 结论：ALIGNED — 完全一致。

### 对比：retries 结构
- 文档（state-machine.md:454-461）：retries 是 dict，key 是 Pn，value 是列表，列表元素含 round/failure_mode/prompt_changed/adjustment
- 脚本（check-state-yaml.sh:51-60）：检查 retries 是 dict，key 匹配 `^P\d+$`，value 是列表
- 结论：ALIGNED（核心结构）— 脚本检查了 retries 的结构和类型。未检查列表元素的内部字段（round/failure_mode/prompt_changed/adjustment）和 failure_mode 的合法值（quality/empty_return/timeout），但作为格式校验（非语义校验），只检查结构是合理范围。failure_mode 合法值检查可作为增强项。

### 对比：Python 调用安全
- 文档（AGENTS.md）：Python 调用用 os.environ，不用 open('$VAR')
- 脚本（check-state-yaml.sh:14, 17）：`STATE_FILE="$STATE_FILE" python3 -c "import os; state_file = os.environ['STATE_FILE']"`
- 结论：ALIGNED — 用 os.environ 传参，符合 AGENTS.md 安全约定。

### check-state-yaml.sh 总结
- ALIGNED: P2.15 格式校验 / 必填字段 / phase 合法值 / retries 结构 / Python 安全调用
- 可增强（非 MISALIGNED）：retries 元素内部字段（failure_mode 合法值等）未检查

---

## 8. check-tdd-red.sh

### 文件概要
- 路径：agate/scripts/check-tdd-red.sh
- 功能：TDD 红灯检查（P3 gate）
- exit 约定：0=正确红灯/B类红灯, 1=A类错误, 2=测试全绿(违反TDD), 3=无测试运行器
- 关键逻辑：
  - 测试运行器回退链：$TEST_RUNNER → which pytest → exit 3
  - 运行测试捕获输出 → 提取 failed/error 数
  - exit 0（全绿）→ exit 2（违反 TDD）
  - assertion failure>0 且 error==0 → exit 0（经典红灯）
  - error>0 → 区分 A/B 类：
    - 有 ImportError 且无语法错误
    - 设置 PROJECT_MODULE → 检查 import 是否项目内模块 → 是则 exit 0（B类），否则 exit 1（A类）
    - 未设置 PROJECT_MODULE → 启发式视为 B 类 → exit 0
    - 有语法错误 → exit 1（A类）

### 对比：P3 gate 门槛
- 文档（dispatch-protocol.md:572, state-machine.md:89）：scripts/check-tdd-red.sh exit 0 AND assertion_failures>0 AND collection_errors==0
- 脚本（check-tdd-red.sh:58-67）：exit 0（全绿）→ exit 2；FAILED>0 且 ERRORS==0 → exit 0
- 结论：ALIGNED — 脚本完整实现文档要求的经典红灯判定。

### 对比：三类红灯区分
- 文档（state-machine.md:258-263）：
  - 经典红灯：assertion failure → 通过
  - B 类红灯：import 失败（项目模块未实现）→ 通过
  - A 类错误：测试代码自身语法/import 错误 → 不通过
- 脚本（check-tdd-red.sh:63-106）：经典红灯 exit 0 / B 类（项目模块 import 错误）exit 0 / A 类（语法错误或非项目 import）exit 1
- 结论：ALIGNED — 脚本完整实现文档定义的三类红灯区分逻辑。

### 对比：B 类检测的 PROJECT_MODULE
- 文档（state-machine.md:282-283）：环境变量 PROJECT_MODULE 用于 B 类检测，未设置则退化为启发式
- 脚本（check-tdd-red.sh:78-99）：设置 PROJECT_MODULE → 检查 import 目标是否匹配 `from ${PROJECT_MODULE}|import ${PROJECT_MODULE}|${PROJECT_MODULE}.`；未设置 → 启发式（所有无语法错误的 ImportError 视为 B 类）
- 结论：ALIGNED — 脚本实现文档要求的精确检测和启发式回退。

### 对比：TEST_RUNNER 环境变量
- 文档（state-machine.md:281, check-tdd-red.sh:26-28）：TEST_RUNNER 从 P0-brief.md env_constraints.debug_env 提取
- 脚本（check-tdd-red.sh:41-49）：$TEST_RUNNER → which pytest → exit 3
- 结论：ALIGNED — 回退链与文档一致。

### 对比：输出格式
- 文档（state-machine.md:265, 299）：脚本输出 `assertion_failures=N, collection_errors=M` 格式
- 脚本（check-tdd-red.sh:56）：`echo "assertion_failures=${FAILED:-0}, collection_errors=${ERRORS:-0}"`
- 结论：ALIGNED — 输出格式与文档定义完全一致。

### 对比：通用性说明
- 文档（state-machine.md:277-279）：本脚本是 pytest 参考实现，非 Python 项目应提供自己的 TDD 红灯检查脚本
- 脚本（check-tdd-red.sh:12-31）：注释详细说明 TEST_RUNNER 输出契约和通用性适配方式
- 结论：ALIGNED — 脚本注释与文档的通用性声明一致。

### check-tdd-red.sh 总结
- ALIGNED: P3 gate 门槛 / 三类红灯区分 / PROJECT_MODULE 检测 / TEST_RUNNER 回退 / 输出格式 / 通用性说明
- 无发现偏差

---

## 9. pre-commit-gate.sh

### 文件概要
- 路径：agate/scripts/pre-commit-gate.sh
- 功能：pre-commit hook 入口，编排所有 gate 检查
- exit 约定：0=允许 commit, 1=拦截 commit
- 关键逻辑（执行顺序）：
  0. P2.15 .state.yaml 格式校验（文件级，不依赖 phase 变更）
  1. 检测是否需要触发 gate（phase 变更或阶段产出变更）
  2. 读取当前状态（phase/task_id）
  3. P1.2 PROD_TOUCHED 检测（git diff --cached 扫 [PROD_TOUCHED]）
  4. P2.3-P2.5 状态转移检查
  5. P1.1 运行 check-gate.sh（写 .gate-result.json）
  5.4. P2.1/P2.10 provenance 审计（gate exit 1 时跳过）
  5.5. P2.7-P2.9 裁剪检查（gate exit 1 时跳过）
  5.6. P2.11 SCOPE+ 追踪（gate exit 1 时跳过）
  5.7. P2.12 复盘提醒（不中止，gate 失败时也提醒）
  6. P1.6 CHANGELOG 检查（|| echo 降级为警告）
  7. P1.7 P6 证据检查（仅 P6/P7 阶段）
  8. gate 结果处理：exit 0→通过, exit 1→拦截, exit 2→允许 commit（需主 Agent 自判）

### 对比：执行顺序
- 文档（dispatch-protocol.md:588-604 表格顺序）：P2.15 → P1.1 → P1.7 → P2.1/P2.10 → P2.3-P2.5 → P2.7-P2.9 → P2.11 → P2.12 → P1.6
- 脚本（pre-commit-gate.sh:32-121 实际顺序）：P2.15 → P1.2 PROD_TOUCHED → P2.3-P2.5 → P1.1 → P2.1/P2.10 → P2.7-P2.9 → P2.11 → P2.12 → P1.6 → P1.7
- 结论：NEEDS_HUMAN_REVIEW — 三处顺序差异：① P1.2 PROD_TOUCHED 提前（文档表格未列 P1.2，但协议正文有规则，提前检测合理）；② P2.3-P2.5 状态转移在 P1.1 gate 之前（先检查转移合法性再跑 gate，功能上合理）；③ P1.7 证据检查放最后（文档列第三位）。顺序差异不影响功能正确性，但文档表格与脚本不同步。

### 对比：PROD_TOUCHED 检测（P1.2）
- 文档（dispatch-protocol.md:395-401, state-machine.md:81）：任意阶段出现 [PROD_TOUCHED] → 立即 PAUSED
- 脚本（pre-commit-gate.sh:60-63）：`git diff --cached | grep -q '\[PROD_TOUCHED\]'` → exit 1 拦截 commit
- 结论：ALIGNED — exit 1 拦截 commit 是实现 PAUSED 的合理方式。R2 修复扫描暂存 diff 而非文件全文，避免协议文档本身含 PROD_TOUCHED 字样导致误报。

### 对比：CHANGELOG 检查的警告降级
- 文档（state-machine.md:214）：P1.6 CHANGELOG | 缺 [Unreleased] → 警告不拦截
- 脚本（pre-commit-gate.sh:104-108）：`check-changelog.sh "$TASK_ID" 2>/dev/null || echo "GATE CHANGELOG: 警告..." >&2`
- 结论：ALIGNED — pre-commit-gate.sh 用 `|| echo` 把 check-changelog.sh 的 exit 1 降级为警告（不拦截），最终行为与文档"警告不拦截"一致。这说明 check-changelog.sh 本身的 exit 1 是分层设计——脚本本身严格，调用方（hook）决定是否降级。

### 对比：gate exit 2 处理
- 文档（dispatch-protocol.md:575, 577）：check-gate.sh P6/P8 → exit 2（需主 Agent 自判）
- 脚本（pre-commit-gate.sh:121）：`2) echo "GATE $PHASE: 需主 Agent 手动判断" >&2; exit 0`
- 结论：ALIGNED — gate exit 2 时 hook exit 0（允许 commit），符合"脚本化部分通过，需主 Agent 手动核实"的语义。

### 对比：P1.7 证据检查触发条件
- 文档（dispatch-protocol.md:597）：P1.7 check-p6-evidence.sh: P6/P7 阶段
- 脚本（pre-commit-gate.sh:111）：`if [ "$PHASE" = "P6" ] || [ "$PHASE" = "P7" ]; then`
- 结论：ALIGNED — 触发条件与文档一致。

### 对比：gate 失败时后续检查的跳过逻辑
- 文档（dispatch-protocol.md:588-604）：未明确说明 gate 失败时其他检查是否跳过
- 脚本（pre-commit-gate.sh:81, 90, 95）：provenance/pruning/scope 在 `GATE_EXIT != 1` 时才执行；但 P1.7 evidence（第 111 行）无此条件，gate 失败时仍执行
- 结论：NEEDS_HUMAN_REVIEW — provenance/pruning/scope 在 gate 失败时跳过（`GATE_EXIT != 1`），但 P1.7 evidence 不跳过。这是不一致的——要么 gate 失败时所有后续检查都跳过，要么都执行。不过 P1.7 只在 P6/P7 执行，gate 失败时多给一些诊断信息可接受。

### 对比：gate-result.json 写入
- 文档（dispatch-protocol.md:590）：Phase 1: P1.1 跑 gate 写 .gate-result.json
- 脚本（pre-commit-gate.sh:78）：`write_gate_result "$PHASE" "$TASK_ID" "$GATE_EXIT" "$GATE_OUTPUT"`
- 结论：ALIGNED — 脚本调用 gate-result.sh 的 write_gate_result 函数记录结果。

### pre-commit-gate.sh 总结
- ALIGNED: PROD_TOUCHED 检测 / CHANGELOG 警告降级 / gate exit 2 处理 / P1.7 触发条件 / gate-result.json 写入
- NEEDS_HUMAN_REVIEW: 执行顺序与文档表格不同步（功能合理但文档滞后）/ gate 失败时 P1.7 不跳过（与其他检查不一致）

---

## 全量审查总结

### 按脚本汇总
| 脚本 | ALIGNED | MISALIGNED | NEEDS_HUMAN_REVIEW |
|------|---------|------------|---------------------|
| check-gate.sh | P3/P6/P7/P8 | P1（未做可脚本化 grep）/ P2（检查项错位）/ P4（文档未同步 git diff --cached） | P5（PROD_TOUCHED 可脚本化未做） |
| check-p6-evidence.sh | 证据目录非空/BDD行数/R1a截图/查询类断言 | md5 去重未实现 | — |
| check-p6-provenance.sh | 审计1/2/3/4/agent字段 | — | FAIL 行证据未检查 / 文档"三道审计"应为四道 |
| check-scope-resolved.sh | SCOPE+追踪/格式匹配/扫描范围 | — | — |
| check-retrospective.sh | 提醒级不拦截/异常模式检测 | — | 重试超限阈值不精确 |
| check-changelog.sh | [Unreleased]含task_id/CHANGELOG_FILE | 缺[Unreleased]时 exit 1（但 hook 层降级为警告） | — |
| check-state-yaml.sh | 格式校验/必填字段/phase合法值/retries结构 | — | — |
| check-tdd-red.sh | 全部对比项 | — | — |
| pre-commit-gate.sh | PROD_TOUCHED/CHANGELOG降级/exit2处理/P1.7触发 | — | 执行顺序与文档不同步/gate失败时P1.7不跳过 |

### 关键发现（按严重度排序）

#### MISALIGNED（需修复）
1. **check-gate.sh P1**：文档列出可脚本化的 grep（NEED_CONFIRM=0、status:GAP=0、risk_level），脚本全未执行，直接 exit 2
2. **check-gate.sh P2**：脚本检查"候选方案数≥2"（文档门槛表未列），却遗漏文档明确列出的 status:approved 和四字段计数
3. **check-p6-evidence.sh md5 去重**：文档明确要求"操作类 BDD 截图必须互不相同（md5 去重）"且"hook 强制"，脚本未实现
4. **check-gate.sh P4 文档滞后**：脚本用 git diff --cached（N1 修复，合理），但文档门槛表仍写 git log

#### NEEDS_HUMAN_REVIEW（需确认）
1. **check-gate.sh P5**：PROD_TOUCHED 的 grep 可脚本化，脚本未做
2. **check-p6-provenance.sh FAIL 行证据**：文档说"每条 BDD 验收结果"应有证据，脚本只查 PASS 行
3. **check-retrospective.sh 重试阈值**：统一 ≥3 vs 阶段差异化的 MAX_RETRY
4. **check-changelog.sh 拦截行为**：脚本 exit 1，但 hook 层降级为警告（分层设计，但脚本独立调用时会拦截）
5. **pre-commit-gate.sh 执行顺序**：与文档表格不同步（功能合理）
6. **pre-commit-gate.sh P1.7 跳过逻辑**：gate 失败时 provenance/pruning/scope 跳过，但 P1.7 不跳过

#### 文档滞后（需更新文档）
1. dispatch-protocol.md:597 仍写"三道客观审计"，应为四道（R1b 已 hook 化）
2. dispatch-protocol.md:573 P4 门槛仍写 git log，应更新为 git diff --cached
3. dispatch-protocol.md:588-604 pre-commit 检查全景表未列 P1.2 PROD_TOUCHED 检测
