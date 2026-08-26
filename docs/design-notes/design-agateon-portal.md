# Agateon 门户设计文档（agateon.com）

> 状态：设计草案 ｜ 日期：2026-08-23 ｜ 作者：用户愿景 + agent 推演
> 定位：与 `design-independent-judge.md` / `design-structured-layer.md` 同级的设计文档，作为后续立项的地基，**非当前立项条目**。
> 一句话：**Agateon 之于 agate，如同 GitHub 之于 git。**

---

## 1. 背景与动机

### 1.1 现状痛点（真实存在）

- agate 目前是"单项目、单 orchestrator"的心智模型：状态分散在 `.state.yaml`（单任务权威）+ `active-tasks.md`（全局汇总，**人工维护**）。
- 实际场景已经是**多项目、多任务并行**：agate 自己 dogfooding 时一个项目多个任务（TAG0023 在跑、其他排队），用户还有 qtcalc 等其他项目在用 agate。
- orchestrator 可能本机或远程，状态散落各处，没有"一眼看到所有项目在干什么"的入口。
- 任务卡住（PAUSED/BLOCKED）或长时间停滞时，**没人主动知道**——靠人工翻文件。

### 1.2 用户愿景（2026-08-23 讨论）

> 单个 agate 可以自行运转、离线运转。之后有个集中门户 agateon.com，上面有用户，用户可以创建或加入组织，每个组织监控管理多个 agate 项目，用户可以看到旗下所有 agate 项目的各个 orchestrator task 执行情况，异常自动上报到监控面板。有网络时，agate setup 可以直接注册到 agateon.com 的组织中。

### 1.3 愿景判定

愿景**自洽且正确**，但它不是"做一个 SaaS 监控平台"，而是复现一个经典架构：

> **git 完全离线可用，GitHub 是可选的控制面。Agateon 亦然。**

---

## 2. 核心定位

**Agateon = 协议（离线自治的数据面）+ 可选门户（agateon.com，只读控制面），关系如 git 之于 GitHub。**

```
数据面（agate 本地，不可妥协）        控制面（agateon.com，可选增值）
─────────────────────────────      ─────────────────────────────
P0-P8 状态机                         用户 / 组织
gate 本地判定（fail-closed）          项目监控面板
.state.yaml / gate-events.jsonl      异常告警（PAUSED/BLOCKED/停滞）
orchestrator 执行                    组织内多项目聚合视图
——完全离线、自治、无云端依赖        ——只读镜像 + 上报，不参与 gate 判定
```

**关键区分**：agateon.com 是"本地 CI 的状态投影"，不是"云端 CI"。
- Buildkite / GitHub Actions：**执行在云端**，本地只是触发。
- agate：**执行在本地**（orchestrator 本地跑 gate），云端只是看状态。
- 这个区分让 Agateon 永远不会变成"带 UI 的编排平台"（那是 oh-my-agent 的主场），护城河始终是**协议标准化 + 离线自治**。

---

## 3. 核心原则（5 条，不可妥协）

| # | 原则 | 含义 |
|---|------|------|
| 1 | **离线自治** | 数据面不依赖控制面。门户挂了/没网，本地任务照跑、gate 照判 |
| 2 | **只读门户** | 控制面不干预数据面。门户只读 + 告警 + 指引，**不提供"一键重试/放行"按钮** |
| 3 | **git-native** | 上报 = push，聚合 = pull，零消息中间件、零数据库、零自建后端 |
| 4 | **可验证性** | 三层同构：gate 验证 agent 工作 → 事件账本（哈希链）验证任务过程 → 门户验证组织状态 |
| 5 | **fail-closed** | 干预必须走本地 gate 流程；云端按钮 = 重新引入 self-authorization，明令禁止 |

---

## 4. 架构分层

### 4.1 实体模型

```
用户（User）
 └─ 组织（Org）            —— 一组 agate 实例的聚合（如一家公司的所有项目）
     └─ 项目（Project）     —— 一个 agate 实例 = 一个 git 仓库 + agate-workspace
         └─ 任务（Task）    —— 一个 orchestrator 会话（TAGxxxx）
             ├─ .state.yaml（当前状态快照）
             └─ gate-events.jsonl（append-only 事件账本，行间哈希链）
```

### 4.2 分层交付路径（每层独立交付、独立有价值、都不破坏离线自治）

```
Layer 0  协议 + 工具链          现有，继续演进（TAG0023 正在补强 gate 机制）
Layer 1  本地聚合层             agate-status --all：跨项目/任务状态聚合命令（零云端）
Layer 2  上报协议               .state.yaml + gate-events.jsonl 的增量序列化格式（纯定义）
Layer 3  git-native 门户        agateon.com = 只读聚合器（GitHub Pages + Actions，零后端）
Layer 4  组织/用户/注册         setup --register + 组织监控仓库 + 权限模型
```

Layer 1 是 Layer 3 的本地版，Layer 2 是 Layer 3 的协议版。**先做 Layer 1，门户是最后一步。**

---

## 5. 关键设计决策

### 5.1 上报机制（`agate-report`）

**不是 push 整个项目仓库**（隐私灾难），而是专门的提取脚本：

```
agate-report
  ├─ 读本地所有任务的 .state.yaml + gate-events.jsonl
  ├─ 提取"最小状态快照"：task_id / phase / status / 更新时间
  │    （脱敏：不含具体 gate 输出、文件路径、敏感上下文）
  ├─ 提取"账本哈希链头"：gate-events.jsonl 的最新链头哈希 + 行数
  │    （可验证性：门户能验证账本完整，却看不到事件内容）
  └─ 生成一个只读快照 commit，git push 到组织的监控仓库
```

**上报粒度两级**：
| 级别 | 内容 | 用途 |
|------|------|------|
| 最小（默认） | task_id/phase/status/时间 + 账本哈希链头 | 公开聚合 + 可验证性，不泄密 |
| 完整（组织内信任） | 完整 .state.yaml + gate-events.jsonl | 内部深查 |

**离线语义**：`agate-report` 是"尽力而为"——有网就 push，没网攒着（本地 commit 后联网再 push）。复用 git 的"离线 commit、联网 push"语义，门户**最终一致**但绝不阻塞本地。

### 5.2 告警定义（"异常"的精确语义）

| # | 异常 | 触发条件 | 优先级 |
|---|------|----------|--------|
| A | PAUSED | retries 超限（check-state-transition 判定） | 高（需人工介入） |
| B | BLOCKED | 依赖缺失 / 环境问题 | 高（需人工介入） |
| C | 停滞 | 某 phase 停留超阈值（如 N 天无事件） | 中（"可能被遗忘"） |
| D | **账本哈希断裂** | 事件账本哈希链验证失败（篡改检测） | **最高（可信度受损）** |

告警 D 是"可验证性"的杀手级应用：门户能发现"有人篡改了任务历史"，这是任何普通监控面板做不到的。

### 5.3 干预边界（fail-closed 不破）

- 门户看到"任务 PAUSED"→ 显示本地路径 + 状态 + **指引**（如"建议 review 后决定回退还是继续，去本地执行"）。
- **不提供"点击重试/放行/回退"按钮**。
- 干预必须通过本地 git/文件操作，走正常 gate 流程。云端永远不写回本地状态。

### 5.4 注册机制（setup 时注册到组织）

```
agate setup
  ├─ 离线模式（默认）：只注册本地 orchestrator，照常跑
  └─ 联网可选：--register agateon.com/org/{org-id}
        → 拿 project token → 存本地配置 → 之后 agate-report 增量 push 上报
```

- 注册失败绝不影响本地运转（数据面独立的必然推论）。
- 离线项目联网后 `agate register` 补一步。

---

## 6. 与现有机制的映射（不是新建，是把人工层自动化）

| 现有机制 | 在门户架构中的角色 |
|----------|--------------------|
| `.state.yaml` | 单任务权威状态 → 上报的快照源 |
| `active-tasks.md` | 人工维护的全局汇总 → 被 Layer 1 的自动聚合取代 |
| `gate-events.jsonl` | append-only 事件账本 → 上报的"可验证历史"源 + 告警 D 的校验对象 |
| `SETUP.md` 平台注册 | 本地 orchestrator 注册 → 扩展为 Layer 4 的组织注册 |
| 双工作区纪律 | 数据面隔离的物理基础 → 门户架构继承此纪律 |
| 共享 git hooks | 本地 gate 判定入口 → 门户不触碰，判定永远在本地 |

---

## 7. 刹车点与风险

1. **时机**：门户是"协议稳定之后（时间未定）"的事。协议还在补强（TAG0023 修 gate 缺口），急着做门户 = 在晃动的基座上盖楼。
2. **云端权威化**：用户用久门户会想要"面板上点按钮"。必须守住只读边界，否则 fail-closed 废掉。
3. **隐私/最小上报**：默认最小上报 + 可关，不强制联网；企业项目可完全离线不注册。
4. **运营成本**：走 git-native（GitHub Pages + Actions），**不做自建后端**——否则运维成本侵蚀开源精力。
5. **并发上报冲突**：多 orchestrator 并发 push 监控仓库——按任务分文件减少冲突；上报协议细节在 Layer 2 定稿（候选：每任务独立状态文件 / git notes / 独立 branch）。
6. **过度设计**：组织/用户系统、跨项目通信在单人项目阶段用不上。Layer 3/4 严格等真实需求出现再动。

---

## 8. 开放问题（写进文档、待未来立项时定稿）

1. **上报协议的物理形态**：每任务独立文件 vs 聚合 snapshot vs git notes？（Layer 2 定稿）
2. **并发上报的合并语义**：多 orchestrator push 同一监控仓库如何无冲突？（候选：按任务分文件）
3. **组织权限模型**：成员可见性粒度（组织级/项目级）、token 粒度、成员"拉取未主动上报项目"的语义。
4. **停滞检测阈值**：N 天的 N 取多少？按任务规模/阶段差异化？
5. **门户的技术栈**：GitHub Pages + Actions 静态聚合够不够，还是需要极轻的 serverless 聚合器？

---

## 9. 与 roadmap 的关系

- **本设计不立即立项**，作为 后续门户方向的地基文档。
- 近端可独立落地的只有 **Layer 1（`agate-status --all`）**，它零云端、零新协议，纯本地聚合命令。
- Layer 2（上报协议）需在协议稳定后定义；Layer 3/4（门户 + 组织）严格等真实多项目/多组织需求出现再动。
- 未来立项时，本设计文档与 `design-independent-judge.md` 同等引用。

---

## 10. 一句话总结

**Agateon 的内核不是"监控面板"，而是"可验证性"——从 agent 的工作、到任务的过程、到组织的状态，三层都用 gate/哈希链/聚合来验证。门户只是让这种可验证性"可见"的最后一层投影，且永远只读、永远离线自治。**

> "verify agents like build systems verify compilers" —— agate 验证 agent，事件账本验证 agate，门户验证组织。
