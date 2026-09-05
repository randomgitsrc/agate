# 博客选题清单（backlog：候选先入库，写之前定优先级）

> 选题纪律：候选题先记录在此（角度一句话 + 素材现状），开写前才升级成正式任务，走
> `publish-checklist.md` 全流程。避免"每次现想选题"和"好想法丢失"。
> 已发布文章的弧线见下表，新选题必须说明它**补哪一层**、与已发的不重叠。
> **选题依据三件套（2026-09-04 固化）**：弧线节奏（愿景篇预告的剩余节拍）+ 层次缺口 +
> 素材成熟度；**单一外部信号（一条评论/一个赞）只做旁证、不驱动选题**——样本太小，
> 把"唯一"当"全部"大概率干扰判断。
>
> **命名说明**：本文件是 site/ 博客的**选题清单（backlog）**，与协议侧任务数据
> `agate-workspace/roadmap/`（RM 卡片、P8 gate 硬校验其回写）是两套东西，互不相通——
> 博客选题不走协议卡片、不进 RM 状态机。

## 已发布弧线（截至 2026-09-03）

| 篇 | 标题 | 管的层次 |
|---|---|---|
| post-01 (08-26) | Our AI Safety Net Depended on the Agent Being Honest. It Wasn't. | 一次真实失败（事故复盘） |
| post-02 (08-27) | Agateon: verify AI agents the way a build system verifies a compiler | 项目介绍（是什么/为什么） |
| post-03 (08-28) | Is it done, or does it just look done? A ladder of evidence | 方法框架（证据阶梯 + 审计清单） |
| post-04 (08-30) | The right to look away: how gates buy autonomy | 收益面（注意力经济学：验证买到"可以不看"） |
| post-05 (08-31) | We keep trying to break our own gates | 自我指涉（验证验证者：对抗性测试 + 独立 judge） |
| post-06 (09-03) | You can't delegate what you can't verify | 愿景北极星（信任税 → 委托边界由验证/判断力决定） |

## post-04（已发布 2026-08-30，本节留档）

选题方向：用户提出"插播一个工程化 loop / 解放注意力"的角度，确认后走完 publish-checklist 全流程。
评审 gate 拦下一处方向性事实错误（thin 路径的验证阶段 P5/P6 是**保留**而非裁剪——"薄化仪式不薄化验证"），复核 PASS 后发布。

- **角度**：前三篇全是"别信、去验"（防 вниз），这篇插播讲验证买到了什么——**你为什么可以不看**。
- **核心反直觉论点**：门禁不是增加监督负担，而是把监督自动化。没有客观证据的自主 = 无界风险，
  你被迫全程盯着；gate 读了 agent 伪造不了的证据，机器才能自己往前推，人只在状态机规定的
  决策点被打断。**自主性是用可验证性买来的，不是用信任换的。**
- **金句方向**："You hired an agent and became its supervisor." / "Interruption is a scheduling
  problem"（回应 post-02 dev.to 评论——版本化状态把中断变调度问题，这篇展开讲注意力账本）。
- **结构草案**：
  1. hook：雇 agent 干活，结果自己成了全职监工——盯着的每一分钟不是因为需要你，是不敢不看
  2. 为什么：无证据自主 = 无界风险 → 注意力被信任问题绑架
  3. 机制：把"何时需要人"变成状态机显式事件——PAUSED（重试超限/回退≥2 强制暂停）、
     NEED_CONFIRM、`[SCOPE+]→[SCOPE_RESOLVED]`（需求歧义必须人解）、P8 发布决策；
     其余时间 orchestrator 派 subagent → gate → 下一阶段，人不在场
  4. 注意力按风险分配：ceremony 路由（agate-risk-score 算分 → thin/standard/full，fail-closed，
     check-routing 校验"声明薄于算分"即拦）——低风险快走，高风险拉人
  5. crash = pause：版本化状态让"回来接着推"成立（引 post-02 那条评论的框架）
  6. 诚实局限：解放的前提是 gate 读真证据（回指 post-03 阶梯）；人的决策点不是零而是
     被设计出来——把人的注意力留给机器验不了的判断（rung 5）
- **素材现状**：机制全部存在且已在 post-01/02/03 埋过伏笔（PAUSED=check-state-transition.py、
  SCOPE=check-scope-resolved.py、routing=check-routing.py+agate-risk-score.py、
  NEED_CONFIRM=check-gate.py、派发循环=agate-next-card/render-dispatch-prompt）。
  数字素材（25 任务里 PAUSED 几次）留给「数字复盘」篇，此处可粗提。
- **需核实**（写稿时）：routing 的实际拦截案例、PAUSED 真实发生次数（workspace 数据）。

## Backlog（按优先级）

0. ~~**【愿景北极星篇】Agateon 最终是什么**~~ → **已发布（post-06，2026-09-03）**。A+B 合一 C 引子落地为
   "You can't delegate what you can't verify"：hook=你雇 agent 却成了它的监工，TL;DR=上限不是模型 IQ
   而是你能检查多少，正文给"今天到哪一步"（四件机制事实）+ "还差什么"（四条诚实缺口，含
   **"We don't yet have long-run data... That's the next honest post"** 的线上承诺——数字复盘篇的接力锚）。

1. **【下一篇正式选题·2026-09-04 用户确认】数字复盘·重构版：agent 工作流不埋点 = 没发生**。
   **选题方法教训（09-04 两轮纠偏后固化）**：单一外部信号（一条评论/一个赞）样本太小，只记录做旁证，
   不驱动选题；选题 = 弧线节奏（愿景篇已预告本篇是下一拍）+ 层次（补"实证/埋点课"层）+ 素材成熟度。
   **主题（对外的埋点课，不是对内的日志导读）**：给读者一套可搬走的埋点问题集——
   ①你的 agent 工作流现在靠什么回答"它干得怎么样"（记忆/感觉/截图？）②该记什么事件
   （gate_run/状态转移/复核判决的最小词表）③天真指标怎么骗人（exit 2 反转只作例证，不作钩子：
   我们的账本天真读数"75% 失败"，读懂语义后真相是 86 次里只真拦了 2 次）④覆盖边界怎么划
   （账本只覆盖 TAG0021+ 的 10 任务、终点=P6.5 judge——先说清楚数的是什么，再谈数）。
   **读者看完的下一步动作**：本周给自己 agent 的运行加一个事件日志（哪怕一行 JSON 一行），
   用三个问题审计它。**兑现 post-06 线上承诺**（"That's the next honest post, once the numbers accumulate"）。
   - 结构草案：hook=问读者"上个月你的 agent 干了多少活、拦了多少次、返工了几回——你答得出来吗"
     → 为什么记忆不可信（我们自己也不知道，直到埋了账本）→ 最小事件词表（三类事件 + hash 链防篡改）
     → worked example：我们账本的真实发现（86 gate_run 只 2 次真拦截 / P4 进入 14 次≥4 回返工可见 /
     零 PAUSED：逃生门存在但 10 任务零触发——机制存在≠被需要，这也是数据）→ 天真指标会骗人（exit 2）
     → 覆盖边界（10/31 任务、P6.5 止）→ 你的三问题行动清单。
   - **与已发篇分工**：post-05 讲"我们攻击 gate"（对抗性），本篇讲"运行数据怎么说"（埋点课）；
     post-04 讲"机制能买到什么"（理论），本篇讲"怎么知道实际买到多少"（测量方法）。
   - **素材库存（09-05 写稿时全量核验修正）**：账本 TAG0021+ 共 10 任务（08-22→09-03）；
     206 事件 = gate_run 86 + state_transition 89 + judge_verdict 31；gate_run exit：2×62 / 0×22 /
     **1×2（真拦截=TAG0027 P4，09-02 23:31/23:33，git 全分支无对应 commit——被拦尝试只活在账本）**；
     **零回退**（from→to 全正向；P3→P4×14 是 P4 阶段多次 commit 尝试，09-04"≥4 回退"推断已证伪）；
     **PAUSED 零事件且 hook 结构性跳过**（pre-commit-gate.py L303：PAUSED/READY/DONE 不产事件——
     仪表盲区，exit2-resolution 文件也是 0；此缺口值得协议侧登记 DEBT，尚未登记）；
     派发轮次重试 17/31 任务（.state.yaml retries：round/failure_mode，另一套测量）；
     账本终点全部=P6.5 judge；P7→P8 仅 4 个事件（TAG0022/26/30）；
     judge 31 verdicts/10 任务（check-events.py 限每 P6.5 ≤2）；哈希链校验可用：
     `python3 agate/scripts/check-events.py <task_dir>` → 0 exit。

2. ~~**对抗性测试：我们故意弄坏自己的 gate**~~ → **已发布（post-05，2026-08-31）**。素材落点：
   check-tdd-red.py 的 A/B 类红灯、TAG0020-independent-judge（三层防造假 / exit code 才是门槛）、
   评审 gate 自指演示。

3. **不需要运行时的协议：状态为什么放版本化 Markdown**——补"设计课"层（为什么是文件不是数据库：
   no daemon / 审计=读文件 / diff=git / Windows symlink 教训 / 规模上限诚实）。
   注意与 post-04 素材交叠（版本化状态/中断恢复），明确分工：post-04 讲"注意力经济学"，
   此篇讲"为什么是文件不是数据库"，引用不复述。

4. **角色分离：orchestrator 永远不写代码**——独立 subagent 干活 + 独立 judge 评审。
   部分素材可并入 post-04；单写则需更多第一手案例。

5. **【候选·转化型】第一人称委托实录：把一个真实任务交给 agent 全程跑一遍**——
   系列缺口：6 篇全是 why/trust，没有一篇"show me"（任务真实生命周期的第一人称体验：
   每次人被打断在哪个决策点、gate 拦了什么、交回来什么）。**转化潜力最高**（读者看完最接近
   "我也要装"），但素材成本最高：需现跑一个完整任务并全程采集 trace，且易与 docs 重复——
   立项前先定"体验叙事 vs 操作手册"的分工（后者归 SETUP.md）。
   依赖：素材不成熟（无现成全程 trace），等一次真实任务顺路采集。

## 已用掉的题（勿重复）

事故复盘（post-01）/ 项目介绍（post-02）/ 证据阶梯（post-03）/ 注意力经济学（post-04）/
对抗性测试·验证验证者（post-05）/ 愿景北极星·信任税（post-06）。
