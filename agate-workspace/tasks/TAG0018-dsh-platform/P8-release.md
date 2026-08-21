---
phase: P8
task_id: TAG0018-dsh-platform
type: release
parent: P6-acceptance.md
trace_id: TAG0018-P8-20260821
status: draft
created: 2026-08-21
agent: implementer
---

# P8 — 发布准备（agate 原生支持 DSH 平台，RM-AG0030）

> P8 releaser 模式：本文件只产出发布准备建议 + 已按派发指引完成版本 bump（4 处），**不执行 git commit/tag/bump-version 之外的任何 git 操作**——commit/tag 由主 Agent 在 gate 验证通过后亲自执行。CHANGELOG.md / UPGRADING.md / README badges 已按 P8-dispatch-context-implementer.md 约束直接编辑（见下文「版本号变更确认」与「CHANGELOG 更新确认」）。

## 包声明核对（单包发布）

P2-design.md frontmatter `packages: [agate]`（协议本体——六项交付物全部落在 `agate/` 内：templates/dsh/ + SETUP.md + platform-notes.md + tests/unit/）。agate 是单一协议仓库，无独立子包发布结构（无 per-package version 文件），`packages` 字段是改动范围分类——**单包发布，无 SCOPE_GAP**。

## bump_type

`bump_type: minor`

## 版本号变更确认（已实际编辑，主 Agent 复核）

- 当前版本（README.md / README.zh-CN.md badge）：`v0.56.0`
- 新版本：**`v0.57.0`**（已直接编辑 4 处，见下方清单）
- 判定依据（AGENTS.md「版本 bump 判定」规则）：
  - 本任务新增**对外能力**：agate 官方支持第三个平台（DSH/deepseek-harness，RM-AG0030）——新增模板目录（agent.cordis.yml / preset.yml / SKILL.md）、SETUP.md「步骤 2-DSH」接入章节、platform-notes.md DSH 平台条目、平台无关回归测试（8 用例）。新平台接入 = 面向用户的新功能 → **minor**。
  - 无破坏性变更（交付物全部为新增文件 + 文档追加章节，未改动任何既有协议机制运行时行为）→ 排除 major。
  - 既有先例：TAG0007（v0.55→v0.56，RM-AG0008/09 机制增强，minor）、TAG0017（v0.54→v0.55，工具链修复批，minor）。
  - 核实结论：与派发指引一致，**采用 minor，v0.56.0 → v0.57.0**。

### 已编辑的 4 处 bump 文件

| 文件 | 变更 |
|------|------|
| `README.md` | badge `version-v0.56.0-blue` → `version-v0.57.0-blue` |
| `README.zh-CN.md` | badge 同步 `version-v0.56.0-blue` → `version-v0.57.0-blue` |
| `CHANGELOG.md` | 新增 `## [0.57.0] - 2026-08-21` 节（Keep a Changelog 格式：新增=DSH 平台支持（RM-AG0030）+ 关键机制 + 说明），位于 `[0.56.0]` 节之上 |
| `agate/UPGRADING.md` | 「已知破坏性变更」节新增 `### v0.57.0 — DSH 平台支持（无破坏性变更）`：无迁移动作；DSH 接入见 `SETUP.md`「步骤 2-DSH」；升级仅需 git pull + 重跑 install-hook.py |

> 仅改动以上 4 处，未触碰其他文件（`git diff --stat`：CHANGELOG.md +43 / UPGRADING.md +14 / 两 README 各 1 行）。

## CHANGELOG 更新确认

已直接编辑 `CHANGELOG.md`：在 `[0.56.0]` 节之上新增 `## [0.57.0] - 2026-08-21` 节，含：

- 「新增」小节：DSH 平台支持（RM-AG0030）——`assets/templates/dsh/` 三文件（agent.cordis.yml / preset.yml / SKILL.md）、SETUP.md「步骤 2-DSH」、platform-notes.md DSH 条目、test_dsh_preset.py 回归（8 用例，含 tool-fs-search 必填配置守护）
- 「关键机制」小节：DSH 平台接入 = 文档化符号链接 + 唯一 install-hook.py（不发明新结构）；身份薄、协议厚；测试平台无关
- 「说明」小节：本版本无破坏性变更；无技术债关闭（`debt_check: none`）；接入步骤单一真相源

格式参照既有 `[0.56.0]`/`[0.55.0]` 节结构（三级标题 + 分组小标题）。

## UPGRADING 更新确认

已直接编辑 `agate/UPGRADING.md`：新增 v0.57.0 章节——**本版本无破坏性变更**（新增平台支持，加性变更）；「DSH 接入见 `SETUP.md` 步骤 2-DSH」；已有项目升级 = `git pull` + 重跑 `install-hook.py`（符号链接模式自动跟随 / Windows 复制模式必须重跑）。

## debt_check

`debt_check: none`

核对 `agate-workspace/debt/tech-debt.md`（640 行，DEBT0001~0017）：本次发布**无技术债关闭、无新登记**——TAG0018 为纯增量交付（新增模板/文档章节/测试文件），不触及任何 open 债务条目（DEBT0002/0003/0004/0007/0008/0014/0015/0016/0017 均与本任务无交集，保持 open 原状）。合法选项 `none`，不阻断发布。

## 发布检查清单逐项结果

### 1. `git log v0.56.0..HEAD --oneline` 对照 CHANGELOG 无遗漏

`git log v0.56.0..HEAD --oneline` 输出（9 个 commit，全部属 TAG0018）：

```
0ccbfd7 wf(TAG0018-P6): 验收 19/19 BDD PASS（0 FAIL/0 NC）六道 provenance 审计全过 → P6 gate exit 2
40a9046 wf(TAG0018-P5): 全量验证通过（1036 passed/0 ERROR/1038 用例）— 修复 R2/R4 平台假设违规后转绿
153c0a2 docs(TAG0018-P4): tests/README.md 映射表补 DSH 平台测试行（M-7 顺手项，独立 docs commit）；self-gate-skip: 纯文档行追加，无协议机制改动
bf69754 wf(TAG0018-P4): 实现 6 交付物过 review（approved）→ 8/8 绿；self-gate-skip: P4 实现提交，完整 self-gate review（protocol-alignment-review）于 P8 统一派发
15a6874 wf(TAG0018-P3): TDD 红灯 8 用例（1030→1038）check-tdd-red exit 0 → P3 gate exit 2
d5b5f8a wf(TAG0018-P2): 方案设计 6 交付物过 plan-eng-review（approved）→ P2 gate exit 2
03fdd8c wf(TAG0018-P1): 需求基线 19 条 BDD 全过 requirements-review（approved）→ P1 gate exit 2
c76c12e wf(TAG0018-P0): 任务看板登记 + roadmap RM-AG0030 scheduled
4da6bfe docs: TAG0018 交接单 — agate 原生支持 DSH 平台
```

对照结论：9 个 commit 全部为 TAG0018（P0~P6）工作，无 P7 阶段（P1 已裁剪 P7，coupling_checklist 显式互链 checked）；CHANGELOG [0.57.0] 节以单条目完整覆盖该任务全部交付（对应 BDD-1~19 全部验收通过，P6-acceptance.md 19/19 PASS）——**对照无遗漏**。

### 2. 版本文件变更（version 双路径）

- README.md / README.zh-CN.md badge v0.56.0 → v0.57.0（README.md 是 `check-protocol-consistency.py` CHECK 7 校验的版本文件；P2 单包无独立 version 文件）
- bump 已实际编辑完成，`git diff` 可查；commit 时入暂存区即满足 gate_p8「暂存区有 version 文件变更」

### 3. CHANGELOG 变更（双路径）

- CHANGELOG.md 新增 [0.57.0] 节，`git diff` 可查；commit 时入暂存区即满足 gate_p8「暂存区 CHANGELOG 有变更」

### 4. bump 后重跑 P5 gate_commands（P8 卡要求）

| 命令 | 结果 | 判定 |
|------|------|------|
| `python3 -m pytest agate/tests/unit/test_dsh_preset.py -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp` | **8 passed**（0.04s，EXIT=0） | ✅ 8/8 绿 |
| `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` | **EXIT=1：1 个 ERROR = CHECK 7（README badge v0.57.0 != 最新 tag v0.56.0）**；319 个 WARNING（与 bump 前基线 319 完全一致，未新增）；无其他 ERROR | ⚠️ 见下方 DEBT0013 时序说明 |

**⚠️ DEBT0013 时序说明（非回归）**：CHECK 7 唯一 ERROR 是设计使然的中间态——bump 已完成（badge=v0.57.0）但 tag v0.57.0 尚未创建（`git describe --tags --abbrev=0` 仍返回 v0.56.0）。按 `phase-cards/P8-release.md`「gate 规则」DEBT0013 注意：P5 重跑应安排在 **commit + 创建 git tag 之后** 进行；主 Agent 创建 tag v0.57.0 后重跑同一条命令即 **0 ERROR**（本 bump 前基线已验证 0 ERROR，bump 未引入任何新 WARNING/新 ERROR，见下）。

### 5. bump 前基线对照（证明 bump 零污染）

| 状态 | EXIT | ERROR | WARNING |
|------|------|-------|---------|
| bump 前（git stash 后基线） | 0 | 0 | 319 |
| bump 后（本次 4 处改动） | 1 | 1（仅 CHECK 7 时序 ERROR） | 319（未新增） |

结论：4 处 bump 未引入任何新 WARNING、未引入任何新 ERROR（唯一 ERROR 是 CHECK 7 对"发布完成态"的校验，tag 创建后消失）。

### 6. SELF-GATE 触发面（BDD-19 核对，供主 Agent commit 参考）

- 本次 bump 触及 `README.md`（根级，命中 commit-msg-self-gate.py 触发面）与 `agate/UPGRADING.md`（`agate/**/*.md`）——**bump commit 的 message 须携带 `self-gate-skip:` 或 `self-gate-review:` 标记**（建议 `self-gate-skip: 版本 bump（badge/CHANGELOG/UPGRADING 纯版本号与发布文档更新，无协议机制改动），完整 self-gate review（protocol-alignment-review）随 P8 统一派发`——与 P4 commit bf69754 同款措辞）。
- 既有 P4/P6 提交已按 BDD-19 覆盖（bf69754/153c0a2 带 self-gate-skip；test_dsh_preset.py 不触发 self-gate），无遗漏。

## Lessons Learned

1. **「对外能力」任务 bump_type 判 minor 时，版本对照要落在"新增平台支持"而非修复体量上**：本任务无任何缺陷修复，纯增量交付，若只看"没改坏东西"容易误判 patch——但"官方支持第三个平台"是面向用户的对外功能（P1 裁剪说明 §5 明确"官方第三平台是面向用户的对外功能，需发版"），按 AGENTS.md 规则取 minor。判据应看"用户可见的新能力面"，而非改动行数。
2. **DEBT0013 的 CHECK 7 时序不是纸面条款，每次 bump 后都会真实撞上**：本任务 bump 后立即重跑 consistency 即复现 `badge v0.57.0 != tag v0.56.0` ERROR——这与 P8 卡注记完全一致。releaser 侧的正确动作是**记录基线对照（bump 前 0 ERROR → bump 后唯一 ERROR 可归因于 CHECK 7）**，用"WARNING 数不变 + 唯一 ERROR 归因明确"证明 bump 零污染，而不是把时序 ERROR 当回归排查或（更糟）去改版本文件迁就检查器。
3. **bump 面 = 版本引用文件清单（AGENTS.md 发布 checklist）是约束性的，不是参考性的**：README badge + README.zh-CN badge + CHANGELOG + UPGRADING 四处的版本号必须同步改——README.zh-CN.md 的 badge 是最容易被漏的一处（与 README.md 分离维护）。改完用 `git diff --stat` 核对恰好 4 处、无多余改动。

## 临时资源清单

**本任务全程未启动任何临时服务/进程/数据库/端口，无开发安装**（纯模板/文档/测试文件改动 + pytest 单元测试 + consistency 静态扫描）。

- 临时服务/进程：无
- 临时数据（测试数据库/临时文件目录）：仅 pytest basetemp `/home/kity/oclab/dsh-workspace/ptmp`（pytest 运行缓存目录，可留可清，非仓库内文件）
- 开发安装（editable install/全局包）：无

如实记录：**无临时资源**，主 Agent READY 收尾检查该项可直接勾选通过，无需额外清理动作。

## PROD_TOUCHED 声明

`[PROD_NOT_TOUCHED]` —— 本任务全程仅仓库内文件断言与测试执行，未触碰生产环境/生产数据/生产 API（P6-acceptance.md 附注同款声明）。
