# 证据：BDD-14 — dispatch-prompt.md 同步 BDD-13 的命令超时兜底 + progress 心跳段落（RM-AG0016）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- Then「该模板文件中的对应段落（「分阶段落盘」/「执行顺序」节）同步包含与 BDD-13 一致的命令超时兜底 + 命令前 progress 要求」：三处同步落地——①「执行顺序」第 4 步改为「按 dispatch-context 约束执行任务（**跑任何 bash 命令前先设超时**，见下方「命令超时兜底」）」；②「分阶段落盘」段追加「落盘粒度还包括**每条 bash 命令执行前**追加一行（要跑什么、预期多久）」；③ 新增 `## 命令超时兜底（层级 4，所有 bash 命令强制）` 段 —— 满足。
- 语义逐条对照（与 dispatch-protocol.md 新增内容）：倍数规则一致（均为「取值 = 预期耗时 ×1.5」）；取值来源一致（`_timeout_seconds` 已声明 → 直接取该值；未声明 → 经验估算 ×1.5）；失败后动作一致（① 停止执行、不自行更换命令、不深入诊断 ② 往 progress 写一行「卡在哪条命令、跑了多久、什么输出」③ 返回主 Agent 决定加长超时重跑/换策略/升级人工）；触发条件一致（超时**或非预期失败**）；层级归属一致（层级 4）—— 无矛盾表述。
- 唯一措辞差异及其性质：协议侧写 `timeout {N}s {命令}`，模板侧写 `timeout 180s <你的命令>`（并把 `{key}_timeout_seconds` 具体化为 `P5_e2e_timeout_seconds: 300`）。原因是 dispatch-prompt.md 是**渲染模板本体**，既有回归 `test_rp_13_no_residual_placeholders_except_whitelisted` 禁止残留 `{N}` / `{key}` 花括号占位符（P4-implementation.md §2.2 记录）。语义等价（同一取值规则的具象写法），不构成矛盾。
- 分层关系不重复展开：模板侧只写「与脚本内部硬超时（Playwright/Node 脚本 HARD timeout）的分层关系见 dispatch-protocol.md「命令超时兜底与既有超时机制的分层关系」——外层取值须留够内层完整走完的余量」，四层对照表仍只在协议侧 —— 符合文件头「协议文件为权威来源」的定位。
- Then「`check-protocol-consistency.py` 的既有一致性检查口径覆盖到这两处文本，不因本次新增内容产生新 ERROR」：本轮 P6 独立实跑 `timeout 180s python3 agate/scripts/check-protocol-consistency.py --strict` → **0 ERROR，279 WARNING**（CHECK 1/3/4/6/7/8/9/11 全 ✅ PASS），与 P4/P5 记录的改动前基线一致 —— 满足（输出见 shared-p6-command-output.log 第 2 节）。
- 双源关键词计数核对（shared-p6-command-output.log 第 4 节）：`命令超时兜底` protocol=6 / prompt=3，`层级 4` 7/1，`×1.5` 6/2，`每条 bash 命令执行前` 1/1，`不自行更换命令` 1/1，`不深入诊断` 1/1 —— 两侧均非零，权威侧更详尽、副本侧精简，符合「同步不等于逐字复制」的既有惯例。

## 实际文件文本摘录（HEAD）

### `agate/assets/templates/dispatch-prompt.md` L27-47

```markdown
## 执行顺序
1. 读取 dispatch-context 派发指引（目标/约束/上游关联/输入文件）
2. 读取角色定义文件和项目约定
3. 按输入文件列表逐一读取，每读完一个追加 progress
4. 按 dispatch-context 约束执行任务（跑任何 bash 命令前先设超时，见下方「命令超时兜底」）
5. 写产出文件到约定路径
6. 自检产出文件（Header/内容/证据）
7. 返回路径 + 一句话摘要

## 分阶段落盘（重要，默认启用）
每读完一个输入文件或完成一个关键步骤，立即把发现追加写入 {AGATE_WORKSPACE}/tasks/{Txxx}/P{N}-progress.md（bash 追加模式）。这样即使你最终无法产出完整报告，progress 文件也能让主 Agent 知道你做了什么。不要等所有文件读完再一次性写——逐条写。
落盘粒度还包括**每条 bash 命令执行前**追加一行（要跑什么、预期多久），命令挂死时主 Agent 从 progress 就能看出卡在哪条命令。

## 命令超时兜底（层级 4，所有 bash 命令强制）
执行任意 bash 命令前必须设 shell 层 timeout，不允许无超时裸跑：`timeout 180s <你的命令>`（秒数按下面算；或用工具自带的 timeout 参数）。
取值 = 该命令预期耗时 ×1.5：
- P2 的 `gate_commands` 里该命令对应的 `_timeout_seconds` 声明（如 `P5_e2e_timeout_seconds: 300`）已给出 → "预期耗时"直接取该值
- 未声明（含绝大多数非 gate 的日常 bash 调用）→ 按经验估算预期耗时，再 ×1.5
超时或出现非预期失败后的动作固定：① 停止执行，不自行更换命令、不深入诊断；② 往 progress 写一行（卡在哪条命令、跑了多久、什么输出）；③ 返回主 Agent 决定加长超时重跑 / 换策略 / 升级人工。
与脚本内部硬超时（Playwright/Node 脚本 HARD timeout）的分层关系见 dispatch-protocol.md「命令超时兜底与既有超时机制的分层关系」——外层取值须留够内层完整走完的余量。

```

## 结论

**PASS** —— 执行顺序 / 分阶段落盘 / 新增命令超时兜底段三处同步落地，与协议侧语义逐条一致、无矛盾，且 consistency --strict 本轮实跑 0 ERROR。
