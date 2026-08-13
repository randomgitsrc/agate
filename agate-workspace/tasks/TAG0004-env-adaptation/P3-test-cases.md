---
phase: P3
task_id: TAG0004-env-adaptation
type: test-cases
parent: P2-design.md
trace_id: TAG0004-P3-20260813
status: draft
created: 2026-08-13
agent: test-designer
---

test_code_dir: agate/tests/

# P3 测试用例清单 — TAG0004 脚本健壮性 + 环境适配

> 37 条 BDD 全部有对应测试用例（1:1），测试名引用 BDD 编号。测试代码融入既有 bats 套件
> （`agate/tests/unit/` + `agate/tests/integration/`，2 个新文件）。自跑结果：37 条中
> **21 条红灯**（失败原因均为"被测模块未实现"，非断言与数据矛盾）、16 条回归守卫当前绿
> （Linux UTF-8 / GNU sed 下实现已满足，防修复引入回归，Windows 特有行为靠 CI 兜底）。
>
> 红灯/绿灯判定原则（P1 §8 注）：
> - Linux 默认 locale（C.UTF-8）+ GNU sed 下，S3 中文读写、M5 全角冒号、S2 负面用例等
>   在修复前已能通过 → 作为回归守卫（绿），Windows/BSD 平台缺陷靠 CI 双平台兜底验证。
> - 红灯集中在：S1 空格切词 fail-open、M9 正则元字符绕过、Q1 反斜杠前缀剥离、M4 POSIX
>   locale 全角冒号、M6 CRLF frontmatter、RM-AG0001 反引号、RM-AG0002 无 formatter A 类、
>   TPV0090-M4 NameError B 类、S3 grep 断言审计、Q2/Q5/CI 文档断言——实现未写必然失败。

## 测试文件布局

| 文件 | 覆盖 BDD |
|------|---------|
| `agate/tests/integration/pre-commit-hook.bats` | BDD-1/2/3/4（S1）、BDD-17（M9）、BDD-19（复制模式） |
| `agate/tests/unit/check-gate.bats` | BDD-11（M4）、BDD-14（M6）、BDD-28/29（RM-AG0001） |
| `agate/tests/unit/check-p6-format.bats` | BDD-12/13（M5） |
| `agate/tests/unit/check-p6-evidence.bats` | BDD-9/10（S2） |
| `agate/tests/unit/check-tdd-red.bats` | BDD-30/31（RM-AG0002）、BDD-35/36/37（TPV0090-M4） |
| `agate/tests/unit/check-tdd-red-formatter.bats` | BDD-35f（TPV0090-M4 formatter name_errors 字段） |
| `agate/tests/unit/agate-md-field-get.bats` | BDD-6（S3 中文读）、BDD-15（M6 LF 回归） |
| `agate/tests/unit/agate-retreat-state.bats` | BDD-7（S3 中文写） |
| `agate/tests/unit/agate-next-card.bats` | BDD-21/22（Q1） |
| `agate/tests/unit/agate-workspace-resolve.bats` | BDD-18（其他-a CR） |
| `agate/tests/unit/agate-render-dispatch-prompt.bats` | BDD-20（其他-c sed 转义） |
| `agate/tests/unit/agate-scripts-encoding.bats`（新） | BDD-5（S3 断言审计）、BDD-8（S3 ASCII 回归） |
| `agate/tests/unit/env-adapt-docs.bats`（新） | BDD-16（M6 .gitattributes）、BDD-23/24/25（Q2）、BDD-26/27（Q5）、BDD-32/33/34（全局） |

## BDD → 测试用例映射（37/37）

### S1 — pre-commit-gate.sh 空格路径 fail-open（候选 1A 数组化）

- **BDD-1** → `pre-commit-hook.bats` `@test "bdd-1 ... 空格路径任务 gate 实际不通过时拦截"`
  - Given 空格路径任务目录 + P1 gate 实际不通过（无 P1-review.md）→ 触发 pre-commit-gate.sh
  - 期望 exit 1（拦截）。**当前红**：空格切词 → `.state.yaml` 被跳过 → fail-open exit 0。
- **BDD-2** → `pre-commit-hook.bats` `@test "bdd-2 ... 多个 .state.yaml 含空格路径逐个处理"`
  - Given 正常任务（合法 state）+ 空格任务（非法 task_id）同 commit 暂存
  - 期望 exit 1（空格任务格式校验拦截）。**当前红**：空格任务被切词跳过，格式校验未执行。
- **BDD-3** → `pre-commit-hook.bats` `@test "bdd-3 ... 空格目录 PROCESSED_DIRS 不拆段 gate 正常执行"`
  - Given 空格目录 + 合法 P1 全流程（含 dispatch-context）
  - 期望 exit 0 且输出含 `GATE P1`（gate 确实执行）。**当前红**：主循环跳过该任务，无 GATE P1。
- **BDD-4** → `pre-commit-hook.bats` `@test "bdd-4 ... 无空格路径单任务 gate 行为不变"`（回归守卫）
  - Given 常规无空格路径 → 期望 exit 0 + `GATE P1`。当前绿。

### S3 — 13 个 py 缺 encoding（候选 2A grep 断言审计）

- **BDD-5** → `agate-scripts-encoding.bats` `@test "bdd-5 全部 ... open()/read_text() 带 encoding=utf-8"`
  - 扫描 `agate/scripts/*.py`，文本 open()/read_text() 必须带 `encoding=`（`Image.open` 除外）。
  - **当前红**：13 个 py / 20 处违规（与 P1 §6 清单一致）。
- **BDD-6** → `agate-md-field-get.bats` `@test "bdd-6 ... 读取含中文内容协议文件正确返回字段"`（回归守卫）
  - 中文 frontmatter 文件 → agate-md-field-get.py risk_level 返回 high。当前绿（Linux UTF-8；Windows 靠 CI）。
- **BDD-7** → `agate-retreat-state.bats` `@test "bdd-7 ... write_retreat 写回中文 reason 完整"`（回归守卫）
  - RETREAT_REASON 含中文 → 写回保留（allow_unicode）。当前绿（Linux UTF-8）。
- **BDD-8** → `agate-scripts-encoding.bats` `@test "bdd-8 ... 纯 ASCII .state.yaml 读取行为不变"`（回归守卫）
  - agate-state-get.py 读 ASCII .state.yaml → phase 返回正确。当前绿。

### S2 — check-p6-evidence.sh 中文证据文件名（候选 3A 负类加宽）

- **BDD-9** → `check-p6-evidence.bats` `@test "bdd-9 ... 中文文件名证据引用识别为合法"`
  - `- PASS BDD-1 (截图 验证通过.png)` + 同名证据文件 → 期望 exit 0。
  - **当前红**：ASCII-only 字符类不匹配中文 → 误判缺引用 exit 1。
- **BDD-10** → `check-p6-evidence.bats` `@test "bdd-10 ... (见截图) 无扩展名引用仍拦截"`（回归守卫）
  - `(见截图)` 无文件名+扩展名 → 期望 exit 1（字符类加宽不放宽结构）。当前绿。

### M4/M5 — 全角冒号 POSIX locale（候选 4A alternation）

- **BDD-11** → `check-gate.bats` `@test "bdd-11 ... P7 LC_ALL=C 全角冒号 [BLOCKER]：3 条 总结行不误计"`
  - P7 含 `[BLOCKER]：3 条`（非真实 BLOCKER）→ `LC_ALL=C` 下 check-gate.sh P7 → 期望 exit 0。
  - **当前红**：`[:：]` bracket 在 POSIX locale 不匹配全角 → BLOCKER=1 → exit 1。
- **BDD-12** → `check-p6-format.bats` `@test "bdd-12 ... --fix LC_ALL=C 小写 fail 全角冒号总结行归一化"`（回归守卫）
  - `- fail：3` → `--fix` → `**Summary**: FAIL: 3`（line 69 路径）。当前绿（GNU sed 碰巧正确；BSD 靠 CI）。
- **BDD-13** → `check-p6-format.bats` `@test "bdd-13 ... --fix+--check LC_ALL=C 半角冒号总结行行为不变"`（回归守卫）
  - `- FAIL: 3` → --fix 归一化 + --check exit 0（与 v0.40.3 一致）。当前绿。

### M6 — md CRLF frontmatter（候选 5A frontmatter 容错）

- **BDD-14** → `check-gate.bats` `@test "bdd-14 ... P1 CRLF 行尾 P1-review.md frontmatter 提取不失效"`
  - CRLF 行尾的 P1-review.md/P1-requirements.md → check-gate.sh P1 → 期望 exit 2。
  - **当前红**：`sed -n '/^---$/...'` 对 `---\r` 不匹配 → status 提取空 → exit 1。
- **BDD-15** → `agate-md-field-get.bats` `@test "bdd-15 ... LF 行尾 ASCII 文件行为不变"`（回归守卫）
  - LF 行尾 → 行为与基线一致。当前绿。
- **BDD-16** → `env-adapt-docs.bats` `@test "bdd-16 .gitattributes 不含强制 *.md eol 规则"`（回归守卫）
  - `.gitattributes` 无 `*.md` 规则 → 历史 CRLF review 文件不被强制改写。当前绿。

### M9 — 路径正则元字符（候选 6A grep -F 前缀）

- **BDD-17** → `pre-commit-hook.bats` `@test "bdd-17 ... 任务目录含 [ 元字符时 PROD_TOUCHED 检测不静默绕过"`
  - 任务目录 `T[1]` + P5 产出含行首 `[PROD_TOUCHED]` → 期望 exit 1。
  - **当前红**：`grep -E "^${TASK_REL}/"` 把 `[1]` 当字符类 → 前缀不匹配 → PROD_TOUCHED 绕过 → exit 0。

### 其他 — .agate.env CR / 复制模式 AGATE_ROOT / sed 转义

- **BDD-18** → `agate-workspace-resolve.bats` `@test "bdd-18 ... .agate.env 尾部 \r 不污染解析"`
  - `AGATE_WORKSPACE=ws-crlf\r\n` → 解析出的 AGATE_WORKSPACE 无 `\r`。
  - **当前红**：`sed 's/^AGATE_WORKSPACE=//'` 未剥离 `\r` → realpath 结果带 `\r`。
- **BDD-19** → `pre-commit-hook.bats` `@test "bdd-19 ... 复制模式 hook 经 .agate-root 标记正确解析 AGATE_ROOT"`
  - 复制安装 hook + `.agate-root` 标记 → `env -u AGATE_ROOT git commit` 合法 P0 → 期望 exit 0。
  - **当前红**：无 env 覆盖时 readlink 解析到 `.git` → gate-result.sh 加载失败 → exit 1。
- **BDD-20** → `agate-render-dispatch-prompt.bats` `@test "bdd-20 ... AGATE_ROOT 含 & 时替换按字面插入"`
  - AGATE_ROOT 含 `&` → 渲染输出无 `{agate_root}` 残留、含字面路径。
  - **当前红**：sed 替换串 `&` 被当"整体匹配引用" → 占位符残留。

### Q1 — 路径归一化（候选 7A）

- **BDD-21** → `agate-next-card.bats` `@test "bdd-21 ... Windows 盘符/反斜杠 AGATE_ROOT 前缀剥离稳定"`
  - `AGATE_ROOT='C:\proj\agate'`（反斜杠盘符风格）→ 输出 `路径：phase-cards/P3-tdd.md`。
  - **当前红**：`${CARD_FILE#$AGATE_ROOT/}` 把 `\p` 当转义 → 剥离失败 → 相对路径含盘符前缀。
- **BDD-22** → `agate-next-card.bats` `@test "bdd-22 ... Linux 常规路径前缀剥离字节不变"`（回归守卫）
  - 常规路径 → `路径：phase-cards/P3-tdd.md` 与修复前一致。当前绿。

### Q2 — 阶段卡片 phase 推进语义对齐（候选 8A，纯文档）

- **BDD-23** → `env-adapt-docs.bats` `@test "bdd-23 7 张阶段卡片与 git-integration.md 规则 2 对齐"`
  - P1/P2/P3/P4/P6/P7/P8 七张卡不得含"更新 .state.yaml phase="旧写法。
  - **当前红**：7 张卡均残留 mode B 旧写法（P1:17 / P2:13 / P3:13 / P4:16 / P6:16 / P7:14 / P8:14）。
- **BDD-24** → `env-adapt-docs.bats` `@test "bdd-24 git-integration.md 规则 2 语义不变"`（回归守卫）
  - git-integration.md 含"不得提前写下一阶段"。当前绿。
- **BDD-25** → `env-adapt-docs.bats` `@test "bdd-25 修复后协议一致性检查 0 ERROR"`（回归守卫）
  - worktree 自己脚本 `python3 agate/scripts/check-protocol-consistency.py` → exit 0。当前绿。

### Q5 — SETUP Windows 章节 + .gitignore 预设（候选 9A）

- **BDD-26** → `env-adapt-docs.bats` `@test "bdd-26 SETUP.md 含 Windows 章节覆盖 PYTHONUTF8"`
  - SETUP.md 含 `PYTHONUTF8`（覆盖项之一，与 PATH/CRLF/AGATE_ROOT 同章节）。
  - **当前红**：SETUP.md 无 PYTHONUTF8/autocrlf/PATH 覆盖。
- **BDD-27** → `env-adapt-docs.bats` `@test "bdd-27 仓库 .gitignore 模板预设 version.txt/dist 白名单"`
  - `.gitignore` 含 `version.txt`/`dist/` 条目。**当前红**：无。

### RM-AG0001 — check-gate.sh P1 反引号盲区（候选 10A）

- **BDD-28** → `check-gate.bats` `@test "bdd-28 ... 反引号包裹 [SUGGEST: ...] 计入 SUGGEST WARNING"`
  - `` `[SUGGEST: 推荐 X]` `` → check-gate.sh P1 → 输出含 SUGGEST WARNING。
  - **当前红**：行首正则不匹配反引号前缀 → 漏计。
- **BDD-29** → `check-gate.bats` `@test "bdd-29 ... 反引号包裹 [NEED_CONFIRM] 判为未解决阻塞项"`
  - `` `[NEED_CONFIRM]` `` → exit 1 且消息含"未解决的 NEED_CONFIRM"。
  - **当前红**：走"不合规格式"路径（消息不含"未解决的"）。

### RM-AG0002 — check-tdd-red.sh 无 formatter 退化（候选 11A）

- **BDD-30** → `check-tdd-red.bats` `@test "bdd-30 ... 无 formatter + exit 1 + 编译/错误关键词 判 A 类"`
  - `TEST_RUNNER` 指向 fake（exit 1 + `Traceback`/`SyntaxError`）→ 期望 exit 1 + A-class。
  - **当前红**：无 formatter 退化 exit-code-only → 误判正确红灯（exit 0）。
- **BDD-31** → `check-tdd-red.bats` `@test "bdd-31 ... 无 formatter 普通断言失败仍判正确红灯"`（回归守卫）
  - exit 1 + 普通失败（无关键词）→ exit 0。当前绿。

### TPV0090-M4 — check-tdd-red.sh NameError B 类（候选 11A）

- **BDD-35** → `check-tdd-red.bats` `@test "bdd-35 ... formatter 项目模块内 NameError 判 B 类红灯"`
  - gate_commands P3_formatter=pytest.sh + project_module=myapp，输出 `NameError: name 'compute' is not defined` → 期望 exit 0 + B-class。
  - **当前红**：errors>0 一律判 A 类 → exit 1。
- **BDD-36** → `check-tdd-red.bats` `@test "bdd-36 ... globals().get() 规避模式断言失败仍判 B 类"`（回归守卫）
  - 断言失败（非 NameError）→ classic red-light exit 0。当前绿。
- **BDD-37** → `check-tdd-red.bats` `@test "bdd-37 ... 非未定义符号的真实测试 bug（TypeError）仍判 A 类"`（回归守卫）
  - TypeError → A 类 exit 1（B 类扩展不扩大到所有 errors）。当前绿。
- **BDD-35f**（formatter 层，P2-review 观察项 4）→ `check-tdd-red-formatter.bats` `@test "bdd-35f FMT.13: pytest.sh 输出含 name_errors 字段"`
  - pytest.sh 对 NameError 输出 JSON 含 `name_errors` 数组。**当前红**：pytest.sh 无该字段。

### 全局回归

- **BDD-32** → `env-adapt-docs.bats` `@test "bdd-32 全量 bats 测试文件可被 bats 解析"`（回归守卫）
  - `bats -c` 逐个解析 unit/regression/integration/sanity 全部 .bats → exit 0。当前绿；
  - "全量绿" 的最终验证由 gate_commands.P5（`bats ... && consistency --strict && shellcheck`）承担。
- **BDD-33** → `env-adapt-docs.bats` `@test "bdd-33 protocol-tests.yml 含 windows-latest matrix"`
  - protocol-tests.yml 含 `windows-latest`。**当前红**：仅 ubuntu-latest。
- **BDD-34** → `env-adapt-docs.bats` `@test "bdd-34 shellcheck -S warning agate/scripts/*.sh 0 error"`（回归守卫）
  - shellcheck 全脚本 0 error。当前绿。

## P2-review 观察项落实

1. **观察项 1（S1 补"中间 commit / dispatch-context-only commit"变体）**：BDD-1 的 Given 为
   "只暂存 .state.yaml（无 P 产出），gate 因缺 P1-review 而失败"——即无 phase 产出 commit 变体
   （pre-commit-gate.sh L228 分支），BDD-2 为多任务混合，覆盖该路径。
2. **观察项 2（关键词清单以风险节精确组合为准）**：BDD-30 用
   `Traceback|SyntaxError|ImportError|ModuleNotFoundError`（fake 输出含 `Traceback`+`SyntaxError`），
   **不用裸 `error:`**（避免误伤断言失败文本）。
3. **观察项 3（`\L` 小写转换跨平台隐患）**：BDD-21 测试按"归一化剥离"预期写，未硬编码 `\L`
   实现细节——P4 用 `tr`/bash 参数替换亦可满足断言（断言只查输出相对路径）。
4. **观察项 4（NameError 解析依赖 formatter 变更）**：BDD-35 + BDD-35f 先写失败测试
   （formatter 需新增 `name_errors` 字段，judge_result 才可据此归 B 类），当前均红。

## 自跑结果（2026-08-13）

- `bats agate/tests/unit/ agate/tests/integration/`：新用例 37 条 → **21 红 / 16 绿**；
  既有用例零回归（unit 602 条、integration 60 条中仅 bdd-* 新增红）。
- `bats agate/tests/regression/`：17 条全绿（无回归）。
- 红灯失败原因逐一核验均为"被测模块未实现"（fail-open 绕过 / 字符类不匹配 / 正则元字符 /
  prefix 剥离失败 / bracket locale / sed & 解释 / formatter 缺字段 / 文档缺项），无"断言与数据矛盾"。

`[PROD_NOT_TOUCHED]` 本阶段仅写测试代码并跑 bats，未接触任何生产环境。
