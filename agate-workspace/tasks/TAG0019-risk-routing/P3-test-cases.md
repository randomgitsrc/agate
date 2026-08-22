---
phase: P3
task_id: TAG0019-risk-routing
type: test-cases
parent: P2-design.md
trace_id: TAG0019-P3-20260821
status: draft
created: 2026-08-21
agent: test-designer
---

# TAG0019 风险分路由 — P3 测试用例设计（TDD）

> 状态标记：`[PROD_NOT_TOUCHED]`。本设计仅映射测试用例，测试代码由后续 implementer/test-code subagent 产出。
> 基线：P1-requirements.md 15 条 BDD（BDD-1..15）approved；P2-design.md 方案 B（check-routing 独立脚本 import check-pruning 同源函数）。
> 口径：**TDD 红灯先行**——以下用例在实现（agate-risk-score.py / check-routing.py / 注册点）尚未落地时执行必须失败（import 失败 / 断言失败 = 真红灯）。

## 测试资产总览

- `test_code_dir:` `agate/tests/unit/`（worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0019/agate/tests/unit/`）
- 测试运行：`python3 -m pytest -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp`（`/tmp` 只读，遵守 agate 测试平台无关原则——不裸 `python3`、不用 `/tmp`、不用 POSIX symlink 字面）
- 分组：BDD-1..5 → 算分脚本测试文件 `test_agate_risk_score.py`；BDD-6..10 → `test_check_routing.py`；BDD-11..15 → 文档断言/平台类（`test_docs_assertions.py` + 既有文件扩展 + 平台扫描）

> 平台类测试（BDD-13/15）部分由既有测试资产承担：`test_check_platform_assumptions.py`（既有 R1-R5 扫描器测试）+ `check-platform-assumptions.py`（gate 层）覆盖 BDD-13；BDD-15 由 `check-protocol-consistency.py --strict-errors-only`（0 ERROR）在 P5 gate 走查。测试文件层补充文档条文可 grep 断言，供评审层（BDD-11/14）静态验证。

## 15 BDD 用例映射（紧凑表格）

### 算分脚本测试文件（BDD-1..5）→ `unit/test_agate_risk_score.py`

| BDD 编号 | 测试文件 | 用例意图（≤2 行） |
|----------|----------|--------------------|
| BDD-1 | `unit/test_agate_risk_score.py` | 对含非空暂存区改动的任务目录算分，断言输出含 `risk_score`（数值）、`tier`（thin/standard/full 之一）、逐信号证据行且与 `git diff --cached` 内容一致（任一缺失/不一致 FAIL） |
| BDD-2 | `unit/test_agate_risk_score.py` | 构造 A 类（`agate/**/*.md` / `agate/scripts/*.py`）与 B 类（仅 tests/配置）两类 fixture 暂存区；断言 A 文件类型信号 high、B low，且 A 信号位评分严格高于 B（分级不可区分 FAIL） |
| BDD-3 | `unit/test_agate_risk_score.py` | 含 `auth/`/`permission`/`data-model` 等敏感关键词路径 → 敏感路径信号 high + 输出 `domain: security` 标注；无关键词路径 → 无该标注（误报/漏报 FAIL） |
| BDD-4 | `unit/test_agate_risk_score.py` | fixture 源码文件（任务产出排除后，与 `_staged_source_count` 同口径）>5 → 规模信号 high；对拍断言 check-routing 规模判定与 check-pruning 的 P7 裁剪条件（>5 拦截）不矛盾（口径不一致 FAIL） |
| BDD-5 | `unit/test_agate_risk_score.py` | 改动文件被其他模块经 grep 反向引用（或 scope 声明 backend/frontend/mcp/security）→ 输出域映射标注 + 影响面信号升级 high；无反向引用则不升级（二值可判） |

### check-routing 测试文件（BDD-6..10）→ `unit/test_check_routing.py`

| BDD 编号 | 测试文件 | 用例意图（≤2 行） |
|----------|----------|--------------------|
| BDD-6 | `unit/test_check_routing.py` | `ceremony: thin/standard/full` 过 frontmatter schema 校验 + 字段可读；非三值（`light`/`THIN`）被拦截（frontmatter-check exit 1 + check-routing 非法值兜底 exit 1） |
| BDD-7 | `unit/test_check_routing.py` | `ceremony: thin` 缺四要素任一（coupling_checklist 流式 / 跳过风险: / P5/P6 保留 / 显式 thin 声明）→ check-routing exit 1 回退 standard；四要素齐全才 exit 0（P5/P6 情形同时验证 check-pruning 检查 3/5 双闸兜底） |
| BDD-8 | `unit/test_check_routing.py` | P1 frontmatter 无 ceremony 字段（存量/新任务）→ check-routing exit 0 按 standard 处理不拦截；断言无任何路径把"无声明"解释为 thin/full |
| BDD-9 | `unit/test_check_routing.py` | 同一暂存区：算分 tier=standard/full 而声明 thin → exit 1（单向 fail-closed）；反向（算分 thin 而声明 standard/full）→ exit 0 不拦截 |
| BDD-10 | `unit/test_check_routing.py` | 对同一 P1 fixture 输入，check-routing 与 check-pruning 判定一致（对拍）；importlib 上下文 agate_common/check-pruning 可导入性断言（防双层模块 sys.path 依赖静默退化），无独立重写/分叉 |

### 文档断言 / 平台 / 既有扩展（BDD-11..15）

| BDD 编号 | 测试文件 | 用例意图（≤2 行） |
|----------|----------|--------------------|
| BDD-11 | `unit/test_docs_assertions.py` | requirements-review 文档条文可 grep 断言：「风险分级/裁剪声明（risk_level/ceremony/phases）vs 暂存区 diff 证据」核对项存在；该核对项缺失时评审不得 approved（文档条文 grep） |
| BDD-12 | `unit/test_docs_assertions.py` | P1 卡 ceremony 机制文档可提取 M3 验收锚四要素：①评审轮数指标定义 ②真实发现数指标定义 ③TAG0018 基线（17 非阻塞 + 1 真实发现且机械可抓）④不达标→回滚 standard 决策规则（任一缺失 FAIL，grep 条文） |
| BDD-13 | `unit/test_check_platform_assumptions.py`（既有扩展）+ `check-platform-assumptions.py`（gate） | 对本任务新增/修改 `agate/scripts/*.py` 变更文件集跑 R1-R5 扫描 0 命中；新脚本 git 调用经 `run_git`、路径对 Windows 分隔符与 CRLF 鲁棒（任何 R1-R5 命中 FAIL）。测试文件自身不硬编码 /tmp/裸 python3/POSIX symlink |
| BDD-14 | `unit/test_docs_assertions.py` | 声明 `ceremony: full`/tier=full 文档条文可 grep：P2 强制独立 plan-eng-review + cso（security 域）+ P7 不可裁（role-system/review-mapping/P2 卡/P4 卡四处同步声明；full→phases 含 P7 核对项） |
| BDD-15 | `unit/test_docs_assertions.py` + `check-protocol-consistency.py --strict-errors-only` | 文档同步断言：scripts/README 工具清单、tests/README 用例映射、agate-summary `_DRIFT_SCRIPTS`、WORKFLOW gate 表均含新机制条目；consistency 注册表含 ceremony/新脚本关键词（0 ERROR，任一未同步 FAIL） |

## 既有测试扩展（跟随 ceremony 注册链，非新增独立文件）

| 关联 BDD | 测试文件 | 扩展内容 |
|----------|----------|----------|
| BDD-6（三节点） | `unit/test_check_frontmatter.py` | ceremony enums 非法值（`light`/`THIN`）拦截补充 |
| BDD-6（三节点） | `unit/test_agate_md_field_get.py` | ceremony 字段读取补充（frontmatter 优先 + 正文正则回退） |
| BDD-7/9（I2） | `integration/test_pre_commit_hook.py` | pre-commit-gate 2j.1 挂载 check-routing 的 hook 链用例 |
| BDD-6/7 | `conftest.py`（fixture helper） | 写 fixture P1 时注入合法 ceremony 字段 | 

## check-routing 分支覆盖清单（P2 §3 映射，落到 `test_check_routing.py`）

- 正向：thin 四要素全过 → exit 0；不声明 → exit 0；standard/full 声明 → exit 0（更保守合法）。
- 拦截：缺任一要素 → exit 1（BDD-7）；声明薄于算分（tier=standard/full）→ exit 1（BDD-9）；**算分异常（run_git 失败 / agate_common 不可导入 → `git_ok: false`）+ thin 声明 → exit 1（fail-closed）**。
- 边界：P1 缺失 → exit 2（对齐 check-pruning exit 2 语义）；非法 ceremony 值 → exit 1。
- 对拍：check-routing vs check-pruning 判定一致（BDD-10）。

## 质量门槛自检

- [x] 15 条 BDD（BDD-1..15）1:1 全覆盖，无挑选
- [x] 测试文件与 BDD 分组对应（1..5 算分 / 6..10 路由 / 11..15 文档+平台）
- [x] 紧凑三列表格（BDD 编号 | 测试文件 | 用例意图 ≤2 行），全文 ≤250 行
- [x] 声明 `test_code_dir:`（`agate/tests/unit/`）
- [x] 测试平台无关（无裸 python3 / 无 /tmp / 无 POSIX symlink 字面）
- [x] UI 任务不适用（P2 `ui_affected: false`）

## 待实现文件清单（供 P4 实现导航，test-design 职责边界 + 对应测试入口）

- `agate/scripts/agate-risk-score.py`（新）→ `test_agate_risk_score.py`
- `agate/scripts/check-routing.py`（新）→ `test_check_routing.py`
- ceremony 注册点（frontmatter-check / md-field-get / pre-commit-gate 2j.1 / summary / consistency / README）→ 既有测试扩展
- 文档条文（P1 卡 / requirements-review / analyst / task-files / role-system / review-mapping / P2 卡 / P4 卡 / WORKFLOW / CONTEXT / tests/README）→ `test_docs_assertions.py`
