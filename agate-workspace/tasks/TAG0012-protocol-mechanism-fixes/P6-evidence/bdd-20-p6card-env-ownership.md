# 证据：BDD-20 — P6/verifier 落地「环境准备职责边界」（RM-AG0014 补充）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- Then「文件中新增一句明确：P6 阶段的环境访问沿用 P5 已由主 Agent 准备的环境（若环境状态未变）」：「按包拆分并行（条件触发，受限模式）」节末新增段「**环境准备职责边界（本阶段落地）**：P6 的环境访问沿用 P5 已由主 Agent 准备好的环境（**环境状态未变时不重复起**）」—— 含 Then 要求的「若环境状态未变」条件，满足。
- Then「需要新环境时同样遵循 dispatch-protocol.md verification_env 节的统一准备规则」：同段「需要新环境时同样遵循 dispatch-protocol.md「verification_env 条件化」/「环境准备职责边界」的统一准备规则——由主 Agent 统一启动并通过 dispatch-context 注入访问方式」—— 指向 BDD-11 权威节，满足。
- Then「不由 verifier subagent 自行启动」：同段加粗「**不由 verifier subagent 自行启动**（多个并行 verifier 各自起环境会导致端口占用与资源竞争）」—— 满足，且给出后果与协议侧条款 2 一致。
- 引用式落地核对：失败处理不在本卡展开——「环境验证失败时的分类与止损见 dispatch-protocol.md「verification_env 失败处理协议」，本卡片不重复展开」—— 与 P5 卡（BDD-18）/ verifier.md（BDD-19）同款模式，三处无分叉。
- 关键词可 grep：段内含逐字「环境准备职责边界」，pytest 锚点 BDD-20 本轮独立实跑 PASSED。

## 实际文件文本摘录（HEAD）

### `agate/phase-cards/P6-acceptance.md` L184-185

```markdown
**环境准备职责边界（本阶段落地）**：P6 的环境访问沿用 P5 已由主 Agent 准备好的环境（环境状态未变时不重复起）；需要新环境时同样遵循 dispatch-protocol.md「verification_env 条件化」/「环境准备职责边界」的统一准备规则——由主 Agent 统一启动并通过 dispatch-context 注入访问方式，**不由 verifier subagent 自行启动**（多个并行 verifier 各自起环境会导致端口占用与资源竞争）。环境验证失败时的分类与止损见 dispatch-protocol.md「verification_env 失败处理协议」，本卡片不重复展开。

```

## 结论

**PASS** —— P6 卡新增职责边界落地段，覆盖「沿用 P5 环境（状态未变时）」「需新环境走统一准备规则」「不由 verifier 自启」三点。
