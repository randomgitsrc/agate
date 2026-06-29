# 变更日志

所有对 agate 协议的重要变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

---

## [0.4.0] - 2026-06-29

### 新增
- P3 gate 红灯 A/B 分类：B 类（import 未实现）exit 0 通过，A 类（测试代码 bug）exit 1。`PROJECT_MODULE` 环境变量提高精度，未设置退化为启发式
- P5 修复流程：修复 subagent 返回后主 Agent 必须重跑 P5 gate 全量测试，不是只检查修复项。修复重派 prompt 必须附修复历史
- P8 gate CHANGELOG 覆盖率检查：`git log v{prev_version}..HEAD --oneline` 对照 CHANGELOG 条目。`CHANGELOG_FILE` 环境变量支持非 CHANGELOG.md 项目
- P6 BDD 结果格式约定：必须用行首 `- PASS`/`- FAIL`，不用表格/emoji，保证 gate grep 可靠匹配
- P6 证据目录（`P6-evidence/`）：非空检查作为 self-authored gate 的防伪造措施
- gate 分类体系：外部产出 gate（P3/P4/P5）vs 自写文件 gate（P1/P2/P6/P7），⚠️ 标记可伪造 gate
- `check-gate.sh`：P3/P4/P6/P7/P8 脚本化 gate 检查（exit 0/1/2）
- `check-protocol-consistency.py`：6 类结构一致性检查 + CI workflow
- 任务粒度指引：拆分判据从"输出异构性"改为"产出文件数 > 3"（T026 实验证实 dispatch prompt 模板可处理异构产出）
- `LIMITATIONS.md` 局限 3：self-authored gate 分类 + T026 事故记录
- CHANGELOG.md 变更日志 + README version badge 与 git tag 一致性检查（CHECK 7）

### 变更
- P6 gate exit code 从 0 改为 2：脚本化检查（FAIL=0/NC=0/证据非空）通过，但 BDD 总数对照需主 Agent 手动核实
- `check-tdd-red.sh`：新增 `PROJECT_MODULE` 环境变量，多语言 import 错误检测，TEST_RUNNER 输出契约文档化，pytest 作为参考实现
- `check-gate.sh` P8：新增 `CHANGELOG_FILE` 环境变量，扩展 version 文件匹配（go.mod/pom.xml 等），文档化单 commit 假设
- P6-evidence/ 子目录：`screenshots/` 和 `traces/` 标注为 UI 任务专属，`test-output.log` 通用
- gate 分类举例：从 pytest/vue-tsc 改为通用术语（test runner/type checker）

### 修复
- `check-tdd-red.sh`：`IndententationError` → `IndentationError` 拼写修复；SyntaxError 正则去重

---

## [0.3.0] - 2026-06-28

### 新增
- `check-gate.sh`：P3/P4/P6/P7 脚本化 gate 检查（exit 0/1 可判定，exit 2 需主 Agent 自判）
- `check-tdd-red.sh`：`TEST_RUNNER` 环境变量 + 回退链（$TEST_RUNNER → which pytest → exit 3）
- P8 gate：bump_type 字段检查、version 文件变更检查、CHANGELOG 变更检查
- T022 债务清还：P6 BDD 覆盖完整性、P8 bump 后重跑 P5、bump 判定指引、DEVIATION-CRITICAL 分类、写跑分离澄清、verifier 证据优先级（DOM > 交互 > vision）、compact 环境恢复（env_state in .state.yaml）

### 变更
- 状态机步骤 5：gate 命令分档——可 shell 化的（P3/P4/P7）写 shell 命令，不可的（P1/P2/P5/P6/P8）保留自然语言
- P5/P8 gate：bump 后必须重跑 P5 gate + bump_type 字段
- P7 gate：DEVIATION-CRITICAL 标记格式
- P8 gate：`git diff HEAD~1` 验证 version/CHANGELOG

---

## [0.2.0] - 2026-06-27

### 新增
- 分阶段落盘改为默认启用：每次派发 prompt 自带落盘指令，不再作为空返回后的补救措施
- P0-brief executor_env 补全、P0/P1 职责边界三层指引
- `LIMITATIONS.md` 局限 5：协议文档自身内部一致性验证不在流程内
- `WORKFLOW.md`：主 Agent 合法职责清单与降级硬边界

### 变更
- T020 评审修复：P6 单步函数旧表述修正（PASS/FAIL 二值），删除重复的写跑分离段落
- assets/ 与 orchestrator 同步 T016-T020 协议修复（6 个执行角色 + 4 个模板 + 所有协议文件）

### 修复
- T019 复盘修复：6 项（复盘机制核对清单模板、LIMITATIONS T019/T016 数据点等）
- T020 复盘修复：6 项（2 bug fix + 3 能力补充 + 1 已知限制）
- subagent 空返回根因验证：证实 `steps` 上限无效，分阶段落盘有效（5 组对照实验）

---

## [0.1.0] - 2026-06-26

### 新增
- 核心协议：状态机（P0-P8 阶段）、派发协议、工作流指南
- 角色体系：6 个执行角色（analyst/architect/test-designer/implementer/verifier/vision-analyst）+ 3 个评审角色
- orchestrator 模板：启动读取列表、平台专有配置区块
- git 集成、loop 编排、平台适配说明
- `LIMITATIONS.md`：5 个已知局限
- T016 复盘：5 项协议修复（输入导航、降级禁止、空返回恢复等）
- 专家评审：10 个 BLOCKER 修复 + 8 个建议

### 变更
- 通用化清理：移除 PeekView 特有内容（6 处）
- 标准安装位置：`~/.agate/`
- 上下文工程优化：orchestrator 启动时读取全部 7 个顶层文件

### 修复
- 模糊触发条件：git-integration 边界 + 评审角色判定标准
- 启动读取缝隙：orchestrator-template 改为强制启动读取，补中断恢复缝隙
