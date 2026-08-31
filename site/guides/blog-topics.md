# 博客选题清单（backlog：候选先入库，写之前定优先级）

> 选题纪律：候选题先记录在此（角度一句话 + 素材现状），开写前才升级成正式任务，走
> `publish-checklist.md` 全流程。避免"每次现想选题"和"好想法丢失"。
> 已发布文章的弧线见下表，新选题必须说明它**补哪一层**、与已发的不重叠。
>
> **命名说明**：本文件是 site/ 博客的**选题清单（backlog）**，与协议侧任务数据
> `agate-workspace/roadmap/`（RM 卡片、P8 gate 硬校验其回写）是两套东西，互不相通——
> 博客选题不走协议卡片、不进 RM 状态机。

## 已发布弧线（截至 2026-08-31）

| 篇 | 标题 | 管的层次 |
|---|---|---|
| post-01 (08-26) | Our AI Safety Net Depended on the Agent Being Honest. It Wasn't. | 一次真实失败（事故复盘） |
| post-02 (08-27) | Agateon: verify AI agents the way a build system verifies a compiler | 项目介绍（是什么/为什么） |
| post-03 (08-28) | Is it done, or does it just look done? A ladder of evidence | 方法框架（证据阶梯 + 审计清单） |
| post-04 (08-30) | The right to look away: how gates buy autonomy | 收益面（注意力经济学：验证买到"可以不看"） |
| post-05 (08-31) | We keep trying to break our own gates | 自我指涉（验证验证者：对抗性测试 + 独立 judge） |

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

1. ~~**对抗性测试：我们故意弄坏自己的 gate**~~ → **已发布（post-05，2026-08-31）**。素材落点：
   check-tdd-red.py 的 A/B 类红灯、TAG0020-independent-judge（三层防造假 / exit code 才是门槛）、
   评审 gate 自指演示。
2. **数字复盘**——25 个任务的数据帖（gate 拦截数 / PAUSED 分布 / 重试 / 返工）。
   依赖：先跑 workspace 数据统计。可给 post-04 供弹药。
3. **不需要运行时的协议：状态为什么放版本化 Markdown**——读者信号最强（post-02 dev.to
   评论专门点名 "version-controlled state choice...most agent demos still hand-wave"）。
   注意与 post-04 有素材交叠（版本化状态/中断恢复），**二选一先写，或明确分工**：
   post-04 讲"注意力经济学"，此篇讲"为什么是文件不是数据库"（no daemon / 审计=读文件 /
   diff=git / Windows symlink 教训）。
4. **角色分离：orchestrator 永远不写代码**——独立 subagent 干活 + 独立 judge 评审。
   部分素材可并入 post-04；单写则需更多第一手案例。

## 已用掉的题（勿重复）

事故复盘（post-01）/ 项目介绍（post-02）/ 证据阶梯（post-03）/ 注意力经济学（post-04）/
对抗性测试·验证验证者（post-05）。
