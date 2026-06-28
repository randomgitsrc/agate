# 派发 Prompt 模板

> 主 Agent 调用 task 工具派发 subagent 时，prompt 用这个结构
> 本模板与 dispatch-protocol.md「派发 prompt 模板」节保持同步，协议文件为权威来源

```
你是 {阶段 Pn} 阶段的 {角色名} 子 Agent。

## 你的角色定义
读取并严格遵循：
{agate_root}/assets/{execution-roles|review-roles}/{role}.md

## 项目约定（必读）
- {project_conventions_file}（项目约定、命名规范、目录结构）
- docs/tasks/{Txxx}/P0-brief.md（本任务的环境约束和风险声明）

## 环境隔离（强制，所有阶段适用）
本任务的环境约束见 P0-brief.md 的 env_constraints 字段。
- 调试/验证必须使用 P0-brief 的 debug_env 声明的测试环境，严禁直接操作生产环境
- 开发全程不应接触生产环境；若意外接触，立即停止并标注 [PROD_TOUCHED] 报告主 Agent

## 输入（自己读取，不要等我提供内容）
- docs/tasks/{Txxx}/P0-brief.md（主 Agent 的任务简报和风险声明）
- docs/tasks/{Txxx}/{上一阶段产出文件}
- {agate_root}/WORKFLOW.md（流程规范）
- docs/tasks/{Txxx}/P{N}-dispatch-context.md（若存在：主 Agent 已查证的客观信息，如环境状态、URL、选择器等）
{按角色定义补充其他需要读的文件}

## 任务
{这个阶段要做什么，一两句话}

## 分阶段落盘（重要，默认启用）
每读完一个输入文件或完成一个关键步骤，立即把发现追加写入 docs/tasks/{Txxx}/P{N}-progress.md（bash 追加模式）。这样即使你最终无法产出完整报告，progress 文件也能让主 Agent 知道你做了什么。不要等所有文件读完再一次性写——逐条写。

## 输出
产出文件：docs/tasks/{Txxx}/{本阶段产出文件}
（Txxx 是完整目录名，如 T002-fix-db-migration；不是纯 T002 编号。所有派发文件路径统一用 {Txxx} 占位符。）

文件必须以这段 Header 开头（直接复制，主 Agent 已填好所有值）：
---
phase: {Pn}
task_id: {完整 task_id，如 T002-fix-db-migration}
type: {problems|design|review|test-cases|implementation|test-results|acceptance|consistency|release}
parent: {上一阶段文件名}
trace_id: {Txxx}-{Pn}-{YYYYMMDD}
status: draft
created: {YYYY-MM-DD}
---

> Header 字段完整列表见 `task-files.md`「通用 Header」。本模板列出主 Agent 派发时必须直接填好的核心字段；其余字段（如 type 的具体取值）由 subagent 按角色定义补全，但主 Agent 必须确保 `phase/task_id/parent/trace_id` 四个字段已直接填好（避免 subagent 自己拼出错）。

## 能力补充说明（若 P1 有 supplementable 条目，此节必填）
本任务需要以下补充能力：
- {能力名}：使用 {补充方式}（如：派发 vision-analyst / 注入 playwright-vision skill）

## 门槛（什么算完成）
{可判定的完成条件，能从文件读出明确值}

## 返回给我（重要）
只返回两行：
  1. 产出文件路径
  2. 一句话摘要（不超过 30 字）
绝对不要返回文件全文——我只需要路径和摘要。
```

## 阶段特定提示（按需追加到 prompt 末尾）

### P2 派发追加
```
## P2 最小验证（若方案依赖浏览器行为/安全模型/外部系统行为）
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。纯代码逻辑不需要最小验证。
```

### P4 派发追加
```
## 上下文控制
读取代码文件以 P2-design.md 的 files_to_read 清单为准，按需读取（标了行号范围的只读片段）。
不要在项目里盲目搜索或整目录全读。
## 写跑分离
若需写验证脚本（Playwright/测试脚本等），只写脚本不跑——主 Agent 会跑脚本验证。
```

### P5/P6 派发追加
```
## 截图质量标准
操作类 BDD 截图必须互不相同（md5 去重），查询类 BDD 可不截图（断言值是唯一证据）。
## P6 BDD 二值规则
每条 BDD 结果只允许 PASS 或 FAIL，不允许"调整/跳过/覆盖"等中间态。任何 BDD 标 FAIL → gate 不通过。
## P6 BDD 结果格式
每条 BDD 验收结果必须用行首 `- PASS` 或 `- FAIL` 格式，便于 gate 命令 `grep -cE '^\s*- (PASS|FAIL)'` 可靠匹配。
不要用表格格式（`| B01 | ... | PASS |`），不要用 ✅/❌ emoji，不要用其他格式。
示例：
- PASS B01: 用户可以创建分享链接
- FAIL B02: 过期链接返回 410
## P6 BDD 覆盖完整性
P6 验收必须全量对照 P1 的 BDD 条数（含 SCOPE+ 增补），不能挑验。
P1 有 N 条 BDD → P6 必须有 N 条验收结果（PASS 或 FAIL）。挑验 = gate 不通过。
## P6 证据要求
每条 BDD 验收结果必须有对应证据文件，存入 docs/tasks/{Txxx}/P6-evidence/。
证据类型：
- test-output.log — 验证脚本执行日志（所有任务通用）
- screenshots/ — Playwright 截图（仅 UI 任务）
- traces/ — Playwright trace（仅 UI 任务，可选）
无证据的 PASS 标记 = gate 不通过。
## P6 verifier 脚本执行
P6 verifier 交付的验证脚本（Playwright / shell / pytest）应由主 Agent 执行。
执行输出落盘到 P6-evidence/test-output.log。
若主 Agent 需要自写脚本（如 verifier 脚本不兼容当前环境），自写脚本的执行输出也落盘到 P6-evidence/test-output.log。
关键约束：P6-evidence/ 必须有执行产出，不接受空目录。
## 写跑分离
若需写验证脚本，只写脚本不跑——主 Agent 会跑脚本验证。
```

### P8 派发追加
```
## READY 收尾检查
P8 gate 通过后，主 Agent 会执行收尾检查（停止调试服务、清理临时数据、还原开发环境、确认生产无残留）。
你在 P8 产出中应列出：启动了哪些临时服务/进程、创建了哪些临时数据、做了哪些开发安装，供主 Agent 清理。

## 版本 bump 判定
- 公共 API 行为变化 / 破坏性变更 → major
- 加功能 / 内部重构改 API（向后兼容）→ minor
- 修 bug / 不改 API 行为 → patch
- 测试缺陷不应影响版本号决策：测试 hard-code 版本号 → 修测试，不降级版本
- 在 P8-release.md 中显式声明：bump 类型（major/minor/patch）+ 理由
```

## 项目占位符映射

> 占位符说明：各项目在自己的约定文件（如 CLAUDE.md）中定义具体映射。以下给出示例值供参考，不是 agate 本身的约定。

| 占位符 | 说明 | 示例值 |
|--------|------|--------|
| {project_conventions_file} | 项目约定文件 | `CLAUDE.md` / `CONTRIBUTING.md` |
| {project_index_file} | 项目总览文件 | `INDEX.md` / `README.md` |
| {test_code_dir} | 测试代码目录 | `tests/` / `backend/tests/` |
| {implementation_dir} | 源码目录 | `src/` / `app/` / `backend/pkg/` |
| {build_command} | 构建验证命令（从 P2 gate_commands 读取）| 项目自定义 |
| {lint_command} | 代码检查命令（从项目约定读取）| 项目自定义 |

## 关键提醒
- prompt 里只写文件**路径**，绝不复制文件内容
- 明确要求 subagent 只返回路径+摘要
- **Header 给成品不给格式**：主 Agent 派发时已知道所有值（phase/task_id/日期），直接填好让 subagent 复制，避免 subagent 自己拼 trace_id 拼错导致门槛校验失败
- **路径用完整目录名**：task_dir 是 Txxx-描述（如 T002-fix-db-migration），不是纯 Txxx
- 这两条是上下文不爆炸的保证
- **P4 派发引用 files_to_read**：让 implementer 按 architect 画好的"上下文地图"读文件，而非自己乱窜——这是控制被派发方上下文的关键
- **分阶段落盘默认启用**：每次派发都带落盘指令，不是空返回后的补救措施
- **dispatch-context.md 按需引用**：主 Agent 派发前若已查证客观信息并落盘，prompt 里加此文件路径
