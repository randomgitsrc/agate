---
review_date: 2026-07-05
reviewer: main
review_target: docs/plans/agate-phase-cards-implementation-2026-07-05.md
type: 专家评审（实施计划挑刺型，实证驱动）
method: 逐条对照仓库实际状态跑脚本/正则/git，非静态阅读
---

# 对「Phase Card 实施计划」的专家评审

## 总判定

**方向成立，但计划不能照现状执行。** 有 1 个致命内部矛盾（step 3 会打破 step 6 自己的验证门）、1 个建立在被证伪证据上的架构决策（内联 vs 引用）、2 个多余/错标范围的工作项。此外上游 review→meta-review 链在最关键的决策点上**退化**了分析质量——一个正确的顾虑被虚构的 git 统计推翻。

下面每条都附实证，不是读 diff 推断的。

---

## F1（致命）：step 3 会打破 step 6 自己声明的「0 ERROR」

计划 step 6 写：`check-protocol-consistency.py 0 ERROR（新增文件可能触发 CHECK 2 检查）`。

**这句话有两处错，且掩盖了一个自造的 ERROR：**

1. **错标 CHECK**。真正会被触发的不是 CHECK 2（引用死链，且死链只降级为 WARNING），是 **CHECK 5（「N 个协议文件」计数锚点）**，而 CHECK 5 报的是 ERROR。

2. **step 3 亲手制造这个 ERROR**。CHECK 5 有两个硬编码锚点（`check-protocol-consistency.py` 的 `FILE_COUNT_ANCHORS`）：
   - 锚点 #1：`orchestrator-template.md` 的启动必读列表，expected = 8 项列表长度
   - 锚点 #2：`state-machine.md`，expected = 8，注明「引用 orchestrator-template.md 的 8 项列表」

   step 3 明确要「删除『8 个要读的文件』列表」。删了 → orchestrator-template.md 的列表长度不再是 8 → **CHECK 5 锚点 #1 直接 ERROR**。

3. **附带一个悬空引用**。`state-machine.md:506` 原文：「依次重读 orchestrator-template.md『工作流规则』列出的 8 个协议文件」。step 3 删了那个列表，这行就指向一个不存在的列表——而且这一行**正是本计划要消灭的过载反模式**（中断恢复=重读 8 个文件）。计划的范围里**完全没提要改 state-machine.md:506**。

**实证：**
```
$ python3 agate/scripts/check-protocol-consistency.py   # 当前 baseline
仅有 3 个 WARNING，无 ERROR。
FILE_COUNT_ANCHORS: orchestrator-template.md expected=len([8个文件列表])
                    state-machine.md expected=8「引用 orchestrator 的 8 项列表」
state-machine.md:506「依次重读…列出的 8 个协议文件」
```

**必须补的范围**：要么保留 orchestrator-template.md 的 8-文件列表作为 reference（mapping 表叠加在其上，不删），保住 CHECK 5；要么把「更新 `FILE_COUNT_ANCHORS` + 改 state-machine.md:506 的中断恢复语义」显式列入实施步骤。注意后者的连锁：改 `check-protocol-consistency.py` 本身触发**递归 self-gate**（它在触发正则里）。

按项目一贯原则——**静态推断不够，实施前先真跑一次**，别等 step 6 才发现。

---

## F2（架构级）：「内联」决策建立在被证伪的证据上

整个计划押注在一个决策上：卡片**内联规则**（而非引用协议文件行范围）。这个决策的**唯一**依据是 meta-review 的论断「agate 已过密集增发期，进入稳定期，频率明显下降 → 内联安全」。

**跑 git 后，这个论断三处皆假：**

| meta-review 声称 | 实际（git 实证） |
|---|---|
| 「v0.6 → v0.7：6 commits，2 周」 | **v0.6.0 这个 tag 根本不存在**。tag 只有 v0.3/v0.4/v0.5/v0.7/v0.8 |
| 版本演进跨度暗示 3 周 | v0.3.0（6/28）→ v0.8.0（7/2）= **4 天** |
| 「v0.8 → 当前：频率明显下降」 | v0.8 后 **18 commits / 3 天**，含 **4 个 feat:**（新增机制）、6 个改协议文档的 docs: |

近三天的 commit 还在动协议本体：`orchestrator-log.md`（新机制）、`gate 分类学`、`方向性错配`、`CHECK 9 反向覆盖`。这不是「修复+小迭代」，是**持续高速的规则增发**。

**更值得警惕的是过程本身**：origin review 的攻击点 4 **判断正确**——「agate 当前快速迭代期…引用+行范围更安全」。meta-review 用**虚构的版本统计**把这个正确顾虑推翻，判为「4/5 有效但高估了迭代频率」。于是计划继承了错误的架构决策。

这恰好撞上项目的核心信条：**自报 vs 客观证据**。meta-review 的 git 统计是「凭记忆自报」的，不是「跑 `git log` 得来」的——结果全错。这是 agent provenance v1 被否的同一个病根。

**建议**：把「内联」从「已决结论」降回「待定选项」，用真实频率（仍在高速迭代）重判。倾向**混合模式**：卡片内联「本阶段做什么」的流程骨架（这部分稳定），对「具体规则细节」引用协议文件的精确行范围（这部分正在每周变，最易漂移）。

---

## F3（多余工作）：step 5 的正则追加是无用功

step 5 要给 `commit-msg-self-gate.sh` 触发正则「追加 phase-cards 和 rules 目录」。origin review §6.8 当时写的是「phase-cards 匹配 `agate/.+/.*\.md` **但需要确认**」——这个「需要确认」从没被确认，就直接固化成了 plan 的工作项。

**实测：现有正则已经覆盖，不用改。**
```
REGEX='^(agate/scripts/.*\.sh|…|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$'
✅ agate/phase-cards/P3-tdd.md      已覆盖（命中 agate/.+/.*\.md）
✅ agate/phase-cards/README.md      已覆盖
✅ agate/rules/state-transitions.md 已覆盖
✅ agate/rules/review-mapping.md    已覆盖
```

删掉 step 5 的正则追加。SELF-GATE.md 的触发条件文档里补一句「phase-cards/ 和 rules/ 已被现有通配覆盖」即可，不动脚本。

---

## F4（顺手该修但没提）：self-gate 已知假阴性仍在，且 step 5 本要碰这个文件

`commit-msg-self-gate.sh:26` 的 `self-gate-review:` 检测缺 `^` 行锚，commit body 里任何位置提一句就绕过：
```
$ printf 'fix: x\n\nrefs self-gate-review: in prose\n' | grep -qE 'self-gate-review:\s*\S+'
❌ 绕过成功 — 假阴性仍存在
```
F3 已说明 step 5 那个改动多余；但**如果**最终因别的原因确实要动这个脚本，请顺手把 `self-gate-review:` 和 `self-gate-skip:` 两行都加 `^` 锚。别单独为它开一次 self-gate。

---

## F5（一致性影响被低估）：卡片描述 gate 规则 → CHECK 9 锚点覆盖没进范围

卡片模板有「## gate 规则」小节，要写清「gate 脚本会检查什么 + exit 0/1/2 含义」。origin review §6.8 自己识别了「完备漏 / 双重维护漏」，但**计划 step 6 只提了 CHECK 2**，没提：

- **CHECK 5**（见 F1，会 ERROR）
- **CHECK 9 反向覆盖**：近期刚加的 `check_anchor_coverage` 扫 `check-*.sh` + `pre-commit-gate.sh`，确认每个 gate 脚本都在锚点表。卡片里新写的 gate 描述会不会被要求进锚点表、或与锚点表冲突，**需要实测**——不能假设「卡片是文档不影响脚本检查」。

step 6 的验证项应改为：`CHECK 5 + CHECK 9`，并在实施**前**先跑一遍确认 restructure 后仍 0 ERROR。

---

## F6（软，非阻塞）：「80 行 / 60 行/卡片」偏乐观

「单次加载 ~80 行」「每张卡片 ~60 行」是会误导实施预期的具体数字。卡片模板有 8 节 + 首次/重试/裁剪三入口 + 下游影响；仅 P2/P4 的派发内容就要从 953 行的 dispatch-protocol.md 抽取候选方案规格、四字段、C8 映射、files_to_read——压到 60 行很难。

方向性结论（2900 → ~200 量级）成立，不受影响。但建议：**先真抽一张 P4 卡片实测行数**，再定模板和节奏表里的「~60 行」。这也顺带验证了「内容已存在、只是重组」这个可行性前提是否真成立。

---

## 正面（这些是对的，别在返工里丢掉）

1. **减信息量的大方向正确**。当前 8 文件全读确实超过有效处理量。
2. **「下游影响」小节是真改进**。它修掉了 origin review 攻击点 2 的近视问题——P4 卡片显式写「P6 验收依赖你实现路径的端点行为已验证」，这是当前全文模式也做不好的事。
3. **首次/重试/裁剪三入口**解决了一个真实的现状缺口（现在 Agent 得自己从三个文件推导「我是首进还是重试」）。
4. **把新增 P1 评审角色排除在范围外**（P1 卡片标「评审：暂无，已知缺口」）是有纪律的——不在一个已经很大的重构里夹带新机制。

---

## 过程观察：self-gate 语义审查这次退化了

review→meta-review 链是 agate 信赖的核心质量机制（self-gate 的 LLM 语义审查就是这个形态）。但这一轮它**降低**了分析质量：一个**正确**的顾虑（攻击点 4：迭代期→引用更安全）被 meta-review 用**虚构的 git 统计**推翻。

这不是要否定这个机制，是提醒它的一个盲点：**评审可以引入比被评审对象更自信、更具体、但更错的「事实」**。meta-review 引了带数字的版本统计，读起来比 origin review 的定性判断更「硬」，但那些数字是编的。缓解方向和项目一贯原则一致——**凡是评审里出现的量化事实（commit 数、版本间隔、行数、覆盖率），落笔前先跑一次命令核对**，别让「记忆里的数字」冒充「客观证据」。

---

## 建议清单（可执行）

| # | 动作 | 对应 |
|---|------|------|
| 1 | **修 step3/step6 矛盾**：保留 orchestrator 的 8-文件列表作 reference（mapping 叠加其上），或显式把「改 `FILE_COUNT_ANCHORS` + state-machine.md:506」列入范围（注意递归 self-gate） | F1 |
| 2 | **「内联」降回待定**，用真实 git 频率（仍高速迭代）重判；倾向混合：骨架内联 + 细则引用行范围 | F2 |
| 3 | **删掉 step 5 的正则追加**（已覆盖，实测过）；仅在别的必要时才动脚本 | F3 |
| 4 | 若确要动 `commit-msg-self-gate.sh`，顺手给 `self-gate-review:`/`self-gate-skip:` 加 `^` 锚 | F4 |
| 5 | step 6 验证项 `CHECK 2` → `CHECK 5 + CHECK 9`，实施前先真跑一次 | F5 |
| 6 | 先抽一张 P4 卡片实测行数，再定「~60 行」模板与节奏 | F6 |
| 7 | 评审里的量化事实一律先跑命令核对，再落笔 | 过程 |

## 一句话结论

方向对，卡片结构（含下游影响+三入口）设计对。但**实施计划照现状会在 step 6 被自己的 step 3 卡住**，且**核心的内联决策踩在被证伪的证据上**。先修 F1、重判 F2，再动手写卡片。
