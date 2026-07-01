# 各阶段产出文件模板

> 每个任务目录 docs/tasks/{Txxx}/ 下的标准文件

## 通用 Header（所有文件必须有）
```yaml
---
phase: {P1-P8}
task_id: {Txxx}
type: {problems|design|review|test-cases|...}
parent: {上一阶段文件名，P1 时是外部需求来源}
trace_id: {Txxx}-{Pn}-{YYYYMMDD}
status: {draft|approved|rejected|done}
created: {YYYY-MM-DD}
agent: {main|analyst|architect|reviewer|test-designer|implementer|verifier|vision-analyst}
---

> **agent 字段由主 Agent 在派发 prompt Header 里填好**（角色 ID），subagent 复制即可，不要自行推断。缺字段 → `check-p6-provenance.sh` 缺字段 WARNING（exit 2 不阻塞，向后兼容）。
```

## 各阶段文件清单

| 阶段 | 文件 | 关键 Header 字段 |
|------|------|-----------------|
| P0 | P0-brief.md | 主 Agent 亲自填写（非 subagent 产出）：task/known_risks/executor_env/env_constraints/pruning_tendency |
| P1 | P1-requirements.md | 含 BDD 验收条件 + `packages:` `domains:` 初判 + 裁剪说明；无未决 `[NEED_CONFIRM]`（门槛）|
| P2 | P2-design.md | **必须声明 `packages:` `domains:` `ui_affected:` `gate_commands:` `files_to_read:` `env_constraints:`；确认/细化 P0-brief 的 `env_constraints`** |
| P2 | P2-review.md | **status: approved/rejected**（门槛）|
| P3 | P3-test-cases.md | 声明 `test_code_dir: {实际路径}`；每用例对应一条 BDD；UI 任务含 E2E 用例 |
| P3 | {test_code_dir}/ | 测试代码目录（项目自定义，如 `backend/tests/`）|
| P4 | P4-implementation.md | 声明 `implementation_dir: {实际路径}` |
| P4 | {implementation_dir}/ | 代码目录（项目自定义，如 `src/` 或 `backend/app/`）|
| P5 | P5-test-results/unit.md | 标注 `failed: N`（仅供参考，gate 以主 Agent 跑 pytest 为准）|
| P5 | P5-test-results/e2e.md | UI 任务必须：Playwright 实跑结果 + 截图路径。须含 `status: passed` 字段（hook 检查） |
| P6 | P6-acceptance.md | P1 每条 BDD 有实跑结果（**只允许 PASS 或 FAIL，不允许中间态**）；UI 条件含截图；无未决 `[NEED_CONFIRM]`（门槛）|
| P7 | P7-consistency.md | 无 `[BLOCKER]` 标记（门槛）|
| P8 | P8-release.md | 每个 package 的版本 bump + CHANGELOG + 临时资源清单 |

### 辅助文件（非阶段产出，由主 Agent 或 subagent 过程产出）

| 文件 | 产出者 | 说明 |
|------|--------|------|
| P{N}-dispatch-context.md | 主 Agent | 派发前查证的客观信息（环境状态、URL、选择器等），信息量 >10 行或需复用时落盘 |
| P{N}-progress.md | subagent | 分阶段落盘的中间产物（每步追加写入），空返回时供主 Agent 判断 subagent 是否动过 |
| PAUSED-resolution.md | 主 Agent | PAUSED 恢复时人工决策内容 |
| HANDOVER.md | 主 Agent | 环境受限时交接给其他 Agent |

## 路径占位符

P3/P4 的代码路径由产出文件显式声明，不使用固定目录名：

- P3-test-cases.md 必须声明：`test_code_dir: backend/tests/`
- P4-implementation.md 必须声明：`implementation_dir: {项目实际源码路径}`

派发 prompt 引用这些声明而非固定路径，避免模板硬编码项目特定路径。

## 门槛字段说明

主 Agent 不依赖 subagent 产出文件字段判定门槛，而是**亲自跑命令验证**：

- P1 → 主 Agent 确认有 BDD 条件 + 无未决 `[NEED_CONFIRM]`
- P2-review.md `status` → subagent 评审产出的结论
- P3 → 主 Agent 跑 `scripts/check-tdd-red.sh` 验证（UI 任务查 Playwright 用例存在）
- P5 → 主 Agent 跑 `pytest -q` 验证（UI 任务实跑 Playwright/E2E）
- P6 → 主 Agent 确认 P1 每条 BDD 有实跑结果 + 无未决 `[NEED_CONFIRM]`
- P7 → 主 Agent grep `[BLOCKER]` 验证
- P8 → 主 Agent 为每个 package 跑发布检查命令验证

## P0-brief.md 结构（主 Agent 任务简报，亲自填写）

P0-brief 是主 Agent 作为 PM 在派发任何 subagent 之前写的判断文件。
不是 subagent 的产出，是主 Agent 的职责——把产品需求翻译为工程视角、注入风险判断。

**核心原则：开发全程在测试环境进行。** 生产环境不在 agate 的编排范围内——
生产部署属于发布步骤（`make publish` 之后的运维范畴），不属于 P1-P8。

```yaml
## P0-brief.md
task: "一句话描述任务（工程视角，不是产品语言）。若写不出一句话 → 任务太大，考虑拆分（见 dispatch-protocol.md「任务粒度指引」）"

known_risks:
  - "涉及数据 schema 变更（需要在测试环境充分验证迁移逻辑）"
  - "跨越 3 个改动端（API+CLI+客户端）"
  - "修改权限/认证逻辑（安全敏感）"

executor_env:
  platform: "opencode"          # opencode | claude-code | codex | claude-project
  has_task_tool: true           # 能否派发 subagent（false = 单 Agent 模式）
  has_local_runtime: true       # 有完整本地环境（npm/python/playwright/测试框架）
  network: "full"               # full | restricted（restricted 时 npm install 等可能失败）

env_constraints:
  debug_env: "项目的测试/调试环境命令或路径（从项目约定读取，如 CLAUDE.md）"
  # 注意：不写 prod_env。生产环境不在开发流程范围内。
  # 若 subagent 接触了生产环境（[PROD_TOUCHED]），说明它走错路了，立即停止。

pruning_tendency: "保守 — 涉及 schema 变更，建议走完整 P1-P8"
# 或："激进 — 单文件 typo 修复，直接做"

phase_hint: [P1, P2, P3, P4, P5, P6, P8]  # 主 Agent 预判；P3 默认保留，跳过须有理由
# has_task_tool=false 时所有阶段由主 Agent 直接执行，subagent 派发步骤自动降级
```

**P0-brief 的核心价值**：每个 subagent 都在独立上下文里启动，不知道项目约定和环境约束。
P0-brief 是把这些约束注入每次派发的桥梁——所有 subagent 的 prompt 都要包含 P0-brief.md 路径。

### 扩展章节（项目自定）

5 字段是 agate 协议要求的最小集。项目可根据需要扩展。

**常见扩展类别（实战中验证有效，仅作参考不强制）**：
- `user_decisions`：PM 视角记录已与用户确认的关键决策
- `coordination`：与其他任务的依赖和时序约束
- `验收基线`：PM 视角的可量化验收条件
- 其他按需扩展

注意：
- 这些是**参考类别**而非模板。具体格式和内容由项目决定。
- agate 不维护具体模板——避免偏向单一项目实践。
- 项目可自由选择不用上述任何类别。

## P1-requirements.md 结构（需求基线）

```markdown
## 1. 需求复述
（用结构化语言重写原始需求）

## 2. 隐含需求识别
- 隐含需求 A：... | 为什么必须：...
- 隐含需求 B：... | 为什么必须：...

## 3. BDD 验收条件
- AC1: Given ... When ... Then ...
- AC2: Given ... When ... Then ...

## 4. 待确认清单
- [NEED_CONFIRM] 问题描述 + 几种可能的理解

## 5. 裁剪说明
risk_level: low                      # low=纯UI/文案/配置 | medium=业务逻辑/API/数据 | high=安全/权限/数据迁移/生产环境
phases: [P1,P2,P4,P5,P6,P8]
- 跳过 P3 理由：...
- 跳过 P7 理由：...
# override（裁剪声明与实际执行不一致时回写，见 dispatch-protocol.md P2.9）
# override: P2 retained (reason: 主 Agent 判断需要方案设计)

## 6. 范围声明
packages: [pkg-a]
domains: [backend, frontend]

## 7. 能力需求声明
capability_requirements:
  - need: browser-vision
    why: P6 验收需截图验证 UI 交互
    available:
      - playwright-vision skill（已注入）
    status: available          # available / supplementable / GAP

  - need: external-network
    why: 验证 CDN 加载
    available: []
    status: GAP
    [CAPABILITY_GAP: external-network] — 建议降级为 mock 验证

## SCOPE+ 增补区（后续阶段回写）
- [SCOPE+ from P2] 新需求 + 对应 BDD
```

**能力三态说明**：
- `available`：环境中已有（Agent 自身 / 已注入 skill / 可调用外部 agent）→ 自走
- `supplementable`：当前没有但有已知补充路径 → 在 prompt 里指引，不阻塞
- `GAP`：无任何补充路径 → 标 `[CAPABILITY_GAP]`，主 Agent 暂停问人

判断 status 时**先看环境**（已注入的 skills、可调用的 agent），不只看主力模型自身能力。

## P2-design.md 结构（方案设计）

```markdown
## 1. 改动方案
（影响域、设计、数据流、异常路径）

## 2. 范围声明（必填）
packages: [pkg-a, pkg-b]
domains: [backend, frontend]
ui_affected: false

## 3. gate 命令（在 P2 固化，后续不得修改）
gate_commands:
  P5: "pytest -q --tb=no"          # 紧凑输出模式（见下）
  P5_e2e: "playwright test --reporter=line tests/e2e/"   # ui_affected: true 时必填
  P6: "pytest -q --tb=no tests/acceptance/"
# 紧凑输出要求：gate 命令只供主 Agent 判断「过没过」，须用工具的汇总/安静模式
# （pytest --tb=no / cargo --quiet / dotnet --verbosity quiet / vitest --reporter=dot
#  / go test | tail -30 / mvn -q），保留通过失败汇总+失败清单，去掉逐项 traceback。
# 工具无紧凑模式时用 shell 兜底：命令 2>&1 | tail -N（语言无关）。

## 4. 实现导航（必填，控制 P4 implementer 上下文体量）
# v0.6 澄清：这是"实现导航"不是"实现计划"——
# 不列每步做什么（那是步骤脚本，superpowers writing-plans 的模型）
# 列实现时需要参考的文件 + 为什么（资源地图，agate P2-P4 模型）
files_to_read:
  - path: backend/services/auth.py
    why: 复用现有 hash_password 模式
  - path: backend/models.py:120-180      # 大文件标行号范围，只读相关片段
    why: User 模型定义，新字段加在这里
# 只列实现确实需要参考的文件，不是相关文件大杂烩。
# P4 implementer 按此清单读取，不在项目里乱窜——这是上下文不爆炸的关键。

## 5. 最小验证（若方案依赖浏览器行为/安全模型/外部系统行为）
minimal_validation:
  assumption: "srcdoc iframe 继承父页面 CSP"
  method: "10 行 HTML 测试页验证 srcdoc 的 CSP 行为"
  result: "confirmed | refuted | not_needed"
  note: "（验证过程和结论简述）"
# 纯代码逻辑不需要最小验证（TDD 覆盖），项目内已有模式不需要（已有先例）。
# T019 教训：srcdoc 方案到 P6 才发现不可行，P2 用 10 行 HTML 5 分钟就能发现。

## 6. env_constraints（确认/细化 P0-brief）
env_constraints:
  debug_env: "..."
  isolation_check: "..."

## SCOPE+ 增补区（后续阶段回写）
- [SCOPE+ from P4] ...
```

## P6-acceptance.md 结构（验收报告）

```markdown
## 验收结果（逐条对照 P1 的 BDD）

**BDD 二值规则**：每条 BDD 结果只允许 PASS 或 FAIL，不允许"⚠️ 调整/跳过/覆盖"等中间态。
**截图质量标准**：操作类 BDD 截图必须互不相同（md5 去重），查询类 BDD 可不截图（断言值是唯一证据）。

### AC1: entry 不指定过期时间默认 15 天
- PASS 创建 entry 不填过期 → 实测 15 天后过期（p6-ac1.png）
- PASS MCP publish_files 不传 expires → 实测同样生效

### AC2: ...
- FAIL 实测结果与预期不符：... → 触发回 P4

## 验收小结
BDD 通过 X/Y，UI 截图 N 张，NEED_CONFIRM M 个
```

**证据引用格式**：每条 PASS 结果必须在括号内引用对应证据文件路径（相对于 `P6-evidence/` 目录）。示例：`- PASS B01: ... (p6-b01.png)`。hook 会检查引用路径必须真实存在。无引用的 PASS 行不算有证据。

**UI 任务证据追加约定**（`ui_affected: true` 时）：
- `P6-evidence/screenshots/` 目录必须非空，每个截图文件大小 > 1KB（防空 png 充数，hook 检查）
- 每条 UI 类 PASS 必须含 vision-analyst YAML 引用：`- PASS B01: ... (screenshots/b01.png) (vision: vision-reports/b01.yaml)`
- vision YAML 文件必须存在且 `summary.blocker_count == 0`（hook 检查）
- vision YAML 格式见 `assets/execution-roles/vision-analyst.md` 的完整 YAML 结构

**查询类 BDD 证据约定**：
- 查询类 BDD（断言值是唯一证据）可不截图，但**须有断言记录文件**作为客观证据
- 断言记录形式：API 响应 JSON（`response.json`）、测试输出日志（`assert.log`）、数据库查询结果（`query-result.txt`）等
- 引用格式：`- PASS B01: 返回 3 条记录 (response.json)`——括号内路径相对 P6-evidence/，文件必须存在
- **所有 PASS 都必须有文件引用**（hook 强制）——无文件引用的纯断言 PASS 不被接受。文件形式不限（截图/日志/JSON/文本），不绑定技术栈

## READY 收尾检查（P8 gate 通过后、标记 READY 前）

详见 state-machine.md「READY 收尾检查」节（权威来源）。主 Agent 逐项检查 4 类（状态与版本 / 测试环境已清理 / 开发环境已还原 / 生产环境无残留），任一项未通过 → 不进入 READY；生产环境相关项未通过 → 立即 PAUSED 报告人工。

P8-release.md 应包含「临时资源清单」节，列出本任务启动的临时服务/进程、临时数据、开发安装，供主 Agent 清理时参照。