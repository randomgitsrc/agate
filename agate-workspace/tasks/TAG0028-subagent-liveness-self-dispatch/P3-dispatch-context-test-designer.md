---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0028
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标

产出 `P3-test-cases.md` + 测试代码（红灯，TDD）：把 P1 的 33 条 BDD 逐条转为 pytest 用例（1:1 映射，
测试名引用 BDD 编号），覆盖 P2-design.md 四 phase 的 M9 测试面：

- **适配器解析**：三平台 fixture → CommandRecord IR 断言（BDD-1~7）
- **检测引擎判定**：复刻 verify_cmdstream_detection.py 9 场景语义（BDD-8~18）+ 阈值覆盖/缺失/损坏兜底（BDD-19/20/21）+ verify 锚保持（BDD-22）+ 证据+触发核查不判死（BDD-23）+ 平台无关输出（BDD-24）
- **心跳文件生命周期**：命名（BDD-25）/ 审计豁免（BDD-26）/ 清理+兜底（BDD-27）
- **自主再派发边界**：.state.yaml 不写（BDD-29）/ 写权限子集（BDD-30）/ judge 例外（BDD-31）/ 产出收敛不触发 gate（BDD-32）/ gate 返回约定（BDD-33）

### 约束

1. **TDD 红灯是硬要求**：测试代码先写、当前全部红灯（被测模块 agate-cmdstream-ir/adapters/detect 尚未实现——
   import 失败/模块不存在属 B 类红灯可推进）。**禁止**在 P3 实现任何被测功能。
2. **BDD 1:1 映射**：每条 `#### BDD-NN` 至少一个测试用例，测试名引用 BDD 编号（如 `test_bdd_1_ir_fields`）；
   编号连续（BDD-1~33），可二值判定。
3. **9 场景语义对齐**：检测引擎单测以 verify_cmdstream_detection.py 的 9 场景（A-I：调用阻塞/空转/合法迭代/
   健康长尾/合法长命令/expected 超期/截断排除/长时间思考/活动冻结）为判据参考实现，阈值常量同源
   （300/900/60/300/10/5 + REPEAT_UNIQUE_MIN=3 + expected×2 下限 30s）。
4. **fixture 脱敏**（BDD-6/7）：三平台 fixture 字段结构取自验证记录
   （verification-cmdstream-datasource-20260903.md），命令/输出内容脱敏（不含真实用户路径/密钥/会话标识）；
   OpenCode SQLite fixture 运行时构造或最小转储。**不得读取其他用户会话**（I-14）。
5. **DSH zstd 测试依赖**（P2-review 非阻塞建议 2）：DSH 适配器解压经 spawn node 单行脚本
   `node:zlib.zstdDecompress`——测试须**探测 node 可用性**（`node -e "..."` 返回 function 才跑真实解压用例；
   node 不可用时跳过该用例并标注 skip 原因），**不得硬依赖 python zstandard**。node 可用性探测结果写进
   P3-progress.md。
6. **gate_commands 固化**（P2 已定稿，勿改）：P3 用 `python3 -m pytest agate/tests/ -q --tb=short` 形态；
   主 Agent 跑 check-tdd-red 时以 gate_commands.P3 为测试运行器。测试文件放 `agate/tests/unit/`。
7. **测试代码可运行**：测试文件语法正确（跑 pytest 收集不报 A 类错误——SyntaxError/第三方 import 失败）；
   红灯必须来自"被测模块未实现"（import 失败/模块不存在），不是断言与 fixture 数据矛盾（T075 教训）。
8. **长期不变量 vs 一次性交付事实**（TAG0025 教训）：BDD-22（verify 脚本 9 场景全 PASS）是长期不变量，
   断言脚本存在 + 运行 exit 0 结论串，不断言"Unreleased 段是否存在"类一次性事实。
9. **范围锁定**：测试设计若发现 BDD 语义歧义需改 P1 基线 → 标 `[SCOPE+]` 报告主 Agent，不擅自改 BDD。

### 上游关联

- P1-requirements.md（33 BDD，验收锚）
- P2-design.md（方案 A 三脚本 + M9 测试面 + gate_commands + files_to_read）
- verify_cmdstream_detection.py（9 场景判据参考 + BDD-22 锚）
- 验证记录（三平台格式差异事实 + fixture 样例来源）
- 同类扫描 S-5（check-p6-provenance 豁免）/ S-8（maintainability.yaml 兜底模式）

### 输入文件（按顺序读）

1. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P1-requirements.md`（33 BDD）
2. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P2-design.md`（方案 + M9 测试面 + gate_commands）
3. `agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/P0-brief.md`（env_constraints）
4. `docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verification-cmdstream-datasource-20260903.md`（fixture 样例来源）
5. `docs/design-notes/260903-design-subagent-liveness-and-self-dispatch/verify-heartbeat-cmdstream/verify_cmdstream_detection.py`（9 场景判据）
6. `agate/tests/conftest.py`（pytest fixture 体系复用）
7. `AGENTS.md`（项目约定，测试平台无关约束）

### 产出文件字段

产出 `P3-test-cases.md` 到任务目录 + 测试代码到 `agate/tests/unit/`。
frontmatter 用 `agate-md-field-set` 填写：phase=P3 / task_id=TAG0028 / parent=P2-design.md /
trace_id=TAG0028-P3-20260903 / status=draft / created=2026-09-03 / agent=test-designer /
**test_code_dir: agate/tests/unit/**（必填）。
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P3

路径：phase-cards/P3-tdd.md
---
# P3 — TDD 测试设计

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → 确认 P1 phases 不含 P3 + 有合规理由（risk=low + 跳过风险已声明）→ 跳过，读 P4 卡片

## 如果是首次进入本阶段

0. 跑 `agate-capture-env-baseline.py $TASK_DIR`（自动捕获环境基线）。**必须执行**。
   该步骤不阻塞流程——脚本的 stderr 输出（含 WARNING）均可忽略，执行完直接继续步骤 1。
1. 派发 test-designer subagent → 产出 P3-test-cases.md + 测试代码目录
   1.1 写 P3-dispatch-context-test-designer.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 主 Agent 跑 check-tdd-red.py 确认红灯
3. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P3，不要提前写 P4——phase = 本 commit 的产出阶段
4. git commit -m "wf({Txxx}-P3): {摘要}"（phase=P3，P3 产出含 P3-test-cases.md + 测试代码）
5. P3 commit 完成后进入 P4：**phase 推进 P4 随 P4 产出 commit 一起**（P4-implementation.md 就绪后），不是单独 phase commit

## refactor 任务：回归测试口径

> 适用：P1 frontmatter 声明 `change_type: refactor` 的任务（P2-design.md §3.4）。功能任务（缺省）走上方既有 TDD 口径，不受本节影响。

refactor 任务无新增功能行为可断言，P3 测试设计改用**回归测试口径**：

- **测试设计 = 回归测试口径**：复用/保留既有测试用例，标注每条回归用例覆盖了重构涉及的哪些文件/路径；**不新增功能行为断言**（无新行为可断言）。
- **跳过 check-tdd-red 红灯步骤**：重构无新功能断言，测试套件本就全绿，红灯语义不适用（check-tdd-red 对 refactor 任务会误报 exit 2 绿灯）。回归质量由 P5 全量回归（gate_commands.P5）+ P6 的 `regression.log`（全量回归重跑）兜底。CI backstop 对 refactor 任务同样跳过 check-tdd-red（ci-gate-backstop.py P3 分支 refactor 感知）。
- **P3 gate 不变**：仍为文件存在性检查——refactor 的 P3 产出是 P3-test-cases.md（回归口径声明 + 既有用例覆盖映射），文件存在即满足 gate。

## 如果是重试

确认上一轮失败原因（测试设计不合理 / 未覆盖关键 BDD / 非真红灯）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P3 MAX=2）

## 前置条件

- [ ] P2-design.md files_to_read 完整（测试设计需要知道实现导航）
- [ ] P2-review.md status: approved（P2 不可裁剪）

## 派发

- **角色**：test-designer（`{agate_root}/assets/execution-roles/test-designer.md`）
- **输入**：P2-design.md + P1-requirements.md（BDD 验收条件，每条 `#### BDD-NN` 对应一个测试用例）
- **输出**：P3-test-cases.md + test_code_dir/
- **派发 prompt**：`{agate_root}/assets/templates/dispatch-prompt.md`

## 产出规格

- P3-test-cases.md 必须声明 `test_code_dir: {路径}`
- 每条测试用例对应一条 P1 的 `#### BDD-NN` 验收条件（1:1 映射）
- UI 任务（P2 ui_affected: true）：必须含 Playwright/E2E 用例

## gate 规则

**check-gate.py P3**（hook + 主 Agent 预跑，秒级文件检查）：
- exit 1：P3-test-cases.md 不存在
- exit 2：P3-test-cases.md 存在（TDD 红灯由 check-tdd-red.py 独立确认）

**check-tdd-red.py**（主 Agent 手动确认红灯 + CI backstop P3 兜底）：

```bash
check-tdd-red.py $TASK_DIR
```

- **exit 0**：真红灯（assertion 失败 / 项目内 import 失败 = B类错误）— 测试正确但因实现未写而失败
- **exit 1**：假红灯（SyntaxError / 第三方 import 失败 = A类错误）— 测试代码自身错误
- **exit 2**：绿了 — 实现先于测试，违反 TDD
- **exit 3**：无可用测试运行器

**技术栈无关**：check-tdd-red.py 通过 formatter 将测试输出标准化为 JSON，不直接解析任何框架的输出格式。formatter 在 gate_commands.P3_formatter 中声明（可选）。不提供 formatter 时退化为 exit-code-only（所有红灯 = 可推进）。

**探测链**：`$TEST_RUNNER` 环境变量 → `gate_commands.P3`（P2-design.md 声明）→ `which pytest` → exit 3。`$TEST_RUNNER` 始终优先（退化为 exit-code-only，无 formatter）。

**formatter 选择**：见 `assets/formatters/README.md` 速查表。常用：pytest → `pytest.sh`，vitest → `vitest.sh`，go test → `go-test.sh`，其他 → `generic-exit-only.sh`。

## 按包拆分并行（条件触发，非强制）

> 仅当 P2 packages > 1 且包间无依赖时适用。单包任务跳过本节。
> 并行上限 / 失败批 retry / 共享文件统一后处理见 dispatch-protocol「派发编排机制」并行规则。

当 P2 声明多个 packages 且包间无数据依赖时，P3 可拆分并行：

1. 每个 package 派一个 test-designer subagent
2. 各自写各自的测试文件（不同目录）
3. 各自返回路径 + 摘要
4. 主 Agent 汇总后统一 commit

拆分判据（本阶段特定）：
- P2 packages > 1 且包间无数据依赖 → 可并行
- 单包或包间有依赖 → 串行（不拆分）
- P2 未声明 packages → 串行

每个 subagent 的 dispatch-context 必须明确其负责的 package 范围（约束节写"只写 {pkg} 目录下的测试"）。

## 推进条件（全部满足才写 phase: P4）

- [ ] check-tdd-red.py exit 0（真红灯确认）
- [ ] P3-test-cases.md 存在且含 test_code_dir
- [ ] 测试代码目录存在
- [ ] UI 任务：Playwright/E2E 用例存在

## 常见错误

1. **测试绿了才 commit**：测试已在 P4 之前通过 → 违反 TDD"测试先于实现"原则。P3 的 gate 要求红灯
2. **忘记声明 test_code_dir**：后续阶段找不到测试代码 → P5 跑 gate_commands 时找不到测试路径
3. **测试覆盖不全**：只为部分 BDD 写了测试 → P6 验收时那些 BDD 没有自动化验证
4. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。
5. **只覆盖交互路径，忽略前置状态**：测试设计应覆盖 BDD Given 隐含的前置状态，不只覆盖 When/Then 路径（详见 WORKFLOW.md §P3 测试设计指导）

## 下游影响

- P4 用测试驱动实现（implementer 看测试理解预期行为）
- P5 跑同一套测试验证实现正确性（gate_commands.P5）

> 完成 → 读 phase-cards/P4-implementation.md
<!-- AGATE_CARD_END -->

<objective_info>
### A. 路径拓扑
- 任务目录 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0028/agate-workspace/tasks/TAG0028-subagent-liveness-self-dispatch/`
- worktree 根 = `/home/kity/oclab/agateon/.worktrees/agate-TAG0028`
- 测试代码落点 = worktree 的 `agate/tests/unit/`（协议本体，本次改造对象）
- 协议本体 = worktree 的 `agate/`（主 checkout 禁止改动，`~/.agate` 稳定版是 gate 工具）

### B. 测试面速查（P2-design.md M9 展开）
- 适配器：`test_agate_cmdstream_adapters.py`（三平台 fixture 解析 + 子 agent 会话定位 + 注册表 + fixture 脱敏断言）
- IR：`test_agate_cmdstream_ir.py`（十字段契约 + 序列化）
- 检测：`test_agate_cmdstream_detect.py`（9 场景复刻 + 阈值兜底 + 截断排除 + 轮询标注 + 平台无关输出 + 不判死）
- 心跳生命周期：命名/豁免/清理（可并入检测或独立 `test_agate_cmdstream_heartbeat.py`）
- 再派发边界：.state.yaml 不写 / 写权限子集 / judge 例外 / 产出收敛 / gate 返回约定（可并入
  `test_agate_cmdstream_dispatch.py` 或以文档断言形式）
- 文件命名建议前缀 `test_agate_cmdstream_`（与既有 `test_agate_*` 惯例一致）

### C. 检测引擎数值锚（BDD 与 verify 脚本同源）
- 调用冻结：expected×2（下限 30s）主信号 / 兜底 alert=300 / suspect=900
- 活动冻结：alert=60 / suspect=300；三类活动（思考/输出/工具）
- 无效重复：窗口 10 同 (命令, exit, 输出哈希) ≥5 → SPIN；REPEAT_UNIQUE_MIN=3（唯一命令数 <3 → 信息级）
- 截断排除：truncated 不参与哈希比对、仍参与冻结检测
- 心跳命名：`${TASK_DIR}/.heartbeat` / `.heartbeat.child-{n}`

### D. 环境事实
- python3 3.12.3 / pytest 9.0.3（`python3 -m pytest` 形态）/ pyyaml 6.0.1
- node：需探测 `node -e "const z=require('node:zlib'); console.log(typeof z.zstdDecompress)"`（验证记录已确认
  node v24.15.0 zlib.zstdDecompress 为 function）
- 无 python zstandard/zstd 二进制（不得硬依赖）
- check-tdd-red 由主 Agent 在 P3 产出后运行：`timeout 180s python3 agate/scripts/check-tdd-red.py $TASK_DIR`
  （TEST_RUNNER 未设置 → 读 gate_commands.P3；exit 0 = 真红灯）

### E. judge 启用
- `.state.yaml` 已写 `judge.enabled: true`（P6.5 走独立 judge，P3 测试设计与之无冲突）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
