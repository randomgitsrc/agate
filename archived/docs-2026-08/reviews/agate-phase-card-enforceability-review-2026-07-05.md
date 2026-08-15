---
review_date: 2026-07-05
reviewer: main
review_target: docs/plans/agate-phase-card-enforceability-2026-07-05.md
type: 专家评审（设计方案，实证驱动）
method: 跑脚本核对 PHASE 前缀 / 现有 dispatch-context 惯例 / 卡片行数；对 hook 伪代码做静态求值
---

# 对「Phase Card 可执行性强化」方案的专家评审

## 总判定

**问题识别对，方案方向对，但方案 C 仍是"更精致的 nudge"而非 barrier——而计划的决策表把它标成"行为层解决 ✓"，这是言过其实。** 外加 hook 伪代码有两个会导致 100% 误拦的具体 bug。建议先修 bug，再诚实地重判"C 到底解决了几层"。

计划回应的核心矛盾是真的、且尖锐：**全量读→爆窗；用 map→不知道 agent 真读没。** 原 Phase Card 计划确实默认了"agent 看到 mapping 会自觉遵循"这个**认知假设**。把它暴露出来、要求换成**可执行保证**，是有价值的一步。问题在于 C 的机制没有真正兑现这个目标。

---

## F1（架构级）：方案 C 的"行为层解决 ✓"言过其实——它是条件式检查，仍是 nudge

计划决策表（第 105-111 行）给方案 C 打的是「行为层解决 ✓」。但看 hook 机制（步骤 3）：

```bash
DC_FILE="$TASK_DIR/P${PHASE}-dispatch-context.md"
if [ -f "$DC_FILE" ]; then   # ← 只有文件存在才检查
    ... hash 校验 ...
fi
```

**这个 hook 只在 dispatch-context.md 存在时才生效。没有任何机制强制它必须存在。** 我实测确认：

```
$ grep -rn "dispatch-context 必须存在\|require.*dispatch" agate/scripts/
（无 — 现有 hook 对 dispatch-context 全是"存在才查"，无 forcing function）
```

所以 agent 的绕过路径极简单：**不生成 dispatch-context.md，直接 commit。** hook 的 `-f` 守卫直接跳过，Phase Card 完全不受强制。这不是 barrier——是"如果你自愿走这条路，就得走对"，本质仍是 nudge。

计划自己在边界小节（第 275-279、285 行）半承认了这点（"主 Agent 绕过 subagent 自己写代码，整个链条失效"）。但**决策表的"行为层 ✓"没有反映这个条件性**。这正是项目已经退休的"anti-forgery"框架的同一个病根——**用 artifact 在场冒充强制力**。用 nudge/barrier 分类学量一下：C 抬高了绕过成本（要么正确嵌卡片、要么放弃派 subagent），但没堵死绕过路径。

**建议二选一**：
- **(a) 加 forcing function 让它真成 barrier**：对 P2/P4（会派 subagent 的阶段），commit 该阶段产出时**要求** `{PHASE}-dispatch-context.md` 存在，否则 exit 1。这样才把"行为层"真正关上。
- **(b) 诚实降级表格**：把 C 的"行为层 ✓"改为"部分（仅当 agent 走 subagent 派发路径）"，并在标题去掉"强化可执行性"里的绝对感。

不建议维持现表述——它会让读者以为可执行性已经解决，而实际只解决了"自愿走对流程时不许糊弄"。

---

## F2（核心）：hash 校验证明"字节在场且最新"，不是"agent 读了卡片"

即便 dispatch-context.md 存在且 hash 匹配，它证明的是：**嵌入的卡片字节 = 当前卡片文件字节**。它不证明 agent 读过、理解过、或据此执行。

agent 完全可以：

```bash
agate-next-card.sh P3 >> P3-dispatch-context.md   # 机械粘贴，一个字没读
```

hash 照样通过。这和 T046「用 1 行空文本文件过 evidence gate」、以及项目反复强调的「自报 vs 客观证据」是同一类：**artifact 在场 ≠ 它代表的认知动作发生了。**

所以 F2 的结论：hash 机制的真实价值是"防止粘贴了过期/篡改的卡片"（防漂移），**不是**"保证 agent 用了卡片"。计划不应把它算作行为层的解决手段。它属于信息层的完整性保障（确保 agent 手里的卡片是最新版），这个价值真实但有限。

---

## F3（实现 bug，会导致 100% 误拦）：hook 伪代码两处缺陷，读代码看不出，跑一次才知道

### (a) `P${PHASE}` = "PP3" —— PHASE 已含 P 前缀

实测 pre-commit-gate.sh：`PHASE=$(read_state_phase ...)` 得到的是 **"P3"**（case 分支是 `P0) P1)`、`check-gate.sh "$PHASE"` 收 "P3"）。而现有惯例文件名就是 `{PHASE}-dispatch-context.md`——实证：

```
check-p6-provenance.sh:105  DISPATCH_CTX="$TASK_DIR/P6-dispatch-context.md"
```

即前缀是 `${PHASE}` 不是 `P${PHASE}`。伪代码的 `P${PHASE}` → "PP3-dispatch-context.md"，且 `agate-next-card.sh P${PHASE}` → `agate-next-card.sh PP3` → CLI 判为无效 phase（exit 2）→ EXPECTED 空。

### (b) hash 两侧规范化不对称 —— 即使诚实输入也必然 mismatch

- **Embedded 侧**：`awk` 区间提取 + `grep -v '^<!--'` + `grep -v '^\`\`\`'` + `sed '/^$/d'`（去注释/fence/空行）
- **EXPECTED 侧**：`agate-next-card.sh PHASE` **原始输出**——按步骤 1，它含 `## 当前阶段卡片：P3` + `路径：...` + `---` 分隔头，且**不经**上面的 strip

两侧 hash 的是不同字节串。**即使 agent 完全正确地嵌入卡片，hash 也永远不相等。**

### 合并后果

按伪代码实现，这个 2p hook 会 **100% 拦截所有 dispatch-context.md**（包括正确的）——(a) 让 EXPECTED 恒空，(b) 让两侧字节恒不等。这正是项目 `printf '%s'` 回归、P4 鸡生蛋悖论那一类——**静态读代码看不出，必须建真实 repo 实跑 commit 才暴露**。步骤 7 的"实跑：注入→commit 成功"是对的，但要确保真跑到 hash 相等这一步，而不是止于"文件生成了"。

**修法**：`P${PHASE}` → `${PHASE}`；EXPECTED 侧套用与 embedded 侧完全相同的提取+strip，或者反过来让两侧都直接 hash CLI 原始输出（更简单：dispatch-context 里原样嵌入 CLI 全部输出，hook 也 hash CLI 全部输出，两边不做任何 strip）。

---

## F4（软）：CLI 的"机械化决策层"价值被高估

计划说 CLI 把决策"从 agent 内部挪走"（第 33 行），方案 A 行打「决策层解决 ✓」。但 agent 仍要：读 .state.yaml → 取 phase=P3 → 决定调 `agate-next-card.sh P3`。这和"读 mapping 表 → cat P3 卡片"的决策数量相同——都是"知道自己在 P3 且选择去取 P3 的内容"。CLI 没有移除任何 agent 决策，只是把 `cat phase-cards/P3-tdd.md` 换成 `agate-next-card.sh P3`。

CLI 的**真实价值**是：给 hook 提供一个**可在 commit 时复算的权威 hash 源**（F2 的防漂移）。这是好的，但它是 hash 机制的支撑件，不是"决策层机械化"。建议把方案 A 的定位从"机械化决策层"改为"提供权威卡片源 + 防漂移锚点"。

---

## F5（惯例）：卡片行数又是凭记忆非实测

计划风险表引"实测卡片行数（97/102/72/85/88 行）"。实际 `wc -l`：

```
P0=51 P1=69 P2=104 P3=65 P4=99 P5=74 P6=87 P7=63 P8=90
```

引用的 5 个数字对不上任何实际子集（最接近 P4=99≈97、P2=104≈102，其余都不匹配）。结论（"单张 ~100 行，装得下"）成立——最长 P2=104 也远低于窗口，所以这条不影响判断。但**又是"实测"字样下写了没实测的数字**。项目刚在 meta-review 虚构 git 统计上栽过，同一惯例问题再提醒一次：**写"实测"就真跑 `wc -l`，别从记忆里填。**

---

## 正面

1. **enforceability gap 是真洞察**。"map 存在 ≠ agent 会读"这层，原 Phase Card 计划确实默认掉了。把认知假设换成可执行保证，方向正确。
2. **"不解决什么"诚实**。主 Agent 绕过 subagent 自己写代码 → 整链失效，明确归给 issue #003 的主 Agent 单点故障。这个自我设限是对的。
3. **三层分解（信息/行为/决策）**是有用的分析框架。
4. **拆 3 个独立可回滚 commit** 是好工程实践。
5. **方向上契合已有惯例**：agate 已有 `{PHASE}-dispatch-context.md`（check-p6-provenance 已对其做内容约束、check-scope-resolved 已扫它）。方案 C 复用这个 artifact 是对的——虽然计划没点明这层先例，但落点一致，说明设计有连贯性。

---

## 建议清单

| # | 建议 | severity |
|---|------|----------|
| 1 | 修伪代码：`P${PHASE}`→`${PHASE}`（PHASE 已含 P 前缀，实测确认） | 高（会 100% 误拦） |
| 2 | 修 hash 两侧规范化不对称——两边 hash 同一字节串（推荐都用 CLI 原始输出，零 strip） | 高（会 100% 误拦） |
| 3 | 决策：要么加 forcing function（P2/P4 commit 要求 dispatch-context 存在）让 C 真成 barrier；要么诚实把表格"行为层 ✓"降级为"部分" | 高（架构诚实） |
| 4 | 不把 hash 校验算作行为层解决手段——它是信息层防漂移，不证明"读了卡片" | 中 |
| 5 | CLI 定位从"机械化决策层"改为"权威卡片源 + 防漂移锚点" | 低 |
| 6 | 卡片行数改为真实 `wc -l` 值，或删掉具体数字只留"均 <110 行" | 低（惯例） |
| 7 | 步骤 7 实跑必须跑到"hash 相等 → commit 成功"，不止于"文件生成" | 中（验证纪律） |

## 一句话结论

**问题抓得准（从认知假设转向可执行保证），但方案 C 兑现得不彻底**——它仍是条件式 nudge，且 hook 伪代码会 100% 误拦。先修 F3 两个 bug，再就 F1 做出选择：**要么给它装上 forcing function 真正成为 barrier，要么在表格里诚实承认它只解决了"自愿走对流程时不许糊弄"。** 别让"可执行性强化"这个标题承诺一个机制没兑现的东西——这正是项目退休"anti-forgery"框架时守住的那条诚实底线。
