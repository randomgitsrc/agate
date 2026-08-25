# 决策记录索引

记录 agate 协议演进过程中讨论过、做出过决策的问题——包括被否决的方案和否决的理由。目的是防止同一个问题被反复重新讨论一遍（每份记录都应该写清楚"为什么否决 A/B/C，为什么采纳 D"，不只是写结论）。

| 文档 | 问题 | 状态 |
|------|------|------|
| `agent-file-reading-guarantee.md` | 主 Agent 会不会真的去读协议文件，"按需读取"为何不可靠 | 已落地 |
| `main-agent-oversight.md` | 谁来监督主 Agent 自己的判断，LLM 裁判员是否可行 | 部分落地，方案C降级为开放问题 |
| `production-isolation-origin.md` | `[PROD_TOUCHED]` 机制的来历，T005/T006 生产环境事故的通用教训 | 已落地 |
| `subagent-empty-return-root-cause.md` | subagent 空返回的根因分析（落盘指令可缓解）| 已落地（dispatch-protocol.md 派发模板默认含分阶段落盘指令）|
| `subagent-context-mechanism.md` | OpenCode/Claude Code subagent context 真实构成与平台差异 | 事实记录 |
| `docs/archived/reviews/agate-postmortem-T019-meta-review-2026-06-24.md` | T016+T019 两个案例的跨任务模式：主 Agent 系统性绕过现成安全网 | 已落地 |
| `design-structured-layer.md` | 协议规则结构化层设计（rules/*.yaml + S-1~S-6 双向一致性 gate，M0-M3 渐进） | 已落地（TAG0021，v0.60.0）|
| `design-risk-routing.md` | 风险分路由（ceremony routing）设计：客观信号算分，analyst 只解释不决定 | 已落地（TAG0019，v0.58.0）|
| `design-independent-judge.md` | 独立 Judge 机制设计（P6.5 信息隔离 + 三层防造假 + 事件账本） | 已落地（TAG0020，v0.59.0）|
| `dsh-integration.md` | DSH 深度集成扩展点清单（cordis 插件 / session hooks / workflow 派发） | 待立项（RM-AG0033）|
| `platform-extension-research.md` | 第四平台扩展调研（Codex/Cursor/Gemini CLI 能力对照 + 优先级建议） | 调研完成（RM-AG0034 素材）|
| `agateon-trademark-research.md` | Agateon 商标四辖区调研 + 注册建议 | 调研完成（RM-AG0035 前置）|
| `rename-recommendation.md` | 品牌改名决策记录（gatewise/agaton/turngate 淘汰原因 → 拍板 Agateon） | 已决策（RM-AG0035 转执行型）|
| `design-agateon-portal.md` | Agateon 门户设计（git 之于 GitHub：数据面/控制面分离 + 可验证性三层同构） | 待立项（v1.0 后，RM-AG0047）|
| `design-maintainability-gate.md` | 维护性反模式 gate 设计（模式层/检测器层分离，协议定义反模式语义） | 待立项（RM-AG0046）|

新增决策记录时，按这个格式写：问题是什么 → 讨论过哪些方案及为何否决 → 最终采纳的方案及理由 → 状态（已决策待落地 / 已落地，落地位置写清楚）。
