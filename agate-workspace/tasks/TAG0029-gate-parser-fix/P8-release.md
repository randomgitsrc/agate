---
phase: P8
task_id: TAG0029
type: release
parent: P7-consistency.md
trace_id: TAG0029-P8-20260904
status: draft
created: '2026-09-04'
agent: implementer
bump_type: patch
---

# P8-release — TAG0029 gate 命令解析器修复批（RM-AG0056）发布准备

> parent: P7-consistency.md（approved：blocker_count=0 / deviation_count=0 /
> deviation_critical_count=0 / DESIGN_GAP 0 条无需配对 / CODE-MAP 2/2 豁免判定零漂移）
> 本文件由 releaser subagent（implementer P8 模式）产出，只做发布准备——**不执行 git commit /
> git tag / bump-version / 不改 README / CHANGELOG / UPGRADING / roadmap 正文**
> （bump 与版本文件改动由主 Agent 在 gate 验证通过后亲自执行）。
> 环境隔离：[PROD_NOT_TOUCHED]（全程只读核验 + 产出本文件，未触碰协议本体/生产面）。

## 1. bump_type 建议与理由

**bump_type: patch**（v0.67.0 → v0.67.1）

理由（逐条，对齐 dispatch-context 判定）：

1. **修 bug，不改 API 行为（semver patch 主判据）**：本任务三处脚本改均为缺口修复——
   M1 值清洗 fail-closed（`agate-read-gate-commands.py` L57/L66）/ M2 P3 收集收紧为精确键
   （同文件 L60–67）/ M3 judge 补 exit 2 显式分支（`check-tdd-red.py`）/
   M4 R2 fixture 目录声明豁免（`check-platform-assumptions.py`）；
   DEBT0027 / DEBT0023 / RM-AG0056 均为修复 + 豁免机制，无破坏性变更。
2. **返回约定不变（非 major）**：`check-tdd-red.py` judge 新分支只改变 exit 2 输入的归属
   （从末尾 exit 0 改判 exit 1），`check-gate.py` 返回约定 0/1/2/3 含义不变（P2 §3.3）；
   `is_gate_meta_key` / `parse_gate_commands_block` 公共判据零触碰（P2 N3/N4，P7 C6）；
   `.state.yaml` schema 未动；3 个 hook 薄壳未动 → 非 major。
3. **非新功能（非 minor）**：无新增脚本、无新增协议机制（P2-design 候选 B 的协议级统一
   已明确不选），纯修复批 → 非 minor。
4. **M5 文档面属同版本附带**：P2 卡 gate_commands 节禁令子节（BDD-6）+ SELF-GATE 反向传播
   （`agate/assets/formatters/README.md` + judge docstring，commit c894cb9）均落在
   protocol-docs 包域内，不独立定版。
5. **单仓单版本**：pyproject.toml 无 version 字段；版本以 README badge + CHANGELOG 为准；
   P2 `packages: [gate-parser, tdd-judge, platform-scanner, protocol-docs]` 四包域均为
   `agate/` 协议本体单包发布范畴（见 AGENTS.md 版本发布清单：badge + CHANGELOG +
   UPGRADING 章节）——P8 卡「多包发布拆批」不触发，无需合并 subagent，无 `[SCOPE_GAP]`
   （prompt 包域覆盖与 P2 声明一致）。

版本号变更确认（供主 Agent bump 时核对，实测 2026-09-04）：

| 项 | 现状（实测） | 目标（主 Agent 执行） |
|---|---|---|
| 最新 git tag | v0.67.0（TAG0028 发布，主 Agent 已确认 badge 一致） | v0.67.1（待主 Agent 创建并推送） |
| README.md version badge（:12） | v0.67.0 | v0.67.1 |
| README.zh-CN.md version badge（:12） | v0.67.0 | v0.67.1 |
| CHANGELOG.md | [Unreleased] 节 = TAG0029 四条目（§3） | [0.67.1] - <发布日> |
| agate/UPGRADING.md | §3 最新章节为 v0.67.0（:92） | §3 新增 v0.67.1 章节（§4 草案） |
| pyproject.toml | 无 version 字段 | 不动 |

## 2. debt_check

**debt_check: reviewed**

已读 `agate-workspace/debt/tech-debt.md`（实读 DEBT0023 L814–841 + DEBT0027 L910–932
closure 原文；两条目 status 均为 open）。逐条核验结论如下：

| id | closure_criteria（原文） | 本任务核验结论 |
|---|---|---|
| DEBT0023（P3* 前缀键静默收集） | ① read-gate-commands 对 P3* 键收集行为有单测锁定 | ✅ P3 BDD-4（P3_xxx 不收集）/ BDD-5（裸 P3 收集 + 元键豁免）单测锁定，全 PASS |
| 同上 | ② 协议文档（P2 卡 gate_commands 节）写明 P3_xxx 键禁止声明及其原因 | ✅ BDD-6：`agate/phase-cards/P2-design.md` L182–189 禁令子节（含 §2.5 白名单后缀清单 + 原因），P6 BDD-6 PASS |
| DEBT0027（解析器行内注释/引号 + judge 假绿灯） | ① 对"命令值同行带注释"输入产出纯命令（注释剥离 + 引号闭合校验），或报解析错误 exit 非 0 | ✅ P3 BDD-1（纯命令）/ BDD-2（未闭合引号 fail-closed：exit 非 0 + stderr）单测锁定，P6 BDD-1/2 PASS |
| 同上 | ② 对测试运行器语法错误/不可解析输出判 exit 1（A 类），不再误判红灯可推进 | ✅ P3 BDD-3（exit 2 + 中英辅证 + 零运行器统计 → exit 1）单测锁定，P6 BDD-3 PASS（含中英各一例） |
| 同上 | ③ 单测覆盖：带行内注释 gate_commands 解析出纯命令；bash -c 执行不报 unterminated quote | ✅ 同①③，BDD-1 证据链含 `bash -c` exit ≠ 2 实测 |

- 条目 id 清单：`DEBT0023 / DEBT0027`（均为 reviewed，可引用；关闭由主 Agent 按 closure 流程定夺，本文件只留痕不主张关闭）。
- 其余 open 债务（DEBT0024/0025/0026 等）与本任务改动面无交集，均不阻断发布。
- 结论：`debt_check: reviewed`——两 DEBT 逐条核验，P3 BDD-4/5 + P6 BDD-4/5/6（DEBT0023）与
  BDD-1/2/3（DEBT0027）全 PASS。

## 3. CHANGELOG 更新确认（主 Agent 执行，本节为转正口径）

现状：`CHANGELOG.md` [Unreleased] 节已有 TAG0029 自审同步条目（A5，四条目 L13–18，
实测）。P8 确认将其转正为 `[0.67.1]` 新版本节：

- `[Unreleased]`（L11–18，含语义变更退役声明 + 值清洗 fail-closed + judge exit 2 分支 +
  R2 fixture 豁免四条）→ `[0.67.1] - <发布日>`（主 Agent 执行转正，标题建议
  `### 修复（TAG0029：gate 命令解析器与 TDD 红灯判定缺口修复，RM-AG0056）`，
  正文沿用现有四条，定稿权在主 Agent）。
- 语义变更条目（`P3_js` / `P3_html` 退役）已在 [Unreleased] 节显式声明，转正后即为本版本
  正式记录；UPGRADING 对应章节见 §4。

## 4. UPGRADING 章节确认（主 Agent 亲自执行）

**checklist 项（v0.62.0 教训）**：新版本**必须在 `agate/UPGRADING.md` §3 新增 v0.67.1 章节——
无破坏性变更也要写**，标题下首行标注「（无破坏性变更，零迁移动作）」；
CHECK 13（CHANGELOG↔UPGRADING 章节对应性）会机械校验漏写。

章节要点草案（对齐 v0.67.0 章节结构，插入位置 = v0.67.0 章节（:92）上方）：

1. **总标注**：本版本无破坏性变更，零迁移动作——未改 `.state.yaml` schema / 既有任务文件
   格式 / 3 个 hook 薄壳（P7 改动清单核对无 `.sh` 改动），无需重跑 `install-hook.py`
   （软链布局 `git pull` 即生效；Windows 复制模式重跑 SETUP.md 步骤 2 的 `cp`）。
2. **① gate 解析语义收紧——对合规任务零影响**：`P3_js` / `P3_html` 历史多栈形态退役
   （收紧为精确键）；真实任务 P2 从未声明 `P3_xxx` 检测键（P2 §2.5 存量证据），存量测试
   已同步 S1；未来多栈回归走协议修订登记收集后缀。值清洗 fail-closed 只影响"命令值同行
   带注释"写法（此前本就 `bash -c` 报 exit 2 失败），合规写法（独立行注释，TAG0028 fix2
   形态）行为不变。
3. **② judge exit 2 改判——对真实红灯零影响**：此前 exit 2（命令串本身语法错误，`bash -c`
   未起运行器）落末尾误判红灯可推进（假绿灯）；现改判 exit 1（A 类）。真实测试红灯
   （运行器正常退出）判定路径不变。
4. **③ R2 fixture 豁免——对代码面零影响**：豁免绑定目录声明（`agate/tests/fixtures/`
   路径前缀），仅 R2 数据面跳过；目录外裸 `python3` 调用仍命中 exit 1（BDD-8 锁定）。
5. **④ 升级动作**：`git pull` 即完成；无迁移动作。

## 5. 发布检查命令结论引用（releaser 不重跑，主 Agent 按 AUDIT7 分支定夺）

P2 §4 gate_commands 7 键执行结论引用自 `P5-test-results/unit.md`（复跑全绿，2026-09-04）：

| key | 结论（P5 实测） |
|---|---|
| P5 全量 pytest | 复跑 exit 0：`1444 passed, 2 skipped`（首次 1 failed 为 archive 时序类偶发 flaky，单跑/同文件整跑/全量复跑三振全绿，已记录） |
| P5_consistency | exit 0：0 ERROR / 329 WARNING（worktree 自有脚本，`--strict-errors-only`） |
| P5_shellcheck | exit 0（无输出，3 hook 薄壳，CI 同口径 `-S warning`） |
| P5_count_tests | exit 0：`总计 1446`（1444 passed + 2 skipped = 1446，口径一致） |
| P5_scanner / P3_scanner / P4_scanner | exit 0（无输出，0 命中干净通过；P3/P4 为常驻面存在性/跑通验证） |

- P3 由 `TEST_RUNNER` 环境变量覆盖跑裸 P3 命令（P2 §4 注记 + §1.3-R6 修前 bootstrap 机制）。
- AUDIT7 验证计划与 DEBT0013 时序注意（先 tag 后重跑）由主 Agent 按 P8 卡 gate 规则执行，
  本文件不含结果预判。

## 6. roadmap 回写 checklist（RM-AG0043 硬校验，主 Agent 执行）

- [ ] `agate-workspace/roadmap/roadmap.md` :62 **RM-AG0056** 行：「状态」列 `scheduled` → `done`
  （P8 gate 硬校验 RM-AG0043：关联任务 TAG0029 的 RM 条目未回写 done 即阻断）。已实测：
  roadmap.md 全文按 task_id 反查 TAG0029 仅 :62 一处
  （`| RM-AG0056 | … | scheduled | … | TAG0029 | 2026-09-03 | 2026-09-03 |`）。
- [ ] 回写时核对列结构：表头 7 列（id/标题/状态/来源/关联任务/创建/更新），按表内 done 行惯例
  同步「更新」列日期为回写当日（参照 RM-AG0055 done 行口径）。
- [ ] 回写与 P8 阶段 commit 同批（.state.yaml phase 与本次产出一致的同一 commit 产出面）。

## 7. 版本引用文件 checklist（Agateon 仓库特有，主 Agent 逐项执行）

| # | 文件 | 动作 | 现状锚点（实测） |
|---|------|------|---------|
| 1 | `README.md` | version badge v0.67.0 → v0.67.1 | :12 badge 行 |
| 2 | `README.zh-CN.md` | 中文镜像 badge 同步（v0.65.0/v0.66.0/v0.67.0 先例两 README 同批更新）；bump 时 `grep -n "v0.67" README*.md` 复核无遗漏 | :12 badge 行 |
| 3 | `CHANGELOG.md` | [Unreleased] → [0.67.1]（§3 转正口径） | §3 |
| 4 | `agate/UPGRADING.md` | §3 新增 v0.67.1 章节（无破坏性变更也写；CHECK 13 对应性校验） | §4 要点草案 |
| 5 | 其余硬编码版本 | **无**——文档优先写「稳定版」不写死版本号；pyproject.toml 无 version 字段，不动 | 已核 |

## 8. git log v0.67.0..HEAD 对照结论（供主 Agent 发布前复核）

- 本任务改动面（P7 §3.2 核对）：`agate-read-gate-commands.py`（M1/M2 → gate-parser）/
  `check-tdd-red.py`（M3 → tdd-judge）/ `check-platform-assumptions.py`（M4 → platform-scanner）/
  `agate/phase-cards/P2-design.md` 禁令子节（M5 → protocol-docs）+ 三项同步（S1 测试同步 /
  I1 顺手简化 / SELF-GATE 反向传播，P4-review 已裁决，均在包域内）。
- CHANGELOG [Unreleased] TAG0029 四条目与改动面一一对应，转正后无遗漏（§3）。
- P7 结论 BLOCKER=0 + P6 9/0 + judge 9/9 passed，主 Agent 发布前跑 P8 卡 gate 规则
  `git log v{prev}..HEAD --oneline` 对照 CHANGELOG 做最终复核。

## 9. 主 Agent 动作清单（P8 gate 通过后按序执行）

| # | 动作 | 依据 |
|---|------|------|
| 1 | `check-gate.py P8 $TASK_DIR` 跑 gate（bump_type/debt_check 字段 + roadmap done + tag 检查面） | P8 卡 gate 规则 |
| 2 | AUDIT7 判定 P5 证据：reuse_allowed → 复用 `P5-test-results/`；否则重跑 gate_commands 全键（DEBT0013：先 tag 后重跑） | P8 卡 gate 规则 |
| 3 | README.md:12 + README.zh-CN.md:12 badge v0.67.0 → v0.67.1 | §7 |
| 4 | CHANGELOG [Unreleased] → [0.67.1]（§3 转正口径） | §3 |
| 5 | UPGRADING.md §3 新增 v0.67.1 章节（无破坏性变更也写，CHECK 13） | §4 |
| 6 | roadmap.md:62 RM-AG0056 scheduled → done（7 列结构 + 更新日期回写当日） | §6（RM-AG0043） |
| 7 | `git tag v0.67.1 && git push origin v0.67.1` + `git ls-remote --tags origin v0.67.1` 验证远端到达（git push 默认不推 tag） | AGENTS.md 版本发布清单 |
| 8 | release PR **普通 merge（--no-ff）禁止 squash**（CHECK 7 / G-5 describe 依赖 tag 与 main 同轨） | AGENTS.md（v0.31.0 事故） |
| 9 | P8 commit message 须含 `self-gate-review:`（触发面：agate/scripts/* 三脚本 + agate/phase-cards/P2-design.md，P2 §6 env_constraints） | P0 env_constraints |
| 10 | G-5 最终验证：`git fetch origin && git describe --tags origin/main` == v0.67.1；`git merge-base --is-ancestor v0.67.1 origin/main` exit 0；合并后 CI 全绿 | AGENTS.md |
| 11 | READY 收尾检查（§10 临时资源清单清理 + 干净 checkout 跑 consistency 0 ERROR + 无 PROD_TOUCHED + 复盘判断） | P8 卡 READY 清单 |

## 10. 临时资源清单（releaser → 主 Agent READY 收尾交接）

| 类别 | 内容 |
|------|------|
| 临时服务/进程 | **无**——本任务全程未启动任何服务 / daemon / 调试进程（P2 env_constraints：pytest 仅本地跑；P5 无 debug server） |
| 临时端口 | **无**（无网络服务占用） |
| 开发安装 | **无**——未做 editable install / 全局包安装（pytest / pyyaml / ruff / pytest-xdist 均用既有环境） |
| 临时数据 | **无**——pytest 临时目录由 pytest 自管理；P5-test-results/（unit.md + fail-list.txt）已随任务目录入库（非临时资源）；无测试数据库、无临时文件目录残留 |
| 残留进程核查 | READY 收尾按 P8 卡逐项实际执行检查命令（`ps aux` 确认无 debug 进程 / `git status` 确认工作区干净），不得仅凭本清单打勾 |

## 11. Lessons Learned（主 Agent 汇入 docs/notes/lessons.md）

1. **流程 / P2-design 的显式取舍声明是 P8 发布说明的免费草稿**：§2.5「历史多栈形态退役 +
   白名单后缀清单」在设计期就写清了语义变更的取舍与存量证据，P8 的 CHANGELOG 转正口径
   （§3）与 UPGRADING 草案（§4）几乎逐字复用——"设计时把取舍写成面向用户的语言，发布时
   零翻译成本"。反之若设计只写实现语言，P8 还要二次翻译且易漏关键取舍。
   （来源任务 TAG0029，2026-09-04）
2. **测试 / fail-closed 校验必须配"残渣零产出"断言**：值清洗类修复若只断言"报错了"而不
   断言"没产出残渣命令串"，消费方仍可能拿到半截命令执行——BDD-2 把"exit 非 0 + stderr
   有解析错误 + 不产出残渣"绑成一条验收原子项，避免 fail-half-open 式半修复通过门槛。
   （来源任务 TAG0029，2026-09-04）
3. **架构 / 豁免机制优先选"目录声明绑定"而非"内容特征匹配"**：R2 豁免若用"含 fixture
   字样就跳过"宽匹配，真代码借用该字样即逃逸（R3）；绑定目录路径前缀后，借用方须把代码
   搬进 fixture 目录才逃逸——逃逸成本从"改一行字"升为"搬家"，且搬家本身在 review 可见。
   豁免设计的强度 = 逃逸成本，评审豁免先问"借用它要付出什么"。
   （来源任务 TAG0029，2026-09-04）

## 12. SELF-GATE 注记（触发面声明）

本任务触发 SELF-GATE（P2 §6 env_constraints）：

- 触发文件面：`agate/scripts/agate-read-gate-commands.py` / `agate/scripts/check-tdd-red.py` /
  `agate/scripts/check-platform-assumptions.py`（M1–M4）+ `agate/phase-cards/P2-design.md`
  （M5 禁令子节）。
- **P8 commit（主 Agent 执行）message 必须含 `self-gate-review:`**（协议本体最终发布 commit，
  与 P4/P6 同触发面）；协议文档改动已由 P5_consistency（`--strict-errors-only`）0 ERROR 验证。
