---
phase: P1
task_id: TAG0009-tests-platform-neutral
type: review
parent: P1-requirements.md
trace_id: TAG0009-tests-platform-neutral-P1-20260813
status: approved
created: 2026-08-13
agent: requirements-review
---

# P1 Review — TAG0009 测试套件平台无关化（复评轮）

## 评审结论

**Status: approved**

上一轮唯一阻塞项（BDD-14 Given 计数错误）已修正并复验通过；其余 BDD-1..29 抽查未发现被重写破坏。全部审查项通过。

---

## 上一轮阻塞项复验（BDD-14）

- BDD-14: **通过**（PY）。Given 计数已改为 **25**（unit 21 + integration 2 + regression 2），与实测一致：全仓 .bats grep 命令位置裸 `python3` = 25 文件（unit 21 匹配 §8 清单逐文件核验 ✓ / integration 2：consistency、pre-commit-hook ✓ / regression 2：v040-dotarchived-exclusion、v060-yaml-indent ✓）。`agate-debt-check.bats` 实测 0 处 python3，已从清单移除并在 Given 注释中正确标注"其失败归 script-side 41 例 bucket"。§8「同类扫描结果」unit 列表（21 个）与 Given 计数一致，无残留旧数。

## BDD 评审（逐条）

> 覆盖维度标注：PATH=路径/环境构造，PY=python 解析，SY=symlink，TMP=/tmp 与路径语义，ENC=输出/编码/外部工具，SC=扫描器，CI=CI 接入，SIM=模拟覆盖，REG=回归底线

### 3.1 静态扫描器 gate（SC）

- BDD-1: 通过（SC）。二值：Linux 与 Windows（MSYS2）均可执行且行为一致。⚠️ 注：本机仅能验证 Linux，Windows 侧依赖 CI（supplementable，I7 已声明），与 BDD-27 联动。
- BDD-2: 通过（SC/PATH）。二值：字面 `PATH="/usr/bin:/bin"` 检出→非零退出。已复核 check-tdd-red.bats 15 处真实存在。
- BDD-3: 通过（SC/PY）。二值：命令位置 `python3` vs 探测形态豁免边界已在 Given 定义（`非 command -v python3 探测形态`）。语义规则精确化属 P2 设计（I2 已声明），不阻二值判定。
- BDD-4: 通过（SC/SY）。二值：`[[ -L ... ]]`/`[ -L ... ]` 检出→非零退出。已复核 install-hook.bats 2 处真实存在。
- BDD-5: 通过（SC/TMP）。二值：Given 已界定"逻辑路径 vs fixture/mock 输出样例文本"边界，样例文本实例（check-tdd-red.bats L139/148、check-tdd-red-formatter.bats L97/105）在 I9/BDD-20 明确标注"保留但非路径假设"。扫描器规则 P2 精确化，BDD-5 可借 BDD-9 fixture 对判定。
- BDD-6: 通过（SC/ENC）。二值：`bc` 裸调用检出→非零退出，模式集可扩充。已复核 agate-extract-context.sh L128 真实依赖 `bc`。
- BDD-7: 通过（SC/CI）。二值：CI 步骤 exit 非零即阻断。
- BDD-8: 通过（SC）。二值：修复完成后全树检出数 = 0。
- BDD-9: 通过（SC）。二值：含假设 fixture→非零 + 报告模式；干净 fixture→零退出。扫描器自身行为测试，判定机制最硬核。

### 3.2 PATH 硬编码（PATH）

- BDD-10: 通过（PATH）。二值：grep 字面出现次数为 0。已复核当前 15 处真实存在。
- BDD-11: 通过（PATH）。二值：TD.1b / TDD.F8 场景改用平台无关构造，exit 语义（3/1）不变。
- BDD-12: 通过（PATH/REG）。二值：全量通过且 exit 0/1/2/3 红绿灯语义与修复前一致。

### 3.3 python3 探测 helper（PY）

- BDD-13: 通过（PY）。二值：`$PYTHON` 解析为可用解释器 + helper 平台无关 + 不触发扫描器误报。⚠️ 微瑕：Given 点名 fixtures.bash/load.bash 属轻微方案泄漏，但 SUGGEST-3 已声明"P2 定精确放置与注入点"，可接受。
- BDD-14: 通过（PY）。见上文"上一轮阻塞项复验"，计数 25 已修正。
- BDD-15: 通过（PY/SIM）。二值：模拟"仅 python 无 python3"→回退 `python` 且有测试用例覆盖。
- BDD-16: 通过（PY）。二值：41 个 script-side 失败用例全部转绿（可计数）。判定核实：产品脚本裸 python3 真实存在（实测 17 文件 68 处，check-state-transition.sh 3 处、check-p6-provenance.sh 6 处、agate-inject-card.sh 2 处等）；Windows 无 `python3` 时 `python3 ... 2>/dev/null || true` 静默失败→脚本读不到状态→exit 0→测试断言 exit 1 失败，真因成立。Then 描述行为结果，机制在 SUGGEST-1，P1 纯净性可接受。⚠️ 观察项（非阻塞）：示例清单写 `agate-debt-check.sh`，实际产品脚本名为 `check-debt.sh`（§8 已正确写 check-debt）——示例为"如"引导的示意性列举，不影响 41 例计数与二值判定。
- BDD-17: 通过（PY/REG）。二值：无 python3 模拟环境 vs 正常环境 gate 判定结果一致。SUGGEST-1（harness PATH shim、范围锁测试套件、不改 17 产品脚本、产品根治另立任务）判定合理：一次覆盖 41 例 script-side 失败、零产品回归风险，与 P0-brief 范围一致。

### 3.4 symlink（SY）

- BDD-18: 通过（SY）。二值：Linux 断言软链语义 + 保留/新增"ln 退化为复制"分支断言复制模式 WARNING。install-hook.bats 2 处 `[[ -L ]]` 已复核。
- BDD-19: 通过（SY/SIM）。二值：模拟 ln 退化复制→输出升级提醒且不误报软链。install-hook.bats L43 既有先例已复核。

### 3.5 /tmp 与 Windows 路径（TMP）

- BDD-20: 通过（TMP）。二值：逻辑路径改 `$BATS_TEST_TMPDIR`，样例文本保留但不被扫描器视为路径假设。已复核 agate-next-card.bats L104（`cd /tmp`）与 check-scope-resolved.bats L8（`/tmp/nonexistent-...`）为逻辑路径，样例文本位置正确归类。
- BDD-21: 通过（TMP/SIM）。二值：Windows 下 setup 正确构造并断言 `路径：phase-cards/P3-tdd.md`，Linux 行为不变；P2 定精确 setup 方式已显式延迟。

### 3.6 输出/编码/外部工具（ENC）

- BDD-22: 通过（ENC）。二值：CRLF 混入模拟输出下断言仍命中。ci-gate-backstop 7 例为该 bucket，已复核。
- BDD-23: 通过（ENC）。二值：cp1252 vs utf-8 两种设置下中文关键词均可命中。ci-gate-backstop 相关 7 例中编码型归属此条。
- BDD-24: 通过（ENC）。二值：移除 bc 后无 bc 环境求和结果正确。已复核 agate-extract-context.sh L128 真实依赖 bc。
- BDD-25: 通过（ENC/SIM）。二值：shellcheck|shellcheck.exe 探测且调用方式双平台一致。已复核 env-adapt-docs.bats bdd-34 以 `bash -c "shellcheck ..."` 调用。

### 3.7 模拟覆盖（SIM）

- BDD-26: 通过（SIM）。二值：每个 Windows 分支（PYTHONIOENCODING 非 UTF-8 / ln 退化复制 / PATH 无 python3 / 无 bc / 无 shellcheck 命令名）在 Linux 上至少一个显式模拟测试用例。与 I4/I8/I9/I3 闭环。

### 3.8 回归与流程（REG/CI）

- BDD-27: 通过（CI）。二值：bats job 增 windows-latest，push/PR 触发且 0 失败；P2 定 matrix/独立 job 方式已显式延迟。
- BDD-28: 通过（REG）。二值：全程 726（720+6）全绿 + consistency 0 ERROR + shellcheck 0 error。基线声明与 count-tests.sh 一致。
- BDD-29: 通过（REG）。二值：每处修复先红后绿（TDD），与 AGENTS.md「改脚本的工作流」一致。

## 隐含需求覆盖

| 维度 | 覆盖情况 |
|------|---------|
| 数据维度 | I1（script-side python3 41 例）→ BDD-16/17；I3（编码/行尾）→ BDD-22/23；I4（外部工具 bc/shellcheck）→ BDD-6/24/25 |
| 前端维度 | N/A（无 UI 变更，domains=[backend] 声明正确） |
| 多端维度 | 平台分支语义（I8 symlink、I9 /tmp、I1 python3）→ BDD-16/17/18/19/20/21 |
| 边界维度 | I2 探测形态豁免边界 → BDD-3/13；I5 扫描范围/模式/阻断 → BDD-1~9 + SUGGEST-2；I7 Windows supplementable → BDD-27 + capability |
| 兼容维度 | Linux 回归红线（I6）→ BDD-28/29；文档计数同步（I10）→ 附注见下 |

- 隐含需求全部映射到 BDD，无遗漏。
- I10（count-tests.sh / tests/README 用例数同步）未单独立 BDD，但属 P2 设计时的文档维护约定（README「何时更新」既有约定 + count-tests.sh 自带漂移告警），不构成覆盖缺口。

## 裁剪评审

- 全 8 阶段保留，无裁剪。risk_level=medium 匹配：测试基建 + CI + 新增 gate 脚本，改动面大但无协议语义/gate 逻辑变更。P3 不可裁（非 low）、P7 用于扫描器模式集与 BDD/README 文档一致性校验、P8 与 TAG0005 联合发布（HANDOFF §8b）理由充分。
- risk_level / phases / packages `[agate-tests, agate-scripts, ci-workflow]` / domains `[backend]` 声明合理，与 P0-brief 范围一致。
- capability_requirements 三态正确：本地可用（available）+ 真 Windows 环境 supplementable（GitHub Actions matrix），无 GAP。

## 待确认清单评审

- `[NO_NEED_CONFIRM]` 标注正确，无阻塞 `[NEED_CONFIRM]` 残留（已 grep 核实）。SUGGEST-1（harness shim）与 SUGGEST-2（扫描范围 tests/ 全树、不含 scripts/、CI 阻断）判定合理，与范围声明一致。

## 观察项（非阻塞，供主 Agent 知悉）

- BDD-16 示例清单中 `agate-debt-check.sh` 实为 `check-debt.sh`（§8 已正确）。纯示例命名瑕疵，41 例计数与二值判定不受影响，无需返修；可在 P2 设计时顺手校准。

---

## 证据摘要

- 已复核：全仓 .bats grep 裸 python3 = 25 文件（unit 21 与 §8 清单逐文件一致 / int 2 / reg 2）；agate-debt-check.bats = 0 处 python3。
- 已复核：产品脚本裸 python3 17 文件 68 处（与 §8 一致）；RC 桶和 13+41+17+3+2+1=77，与 77 真失败一致。
- 已复核：check-tdd-red.bats 15 处 `PATH="/usr/bin:/bin"`；install-hook.bats 2 处 `[[ -L ]]`；agate-next-card.bats L104 逻辑路径 /tmp；agate-extract-context.sh L128 `bc`。
- 已复核：BDD-1..29 编号连续（grep `^#### BDD-` 29 条无跳号）；无中间态；无 `[NEED_CONFIRM]` 残留；无行首 `- PASS`/`- FAIL` 格式。
