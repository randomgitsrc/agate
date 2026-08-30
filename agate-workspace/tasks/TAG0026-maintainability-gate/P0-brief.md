# P0-brief — TAG0026 维护性反模式 gate（RM-AG0046）

> 本文件由主 Agent 亲自填写（P0 阶段产出）。落地计划：`docs/design-notes/rm-ag0046-maintainability-gate-plan.md`
> （v3，2026-08-30 独立评审修复 5 项后定稿）；设计地基：`docs/design-notes/design-maintainability-gate.md`
> （G0-G3 分级 + 决策 1/2/3）。

## task

"在 agate 协议层落地维护性反模式 gate（RM-AG0046，G0 优先 diff 驱动）：新增
`agate/scripts/check-maintainability.py`（god-file 跨越 + fuzzy-boundary 检测，复用
`agate-risk-score.py` 的 `score_task`/`_load_script`/`_norm_rel` 模式）+ `check-gate.py`
**P4 挂载三重门槛**（violation 登记 + 数量对齐 + P4 评审 approve，非"登记即放行"）+
`known-violations-template.md` 模板 + P4/P6 phase card 自查提醒 + pytest 覆盖计划 13 条 BDD。
只在 P4 挂载（代码 staged 时，`git diff --cached` 有代码），不挂 P6（代码已 commit）。"

### scope

- **G0 两条**：god-file 跨越（`before < N and after >= N`，N 默认 1000 可配置）+ fuzzy-boundary
  （diff 新增行匹配 Python/TS 类型逃逸正则）
- **P4 gate 硬挂钩**（check-gate.py gate_p4 新增一步）：v3 三重门槛
- **P4/P6 phase card**：P4 自查清单项 + P6 自查提醒（非阻断）
- **known-violations-template.md**：登记模板，`| N |` 行首格式（对齐 `count_kf_entries` 计数）
- **配置**：`agate-workspace/maintainability.yaml`（阈值/正则集，缺失用默认值）
- **测试**：`agate/tests/` 新增 pytest 覆盖 13 条 BDD（含移动代码假阳性 BDD-12、挂载阶段对齐 BDD-13）

### out-of-scope

- G1（DRY，需 canonical 清单）/ G2（条件纠缠/薄抽象/顺序耦合，AST 级）/ G3（纯品味）
- RM-AG0022 结构化层联动（语义进 `rules/*.yaml`）
- 新增第 8 道 provenance 审计（登记内容暂不机械审计，靠 P4 评审角色 + 事后人工）
- 门户/可视化面板、跨行移动代码识别

## known_risks

- "同类/影响面预判（check-gate.py 是核心 gate）：所有任务 P0-P8 都经它判定，P4 判定新增一步
  须保证返回约定（1/2）与既有调用链兼容，改动回归风险高——全量 pytest + consistency 0 ERROR
  是硬门槛；grep 确认消费方：pre-commit-gate.py / ci-gate-backstop / check-judge-verdict /
  agate_common / rules/ 多处引用 check-gate"
- "同类/影响面预判（检测器数据源与挂载阶段对齐）：`git diff --cached` 必须在代码 staged 时
  （P4）调用；挂 P6 是死代码（v2 教训，BDD-13 防复发）——本次只挂 P4，P6 仅自查提醒"
- "阈值 N=1000 无实证依据（来自 Cursor skill），须在文档/配置明确'默认值仅供参考可配置'，
  不造成'协议断言该阈值'的错觉"
- "fuzzy-boundary 正则集只覆盖 Python/TS，其它语言（Go interface{}、Java @SuppressWarnings）
  不在本版范围——协议参考实现语义，项目经 gate_commands 自行补充"
- "移动代码假阳性已知（含裸 except 的代码块被移动 → diff 判新增），靠 known-violations 登记
  吸收，不引入跨行移动检测（复杂度和零歧义原则冲突，BDD-12 验证登记路径可用）"
- "known-violations 与 known-failures 语义相反（自引入 vs 预存）：三重门槛必须落实
  '数量对齐 + P4 评审 approve'，不得退回 v1 的'登记即放行'——V3 已修复，实现须守住"
- "known-violations.md 模板须用 `| N |` 行首表格格式（`count_kf_entries` 依赖），模板字段
  含 P4 评审确认列但不参与机械计数（防'填了就自动放行'错觉）"

## executor_env

platform: "dsh（DeepSeek Harness Web GUI，deepseek-v4-flash-free）"
has_task_tool: true
has_local_runtime: true
network: "full"

## env_constraints

debug_env: "python3 -m pytest agate/tests/ -n auto（unit/regression/integration 分片）+
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only +
bash agate/tests/scripts/count-tests.sh；gate/hook 用 ~/.agate 稳定版；
改协议本体须自审 SELF-GATE（protocol-alignment-review）"

## 推进条件自检（P0 卡要求）

- **时效性自检**：立项与计划定稿同日（2026-08-30）；计划 v3 经独立评审（peek.gsis.top/uucahi）
  修复 5 项后定稿，设计地基 2026-08-25 → **已核对，无漂移**
- **环境自检**：bash / python3 / pytest / pyyaml / shellcheck / ruff 可用；基线——
  unit 全绿 / consistency 0 ERROR / count-tests 1308（2026-08-30 实测）
- **同类/影响面预判**：已含（见 known_risks 前两条：check-gate 消费方 + 挂载阶段对齐）
- **任务粒度**：一句话可描述（G0 两条落地 + P4 三重门槛 + 测试），不需拆分；
  G1/G2/结构化层联动已显式切出
