---
phase: P1
task_id: TAG0009-tests-platform-neutral
type: problems
parent: P0-brief.md
trace_id: TAG0009-tests-platform-neutral-P1-20260813
status: draft
created: 2026-08-13
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-tests, agate-scripts, ci-workflow]
domains: [backend]
# ── v2.0 标记"已解决/已确认"状态 ──
scope_resolved: ["产品脚本裸 python3 真实 Windows 环境失效（17 文件 68 处）：判定另立任务（TAG0010+）根治，本任务 harness shim 只覆盖测试场景"]
---

# P1 需求基线 — agate 测试套件平台无关化（TAG0009）

> 基线事实（本文件已核验，作为 P2 设计的输入依据）：
> - CI 日志 `/tmp/bats-win-fail.log` 中 `not ok N` 实际 **77** 例（19 文件）；字面 "not ok" 78 次含 1 个假阳性——FMT.11 用例名 `(2 ok, 1 not ok)`。
> - Linux 基线：`count-tests.sh` = 720（+sanity 6 = 726），consistency 0 ERROR，shellcheck 0 error。此为回归底线。
> - 现有 CI：bats job 仅 ubuntu-latest；shellcheck / consistency / gate-backstop 三个 job 已 windows-latest matrix，且 Windows 分支用 `python` + `PYTHONIOENCODING=utf-8`（TAG0009 可直接复用此模式）。

## 1. 需求复述

把 77 个 Windows bats 失败按「测试平台无关原则」（AGENTS.md「测试约定」，v0.44.0 确立）根治：测试代码不得硬编码单平台假设；目标状态是**测试套件平台无关——Linux 全量覆盖所有分支，Windows CI 只作最终确认**。四层方案：

1. 新增静态扫描器 gate（check-platform-assumptions，bash+grep 实现，自身平台无关）扫描测试代码的 Unix 假设，接入 CI 阻断新假设；
2. 批量修现有 77 个失败（按根因分类：PATH 硬编码 / python3 解析 / symlink 单平台断言 / /tmp Unix-only 路径 / CRLF 编码 / 外部工具依赖）；
3. 每个 Windows 分支在 Linux 上用模拟环境覆盖（PYTHONIOENCODING / ln mock / PATH 探测）；
4. 真 Windows CI 作最终确认。

本任务**不改协议语义、不改 gate 逻辑判定规则**，只改测试套件平台无关性 + 加一道静态扫描 gate。Linux 基线是红线。

## 2. 隐含需求识别

| # | 隐含需求 | 为什么必须 |
|---|---------|-----------|
| I1 | 被测试调用的**产品脚本**（`agate/scripts/*.sh`）内部的裸 `python3`（17 文件 68 处）也必须在 Windows 测试环境下可解析——否则测试套件无法在 Windows 跑 | 核验发现：77 例中 **41 例（53%）** 的真因是产品脚本内部裸 `python3`（check-state-transition / check-frontmatter / check-state-yaml / check-changelog / agate-debt-check / check-p6-provenance / check-retrospective / check-scope-resolved / agate-inject-card 等）。Windows 无 `python3`（仅 `python`）时这些调用静默失败 → 脚本读不到状态 → exit 0 → 测试断言 exit 1 失败。**仅改测试侧 python3 调用修不了这批**（见 SUGGEST-1 定方向） |
| I2 | python3 探测 helper 自身不得触发扫描器误报 | helper 用 `command -v python3 || command -v python` 探测时，"python3" 字面会出现在 helper 里；扫描器必须区分"调用 python3"与"探测 python3"，否则 gate 扫 helper 自爆（P2 定白名单/语义规则） |
| I3 | 输出匹配断言须对行尾/编码差异健壮 | Windows 下 git CRLF warning（`LF will be replaced by CRLF`）混入 stderr 捕获、python stdout 默认代码页非 UTF-8（cp1252 等）时，中文关键词断言（如 `*"真红灯"*`）可能因编码 mojibake 失败（ci-gate-backstop 7 例相关） |
| I4 | 外部工具依赖（`bc`/`shellcheck` 等）须平台无关 | 核验发现 agate-extract-context.bats 2 例真因是 `agate-extract-context.sh` L128 依赖 `bc`（Windows Git Bash 无）；env-adapt-docs bdd-34 真因是 `shellcheck` vs `shellcheck.exe` 工具名差异。同类扫描须纳入 |
| I5 | 静态扫描器的**扫描范围/模式集/阻断强度**须 P1 定义 | 范围决策影响"同类扫描闭环"是否真成立：扫 `agate/tests/` 全树（unit/regression/integration/helpers/scripts/sanity.bats）才能兜底新 Unix 假设；产品 `agate/scripts/` 不在本任务范围（见 SUGGEST-2） |
| I6 | 修改流程纪律：每处修复先加平台无关的失败测试（红）再改 | Linux 基线是红线（P0 known_risks[0]）；无红不绿会悄悄破坏 Linux 行为 |
| I7 | 真 Windows CI 是"最终确认"而非本机能力 | 本机 Linux，无法本地跑 Windows；声明 supplementable（GitHub Actions matrix），不声明 GAP |
| I8 | symlink 断言按平台分支（Linux 断言软链 / Windows 断言复制模式 + WARNING） | install-hook.bats 2 例：Windows Git Bash `ln -sf` 退化为复制，`[[ -L ]]` 恒假；既有「ln 退化为复制时打印升级提醒」用例（install-hook.bats L43）已确立模拟先例 |
| I9 | /tmp 字面量替换为 `$BATS_TEST_TMPDIR`（测试逻辑路径）；fixture 内容字符串中的 /tmp 属输出样例非路径假设，须与逻辑路径区分 | agate-next-card.bats L104（`cd /tmp`）是逻辑路径；check-tdd-red.bats L139/148 等是 mock 输出字符串。扫描器规则须区分，避免误报样例文本 |
| I10 | 测试计数文档（tests/README.md 表格 + count-tests.sh）若因修复新增用例须同步 | 新增扫描器测试用例/探测 helper 用例会改变用例数，README「何时更新」已有约定 |

## 3. BDD 验收条件

### 3.1 静态扫描器 gate（check-platform-assumptions）

#### BDD-1: 新增平台假设扫描器，自身平台无关
- Given 仓库新增 `check-platform-assumptions` 扫描脚本
- When 在 Linux 与 Windows（MSYS2）环境分别运行扫描器自身
- Then 两个平台均能执行且行为一致（无 Unix-only 依赖、无报错退出）

#### BDD-2: 扫描器检出硬编码 PATH
- Given 扫描范围内任一 .bats/.bash/.sh 文件含 `PATH="/usr/bin:/bin"` 字面
- When 运行扫描器
- Then 以非零退出码报告该文件与该行

#### BDD-3: 扫描器检出测试侧裸 python3 调用
- Given 扫描范围内任一文件以"命令位置"调用 `python3`（非 `command -v python3` 探测形态）
- When 运行扫描器
- Then 以非零退出码报告该文件与该行

#### BDD-4: 扫描器检出 symlink 单平台断言
- Given 扫描范围内任一文件含 `[[ -L ... ]]` 或 `[ -L ... ]` 形式断言
- When 运行扫描器
- Then 以非零退出码报告该文件与该行

#### BDD-5: 扫描器检出 /tmp 逻辑路径假设
- Given 扫描范围内任一文件使用 `/tmp` 作为测试逻辑路径（排除 `$BATS_TEST_TMPDIR`、排除 fixture/mock 输出字符串中的样例文本）
- When 运行扫描器
- Then 以非零退出码报告该文件与该行

#### BDD-6: 扫描器检出 Unix-only 外部工具依赖
- Given 扫描范围内任一文件以命令位置裸调用 `bc`（以及扫描器模式集后续扩充的工具，如 `seq`/`timeout`）
- When 运行扫描器
- Then 以非零退出码报告该文件与该行

#### BDD-7: 扫描器接入 CI，检出即阻断
- Given 扫描范围内存在任一 Unix 假设（新引入）
- When 推送/PR 触发 CI
- Then Linux CI 的扫描步骤失败（exit 非零），阻断合并

#### BDD-8: 扫描器对"干净"测试套件零检出（同类扫描闭环）
- Given 本任务全部修复完成后，扫描器在 `agate/tests/` 全树运行
- When 收集全部检出
- Then 检出数 = 0（含原 77 例所在 19 文件 + 全部同类实例，非仅已知失败）

#### BDD-9: 扫描器自身有行为测试
- Given 构造一个含硬编码 PATH / 裸 python3 / [[ -L ]] / /tmp 的 fixture 文件与一个干净 fixture
- When 分别运行扫描器
- Then 含假设 fixture → 非零退出且报告具体模式；干净 fixture → 零退出且无报告

### 3.2 PATH 硬编码修复（check-tdd-red.bats，15 处 / 13 失败）

#### BDD-10: check-tdd-red.bats 移除 PATH 硬编码
- Given 当前文件含 15 处 `PATH="/usr/bin:/bin"` 字面
- When 完成修复后对全文件 grep
- Then 字面 `PATH="/usr/bin:/bin"` 出现次数为 0

#### BDD-11: "PATH 无 python" 场景改为平台无关构造
- Given 测试需验证"测试运行器不可用"（TD.1b / TDD.F8 场景）
- When 完成修复后查看这两个用例
- Then 不再通过覆盖 PATH 为 Unix 路径构造，而改用平台无关方式（如探测出的 PATH + 移除 python、或 TEST_RUNNER 指向不存在路径），且原 exit 语义（exit 3/1）不变

#### BDD-12: 原 13 个 PATH 失败用例红绿灯语义不变
- Given check-tdd-red.bats 全量运行
- When 修复后
- Then 全部用例通过，且每个用例判定的 exit 0/1/2/3 红绿灯语义与修复前一致（未改判定逻辑，只改环境构造）

### 3.3 python3 探测 helper（I1 / I2）

#### BDD-13: 提供 PYTHON 探测 helper
- Given fixtures.bash/load.bash 新增 PYTHON 探测（优先 `python3`，回退 `python`）
- When 在 Linux 全量测试中引用该 helper
- Then `$PYTHON` 解析为可用的 python 解释器，且 helper 自身平台无关、不触发扫描器误报（探测形态豁免）

#### BDD-14: 全部测试侧裸 python3 调用改为 $PYTHON
- Given 同类扫描确认 25 个含裸 python3 的测试文件（unit 21 + integration 2 + regression 2；README 为文档不适用）。计数口径 = 含命令位置裸 `python3` 的 .bats 文件数（含引号边界在内的命令位置，如 `bash -c "python3 ..."` 中 python3 前是引号而非空格；`command -v python3` 探测形态与 helper 内部引用除外）；`agate-debt-check.bats` 实测 0 处 python3，不属测试侧
- When 完成修复后对全部 .bats 文件 grep 命令位置裸 `python3`
- Then 检出为 0（扫描器 BDD-3 亦确认），所有调用改用探测出的解释器

#### BDD-15: helper 回退分支有 Linux 模拟测试
- Given 构造"PATH 仅含 python（无 python3）"的模拟环境
- When 运行探测 helper
- Then 解析结果回退到 `python`，且该回退分支有对应测试用例（在 Linux 上覆盖 Windows 无 python3 场景）

#### BDD-16: 被测试调用的产品脚本内 python3 在 Windows 模拟下可解析（I1，41 例修复）
- Given 产品脚本（如 check-state-transition.sh / check-frontmatter.sh / check-state-yaml.sh / check-changelog.sh / agate-debt-check.sh / check-p6-provenance.sh / check-retrospective.sh / check-scope-resolved.sh / agate-inject-card.sh）内部存在裸 `python3`
- When 测试运行在这些脚本上，且环境为"仅 python 可解析、python3 不可用"（Linux 模拟 + 真 Windows）
- Then 脚本内 python3 调用仍能解析到探测出的解释器，原 41 个 script-side 失败用例全部转绿

#### BDD-17: Linux 模拟"无 python3"下产品脚本行为不劣化
- Given 在 Linux 上用模拟环境（屏蔽 python3、仅留 python）运行受影响产品脚本
- When 与正常环境（有 python3）行为对比
- Then gate 判定结果一致（无 python3 时不再静默 exit 0 误放行，能执行原判定）

### 3.4 symlink 按平台分支（install-hook.bats，2 例）

#### BDD-18: install-hook.bats 的 [[ -L ]] 断言按平台分支
- Given install-hook.bats 的 2 处 `[[ -L ]]` 断言
- When 在 Linux 上运行
- Then 断言软链语义（真软链存在且指向 pre-push-gate.sh）；同时保留/新增「模拟 ln 退化为复制」分支用例，断言输出复制模式 WARNING 而非软链

#### BDD-19: Windows 分支（ln 复制模式）有 Linux 模拟覆盖
- Given 模拟 ln 退化为复制（既有 mock 模式，install-hook.bats L43 先例）
- When 在 Linux 上运行安装脚本测试
- Then 复制模式下输出升级提醒（"复制"/"需重跑"）且不误报软链语义

### 3.5 /tmp 与 Windows 路径（agate-next-card.bats / check-scope-resolved.bats）

#### BDD-20: 测试逻辑路径不再使用裸 /tmp
- Given agate-next-card.bats L104（`cd /tmp`）与 check-scope-resolved.bats L8（`/tmp/nonexistent-...`）
- When 完成修复后
- Then 逻辑路径改用 `$BATS_TEST_TMPDIR`（或等价平台无关临时目录），fixture 输出字符串中的 /tmp 样例文本保留但不再被扫描器视为路径假设

#### BDD-21: agate-next-card.bats bdd-21（盘符/反斜杠）setup 平台无关
- Given bdd-21 在 Linux 以字面反斜杠目录名模拟 Windows 路径前缀剥离（当前通过）
- When 在 Windows 上运行（目录名含反斜杠会被当作分隔符、setup 失效的场景）
- Then 测试在 Windows 也能正确构造并断言"路径：phase-cards/P3-tdd.md"，且 Linux 行为不变（P2 定精确 setup 方式）

### 3.6 输出匹配 / 编码 / 外部工具（ci-gate-backstop / extract-context / env-adapt-docs）

#### BDD-22: 输出匹配断言对行尾差异健壮
- Given 断言形如 `[[ "$output" == *"关键词"* ]]` 且捕获输出可能含 CRLF/git warning
- When 在 Linux 上用 CRLF 混入的模拟输出验证这些断言
- Then 匹配仍成功（匹配前归一化输出或断言写法对换行差异免疫），ci-gate-backstop.bats 7 例转绿

#### BDD-23: 中文关键词输出匹配对编码差异健壮
- Given 调用会输出中文关键词（如"真红灯"/"绿灯"/"SKIP"）的 python 工具
- When 在 PYTHONIOENCODING=cp1252（Windows 默认代码页）与 utf-8 两种设置下运行
- Then 输出中的中文关键词在两种设置下均可被断言命中（显式设置 PYTHONIOENCODING 或断言对编码免疫）

#### BDD-24: agate-extract-context.sh 移除 bc 依赖
- Given agate-extract-context.sh L128 用 `bc` 求和 P5 failed 数
- When 完成修复后在无 bc 环境（模拟）运行
- Then 求和结果正确（改用 bash 原生整数运算或等价平台无关方式），agate-extract-context.bats 2 例转绿

#### BDD-25: env-adapt-docs.bats bdd-34 shellcheck 调用平台无关
- Given bdd-34 以 `bash -c shellcheck ...` 调用（Windows 下工具名为 shellcheck.exe，且 glob 引号在 Git Bash 解析不同）
- When 完成修复后在 Windows 模拟下运行
- Then shellcheck 可被解析（探测 shellcheck|shellcheck.exe）且调用方式在双平台一致，bdd-34 转绿

### 3.7 Linux 模拟覆盖 Windows 分支（显式清单）

#### BDD-26: 每个 Windows 分支有对应 Linux 模拟测试
- Given 本任务引入/依赖的 Windows 分支（PYTHONIOENCODING 非 UTF-8 代码页、ln 退化为复制、PATH 无 python3 仅 python、无 bc、无 shellcheck 命令名）
- When 统计覆盖
- Then 每个分支在 Linux 上至少有一个显式模拟测试用例（含真实断言，非仅注释）

### 3.8 真 Windows CI 最终确认

#### BDD-27: bats job 增加 windows-latest 作最终确认
- Given protocol-tests.yml 的 bats job 当前仅 ubuntu-latest
- When 本任务修复完成（Linux 全绿）后
- Then bats job 增加 windows-latest（P2 定精确方式：matrix 或独立 job），push/PR 触发且 0 失败

#### BDD-28: Linux 全量基线全程保持全绿
- Given 修改全程
- When 每完成一处修复
- Then `bats sanity+unit+regression+integration` 全绿（720+6=726）+ `check-protocol-consistency.py --strict` 0 ERROR + `shellcheck -S warning` 0 error，作为回归底线

#### BDD-29: 修改流程先红后绿
- Given 每处平台假设修复（PATH / python3 / symlink / /tmp / bc / shellcheck）
- When 开始修改前
- Then 先加平台无关的失败测试并确认红（exit 非 0），再改实现确认绿（test-driven，AGENTS.md「改脚本的工作流」）

## 4. 待确认清单

[NO_NEED_CONFIRM]（无阻塞待确认项；以下为有明确倾向、可自行采纳的 SUGGEST 项）

- [SUGGEST: 产品脚本裸 python3（17 文件 68 处）用测试 harness PATH shim 兜底（fixtures 在临时 bin 目录放 `python3` 包装器指向探测出的解释器、测试运行产品脚本时前置到 PATH），不改 17 个产品脚本；理由：TAG0009 范围锁测试套件（P0-brief）、零产品回归风险、一次覆盖 41 例 script-side 失败。产品脚本在真实 Windows 用户环境的潜在失效（hooks 场景）属产品问题，建议另立任务（见 [SCOPE+] 观察）]
- [SUGGEST: 扫描器范围 = `agate/tests/` 全树（unit/regression/integration/helpers/scripts/fixtures + sanity.bats），不含 `agate/scripts/`（产品脚本，本任务范围外）；阻断方式 = Linux CI 步骤失败（exit 1），本地 pre-commit 不接入（避免误伤正常开发）]
- [SUGGEST: python3 探测 helper 放 fixtures.bash（`detect_python` + 导出 `PYTHON`），load.bash 在加载 fixtures 时调用一次；P2 定精确放置与注入点]
- [SUGGEST: Windows bats job 采用现有三个 job 的成熟模式（windows-latest 分支用 `python` + `PYTHONIOENCODING=utf-8`），新增时复用不另起炉灶]
- [SUGGEST: 输出匹配归一化采用匹配前 `tr -d '\r'`（或等价），不动被匹配的断言关键词]

[SCOPE+] 观察（不阻塞本次，供主 Agent 判断是否回写需求基线或另立任务）：产品脚本 17 文件 68 处裸 `python3` 在真实 Windows 用户环境（用户本机 Git Bash 装 hooks）同样会失效，属产品层平台化缺口；本次 harness shim 只覆盖测试场景，根治需产品脚本探测 python3|python（建议 TAG0010+ 单独任务）。

## 5. 裁剪说明

- 全部 8 个阶段均保留，无裁剪。理由：risk_level=medium（测试基建 + CI + 新增 gate 脚本，改动面大、涉多文件多脚本）；P3 不可裁（非 low）；P7 一致性用于校验扫描器模式集与 BDD/README 文档不漂移；P8 与 TAG0005 联合发布（HANDOFF §8b 已约定一次 P8 bump v0.45.0）。

## 6. 范围声明

- `packages: [agate-tests, agate-scripts, ci-workflow]`（见 frontmatter）
  - `agate-tests`：`agate/tests/**`（unit/regression/integration/helpers/scripts/fixtures/sanity.bats）——批量修 + 扫描器测试 + helper
  - `agate-scripts`：`agate/scripts/check-platform-assumptions*`（新增扫描器）；agate-extract-context.sh（bc 移除，唯一产品脚本改动）；其余 17 个产品脚本**不改**（harness shim 兜底）
  - `ci-workflow`：`.github/workflows/protocol-tests.yml`（扫描器 job + Windows bats job）
- `domains: [backend]`（内部工具/测试基建，无 frontend/mcp/security 影响）

## 7. 能力需求声明

```yaml
capability_requirements:
  - need: bats 测试运行（全量 726 用例）
    why: 回归底线 + 修复验证
    available:
      - "本地 bats ≥1.2.0（已装，Linux）"
    status: available

  - need: python3 + pyyaml + Pillow
    why: 既有 gate 依赖 + 扫描器/探测验证
    available:
      - "python 3.12 + pyyaml（已装，Linux）"
    status: available

  - need: shellcheck
    why: env-adapt-docs bdd-34 修复验证（shellcheck|shellcheck.exe 探测）
    available:
      - "shellcheck（已装，Linux）"
    status: available

  - need: 真 Windows 执行环境
    why: Windows bats CI 最终确认（本机 Linux 无法本地跑 Windows）
    available: []
    status: supplementable
    gap_note: "借助 GitHub Actions windows-latest matrix 作最终确认；Linux 上用 PYTHONIOENCODING / ln mock / PATH 探测模拟覆盖 Windows 分支"

  - need: 静态扫描器运行环境（bash + grep）
    why: check-platform-assumptions 实现与 CI 接入
    available:
      - "bash + grep（已装，Linux；MSYS2 下等价）"
    status: available
```

## 8. 附：核验证据（供 P2/P4/P5 引用）

- 77 失败逐文件计数（19 文件，PR #127 CI 日志 `/tmp/bats-win-fail.log`）：
  - RC-PATH 硬编码（13）：check-tdd-red.bats（15 处 PATH 字面）
  - RC-python3 脚本侧（41）：check-state-transition 10 / check-frontmatter 9 / check-state-yaml 7 / check-changelog 5 / agate-debt-check 4 / check-p6-provenance 2 / check-retrospective 1 / check-scope-resolved 1 / agate-inject-card 2
  - RC-python3 测试侧（17）：ci-gate-backstop 7 / agate-state-yaml-check 3 / check-protocol-consistency 3 / check-p6-format 2 / agate-evidence-consistency 1 / env-adapt-docs(bdd-25) 1
  - RC-外部工具（3）：agate-extract-context 2（bc）/ env-adapt-docs(bdd-34) 1（shellcheck 工具名）
  - RC-symlink 单平台断言（2）：install-hook.bats
  - RC-Windows 路径语义（1）：agate-next-card.bats bdd-21
- 同类扫描结果（全仓 grep）：
  - `PATH="/usr/bin:/bin"`：1 文件（check-tdd-red.bats，15 处）+ tests/README.md（文档提及）
  - 裸 python3：25 文件（unit 21：agate-card-inject / agate-changelog-unreleased / agate-evidence-consistency / agate-gate-missing-cmds / agate-gate-p5-count / agate-image-check / agate-json-get / agate-md-field-get / agate-read-p5-commands / agate-retreat-state / agate-scripts-encoding / agate-state-get / agate-state-yaml-check / agate-vision-blocker / check-frontmatter / check-p6-format / check-protocol-consistency / check-tdd-red / check-tdd-red-formatter / ci-gate-backstop / env-adapt-docs；integration 2：consistency / pre-commit-hook；regression 2：v040-dotarchived-exclusion / v060-yaml-indent）。agate-debt-check.bats 实测 0 处 python3，不属测试侧（其失败归 script-side 41 例 bucket，见 RC-python3 脚本侧）
  - `[[ -L ]]`：1 文件（install-hook.bats，2 处）；readlink：agate-next-card.bats / install-hook.bats
  - `/tmp`：agate-next-card.bats L104（逻辑路径）/ check-scope-resolved.bats L8（逻辑路径）/ check-tdd-red.bats L139、148 / check-tdd-red-formatter.bats L97、105（fixture 输出字符串样例，非路径假设）
  - 产品脚本裸 python3：17 文件 68 处（gate-result / check-debt / check-frontmatter / agate-capture-env-baseline / pre-commit-gate / check-p6-evidence / check-gate / agate-inject-card / check-p6-provenance / check-pruning / check-scope-resolved / agate-retreat-to / check-retrospective / check-state-transition / check-state-yaml / check-changelog / check-tdd-red）
- CI 现状：bats job 仅 ubuntu；shellcheck/consistency/gate-backstop 已 windows matrix 且 Windows 用 `python`+`PYTHONIOENCODING=utf-8`（复用模板）。
