# 证据：BDD-22 — check-gate.py 校验逻辑按 P2 设计结论决定是否扩展（RM-AG0016）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- 验收标准（P1 Then 第二分支 + P6 dispatch-context 约束 7）：「若 P2 决定该字段仅作文档约定不做脚本硬校验，则本 BDD 以『P2-design.md 中显式声明该决定 + 理由』为通过标准」+「test_protocol_mechanism_anchors.py 测试文件存在且全部用例可运行」。
- 判据 1「P2-design.md 显式声明该决定」：§3.7 标题即「BDD-22 分支决定：不做脚本硬校验，仅文档约定 + grep 断言审计测试」，正文「**决定**：`check-gate.py` 不新增 `timeout_seconds` 校验函数。」—— 显式，满足。
- 判据 2「+ 理由」：§3.7 给出三条理由——① `timeout_seconds` 对 P5/P6 无运行时消费方（P5/P6 由 subagent 自跑 gate 命令，`check-gate.py` 不是命令执行器，不像 P3 有 `run_test_with_formatter()` 的「读字段 → 施加真实 subprocess timeout」消费链路）；② 强行加只能做「数值合法性」级浅校验，收益有限且增加 check-gate.py 复杂度/测试面；③ BDD-22 明确两种结果都是合法收敛，选文档约定分支并把回归拦截压力转移到 §3.6 的 grep 断言审计测试 —— 理由具体、指向代码事实，满足。
- 判据 3「测试文件存在且全部用例可运行」：`agate/tests/unit/test_protocol_mechanism_anchors.py` 存在（28 条 parametrize 用例覆盖 BDD-1~21 + BDD-15b）；本轮 P6 独立实跑 `timeout 120s python3 -m pytest agate/tests/unit/test_protocol_mechanism_anchors.py -v` → **28 passed，exit 0**（逐条 PASSED 列表见 shared-p6-command-output.log 第 1 节）—— 满足。
- 决定与实现一致性核对：P4-implementation.md §5 声明 `check-gate.py` 零改动；本轮独立核实 `git show 27509a2 --stat` 的 20 个改动文件中**不含** `agate/scripts/check-gate.py`（改动仅 12 个协议文件 + 任务工作区文件 + 1 个 review 文档）—— 决定与落地一致，无「声明不改却改了」的矛盾。
- 「两种结果都是合法收敛，不预设哪种一定发生」：本次收敛到文档约定分支，属 P1 允许的两个分支之一，非降级或裁剪。

## 实际文件文本摘录（HEAD）

### `agate-workspace/tasks/TAG0012-protocol-mechanism-fixes/P2-design.md` L211-219

```markdown
### 3.7 BDD-22 分支决定：不做脚本硬校验，仅文档约定 + grep 断言审计测试

**决定**：`check-gate.py` 不新增 `timeout_seconds` 校验函数。

**理由**：
1. `timeout_seconds` 对 P5/P6 目前无运行时消费方——P5/P6 由 subagent 自己跑 `gate_commands.{key}` 命令并观察结果，`check-gate.py` 不是命令执行器，不像 P3 有 `run_test_with_formatter()` 那样"读字段→施加真实 subprocess timeout"的消费链路
2. 若强行加脚本校验，只能做到"数值合法性"级浅校验（类似 `_gate_p2_dispatch_plan` 对 `parallel_limit` 的 `int ≥1` 校验模式），但一个格式合法却没有代码读取它去真正生效的字段，校验收益有限，且会增加 `check-gate.py` 复杂度/测试面，与 P0-brief"少量脚本 schema 字段"定性不完全匹配（"少量"更贴合"文档约定优先"）
3. BDD-22 明确"两种结果都是合法收敛"，选择文档约定分支，把回归拦截压力转移到 §3.6 的 grep 断言审计测试（P1 已强制要求，无论 BDD-22 走哪个分支都需要）

```

## 结论

**PASS** —— P2-design.md §3.7 显式声明「不做脚本硬校验」的决定并给出三条理由；锚点测试文件存在且 28/28 用例本轮独立实跑通过；check-gate.py 确未被改动，决定与落地一致。
