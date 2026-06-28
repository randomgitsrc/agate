# agate 协议回顾 — 来自 T025 的执行反馈（修订版）

> 基于 PeekView T025 user-page（P0-P7 完整执行，19 次 subagent 派发，8 次 gate 判定）
> 日期：2026-06-28
> 修订：补充 gate 信息密度量化数据 + 精确时间线

---

## 背景

T025 是一次典型的中等跨端任务（后端 User join + 前端三态 UI）。P0-P7 执行产生 **19 次 subagent 派发**，用户两次手动中止（均因主 Agent 在简单的 bash 命令发出之前已有过长静默）。

踩到的的协议摩擦分为两类：
- **A 类（产出→判定的距离）**：gate 判定的有效信息只有 1 行（exit code / grep count / Header status），但协议设计迫使主 Agent 在判定前消费几百行上下文。
- **B 类（派发→返回的往返）**：某些往返（评审双循环、写跑分离）的边际成本高于边际收益。

---

## 摩擦 1：gate 判定的信息密度比

### 现象

T025 的 8 次 gate 判定，主 Agent 的典型操作：

```
收到 subagent 返回摘要
  → Read 工具读产出文件全文（P1 353 行 / P2 775 行 / P6 两轮各 N 行）
  → 在心中逐条对照 dispatch-protocol.md「可判定门槛规范」表
  → 推演 state-machine.md 的状态转移规则
  → 扫描 5 种协议标记（SCOPE+/NEED_CONFIRM/CAPABILITY_GAP/PROD_TOUCHED/UPGRADE）
  → 执行实际判定命令（大部分时间只有：grep / exit code check / Header 字段读取）
```

**8 次 gate 的信息密度对比：**

| gate | 实际判定的命令 | 有效字节 | 文件阅读量 | 冗余比 |
|------|---------------|---------|-----------|--------|
| P1 | `grep NEED_CONFIRM`；`grep CAPABILITY_GAP`；确认 BDD ≥1 | ~30B | 353 行 | ~20:1 |
| P2 | `grep "status: approved" P2-review.md`；确认四字段 | ~20B | 775 行 + 3 份评审 | ~100:1 |
| P3 | `pytest -q` exit 0，`N failed` > 0，`N errors` = 0 | ~20B | 脚本源码 54 行 | ~10:1* |
| P4 | `pytest -q` exit 0，failed=0 | ~10B | 2 份实现记录 | ~20:1 |
| P5 | `pytest -q` exit 0，failed=0，grep PROD_TOUCHED | ~20B | 验证报告 + E2E 日志 | ~30:1 |
| P6 | `grep -c "FAIL" P6-acceptance.md` = 0 | ~10B | acceptance.md 全文 | ~50:1 |
| P7 | `grep -c "BLOCKER" P7-consistency.md` = 0 | ~10B | consistency.md 全文 | ~30:1 |

平均冗余比约 **30:1**。主 Agent 在每 gate 前静默消费了远超判定所需的信息量。

\* P3 的 10:1 不算高，但不是因为效率好——是因为 `check-tdd-red.sh` 脚本本身有 bug（裸 `pytest` 在 venv 项目中不可用），导致主 Agent 花了 3 轮调试才得到正确结果。

### 根因

agate 将 gate 的**定义**（dispatch-protocol.md「可判定门槛规范」表）和 gate 的**执行**（主 Agent 在现场跑命令）混在同一个文档里。gate 定义是"写一次就不变"的参考文件，但主 Agent 每次做 gate 都在现场重读这份参考——而参考本身的 95% 内容和当前 gate 无关（做 P3 判定时不需要看 P6 的 BDD 二值规则）。

更根本的原因：**协议没有"gate cheatsheet"概念**——一个每阶段只有一行的、只回答"跑什么命令 + 看什么输出"的紧凑参考。主 Agent 不得不自己从三个文件中提取。

### 建议 A

**新增 `~/.agate/gate-cheatsheet.md`**：

```markdown
# Gate cheatsheet — 每个阶段一条命令

| Gate | 命令 | 通过 |
|------|------|------|
| P1  | cd docs/tasks/{task} && grep -q NEED_CONFIRM P1-requirements.md && exit 1 \|\| true; grep -q CAPABILITY_GAP P1-requirements.md && exit 1 \|\| true | 两次 grep 均无命中 |
| P2  | grep "status: approved" docs/tasks/{task}/P2-review.md | 命中 |
| P3  | {project_test_runner} {test_dir} -q 2>&1 \| grep "failed" | failed>0, error=0 |
| P4  | git log --oneline -1 | 含 "P4" |
| P5  | {project_test_runner} -q; grep -r PROD_TOUCHED docs/tasks/{task}/ | exit 0, failed=0, PROD_TOUCHED=0 |
| P6  | grep -c "FAIL" docs/tasks/{task}/P6-acceptance.md | = 0 |
| P7  | grep -cE '^\s*-?\s*\[BLOCKER\]' docs/tasks/{task}/P7-consistency.md | = 0 |
| P8  | 从 P2 gate_commands 读取每个 package 的发布检查命令 | exit 0 |
```

主 Agent 做 gate 前只读这一行，不读三个协议文件、不读产出全文、不推演状态转移。

**额外收益**：cheatsheet 内容可被机械翻译为 `scripts/check-gate.sh {phase} {task_id}`，使 gate 判定从"主 Agent 推演"降级为"跑一个 bash 脚本 → exit code"。

**代价**：失去"分析产出文件质量"的副收益（如主 Agent 读全文时顺带发现的潜在问题）。但这个收益是偶然的、不均匀的——大部分 gate 判定中，读完 P2-design.md 775 行后主 Agent 没有发现评审未捕获的新 bug，只是浪费了上下文。

---

## 摩擦 2：dispatch prompt 的信息重复率

### 现象

19 次派发中，每次 dispatch prompt 的常量段如下（约占 prompt 的 60%）：

```
你是 {阶段} 的 {角色} 子 Agent。
读取并遵循：~/.agate/assets/execution-roles/{role}.md
项目约定（必读）：{CLAUDE/AGENTS.md}
环境隔离（强制）：...
分阶段落盘（默认启用）：...
输出 Header 规范：phase/task_id/type/parent/trace_id/status/created
返回格式：只返回路径 + 一句话摘要
```

这些在所有派发中完全不变。真正变的只有：角色名、任务描述、导航提示、输入文件路径。加起来约 15-20 行，内联模板却要求 70-100 行。

### 建议 B

**新增 `~/.agate/assets/templates/dispatch-base.md`**，包含所有不变段。主 Agent 派发时 prompt 压缩为：

```
你是 {phase} 的 {role} 子 Agent。
角色定义、项目约定、环境隔离、落盘要求、输出 Header、返回格式：全部见 dispatch-base.md

## 输入（自己读取）
- {paths}

## 任务
{1-2 sentence task}

## 导航提示（按需）
{节/文件名}
```

prompt 从 80 行压缩到 15 行。对 8-20 次派发/任务，节省 ~1,300 行 prompt 组织成本。

---

## 摩擦 3：评审角色的完全机械映射缺少 escape hatch

### 现象

P2 的评审触发是完全机械的：`domains: [backend, frontend]` → plan-eng-review + plan-design-review。

T025 的后端改动只是 `list_entries` 函数加 20 行管线 + 一个可选字段。plan-eng-review 发现了 BLK-1/BLK-2，但这两个 bug 都属于"逻辑漏洞"而不是"架构缺陷"——它们在 P3/P4 的生产级代码审查中也可能被发现。

两轮评审（6 次 subagent）占用了 P2 总时间的 ~80%。

### 建议 C

**在 P0-brief.md 中新增可选字段 `skip_reviews`**：

```yaml
skip_reviews:
  - plan-eng-review
  - plan-design-review
```

**判定规则**（写进协议，不靠主 Agent 临场感觉）：

| 可跳过 | 不可跳过 |
|--------|---------|
| 纯增量改动（不改变现有接口语义） | 新 table / new endpoint / new contract |
| 有先例的模式复用（如按现有 API 模式加字段） | 安全敏感（认证/权限/加密/密钥） |
| 改动量 ≤ 50 行（不含测试） | 涉及并发/性能/资源管理 |
| 单文件改动 | 跨 ≥3 个文件的协调改动 |
| 已有充分单元测试覆盖的模块 | 无测试覆盖的模块 |

默认行为不变（机械映射全开），但允许 P0 声明跳过。

---

## 摩擦 4：回归测试的全量模式不适应增量修复循环

### 现象

T025 走了 P4→P5→P6→P4fix→P5→P6 的回归修复循环。每次回到 P5，gate 规则都要求 `pytest -q` 全量跑（586 tests, ~106s）。

但 P6→P4 fix 改的只是 EntryListView 的 3 行代码（onMounted 补 loadEntries 调用 + chip 模式的 All tab 条件），全量 586 后端测试 100% 不会因前端改动而失败。

### 建议 D

**引入分层的 P5 gate**：

| 场景 | 触发条件 | gate 命令 | 理由 |
|------|---------|----------|------|
| 首次 P5 | `retries[P6] == 0` | 全量 `pytest -q` | 全部代码第一次验证 |
| P6→P4 回归 | `retries[P6] > 0` | 仅跑 P3 创建的测试文件 | 全量已在首次 P5 通过；回归修复是局部 bug |

注意：这不适用于涉及核心数据结构改动的任务（如改了 Entry 模型定义），因为级联破坏风险高。但对于增量功能（如 T025 只是给 list_entries 加参数），首次全量 + 回归增量是安全的。

---

## 摩擦 5：写跑分离对本地可控验证的不必要往返

### 现象

P5 verifier 写了 `e2e/user-page.spec.ts`（476 行），主 Agent 来跑 → 结果 16/24 fail。主 Agent 需要诊断是脚本 bug 还是实现 bug → 又是一轮思考。

verifier 自己在独立上下文跑，跑完返回结构化结果（exit code + 失败清单），主 Agent 直接验结果——少一轮往返。

### 讨论：不需要完全取消写跑分离

T019 的教训（subagent 内 Playwright 脚本 hang → 主 Agent 卡死数小时）是真实的。但 T019 和 T025 的区别在于：T019 的 Playwright 脚本**依赖跨平台的 CDP 连接**（WSL→Windows Chrome），是"不可控外部资源"；T025 的 Playwright 脚本是**本地项目内**的标准化测试框架。

### 建议 E

**将写跑分离从"默认"改为"按环境判定"**：

P0-brief.md 新增字段：

```yaml
verification_env:
  e2e_runtime: local          # local = verifier 自跑 / remote = 主 Agent 跑
  external_deps: false        # true = 涉及 CDP/远程 API/WebSocket 等可能 hang 的
```

| verification_env | E2E 谁跑 | 写跑分离 |
|-----------------|---------|---------|
| `e2e_runtime: local, external_deps: false` | verifier | 关闭 |
| `e2e_runtime: local, external_deps: true` | 主 Agent | 开启 |
| `e2e_runtime: remote` | 主 Agent | 开启 |

---

## 摩擦 6：gate 判定中的"第二次验证"过度（新增）

### 现象

P6 R2（18/18 PASS）后，我在 P7 gate 前做了：

1. 读 P7-consistency.md 全文
2. 检查每个一致性标注是否合理
3. 然后跑 `grep BLOCKER`（0 命中）
4. 确认 P8 已跳过（pruning 声明）
5. 推演 READY 转移
6. 写 .state.yaml
7. 写 active-tasks.md
8. 跑 `make debug-stop`
9. commit
10. 写交付小结

第 2 步（检查一致性标注是否合理）是对 P7 subagent 的**二次判断**——我已经信任 P7 subagent 的产出，却又在心里重做了一遍它的工作。

### 建议 F

**在 gate-cheatsheet.md 中标记每个 gate 的"信任等级"**：

```markdown
| Gate | 信任等级 | 说明 |
|------|---------|------|
| P1 | 手动 | NEED_CONFIRM/CAPABILITY_GAP 需要人确认，不过机器 |
| P2 | 信号 | 只看 status: approved，不重审设计 |
| P3 | 信号 | 只看 pytest exit code，不分析具体失败原因 |
| P4 | 信号 | 只看 commit log + exit code |
| P5 | 信号 | 只看 exit code + PROD_TOUCHED |
| P6 | 手动 | BDD 二值需要人确认中间态 |
| P7 | 信号 | 只看 grep BLOCKER count |
| P8 | 信号 | 只看各 package 发布命令 exit code |
```

"信号级"gate = 主 Agent 只跑命令，命令的 exit code = gate 判定。不做任何额外分析。

---

## 总结

| # | 摩擦 | 建议 | 影响范围 |
|---|------|------|---------|
| A | gate 信息密度 30:1 冗余比 | `gate-cheatsheet.md`（每阶段一行） | 所有项目的所有任务 |
| B | dispatch prompt 60% 重复 | `dispatch-base.md`（常量段提取） | 所有派发 |
| C | 评审机械映射无跳过 | P0 `skip_reviews` + 判定规则 | 所有中低风险任务 |
| D | 全量回归不适应修复循环 | 分层 P5 gate（首次全量/回归增量） | 所有有回归修复的任务 |
| E | 写跑分离对本地 E2E 多余 | P0 `verification_env` + 按环境判定 | 所有 UI 任务 |
| F | gate 中二次验证 subagent 工作 | gate-cheatsheet 信任等级 | 所有信号级 gate |

### 核心设计原则

**gate 的判定成本应该和它的信息密度成正比。** 一个 exit code 就能回答的问题，不应该需要读 300 行上下文才能得到。每个 gate 的定义文件中，90% 的篇幅是"为什么需要这个 gate"和"什么算通过/不通过"——这些对协议设计者有价值，对正在执行 gate 的主 Agent 没有。将两者分离：定义留在协议文件里，执行压缩到 cheatsheet 里。
