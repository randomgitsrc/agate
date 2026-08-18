# 证据：BDD-18 — P5 卡落地「环境准备职责边界」（RM-AG0014 补充）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- Then「文件中新增一句明确：P5 verifier 默认不自行启动/维护运行环境」：新增段「**环境准备职责边界（本阶段落地）**：verifier subagent **默认不自行启动环境**——debug server、测试数据库、临时端口等由主 Agent（或 P0-brief 声明的单一责任方）统一准备好」—— 满足（「维护」亦由主 Agent 承担，与协议侧条款 1 的启动/维护/关停一致）。
- Then「环境由主 Agent 按 `verification_env` 声明统一准备并通过 dispatch-context 注入访问方式」：同段「通过 dispatch-context 注入访问方式」—— 满足。
- Then「多个并行 verifier 共享同一环境时，遵循 dispatch-protocol.md verification_env 节（BDD-11）定义的统一准备规则」：同段「多个并行 verifier 共享同一环境时更是如此，不允许各自启动。环境验证失败时的可重试/不可重试分类、批处理要求与止损轮次，一律按 dispatch-protocol.md「verification_env 失败处理协议」与「环境准备职责边界」执行」—— 指向 BDD-10/BDD-11 两节权威定义，满足。
- Then「本节只做落地引用」：末句「本卡片只做落地引用，不重复展开规则」；分类清单/轮次数值/归属判据均未在 P5 卡复制 —— 满足。
- 角色侧一致性：verifier.md（BDD-19）落到 verifier 身上的两条操作约束与本段结论一致（默认不自启环境；失败先分类再动作），卡片与角色文件无分叉。
- 关键词可 grep：段内含逐字「环境准备职责边界」，pytest 锚点 BDD-18 本轮独立实跑 PASSED。

## 实际文件文本摘录（HEAD）

### `agate/phase-cards/P5-verification.md` L124-125

```markdown
**环境准备职责边界（本阶段落地）**：verifier subagent **默认不自行启动环境**——debug server、测试数据库、临时端口等由主 Agent（或 P0-brief 声明的单一责任方）统一准备好，通过 dispatch-context 注入访问方式；多个并行 verifier 共享同一环境时更是如此，不允许各自启动。环境验证失败时的可重试/不可重试分类、批处理要求与止损轮次，一律按 dispatch-protocol.md「verification_env 失败处理协议」与「环境准备职责边界」执行，本卡片只做落地引用，不重复展开规则。

```

## 结论

**PASS** —— P5 卡新增职责边界落地段，明确 verifier 不自启环境、主 Agent 统一准备并注入访问方式，并以引用协议两节的方式处理失败与并行共享。
