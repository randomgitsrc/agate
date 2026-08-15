---
phase: P2
task_id: TAG0011-test-migration
type: review
parent: P2-design.md
trace_id: TAG0011-P2-review-20260815
status: approved
created: 2026-08-15
agent: plan-eng-review
---

# P2 方案工程评审 — agate 测试框架迁移（bats → pytest）

> 评审范围：P2-design.md（candidate_count: 9，4 组决策点，本版含 BLOCKER-1 修订）+ P1-requirements.md（12 BDD + 17 批基线）。
> 评审方式：只评审不改；关键假设（bats `$output` 合并流语义、pytest `-k`/`-m`/`--collect-only` 行为、
> conftest sys.path 插入、脚本流归属）均已本地实测验证（python3 3.12.3 + pytest 9.0.3 + bats 1.10.0）。
> 本版为 **rejected → approved 的修订复核**：BLOCKER-1 已修正，N1-N5 已吸收，另附 5 项新的非阻塞观察（m1-m5）。

## 结论

**status: approved — 0 个 BLOCKER（阻塞级）**

方案总体架构正确：A1 同目录替换 + B1 单根 conftest + C1 显式 marker + D1 count-tests 改写的四组决策
权衡充分、选择理由成立；批次粒度（17 批 + 专项批子批表 ≤32 @test/子批）直接回应了用户"任务过重→卡死"的
约束，双跑对照（BDD-6）+ 命名契约 + files_to_read 精度控制良好。上一轮唯一 BLOCKER（`$output` 合并流语义
被映射为 stdout-only）已在本版 §3.1/§3.2/§5 全面修正并经实测复核，5 项非阻塞意见（N1-N5）全部吸收进设计，
上一轮 2 项测试缺口均已落地（批次 1 合并流回归锁；conftest 自检部分落地，见 m3）。

---

## 架构问题（阻塞级）

### BLOCKER-1（已解决，复核通过）：`$output` 合并流语义修正

上一轮 BLOCKER-1 指出 §3.2 将 bats `$output`（stdout+stderr 合并）错误映射为 stdout-only。本版修订复核：

- **§3.1** `CommandResult(returncode, stdout, stderr)` 新增 `output` = `stdout + stderr` 合并流 `property`
  （实现为 `self.stdout + self.stderr`），并明确"仅当断言明确只关心单流才用 `.stdout`/`.stderr`"。
- **§3.2 映射表**：所有 `$output` 行统一改为合并流——子串断言 `assert "X" in result.output`、反向断言
  `assert "X" not in result.output`（N5 补行）、精确/空判断 `assert result.output.strip() == "X"` /
  `assert result.output == ""`，并显式标注"空/非空判断必须基于合并流，映射为 stdout-only 会静默反转语义"。
- **§3.2 流语义迁移规则** 三条强制规则：(a) 空/非空判断一律合并流；(b) stderr 特定内容先判流归属
  （内容确定写 stderr → `.stderr`，不确定 → 合并流 `.output`）；(c) `2>&1` 显式合并模式直接用 `.output`。
- **26 处 `[ -z "$output" ]` 覆盖核对（实测）**：grep 全树 = 26 处，与设计分布逐项一致——
  批次 1（gate-missing-cmds/evidence-consistency/changelog-unreleased 各 1）、批次 2（state-yaml-check +
  json-get + retreat-state 各 1 + state-get 2 + read-p5 2 = 7）、批次 5（debt-check 5）、批次 7
  （frontmatter 2 + retrospective 3 = 5）、批次 12（commit-msg-self-gate 1）、批次 16
  （check-platform-assumptions 4）、批次 17 退役（check-windows-smoke 1，不迁移）。**零遗漏**。
- **流归属事实核对（实测）**：`GATE ...:`（check-gate.py 全数 sys.stderr.write）、`ENV_BASELINE:`、
  角色文件不存在（agate-render-dispatch-prompt.py L93/102/106/112/125）、`GATE PRUNING`、`GATE PROVENANCE`、
  `GATE DEBT WARNING` 均写 stderr——设计 §3.2 流归属列与脚本真实行为一致；全树 `$stderr`/`--separate-stderr`
  引用 = 0 处（映射表"无 $stderr 引用"声明成立）。
- **批次 1 回归锁落地**：补 1 条"脚本写 stderr + 断言 `$output` 合并流"正例（EB.8 等价物：
  stderr 输出 + `assert "X" in result.output`），作为合并流语义回归锁（上一轮测试缺口 #2）。
- **§7.2 回归风险表**：已新增 BLOCKER-1 对应风险行及缓解（合并流 `.output` + 流语义规则 + 批次 1 回归锁）。

BLOCKER-1 判定：**已解决**。

---

## 架构问题（非阻塞）

上一轮 N1-N5 均已在设计正文吸收（复核确认），不再列为未决问题：

- **N1（已吸收）**：§5 批次 8 备注行显式声明 `-k` 非穷举分区——`PG.P2REVIEW`/`bdd-14`/`bdd-28`/`bdd-29`
  由"8 子批完成后整文件跑"兜底（实测 4 个 @test 真实存在，check-gate.bats L2023/2034/2044/2075），
  P4 勿误判 `-k` 覆盖 124 全数。
- **N2（已吸收）**：同备注行声明 8b `-k "bdd1"` 与 8d `test_bdd_1_*` 重叠无害，子批 = 增量验证非严格分区。
- **N3（已吸收）**：count-tests.sh 改写显式传 `"$TESTS_DIR"` 绝对路径（§3.5），不依赖 testpaths 相对 rootdir 隐式收集。
- **N4（已吸收）**：映射表补"命令替换直接捕获"行（`output=$(...)` → `run_cli(...).output` + 剥尾部换行
  注意），实测 RP.16（L126）与 ci-gate-backstop.bats 6 处 CRLF 归一化捕获均属此类（后者见 m4）。
- **N5（已吸收）**：映射表补 `[[ "$output" != *"X"* ]]` 反向断言行（`assert "X" not in result.output`），
  实测 RP.18 等十余处反向断言存在。

### 本轮新增非阻塞观察（m1-m5，不阻塞，P4 知悉即可）

- **m1：`.output` 拼接丢失流间交错顺序**。bats `$output` 是两流按实时写入交错合并，pytest 侧分离捕获后
  `stdout + stderr` 拼接为"先全部 stdout 再全部 stderr"。对子串/空判断（覆盖全部 26 处空判断 + 已知 stderr
  源断言）顺序无关，但理论上多流混合输出的精确 `==` 等值断言顺序可能与 bats 不同——设计 §3.2 已建议"不确定
  时用合并流"，已知精确等值用例均单流，风险低。P4 若遇混合流精确比较，按流归属拆分断言。
- **m2：count-tests.sh 缺 pytest 时静默回落 0**。§3.5 实现 `2>/dev/null` 抑制 pytest 报错 + `|| true` 兜底
  → python 存在但 pytest 缺失时输出"总计：0"而非 D1 宣称的"fail-closed 明确报错"（仅 python 本身缺失才报错）。
  功能无缺口（`≥749` 守卫仍会触发），建议 P4 把"pytest 未安装"分支的 stderr 提示保留（去掉 `2>/dev/null`
  或改 `2>&1` 提取）。
- **m3：批次 0 conftest 自检未显式覆盖"子目录 `from conftest import` 纯函数"**。test_sanity.py 自检
  agate_root/task_dir/git_repo（fixture 路线），但"子目录 test 模块 `from conftest import` 纯函数可 import"
  这一前提（上一轮测试缺口 #1）未显式落断言。minimal_validation 已实测 prepend 模式成立，风险低；建议批次 0
  在任一子目录用例加 1 条 `from conftest import add_frontmatter_field` 断言锁 pytest 版本漂移。
- **m4：ci-gate-backstop.bats 的 CRLF 归一化重捕获模式未显式列映射**。L74/90/107/141/203/229
  `output=$(printf '%s' "$output" | tr -d '\r')` 是"合并流再剥 CRLF"而非普通捕获，N4 行只覆盖捕获形态。
  批次 9 迁移时对应 `result.output.replace("\r", "")` 归一化，建议 P4 知悉（不影响合并流主规则）。
- **m5：bats 空输出边界**。脚本仅输出单个 `\n` 时 bats `$output`=""（行剥离）而 pytest `.output`="\n"
  （非空）。26 处空判断目标脚本均无此形态，规则（合并流空判断）本身正确；P4 若遇"仅空白输出"边界，用
  `.strip() == ""` 形态更稳。

---

## 8 项评审关注点逐项结论

1. **候选方案权衡（通过）**：9 候选 / 4 决策点，每个否决候选都有真实缺陷（A2 破碎映射、A3 双份维护、
   B2 重复样板、C2 自研 plugin 违依赖约束、D2 断引用链），选择理由与 P1 DECIDED/SUGGEST 一致，非稻草人。
2. **批次迁移设计可行性（通过）**：17 批对齐 P1 表，@test 数逐批核对无误（合计 749）；批次 8（146，实测
   check-gate 124 + p1-review 9 + p5-diff 13）拆 8 子批 ≤32、批次 13（56）拆 3 子批、批次 6/9/10 均拆子批，
   每子批有独立可执行 `-k` 验证命令 + 原 bats 对照——粒度直接满足"1 轮可完成"约束。N1/N2 已以显式备注落地。
3. **bats → pytest 语义映射正确性（通过，BLOCKER-1 复核）**：`run`/`$status`/`$output` 映射修正为合并流
   语义（§3.1 + §3.2 规则，见上）；`setup`→fixture、BATS_TEST_TMPDIR→tmp_path、mktemp→tmp_path/xxx、
   skip→skipif、@test 编号保留均正确。26 处空判断零遗漏。
4. **fixture 策略（通过，含 1 项验证确认）**：单根 conftest ~350 行镜像三 bash 文件职责合理；`from
   conftest import ...` 依赖 pytest prepend 模式——已实测确认在子目录 test 模块可 import。batch 0 一次性
   交付 + 后续追加的过渡约定可防"单文件过大"。子目录 import 的显式断言建议见 m3。
5. **gate_commands 可执行性（通过）**：P3 `pytest -q` / P5 `-q --tb=no` 在本机 pytest 9.0.3 可跑；
   `-m windows_smoke` / `-k` / `--collect-only` 计数提取均已实测验证；P5_consistency/ruff/scan/ci 辅助
   gate 命令合理。
6. **Windows 冒烟 marker 方案（通过）**：C1 显式 `@pytest.mark.windows_smoke` + pyproject markers 注册
   消除 PytestUnknownMarkWarning（minimal_validation 已实测）；打标清单（PLATFORM_KEYWORDS_RE 关键词 +
   每文件第 1 个 @test）与 check-windows-smoke.sh L32 语义一致；Linux 全量不受 marker 影响。
7. **files_to_read 精度（通过）**：13 项含行号范围（check-windows-smoke.sh:32、check-gate.py:188-710、
   pre-commit-hook.bats:1-70 等），全部是迁移必需参照，无上下文爆炸风险。
8. **风险缓解（通过）**：§7.1 卡死风险四类缓解（子批 ≤32、files_to_read 精化、单文件串行 + timeout、
   命名契约自校验）直接对应用户约束；§7.2 回归风险覆盖语义偏差（双跑 + bdd 编号）、BLOCKER-1 合并流
   语义（本轮已补行）、扫描器自触发、R2.4 flaky、打标遗漏、ruff 新违规、文档引用链断裂等。

---

## 测试缺口

- **合并流回归锁（已落地）**：批次 1 补 EB.8 等价"stderr 输出 + 合并流断言"正例。✓
- **conftest 子目录 import 断言（部分落地）**：batch 0 test_sanity.py 覆盖 agate_root/task_dir/git_repo
  fixture 加载，未显式覆盖子目录 `from conftest import` 纯函数（见 m3）。建议批次 0 补 1 条，不阻塞。

---

## 锁定决策（本次评审确认成立的技术方向）

- A1 同目录 `test_*.py` 替换 + 保留目录树；迁移期双跑对照，收尾删 .bats。
- B1 单根 `tests/conftest.py`（会话级 + 函数级 fixture + 纯函数，`from conftest import` 已实测可用）。
- C1 显式 `@pytest.mark.windows_smoke`（pyproject 注册 markers）+ CI Windows `-m windows_smoke`。
- D1 count-tests.sh 改写为 `pytest --collect-only` 提取收集数（正则 `[0-9]+ tests? collected` 已验证
  匹配 "1 test collected" / "N tests collected"）。
- **合并流契约（BLOCKER-1 修正后确认）**：`CommandResult.output = stdout + stderr`；空/非空断言一律
  基于合并流；stderr 特定内容先判流归属；精确等值前 `.strip()`。
- gate_commands P3/P5 用 pytest；`ui_affected: false` 无需 P5_e2e。
- 批次粒度方案（17 批 + 子批 ≤32）作为 P4 执行契约保留。

---

## 返回主 Agent

- **status: approved**
- **BLOCKER 数：0**
- **摘要**：上一轮 rejected 的唯一 BLOCKER（`$output` 合并流语义误映射为 stdout-only）已彻底修正——
  §3.1 新增 `.output` 合并流属性、§3.2 映射表与三条流语义规则统一基于合并流、26 处 `[ -z "$output" ]`
  分布经实测零遗漏、流归属事实（GATE/ENV_BASELINE 等写 stderr）经实测一致、批次 1 回归锁与 §7.2 风险行
  已补。N1-N5 全部吸收进正文。方案总体架构与批次粒度设计满足用户"任务过重→卡死"约束。另附 5 项非阻塞
  观察（m1-m5：合并流拼接顺序、count-tests 缺 pytest 静默回落、conftest 子目录 import 断言、CRLF 归一化
  重捕获模式、空输出边界），P4 知悉即可，不阻塞推进。
