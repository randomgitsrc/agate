---
phase: P1
task_id: TAG0004-env-adaptation
type: problems
parent: P0-brief.md
trace_id: TAG0004-P1-20260813
status: draft
created: 2026-08-13
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-scripts-sh, agate-scripts-py, agate-phase-cards, agate-docs, agate-gitconfig, agate-ci, agate-tests]
domains: [backend, security, cli]
---

[NO_NEED_CONFIRM]

# P1 需求基线 — agate 脚本健壮性 + 环境适配（Windows 原生兼容 + Linux 基线回归）

## 1. 需求复述

**目标**：修复已核实的环境/健壮性缺陷，让 agate 协议脚本在 **Windows（含中文路径/文件名/内容）** 下正确运行，同时**保证 Linux 现有行为完全不变**（现有 676 bats 测试全绿为回归底线）。缺陷清单由 P0-brief 锁定，全部有代码证据 + 行号（见 §6 审计范围）。

修复对象分五组：
1. **SEVERE**：S1（pre-commit-gate.sh 空格路径 fail-open 静默绕过）、S3（13 个 py `open()` 缺 `encoding="utf-8"`）、S2（check-p6-evidence.sh 证据引用 ASCII 正则）
2. **MODERATE**：M4/M5（全角冒号 `[:：]` POSIX locale 残留）、M6（md CRLF 污染 frontmatter 提取）、M9（路径正则元字符被吞）
3. **TQC0001 复盘归入**：Q1（`${CARD_FILE#$AGATE_ROOT/}` 前缀匹配 Windows 失效）、Q2（7 张阶段卡片 mode B 旧写法与 git-integration.md 规则 2 对齐）、Q5（SETUP.md Windows 章节 + .gitignore 模板预设）
4. **roadmap 并入**：RM-AG0001（check-gate.sh P1 反引号包裹盲区）、RM-AG0002（check-tdd-red.sh 无 formatter A 类误判）
5. **其他**：`.agate.env` 尾部 `\r`、复制模式 hook AGATE_ROOT 解析、agate-render-dispatch-prompt.sh sed 替换串未转义

**核心约束（两条不可违反）**：
- Linux 现状是基线，Windows 兼容是增量。每个修复点必须同时满足「Linux 行为不变」+「Windows 行为正确」。
- 本环境（Linux）无法实测 Windows——Windows 验证靠静态修复 + Linux 回归 + CI windows-latest matrix 兜底，**不得声明"已实测 Windows"**。

## 2. 隐含需求识别

| # | 隐含需求 | 为什么必须 |
|---|---------|-----------|
| I1 | S3 需建立「所有 `open()` 必须带 `encoding=`」的 grep 断言审计测试 | 13 个 py 是机械改动，漏一处仍有隐患；断言审计作回归拦截（HANDOFF 明确建议） |
| I2 | CI 需新增 windows-latest matrix（bats/shellcheck/consistency） | 本环境无法实测 Windows，CI 双平台是唯一兜底 |
| I3 | S2 改正则需新增中文文件名回归测试，防止"改正则过宽放过真缺证据" | known_risk 明确：过宽会掩盖真缺证据误报 |
| I4 | M6 修法需评估历史 CRLF review 文件影响 | `.gitattributes` 改 `*.md` 会强制所有仓库 md 换行、污染历史文件 PR；需在「gitattributes」与「frontmatter 提取处容错」间选择 |
| I5 | Q1 路径归一化必须同时保证 Linux 前缀匹配不变 | `${CARD_FILE#$AGATE_ROOT/}` 在 Linux 下工作正常，Windows 修复不能破坏它 |
| I6 | S1 改数组后需验证 Linux 全部 commit 场景（根/任务级 .state.yaml 混合、多任务并发） | S1 是最危险修复，fail-open 改错方向会引入新回归 |
| I7 | 修改 phase-cards/*.md 触发 SELF-GATE | commit message 需含 `self-gate-review:` 或 `self-gate-skip:`，否则 commit-msg hook WARNING |
| I8 | 改脚本走 TDD（先红后绿），不能跳过测试直接改 | AGENTS.md「改脚本的工作流」硬性约定 |
| I9 | consistency 检查必须用 worktree 自己的脚本 | 检查对象是 worktree 里的协议文件；误用 `~/.agate` 会扫主 checkout |
| I10 | P6 验收 Windows 类 BDD 用 Linux 中文 fixture 模拟，Windows 特有行为留给 CI | 本环境无 Windows 运行时 |

## 3. BDD 验收条件

> 组织原则：高风险缺陷（S1/S3）单独编号、可独立验证；低风险批量缺陷（M4/M5、其他）按组编号。每条 BDD 均映射「Linux 行为不变 + Windows/中文行为正确」两维，可二值判定。

### S1 — pre-commit-gate.sh 空格路径 fail-open 静默绕过

#### BDD-1: 路径含空格时 gate 不静默绕过
- Given 暂存的 .state.yaml 位于含空格路径的任务目录，且该阶段 gate 实际不通过（如 P1 缺 P1-review.md）
- When 触发 pre-commit-gate.sh
- Then 返回 exit 1（gate 拦截），而不是 fail-open 静默通过

#### BDD-2: 路径含空格时所有暂存 state 文件都被逐个处理
- Given 同一 commit 暂存多个 .state.yaml，其中至少一个位于含空格路径
- When 触发 pre-commit-gate.sh
- Then 每个暂存 .state.yaml 的格式校验/状态转移/gate 均被执行（无因空格切词丢失文件）

#### BDD-3: PROCESSED_DIRS 含空格路径时一致性检查正确
- Given 某任务目录路径含空格，其 .state.yaml 与 P{n}-*.md 产出同 commit 暂存
- When 触发 pre-commit-gate.sh
- Then 不因空格切词把单个目录拆成多段（不误报该目录"未处理"也不漏检）

#### BDD-4: Linux 路径不含空格时行为与现状完全一致
- Given Linux 常规无空格路径 + 现状场景（单任务、多任务）
- When 触发 pre-commit-gate.sh
- Then 检查结果与基线 676 bats 行为一致（含空格修复不引入 Linux 回归）

### S3 — 13 个 py 缺 encoding

#### BDD-5: 所有文本 open() 调用带 encoding="utf-8"
- Given agate/scripts/ 下全部 .py 文件
- When 执行 grep 断言审计（扫描 `open(`/`read_text(` 必须带 `encoding=`）
- Then 0 个文本读写 open() 缺失 encoding（二进制 Image.open 除外）

#### BDD-6: 含中文的协议文件被 py 工具正确读取
- Given P2-design.md / .state.yaml 含中文内容（如中文任务名、中文描述）
- When 运行 agate-md-field-get.py / agate-state-get.py / agate-read-gate-commands.py 等
- Then 正确返回字段值，无 UnicodeDecodeError，不被 bash `2>/dev/null || echo ""` 静默吞掉

#### BDD-7: 含中文的协议文件被 py 工具正确写回
- Given 任务含中文内容，执行写回类操作（如 retreat-state 写 reason、card-inject 写卡片）
- When 运行 agate-retreat-state.py / agate-card-inject.py
- Then 写回文件中文内容完整（allow_unicode 语义保持），无编码错误

#### BDD-8: Linux 下纯 ASCII 文件读取行为不变
- Given 现有测试夹具（ASCII 内容 .state.yaml / md）
- When 跑全量 bats
- Then 相关 unit/regression 测试全绿（加 encoding 不改变 Linux 读取结果）

### S2 — check-p6-evidence.sh 中文证据文件名

#### BDD-9: 中文文件名证据被识别为合法引用
- Given P6-acceptance.md 的 PASS 行引用中文文件名证据（如 `(截图 验证通过.png)`，ASCII 括号包裹、文件名含中文）
- When 运行 check-p6-evidence.sh（S2 修复：字符类加宽以支持中文，括号宽度不变仍为 ASCII）
- Then 判定该 PASS 有文件引用（exit 0 / 不因 ASCII 字符类假失败）

#### BDD-10: 无证据引用的 PASS 仍被拦截
- Given P6-acceptance.md 的 PASS 行无文件引用——不含括号，或括号内仅有描述性文字无文件名/扩展名（如 `(见截图)`）
- When 运行 check-p6-evidence.sh
- Then 判定缺证据引用（exit 1），字符类加宽不放宽"必须有文件名+扩展名"结构（防修复过宽误放行）

### M4/M5 — 全角冒号 POSIX locale 残留

#### BDD-11: check-gate.sh P7 全角冒号计数行正确排除
- Given 执行前置 `LC_ALL=C`（POSIX locale，回归测试须强制该 locale，默认 C.UTF-8 下不区分修复前后），P7-consistency.md 含 `[BLOCKER]：3 条` 形式的全角冒号总结行（非真实 BLOCKER）
- When 运行 check-gate.sh P7（旧格式回退路径）
- Then 总结行被正确排除，仅真实 `[BLOCKER]` 计数（不把总结行误计为阻塞）

#### BDD-12: check-p6-format.sh --fix 全角冒号总结行归一化成功（line 69 残留路径）
- Given 执行前置 `LC_ALL=C`（POSIX locale，回归测试须强制该 locale），P6-acceptance.md 含小写 `- fail：3` 全角冒号总结行（走 line 69 `[[:space:]:：]` bracket 归一化路径，区别于已修的 line 84 大写路径）
- When 运行 check-p6-format.sh --fix
- Then 该行被归一化为 `**Summary**: FAIL: 3`（全角冒号实例在 line 69 bracket 中不丢失）

#### BDD-13: 半角冒号与已有修复（check-p6-format.sh:84）行为不变
- Given 执行前置 `LC_ALL=C`（POSIX locale，回归测试须强制该 locale），P6-acceptance.md 含半角冒号 `- FAIL: 3` 总结行
- When 运行 check-p6-format.sh --fix + --check
- Then 归一化/校验结果与 v0.40.3 一致（全角修复在 POSIX locale 下不破坏半角路径）

### M6 — md CRLF 污染 frontmatter 提取

#### BDD-14: CRLF 行尾的 md 产出文件 frontmatter 提取不失效
- Given P1-requirements.md / P2-design.md 为 CRLF 行尾（`\r\n`）
- When 运行 frontmatter 提取（`sed -n '/^---$/...'` 或 check-frontmatter.sh）
- Then 正确识别 `---` 边界并提取 frontmatter 字段（不因 `\r` 导致整块缺失/字段为空）

#### BDD-15: Linux LF 行尾 md 文件行为完全不变
- Given 现有 LF 行尾产出文件
- When 运行全部 frontmatter/gate 相关检查
- Then 行为与基线一致（CRLF 容错不改变 LF 处理）

#### BDD-16: 历史 CRLF review 文件不受影响
- Given 仓库中已存在的 CRLF 历史 review 文件
- When 应用 M6 修复方案
- Then 这些历史文件不被强制改写（PR diff 无污染）；或修法本身不依赖改写历史文件（`[SUGGEST]` 见 §5 优先 frontmatter 容错）

### M9 — 路径正则元字符

#### BDD-17: 目录含 `[` 或 `*` 时 gate 正则不报错被吞
- Given 任务目录名含 `[`/`*` 等正则元字符，P0-brief/hook 流程正常运行
- When 触发 pre-commit-gate.sh / check-gate.sh（含 TASK_REL 拼入 grep -E 的路径）
- Then grep 正则不报错（不做特殊字符解释）、gate 判定正确、错误不被 `2>/dev/null` 吞掉

### 其他 — .agate.env CR / 复制模式 AGATE_ROOT / sed 转义

#### BDD-18: .agate.env 尾部 \r 不污染工作区解析
- Given .agate.env 为 CRLF 行尾（`AGATE_WORKSPACE=...` 后带 `\r`）
- When 运行 agate-workspace-resolve.sh
- Then 解析出的 AGATE_WORKSPACE 不含 `\r` 尾字符，路径有效

#### BDD-19: 复制模式安装的 hook 能正确解析 AGATE_ROOT
- Given hook 以复制模式安装（Windows 无符号链接权限，install-hook.sh 复制而非软链）
- When 运行复制到 .git/hooks/ 的 pre-commit-gate.sh
- Then AGATE_ROOT 正确解析到协议本体（不落到 .git/hooks 上层），gate 正常执行

#### BDD-20: render-dispatch-prompt sed 替换串转义正确
- Given AGATE_ROOT 路径或替换值含 `&`/`|` 等 sed 特殊字符（如 `C:\path&co\agate`）
- When 运行 agate-render-dispatch-prompt.sh
- Then 替换结果按字面值插入（`&` 不被当"整体匹配引用"、`|` 不被当分隔符），渲染输出正确

### Q1 — 路径归一化（agate-next-card.sh）

#### BDD-21: Windows 盘符/反斜杠路径下前缀匹配稳定
- Given AGATE_ROOT 为 Windows 风格路径（盘符+反斜杠或混合斜杠），CARD_FILE 在其下
- When 运行 agate-next-card.sh
- Then 输出相对路径正确（hash 校验用字节稳定），不因前缀匹配失效产生 hash mismatch

#### BDD-22: Linux 前缀匹配行为不变
- Given Linux 常规路径
- When 运行 agate-next-card.sh
- Then 相对路径输出与修复前完全一致（路径归一化不改变 Linux 字节输出）

### Q2 — 阶段卡片 phase 推进语义对齐（纯文档）

#### BDD-23: 7 张阶段卡片与 git-integration.md 规则 2 对齐
- Given P1/P2/P3/P4/P6/P7/P8 七张 phase-cards
- When 检查每张卡片的推进步骤描述
- Then 均含「commit 时 phase = 本 commit 产出阶段，下一阶段推进随下一阶段产出同 commit」语义，无"先更新 phase=N→N+1 再 commit"的旧 mode B 引导

#### BDD-24: 修复不改变 commit 顺序与 gate 判定逻辑
- Given Q2 修复后的卡片 + git-integration.md 规则 2 + P2.64 原子性设计
- When 对照检查
- Then commit 顺序要求不变、gate 判定逻辑不变（仅文档补注对齐，无逻辑改动）

#### BDD-25: 修复后协议一致性检查 0 ERROR
- Given phase-cards 变更后
- When 运行 worktree 的 `python3 agate/scripts/check-protocol-consistency.py --strict`
- Then 0 ERROR（文档改动未破坏协议一致性）

### Q5 — SETUP.md Windows 章节 + .gitignore 模板预设

#### BDD-26: SETUP.md 含 Windows 章节
- Given SETUP.md
- When 阅读 Windows 相关章节
- Then 覆盖：AGATE_ROOT Unix 路径（Git Bash 下）、PATH 注入、Git Bash 执行 hook、`PYTHONUTF8=1` 编码、CRLF/core.autocrlf 处理

#### BDD-27: .gitignore 模板预设 version.txt / dist 白名单
- Given .gitignore 模板/建议
- When 检查预设
- Then 包含 `!version.txt` 与 `dist/` 相关条目（版本文件不被误忽略）

### RM-AG0001 — check-gate.sh P1 反引号包裹盲区

#### BDD-28: 反引号包裹的 [SUGGEST: ...] 被识别为 SUGGEST
- Given P1-requirements.md 含 `` `[SUGGEST: 推荐 X]` ``（反引号包裹，行首标记）
- When 运行 check-gate.sh P1
- Then 该行被计入 SUGGEST（WARNING 提示主 Agent 采纳），不因反引号前缀漏计

#### BDD-29: 反引号包裹的 NEED_CONFIRM 阻塞标记被正确识别
- Given P1-requirements.md 含行首反引号包裹的未解决 NEED_CONFIRM 声明（方括号标记字面量整体被反引号包住）
- When 运行 check-gate.sh P1
- Then 判定为未解决 NEED_CONFIRM（exit 1 阻塞），不因反引号前缀漏计

### RM-AG0002 — check-tdd-red.sh 无 formatter 退化

#### BDD-30: 无 formatter + 编译失败（A 类）判 A 类红灯
- Given 测试运行器 exit 1 且输出含 compile/error 关键词，无 formatter 可用
- When 运行 check-tdd-red.sh
- Then 判定为 A 类错误（exit 1），不再误判为正确红灯（exit 0）

#### BDD-31: 无 formatter + 断言失败（B 类）判正确红灯
- Given 测试运行器 exit 1 且输出为普通断言失败（无 compile/error 关键词）
- When 运行 check-tdd-red.sh
- Then 判定为正确红灯（exit 0），行为与现状一致

### 全局回归（Linux 基线 + CI）

#### BDD-32: 全量 bats 测试全绿
- Given 本任务所有修复完成
- When 在 worktree 跑 `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/`
- Then 全部通过（无新增失败，676 基线回归 + 新增用例）

#### BDD-33: CI 含 windows-latest matrix 且通过
- Given protocol-tests.yml
- When CI 在 windows-latest 上运行 bats/shellcheck/consistency
- Then 双平台 job 均配置且通过（Windows 兼容的唯一兜底验证）

#### BDD-34: shellcheck 无 error
- Given 修改后的 scripts/*.sh
- When 运行 `shellcheck -S warning agate/scripts/*.sh`
- Then 0 error（修复不引入 shellcheck 问题）

### TPV0090-M4 — check-tdd-red.sh B 类 NameError 盲区

> 与 RM-AG0002（BDD-30/31）**同文件（check-tdd-red.sh）同修**——A/B 判定增强一次完成，P3 先写失败测试。修复方向：B 类检测纳入 NameError（项目内未定义符号，`errors` 中区分"未定义名"与"真实测试 bug"），保持向后兼容（现有 `globals().get()` 规避模式不回退）。

#### BDD-35: 测试引用未实现符号（NameError）判 B 类红灯
- Given 测试代码引用项目内未实现符号（如 `myapp.compute` 尚未实现）运行失败，formatter 输出 `syntax_errors=[]`、`import_errors=[]`、`errors>0`（失败为 NameError），PROJECT_MODULE 指向项目模块
- When 运行 check-tdd-red.sh
- Then 判定为 B 类红灯（exit 0），不被 `errors>0` 误判为 A 类（test code has errors）拦截

#### BDD-36: 使用 globals().get() 规避的既有测试不受破坏
- Given 既有测试以 `globals().get("未实现符号")` 规避 NameError（修复前推荐的规避写法），运行失败为普通断言失败
- When 运行 check-tdd-red.sh（NameError 修复后）
- Then 判定仍为正确红灯（exit 0），规避模式不被破坏（修复后规避不再必要但不回退）

#### BDD-37: 非未定义符号的真实测试 bug 仍判 A 类
- Given 测试代码存在真实 bug（非未定义符号 NameError，如 TypeError/断言内部异常）运行失败，formatter 输出 `syntax_errors=[]`、`import_errors=[]`、`errors>0`
- When 运行 check-tdd-red.sh
- Then 判定为 A 类错误（exit 1），B 类 NameError 扩展不扩大到所有 errors（防修复过宽）

## 4. 待确认清单

[NO_NEED_CONFIRM]

- 缺陷清单与修复范围已由 P0-brief 锁定，无真无方向的决策点。
- Q2 分析结论：7 张卡片（P1:17 / P2:13 / P3:13 / P4:16 / P6:16 / P7:14 / P8:14 的"更新 phase=Pn→Pn+1"步）是**纯文档对齐**（补注规则 2 语义），不需要改 check-gate.sh / pre-commit-gate.sh 的 gate 判定逻辑 → 不触发 NEED_CONFIRM 硬停。
- 倾向项见下方 `[SUGGEST]`（主 Agent 可自行采纳，不阻塞）。

## 5. 建议项（[SUGGEST]，不阻塞）

- [SUGGEST: M6 优先选「frontmatter 提取处统一容错（CRLF 归一，如 tr -d '\r'）」，而非 .gitattributes 加 *.md —— 理由：.gitattributes 注释明确历史 review 文档为 CRLF 存储，加 *.md 会强制重写全部历史文件、污染 PR；frontmatter 容错是局部、可回归的]
- [SUGGEST: S3 用「grep 断言审计」测试作回归拦截（所有 open() 带 encoding），不为 13 个 py 各写单测 —— 理由：机械改动单测边际成本高，HANDOFF 已建议；断言审计 + 全量 bats 兜底足够]
- [SUGGEST: RM-AG0002 无 formatter 时对 exit 1 + compile/error 关键词判 A 类（exit 1），普通失败保持红灯（exit 0）—— 理由：known_risk 已给该方向，保守判定避免编译失败被放行]

## 6. 审计范围（实际核验过的代码位置）

以下为 analyst 在 P1 阶段逐行核验、与 P0-brief 缺陷清单一致的代码位置：

**S1** `agate/scripts/pre-commit-gate.sh:50`（`STAGED_STATE_FILES` 空格拼接）、`:57`（`for ... in $STAGED_STATE_FILES` 未引号切词）、`:339/:343`（`PROCESSED_DIRS` 空格拼接）、`:350`（`case " $PROCESSED_DIRS "` 切词匹配）

**S3** 13 个 py（grep 全量核验，文本 `open()` 缺 encoding）：`agate-card-inject.py:13/15/28`、`agate-changelog-unreleased.py:8`、`agate-evidence-consistency.py:21/30`、`agate-gate-missing-cmds.py:12`、`agate-gate-p5-count.py:11`、`agate-md-field-get.py:112`、`agate-read-gate-commands.py:16`、`agate-read-p5-commands.py:18`、`agate-retreat-state.py:28/42/49`、`agate-state-get.py:25`、`agate-state-yaml-check.py:21`、`agate-vision-blocker.py:17`、`ci-gate-backstop.py:51/118/180`（`agate-image-check.py:31/44` 的 `Image.open` 为二进制图片，不在范围）

**S2** `agate/scripts/check-p6-evidence.sh:37`（`\([a-zA-Z0-9_/. -]*...\)` ASCII-only 正则）

**M4** `agate/scripts/check-gate.sh:356`（`\[BLOCKER\][:：]?` POSIX locale 全角冒号）

**M5** `agate/scripts/check-p6-format.sh:69`（三处 sed 的 `[[:space:]:：]` bracket；:84 已修，69 残留）

**M6** `.gitattributes`（无 `*.md`，注释行 4 明确排除历史 CRLF review）

**M9** `pre-commit-gate.sh:102/133/228`（`TASK_REL` 拼入 `grep -E "^${TASK_REL}/..."`）

**其他** `agate-workspace-resolve.sh:33`（grep 取 AGATE_WORKSPACE 未 `tr -d '\r'`）、`install-hook.sh:31` + `pre-commit-gate.sh:26`（复制模式 readlink 解析 AGATE_ROOT）、`agate-render-dispatch-prompt.sh:112-126`（sed 替换串未转义 `&`/`|`）

**Q1** `agate/scripts/agate-next-card.sh:56`（`${CARD_FILE#$AGATE_ROOT/}` 前缀匹配）

**Q2** `agate/phase-cards/P1-requirements.md:17`、`P2-design.md:13`、`P3-tdd.md:13`、`P4-implementation.md:16`、`P6-acceptance.md:16`、`P7-consistency.md:14`、`P8-release.md:14`（"更新 phase=Pn→Pn+1" mode B 残留）；对照 `git-integration.md:27/33` 规则 2；P5-verification.md:14 已对齐（参照样例）

**Q5** `agate/SETUP.md`（无 Windows 章节）、仓库根 `.gitignore`（无 version.txt/dist 预设）

**RM-AG0001** `agate/scripts/check-gate.sh:69/71/89/109`（`^\s*-?\s*\[...` 行首正则不匹配反引号前缀）

**RM-AG0002** `agate/scripts/check-tdd-red.sh:43`（无 formatter 退化 exit-code-only 说明）+ `:128-131`（TEST_RUNNER 直用无 formatter 路径）

**TPV0090-M4** `agate/scripts/check-tdd-red.sh:70/87-102`（B 类检测只认 `import_errors` 前缀匹配）+ `:104-107`（`errors>0` 一律判 A 类——测试引用未实现符号抛 NameError 落入 errors 被误判）

**CI** `.github/workflows/protocol-tests.yml`（仅 ubuntu-latest，无 windows-latest）

## 7. 裁剪说明（逐阶段理由）

全部 8 阶段均保留，不裁剪任何阶段：

- **P1 需求**：核心阶段，不可裁（本文件即产出）
- **P2 设计**：不可裁——需多方案评估：M6 修法选择（gitattributes vs frontmatter 容错）、S1 数组化改造、Q1 路径归一化策略；改动面 46 脚本，需架构级评审
- **P3 TDD**：不裁——改脚本必须测试先行（AGENTS.md 硬性工作流）；I1/I3 需新增回归测试（grep 断言审计、中文文件名用例），非配置类任务
- **P4 实现**：不可裁——46 脚本 + 文档实际改动
- **P5 验证**：不可裁——全量 bats + shellcheck + consistency 是 Linux 基线回归的客观证据
- **P6 验收**：不可裁——逐条对照本文件 BDD-1..37 验收（PASS/FAIL 总数 ≥ 37；新增 TPV0090-M4 三条 BDD-35/36/37 与 RM-AG0002 同脚本同批验收）
- **P7 一致性**：不可裁——46 脚本跨文件交叉核对 + phase-cards 文档一致性（I7 SELF-GATE）；P0-brief known_risk 明示"每处修复都可能破坏 Linux 行为"，跨文件改动必做 P7
- **P8 发布**：不裁——协议本体变更需发布（README version badge + tag + CI 双平台验证）；`internal_only: false`

**不裁 P3/P7/P8 的风险评估**（而非基于"任务小"）：改动面 46 脚本、含 SEVERE fail-open 类缺陷、跨 Linux/Windows 双平台——任何一跳都会放大回归风险，全部保留是低成本高回报的保守选择。

## 8. 能力需求声明

```yaml
capability_requirements:
  - need: windows-runtime
    why: 修复目标是 Windows 原生兼容，但本环境（Linux）无 Windows 运行时
    available:
      - "CI windows-latest matrix（protocol-tests.yml 需新增，唯一兜底）"
    status: supplementable
    note: 本环境不可实测，P6 验收 Windows 类 BDD（BDD-9/11/12/14/21/26 等）用 Linux 中文 fixture 模拟 + CI 双平台结果兜底，不宣称已实测

  - need: grep-assert-audit
    why: S3 需断言「所有 open() 带 encoding」作回归拦截
    available:
      - "bash + grep（本地，bats 测试内实现）"
    status: available

  - need: bats-test-framework
    why: 全量回归（676 基线 + 新增用例）
    available:
      - "本机 bats 1.10"
      - "CI ubuntu-latest + windows-latest"
    status: available

  - need: shellcheck
    why: 修改 .sh 后静态检查
    available:
      - "本机 shellcheck"
    status: available

  - need: protocol-consistency
    why: 协议文档（phase-cards/SETUP.md）变更后一致性检查
    available:
      - "worktree 自己脚本 python3 agate/scripts/check-protocol-consistency.py"
    status: available
```

无 `status: GAP` 项（windows-runtime 为 supplementable，通过 CI 补充，不阻塞流程）。

## 9. 环境约束记录

- `[PROD_NOT_TOUCHED]` 本阶段仅读 worktree 内文件，未接触任何生产环境。
