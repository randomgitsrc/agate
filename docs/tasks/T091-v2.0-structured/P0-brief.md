---
phase: P0
task_id: T091
type: brief
parent: HANDOFF-V2.0.md + 可行性评估（peek.gsis.top/mpifxr）
trace_id: T091-P0-20260809
status: done
created: 2026-08-09
agent: main
---

# T091 — agate v2.0 结构化数据改造 P0-brief

> 本文档是主 Agent（orchestrator）亲自填写的任务简报。输入：HANDOFF-V2.0.md（交接文档）+ 可行性评估全文（mpifxr）。

```yaml
task: "把 agate 协议中 P1/P2 产出物的机器读取字段从'正文内嵌 YAML + 正则提取'重构为'YAML frontmatter + pyyaml 解析'，新增 frontmatter schema 校验器，消除持续性的正则摩擦补丁税（v0.30.2 → v0.35.0 连续 5 版同类补丁），发布 agate v2.0.0"

known_risks:
  - "涉及数据格式变更（P1/P2 产出物 frontmatter schema），需要双读兼容在途任务旧格式"
  - "gate 本身（check-gate.sh / check-pruning.sh 等）被修改——自我改造，需 self-gate 流程 + 全量 bats 无退化"
  - "count-tests.sh 数字不能漂移（当前基线 594 + sanity 6）——测试改造必须保持用例数不变"
  - "gate_commands 暂留正文（3 个读取工具 agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-read-p5-commands.py 仍从正文正则读），移入 frontmatter 会失配"
  - "CHECK 9 锚点表（check-protocol-consistency.py 33 条）需全量过一遍，防止一致性检查红"
  - "P5_DATA 中间格式缓存键（agate-capture-env-baseline.sh 的 CACHE_KEY）若 gate_commands 相关改动可能再失效一次"
  - "frontmatter 禁止 >3 层嵌套；LLM 写嵌套 YAML 缩进错误率高——需 schema 校验器 + 角色卡可复制模板"
  - "语义真实性不升不降（BDD-8 单侧/双侧歧义、candidate_count 虚报在结构化后依旧）——设计文档必须写明，防止'做了结构化就以为 gate 变强'的错觉"

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

phase_hint: [P1, P2, P3, P4, P5, P6, P7, P8]
```

## 扩展：范围决策（来自评估 §6.2 + HANDOFF §5.3）

- **流 A（先做）**：P1/P2 格式迁移 + schema 校验器——最小爆炸半径
- **流 B（依赖 A）**：P6/P7 结果结构化
- **流 C（最后）**：标记状态收尾
- **scope 决策（已定）**：`gate_commands` **暂留正文**。只迁移候选数/裁剪类字段（risk_level/phases/candidate_count/packages/domains/ui_affected）。

## 扩展：硬约束（评估 §6.3）

1. `count-tests.sh` 数字不能漂移
2. frontmatter 禁止 >3 层嵌套
3. 角色卡必须贴可复制模板
4. 在途任务：**双读**（frontmatter 优先 + 旧正则回退）
5. CHECK 9 锚点表（33 条）全量过一遍
6. v2.0 设计文档必须写明"结构化不解决语义真实性"

## 环境自检（P0 卡片要求）

- [x] debug 环境可访问：bats 1.10.0 可用，sanity.bats 全过（基线）
- [x] 测试框架可用：bats（594 + sanity 6）
- [x] 本任务非 UI 任务，不需要浏览器自动化

## 任务粒度自检（office-hours 六问）

1. 需求真实性：T090 计划明确写着"会被未来的结构化方案取代"，v0.30.2→v0.35.0 连续 5 版正则补丁 = 持续性维护税 → 真实
2. 现状：gate 靠正则从正文 grep 机器字段，全角冒号/缩进/PROD_TOUCHED 误报反复修
3. 绝望的具体性：agate 协议维护者每周都要处理格式摩擦
4. 最窄切入点：P1/P2 字段并入已有 frontmatter + pyyaml 读取 + schema 校验器
5. 亲眼观察：可行性评估已核实 40+ 字段现状、14 个 py 工具、594 测试分布
6. 未来契合：为全 py 化 + Windows 原生适配铺路（无 Git Bash 依赖）

## 参考资料

- 可行性评估全文：https://peek.gsis.top/mpifxr（字段清单 §1、方案对比 §3、风险 §5、路线 §6）
- 交接文档：HANDOFF-V2.0.md（本 worktree 根目录）
- 既有 v2.0 Phase1 plan（已过时但含字段清单）：`git cat-file -p 857a5d0:docs/plans/agate-v2.0-structured-phase1-20260809.md`
