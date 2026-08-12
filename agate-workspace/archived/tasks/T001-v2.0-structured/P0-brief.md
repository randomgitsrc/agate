---
phase: P0
task_id: T001
type: brief
parent: HANDOFF-V2.0.md + 可行性评估（peek.gsis.top/mpifxr）
trace_id: T001-P0-20260809
status: done
created: 2026-08-09
agent: main
---

# T001 — agate v2.0 结构化数据改造 P0-brief

> 本文档是主 Agent（orchestrator）亲自填写的任务简报。输入：HANDOFF-V2.0.md（交接文档）+ 可行性评估全文（mpifxr）。
> 2026-08-09 修订：**范围从"仅流 A"扩为"A+B+C 全做"**（决策：一个 task 完成全部三层结构化，v0.40.0 一次发布）。P1 曾撤回，本文件为重审后的权威立项。

```yaml
task: "把 agate 协议中所有机器读取字段从'正文内嵌 YAML/纯散文 + 正则提取'重构为'YAML frontmatter + pyyaml 解析 + schema 校验'，覆盖三层：流 A（P1/P2 候选数/裁剪字段入 frontmatter + 校验器）、流 B（P6/P7 结果结构化）、流 C（标记状态收尾），一次性发布 agate v0.40.0，消除 v0.30.2 → v0.35.0 连续 5 版的'正则摩擦补丁税'"

known_risks:
  - "涉及数据格式变更（P1/P2/P6/P7 产出物 frontmatter schema），需要双读兼容在途任务旧格式"
  - "gate 本身（check-gate.sh / check-pruning.sh / check-p6-*.sh 等）被修改——自我改造，需 self-gate 流程 + 全量 bats 无退化"
  - "count-tests.sh 数字不能漂移（当前基线 594 + sanity 6）——测试改造必须保持用例数不变"
  - "测试大换血：355 个 @test（占 594 的 60%）直接触及待迁移字段，fixture 重写而非删减"
  - "gate_commands 暂留正文（4 个读取工具 agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-read-p5-commands.py / agate-gate-p5-count.py 仍从正文正则读），移入 frontmatter 会失配"
  - "CHECK 9 锚点表（check-protocol-consistency.py 37 条）需全量过一遍，防止一致性检查红"
  - "P5_DATA 中间格式缓存键（agate-capture-env-baseline.sh 的 CACHE_KEY）若 gate_commands 相关改动可能再失效一次"
  - "frontmatter 禁止 >3 层嵌套；LLM 写嵌套 YAML 缩进错误率高——需 schema 校验器 + 角色卡可复制模板"
  - "语义真实性不升不降（BDD-8 单侧/双侧歧义、candidate_count 虚报在结构化后依旧）——设计文档必须写明，防止'做了结构化就以为 gate 变强'的错觉"
  - "单 task 覆盖 A+B+C 范围大：内部按流 A→B→C 严格推进，每个流独立过 gate 再动下一个，防止一次性全改导致回归爆炸"
  - "流 B 的 P6 逐条 PASS/FAIL 是语义判断密集处——评估 §6.2 建议'结构放 frontmatter、枚举留正文但格式从严'，P2 设计需细化此折中"
  - "SCOPE+/PROD_TOUCHED/DESIGN_GAP 的'发现性'标记本体保持散文（评估 §5.5），只结构化其'已解决/已确认'状态——强行结构化反而漏报"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  model_tier: "standard"

env_constraints:
  debug_env: "worktree 里跑 bats：cd /home/kity/oclab/agate/.worktrees/v2.0 && bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/（load.bash 自动反推 AGATE_ROOT 到 worktree 本体）"
  # 开发工具 = ~/.agate（v0.35.0 稳定版）；改造对象 = worktree 的 agate/；两者必须分清，不可混用
  # 主 checkout /home/kity/oclab/agate（main = v0.35.0，~/.agate 指向它）是协议本体，勿动
  python_toolchain: "py3.12 + pyyaml（agate-state-yaml-check.py 在用，frontmatter 校验器同依赖，无需新装）"

phase_hint: [P1, P2, P3, P4, P5, P6, P7, P8]
```

## 扩展：三层现状与范围全景（评估 §0/§1 核实）

机器字段分布在三层，**本任务全做**：

| 层 | 现状 | 本任务处理 |
|----|------|-----------|
| 1️⃣ 真 YAML frontmatter | `P*-review.md` status/agent、通用 Header（已是 pyyaml 可读） | **不迁移**（已是结构化），只确保 schema 校验覆盖 |
| 2️⃣ 正文内嵌 YAML（"半结构化"） | P0/P1/P2 的 `risk_level`/`phases`/`candidate_count`/`packages`/`ui_affected` 等约 12-16 个字段，靠正则 grep | **流 A：迁入 frontmatter + pyyaml 双读 + schema 校验器** |
| 3️⃣ 纯散文标记 | P6 `- PASS/FAIL`、P7 `[BLOCKER]`/`[DESIGN_GAP]`、P1 `[NEED_CONFIRM]` 等约 25 个 | **流 B：P6/P7 结果结构化；流 C：标记状态收尾** |

**统计**（评估 §1 末）：约 40+ 个独立字段/标记，其中纯正则散文约 25、正文内嵌 YAML 约 12-16、真 frontmatter/YAML 约 6（.state.yaml、review status/agent、vision YAML、evidence JSON）。

## 扩展：分阶段路线（一个 task，内部按流推进）

> 决策（2026-08-09）：**A+B+C 全做，一个 task，v0.40.0 一次发布**。不做 3 个 task——每个 task 独立 P0-P8 的开销 3 倍、流 B/C 依赖流 A 校验器只能串行、且"一次发布"语义要求一次发布。

- **流 A（P1/P2 格式迁移 + schema 校验器）**——最小爆炸半径，先做
  - P1 字段：`risk_level` / `phases` / `override` / `implicit_coupling` / `coupling_checklist` / `internal_only` / `internal_only_reason` / `跳过风险` / `design_trivial` / `follows_existing_pattern` / `domains` / `packages`
  - P2 字段：`candidate_count` / `packages` / `domains` / `ui_affected`
  - 交付：`agate-md-field-get.py` 双读改造（pyyaml frontmatter 优先 + 正则回退）+ 新增 `agate-frontmatter-check.py` / `check-frontmatter.sh` 校验器挂 pre-commit（仿 `.state.yaml` 的 `agate-state-yaml-check.py` 范式）+ 模板/角色卡/fixtures/锚点表同步
- **流 B（P6/P7 结果结构化）**——依赖流 A 的校验器基建
  - P6：汇总（pass/fail/ui_affected）入 frontmatter；逐条 PASS/FAIL 保留正文但**格式从严**（行首 `- PASS|FAIL BDD-NN:` 带 BDD 编号，消除"总结行误判"）
  - P7：BLOCKER/DEVIATION/DESIGN_GAP_REVIEWED 状态入 frontmatter
  - 交付：`agate-p6-facts.py` / `agate-p7-facts.py`（或扩展）+ `check-p6-format.sh` 升级（行格式校验）
- **流 C（标记状态收尾）**——最后
  - NEED_CONFIRM/SUGGEST/SCOPE_RESOLVED 状态结构化（只结构化"已解决/已确认"状态，**SCOPE+/PROD_TOUCHED/DESIGN_GAP 发现性标记本体保持散文**，评估 §5.5）
  - 全量文档/角色卡/模板统一 + 回归清理
- **流 D（任务编号规则改造）**——协议约定收尾，随本次发布
  - 背景（自举原则）：本 task 用 v0.35 旧协议改造，自身编号保持旧格式 `T001`；改造完成后新任务用新格式
  - 新编号规则：`T{项目代号}{编号}`，如 `TAG0001`（AG=agate 改造）/ `TPV8019`（PV=peekview）。项目代号 2 个大写字母（对齐 Jira `[A-Z][A-Z]+` 规则），编号数字动态 `\d+`（3 位起步可扩到 6 位，不设固定上限）
  - 交付：`agate-state-yaml-check.py` 校验器 `^T\d+$` → `^T[A-Z]{2}\d+$`；`check-changelog.sh` 去掉短前缀提取摩擦（`grep -oE 'T[0-9]+'` → 直接匹配完整 task_id）；`active-tasks-template.md` 第 4 条规则明确"项目局部命名空间 + 项目代号 + 动态编号"；dispatch-protocol/state-machine 文档示例同步
  - **迁移策略：硬切（已定）**——新校验器只认新格式 `^T[A-Z]{2}\d+$`，不兼容旧 `T\d+`；发布时存量旧格式任务已归档（含本 task T001），不再过 gate。不做双格式兼容（避免再造一个"双格式摩擦"——正是本 task 要消灭的东西）
  - 本 task 自身编号不变（T001），全程用 v0.35 跑 gate，直到本次发布

**推进纪律**：P4 实现严格按流 A→B→C→D 串行，每个流全绿 + gate 通过再动下一个；P3 测试设计按流分组；P6 验收逐条 BDD 全验。

## 扩展：硬约束（评估 §6.3 + HANDOFF §5.4）

1. `count-tests.sh` 数字不能漂移（594 + sanity 6）
2. frontmatter 禁止 >3 层嵌套
3. 角色卡必须贴可复制模板
4. 在途任务：**双读**（frontmatter 优先 + 旧正则回退）
5. CHECK 9 锚点表（37 条）全量过一遍
6. 设计文档必须写明"结构化不解决语义真实性"（gate 强度不升不降）
7. `gate_commands` 暂留正文（4 个读取工具仍从正文正则读）
8. 每个流先写 regression 测试（改坏格式要能抓住）
9. 流 D 编号规则：新格式 `T{代号}{编号}`（如 `TAG0001`），校验器硬切 `^T[A-Z]{2}\d+$`；本 task 自身用旧格式 `T001` 跑 v0.35 gate

## 环境自检（P0 卡片要求）

- [x] debug 环境可访问：bats 1.10.0 可用，sanity.bats 全过（基线）
- [x] 测试框架可用：bats（594 + sanity 6），py3.12 + pyyaml 可用
- [x] 本任务非 UI 任务，不需要浏览器自动化（ui_affected: false 由 P2 声明）

## 任务粒度自检（office-hours 六问）

1. 需求真实性：T090 计划明确写着"会被未来的结构化方案取代"，v0.30.2→v0.35.0 连续 5 版正则补丁 = 持续性维护税 → 真实
2. 现状：gate 靠正则从正文 grep 机器字段，全角冒号/缩进/PROD_TOUCHED 误报反复修
3. 绝望的具体性：agate 协议维护者每周都要处理格式摩擦
4. 最窄切入点：流 A 的 P1/P2 字段并入已有 frontmatter + pyyaml 读取 + schema 校验器；流 B/C 依次承接
5. 亲眼观察：可行性评估已核实 40+ 字段现状、14 个 py 工具、594 测试分布、三层结构
6. 未来契合：为全 py 化 + Windows 原生适配铺路（无 Git Bash 依赖）

## 参考资料

- 可行性评估全文：https://peek.gsis.top/mpifxr（字段清单 §1、方案对比 §3、迁移成本 §4、风险 §5、路线 §6）
- 交接文档：HANDOFF-V2.0.md（本 worktree 根目录）
- 既有 v2.0 Phase1 plan（已过时但含字段清单）：`git cat-file -p 857a5d0:docs/plans/agate-v2.0-structured-phase1-20260809.md`
