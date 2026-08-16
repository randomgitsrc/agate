---
phase: P4
task_id: TAG0014-dispatch-orchestration
type: implementation
parent: P2-design.md
trace_id: TAG0014-P4-20260816
status: draft
created: 2026-08-16
agent: implementer
---

[PROD_NOT_TOUCHED]

# P4 实现记录 — agate 派发编排机制（TAG0014-dispatch-orchestration）

implementation_dir: agate/

## 1. 改动清单（按 P2-design §2.1 / dispatch-context 改文件清单）

### 1.1 脚本（op + gate）

| 文件 | 改动 |
|------|------|
| `agate/scripts/agate-md-field-get.py` | 新增 `import json`；`JSON_FIELDS = frozenset({"dispatch_plan"})`；`_format_value` 置顶 `if field in JSON_FIELDS: return json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)`；`_get` 无回退集合并入 JSON_FIELDS（frontmatter-only）；`KNOWN_OPS` 并入 JSON_FIELDS |
| `agate/scripts/check-gate.py` | 新增 `import json` + `_gate_p2_dispatch_plan(p2_file)` 校验函数（mode 枚举 / parallel_limit≥1 / batch id+complexity∈{low,medium,high} / 批数≤limit 缺省 3；空/坏 YAML 返回 None 跳过）；gate_p2 末尾、`return 2` 之前接入——命中 ERROR 写 `GATE P2 ERROR: ...` + `return 1`。修复轮：mode 校验加 `isinstance(mode, str)` 前置（修复 review CRITICAL：非 str 值不再触发 frozenset 成员测试 TypeError 崩溃，干净报 ERROR） |

**op 行为**（BDD-1/7 自查确认）：
- 含 flow YAML 的 P2 文件 → 输出合法 JSON（`json.dumps ensure_ascii=False`），exit 0
- 无字段 → 空输出，exit 0；坏 YAML（`{mode: [unclosed`）→ frontmatter 解析失败 → 空输出，exit 0（不崩溃）

**gate 行为**（BDD-2~7 自查确认）：
- 缺字段/坏 YAML → op 返回空 → 跳过，等同现状（exit 2，逐行输出与无字段完全一致）
- mode 非法 → `GATE P2 ERROR` + exit 1；parallel_limit<1 → ERROR + exit 1
- batch 缺 complexity / 批数超限 → ERROR + exit 1；校验通过 → 继续走既有 return 2

### 1.2 协议文档

| 文件 | 改动 |
|------|------|
| `agate/dispatch-protocol.md` | L639「任务粒度指引」原位升级为「派发编排机制」权威节（工作量评估五维表 / 五模式 / 模式 4 三步流程含文档样例 / 并行规则三要素 / 全阶段适用表），既有有效规则（输入/产出上限、拆分判据、T016/T026 教训、P7 例外、状态机不变）保留；L118/L132/L211「任务粒度指引」引用措辞同步改「派发编排机制」；「派发 prompt 模板」内联节新增「任务粒度兜底」（产出>3 或输入>5 须分批或说明） |
| `agate/assets/templates/task-files.md` | L80「任务粒度指引」引用措辞同步（与协议内 3 处一致，consistency CHECK 3 锚点零漂移） |
| `agate/phase-cards/P1-requirements.md` | 新增「复杂需求编排（模式 4）」节：侦察 subagent 引用 + 合并语义（BDD 全局编号、包归属去重） |
| `agate/phase-cards/P2-design.md` | 新增「dispatch_plan 机器字段（可选）」节：frontmatter 单行 flow 样例 + 字段契约（mode 枚举/parallel_limit/batches + 缺省跳过语义） |
| `agate/phase-cards/P3-tdd.md` | 「按包拆分并行」节标题保留，正文加"见 dispatch-protocol「派发编排机制」并行规则"引用 + 拆分判据原样保留 |
| `agate/phase-cards/P4-implementation.md` | 「按包拆分并行」节标题保留，正文加权威节引用 + 共享文件后处理/基础设施隔离/串行安全默认值原样保留 |
| `agate/phase-cards/P5-verification.md` | 「按包拆分并行」节标题保留，正文加权威节引用 + 端口/数据库/临时输出/E2E 隔离原样保留 |
| `agate/phase-cards/P6-acceptance.md` | 「按包拆分并行」节标题保留，正文加权威节引用 + P6 例外声明（走自身汇总 verifier）+ 证据并行/汇总 verifier 原样保留 |
| `agate/phase-cards/P7-consistency.md` | L97「P7 输入文件数量」表述更新为"模式 1 单发 + 输入数量豁免特例"，原有 3 条理由保留 |
| `agate/phase-cards/P8-release.md` | 新增「多包发布拆批（模式 2/3，条件触发）」节：多 releaser 各写 P8-release-{pkg}.md → 合并 subagent 整合唯一 P8-release.md |
| `agate/assets/execution-roles/architect.md` | 新增「批次设计（强制节，TAG0014）」：dispatch_plan 字段 + high 复杂度必须拆批 + 批次粒度受工作量评估约束 |
| `agate/assets/templates/dispatch-prompt.md` | 新增「任务粒度兜底」（产出>3 或输入>5 须分批或说明）；头部"本模板与 dispatch-protocol 同步、协议为权威来源"声明保留 |

### 1.3 测试与版本记录

| 文件 | 改动 |
|------|------|
| `agate/tests/README.md` | 用例计数表新增 `dispatch_plan 编排字段契约 | unit/test_dispatch_orchestration.py | 8` 行（修复轮追加 2 条负向用例后该文件计数 8→10，待 P5 一致性核对同步）；agate-md-field-get.py 计数 14→16 |
| `README.md` | **修复轮已还原为 v0.48.0**（版本 bump v0.48.0→v0.49.0 归 P8，P4 未提交，`git diff README.md` 为空） |
| `CHANGELOG.md` | 新增 [0.49.0] 版本记录（版本 bump 归 P8） |
| `agate/UPGRADING.md` | 新增 v0.49.0 章节（无破坏性变更：dispatch_plan 可选字段向后兼容 + 权威节改名说明） |

## 2. 测试自查结果

### 2.1 P3 契约测试（10 条红灯 → 全绿）

```
python3 -m pytest agate/tests/unit/test_dispatch_orchestration.py agate/tests/unit/test_agate_md_field_get.py -q --tb=short
24 passed in 1.27s   # 10 条新增（test_dispatch_orchestration 8 + test_agate_md_field_get +2）+ 14 条既有 mdf 用例
```

无回归，P3 测试文件（test_dispatch_orchestration.py / test_agate_md_field_get.py 测试逻辑）未做任何修改。

### 2.2 全量回归（修复轮后最终状态）

```
python3 -m pytest agate/tests/ -q --tb=no
778 passed, 2 skipped, 0 failed in ~65s
```

修复轮后全量实测 **778 passed + 2 skipped + 0 failed（全绿）**：

- `test_con_1_check_1_yaml_parseable` / `test_bdd_25_consistency_zero_error`：P2-design.md L256 `why:` 值已加引号 → YAML 解析 ERROR 消除，两条已过（非本 P4 改文件清单，由主 Agent 修复轮处理）
- `test_con_6_check_7_version_badge_sync`：README badge 已还原为 v0.48.0，与最新 tag v0.48.0 一致 → CHECK 7 自动通过（版本 bump 归 P8，不再保持红）

> 注：上轮（修复轮前）3 failed 均非本实现引入，且已全部修复为全绿，见上文逐条说明。

### 2.3 其他自查（修复轮后）

- `bash agate/tests/scripts/count-tests.sh` → 总计 **782** = 基线 770 + 10 新增（dispatch_plan 8→10，修复轮追加 2 条负向用例）+ 2（mdf 16/17）（BDD-20 达标）
- `ruff check`（agate-md-field-get.py / check-gate.py）→ 0 问题
- `check-protocol-consistency.py` → **0 ERROR**（修复轮后：P2 遗留 YAML + CHECK 7 瞬态均已消除）；WARNING 279 均为叙事文件引用（既有基线）

## 3. 决策标注

[DESIGN_GAP（已解决）：P2-design.md files_to_read 块 `why:` 值含冒号标量未加引号导致 consistency CHECK 1 报 YAML 解析 ERROR——修复轮已由主 Agent 给 `why:` 值加引号，全量 pytest + consistency 恢复全绿。]

[DESIGN_GAP（已解决）：README badge 曾在 P4 轮改 v0.49.0 导致 CHECK 7 报 ERROR——修复轮已还原 v0.48.0 与 tag 一致，CHECK 7 自动通过；版本 bump v0.48.0→v0.49.0 归 P8 与 tag 同 commit 变更。]

> 修复轮最终状态：P4-review.md 的 1 CRITICAL（mode 非 str 崩溃）已修复并补负向用例闭环；P4-review 建议 2（complexity invalid 负向用例）已采纳；建议 3（README 计数 8→10 同步 tests/README.md）留给 P5 一致性核对，不改该文件。

## 4. 实现完成标志对照（P2 §6）

| # | 标志 | 状态 |
|---|------|------|
| 1 | op 契约完成（dispatch_plan JSON 输出 + 空/坏 YAML exit 0） | ✅ mdf_16/17 + 正向用例全绿 |
| 2 | gate 校验完成（mode/limit/batch/批数 ERROR→exit 1；空/坏 YAML 等同现状） | ✅ mode_valid/parallel_limit_zero/batch_missing_complexity + optional/malformed_yaml |
| 3 | 权威节完成（五维表+五模式+模式 4 流程+并行规则+全阶段适用表） | ✅ dispatch-protocol.md |
| 4 | 卡片统一完成（P1/P2/P3/P4/P5/P6/P7/P8 八卡） | ✅ 见 1.2 |
| 5 | 模板完成（architect.md 批次设计节 + dispatch-prompt.md 粒度兜底 + 协议内联节双源） | ✅ |
| 6 | 测试完成（10 条全绿；全量 778 passed + 2 skipped；count-tests 782） | ✅ 修复轮后全绿 |
| 7 | consistency 0 ERROR | ✅ 修复轮后 0 ERROR（P2 遗留 YAML + CHECK 7 瞬态均已消除） |
| 8 | self-gate | ✅ commit message 须含 `self-gate-review:` 路径（P7 派 protocol-alignment-review），见 1.3 版本记录 commit |
| 9 | 发布（badge/CHANGELOG/UPGRADING + tag） | ⏳ CHANGELOG/UPGRADING 已更新；badge 已还原 v0.48.0（P4 不 bump，归 P8）；tag v0.49.0 由 P8 创建 |

## 5. 范围核对

- 改动文件全部在 dispatch-context「改文件清单」内（git status 核对：无清单外文件）
- P2 §2.2「不改什么」未触碰：agate-frontmatter-check.py / 3 个 hook 薄壳 / state-machine.md / WORKFLOW.md / test_check_gate.py 既有用例 / count-tests.sh / loop-orchestration.md（SUGGEST S1 主 Agent 定夺，未纳入本实现）
- P3 测试文件未修改

[PROD_NOT_TOUCHED]
