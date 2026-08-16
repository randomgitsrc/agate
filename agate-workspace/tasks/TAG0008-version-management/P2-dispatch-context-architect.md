> **所有 P1-P8 阶段统一强制本文件存在**——commit 前暂存区必须含至少一个当前阶段的 dispatch-context 文件。该文件是 subagent 的核心信息源，禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。

---
phase: P2
generated_by: agate-inject-card.py + 主 Agent
task_id: TAG0008
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P2-design.md——agate 版本管理机制（v1）的方案设计：候选方案（≥2）+ 权衡 + 选择理由 + 四字段（packages/domains/ui_affected/gate_commands）+ files_to_read + env_constraints + minimal_validation + dispatch_plan。

### 约束
1. **范围锁定（P0-brief + P1-requirements 已锁定，不可扩大/缩小）**：v1 = 6 组件（agate-install / agate-resolve / hook 解析入口 / summary 集成 / agate-pack-offline.py / install-offline.py）+ 环境探测（--check）+ 向后兼容红线（BDD-31/32）。v2 边界不做：>= 折中、版本列表、离线包自动更新、离线首次安装、prune 自动清理。
2. **设计必须覆盖 P1 影响面表全部联动点**（P1-requirements.md §2）：
   - 2.1 脚本层：pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh（3 hook 薄壳改 resolve-entry 解析）、install-hook.py（装固定解析入口）、agate_common.py（resolve_agate_root 集成项目版本解析，env 最高 → 项目声明 → current）、pre-commit-gate.py / ci-gate-backstop.py（复核）、agate-summary.py（显示解析版本 + 原因）、agate-inject-card.py / agate-next-card.py / agate-render-dispatch-prompt.py（3 个内联 _agate_root 复核是否统一走 agate_common）、scripts/README.md、check-protocol-consistency.py（新脚本入清单）
   - 2.2 文档层：README / README.zh-CN / SETUP（新增 agent 版环境准备节）/ UPGRADING / platform-notes / AGENTS / WORKFLOW / orchestrator-template（复核）/ handoff-template（复核）/ adr.md（复核）/ templates/project.md（复核）/ install.sh（兼容保留）
   - 2.3 测试层：新增 test_agate_version_install.py / test_agate_version_resolve.py / test_agate_summary.py / pack-offline / install-offline 测试；改 test_install_hook.py；复核 integration/ 下 hook 相关测试
3. **核心设计红线**：
   - `~/.agate` 软链保留（向后兼容）；无 .agate-version 回退 current（默认→latest）；AGATE_ROOT env 覆盖优先级最高
   - resolve 失败必须回退稳（回退 current），绝不静默禁用 gate（BDD-18/19）
   - BDD-32 legacy 布局兜底：`~/.agate` 本身是软链时直接解析软链目标为 AGATE_ROOT
   - gate 逻辑（check-gate.py 等）本身不改，只改"如何解析到哪个版本"（BDD-33）
   - hook 解析入口：install-hook 装固定 resolve-entry，运行时读 .agate-version → exec 对应版本 gate 逻辑；切版本不用重装 hook（BDD-16/20/21）
   - Windows 复制模式（AGATE_HOOK_COPY_MODE=1 / .agate-root 标记）下解析入口仍可用（BDD-22）
   - 离线包：manifest.json 含平台标签 + sha256 checksum；安装时平台核对 + checksum 校验（BDD-25/28）；勾选语义 --skip-python/--skip-pillow（BDD-31）
   - 卸载引用保护：项目仍引用该版本时拒绝卸载（BDD-8）；重复安装幂等（BDD-6）
4. **Python 路线**：产品逻辑全 .py；3 个 hook 保留 sh 薄壳（python 探测 + exec py）；不引入 .sh 新脚本（设计稿 §3.2 的 .sh 路线已过时）。
5. **候选方案 ≥2** + 权衡 + 选择理由（candidate_count 字段与正文一致）。本任务机制级、无 design_trivial / follows_existing_pattern 声明空间（可参照既有脚本模式但作为理由之一）。
6. **dispatch_plan 必填**（high 复杂度硬规则）：工作量五维评估 → 声明编排模式 + 批次（P3-P6 用）。各批次 id + complexity，遵守任务粒度基准（产出 ≤3 / 输入 ≤3）。建议考虑：组件间依赖（install→resolve→hook→summary 是同一解析链路；pack-offline/install-offline 是独立离线链路），拆批须声明共享文件后处理（agate_common.py）。
7. **files_to_read 控制上下文**：只列实现确实需要参考的文件，标行号范围（大文件）。重点：agate_common.py、install-hook.py、3 个 hook 薄壳、agate-summary.py、agate-inject-card.py（内联 _agate_root 参照）、check-protocol-consistency.py（L765 扫描面）、agate/tests 相关测试文件。
8. **gate_commands 固化**（P3/P5/P6 用）：声明 test runner（pytest）+ 紧凑模式。新增测试文件的单测命令。
9. **minimal_validation 必声明**：本任务依赖 git worktree / pip download / pip install --no-index 等外部工具行为 → 设计阶段先做最小验证（20 行脚本验证 git worktree add tag 行为 + pip download --platform 按平台拉 wheel 行为 + checksum 计算），结果写入 minimal_validation。
10. **设计中发现新隐含需求 → 标 [SCOPE+]**（行首声明），不擅自扩大范围。
11. **双工作区纪律**：worktree 内设计 + 只读扫描代码；`~/.agate` / 主 checkout 禁止改动。
12. **不实现代码**：P2 只出设计文档，不写任何功能代码。

### 上游关联
- analyst rev2 产出：P1-requirements.md（31 BDD + 影响面表 + I-1~I-16，review approved）
- P0-brief 范围锁定：6 组件 + 2026-08-16 用户确认补充（离线部署包/平台维度/checksum/uninstall/环境探测）
- 设计稿：archived/docs-2026-08/plans/agate-version-management-20260813.md（§8 决策定稿 + v1/v2 范围，可作方案参照；§3.2 .sh 路线已过时）

### 已完成的调研结论（上一轮 architect 已核实，直接采信，无需重做）
> 以下结论来自 P2-progress.md + 最小验证（/tmp/opencode/tag0008-mv.sh 实测通过），作为设计输入，省去重新扫描：

1. **最小验证全部通过**：
   - `git worktree add <path> <tag>` 成功（detached HEAD @ tag）；重复 add 已存在路径 → exit 128 'already exists' → **幂等必须程序先判存在**（BDD-3 依赖此预判，非 git 行为）
   - `pip download --platform win_amd64/manylinux_2_17_x86_64 --python-version 311 --only-binary=:all: --no-deps` → 按目标平台拉到对应 wheel → **pack-offline 按平台拉 wheel 可行**
   - sha256 checksum 用 hashlib 标准库（无外部依赖），64 hex 字符 → manifest checksum 链路可行
2. **resolve_agate_root 语义**（agate_common.py L76-94）：env 优先 → 脚本真实路径上溯 → 复制模式 `.agate-root` 恢复。项目级版本解析须在此层做加法（env 最高 → 项目声明 → current）
3. **3 个 hook 薄壳**（pre-commit-gate.sh / commit-msg-self-gate.sh / pre-push-gate.sh）：当前单行 AGATE_ROOT 自定位直接 exec 具体版本 py → 需改为经 resolve-entry
4. **install-hook.py**：不 import agate_common（pyyaml 无关，本地 run_git 降级）；契约 `argv[1] > env AGATE_ROOT > ~/.agate`；软链/复制模式（`.agate-root` 标记）→ resolve-entry 设计须考虑
5. **agate-inject-card.py / agate-next-card.py / agate-render-dispatch-prompt.py**：3 个内联 `_agate_root()`（env → 脚本真实路径上溯两级），未走 agate_common → 设计须决策是否统一归口
6. **check-protocol-consistency.py** CHECK 10 SCRIPT_REF_RE（L771）：install-offline.py 不在正则白名单 → 无漂移检查但也不报错；**新增脚本须入 scripts/README.md 清单**
7. **ci-gate-backstop.py**：`_AGATE_ROOT = Path(__file__).resolve().parent.parent` 上溯 → 复核
8. **agate-summary.py**：当前显示仓库自身 git describe tag + 硬编码 `~/.agate/scripts/agate-changes.py` 提示 → 语义迁移（显示项目解析版本 + 原因）
9. **测试现状**：test_install_hook.py（6 用例，_make_fake_root / AGATE_HOOK_COPY_MODE=1 复制模式）；conftest.py fixture 体系；test_pre_commit_hook.py L1351 bdd-19 复制模式
10. **设计稿 §8 决策**：`~/.agate/{repo, dev, vX.Y.Z/..., latest->vX, current}`；latest 纯指针；current 默认→latest；引用即保护（任何项目声明 v0.43.0 → 该版本永不清理）；summary 显示版本+原因；repo 只 clone 一次

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P1-requirements.md（需求基线 + BDD + 影响面表——P2 主输入）
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P0-brief.md（环境约束 + known_risks）
- {AGATE_WORKSPACE}/tasks/TAG0008-version-management/P2-progress.md（上轮调研结论，已内联摘要于上方）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/archived/docs-2026-08/plans/agate-version-management-20260813.md（设计稿，读 §8 + v1/v2）
- /home/kity/oclab/agate/.worktrees/agate-TAG0008/AGENTS.md（项目约定 + 开发命令）
- 只读代码：worktree 内 agate/scripts/*.py、agate/scripts/*.sh、agate/tests/**（按需 grep/read，不重做已确认调研）
</dispatch_guide>

<!-- AGATE_CARD_START -->
## 当前阶段卡片：P2

路径：phase-cards/P2-design.md
---
# P2 — 方案设计

> 当前状态：[首次 / 重试 #N / 裁剪跳阶]
> 裁剪跳阶 → P2 不可裁剪。design_trivial / follows_existing_pattern 可简化（1 个候选方案），不可省略。

## 如果是首次进入本阶段

1. 派发 architect subagent → 产出 P2-design.md
   1.1 写 P2-dispatch-context-architect.md（派发指引：目标/约束/上游关联/输入文件 + 客观查证信息）
2. 按 C8 映射表派评审（见下方）
3. 评审通过 → P2-review.md status: approved
4. 预跑 check-gate.py P2（脚本化检查）
5. git add {AGATE_WORKSPACE}/tasks/{Txxx}/（含 .state.yaml + 产出文件，若 .gitignore 忽略需 git add -f）
   ⚠️ 此时 .state.yaml 的 phase 保持 P2，不要提前写 P3——phase = 本 commit 的产出阶段
6. git commit -m "wf({Txxx}-P2): {摘要}"（phase=P2，P2 产出含 P2-design.md + P2-review.md）
7. P2 commit 完成后进入 P3：**phase 推进 P3 随 P3 产出 commit 一起**（P3-test-cases.md 就绪后），不是单独 phase commit

## 如果是重试

确认上一轮失败原因（方案选择有误 / 候选方案不足 / 评审 rejected）
→ 读 agate/rules/state-transitions.md 确认 retry 上限（P2 MAX=3）

## 前置条件

- [ ] P1-requirements.md 含 domains / risk_level / phases 声明
- [ ] P0-brief.md env_constraints 可查阅

## 派发

- **角色**：architect（`{agate_root}/assets/execution-roles/architect.md`）
- **输入**：P1-requirements.md + P0-brief.md
- **输出**：P2-design.md
- **派发 prompt 追加**：

```
## P2 最小验证
方案设计前，先用最小验证确认关键假设（10 行 HTML 测试页 / curl 请求 / 20 行脚本）。
验证结果写入 P2-design.md 的 minimal_validation 字段。
- 方案依赖浏览器行为/安全模型/外部系统行为 → 必须做最小验证
- 纯代码逻辑 → 须在 minimal_validation 字段声明 `纯代码逻辑，无外部系统依赖`（须写明依赖了哪些内部函数/数据转换）
```

## 产出规格

P2-design.md 必须包含：
- **候选方案 ≥2** + 权衡 + 选择理由（design_trivial / follows_existing_pattern 时可只写 1 个，见下方）
- **`candidate_count: N` 必填**：本方案候选方案数（≥2，design_trivial/follows_existing_pattern 时可 1），gate 按此字段校验，不再解析标题。你写几个候选就填几个，与正文一致。
- **四字段**：`packages:` `domains:` `ui_affected:` `gate_commands:`
- **files_to_read**：实现时需要参考的文件清单（控制 P4 implementer 上下文）
- **env_constraints**：确认/细化 P0-brief 的环境约束
- **minimal_validation**：验证结果 或 声明"纯代码逻辑，无外部系统依赖"（声明时须附理由）

`candidate_count`/`packages`/`domains`/`ui_affected` 写在文件头 **frontmatter**（`---` 分隔块），
不写正文；`gate_commands:`/`files_to_read:`/`env_constraints:`/`minimal_validation:` 留正文。
**可直接复制的完整样例**：
```yaml
---
phase: P2
task_id: TAG0001           # 替换为实际任务编号
type: design
parent: P1-requirements.md
trace_id: T001-P2-20260101 # {task_id}-P2-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2                # int ≥1，必填
packages: [pkg-a]                 # list，必填
domains: [backend, cli]           # list，必填
ui_affected: false                # bool，必填
---
```

候选方案简化（须附理由，无理由视为无效声明，要求 ≥2 候选方案）：
- `design_trivial: true` + 理由（为什么 trivial）→ 可只写 1 个候选方案（P2 仍不可省略）
- `follows_existing_pattern: [src/foo.py]`（列出参照文件路径）→ 可只写 1 个候选方案，参照已有模式（P2 仍不可省略）

## dispatch_plan 机器字段（可选，TAG0014）

> 本字段是 P2 对**后续阶段编排方案**的机器声明（评估 + 编排模式，见 dispatch-protocol「派发编排机制」），由 architect 在"批次设计"节（execution-roles/architect.md）产出，P2 gate 校验其合法性。

方案含多个独立子任务（多包/多模块/high 复杂度）时，P2-design.md frontmatter 应声明 `dispatch_plan:`（单行 flow YAML，与 candidate_count 同级，**不入 frontmatter-check schema**，缺省不校验）：

```yaml
# ── v2.0 派发编排字段（可选）──
dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: pkg-a, complexity: medium}, {id: pkg-b, complexity: low}]}
```

字段契约（gate 校验口径）：
- `mode` ∈ {single, static-batch, parallel, recon-then-split, serial}——编排模式（单发/静态拆批/并行/先理解后拆/串行链）
- `parallel_limit` 可选，≥1 整数——并行上限（缺省 3）
- `batches` 可选——mode ∈ {static-batch, parallel} 时每批须含 `id` + `complexity` ∈ {low, medium, high}；批数 ≤ parallel_limit
- 缺字段 / 坏 YAML → P2 gate 跳过校验，行为等同现状（向后兼容，不误拦）

## gate_commands 声明

gate_commands 在 P2 固化，后续阶段按此执行：

```yaml
gate_commands:
  P3: "pytest"                  # 可选：测试运行器（verbose 输出，供 check-tdd-red.py 自动读取）
  P5: "pytest -q --tb=no"       # 紧凑输出模式
  P5_e2e: "playwright test --reporter=line tests/e2e/"  # ui_affected: true 时必填
```

## 评审派发（C8 机械映射）

按 P1 声明的 domains + risk_level 机械映射评审：

| domain | risk_level | 必须派的评审 |
|--------|------------|------------|
| backend | 任意 | plan-eng-review（P2 方案评审） |
| frontend | 任意 | plan-design-review |
| 任意 | high | plan-eng-review（硬规则，必须派独立 subagent） |
| P1-requirements.md 含 [NEED_CONFIRM] 且涉及业务方向 | 任意 | plan-ceo-review |

> **去重说明**：同一任务命中多行且触发同一评审角色时，去重只派发一次（如 backend + high 均命中 plan-eng-review，只派 1 个 plan-eng-review，不重复派发）。

多个评审角色 `专家组并行` → 组长汇总 → P2-review.md（status: approved / rejected）。
详见 `agate/rules/review-mapping.md`。

**并行派发**（多个评审角色时）：
1. 同时派发所有触发的评审 subagent（每个一个 task 调用）
   > **操作方式**：在一个 assistant 消息中连续发起多个 task 工具调用（每个评审角色一个）。
   > 不要等前一个 task 返回再发下一个——那是串行，不是并行。
   > 平台会并行执行多个 task，全部返回后再进入下一步（派发组长汇总）。
2. 每个评审 subagent 各写一个 dispatch-context + 各自产出文件（示例非穷举，按 C8 映射表触发）：
   - plan-eng-review → P2-review-eng.md
   - plan-design-review → P2-review-design.md
   - plan-ceo-review → P2-review-ceo.md
   - cso → P2-review-cso.md
3. 所有评审返回后，派发组长汇总 subagent（角色：review + 指定为「专家组组长」）
4. 组长输入：所有评审文件路径
5. 组长产出：P2-review.md（统一 status: approved / rejected）。**组长 subagent 产出的 P2-review.md 的 Header agent 字段必须是组长角色名（非 main）——check-gate.py P2 硬拦截 agent=main 的 approved**
6. 组长规则：
   - 不发表新意见，只汇总
   - 任何专家标 BLOCKER → status: rejected
   - 多位专家分歧 → 标「专家组分歧」交人工
   - 全票无 BLOCKER → status: approved

**单评审角色时**：直接派发，无需组长汇总，产出直接写 P2-review.md。

review 不通过 → architect 修改方案 → 再 review → … → approved（⑩迭代循环，review 和 gate 重试共享 retry 预算）

**UI 测试选择器**：涉及前端时，P2 design 建议声明 UI 组件的稳定测试标识清单（如 `data-testid`，而非 class 命名）。P3 test-designer 用稳定标识定位元素，P4 implementer 按清单实现--class 命名可重构，稳定标识不变。具体方案由 P2 architect 决定。

## gate 规则

```bash
check-gate.py P2 $TASK_DIR
```

- 候选方案数 ≥2（design_trivial / follows_existing_pattern 时可只写 1 个）
- P2-review.md 存在且 status: approved（agent≠main）— 不存在 → gate exit 1
- 四字段齐全（packages/domains/ui_affected/gate_commands）
- gate_commands.P3 可选（非 pytest 项目建议声明，供 check-tdd-red.py 自动读取测试运行器）
- 候选方案 ≥2 时含权衡/选择理由

## 推进条件（全部满足才写 phase: P3）

- [ ] P2-design.md 候选方案 ≥2（或 design_trivial/follows_existing_pattern 须附理由时可只写 1 个）+ 四字段齐全
- [ ] P2-review.md 存在且 status: approved（agent≠main）
- [ ] gate_commands.P5_e2e 已声明（ui_affected: true 时）

## 常见错误

1. **忘了最小验证**：方案依赖外部系统行为（API MIME 类型、浏览器 CSP 等）但直接假设前提成立 → 到 P6 才发现不可行。跑一个 curl / 10 行 HTML 就能 5 分钟发现
2. **gate_commands.P5 只列单元测试**：UI 任务时缺少 P5_e2e → P5 不会跑端到端验证
3. **files_to_read 列太多文件**：把所有相关文件都列上 → P4 implementer 上下文爆炸。只列确实需要参考的
4. **忘了派评审**：按 C8 映射机械执行，不靠"觉得不需要"
5. **gate 不过 ≠ 你失败了**：红灯指向工作/设计的问题，不指向你。正确动作是诊断→退回/重试/PAUSED，不是修改产出让它变绿。

## 下游影响

- P4 依赖 files_to_read 导航代码阅读范围
- P5 依赖 gate_commands 执行验证命令
- P6 依赖 ui_affected 判断是否需要 vision-helper
- gate_commands 在 P2 固化后 P4-P6 不能改——设计阶段是声明验证契约的唯一窗口

> 完成 → 读 phase-cards/P3-tdd.md
<!-- AGATE_CARD_END -->

<objective_info>
- 环境状态：worktree 分支 feat/TAG0008-version-management；P1 已 commit（d97de41），31 BDD approved
- 关键路径：AGATE_WORKSPACE=/home/kity/oclab/agate/.worktrees/agate-TAG0008/agate-workspace
- 查证结果：基线 780 pytest + consistency 0 ERROR；git worktree / pip download 可用（executor_env.network=full）；无既有 agate-install/agate-resolve/.agate-version 实现（全新组件）
</objective_info>

> 注：该文件禁止包含 PASS/FAIL 预判——否则被 `check-p6-provenance.py` 审计失败。
