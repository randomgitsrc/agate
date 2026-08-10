---
phase: P8
task_id: T001
type: release
parent: P2-design.md
agent: implementer
bump_type: minor
---

# T001 — P8 发布准备

> 本文件为发布准备记录，不代表 git commit/tag 已执行——bump-version / commit / tag 由主 Agent
> 在 gate 验证通过后亲自执行。本 subagent 未执行任何 git 命令。

## 1. bump_type

```
bump_type: minor
```

**判定依据**（`agate/WORKFLOW.md` 第 7 行："规则新增/调整升 minor，破坏性变更升 major"）：
本次 T001 是"机器字段承载方式"的迁移（正文内嵌 YAML/正则提取 → frontmatter + pyyaml +
schema 校验），新增校验器（`agate-frontmatter-check.py`/`check-frontmatter.sh`）、新增结构化
字段（P6/P7 汇总字段、P1 已解决状态字段）、新增流程挂载点（pre-commit 步骤 2g.2）——属"规则
新增/调整"范畴。虽然任务编号正则硬切（`^T\d+$` → `^T[A-Z]{2}\d+$`）对使用旧格式编号的在途
任务不兼容，但这是协议内部对"新任务如何命名"的规则收紧，不改变协议对外的核心工作流架构
（P0-P8 状态机、双层角色体系、gate 判定语义均未变），且旧格式 frontmatter 缺失时全部新校验
器均豁免为"旧格式兼容"（向后兼容读取路径保留）。综合判断为 **minor**，不是破坏性架构大改
（major），也不是纯 bug fix（patch，虽含 2 个 bug 修复，但主体是规则新增）。

- 旧版本：`0.35.0`
- 新版本：`0.40.0`（0.35.0 → 0.40.0，跳过 0.36-0.39 是主 Agent/PM 层面的版本号分配决策，
  不影响本次 bump_type 判定本身）

## 2. 版本号变更确认

**本 subagent 未修改 `README.md`**（约束 6 明确禁止）。需要主 Agent 亲自执行的改动：

- 文件：`README.md`
- 位置：第 6 行
- 现状：
  ```
  [![version](https://img.shields.io/badge/version-v0.35.0-blue)](https://github.com/randomgitsrc/agate)
  ```
- 目标：
  ```
  [![version](https://img.shields.io/badge/version-v0.40.0-blue)](https://github.com/randomgitsrc/agate)
  ```
- 仅替换 `v0.35.0` → `v0.40.0` 这一处子串，其余不变。

（`agate/WORKFLOW.md` 第 5 行提到"当前版本见 `git describe --tags` 或 README.md badge"，
未发现本任务范围内其他需要同步改动版本号的文件；P2-design.md §4 `packages: [agate]` 仅声明
单一包，未见 `package.json`/`VERSION` 等独立版本文件。）

## 3. CHANGELOG 更新确认

**已实际执行**：在 `CHANGELOG.md` 的 `# 变更日志` 说明段与 `## [0.35.0] - 2026-08-09` 之间
插入新的 `## [Unreleased]` 区块，分类为"新增/变更/修复/已知偏离"四组，内容总结 T001 v0.40.0
全部变更（frontmatter schema 校验器新建、双读工具改造、P6/P7 结果结构化、P1 标记状态结构化、
角色卡/模板样例、CHECK 9 锚点表 37→38、任务编号规则硬切、2 处 bug 修复、7 条 DESIGN_GAP 已
REVIEWED-ACCEPTED 的已知偏离），全部条目含 "T001" 字样。

内容来源：`docs/tasks/T001-v2.0-structured/P4-implementation.md`（六个小节完整实现记录：
流 A/B/C/D + Review 修复 + P6 回退修复，另含 Self-gate 文档修复 + ADR-007 补充两个附加小节）、
`docs/tasks/T001-v2.0-structured/P7-consistency.md`（7 条 DESIGN_GAP 的最终核实结论，用于
"已知偏离"分组措辞）。

自查命令与结果：
```
CHECK_CHANGELOG_MODE=normal bash ~/.agate/scripts/check-changelog.sh T001
```
exit 0（`[Unreleased]` 区域含 "T001" 字样，检查通过）。

## 4. 临时资源清单

本任务全程为纯 bash/python 脚本改造 + bats 单元/集成测试驱动开发，**未启动任何调试
服务/进程、未创建任何临时数据库、未做任何开发安装（无 editable install / 全局包安装）**。
P8 阶段 subagent 本次执行也仅涉及文件读写（CHANGELOG.md 编辑 + 本文件写入 + 一次只读 gate
自查命令），无需清理任何临时资源。

## 5. Lessons Learned

| 类别 | 教训 | 来源任务 | 日期 |
|------|------|----------|------|
| 流程 | "字段级双读判别契约"（frontmatter 存在且非 null 才取 frontmatter，否则正文回退）需要在 P2 设计阶段就把"新旧格式共存期的判定条件"讲清楚到函数签名级别，否则实现阶段容易在"任一缺失即回退"与"全部缺失才回退"两种语义间产生歧义（本任务两处均选了更严格的 AND 语义，靠 schema 校验器的必填组合规则兜底论证，但论证过程本可在 P2 阶段就写死，省去 P4 自行决策 + P7 逐条核实的成本） | T001 | 2026-08-10 |
| 测试 | 硬切一个被"真实 pre-commit hook 间接调用"的校验正则（本任务是 `task_id` 格式）时，仅核对专项单元测试文件是否覆盖，不足以发现连带影响——必须额外核对代码库里所有"经由真实 hook 触发该脚本"的集成测试 fixture 是否使用了将被新规则拒绝的旧格式测试数据。本任务流 D 一次性引入了 33 个未被预判到的既有用例回归，靠后续追加派发才收尾（commit 68e4173） | T001 | 2026-08-10 |
| 架构 | 新增校验器接入既有 pre-commit 流程时，若该校验器的 `--fix`/写入类分支对整个文件做归一化处理（如 sed 批量替换），必须显式排除掉同一文件里其他阶段新引入的结构化区块（本任务是 frontmatter 块）——否则一个此前从未触发过的潜伏路径冲突（`check-p6-format.sh --fix` 破坏 frontmatter）会在新旧特性组合出现时才暴露，且不会被任何单一阶段的既有测试捕获 | T001 | 2026-08-10 |

## 6. P2 packages 声明核对

P2-design.md §4：`packages: [agate]`，单包任务。P7-consistency.md §3.2 已独立核实 P4 实际
改动文件范围与该声明一致（`git diff main..HEAD --stat` 全部改动落在 `agate/` 目录内，
少量 `agate/` 目录外的 `.gitignore`/`AGENTS.md`/`docs/reviews/*`/`docs/progress/*` 改动经
溯源均非 T001 P4 产出，属环境接入 chore 或阶段产出证据文档）。P8 本次仅需为 `agate` 单包
准备发布，无遗漏包。

## 7. 主 Agent 待执行清单（本 subagent 不执行）

1. 亲自执行 `git diff main..HEAD --stat` 复核范围（P7 已核实一次，P8 gate 前建议复核 HEAD
   是否漂移）
2. bump-version：`README.md` 第 6 行 `v0.35.0` → `v0.40.0`（见上文第 2 节）
3. 重跑 P5 gate 全量测试确认仍全绿
4. `git log v0.35.0..HEAD --oneline` 对照 CHANGELOG `[Unreleased]` 内容无遗漏
5. bump-version + CHANGELOG 变更 → 同一 commit + tag（`v0.40.0`）
6. READY 收尾检查（本任务临时资源清单为空，无需额外清理动作）
