# 变更日志

所有对 agate 协议的重要变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

---

## [0.13.0] - 2026-07-13

### 新增
- **P1 NEED_CONFIRM 检查**：check-gate.sh P1 分支加 NEED_CONFIRM 检查（与 P6 二行式对称），P1-requirements.md 含 `[NEED_CONFIRM]` 时 exit 1
- **P4/P5 不可裁剪检查**：check-pruning.sh 补检查 4/5（P4 实现底线 + P5 验证底线），与 P2/P6 不可裁检查对称
- **P3 裁剪条件收紧**：risk≠high可裁 → risk=low才可裁（medium/high 必须走 TDD 红灯），可裁比例从 ~80-90% 降到 ~33%
- **P4 gate 排除收窄**：从排除所有 .md/.yaml → 仅排除 agate 流程产物（`P[0-8]-*.md` + `.state.yaml`），配置类 .yaml 交付不再被误拦
- **P8 version 检测降级 WARNING**：不匹配时从 exit 1 降为 WARNING + `AGATE_VERSION_FILES` 环境变量覆盖
- **TEST_RUNNER_FLAGS + 可配汇总正则**：check-tdd-red.sh 支持 `TEST_RUNNER_FLAGS`（多 flag 展开）、`TEST_FAIL_PATTERN`/`TEST_ERROR_PATTERN`（适配 go test/cargo test/jest 等非 pytest 输出格式）
- **AGATE_TASKS_DIR 环境变量**：ci-gate-backstop.py 支持 `AGATE_TASKS_DIR` 配置任务目录路径 + 补 `import os`
- **review-mapping.md C8 机制警告**：顶部加 C8 是 mapping 机制而非结果的警告，项目方应基于本表扩展自己的 mapping
- **LIMITATIONS.md 局限 6/7/8**：运行时依赖（bash+git+python3+pyyaml）不限制被管理项目语言、vision/UI 验收依赖外部基础设施、CI backstop 仅 GHA

### 变更
- **P1 卡片评审措辞修正**：从"P1 评审与 P2 对称"改为"P1 评审通用必有，P2/P4 评审是 C8 域触发——二者不对称"
- **WORKFLOW.md 删"纯文档"范畴**：P3 裁剪条件从"纯文档/配置类"改为"配置类任务"，文档任务不是独立范畴，配置类仍是软件工作
- **state-machine.md 裁剪条件同步**：P3 从"high 风险不可裁剪"改为"仅 low 风险可裁剪"；补 P4/P5 不可裁剪
- **P3-tdd.md 裁剪条件同步**：从"risk≠high"改为"risk=low"
- **AGENTS.md 依赖节**：列出所有 8 个内联 python3 的 sh 脚本
- **check-protocol-consistency.py**：PATH_IGNORE_SUBSTRINGS 加 `docs/decisions/`（项目侧决策记录示例路径）

---

## [0.12.0] - 2026-07-12

### 新增
- **P1 强制需求评审**：P1 阶段须产出 `P1-review.md`（`status: approved` + `agent≠main` + BDD 锚点），gate 检查从 frontmatter 提取 status（非全文 grep，防正文误匹配）
- **P1 评审角色**：`assets/review-roles/requirements-review.md`，P1 阶段由独立 subagent 执行需求基线评审
- **do→review 迭代循环**：P2/P4/P6/P7 阶段卡片增加 do→review 迭代注释，retry 预算耗尽走 PAUSED
- **P5/P7/P8 subagent 派发**：P5 verifier / P7 consistency-reviewer / P8 releaser 均由 subagent 执行，主 Agent 只做 P0-brief + P8 READY 收尾
- **P7 一致性检查角色**：`assets/execution-roles/consistency-reviewer.md`，P7 阶段由 consistency-reviewer subagent 执行跨文件交叉检查
- **dispatch-context 扩展**：任务上下文节（目标/关注点/已知约束/与上阶段关联）+ P2 结构化字段 grep
- **gate 诊断落盘**：gate 失败时写入独立 `P{N}-gate-diagnosis.md`，不追加到 dispatch-context
- **N2 诊断格式禁令**：`gate-diagnosis.md` 和 dispatch-context 回退节禁止 `- PASS/FAIL` 行首（防误触审计2）
- **check-p6-format.sh**：`--fix`/`--check` 模式，仅修行首大小写+空白（无歧义自动修复），printf '%s' 防路径转义
- **PAUSED 语义翻转**：PAUSED = 正确路由（非失败），state-machine 13 处标注 + 8/8 阶段卡片 + WORKFLOW 声明
- **回退机制修正**：诊断→跳转→PAUSED→人工批准→修→重跑（替代"一次退一阶"）
- **CI 证据原则**：P6 验收声明"CI 证据原则"（L0），CI backstop 兜底外部产出 gate
- **subagent 假完成校验**：D2 最小校验 grep test runner 真实输出签名 + dispatch-prompt 返回前自检
- **P2 gate regex 放宽**：支持 Alternative/Option/多词方案名 + 数字编号（方案1/2/3）
- **verification_env 条件化**：仅 `ui_affected` 或 `e2e` 需要时声明，纯后端无需
- **CHECK 9 锚点表扩展**：6 条新增锚点（P1 review agent≠main / consistency-reviewer / dispatch-context / PAUSED / check-p6-format / gate-diagnosis）

### 变更
- `check-gate.sh` P1 分支：frontmatter 提取 status（替代全文 grep）
- `check-gate.sh` P7 分支：N3 WARNING（有 DESIGN_GAP_REVIEWED 但缺跨文件引用关键词 → WARNING，不改变 exit code）
- `check-gate.sh` P2 分支：regex 扩展支持数字编号方案名
- `dispatch-protocol.md`：P1 评审 + 迭代循环 + P5/P7/P8 派发 + 任务上下文 + 诊断落盘 + N2 + D2 + CI 证据 + verification_env
- `state-machine.md`：P1 转移 + P5/P7/P8 subagent 注释 + PAUSED 标注 + 回退修正 + 诊断落盘
- `WORKFLOW.md`：P1/P5/P7/P8 角色更新 + PAUSED 声明
- `orchestrator-template.md`：P1 不变量 + READY 交接 + 任务上下文 + verification_env
- `dispatch-prompt.md`：结构化任务节 + 返回前自检
- `verifier.md`：P5 subagent 派发说明
- `AGENTS.md`：角色清单新增 consistency-reviewer + requirements-review

## [0.10.0] - 2026-07-05

### 新增
- **逐阶段 commit 强制**：`check-state-transition.sh` 检查 3（commit gate）。推进 phase 到 Pn+1 前，Pn 产出必须已 commit——产出+推进同 commit 或产出从未 commit 均拦截。仅任务级 `.state.yaml`（`docs/tasks/Txxx/`）生效，根 `.state.yaml` 跳过。回退/PAUSED 恢复不受影响
- **拦截后处理策略**：`orchestrator-template.md` 补 8 种拦截类型对应处理方案 + 同一阶段累计 3 次拦截 → PAUSED
- **`git-integration.md` 标记强制执行**：每阶段 commit 规则由 `check-state-transition.sh` 强制执行

### 变更
- `check-state-transition.sh`: `get_old_phase` 支持任务级 `.state.yaml` 路径（`HEAD:docs/tasks/Txxx/.state.yaml`），不再只读根路径

## [0.11.0] - 2026-07-08

### 新增
- **main 分支保护**：GitHub required status checks（bats / shellcheck / consistency / gate-backstop），红 CI 阻断 PR 合入
- **CI gate-backstop job**：`protocol-tests.yml` 新增 `gate-backstop` job，CI 兜底重跑 gate + ci-gate-backstop.py
- **shellcheck -S warning**：CI shellcheck 过滤 info 级误报，只报 warning 及以上
- **bats fetch-depth: 0**：CI bats job 拉完整历史+tag，修复 CHECK 7 在浅克隆下失败

### 变更
- **CI workflow 合并**：`gate-backstop` job 并入 `protocol-tests.yml`，删除冗余的 `protocol-consistency.yml`。单一 workflow 为真相源，4 个 job：bats / shellcheck / consistency / gate-backstop
- **P2 不可裁剪**：删除 design_trivial / follows_existing_pattern / legacy_p2_pruned 例外口。design_trivial / follows_existing_pattern 语义改为"可简化 P2（1 个候选方案），不可省略 P2"
- **P6 不可裁剪**：删除 no_behavior_change 例外口。no_behavior_change 语义改为"可简化 P6（快速验收），不可省略 P6"
- **P7 裁剪加强**：声明"无隐式耦合"时须有 coupling_checklist 列出检查过的耦合点
- **T-G2.5 root_cause 更正**：从"bats not in CI"更正为"CI detective not preventive (no branch protection)"

---

## [0.9.1] - 2026-07-05

### 热修复
- **dispatch-context 强制化范围收窄**：v0.9.0 barrier 从"派发阶段任何 commit"改为"派发阶段产出 commit"。仅当该阶段的产出文件（P1-requirements.md / P2-design.md 等）被暂存时才要求 dispatch-context.md，避免拦截中间 commit / legacy 根 .state.yaml 任务 / 裁剪跳阶场景

---

## [0.9.0] - 2026-07-05

### 新增
- **Phase Card 渐进披露**：`agate/phase-cards/P{N}-*.md`（9 张）+ `agate/rules/state-transitions.md` + `review-mapping.md`（2 个）。主 Agent 按当前阶段只读一张卡片（~100 行），不再全量加载 8 个协议文件（~2900 行）。`orchestrator-template.md` mapping 表为默认入口，8 文件降级为 reference。旧 CHECK 5（协议文件计数校验）随之删除
- **agate-next-card.sh CLI**：输出当前阶段卡片全文（PHASE P0-P8）。9 个 sha256 byte-stability 硬证明测试。跨 checkout/CI 路径 hash 稳定（相对路径）
- **dispatch-context.md 防漂移**：新模板（`agate/assets/templates/dispatch-context.md`）+ hook 2p hash 校验。嵌入卡片 sha256 与 CLI 输出一致（防过期/防篡改）。**P1/P2/P3/P4/P6 派发阶段强制要求** dispatch-context.md 存在，缺则 exit 1
- **P0 gate 显式分支**：check-gate.sh 加 `P0` 分支，停止把标准阶段谎报为"未知"写入审计轨迹
- **pre-commit-gate.sh 2j/2k 容错**：仅 exit 1 拦截，exit 2 静默放过（与 2i 对齐）
- **self-gate-review:/skip: 加 ^ 行锚**：修复 commit body 任意位置提一句即绕过的假阴性
- **orchestrator-log.md 机制**：主 Agent 长操作前写 NEXT 锚点防无响应

### 变更
- 同 [Unreleased] 节（措辞修正 / LIMITATIONS 方向性错配 / self-gate 强制触发 / self-gate 递归终止 / CHECK 9 反向覆盖 / README gate 分类学 / CON.9 测试改写 / SELF-GATE 强制力边界）

### 破坏性变更
- 同 [Unreleased] 节（删 8 文件必读框架 + 删 CHECK 5 + state-machine.md:506 中断恢复语义更新 + 反向传播同步 + scripts/README.md 改检查数）

---

## [0.8.0] - 2026-07-02

### 新增
- **self-gate 反向传播机制**：SELF-GATE.md 派发模板加意图分析 + 反向传播两步。protocol-alignment-review 角色 A3 拆为 A3a（一致性连锁）+ A3b（反向传播），A5 加文档传播。加"反向传播常见路径"推理起点表。变更触发模式审查从"改了什么对不对"升级为"改了什么 + 应影响什么 + 影响到了没"
- **subagent 产出路径约束**：派发模板"## 输出"节加路径硬约束（不得将产出文件写入 /tmp 或其他路径）。新增"非阶段产出的路径规范"节覆盖 self-gate 审查/设计评审等场景。SELF-GATE.md 两个派发模板同步
- **pre-commit-gate.sh 多任务适配**：hook 扫描所有暂存的 `.state.yaml`（根 + `docs/tasks/{Txxx}/`），多任务架构下不再静默放行。新增 phase-产出一致性 WARNING（暂存了 P{n} 产出但 phase 不匹配时提醒，不拦截）

### 变更
- **check-state-transition.sh 行为变更**：
  - 回退跳变（差 ≥2 阶段）从 WARNING 恢复为 exit 1（强制 PAUSED）。之前因 `.gate-history.jsonl` 未实现降级，现确认 HEAD/staged diff 机制已隐式覆盖 PAUSED 验证，无需等待精确历史记录
  - 重试上限改为按阶段差异化：P3/P5/P6/P7/P8 = 2（上限定严，少轮次），P1/P2/P4 = 3。之前所有阶段统一为 3
- **check-retrospective.sh 同步**：复盘提醒的重试阈值改为按阶段差异化，与 check-state-transition.sh 保持同步
- **state-machine.md L407-411 回退跳变规则**：去绝对值，明确为回退方向（current - next >= 2）。前向跨阶跳不由本检查拦截，由 P5 gate 的阶段产出文件检查兜底
- **check-pruning.sh 行为变更**：
  - P8 裁剪新增 `internal_only_reason:` 字段检查（之前只查 `internal_only: true`，现在还需理由字段）
  - P6 裁剪新增"跳过风险:"评估要求（检查 7 条件补 P6）
- **check-gate.sh P2 行为变更**：
  - 新增 P2-review.md `status: approved` 检查（评审文件存在时）
  - 新增 P2-design.md 四字段计数（packages/domains/ui_affected/gate_commands ≥4）
  - 新增 P2-design.md 权衡/选择理由 form check
- **门槛表对齐**：P4 门槛从 `git log` / `P4-implementation/ 下文件非空` 改为 `git diff --cached` 暂存区检查（对齐脚本实际行为）
- **P3 裁剪措辞**：state-machine.md 从"需 risk_level=low"改为"high 风险不可裁"（对齐脚本实际行为——medium 放行）
- **P8 裁剪文档**：明确字段名 `internal_only_reason: <理由>`（之前只写"理由"未指定字段名）
- **md5 去重已实现**：check-p6-evidence.sh 新增截图 md5 重复检测（hook 强制），文档从"建议"改回"hook 强制"
- **BDD 总数对照**：从"="改为"≥"（允许 SCOPE+ 增补）
- **客观审计计数**：从"三道"统一为"四道"（R1b vision YAML 审计已落地）
- **P3 UI 用例**：从"gate 不通过"改为"主 Agent 确认"（P3 gate 不检查 UI 用例存在性）
- **pre-commit 表格**：补 P1.2 PROD_TOUCHED 行 + 调顺序对齐脚本实际执行顺序

### 影响
- 下游项目（如 PeekView）：重试超限会更早触发 PAUSED（少 1 轮），跨阶段回退会被强制 PAUSED（之前只警告）

---

## [0.5.0] - 2026-06-30

### 新增
- **hardening-roadmap Phase 1+2 完整实施**：9 项 pre-commit 检查脚本 + 1 CI backstop
  - P1.1 `check-gate.sh`：各阶段脚本化 gate（在 v0.4.0 已实现）
  - P1.6 `check-changelog.sh`：本次 `[0.5.0]` 条目含 task_id 检查（自动 run）
  - P1.7 `check-p6-evidence.sh`：P6/P7 阶段证据目录非空 + BDD 行数 ≥ 1
  - P2.1/P2.10 `check-p6-provenance.sh`：P6 客观行为审计（三道审计 + agent 字段协作规范）
  - P2.3-P2.5 `check-state-transition.sh`：状态转移合法性 + 重试上限
  - P2.7-P2.9 `check-pruning.sh`：裁剪条件 + override 校验
  - P2.11 `check-scope-resolved.sh`：`[SCOPE+]` 必须 `[SCOPE_RESOLVED]`
  - P2.12 `check-retrospective.sh`：异常模式提醒（不阻塞）
  - P2.15 `check-state-yaml.sh`：`.state.yaml` 格式校验
- **P6 客观行为审计三道硬拦截**（P2.1/P2.10 v2 降级方案）：
  - 审计 1：证据-结论对应（每条 PASS 引用证据路径 + PASS 数 ≤ 证据数 + 每个证据文件被 PASS 行引用）
  - 审计 2：`P{N}-dispatch-context.md` 禁止预判 PASS/FAIL
  - 审计 3：BDD 总数对照（P6 PASS 数 ≥ P1 BDD 数）
- **agent 字段协作规范**：阶段产出文件 Header 含 `agent: <角色>`（v2 协作层），缺字段 WARNING 不阻塞，`risk_level=high` + `agent=main` WARNING 建议派发独立 subagent
- **CI backstop（P1.3）**：`.github/workflows/protocol-consistency.yml` 增加 `gate-backstop` job，重跑 `check-gate.sh` + `ci-gate-backstop.py`（git blame P6 单 author WARNING 兜底）
- **目录结构重构**：协议本体移至 `agate/` 子目录，仓库根放项目资料（README/CHANGELOG/docs/等），`~/.agate` 软链接指向协议本体
- **`install.sh`**：一键 install（clone + 软链接），支持 `AGATE_REPO_DIR` 和 `AGATE_SYMLINK` 环境变量
- **`install-hook.sh`** 接受 AGATE_ROOT 参数：可在项目仓库内运行，明确指定 agate 路径
- **`pre-commit-gate.sh`** 路径分离：`AGATE_ROOT` 解析协议脚本（默认 `~/.agate` 软链接），`REPO_ROOT` 解析项目运行时文件
- **`agate/AGENTS.md`**：新建协议本体入口指引（角色清单 + 升级/卸载）
- **`check-protocol-consistency.py`**：`PROTOCOL_FILES/DIRS` 加 `agate/` 前缀；内部引用检查兼容子目录；FILE_COUNT_ANCHORS 锚点修复（指向真实声明位置）
- **`python3 -c "import ast"` 所有 Python 脚本语法验证通过**

### 变更
- **协议文档同步**：WORKFLOW.md / dispatch-protocol.md / state-machine.md 新增「Pre-commit 检查总览/全景」表；orchestrator-template.md 加 hardening-roadmap 关键机制段；verifier.md 加「Hardening 关键约束」段（PASS 引用证据 + dispatch-context 禁预判 + 诚实边界）
- **15 个角色文件 Header 加 `agent:` 字段**：6 个 execution-roles + 9 个 review-roles（与 role_id 对应）
- **RISK/gating 一致性**：P2 评审 risk=high 时必须派发独立 subagent，hook 对 agent=main 输出 WARNING
- **gate exit 语义统一**：`exit 0` 通过、`exit 1` 拦截、`exit 2` WARNING 不阻塞；跨脚本对齐
- **`scripts/check-p6-provenance.sh`** v2 实施：精确匹配（括号上下文）+ 只搜 PASS 行 + FAIL 词边界 + evidences/ 旧前缀兼容 + 隐藏文件排除
- **README.md**：安装命令改为 `git clone + ln -s`；新增「为什么装到 `~/oclab/agate`」段 + 常见误区 + 升级/卸载
- **.gitignore**：加 `*.swp/*.swo/*.bak/*~/.DS_Store`

### 移除/破坏性变更
- 无（向后兼容：v2 前存量任务 agent 字段缺失降级 WARNING 不阻塞）

### 修复
- agent 字段向后兼容陷阱：v2 引入前所有文件无 agent，缺失从 `exit 1` 降为 `exit 2` 不阻塞
- `get_agent()` 在 `set -euo pipefail` 下 grep 无匹配时 pipefail 传播 crash，加 `{ grep || true }` 修复
- `ci-gate-backstop.py` 中 P6 git blame 在新文件总是 WARNING 的噪音接受（M3 评审）
- 安装 hook 路径死锁：pre-commit hook 装在 agate 仓库自己时 `REPO_ROOT/scripts/` 不存在导致 gate 加载失败；用 `AGATE_ROOT` 软链接解析修复
- `__pycache__` 入库：`scripts/__pycache__/*.pyc` 被 commit；`.gitignore` 加 `__pycache__/` + `*.pyc` 防御
- 评测 README.md 末尾残留 `# test`
- `check-protocol-consistency.py` CHECK 5 FILE_COUNT_ANCHORS 第二个锚点位置错误（指向引用而非源声明）

### Known Limitations 更新
- `LIMITATIONS.md` 局限 3：v2 客观行为审计已落地（"等等" 内容已大段补全）
- 局限新增：空 png 充数仅验证引用存在性和数量，不验证内容真实性
- 局限新增：CI backstop 当前不重跑 `check-p6-provenance.sh`（只重跑 check-gate.sh），`--no-verify` 绕过 hook 时 provenance 也被绕过

---

## [0.4.0] - 2026-06-29

### 新增
- P3 gate 红灯 A/B 分类：B 类（import 未实现）exit 0 通过，A 类（测试代码 bug）exit 1。`PROJECT_MODULE` 环境变量提高精度，未设置退化为启发式
- P5 修复流程：修复 subagent 返回后主 Agent 必须重跑 P5 gate 全量测试，不是只检查修复项。修复重派 prompt 必须附修复历史
- P8 gate CHANGELOG 覆盖率检查：`git log v{prev_version}..HEAD --oneline` 对照 CHANGELOG 条目。`CHANGELOG_FILE` 环境变量支持非 CHANGELOG.md 项目
- P6 BDD 结果格式约定：必须用行首 `- PASS`/`- FAIL`，不用表格/emoji，保证 gate grep 可靠匹配
- P6 证据目录（`P6-evidence/`）：非空检查作为 self-authored gate 的造假成本提升措施
- gate 分类体系：外部产出 gate（P3/P4/P5）vs 自写文件 gate（P1/P2/P6/P7），⚠️ 标记造假风险较高的 gate
- `check-gate.sh`：P3/P4/P6/P7/P8 脚本化 gate 检查（exit 0/1/2）
- `check-protocol-consistency.py`：6 类结构一致性检查 + CI workflow
- 任务粒度指引：拆分判据从"输出异构性"改为"产出文件数 > 3"（T026 实验证实 dispatch prompt 模板可处理异构产出）
- `LIMITATIONS.md` 局限 3：self-authored gate 分类 + T026 事故记录
- CHANGELOG.md 变更日志 + README version badge 与 git tag 一致性检查（CHECK 7）

### 变更
- P6 gate exit code 从 0 改为 2：脚本化检查（FAIL=0/NC=0/证据非空）通过，但 BDD 总数对照需主 Agent 手动核实
- `check-tdd-red.sh`：新增 `PROJECT_MODULE` 环境变量，多语言 import 错误检测，TEST_RUNNER 输出契约文档化，pytest 作为参考实现
- `check-gate.sh` P8：新增 `CHANGELOG_FILE` 环境变量，扩展 version 文件匹配（go.mod/pom.xml 等），文档化单 commit 假设
- P6-evidence/ 子目录：`screenshots/` 和 `traces/` 标注为 UI 任务专属，`test-output.log` 通用
- gate 分类举例：从 pytest/vue-tsc 改为通用术语（test runner/type checker）

### 修复
- `check-tdd-red.sh`：`IndententationError` → `IndentationError` 拼写修复；SyntaxError 正则去重

---

## [0.3.0] - 2026-06-28

### 新增
- `check-gate.sh`：P3/P4/P6/P7 脚本化 gate 检查（exit 0/1 可判定，exit 2 需主 Agent 自判）
- `check-tdd-red.sh`：`TEST_RUNNER` 环境变量 + 回退链（$TEST_RUNNER → which pytest → exit 3）
- P8 gate：bump_type 字段检查、version 文件变更检查、CHANGELOG 变更检查
- T022 债务清还：P6 BDD 覆盖完整性、P8 bump 后重跑 P5、bump 判定指引、DEVIATION-CRITICAL 分类、写跑分离澄清、verifier 证据优先级（DOM > 交互 > vision）、compact 环境恢复（env_state in .state.yaml）

### 变更
- 状态机步骤 5：gate 命令分档——可 shell 化的（P3/P4/P7）写 shell 命令，不可的（P1/P2/P5/P6/P8）保留自然语言
- P5/P8 gate：bump 后必须重跑 P5 gate + bump_type 字段
- P7 gate：DEVIATION-CRITICAL 标记格式
- P8 gate：`git diff HEAD~1` 验证 version/CHANGELOG

---

## [0.2.0] - 2026-06-27

### 新增
- 分阶段落盘改为默认启用：每次派发 prompt 自带落盘指令，不再作为空返回后的补救措施
- P0-brief executor_env 补全、P0/P1 职责边界三层指引
- `LIMITATIONS.md` 局限 5：协议文档自身内部一致性验证不在流程内
- `WORKFLOW.md`：主 Agent 合法职责清单与降级硬边界

### 变更
- T020 评审修复：P6 单步函数旧表述修正（PASS/FAIL 二值），删除重复的写跑分离段落
- assets/ 与 orchestrator 同步 T016-T020 协议修复（6 个执行角色 + 4 个模板 + 所有协议文件）

### 修复
- T019 复盘修复：6 项（复盘机制核对清单模板、LIMITATIONS T019/T016 数据点等）
- T020 复盘修复：6 项（2 bug fix + 3 能力补充 + 1 已知限制）
- subagent 空返回根因验证：证实 `steps` 上限无效，分阶段落盘有效（5 组对照实验）

---

## [0.1.0] - 2026-06-26

### 新增
- 核心协议：状态机（P0-P8 阶段）、派发协议、工作流指南
- 角色体系：6 个执行角色（analyst/architect/test-designer/implementer/verifier/vision-analyst）+ 3 个评审角色
- orchestrator 模板：启动读取列表、平台专有配置区块
- git 集成、loop 编排、平台适配说明
- `LIMITATIONS.md`：5 个已知局限
- T016 复盘：5 项协议修复（输入导航、降级禁止、空返回恢复等）
- 专家评审：10 个 BLOCKER 修复 + 8 个建议

### 变更
- 通用化清理：移除 PeekView 特有内容（6 处）
- 标准安装位置：`~/.agate/`
- 上下文工程优化：orchestrator 启动时读取全部 7 个顶层文件

### 修复
- 模糊触发条件：git-integration 边界 + 评审角色判定标准
- 启动读取缝隙：orchestrator-template 改为强制启动读取，补中断恢复缝隙
