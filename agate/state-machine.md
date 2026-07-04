# 状态机落盘设计

> agate，解决"LLM 不能稳定执行长循环"的问题

---

## 核心思想

**状态存在文件里，不在 LLM 的记忆里。**

LLM 不是可靠的循环执行器。让它"一直 while 下去"，跑几轮后会忘记自己在循环里、会偏离、会自己开始干活。所以 agate 不依赖 LLM 记住状态，而是每一轮都从文件读状态、执行一步、把新状态写回文件。

即使会话被压缩、中断、重启，主 Agent 重新读文件就知道接着干什么。

---

## 状态存在哪

状态分两层落盘：

### 第一层：任务看板（active-tasks.md）

记录每个任务的**当前阶段、状态、重试记录**：

```markdown
| 序号 | 任务名 | 状态 | 阶段 | 重试 | 更新日期 |
|------|--------|------|------|------|----------|
| T001 | example-task | 🔄 进行中 | P4 | 0 | YYYY-MM-DD |
```

这是"宏观状态"——任务走到哪了。

**首次接入项目时，`docs/tasks/` 和 `active-tasks.md` 不存在，这是正常情况，不是异常**：

```
主 Agent 任何时候要读 active-tasks.md 之前，先检查：
  docs/tasks/active-tasks.md 是否存在？
    存在 → 正常读取，按下面的状态机推进
    不存在 → 这是项目第一次接入 agate：
      1. mkdir -p docs/tasks/
      2. 从 {agate_root}/assets/templates/active-tasks-template.md
         复制结构到 docs/tasks/active-tasks.md（清空示例数据，保留表结构）
      3. 视为"无进行中任务"，可以直接创建第一个任务（T001）
```

不要把"文件不存在"误判为错误或异常，更不要因为读不到文件就假设任务已完成或卡住——这是初始化场景，唯一正确动作是建表，然后继续往下走。

### 第二层：阶段产出文件（docs/tasks/Txxx/Pn-*.md）

每个阶段的产出文件本身就是"这个阶段完成了"的证据。文件的 Header 里有可判定字段：

```yaml
---
phase: P2
task_id: T001
parent: P1-requirements.md
trace_id: T001-P2-YYYYMMDD
status: approved        # ← 门槛判定字段
---
```

这是"微观状态"——每个阶段的门槛过没过。

---

## 状态机定义

```
状态集合：{ P0, P1, P2, P3, P4, P5, P6, P7, P8, READY, DONE, PAUSED }
（P0 是主 Agent 亲自执行的简报阶段，不派发 subagent，完成后直接进入 P1）

转移规则（主 Agent 亲自跑命令验证，不靠读 subagent 产出文件字段）：
注意：所有"文件存在"判定 = 文件存在 AND 含合法 Header AND 有实质内容
     （不能只看文件存在——subagent 可能写一半崩了，留下空/半截文件）

P0 --[P0-brief.md 完成，五字段自查通过（task/known_risks/executor_env/env_constraints/pruning_tendency）]--> P1
P1 --[P1-requirements.md 有效 AND 含至少一条 BDD 验收条件 AND 无未决 NEED_CONFIRM AND 无 status: GAP（不含 supplementable）]--> P2
P1 --[存在未决 NEED_CONFIRM]--> PAUSED（等人确认方向）
P1 --[存在 status: GAP]--> PAUSED（等人补充能力/确认降级方案。supplementable 不阻塞，见 dispatch-protocol.md「supplementable 能力的传递规则」）

任意阶段 --[出现 PROD_TOUCHED]--> PAUSED（生产环境被意外触碰，需人工处置）
任意阶段 --[出现 NEED_CONFIRM（不可逆操作）]--> PAUSED（等人确认后才可执行）

P2 --[P2-review.md 有效 AND status==approved AND P2-design.md 声明 packages/domains/ui_affected/gate_commands AND 候选方案≥2 AND 含权衡/选择理由]--> P3
P2 --[P2-review.md status==rejected && retry<MAX]--> P2 (retry+1)
P2 --[retry>=MAX]--> PAUSED
    （若 P2 设计涉及 UI：P2-design.md 必须声明 ui_affected: true，并列出需 E2E 覆盖的交互点）

P3 --[scripts/check-tdd-red.sh exit 0 AND assertion_failures>0 AND collection_errors==0]--> P4
    （TDD 红灯：测试正确但因实现未写而断言失败。collection/import error 视为测试本身错误）
    （若 P2 声明 ui_affected：P3 必须包含对应的 Playwright/E2E 用例，主 Agent 确认）
P3 --[retry>=MAX]--> PAUSED

P4 --[暂存区含非 md/yaml 文件（git diff --cached）]--> P5
    （不能用 git diff，因为 P4 完成时会 commit，git diff 永远是空）
P4 --[retry>=MAX]--> PAUSED

P5 --[P2 gate_commands.P5 命令 exit 0 AND failed==0 AND 无 [PROD_TOUCHED] 标记 AND (若 ui_affected: P2 gate_commands.P5 E2E 命令 exit 0)]--> P6
    （gate 命令从 P2-design.md 的 gate_commands.P5 动态读取，不硬编码 pytest。规则见 dispatch-protocol.md「P5/P6 gate 命令固化（B7）」节）
    （UI 任务：P5 必须实际运行 Playwright，不能跳过、不能靠"代码看起来对"判断）
    （「测试环境隔离正常」判定：
      ① 无 [PROD_TOUCHED] 标记（被动检测）
      ② 若项目有生产数据状态检查机制：对比测试前后生产库状态（记录数/checksum），
         差值 > 0 说明测试写入了生产环境 → P5 失败。
         具体检查方式由项目约定（如 conftest snapshot），agate 不硬编码路径。
      ③ 以上均为最低要求，项目应在代码层面实现强制隔离（见 README 隔离原则）。）
    （若 P5 过程中出现任何 [PROD_TOUCHED] 标记 → 立即 PAUSED，不允许进入 P6）
P5 --[failed>0 && retry<MAX]--> P4 (retry+1)
    （修复后必须重跑 P5 gate 全量测试，不是只检查修复项。T027 教训：修复引入回归）
    （修复重派 prompt 必须附修复历史，避免 subagent 重复踩坑。见 dispatch-protocol.md「P5 修复流程」）
P5 --[有 PROD_TOUCHED]--> PAUSED（生产环境被触碰，需人工处置后才能继续）
P5 --[retry>=MAX]--> PAUSED

P6 --[scripts/check-gate.sh P6 exit 2（FAIL=0/NC=0/证据非空）AND scripts/check-p6-provenance.sh exit 0 或 exit 2（证据-结论对应 + dispatch-context 审计 + BDD 总数对照）AND 主 Agent 手动核实 BDD 总数 = P1 BDD 总数（provenance exit 2 时必做）]--> P7
     ⚠️ self-authored（降级缓解：provenance 审计，根治待 Phase 3 平台支持独立 git author）
     （验收 = 把 P1 的 BDD 条件逐条实际跑一遍，结果翻译成人能看懂的行为描述）
     （涉及显示/交互的 BDD 条件：必须 Playwright 实跑 + 截图佐证，不接受"应该能工作"）
     （"⚠️ 调整"等中间态不合法——T019 教训：BDD-4 标"⚠️ 调整"就推进到 P7）
P6 --[任何 BDD 标 FAIL && retry<MAX]--> P4 (retry+1)（行为不符 → 回实现）
P6 --[存在未决 NEED_CONFIRM]--> PAUSED（验收结果需人判断方向）
P6 --[retry>=MAX]--> PAUSED

P7 --[! grep -qE '^\s*-?\s*\[BLOCKER\]' P7-consistency.md AND ! grep -qE '^\s*-?\s*\[DEVIATION-CRITICAL\]' P7-consistency.md AND (grep -cE '\[DESIGN_GAP:' P7-consistency.md) == (grep -cE '\[DESIGN_GAP_REVIEWED' P7-consistency.md)（v0.6：P4 implementer 自主决策偏差声明，主 Agent 审查后追加 REVIEWED 配对标记，未配对 → gate 不通过）]--> P8
    （已知限制：P7 定性分析不可全自动验证。主 Agent 可抽查 1-2 条一致性声明，
     完整性由 P5 回归测试兜底）
P7 --[retry>=MAX]--> PAUSED

P8 --[每个声明的 package 的发布检查命令 exit 0 + bump-version 后重跑 P5 gate（gate_commands.P5 exit 0 AND failed==0）+ P8-release.md 含 bump_type: 字段 + git diff --cached --stat 确认各包 version bump + git diff --cached -- CHANGELOG.md 非空]--> READY
     （gate 命令集由 P2-design.md 的 packages + gate_commands 字段动态生成，不同项目不同命令，agate 不硬编码。规则见 dispatch-protocol.md「packages 动态注入（B4/B6）」节）

### READY 收尾检查（P8 gate 通过后、标记 READY 前）

P8 gate 通过 ≠ 直接标记 READY。主 Agent 必须逐项检查：

**状态与版本：**
- [ ] .state.yaml phase == READY
- [ ] active-tasks.md 任务行状态已更新
- [ ] git 工作区干净（git status 无 untracked）
- [ ] git tag 已创建

**测试环境已清理：**
- [ ] 调试服务/进程已停止（启动的 debug server、临时 daemon）
- [ ] 临时数据已删除（测试创建的临时数据库、临时文件目录）
- [ ] 测试占用的端口已释放

**开发环境已还原：**
- [ ] 开发安装已卸载（editable 安装、全局包安装等非标准安装方式已还原）
- [ ] 系统环境无污染（PATH、Python path、node_modules 等无开发残留）
- [ ] 项目依赖恢复到发布版本（非开发分支的源码挂载）

**生产环境无残留：**
- [ ] 生产数据库无新增/修改记录（对比任务前后，测试不应触碰生产 DB——若有 [PROD_TOUCHED] 则此项已失败）
- [ ] 生产服务无残留影响（生产服务加载的代码/配置仍为上次发布版本，未被开发操作覆盖）
- [ ] 生产环境无孤儿资源（测试产生的文件、缓存、定时任务等未残留在生产路径）

任一项未通过 → 不进入 READY，逐项修复后重新检查。
生产环境相关项未通过 → 立即 PAUSED 报告人工（生产残留不可自行清理）。

阶段跳过转移规则（P1 裁剪声明驱动）：
  P1-requirements.md 的「裁剪说明」声明 phases: [列表]，主 Agent 据此跳过未列出的阶段。
  跳过时，当前阶段的 gate 自动判定为"通过"，直接转移到裁剪声明中的下一个阶段。

  **裁剪条件（hook 验证，见 scripts/check-pruning.sh）**：
  - 裁剪 P2：不可裁（v0.6：方案设计 + 评审是必经阶段。P1 analyst 做需求分析不做方案设计，无法预知 P2 architect 会发现哪些 P0/P1 没想到的问题。例外口：`design_trivial: true` 纯 typo/文案/配置值修改，或 `follows_existing_pattern: [参照文件]` 照搬已有模式。过渡期：`legacy_p2_pruned: true`）
  - 裁剪 P3：high 风险不可裁
  - 裁剪 P6：不可裁（除非 no_behavior_change: true）
  - 裁剪 P7：需源码文件数 ≤ 5 AND 无 implicit_coupling 声明（隐式耦合维度，self-declaration。如共享 CSS class、API schema、数据模型、配置项等）
  - 裁剪 P8：需声明 internal_only: true + internal_only_reason: <理由>

  **裁剪理由格式**：每条裁剪须含"跳过风险:"评估。没有评估风险的裁剪 = 无效裁剪。
  （局限性：这是 self-declaration nudge——"跳过风险: 低"可以无脑填，但强制写一行制造"我考虑过风险"的形式义务）

  **P7 语义**：P7 是"实现是否偏离 P2 设计"，不是"是否跨端"。跨端一致性是 P7 的子集，不是 P7 的全部。
  
  **裁剪声明回写（P2.9）**：若主 Agent 决定不执行 P1 声明的裁剪（保留被裁剪的阶段），
  必须在 P1-requirements.md 追加 override 字段。

  可跳过的阶段及其跳过转移：
    跳过 P2（无设计阶段）→ P1--[P1 gate 通过]--> P3 或 P4（取决于 phases 列表）
    跳过 P3（无 TDD）→ P2--[P2 gate 通过]--> P4
      （P3 跳过时 P4 gate 不要求红灯变绿，P5 的 pytest 全绿兜底）
    跳过 P6（无验收）→ P5--[P5 gate 通过]--> P7
    跳过 P7（无一致性检查）→ P6--[P6 gate 通过]--> P8
    跳过 P8（无发布）→ P7--[P7 gate 通过]--> DONE（仅限不涉及发布的内部任务）

  不可跳过的阶段：P1（需求基线）、P4（实现）、P5（技术验证）
    P1 基线是全流程脊梁，无论任务大小都需建立（小任务可简化，见 WORKFLOW.md 适用边界）
    P4/P5 是交付底线——没有实现和验证就没有可发布产物

  gate 判定方式：主 Agent 读 P1-requirements.md 的 phases 字段，确认跳过列表，按上述转移规则推进。
  若 P1 声明的 phases 列表与实际 gate 判定冲突（如声明跳过 P6 但 P5 发现行为不符需验收），主 Agent PAUSED 报告人工决策。

特殊转移（SCOPE+ 定向回补）：
任意阶段 Pn 产出含 [SCOPE+] → 主 Agent 增补 P1 基线 → 判断影响范围 → 定向回补：
  Pn --[SCOPE+ 增补基线]--> P1（仅增补 requirements.md，不重跑 P1 分析）
  → 主 Agent 判断该新需求实际需要哪些阶段，定向回到最早受影响的阶段
  ⚠️ 已知限制：「判断影响范围」目前依赖主 Agent 临场判断，无明确决策规则。
     T004/T005/T006 均未触发 SCOPE+，尚无实战数据支撑规则化。
     下一个触发 SCOPE+ 的任务应记录判断过程，供后续规则化参考。
  → 例：P5 发现需写新代码 → 回 P4；仅验收条件遗漏 → 仅补 P6
  → 回补阶段完成后，沿正常转移继续，已完成且未受影响的阶段不重跑
  retry 计数：定向回补不清零目标阶段已有的 retry（防止借回补绕过重试上限）

  **[SCOPE_RESOLVED] 标记（P2.11）**：主 Agent 增补 P1 基线时，必须标记 [SCOPE_RESOLVED: from {来源文件}]。
  未标记的 [SCOPE+] → gate 拦截（scripts/check-scope-resolved.sh）。

## Pre-commit 检查全景（hardening-roadmap Phase 1-2 已落地）

每次 `git commit` 触发 pre-commit hook，按以下顺序自动运行；详细机制见 WORKFLOW.md「Pre-commit 检查总览」：

| 检查（编号 = hardening-roadmap 机制编号）| 触发条件 | 拦截行为 |
|------|--------|------|
| **P1.1** gate (scripts/check-gate.sh) | phase 变更或阶段产出变更 | exit 1 拦截 |
| **P1.6** CHANGELOG (scripts/check-changelog.sh) | gate 通过后 | 缺 `[Unreleased]` → 警告不拦截 |
| **P1.7** P6 证据 (scripts/check-p6-evidence.sh) | phase ∈ {P6,P7} | 缺证据目录/BDD → 拦截 |
| **P2.1/P2.10** provenance (scripts/check-p6-provenance.sh) | gate 通过后 | 四道客观审计失败 → exit 1 拦截；agent 字段/BDD 非标 → exit 2 警告 |
| **P2.3-P2.5** 状态转移 (scripts/check-state-transition.sh) | gate 通过后 | 非法转移 → exit 1 拦截 |
| **P2.7-P2.9** 裁剪 (scripts/check-pruning.sh) | gate 通过后 | 裁剪条件不满足 → exit 1 拦截 |
| **P2.11** SCOPE_RESOLVED (scripts/check-scope-resolved.sh) | gate 通过后 | 缺标记 → exit 1 拦截 |
| **P2.12** 复盘提醒 (scripts/check-retrospective.sh) | gate 任何结果 | 检测异常模式 → 提醒写复盘（exit 0 不拦截）|
| **P2.15** 格式校验 (scripts/check-state-yaml.sh) | `.state.yaml` 暂存变更 | 格式错误 → exit 1 拦截 |

**多任务 hook 扫描**：pre-commit-gate.sh 扫描暂存区中所有变更的 `.state.yaml`（根目录 + `docs/tasks/{Txxx}/`），对每个文件独立跑格式校验 + 状态转移 + gate。phase-产出不一致（暂存了 P{n}-*.md 但 phase 不匹配）只发 WARNING 不拦截。

**CI 兜底（P1.3）**：push 后 GitHub Actions 重跑 `check-gate.sh` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的 commit。

特殊转移：
READY --[人手动触发 make publish]--> DONE

PAUSED 恢复协议：
  PAUSED --[人工确认/决策]--> 恢复到 PAUSED 前的阶段

  恢复步骤：
  1. 主 Agent 重读该任务的 .state.yaml → 获取 PAUSED 前的阶段和 retry 计数
  2. 人工回复的内容写入 docs/tasks/{Txxx}/PAUSED-resolution.md（含 Header）
  3. 主 Agent 将 PAUSED-resolution.md 路径加入重派 prompt（"人工决策见此文件"）
  4. 按 PAUSED 前的阶段重新派发 subagent

  recovery_bonus：若 PAUSED 原因是 retry 耗尽（如 P2 retry=3/3），恢复后该阶段获得 recovery_bonus=1（允许额外 1 次重试），避免恢复后立即再次超限导致无意义循环。recovery_bonus 写入 .state.yaml 对应阶段的计数。

  PAUSED 期间 SCOPE+ 处理：
  - SCOPE+ 在 PAUSED 期间暂不处理，等恢复后一并纳入 P1 基线增补
  - 如 SCOPE+ 与 PAUSED 原因相关（如验收中发现新需求导致 NEED_CONFIRM），恢复时优先处理

进入 READY 时（P8 gate 通过后，写状态前）：
主 Agent 必须立即输出交付小结（强制，不可跳过）：
  格式见 dispatch-protocol.md「任务完成小结」模板：
    [{task_id}] READY — {task_name} {version}
    改动：{git diff --stat 提取}
    验证：{各阶段 gate check 结果 + 验收 BDD 条目通过数}
    说明：{一句话设计摘要}
    下一步：make publish（人工触发）
  这是主 Agent 对 PM 的正式交付，是任务编排层的职责。
```

每次转移后，把新状态写回 active-tasks.md。

**"有效"的定义**：文件存在 + 含合法 Header（phase/task_id/parent/trace_id）+ 有实质内容（非空、非半截）。只看"文件存在"会被 subagent 写一半崩溃留下的垃圾文件误导。

**P3 红灯的特别说明**：TDD 要求测试先失败，但"失败"有三种——
- (1) 经典红灯：测试逻辑对，因实现未写而断言不满足（assertion failure）→ 通过
- (2) B 类红灯：测试逻辑对，因依赖模块未实现而 import 失败（T027 教训：P3 test-designer 不写 stub，所以 TDD 红灯几乎都是此类）→ 通过
- (3) A 类错误：测试代码自身有语法/import 错误，根本跑不起来 → 不通过

门槛接受**前两种**（assertion failure 或 B 类 import failure），拒绝第三种。

**判定方式**：主 Agent 跑 `scripts/check-tdd-red.sh`（见下），不自行解析 pytest 输出。脚本输出 `assertion_failures=N, collection_errors=M` 格式，gate 判定为 exit 0（含经典红灯和 B 类红灯）。

**`scripts/check-tdd-red.sh` 设计**：

```bash
#!/bin/bash
# 检查 TDD 红灯：区分 A 类（测试代码有 bug）和 B 类（实现未写的 import 失败）
# 退出 0 = 正确红灯（assertion failure > 0, collection error == 0）或 B 类红灯（import 未实现）
# 退出 1 = A 类错误（测试代码自身有语法/import 错误）
# 退出 2 = 测试全绿（说明实现先于测试写完，违反 TDD）
# 退出 3 = 找不到测试运行器
#
# 本脚本是 pytest 的参考实现。agate 是通用协议，不绑定特定技术栈。
# 非 Python 项目应提供自己的 TDD 红灯检查脚本，遵循 TEST_RUNNER 输出契约
#（见 scripts/check-tdd-red.sh 完整注释）。
#
# 环境变量 TEST_RUNNER：主 Agent 从 P0-brief.md env_constraints.debug_env 提取。
# 环境变量 PROJECT_MODULE：项目模块前缀（用于 B 类检测），未设置则退化为启发式。

if [ -n "$TEST_RUNNER" ]; then
    RUNNER="$TEST_RUNNER"
elif command -v pytest &>/dev/null; then
    RUNNER="pytest"
else
    echo "TDD_CHECK: no test runner found. Set TEST_RUNNER env var." >&2
    exit 3
fi

RESULT=$($RUNNER -q 2>&1)
EXIT=$?

FAILED=$(echo "$RESULT" | grep -oP '\d+ failed' | grep -oP '\d+')
ERRORS=$(echo "$RESULT" | grep -oP '\d+ error' | grep -oP '\d+')

echo "assertion_failures=${FAILED:-0}, collection_errors=${ERRORS:-0}"

if [ "$EXIT" -eq 0 ]; then
    echo "TDD_CHECK: tests pass, no red-light"
    exit 2
fi

if [ "${ERRORS:-0}" -eq 0 ] && [ "${FAILED:-0}" -gt 0 ]; then
    echo "TDD_CHECK: classic red-light (assertion failures only)"
    exit 0
fi

if [ "${ERRORS:-0}" -gt 0 ]; then
    IMPORT_ERRORS=$(echo "$RESULT" | grep -E '(ImportError|ModuleNotFoundError|Cannot find module|ClassNotFoundException|NoClassDefFoundError|unresolved import):' || true)
    if [ -n "$IMPORT_ERRORS" ]; then
        SYNTAX_ERRORS=$(echo "$RESULT" | grep -E '(SyntaxError|IndentationError|CompileError|ParseError)' || true)
        if [ -z "$SYNTAX_ERRORS" ]; then
            if [ -n "$PROJECT_MODULE" ]; then
                INTERNAL_IMPORT=$(echo "$IMPORT_ERRORS" | grep -E "(from ${PROJECT_MODULE}|import ${PROJECT_MODULE}|${PROJECT_MODULE}\.)" || true)
                if [ -n "$INTERNAL_IMPORT" ]; then
                    echo "TDD_CHECK: B-class red-light (project module '${PROJECT_MODULE}')"
                    exit 0
                else
                    echo "TDD_CHECK: A-class error (not from project module '${PROJECT_MODULE}')"
                    exit 1
                fi
            else
                echo "TDD_CHECK: B-class red-light (heuristic: no syntax errors)"
                exit 0
            fi
        fi
    fi
    echo "TDD_CHECK: A-class error (test code has bugs)"
    exit 1
fi

echo "TDD_CHECK: unexpected test result"
exit 1
```

**P8 与 READY 的说明**：

P8 是**「发布准备」**，不是「发布」。P8 gate 通过后进入 READY 状态——表示每个受影响包的版本 bump、CHANGELOG 更新、测试全通过，**已准备好发布**。实际的 `make publish`（上传到 PyPI）由人手动触发。

| 概念 | 含义 | 谁执行 |
|------|------|--------|
| 发布准备 (READY) | 各包 version bump + CHANGELOG + lint + test 全通过 | Subagent + 主 Agent 验证 |
| 发布 (DONE) | 上传到 PyPI | 人手动触发 |

**多包发布**：一个任务可能涉及多个独立版本的包（如 backend + mcp-server）。P8 必须为 P2 声明的**每一个** package 执行 version bump 和发布检查，gate 命令由 packages 列表动态生成。漏 bump 某个包 = gate 不通过。

---

## 主 Agent 的单步执行（一轮）

主 Agent 不跑 while 循环，而是执行"单步函数"，每次调用推进一个阶段：

```
function 执行一步(task_id):
    1. 读 .state.yaml 或 active-tasks.md → 得到 (当前阶段, 重试记录)
       **状态标记绑定检查**（T019 教训：.state.yaml 标了 P5 但无 P5 产出）：
       .state.yaml 的 phase 标记为 Pn，但 docs/tasks/{task_id}/ 下 Pn 产出文件
       不存在 → 无效标记，回退到 Pn-1 重新执行 gate。标记前必须验证 gate。
    1.5 环境一致性验证（若 .state.yaml 含 env_state 字段）

       若 .state.yaml 含 `env_state:` 块（运行时环境状态，如 debug backend URL、test entry ID、端口等）：
       - 验证这些状态在当前环境中仍有效（具体检查方式由项目自定，如 curl health check、查询 entry 是否存在）
       - 若任一失效：重新创建对应资源，更新 .state.yaml 的 env_state，commit 修订
       - 若环境全部失效 → PAUSED 报告人工

       注意：此步骤只适用于 .state.yaml 显式记录了 env_state 的任务。
       无 env_state 的任务跳过此步骤。
    2. 若当前阶段 == P0：主 Agent 亲自写 P0-brief.md（见 dispatch-protocol.md 步骤0），完成后继续
       否则：确认 docs/tasks/{task_id}/P0-brief.md 已存在（必填字段：task/known_risks/executor_env/env_constraints/pruning_tendency）
       读 docs/tasks/{task_id}/ → 确认当前阶段输入文件就绪
    3. 派发当前阶段的 subagent（见 dispatch-protocol.md）
    4. subagent 返回摘要（路径 + 一句话）
    4.5 扫描 subagent 产出是否含 [SCOPE+] 或 [SCOPE_GAP]：
        - [SCOPE+]：发现新隐含需求 → 增补 P1 基线 → 定向回补（见特殊转移）
        - [SCOPE_GAP]：prompt 漏了 P2 已声明的改动 → 暂停修正 prompt 重派
        （subagent 的自我检查结果仅供参考，不作为 gate 判定依据——gate 以主 Agent 跑命令为准）
    5. 主 Agent 亲自跑 gate 命令验证门槛（A1 原则：跑命令不信文件）：
       - P1: P1-requirements.md 含 ≥1 条 BDD 条件（BDD 编号格式不固定，按实际格式 grep）;
             grep -cE '\[NEED_CONFIRM\]' {task}/P1-requirements.md → =0;
             grep -cE 'status:.*GAP\b' {task}/P1-requirements.md → =0（仅匹配 status: GAP，不匹配 supplementable）
       - P2: grep 'status: approved' {task}/P2-review.md → 命中;
             grep -cE '^(packages|domains|ui_affected|gate_commands):' {task}/P2-design.md → ≥4;
             候选方案 ≥2; grep -qE '权衡|选择理由' {task}/P2-design.md → 命中
       - P3: scripts/check-tdd-red.sh → exit 0（含经典红灯和 B 类 import 红灯）；
             （UI 任务：确认 P3-test-cases.md 含 Playwright/E2E 用例描述）
       - P4: git diff --cached --name-only | grep -qvE '\.(md|yaml)$|^\.state'
       - P5: 从 P2-design.md gate_commands.P5 读取命令执行 → exit 0 AND failed==0;
             grep -rl '\[PROD_TOUCHED\]' {task}/ → 无命中（匹配标记格式，不匹配说明性文本）;
             （UI 任务：从 gate_commands.P5 读取 E2E 命令执行 → exit 0）
         - P6: scripts/check-gate.sh P6 → 脚本化部分通过（exit 2，FAIL=0/NC=0/证据非空已验，BDD 总数对照需主 Agent 手动核实）;
              grep -cE '^\s*- (PASS|FAIL)' {task}/P6-acceptance.md → =P1 BDD 总数（主 Agent 手动核实）;
              （UI 条件：vision-analyst YAML summary.blocker_count → =0）
       - P7: grep -cE '^\s*-?\s*\[BLOCKER\]' {task}/P7-consistency.md → =0;
             grep -cE '^\s*-?\s*\[DEVIATION-CRITICAL\]' {task}/P7-consistency.md → =0
        - P8: scripts/check-gate.sh P8 → 脚本化部分通过（exit 2）;
              从 P2-design.md gate_commands 逐包读取发布检查命令执行 → 全部 exit 0;
              从 P2-design.md gate_commands.P5 重跑 P5 命令 → exit 0 AND failed==0;
              git log v{prev_version}..HEAD --oneline 对照 CHANGELOG 条目 → 无遗漏;
              从 P2-design.md packages 验证 version 文件路径变更;
              grep -q 'bump_type:' {task}/P8-release.md → 命中;
               git diff --cached --stat → 含 version 文件变更;
               git diff --cached -- ${CHANGELOG_FILE:-CHANGELOG.md} → 非空
              （CHANGELOG 是项目根文件，默认 CHANGELOG.md；项目可用 CHANGELOG_FILE 环境变量覆盖路径）
    6. 计算下一状态（按转移规则）
       **回退跳变检测**（T019 教训：P5→P2 跨 3 阶段回退未 PAUSED）：
       若 current_phase_num - next_phase_num >= 2（回退 ≥2 阶段）
       → 强制 PAUSED，报告"跨 N 阶段回退，需人工确认"
       检测基于 phase 编号差值，不依赖 commit message 格式。
       例外：P5→P4（差 1，正常回归）不需要 PAUSED。
       注意：仅检查**回退**方向，不检查前向跨阶跳。前向跳（P2→P5）通常是裁剪后的合法跳变（state-machine.md:160-161），由 P5 gate 的阶段产出文件检查兜底。
    7. if 下一状态 == READY:
          输出交付小结（强制）：见「进入 READY 时」的格式要求
          再写回 .state.yaml
       else:
           写回 .state.yaml（新阶段 / 重试记录 / PAUSED）
    8. 返回：下一状态是什么
```

"一步"就是一次完整的派发 + 跑命令验证 + 状态更新。gate 判定由主 Agent 亲笔完成，不信任 subagent 产出的文件字段。

谁来反复调用？三种方式（见 loop-orchestration.md）：人工逐步、半自动、全自动 /loop。

---

## 重试上限

| 阶段 | MAX_RETRY | 说明 |
|------|-----------|------|
| P1 | 3 | 需求基线，涉及需求定义 |
| P2 | 3 | 涉及方案设计 |
| P3 | 2 | TDD 红灯，少轮次 |
| P4 | 3 | 实现复杂度高 |
| P5 | 2 | 技术验证，少轮次 |
| P6 | 2 | 验收，少轮次 |
| P7 | 2 | 一致性检查，少轮次 |
| P8 | 2 | 发布准备，少轮次 |

重试记录按阶段独立存储于 `.state.yaml` 的 `retries` 字段，不因进入新阶段而清零。

---

## 每任务独立状态文件

除 active-tasks.md 宏观看板外，每任务有独立状态文件：

位置：`docs/tasks/{Txxx}/.state.yaml`

```yaml
task_id: T001
phase: P4
status: in_progress

# ── 重试记录（T016 教训：整数计数无法区分"原样重试"和"调整策略后重试"）──
retries:
  P2:
    - round: 1
      failure_mode: quality           # quality=产出了但不够好 / empty_return=空返回 / timeout=超时
      prompt_changed: false           # 本次重试是否调整了 prompt
      adjustment: null                # 调整方式：split_task / add_navigation / switch_type / null
  P4: []                               # 空列表 = 该阶段无重试
  P5: []

retry_count: { P2: 1, P4: 0, P5: 0 }  # 派生字段 = len(retries[Pn])，向后兼容 active-tasks.md 看板

review_scores:
  P2:
    - round: 1
      reviewer: plan-eng-review
      score: 7.5
      status: rejected
      feedback: "API 限流策略未考虑并发边界"
updated: 2026-06-12

# 可选：运行时环境状态（P6 等需要运行环境的阶段记录）
env_state:
  debug_backend: "http://127.0.0.1:8888"
  test_entry_slug: "zg71s7"
  env_verified_at: "2026-06-26T03:25:00"
```

**字段说明**：
- `retries[Pn]`：列表，每次重试追加一条记录，`len(retries[Pn])` 即重试次数
- `retry_count`：派生字段，从 `retries` 计算，保留是为了 active-tasks.md 看板兼容
- `failure_mode`：失败模式（`quality` / `empty_return` / `timeout`），区分"产出了但不够好"和"根本没产出"
- `prompt_changed`：本次重试是否调整了 prompt，用于验证"空返回后必须改变策略"是否被遵守
- `adjustment`：具体调整方式（`split_task` / `add_navigation` / `switch_type` / `null`）

**commit 时机**：与 gate commit 同步——一次 commit 包含 stage output + `.state.yaml` 更新，避免文件与实际阶段不一致。

**active-tasks.md 降级为汇总视图**：不再由 subagent 直接修改，由主 Agent 维护。更新规则：**owner agent 只重写自己任务那一行**（从该任务 .state.yaml 派生），不碰其他任务的行，不做全表覆写。这样多 Agent 并发时各写各的行，冲突面最小。定期（或怀疑不一致时）可从所有 `.state.yaml` 全表重建作为对账。（与 git-integration.md 策略2 一致，.state.yaml 是唯一真相源）

---

## 为什么这样能抗中断

```
场景：主 Agent 在 P4 派发到一半，会话被压缩/中断

恢复时：
  0. 这是"重新接手任务"，等同于一次新的启动：
     依次重读 orchestrator-template.md「工作流规则」列出的 8 个协议文件
     （WORKFLOW.md / dispatch-protocol.md / state-machine.md / role-system.md /
      loop-orchestration.md / git-integration.md / platform-notes.md / LIMITATIONS.md）
     不能假设压缩前读过的内容还在上下文里。
  1. 主 Agent 重新读 active-tasks.md → "T001 在 P4，重试 0"
  2. 读 docs/tasks/T001/ → P4-implementation/ 是否已有文件？
     - 有 → P4 已完成，直接判定门槛，进 P5
     - 没有 → P4 没做完，重新派发 P4 subagent
  3. 接着干
```

状态完全由文件重建，不依赖会话记忆。这是"状态落盘"的核心价值。

**协议文件同样要重建，不止任务状态**：步骤 1-3 重建的是"任务进度"，但若压缩/中断丢失的是上下文里的协议规则本身（不是任务状态），单靠重读 active-tasks.md 不够——主 Agent 会"知道任务在 P4"，但可能已经不记得 P4 派发 prompt 该怎么写、gate 该怎么判。步骤 0 解决的是这一层：协议规则和任务状态是两类不同的东西，要分别确保能重建。

**`orchestrator-log.md` 防无响应**：主 Agent 在长操作前写 `NEXT: ...` 到 `orchestrator-log.md`，写下去就完成使命——不需要再读回来。恢复任务用 `.state.yaml` + 产出文件。

---

## 状态标记绑定规则（T019 教训）

.state.yaml 的 phase 字段标记为 Pn+1 前，必须满足：
1. Pn 的 gate 命令已执行（主 Agent 亲自跑）
2. Pn 的产出文件存在且含合法 Header
3. gate 结果已记录在 Pn 产出文件中

**违反判据**：.state.yaml 标记 Pn+1 但 Pn 产出文件不存在 → 无效标记，回退到 Pn 重新执行 gate。

**判定方式**：主 Agent 每轮开始时（单步函数步骤 1），检查 .state.yaml 的 phase 与产出文件是否匹配。不匹配 → 按标记前的阶段重新跑 gate。

T019 中 .state.yaml 标记 P5 但 P5-test-results/ 目录不存在——状态标记先于 gate 验证，中间窗口期状态不一致。本规则把"标记"和"验证"绑定，标记不能先于验证。

---

## 重试记录也要落盘

重试记录不能存在 LLM 记忆里（会忘）。**按阶段独立记录**，写进 `.state.yaml` 的 `retries` 字段（格式见上方「每任务独立状态文件」）：

```
每次某阶段门槛失败：
  retries[Pn].append({
    round: len(retries[Pn]) + 1,
    failure_mode: quality | empty_return | timeout,
    prompt_changed: true | false,
    adjustment: split_task | add_navigation | switch_type | null
  })
  → 写回 .state.yaml
```

**关键：不要"进入新阶段就把所有计数归零"。** 否则存在绕过上限的漏洞：

```
P2 retry 用到 2/3 → approved 进 P3 → 若简单归零
P3 发现 P2 设计有问题，回退到 P2 → retry 又从 0 开始 → P2 可被反复重试远超上限
```

按阶段独立记录后，P2 的历史重试记录累积保留，即使从 P3 回退到 P2，P2 的重试次数仍在，不会被绕过。

**T016 教训**：旧格式只有 `retry_count: { P3: 0 }` 一个整数，主 Agent 3 次空返回后 retry_count 仍为 0——既无法区分"原样重试"和"调整策略后重试"，也无法事后验证"空返回后是否改变了策略"。新格式的 `prompt_changed` 和 `adjustment` 字段解决这个盲区。

### 阶段回退规则

明确允许哪些回退，避免无限打转：

| 回退 | 是否允许 | 说明 |
|------|----------|------|
| P5 → P4 | ✅ 允许 | 测试失败回到实现，设计内的正常回归 |
| P2 → P2 | ✅ 允许 | 评审打回重做（同阶段重试）|
| P3/P6 → P2 | ⚠️ 谨慎 | 发现上游设计问题。允许，但 P2 的 retry 计数累积保留，且计入全局步数上限 |
| 跨多阶段回退 | ❌ 禁止自动 | 如 P6→P1，说明问题严重，停下 PAUSED 报告人工。检测方式：单步函数步骤 6 的 phase 编号差值检查（|next - current| >= 2 → PAUSED） |

全局步数上限（护栏 2，默认 20）是最后兜底，但按阶段独立计数 + 回退规则让它不必单独扛所有失控场景。

---

## 一致性要求

- .state.yaml 的 phase 字段和 active-tasks.md 的"阶段"列必须一致
- 如果两者冲突，以 **.state.yaml 为准**，修正 active-tasks.md
- 主 Agent 每轮开始先做这个一致性检查，避免状态漂移

---

## 评审迭代机制

### L1：阶段内再评审循环

```
阶段内循环：
  阶段执行者产出文件
       ↓
  主 Agent 跑 gate 命令（A1 原则）
       ↓
  通过？ ──是──→ 进入下一阶段
       ↓ 否
  派发评审角色读产出
       ↓
  评审角色产出 Pn-review.md (status: approved/rejected)
       ↓
  approved? ──是──→ 进入下一阶段
       ↓ 否
  retries[Pn].append({ failure_mode: quality, prompt_changed: <bool>, adjustment: <str> })
       ↓
  len(retries[Pn]) > MAX_RETRY?
       ↓ 是
  触发 L2 上溯（见下）
       ↓ 否
  执行者重写产出（带回评审反馈）
       ↓
  回到"主 Agent 跑 gate 命令"步骤
```

### L2：单规则跨阶段上溯

**确定性单规则**：任何阶段失败 MAX_RETRY 轮 → 上溯到紧邻的上游阶段，上游标记为 `needs-review`。

| 失败阶段 | 上溯到 | 动作 |
|----------|--------|------|
| P1 | 用户 | PAUSED，报告用户需求可能不合理 |
| P2 | P1 | P1 标记 needs-review，复审需求基线与 BDD |
| P3 | P2 | P2 标记 needs-review，architect 重新设计 |
| P4 | P2 | P2 标记 needs-review，质疑设计方案 |
| P5 | P4 | P4 标记 needs-review，重新实现 |
| P6 | P4 | P4 标记 needs-review，行为不符 → 重新实现（验收失败回实现）|
| P7 | P2 | P2 标记 needs-review，质疑设计（僵尸需求/偏差）|
| P8 | P7 | P7 标记 needs-review，重新检查一致性后再发布 |

**不区分原因、不判断分支**：主 Agent 只需确定 `len(retries[Pn]) > MAX_RETRY` → 执行固定上溯动作，无需推理多变量决策。

### 用户介入边界

| 情况 | 动作 |
|------|------|
| P1 失败 3 轮 | PAUSED，报告用户需求可能不合理 |
| 涉及业务方向决策 | PAUSED，询问"这个功能要不要做" |
| 涉及外部资源/权限 | PAUSED，需 API key / 授权 |
| P1 检测到 CAPABILITY_GAP | PAUSED，等人补充能力路径或确认降级方案 |
| 任意阶段出现 [PROD_TOUCHED] | 立即 PAUSED，人工处置生产环境后才能继续 |
| 涉及批量删除或 schema 迁移（测试环境内）| [NEED_CONFIRM] → PAUSED，确认范围后才可执行 |
| 涉及安全/合规 | PAUSED，需要人判断 |
| retry 超限且上溯仍失败 | PAUSED，兜底机制 |

PAUSED 报告使用占位符模板（见 dispatch-protocol.md）。

---

*状态机是 /loop 自动编排的基础，配合 dispatch-protocol.md 和 loop-orchestration.md*
