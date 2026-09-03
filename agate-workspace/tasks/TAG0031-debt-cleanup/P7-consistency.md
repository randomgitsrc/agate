---
phase: P7
task_id: TAG0031
type: consistency
parent: P2-design.md
trace_id: TAG0031-P7-20260904
status: draft
created: 2026-09-04
agent: consistency-reviewer
blocker_count: 0
deviation_count: 0
deviation_critical_count: 0
design_gap_count: 1
design_gap_reviewed_count: 1
code_map_new_files_count: 0
code_map_reviewed_count: 0
---

# P7-consistency.md — TAG0031-debt-cleanup 一致性交叉检查

对照 P0-P6.5 产出做跨文件一致性审查。范围：7 条历史遗留 DEBT（DEBT0002/0003/0004/0007/0016/
0017/0018）三簇实现（version-mgmt / test-isolation / gate-robustness）+ debt 登记收尾。

## 1. DESIGN_GAP 配对（硬门槛）

P4-implementation-version-mgmt.md:31 逐字转抄：

> [DESIGN_GAP: P2-design.md §1.3 R1 未明确说明如何在满足"install-offline.py 不能顶层无条件
> import agate_common"约束的同时，让 `test_offline_bundle_roundtrip.py` 的
> `install_module.compute_sha256 is agate_common.compute_sha256` identity 断言成立——实现中
> 采用"先探测 yaml 可用性，可用才顺带模块级导入并暴露 compute_sha256 引用，不可用保持 None"的
> 折中方案，`_ensure_agate_common` 独立重新探测不复用该结果，两条路径互不干扰，12 个测试函数
> （含该 identity 断言）全部转绿验证方案自洽。]

[DESIGN_GAP_REVIEWED: 接受此实现细化。核对依据——① P2-design.md §1.3 R1「缓解设计」段落原文
明确了 `_ensure_agate_common(bundle_dir, manifest)` 的三步引导逻辑（探测 yaml → 不可用则内联
hashlib 校验 pyyaml 组件 → pip install 前置校验），但**确实未提及**模块级 `compute_sha256`
暴露方式，即 P4 implementer 指出的 gap 属实，不是编造的空白。② P2 R1 唯一的字面不变量约束是
"install-offline.py 不能顶层无条件 `from agate_common import compute_sha256`"（避免未装 pyyaml
的机器在 `verify_checksums` 阶段崩溃）——P4 实现的"先探测 yaml 可用性、可用才模块级顺带导入"
写法未违反这条约束：`import yaml` 探测失败时模块级引用保持 `None`，不会触发 agate_common 的
硬依赖崩溃；`_ensure_agate_common` 内部路径完全独立重新探测，不与模块级暴露耦合，也未削弱 R1
"先校验后安装"的核心顺序保证。③ 折中方案的必要性来自测试断言本身（identity 检查）
而非实现随意发明——`test_offline_bundle_roundtrip.py` 要求 `install_module.compute_sha256 is
agate_common.compute_sha256`，这一断言在"完全不做模块级导入"的方案下无法成立（找不到
`install_module.compute_sha256` 这个属性），P4 选择的路径是在不违反 R1 约束前提下满足测试契约
的合理最小改动。④ 影响面：P4-implementation-version-mgmt.md「测试结果」节显示本簇 12 个目标
测试函数（含该 identity 断言）+ 既有 32 项回归全部转绿（44 passed），P6.5 judge 独立复核
（bdd-02.log）对 R1 相关的"pyyaml 引导 + checksum 不匹配前置拒绝"2 个机制细节用例重跑确认
PASS，未发现该折中方案引入新的行为偏离。结论：这是设计文档遗漏细节、实现在授权边界内做出的
合理补全，不构成偏离设计意图的 DEVIATION，不阻断。]

## 2. SCOPE+ 闭环核对

P1-requirements.md「P2 阶段 [SCOPE+] 回补」节（L361-376）：

> [BASELINE_CHANGE: P2 architect 设计阶段发现 P1 未预见的必须处理项——`compute_sha256` 迁移到
> `agate_common.py` 后，`install-offline.py` 的离线 bootstrap 前提被打破……]

> [SCOPE_RESOLVED: P2-design.md §1.3 R1「缓解设计」已给出闭环方案——`install-offline.py` 新增
> `_ensure_agate_common(bundle_dir, manifest)` 引导函数……方案已经 plan-eng-review 第 2 轮
> approved（复核确认顺序缺口已消除 + 回归覆盖已补齐 checksum 不匹配场景用例）。]

闭环链条逐环核对：
- **发现**：P2-design.md §1.3 R1（L75-89）"发现"段落——`compute_sha256` 迁移后
  `install-offline.py` 引导流程出现 pyyaml 组件"先 pip install 后 checksum 校验"顺序缺口，
  与 P1 的 `[BASELINE_CHANGE]` 转抄内容一致。
- **回补**：P1-requirements.md `[BASELINE_CHANGE]` 已记录主 Agent 核实事实基础（
  `install-offline.py` L228/L237 执行顺序、`agate_common.py` L30-34 硬依赖、
  `agate-pack-offline.py` L129 pyyaml 组件 manifest 结构），已批准纳入实现范围。
- **解决**：P2-design.md §1.3 R1「缓解设计」（L87）给出 `_ensure_agate_common` 三步方案；
  P4-implementation-version-mgmt.md 改动清单第 3 行确认按此方案落地（"新增
  `_ensure_agate_common(bundle_dir, manifest)` 引导函数……引导失败时抛 `RuntimeError`，`main()`
  捕获并 stderr 输出 + `return 1`"），与 P2 设计一致，仅第 1 节 DESIGN_GAP 描述的模块级暴露
  细节属方案内的合理补全。
- **测试覆盖**：P2-design.md §1.3 R1「回归覆盖」段落（L89）声明的 2 项用例（yaml 不可导入时
  引导路径可用 / checksum 不匹配时 pip install 前置拒绝且 `subprocess.run` 未被调用）已在
  P4-implementation-version-mgmt.md「测试结果」节确认落地（44 passed，含本簇 12 个目标测试
  函数），P6-acceptance.md BDD-2 证据行明确标注"含 R1 pyyaml 引导前置校验缓解方案的 2 个机制
  细节用例（bootstrap 引导 + checksum 不匹配前置拒绝）"，P6.5-judge-verdict.md BDD-2 独立重跑
  3 项全 PASS（bdd-02.log）。

结论：**SCOPE+ 闭环完整**（发现→回补→解决→测试覆盖四环均有具体文件/行号锚点，无缺口）。

## 3. 跨文件一致性核对

### 3.1 P2 packages 与实际改动文件

P2-design.md frontmatter 声明 `packages: [agate-scripts, agate-tests, agate-docs]`
（P2-design.md:11，与 P1-requirements.md:13 一致）。对照 git 实际提交记录：

- P3 commit `233a4f3`（TDD 红灯）：新增/修改 `agate/tests/unit/test_agate_common.py` /
  `test_agate_install_uninstall.py` / `test_agate_pack_offline.py` / `test_check_gate.py` /
  `test_debt_registry_closure.py` / `test_install_offline.py` +
  `agate/tests/regression/test_offline_bundle_roundtrip.py`（`agate-tests` 域）。
- P4 commit `9faf19a`（实现）：`M agate/scripts/agate_common.py` / `agate-install.py` /
  `agate-pack-offline.py` / `check-gate.py` / `install-offline.py`（`agate-scripts` 域）+
  `M agate/UPGRADING.md` / `agate/scripts/README.md`（`agate-docs` 域）+
  `M agate-workspace/debt/tech-debt.md`（登记收尾，workspace 数据面，不计入 packages 三域但
  P2 §1.1「跨簇共享写入」表已单独声明此文件，非未声明改动）。

三域（scripts/tests/docs）均有实际改动落地，P2 声明与实际改动一致，无遗漏域、无越界域。

### 3.2 P1 15 条 BDD 与 P6 15 条 PASS 语义对应抽查（≥3 条，非仅数量核对）

- **BDD-7**（P1-requirements.md L274-280，DEBT0007 登记闭合）：P1 原文要求"`status` 改为
  `closed`，追加 `closed_at` 与 closure 说明，evidence 追加指向 `e2357fc`/
  `test_p2_6f_...` 与本任务 BDD-6 验证记录，登记格式与既有 DEBT0005/DEBT0006 closed 条目一致"
  ——P6-acceptance.md BDD-7 行逐字对应同一描述（status closed / closed_at / evidence 指向
  e2357fc 与 BDD-6 / 格式对齐 DEBT0005/6），语义完全对应，非空泛复述。
- **BDD-9**（P1-requirements.md L290-295，非标准两级嵌套边界流）：P1 原文"`task_dir` 与
  `workspace` 的层级关系非标准两级嵌套（如经由 `.agate.env` 的 `AGATE_WORKSPACE=` 覆盖）……
  解析结果仍与 `resolve_workspace` 权威函数结果一致，不产出错误/不存在的路径"——P6-acceptance.md
  BDD-9 行"非标准两级嵌套场景（经 `.agate.env` `AGATE_WORKSPACE=` 覆盖）下 `gate_p4` 路径解析仍
  与 `resolve_workspace` 一致，不产出错误/不存在路径"，字面场景描述与判定条件均对应，非仅编号
  和 PASS 状态对齐。
- **BDD-14**（P1-requirements.md L328-335，同类扫描回归拦截）：P1 原文要求"新增至少 2 条 open
  状态 DEBT 条目（分别对应①`task_dir`类②标题字符串子串判定类两类），evidence 指向本次 P1
  同类扫描结论"——P6-acceptance.md BDD-14 行"新增 DEBT0028（`dirname(dirname(...))` 类别 A 非
  本体 2 处实例）与 DEBT0029（`check-gate.py:881` gate_p2 骨架声明标题子串判定，风险高于
  DEBT0017 本体）两条条目，均 `status: open`，evidence 指向本任务 P1「同类扫描」节第 3/4 小节
  结论"，与 P1 的①②两类要求逐一对应（DEBT0028↔①、DEBT0029↔②），非张冠李戴。经
  `agate-workspace/debt/tech-debt.md` 实际条目核对（L998-1049），DEBT0028/0029 均确实存在且
  status 为 open，与 P6 描述一致。

抽查结论：3 条 BDD 的 P1 原始条件与 P6-acceptance.md 对应行描述语义一致，非仅数量凑对
（15 BDD ↔ 15 PASS，frontmatter `pass: 15 / fail: 0` 与 P1-requirements.md BDD 编号 BDD-1~
BDD-15 一一对应，P6-acceptance.md「交叉核对」节已自行声明"15 条 BDD 逐条实跑，PASS=15，
FAIL=0，与 P1-requirements.md 全部 BDD 编号一一对应，无遗漏、无重复"）。P6.5-judge-verdict.md
以 fresh context 独立复核 15/15 全部 PASS（criteria_total: 15, criteria_passed: 15,
status: passed），对 BDD-13 额外补跑 P2-design.md 固化的 `gate_commands.P5` 全量套件（而非仅
证据文件里的单条测试），进一步加强了"全量既有测试无新增失败"表述的验证强度，两轮独立验收
（P6 verifier + P6.5 judge）结论一致，未发现证据造假或过时迹象。

### 3.3 P4 实现路径与 P2 §4 files_to_read / §1.1 改动点表吻合性

逐簇核对 P4-implementation-*.md「改动清单」与 P2-design.md §1.1 改动点表：

- **簇 A（version-mgmt）**：P4-implementation-version-mgmt.md 改动清单列出的 6 个文件
  （`agate_common.py`/`agate-pack-offline.py`/`install-offline.py`/`agate-install.py`/
  `UPGRADING.md`/`scripts/README.md`）与 P2-design.md §1.1「簇 A」表（L27-38）声明的改动点
  文件集合逐一对应，无额外改动文件。`compute_sha256` 插入位置（"紧邻 `resolve_workspace` 定义
  之后"）与 P2 表格"紧邻 `resolve_workspace`（L551-580）之后新增"描述一致。`_find_references`
  返回二元组的设计与 P2 表格"返回值改为 `(refs, hit_limit)` 二元组"描述一致。R1
  `_ensure_agate_common` 引导函数与 P2 §1.3 R1 缓解设计一致（第 1 节已核对细化点）。
- **簇 B（test-isolation）**：P4-implementation-test-isolation.md 明确"本簇本次无任何代码/文档
  改动"，与 P2-design.md §1.1「簇 B」表"（无代码改动）"描述一致，未触碰
  `check-pruning.py`/`debt/tech-debt.md`（登记闭合动作按 P2 §1.1「跨簇共享写入」表划归主 Agent
  收尾处理），无越界改动。
- **簇 C（gate-robustness）**：P4-implementation-gate-robustness.md 唯一改动文件
  `check-gate.py`，与 P2-design.md §1.1「簇 C」表一致；resolve_workspace import 追加位置
  （原 L42-46 import 块）、gate_p4 CODE-MAP 路径改造（原 L985-987）、「新增文件核对表」整行
  正则判定（原 L990，改为 `re.search(r"^##\s+新增文件核对表", ..., re.MULTILINE)`）、4 个
  fail-closed 消费点（gate_p1 L687 / gate_p6 L1084 / gate_p7 L1144, L1238）均与 P2 表格逐行
  对应。P4 实现额外新增 `_reader_missing(fn)` 辅助函数（判定 `fn.__module__ == "agate_common"`
  而非 P2 设想的"模块级哨兵 `_AGATE_COMMON_MISSING = object()`"比较）——P4-implementation-
  gate-robustness.md「DEBT0018」节（L48-57）已给出理由（白盒测试 monkeypatch 重新绑定函数名
  对象场景下一次性哨兵标记无法感知后续重新绑定，身份判定更稳健），属于实现层面的等价替代手段
  （判定目标一致：区分"真实 agate_common 实现"与"降级/替换实现"），未改变 P2 declared 的行为
  契约（fail-closed 触发条件、错误信息内容、`return 1`），不构成偏离设计意图的实质性问题，
  P4-review.md 已 approved（backend 域评审）未标注该点为 CRITICAL。
- **无未声明的额外改动**：三簇改动清单与 P2 §1.1 表格逐项核对完毕，git 实际 diff（P4 commit
  `9faf19a` 的 `M` 行）与三份 P4-implementation-*.md 声明的改动文件集合完全重合，未发现 P2
  未声明、P4 却改动的文件。

### 3.4 debt/tech-debt.md 闭合与新登记与 P1 BDD-7/14/15 吻合性

`agate-workspace/debt/tech-debt.md` 实际核对（L40-1049）：
- DEBT0002（L40-56）：`status: closed`，closure evidence 指向本次 TAG0031-P4 commit，与
  BDD-1/2/15 要求一致。
- DEBT0003（L75-90）：`status: closed`，closure evidence 指向 UPGRADING.md/README.md 信任
  边界文案，与 BDD-3/15 一致。
- DEBT0004（L106-121）：`status: closed`，closure evidence 指向 `_find_references` 二元组
  改造，与 BDD-4/5/15 一致。
- DEBT0007（L187-…）：`status: closed`，与 BDD-7 一致。
- DEBT0016/0017/0018（L604-…）：均 `status: closed`，与 BDD-8/9/10/11/12/13/15 一致。
- DEBT0028/0029（L998-1049）：均 `status: open`，evidence 指向 P1「同类扫描」节，与 BDD-14
  一致。

7 条闭合（DEBT0002/3/4/7/16/17/18）+ 2 条新登记（DEBT0028/29）与 P1-requirements.md BDD-7/14/15
的要求逐条吻合，无缺失、无多记、无状态错标。

## 4. 未决项清零核对

- P1-requirements.md「待确认清单」（L352-359）：`[NO_NEED_CONFIRM]`，全文 grep 无残留行首
  `[NEED_CONFIRM]` 标记（仅 DEBT0003 签名 vs 文档取舍用 `[SUGGEST]` 标记，非 NEED_CONFIRM，
  且已给出明确倾向不阻塞推进）。
- P6-acceptance.md：全文 grep 无 `[BLOCKER]`/`[DEVIATION-CRITICAL]` 标记，frontmatter
  `pass: 15 / fail: 0`，全部为客观 PASS/FAIL 二值判定，无残留 NEED_CONFIRM。
- P4-review.md：`status: approved`（L8），正文结论"approved"（L214），无 rejected 记录。

未决项清零核对通过。

## 5. CODE-MAP 核对

`agate-workspace/agents/CODE-MAP.md` 描述对象为 `agate/` 协议本体自身五大模块
（phase-cards/execution-roles/review-roles/scripts/templates/rules），新增文件同步义务
针对这些模块下的**生产文件**。本次核对：

- P4 commit `9faf19a` 实际 `git show --name-status` 结果：`agate/scripts/*.py`
  （`agate_common.py`/`agate-install.py`/`agate-pack-offline.py`/`check-gate.py`/
  `install-offline.py`）与 `agate/UPGRADING.md`/`agate/scripts/README.md` 均为 `M`（修改），
  无 `A`（新增）标记。
- 该 commit 中标记为 `A`（新增）的文件仅为任务 workspace 过程性产出
  （`P4-dispatch-context-implementer-*.md`/`P4-progress-*.md`/`P4-review.md`/
  `P4-implementation*.md`）与 SELF-GATE 产出（`docs/reviews/agate-alignment-review-
  2026-09-04-TAG0031.md` 及其 progress 文件），均不属于 CODE-MAP.md 追踪的五大模块范畴
  （不是 phase-cards/execution-roles/review-roles/scripts/templates/rules 下的生产文件）。
- P3 commit `233a4f3` 新增的 3 个测试文件（`test_offline_bundle_roundtrip.py`/
  `test_agate_install_uninstall.py`/`test_debt_registry_closure.py`）属于 `agate/tests/`
  测试域，同样不在 CODE-MAP.md 追踪范畴内（CODE-MAP.md 描述的是协议本体架构，非测试文件清单）。

[CODE_MAP_SYNC: 本次三簇 P4 实现（agate/scripts/*.py + agate/UPGRADING.md +
agate/scripts/README.md）经 `git show --name-status 9faf19a` 核实全部为 `M` 修改类型，无 `A`
新增类型，P4-implementation.md「新增文件核对表」声明"本次无新增文件……无需逐行填表"属实，
CODE-MAP.md 新增文件核对表义务不适用，`code_map_new_files_count: 0` / `code_map_reviewed_count: 0`
准确反映本次实际状态。]

## 6. 结论

- BLOCKER=0：第 1 节 DESIGN_GAP 已完整配对转抄 + REVIEWED 判定（接受，理由已给出），无遗留
  未配对的 DESIGN_GAP。
- CRITICAL=0：第 3 节四项跨文件一致性核查（P2 packages↔实际改动、P1 BDD↔P6 PASS 语义抽查、
  P4 实现路径↔P2 设计、debt 登记↔BDD-7/14/15）均引用了具体文件/行号锚点，未发现偏离设计意图
  的实质性问题。
- SCOPE+ 闭环：第 2 节确认发现→回补→解决→测试覆盖四环完整，`[SCOPE_RESOLVED]` 有效。
- 未决项清零：第 4 节确认 P1 无残留 `[NEED_CONFIRM]`，P6 无 `[BLOCKER]`/`[DEVIATION-CRITICAL]`。
- CODE-MAP：第 5 节确认本次无新增生产文件，核对表义务不适用，判定属实。

TAG0031-debt-cleanup 三簇实现与 P1-P6.5 全部产出一致，无跨文件偏离，具备进入 P8 发布阶段的
一致性前提。
