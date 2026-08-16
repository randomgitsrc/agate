---
phase: P2
task_id: TAG0014-dispatch-orchestration
type: review
parent: P2-design.md
trace_id: TAG0014-P2-20260816
status: approved
created: 2026-08-16
agent: plan-eng-review
---

[PROD_NOT_TOUCHED]

# P2-review — 工程经理评审（plan-eng-review）

> 评审对象：`P2-design.md`（candidate_count: 3，agent: architect）
> 契约基准：approved plan `agate-workspace/plans/agate-dispatch-orchestration-20260815.md`
> 需求基线：`P1-requirements.md`（22 BDD，[NO_NEED_CONFIRM]）
> 方法：实读核对 architect 对现状代码的描述 + 实际运行验证关键假设 + 契约/BDD 逐条对照

## 结论

**Status: approved**

- 架构问题（阻塞级）：0
- 架构问题（非阻塞）：2
- 测试缺口：1
- 22 BDD 全覆盖：是
- 契约核对：与 approved plan 字段契约完全一致（含 1 处合法扩展，见锁定决策 2）
- 实读核对：全部一致，无 architect 误述

---

## 架构问题（阻塞级）

无。

---

## 架构问题（非阻塞）

1. **`agate-md-field-get.py` 的 op 层测试计数口径：design 声称"新增 op 层测试 2 条（S2）"与 `agate/tests/README.md` 更新为"14→16"一致，但 plan Task 1 的 Files 仅列 test_dispatch_orchestration.py。这是 plan 外扩展（P1 SUGGEST S2），design 已显式标注为 S2 落地，非偏离。**（信息性，无行动）
2. **BDD-1 的 op 层 JSON 输出含 `ensure_ascii=False`**：design §3.1 步骤 3 用 `json.dumps(value, ensure_ascii=False)`。与 minimal_validation ② 实测一致（输出合法 JSON）。无问题。
3. **`gate_commands.P3` 只跑 2 个文件**（test_dispatch_orchestration.py + test_agate_md_field_get.py）：P3 是 TDD 红灯阶段，全量 pytest 应留在 P5（已含）。合理。

---

## 测试缺口

- **8 条 dispatch_plan 用例 + 2 条 op 层用例 = 10 条新用例，design §3.5 已声明**（改造前基线 770 实测 + 10 → 目标 ≥780）。BDD-19 只要求 8 条（test_dispatch_orchestration.py），BDD-20 要求 count ≥ 基线 + 新增（design 用"≥ 基线 + 10"）。P6 验收须按"基线 770 + 实际新增"口径核对，design 表述正确。
- **未发现实质测试缺口**。8 条用例与 plan Task 1 完全对应（5 正向 + 3 负向），且 op 层 2 条补 S2。唯一需 P6 注意：BDD-5 双子场景（batch 缺 complexity + complexity 非法值）须各验一次（design §4 BDD-5 已标注"P6 分双子场景各验一次"）——已覆盖。

---

## 锁定决策

1. **方案 A1（读取路径）**：新增 op `dispatch_plan` + `_md_field_get` 子进程读取 + `json.dumps` 分支——与 pass/blocker_count 同路径，符合 plan N8/N9 修复。
2. **模式枚举含 `recon-then-split` 时 batches 不校验**：design §3.1 gate 步骤 3 把"batches 不校验"从 plan 的"模式 1/5"扩展为"single/serial/recon-then-split"（含模式 4）。**这是对 plan 的合法扩展而非偏离**——recon-then-split 是先理解后拆，设计时无预定义批次，校验 batches 无意义；且 BDD-4/BDD-5/BDD-6 均未要求模式 4 校验 batches。理由自洽。
3. **校验插入点**：candidate_count 之后、return 2 之前（check-gate.py L323 附近），ERROR 时 return 1 覆盖 return 2——与代码结构吻合（L366 return 2 实测）。
4. **frontmatter-only 无正则回退**：与 change_type/regression_pass 同语义，防正文伪造——正确（设计 §3.1 步骤 4）。

---

## 协议契约核对（dispatch_plan 字段契约 vs approved plan）

| 契约点 | plan 定义 | design 落地 | 判定 |
|---|---|---|---|
| 序列化格式 | frontmatter 单行 flow YAML | §1 A1 + §3.1 | ✅ 一致 |
| mode 枚举 | single/static-batch/parallel/recon-then-split/serial | §3.1 gate 步骤 3 | ✅ 一致 |
| 读取机制 | 新增 op + `_md_field_get` 子进程（N8，不复用 `_frontmatter_field`） | §1 A1 明确"不复用 `_frontmatter_field`" | ✅ 一致 |
| KNOWN_OPS 注册 | 须注册否则 exit 2 静默跳过（N9） | §3.1 步骤 5 | ✅ 一致 |
| json.dumps 输出 | 新增 dict→JSON 分支（N9） | §3.1 步骤 3 | ✅ 一致 |
| 不入 frontmatter-check schema | 完全不入（B3 方案 c） | §2.2 明确"不改" | ✅ 一致 |
| 向后兼容 | 缺字段等同现状 | §3.1 gate 步骤 2（空→跳过） | ✅ 一致 |
| P2 gate 校验规则 | mode 合法 / parallel_limit≥1 / batch id+complexity / batch 数≤parallel_limit 默认 3 | §3.1 gate 步骤 3 逐条 | ✅ 一致 |

---

## self-gate 流程核对（BDD-22）

- design §3.6 覆盖：commit message 含 `self-gate-review:` 路径 + P7 派发 protocol-alignment-review + 产出 `docs/reviews/agate-alignment-review-{date}.md`。与 SELF-GATE.md（commit-msg-self-gate.sh 触发面：`agate/*.md` + `agate/scripts/*.py` + phase-cards）一致。
- 本任务触发面确认：Modify 面含 `agate/*.md`（dispatch-protocol、7 张阶段卡、architect.md、dispatch-prompt.md）+ `agate/scripts/*.py`（check-gate.py、agate-md-field-get.py）→ 全部命中 self-gate 触发。✅

---

## 实读核对（architect 对现状代码的描述 vs 实际代码）

### agate-md-field-get.py
- **"yaml 解析 L124"**：✅ `_read_frontmatter` L116-126，`yaml.safe_load` 在 L124。
- **"`_format_value` L129-142"**：✅ 函数 L129-142，dict 值走 `return str(value)`（Python repr 单引号）→ I4（须加 json.dumps 分支）成立。
- **"KNOWN_OPS L194-198"**：✅ L194-198。`dispatch_plan` 未注册 → `main()` L204-206 exit 2 "unknown op"。**实测确认**：`env FILE=P2-design.md .../agate-md-field-get.py dispatch_plan` → `agate-md-field-get: unknown op dispatch_plan` + EXIT=2。N9 成立。
- **"frontmatter-only 无正文回退"**：✅ `_get` L183-191 有 NO_FALLBACK 集合分支；坏 YAML → `_read_frontmatter` L123-126 捕获 YAMLError 返回 None → `_get` 走 NO_FALLBACK 返回空。设计步骤 4 把 JSON_FIELDS 并入该分支，合理。

### check-gate.py
- **"`_md_field_get` L115"**：✅ L115-129 子进程模式（env FILE + sys.executable），失败回退 ""。
- **"candidate_count L301-307"**：✅ gate_p2 L291-366，candidate_count 正则逐行 L301-307；`_frontmatter_field` L106-112 是单行 sed——设计 A2 说"不可用"判断正确。
- **"return 2 需主 Agent 自判"**：✅ L365-366。design 注"dispatch_plan ERROR 时 return 1 覆盖"与代码结构吻合（在 return 2 之前 return 1）。
- **"校验插在 candidate_count 之后、return 2 之前"**：✅ 结构吻合。

### 其他
- **frontmatter-check P2 schema**：✅ 实测（见 minimal_validation ⑤）。P2 schema L55-66 仅 candidate_count/packages/domains/ui_affected，无 dispatch_plan。
- **pre-commit-gate.py L313-316**：✅ L312-317 对 P1/P2/P6/P7 产物跑 frontmatter schema 校验——I2"入 schema 会误拦 dict"成立（types 用 str 时 isinstance 对 dict 失败）。
- **conftest / test 文件 fixture 行号**：conftest.py L213-227（add_p2_candidate_count L218 / add_p2_review L223）✅；test_check_gate.py L220-272（_write_p2_design L220 / _run_gate 模式）✅；test_agate_md_field_get.py L10-16（_run_mdf L10）✅。
- **P4-implementation.md L94-117**：✅ 共享文件/隔离全组/串行默认值均在。
- **count-tests 基线 770**：✅ 实测 `count-tests.sh` 输出"总计：770 个测试用例"。

### minimal_validation 复现（实跑验证）
- ① 未注册 op → exit 2：✅ 实测。
- ② yaml round-trip：✅ 实测（dict → json.dumps 合法 JSON，round-trip 成功）。
- ③ dict 当前走 str() repr：✅ 实测（repr 单引号非 JSON）。
- ④ 坏 YAML → 不崩溃：✅ 实测（yaml.safe_load 抛 YAMLError，_read_frontmatter 返回 None）。
- ⑤ frontmatter-check 不误拦：✅ 实测含 dispatch_plan 的 P2 文件 exit 0。
- ⑥ consistency 0 ERROR：✅ 实测（仅 279 WARNING 叙事引用）。
- ⑦ count-tests 基线 770：✅ 实测。

---

## BDD 覆盖核对（22 条全量）

| BDD | design 落点 | 判定 |
|---|---|---|
| 1 op 输出合法 JSON + mode 枚举 | §3.1 + BDD 映射 | ✅ |
| 2 缺字段等同现状 | §3.1 空跳过 + test 断言 | ✅ |
| 3 mode 非法拦截 | §3.1 gate 步骤 3 | ✅ |
| 4 parallel_limit<1 拦截 | §3.1 gate 步骤 3 | ✅ |
| 5 batch 缺 complexity/非法 | §3.1 + 双子场景标注 | ✅ |
| 6 批数超限拦截 | §3.1 gate 步骤 3 | ✅ |
| 7 YAML 解析失败不误拦 | §3.1 op + gate 双层 | ✅ |
| 8 工作量评估五维表 | §3.2 | ✅ |
| 9 五模式定义 | §3.2 | ✅ |
| 10 模式 4 三步 + 样例 | §3.2 | ✅ |
| 11 并行规则三要素 | §3.2 | ✅ |
| 12 全阶段适用表 + P2/P7/P8 特例 | §3.2 | ✅ |
| 13 四卡引用 + 保留约束 | §3.3 + C1 | ✅ |
| 14 P7 表述更新 | §3.3 | ✅ |
| 15 P1 卡片侦察引用 | §3.3 | ✅ |
| 16 P8 拆批 + 合并 | §3.3 | ✅ |
| 17 architect 批次强制节 | §3.4 | ✅ |
| 18 dispatch-prompt 双源同步 | §3.4 | ✅ |
| 19 8 条用例 | §3.1 | ✅ |
| 20 全量 + 不漂移 | §3.5 | ✅ |
| 21 consistency 0 ERROR | §3.5 + ⑥ | ✅ |
| 22 self-gate 流程 | §3.6 | ✅ |

---

## 结论

P2-design.md 数据流清晰（op 读取 → gate 校验 → 缺字段向后兼容），错误边界完整（空/坏 YAML/mode 非法/parallel_limit 非法/batch 非法/超限各归各路径），接口契约与 approved plan 完全一致，测试策略覆盖 22 BDD，多方案探索三维度各 ≥2 候选且理由自洽，实现就绪度达标，minimal_validation 实读复现全部 confirmed。无阻塞问题，**approve**。
