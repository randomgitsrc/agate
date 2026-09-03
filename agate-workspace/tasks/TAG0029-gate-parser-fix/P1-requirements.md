---
phase: P1
task_id: TAG0029
parent: P0-brief.md
trace_id: TAG0029-P1-20260904
status: draft
created: 2026-09-04
agent: analyst
risk_level: high
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [gate-parser, tdd-judge, platform-scanner, protocol-docs]
domains: [backend]
---

# P1 需求基线 — TAG0029 gate 命令解析器修复批

> [PROD_NOT_TOUCHED] 本阶段只做只读查证与需求分析，未改动任何实现代码。
> 改造对象为 worktree 的 `agate/`，`~/.agate` 稳定版未动。
> 提醒：`judge.enabled: true` 启用声明写在 `.state.yaml`，由主 Agent 落盘，不在本文件声明。

## 1. 需求复述

P0-brief 锁定的三个关联缺口（范围不可自行扩大）：

1. **DEBT0027（high，假绿灯）**：`agate-read-gate-commands.py` 值清洗
   `raw.strip().strip(chr(34)).strip(chr(39))` 不剥离值内 `# 注释` 与残留引号
   （值不以引号结尾时只剥开头引号）；消费方 `bash -c` 执行报 unterminated quote
   语法错误（exit 2）；`check-tdd-red.py` 的 `judge_result` 对"命令串本身语法错误致
   exit 2"无显式分支，落到末尾 red-light exit 0 —— 测试根本没跑却被当红灯证据放行。
   要求：解析器输出纯命令或报解析错误；judge 仅在测试运行器正常退出时才判定红灯可推进。
2. **DEBT0023（low，P3* 键静默收集）**：收集侧 `key.startswith("P3")` 把所有 P3*
   非元键收集为 TDD 测试命令执行；`is_gate_meta_key` 仅精确匹配
   `_formatter` / `_timeout_seconds` 后缀，P3_xxx 不被豁免；协议层无机械防护
  （TAG0026 靠"禁用 P3_xxx 键"约定规避）。要求：P3 精确键 + 白名单后缀收紧或扩展
   元键约定 + P2 卡 gate_commands 节禁止声明 + 单测锁定收集行为。
3. **RM-AG0056（扫描器数据面误伤 + 未进常驻面）**：R2 规则
   `(^|[\s=(\'\"])python3([\s]|$)` 静态扫描无法区分"测试代码里的命令调用"
   （应禁裸 python3）与"fixture 模拟平台日志的数据面内容"（command 字段模拟真实日志
   本应含 `python3 -m pytest`）；cmdstream fixture 17 处裸 python3 破坏 TAG0011
   bdd-8「tests 树 0 命中」，P5 全量红灯回 P4 fix3 才闭环；且扫描器不在 P3/P4
   gate_commands 常驻面，回归到 P5 全量才暴露。要求：fixture 目录/文件声明豁免
   （禁"含 fixture 字样就跳过"的宽匹配，须绑定目录声明）+ 纳入 P3/P4
   gate_commands 常驻面 + fixture 恢复真实日志形态。

## 2. 隐含需求识别

- **H1 值清洗须校验引号闭合**：只剥注释不够，残留引号同样导致 unterminated quote；
  输出只能是"纯命令"或"解析错误（exit 非 0 + stderr）"，不允许第三种带残渣输出。
  否则 DEBT0027 只修一半。
- **H2 judge 须区分两类 exit 2 语义**："测试运行器正常退出且报告错误"
  （既有 A 类 exit 1 分支覆盖 Traceback/SyntaxError/exit>=120）与"命令串本身语法错误
  致 bash exit 2"（无运行器产出、无失败断言统计）是不同输入，必须走不同分支；
  混淆两者就是本次假绿灯的根因。
- **H3 改收集判据须同步 rules YAML**：`is_gate_meta_key` 判据与
  `rules/` YAML 声明由 `check-structure-consistency.py` S-4 校验绑定；
  若收紧方案动了该判据，必须同步 YAML，否则 consistency 红灯。
- **H4 收紧前须 grep 全部消费方**：解析器是 P2/P3/P5 gate 消费链共享件；
  P3 精确键 + 白名单后缀必须先确认不漏合法用法，再以单测锁定。
- **H5 fixture 豁免须绑定目录声明并以单测锁边界**：宽匹配会被真代码借用；
  需证明"声明目录内的数据面豁免、目录外的同类文本仍命中"。
- **H6 常驻面是行为变更，启用前先全量扫描存量**（DEBT0025 流程）：有命中先登记
  清单再启，不带病上线。
- **H7 语义修正类修复走 TDD**：先补"语法错误 → exit 1"失败测试确认红，再改实现。
- **H8 回归底线与提交义务**：Linux 全量 pytest 全绿为底线；改 `agate/scripts/*` +
  `agate/phase-cards/P2-design.md` 触发 SELF-GATE，commit message 须含
  `self-gate-review:` 或 `self-gate-skip:`。
- **H9 fixture 恢复真实日志形态后 TAG0011 bdd-8 须保持绿**：豁免机制与
  fixture 内容恢复是同一闭环的两面，缺一面验收不完整。

## 3. BDD 验收条件

### 解析器值清洗（DEBT0027）

#### BDD-1: 行内注释的命令值解析出纯命令且可被 bash 执行
- Given P2-design.md 的 gate_commands 块中某命令值为带行内注释形态
  （命令正文后跟空格 + `#` 注释尾巴，整体被引号包裹）
- When 运行 gate 命令解析器解析该块
- Then 输出 JSON 中对应 cmd 恰等于注释剥离后的纯命令（无注释尾巴、无残留引号），
  且 `bash -c` 执行该 cmd 的退出码不为 2，stderr 无 unterminated quote 文案

#### BDD-2: 引号未闭合的命令值报解析错误而不产出残渣命令串
- Given gate_commands 块中某命令值引号未闭合（剥离后仍含残留引号）
- When 运行 gate 命令解析器解析该块
- Then 解析器以非零退出码退出并在 stderr 输出解析错误，不输出带残渣的命令串

### TDD 红灯判定（DEBT0027 judge 侧）

#### BDD-3: 命令串本身语法错误判 A 类错误，不计入红灯证据
- Given 某测试命令串本身含语法错误（bash 执行退出码为 2，输出含语法错误文案，
  且无测试运行器产出的失败断言统计）
- When check-tdd-red 判定该次运行结果
- Then 判定退出码为 1，不为 0

### P3 键收集（DEBT0023）

#### BDD-4: P3_xxx 辅助键不被收集为测试命令
- Given gate_commands 块含 P3_xxx 形态的辅助键且其不具测试命令语义
- When 解析器收集 TDD 测试命令
- Then 输出 commands 中不含该键对应的命令条目

#### BDD-5: 裸 P3 键被收集而元键被豁免
- Given gate_commands 块同时含裸 P3 键与 `_formatter` / `_timeout_seconds`
  后缀的元键
- When 解析器收集 TDD 测试命令
- Then 输出 commands 含裸 P3 对应的命令条目，且不含任一元键对应的条目

#### BDD-6: P2 卡 gate_commands 节含 P3_xxx 禁止声明及其原因
- Given 本任务完成后的 P2 阶段卡片
- When 查看其 gate_commands 节
- Then 节内存在 P3_xxx 键禁止声明文本及其原因说明

### 平台假设扫描器（RM-AG0056）

#### BDD-7: R2 对 fixture 数据面豁免，tests 树保持 0 命中
- Given fixture 目录内的数据文件 command 字段为模拟真实日志形态
  （含 `python3 -m pytest` 字样）
- When 运行平台假设扫描器扫描 tests 树
- Then R2 对该数据面内容无命中，扫描退出码为 0

#### BDD-8: R2 对代码面裸 python3 调用仍拦截
- Given 测试代码行含命令位置的裸 python3 调用（非注释、非 docstring、
  非探测形态、位于 fixture 豁免目录之外）
- When 运行平台假设扫描器扫描该文件
- Then R2 报出该行命中，扫描退出码为 1

#### BDD-9: 扫描器纳入 P3/P4 gate_commands 常驻面
- Given 本任务完成后的任务 P2-design.md
- When 查看其 P3 与 P4 的 gate_commands 声明
- Then P3 与 P4 块均含平台假设扫描器命令条目

## 4. 同类扫描结论

以 `strip(chr(34))` / `is_gate_meta_key` / `startswith("P3")` / R2 正则
及 `judge_result` 末尾分支扫全仓（已独立复核主 Agent 初扫）：

| # | 命中 | 判定 |
|---|------|------|
| 1 | `agate-read-gate-commands.py` L57（命令值清洗） | 本次处理（DEBT0027 Phase 1，BDD-1/BDD-2） |
| 2 | `agate-read-gate-commands.py` L66（formatter 值清洗） | 本次处理（同文件同模式，注释尾巴同样污染 formatter） |
| 3 | `agate-read-p5-commands.py` L30/L37（P5 值清洗同模式） | 本次不处理：P0-brief scope 锁定三缺口且 P5 路径不在假绿灯消费链上； |
  同源不同严重度，候选后续任务，不在本任务扩大范围 |
| 4 | `agate-gate-missing-cmds.py` L24（首 token 检测） | 本次不处理：该脚本只取首 token 做缺失检测，不经 `bash -c` 执行， |
  注释尾巴不构成 unterminated quote；回归验证覆盖即可 |
| 5 | `key.startswith("P3")` 仅 `agate-read-gate-commands.py` L60 一处 | 本次处理（DEBT0023 Phase 2，BDD-4/BDD-5/BDD-6） |
| 6 | `is_gate_meta_key` 消费方：`check-gate.py`（对账语义）/ |
  `agate-read-p5-commands.py` / `agate-gate-missing-cmds.py` / |
  `agate-read-gate-commands.py` / `agate-gate-p5-count.py` + |
  `check-structure-consistency.py` S-4 + `rules/` YAML 声明 | 本次处理范围：仅收集侧收紧； |
  若动公共判据须同步 YAML（S-4），其余消费方不改语义，只做全量回归验证 |
| 7 | R2 正则 `check-platform-assumptions.py` L39 全仓唯一 | 本次处理（RM-AG0056 Phase 3，BDD-7/BDD-8；只加数据面豁免， |
  不改 R2 本体判定逻辑之外的扫描面） |
| 8 | `judge_result` 末尾 red-light exit 0（L156-157，exit 2 无显式分支） | 本次处理（DEBT0027 judge 侧，BDD-3；须区分运行器正常退出与命令串语法错误） |

## 5. P0-brief 时效性质疑结论

已核对 P0-brief 时效性，无漂移。核对依据（worktree 只读查证，2026-09-04）：

- P0-brief 与交接单同日立项（2026-09-03），仅隔 1 天，项目前提无变化。
- 三处缺陷模式在 worktree 现状中仍全部命中：L57 值清洗仍为双 strip 无注释剥离；
  L60 仍为 `startswith("P3")`；R2 正则仍为原式且无 fixture 豁免分支；
  `judge_result` exit 2 仍无显式分支。`task` 目标方案成立、`executor_env`
  平台前提成立、`known_risks` 无"已解决前提"。
- `.state.yaml` 为 task_id/phase/status 三行、phase=P0，与"首次派发"一致。

## 6. 待确认清单

[NO_NEED_CONFIRM]
（范围由 P0-brief 锁定，closure_criteria 来自 DEBT/RM 条目原文，收紧与豁免方向
均有明确约束，无需人工定方向。）

## 7. 裁剪说明

`phases` 取全量 [P1, P2, P3, P4, P5, P6, P7, P8]，不裁剪任何阶段。理由：

- P2 不可裁：收集收紧与豁免机制各有多种实现形态，需候选方案比选。
- P3 不可裁：DEBT0023/DEBT0027/RM-AG0056 的 closure_criteria 均要求新增单测锁定。
- P4 不可裁：实现改动面跨解析器/judge/扫描器/协议卡四处。
- P5/P6 不可裁：全量回归 + 逐 BDD 验收是 high 风险任务的底线。
- P7 不可裁：新扫描面与判据变更上线须过一致性（含 S-4 YAML 对账与用例数核对）。
- P8 不可裁：roadmap 回写 RM-AG0056 → done 与 DEBT0023/0027 关闭登记是 gate 硬校验。

## 8. 能力与环境声明

```yaml
capability_requirements: []
```

- 本任务无特殊 agent 侧能力需求：纯脚本与协议文本改动，不涉及浏览器行为、
  视觉验收、外部系统交互；bash / python3.12 / pyyaml / pytest / ruff /
  shellcheck 环境齐全，无 supplementable 项，无 GAP。
- 运行环境为标准 worktree 本地环境，无额外服务、端口、数据库依赖；
  不声明 `verification_env`，验证轮次预算不适用。
- domains 取 [backend]：改动面为 `agate/scripts/*` 与阶段卡片文本，
  无前端显示与交互变化，故无视觉能力条目与 UX 类别 BDD。
