---
type: review
source: docs/reviews/T025-feedback.md
trace_id: agate-T025-feedback-review-2026-06-28
created: 2026-06-28
status: done
---

# T025 协议反馈评审

> 评审对象：`docs/reviews/T025-feedback.md`（6 条摩擦 + 建议 A-F）
> 评审依据：agate 核心设计原则——gate 可判定、Agent 自信判断不可信、质量环节不可裁减
> 评审日期：2026-06-28

---

## 评审原则

T025 反馈的核心观察——gate 判定信息密度 30:1 冗余比——是真实且有价值的。但建议中有 5 条的解法方向违背 agate 的一条根本约束：**Agent 的自信判断不可信**。"简单任务捅大漏子"不是偶然，是 Agent 能力的系统性局限。任何允许 Agent 跳过或裁减质量环节的机制，都是在"Agent 自信"这个脆弱基础上盖楼。

因此评审的判定标准只有一条：**该建议是否让质量环节更高效地无条件执行？** 如果是，采纳；如果它是让质量环节变成有条件执行，拒绝。

---

## 逐条评审

### A. gate-cheatsheet.md — 采纳（修正定位）

**原始建议**：新增 gate-cheatsheet.md，每个 gate 一行命令，主 Agent 只读这一行做判定。

**评审判定**：方向正确，但原始定位——"主 Agent 只读一行，不读三个协议文件、不读产出全文"——是危险的。gate 判定的**命令**可以提取，但 gate 判定的**过程**不能省略：

- P1 gate 不只是 `grep NEED_CONFIRM`——BDD 写得有歧义时需读上下文判断
- P2 gate 不只是 `grep status:approved`——评审 rejected 时需理解理由才能构造回流 prompt
- P6 gate 不只是 `grep -c FAIL`——FAIL 的根因决定回 P4 还是修验收脚本

cheatsheet 的正确定位：**导航索引，不是执行替代。** 它告诉主 Agent "这个 gate 跑什么命令"，减少"从三个协议文件里找判定规则"的重复劳动。但异常时必须读产出全文分析，不可仅凭 exit code 跳过。

**修正点**：

1. cheatsheet 每行加注释：`# 异常时必须读产出全文，不可仅凭 exit code 跳过分析`
2. cheatsheet 的项目级变量（`{project_test_runner}`、`{test_dir}`）从 P0-brief.md 的 `executor_env` 读取，不硬编码
3. cheatsheet 可被翻译为 `scripts/check-gate.sh`，但脚本只做"快速通过"路径——首次通过时省时间，异常时仍需人工分析

**收益**：每次 gate 判定省 30-90s 的"找判定规则"时间。19 次派发 × 8 次 gate ≈ 省 8-12 分钟。不损失任何质量保障。

### B. dispatch-base.md（常量段提取）— 拒绝

**原始建议**：把 dispatch prompt 的 60% 常量段提取到 dispatch-base.md，主 Agent 派发时只写 15 行变量段。

**评审判定**：节省的是主 Agent 写 prompt 的时间，不是 subagent 消费的上下文——subagent 读 dispatch-base.md 和读内联文本，上下文消耗完全相同。而且引入新风险：dispatch-base.md 更新后，正在执行的旧 subagent 可能读到旧版。内联虽然冗余，但保证每次派发的内容是原子一致的。

在当前架构下，内联冗余是最小的恶。不做。

### C. skip_reviews + 判定规则表 — 拒绝

**原始建议**：P0-brief.md 新增 `skip_reviews` 字段，配合可跳过/不可跳过的判定规则表。

**评审判定**：判定规则表写得清晰可执行，但问题不在规则本身，在于谁来执行。无论把 skip 决策放在 P0（需求阶段，不知道改动量）还是 P2（设计阶段，可能低估风险），都是让 Agent 做自信判断。T025 的 BLK-1/BLK-2（FTS early return 丢失 owner_found）就是"看起来简单的 20 行改动"里的逻辑漏洞——如果 Agent 在 P2 判定"后端只加了 20 行，可跳过 plan-eng-review"，这两个 BLOCKER 就会流到 P6 才被发现。

评审是 agate 质量保障的关键环节。P2 评审双循环的 6 次 subagent 是成本，但 BLK-1/BLK-2 的拦截证明了这个成本的必要性。**不提供逃逸口。**

不做 skip_reviews，不做判定规则表。评审全量执行。

### D. 分层 P5 gate（首次全量/回归增量）— 拒绝

**原始建议**：`retries[P6] > 0` 时 P5 gate 只跑 P3 创建的测试文件，不做全量。

**评审判定**：P5 全量回归的 106s 是安全冗余——它保障的是"P4fix 没有引入新回归"。增量测试的隐含假设是"改动的影响范围可预知"，但 Agent 对影响范围的判断不可信。P6→P4→P5→P6 多跑一轮全量测试是冗余，但这个冗余的代价是 106s，收益是"不会漏掉级联破坏"。

"为提升质量的阶段不能随意裁减"——这不需要进一步论证。

不做分层 P5 gate。首次和回归都跑全量。

### E. verification_env 按环境判定写跑分离 — 拒绝

**原始建议**：P0 新增 `verification_env` 字段，本地无外部依赖时 verifier 自跑 E2E，关闭写跑分离。

**评审判定**：T019 的教训（subagent 内 Playwright hang → 主 Agent 卡死数小时）没有过期。T025 没复现只是因为 T025 的 E2E 恰好简单。hang 的风险不取决于"本地 vs 远程"，取决于"subagent 进程是否可能阻塞在 I/O 上不返回"。本地 Playwright 一样可以 hang（端口占用、浏览器崩溃、测试死锁）。

写跑分离的代价是一轮 subagent→主 Agent 的往返，收益是主 Agent 不会因 subagent hang 而卡死。在当前 Agent 基础设施下（subagent 无 timeout kill 能力），这个 trade-off 仍偏向保留写跑分离。

如果未来 subagent 有了可靠的 timeout + kill 机制，再重新评估。不加 `verification_env`。

### F. gate 信任等级 — 不单独做，合并进 A

**评审判定**：信任等级（信号级/手动）是 A 的 cheatsheet 的一列信息。但 A 已修正为"导航索引而非执行替代"后，信任等级的"信号级"标签会产生误导——如果异常时必须读全文分析，那所有 gate 在异常时都是"手动"，"信号级"标签暗示可以不看全文。

不做单独的信任等级列。A 的 cheatsheet 加一行全局注释覆盖此需求。

---

## 裁决总览

| # | 建议 | 裁决 | 理由 |
|---|------|------|------|
| A | gate-cheatsheet.md | ✅ 采纳（修正：导航索引，非执行替代） | 降低"找判定规则"的重复成本，不裁减质量环节 |
| B | dispatch-base.md | ❌ 拒绝 | 不省 subagent 上下文，引入版本一致性风险 |
| C | skip_reviews | ❌ 拒绝 | Agent 自信判断不可信，评审不可跳过 |
| D | 分层 P5 gate | ❌ 拒绝 | 质量环节不可裁减，增量测试假设影响范围可预知 |
| E | verification_env | ❌ 拒绝 | 写跑分离隔离 hang 风险，当前无 timeout kill 机制 |
| F | 信任等级 | ❌ 合并进 A | 修正后的 cheatsheet 不需要此分类，全局注释覆盖 |

**6 条建议中采纳 1 条（修正版），拒绝 5 条。**

---

## 核心结论

T025 反馈最有价值的贡献不是 6 条具体建议，而是 **gate 判定信息密度 30:1 冗余比** 这个量化事实。它指向的真实问题是：主 Agent 在每个 gate 前做了一件完全可以预计算的工作——从三个协议文件中提取"这个 gate 跑什么命令"。cheatsheet 解决的是这个提取成本，不是 gate 本身的必要性。

所有被拒绝的建议共享同一个模式：**试图让 Agent 判断"这个环节是否必要"，然后跳过它认为不必要的部分。** 这条路走不通——Agent 的自信判断是系统性弱点，agate 的设计必须绕过这个弱点，而不是依赖它。

优化方向：**降低执行成本（导航索引），不裁减环节。**
