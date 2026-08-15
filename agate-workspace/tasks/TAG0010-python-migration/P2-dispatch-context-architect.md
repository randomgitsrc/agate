---
phase: P2
generated_by: agate-inject-card.sh + 主 Agent
task_id: TAG0010-python-migration
role: architect
---

<dispatch_guide>
> ⚠️ 以下派发指引是本次任务的强制指令，不是参考信息。执行优先级：派发指引 > 客观查证信息 > 阶段卡片（参考规范）

### 目标
产出 {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P2-design.md：agate 产品逻辑 Python 化（30 个 sh → py，hook 保留 sh 薄壳）的技术方案设计。P1 已把影响面摸全（表 A-E），你的核心工作是把映射表转化为可实现、可验证、可分批执行的方案。

### 约束
- **范围锁定**（P1 已确认）：30 个 sh → py；3 个 hook 入口（pre-commit-gate / commit-msg-self-gate / pre-push-gate）保留 sh 薄壳；gate-result.sh + agate-workspace-resolve.sh → agate_common.py；install-hook.sh **一并 py 化**（→ install-hook.py）；`count-tests.sh`/`check-windows-smoke.sh` 属 tests/scripts/ 不在迁移范围；18 个既有 py 不做功能改写（可最小调整满足规则集，P1 §2 已声明边界）。
- **主 Agent 已采纳的 SUGGEST（设计必须遵守）**：
  1. 非 hook 脚本迁移后**不保留** .sh 兼容薄壳（删档）
  2. 迁移命名按**同名换后缀**（check-gate.sh → check-gate.py）
  3. hook 薄壳 python 探测顺序 = `python3` → `python`
  4. ruff 以 CI 独立 job 形式接入（不做 pre-commit hook 子步骤）
  5. check-platform-assumptions 扩展名过滤新增 `.py` 后保留 `.bats/.bash/.sh` 不删
- **consistency 锚点约束**：表 C 已列 CHECK 8/9 锚点映射——设计必须明确"关键字存活在 py"或"锚点表同步"的落地方案；`check_anchor_coverage` 的 glob 必须改为扫新 py gate 脚本（否则反向覆盖检查空转）；GATE_SCRIPT_EXEMPT 白名单随迁移调整。
- **编码规范**：所有 py 显式 `encoding="utf-8"`（gate 规则）；**Python 3.8+**（避免 match/str.removeprefix 等 3.9+/3.10+ 语法）。
- **pyyaml 强制依赖**：SETUP.md 明确 pip install pyyaml；环境缺 pyyaml 时 py gate fail-closed。
- **hook 薄壳设计**：~15 行/个 = shebang + AGATE_ROOT 自定位 + 复制模式 `.agate-root` 恢复 + python 探测（python3→python）+ exec python 主程序 + exec 失败回退（保留 sh 逻辑 fallback，非静默放行）。注意 PROD_TOUCHED / AGATE_ALIGNMENT_REVIEW_THRESHOLD 两个锚点关键字必须存活在薄壳中（表 C 观察项）。
- **BDD-3 ruff 规则集**：范围 = 全部 `agate/scripts/*.py`（既有 18 + 新增）；规则集（pyproject.toml）是 P2 交付物——须让既有 py 在选定规则集下零违规。**P2 必须给出 pyproject.toml 的 select 规则集建议**（实测基线：默认规则集 70 错误，UP032×35 / BLE001×9 / PLW1510×6 为主，ci-gate-backstop.py 14、agate-debt-check.py 14、agate-frontmatter-check.py 11、agate-state-yaml-check.py 7）。
- **BDD-6 前置**：设计须含"对既有 18 个 py 跑扩展后扫描器确认洁净度（或列出预期违规并规划处理）"的执行方案。
- **CLI 输出契约**（P1 §2.2/BDD-10）：`GATE ...:` 前缀、exit 0/1/2 语义、`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出、gate-result.json 结构——迁移后保持不变。
- **gate_commands 在 P2 固化**：本项目测试运行器是 bats（阶段一保持），P3/P5 gate 命令须声明（如 `bats agate/tests/...` 全量 + 分片），供 check-tdd-red.sh 读取。
- **minimal_validation 必须产出**：P1 已标 `requires_minimal_validation: true`（Windows 真机行为本地无法验证）——方案设计须声明哪些假设需最小验证、在本地 Linux 可做什么验证（如：hook 薄壳 exec 失败回退逻辑可用模拟 python 缺失验证；复制模式 `.agate-root` 恢复可用模拟环境验证；Windows 专属行为标"CI Windows matrix 验证"）。

### 上游关联
- P1-requirements.md 已 approved（10 BDD + 表 A-E）：表 A = 30 sh 清单（批次 0-4 划分）；表 B = 文档引用映射（批次 4 输入）；表 C = 锚点关键字映射（CHECK 8/9 + 4 项结构性同步点）；表 D = 受影响 bats 清单；表 E = 迁移批次建议（0 公共库 → 1 自足叶 13 → 2 复合 11 → 3 hook 链 4 → 4 收尾）。
- 主 Agent 决策已固化：ruff 全量范围 + P2 定规则集；install-hook py 化；3 hook 薄壳。

### 输入文件
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-requirements.md（需求基线——主输入）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P1-review.md（approved 评审——含表 B 实测数据）
- {AGATE_WORKSPACE}/tasks/TAG0010-python-migration/P0-brief.md（任务简报与风险声明）
- {project_root}/docs/reviews/agate-python-migration-analysis-20260814.md（定稿分析报告 §3.1 hook 薄壳设计依据）
- {project_root}/agate/scripts/（按需读取具体脚本核实设计依据——重点：check-gate.sh、pre-commit-gate.sh、gate-result.sh、agate-workspace-resolve.sh）
- {project_root}/agate/scripts/check-protocol-consistency.py（CHECK 8/9 锚点表 + check_anchor_coverage glob + GATE_SCRIPT_EXEMPT——设计结构性同步点）
- {project_root}/agate/tests/（按需读取受影响 bats 文件，设计断言改动方案）
- {project_root}/AGENTS.md（项目开发约定）

### 产出要求
P2-design.md 必须含：
- frontmatter：phase/task_id/type/parent/trace_id/status/agent + candidate_count + packages + domains + ui_affected
- 候选方案 ≥2（候选方案必须真实可行，非稻草人）+ 权衡 + 选择理由；如用 design_trivial/follows_existing_pattern 简化须附理由
- 四字段：packages / domains / ui_affected / gate_commands（正文）
- files_to_read（实现导航，控制 P4 implementer 上下文——只列确实需要参考的文件）
- env_constraints（继承/细化 P0-brief，不得弱化）
- minimal_validation（P1 已标 requires_minimal_validation: true，必须产出）
- 设计方案主体应覆盖：agate_common.py 模块设计（替代 gate-result.sh + workspace-resolve 的函数库）；30 个脚本分批迁移方案（按表 E 批次，含每批验证口径）；hook 薄壳设计（3 个）；pyproject.toml 规则集建议（让既有 py 零违规）；consistency 锚点表同步方案（表 C 结构性同步点 4 项）；bats 断言改动方案（表 D）；文档引用同步方案（表 B）；UPGRADING/SETUP 更新要点
- 实现完成的标志（可判定完成标准）

### 门槛（什么算完成）
- P2-design.md 存在且非空
- frontmatter 四字段齐全（candidate_count ≥2 / packages / domains / ui_affected）
- gate_commands 已声明（P3/P5）
- minimal_validation 已产出
- 不写行首 `- PASS`/`- FAIL` 格式
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
4. 预跑 check-gate.sh P2（脚本化检查）
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

## gate_commands 声明

gate_commands 在 P2 固化，后续阶段按此执行：

```yaml
gate_commands:
  P3: "pytest"                  # 可选：测试运行器（verbose 输出，供 check-tdd-red.sh 自动读取）
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
5. 组长产出：P2-review.md（统一 status: approved / rejected）。**组长 subagent 产出的 P2-review.md 的 Header agent 字段必须是组长角色名（非 main）——check-gate.sh P2 硬拦截 agent=main 的 approved**
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
check-gate.sh P2 $TASK_DIR
```

- 候选方案数 ≥2（design_trivial / follows_existing_pattern 时可只写 1 个）
- P2-review.md 存在且 status: approved（agent≠main）— 不存在 → gate exit 1
- 四字段齐全（packages/domains/ui_affected/gate_commands）
- gate_commands.P3 可选（非 pytest 项目建议声明，供 check-tdd-red.sh 自动读取测试运行器）
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
- 环境：Linux；python3 3.12.3 + pyyaml 6.0.3 + ruff 0.16.3（~/.venvs/agate-dev/）；bats 1.10.0
- 测试基线：733 bats 全绿 + consistency 0 ERROR（--strict）
- 脚本基线：30 个 sh（3813 行）+ 18 个 py（2293 行）；check-gate.sh 488 行 + pre-commit-gate.sh 404 行最重
- ruff 实测：默认规则集对现有 18 py 报 70 错误（UP032×35 / BLE001×9 / PLW1510×6；ci-gate-backstop.py 14、agate-debt-check.py 14、agate-frontmatter-check.py 11、agate-state-yaml-check.py 7）
- worktree 根：/home/kity/oclab/agate/.worktrees/agate-TAG0010（改造对象）；~/.agate = 稳定版 v0.45.0（禁止改动）
</objective_info>
