# 决策记录索引

记录 agate 协议演进过程中讨论过、做出过决策的问题——包括被否决的方案和否决的理由。目的是防止同一个问题被反复重新讨论一遍（每份记录都应该写清楚"为什么否决 A/B/C，为什么采纳 D"，不只是写结论）。

| 文档 | 问题 | 状态 |
|------|------|------|
| `agent-file-reading-guarantee.md` | 主 Agent 会不会真的去读协议文件，"按需读取"为何不可靠 | 已落地 |
| `main-agent-oversight.md` | 谁来监督主 Agent 自己的判断，LLM 裁判员是否可行 | 部分落地，方案C降级为开放问题 |
| `production-isolation-origin.md` | `[PROD_TOUCHED]` 机制的来历，T005/T006 生产环境事故的通用教训 | 已落地 |
| `t019-safety-net-pattern.md`（见 docs/reviews/agate-postmortem-T019-meta-review-2026-06-24.md） | T016+T019 两个案例的跨任务模式：主 Agent 系统性绕过现成安全网 | 待落地 |

新增决策记录时，按这个格式写：问题是什么 → 讨论过哪些方案及为何否决 → 最终采纳的方案及理由 → 状态（已决策待落地 / 已落地，落地位置写清楚）。
