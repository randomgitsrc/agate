> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P3
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0008
role: test-designer
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
批次 **offline**（P2-design dispatch_plan 批次 3/3）：产出离线部署包（agate-pack-offline.py 外网打包 + install-offline.py 内网安装）的测试用例与测试代码。产出 P3-test-cases-offline.md + 测试代码。

### 约束
1. **本批范围（BDD 归属）**：BDD-22~29（pack-offline 产出 bundle+manifest / manifest 字段 / 失败路径非 0 / install-offline 平台核对 / checksum 校验 / wheels 离线安装 / 版本目录+hook+验证闭环 / --skip 勾选）。**只写本批测试**，不碰 resolve-chain（BDD-9~21/30/31）与 install（BDD-1~8）批次的测试文件。
2. **1:1 BDD 映射**：每条 `#### BDD-NN` 对应一个测试用例，测试名引用 BDD 编号（如 `test_bdd_22_bundle_manifest`）。
3. **测试代码落盘位置**：
   - 新建 `agate/tests/unit/test_agate_pack_offline.py`（打包器：manifest 结构 / checksum 计算 / 失败路径）
   - 新建 `agate/tests/unit/test_install_offline.py`（安装器：平台核对 / checksum 校验 / wheels 安装模拟 / 勾选跳过）
   - **不实际访问网络 / 不实际 pip download**：打包测试用假 tag 目录 + 假 wheel 文件（tmp_path），checksum 用真实 hashlib 算小文件；pip 安装步骤 mock（`unittest.mock.patch` 或 subprocess mock）。manifest 平台核对与 checksum 校验是纯逻辑，可直接测。
4. **平台无关原则（AGENTS.md 测试约定，硬约束）**：禁止裸 `python3`（探测 `python3|python`）；禁止裸 `/tmp`（用 pytest `tmp_path`）；禁止假设 POSIX symlink 语义（Linux 断言软链 / Windows 断言"复制模式 + WARNING"或用 `AGATE_HOOK_COPY_MODE=1` 模拟）；每文件第 1 个用例标 `@pytest.mark.windows_smoke`。
5. **红灯确认**：写完后自跑 `python3 -m pytest agate/tests/unit/test_agate_pack_offline.py agate/tests/unit/test_install_offline.py -q --tb=no`，确认**全部红灯**且失败原因是"被测模块未实现"（import 失败 / 模块不存在 = B 类），不是测试代码自身 bug（A 类）。自跑结果记入 P3-progress.md。
6. **test_code_dir 声明**：P3-test-cases-offline.md 须含 `test_code_dir: agate/tests/unit/`。
7. **双工作区纪律**：只写测试代码 + P3-test-cases-offline.md + progress；不修改任何功能代码（P4 才实现）；`~/.agate` / 主 checkout 禁止改动。
8. **不跑全量测试**：只跑本批测试文件。

### 上游关联
- P2-design.md §4.7（离线部署包：pack-offline 流程 + 失败路径 / install-offline 流程 + 平台核对 + checksum + wheels + 勾选）
- P1-requirements.md BDD-22~29 + I-8/9/10
- 最小验证结论（P2 §7）：pip download --platform 按目标平台拉 wheel 可行；sha256 用 hashlib 标准库

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P1-requirements.md（BDD-22~29）
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P2-design.md（§4.7 方案 + §7 minimal_validation）
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P0-brief.md（环境约束）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/AGENTS.md（项目约定 + 测试平台无关原则）
- 只读代码：agate/tests/conftest.py（fixtures 参照）
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
- 环境状态：worktree 分支 feat/TAG0008-version-management；P2 已 commit（ae2fe2b）
- 关键路径：AGATE_WORKSPACE=/home/kity/oclab/agate/.worktrees/agate-TAG0008/agate-workspace；测试目录 agate/tests/unit/
- 查证结果：被测模块 agate-pack-offline.py / install-offline.py **尚未实现**；最小验证已确认 pip download --platform / sha256 checksum 可行（P2 §7）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
