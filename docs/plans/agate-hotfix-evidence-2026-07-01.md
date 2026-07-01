---
task_id: agate-hotfix-evidence
agent: main
date: 2026-07-01
status: 设计文档（待评审）
来源: ~/oclab/peekview/docs/reviews/v0.5.1-regression-retrospective-20260701.md
---

# hotfix 协议 + evidence L3 + 诊断优先

## 背景

### v0.5.1 回归复盘教训

PeekView v0.5.1 上线后出现空行塌缩 bug。修复过程暴露 3 个 agate 盲区：

1. **hotfix 零流程**：5 轮修改全靠猜测，没跑诊断命令。如果有最小 gate 拦住第 1 轮，1 轮就能定位
2. **P6 evidence "读源码当证据"**：verifier 确认 `display:block` 写在源码里就判 PASS，没检查运行时渲染效果
3. **猜测→修改→猜测→修改的试错循环**：用户给了精确行号和截图，Agent 仍然先猜后测

### 与 t045-lessons R1 的关系

t045-lessons R1 已落地：`ui_affected: true` 时检查截图 >1KB + vision YAML `blocker_count=0`（客观证据存在性）。

本方案补的是 R1 未覆盖的一层：**evidence 类型检查**——确保 evidence 含运行时断言数据，不是"读源码当证据"。

---

## 1. hotfix 协议

### 1.1 触发条件

commit message 含 `wf(hotfix):` 前缀。

### 1.2 流程（5 步，不走 P0-P8）

```
1. 根因确认 → 跑诊断命令获取定量数据 → 写 P0-diagnosis.md
2. 修改 → 改动文件
3. 验证 → 重跑诊断命令（证明修复前失败、修复后通过）
4. 人确认效果
5. commit（wf(hotfix): ...）
```

### 1.3 P0-diagnosis.md 格式

放在 hotfix 任务目录 `docs/tasks/hotfix-{YYYYMMDD}/P0-diagnosis.md`：

```markdown
---
task_id: hotfix-{YYYYMMDD}
agent: main
phase: hotfix
---
## 诊断
- 命令：`document.querySelectorAll('.line').forEach(l => console.log(l.getBoundingClientRect().height))`
- 修复前输出：空行 h=0，非空行 h=25.6
- 根因：MarkdownViewer.vue 的 .line 规则缺 height:1.6em
- 改动文件：frontend-v3/src/components/MarkdownViewer.vue

## 验证
- 修复后输出：空行 h=25.6，与非空行一致
- 测试：npm run test → 全过
```

**关键字段**：
- `命令`：实际跑的诊断命令（不是"我看了源码"）
- `修复前输出`：证明问题可复现
- `修复后输出`：证明修复有效
- `根因`：基于诊断数据的结论，不是猜测
- `改动文件`：声明的改动范围

### 1.4 check-hotfix.sh 检查项

| # | 检查 | 条件 | 失败动作 |
|---|------|------|---------|
| 1 | P0-diagnosis.md 存在 | commit message 含 `wf(hotfix)` | 拦截 |
| 2 | 含诊断命令行 | grep `^- 命令：` 或 ``^- 命令:` `` | 拦截 |
| 3 | 含修复前输出 | grep `修复前` | 拦截 |
| 4 | 含修复后输出 | grep `修复后` | 拦截 |

**不检查的**：
- 改动文件数 — hotfix 定义上就是小范围，不需要硬阈值
- P5-test-results/ — 命名混淆（P5 是 agate 阶段名），诊断验证已在 P0-diagnosis.md 里
- CHANGELOG — hotfix commit message 本身就是变更记录
- .state.yaml — hotfix 不走状态机，加状态文件增摩擦

### 1.5 hook 机制

**问题**：pre-commit hook 运行时看不到 commit message（message 在 hook 之后输入）。

**方案**：加装 `commit-msg` hook。

- `install-hook.sh` 扩展：同时装 pre-commit + commit-msg
- `commit-msg-gate.sh`（新脚本）：读 commit message（参数 `$1` = message 文件路径），含 `wf(hotfix):` 时跑 `check-hotfix.sh`
- 两个 hook 互不干扰：
  - pre-commit hook：检测 `.state.yaml` phase 变更 → 跑常规 gate（hotfix 不动 .state.yaml，不会触发）
  - commit-msg hook：检测 `wf(hotfix):` → 跑 hotfix 检查

**commit-msg-gate.sh 逻辑**：

```bash
#!/usr/bin/env bash
set -euo pipefail
MSG_FILE="$1"
MSG=$(cat "$MSG_FILE")

# 只检查 wf(hotfix): 前缀的 commit
if ! echo "$MSG" | grep -qE '^wf\(hotfix\):'; then
    exit 0
fi

AGATE_ROOT="${AGATE_ROOT:-$HOME/.agate}"
REPO_ROOT=$(git rev-parse --show-toplevel)

# 找 hotfix 任务目录（docs/tasks/hotfix-*/）
HOTFIX_DIR=$(find "$REPO_ROOT/docs/tasks" -maxdepth 1 -type d -name 'hotfix-*' 2>/dev/null | sort -r | head -1)

if [ -z "$HOTFIX_DIR" ]; then
    echo "GATE HOTFIX: 未找到 hotfix 任务目录（docs/tasks/hotfix-*/）" >&2
    exit 1
fi

bash "$AGATE_ROOT/scripts/check-hotfix.sh" "$HOTFIX_DIR"
```

### 1.6 install-hook.sh 扩展

```bash
# 现有：装 pre-commit hook
ln -sf "$SOURCE_PRECOMMIT" "$HOOK_DIR/pre-commit"

# 新增：装 commit-msg hook
ln -sf "$SOURCE_COMMITMSG" "$HOOK_DIR/commit-msg"
```

幂等性：`ln -sf` 覆盖旧链接，重复执行安全。

### 1.7 与 P2.14"直接做"的关系

| 场景 | 流程 | 要求 |
|------|------|------|
| 微改动/低风险 | 直接做（P2.14）| commit message 声明改了什么 + 为什么安全 |
| 线上问题/回归 | hotfix 协议 | P0-diagnosis.md + 诊断命令验证 |
| 复杂任务 | 完整 P0-P8 | 全流程 |

互斥：线上问题不能"直接做"，必须走 hotfix 流程。

### 1.8 文档位置

`WORKFLOW.md` 风险矩阵后新增"hotfix 协议"节。

---

## 2. evidence L3 检查

### 2.1 现状

`check-p6-evidence.sh` 已检查：
- P6-evidence/ 目录非空
- 每条 PASS 行含文件引用（.png/.jpg/.log/.json/.html/.txt/.yaml/.yml）
- `ui_affected: true` 时截图 >1KB（R1a）
- `ui_affected: true` 时 vision YAML `blocker_count=0`（R1b，在 check-p6-provenance.sh）

**盲区**：evidence 文件内容不检查。subagent 可以写一个 `.txt` 文件，内容是"源码第 369 行有 display:block"——形式合规，实质是"读源码当证据"。

### 2.2 改动

`check-p6-evidence.sh` 扩展，`ui_affected: true` 时增加 L3 检查：

**检查逻辑**：P6-evidence/ 下至少 1 个文件含运行时断言关键词。

**运行时断言关键词**（任一匹配即可）：
- `getComputedStyle` — CSS 计算值
- `getBoundingClientRect` — 元素几何尺寸
- `page.evaluate` — Playwright 运行时求值
- `screenshot` / `screenshots` — 截图
- `vision-reports` / `blocker_count` — vision-analyst YAML

**为什么用关键词检查而非目录约定**：
- 不强制 `runtime/` 子目录 — 向后兼容现有任务
- 关键词检查覆盖文件内容 — 比"目录存在"更精确
- 与 R1 的截图 >1KB 叠加 — subagent 必须同时有截图文件 + 截图 >1KB + evidence 含运行时关键词

**检查位置**：在现有 `ui_affected: true` 分支内（check-p6-evidence.sh:63-85），截图检查之后。

```bash
# L3 检查：evidence 文件含运行时断言关键词
L3_HIT=0
while IFS= read -r -d '' evfile; do
    if grep -qE 'getComputedStyle|getBoundingClientRect|page\.evaluate|screenshot|vision-reports|blocker_count' "$evfile" 2>/dev/null; then
        L3_HIT=1
        break
    fi
done < <(find "$EVIDENCE_DIR" -type f -not -name '.*' -print0 2>/dev/null)

if [ "$L3_HIT" -eq 0 ]; then
    echo "GATE P6-EVIDENCE: ui_affected=true 但 evidence 无运行时断言（需含 getComputedStyle / getBoundingClientRect / screenshot / vision-reports 之一，源码引用不算）" >&2
    exit 1
fi
```

### 2.3 三重检查的伪造成本

subagent 要伪造 P6 evidence（`ui_affected: true`）需同时：
1. P6-evidence/screenshots/ 有截图文件（R1a）
2. 截图文件 >1KB（R1a）
3. P6-evidence/ 下有文件含运行时断言关键词（L3）
4. vision YAML `blocker_count=0`（R1b）
5. PASS 数 ≤ 证据数 + BDD 总数对照（provenance 审计）

单层伪造易，五层叠加难——这是"客观证据 barrier"的设计意图（t045-lessons 第 5 节"两类防线的分野"）。

### 2.4 文档位置

`dispatch-protocol.md` P6 派发模板补一句：`ui_affected: true` 时 evidence 必须含运行时断言数据，源码引用不算通过。

---

## 3. 诊断优先规则

### 3.1 软规则（文档）

`dispatch-protocol.md` 铁律区新增：

```
收到外部 bug 反馈（用户报告 / SCOPE+ / 视觉验证异常）→ 
  第一步：跑诊断命令获取定量数据
  第二步：根据诊断数据定位根因
  第三步：修改
禁止 猜测→修改→猜测→修改 的试错循环。
```

### 3.2 hook 提醒（retries 触发）

`check-retrospective.sh` 已读 `.state.yaml` 的 retries 字段做异常模式检测。扩展：

`retries[Pn] >= 2` 时输出诊断提醒：
```
GATE RETROSPECTIVE: 警告 — P{n} 重试 {N} 次，建议跑诊断命令确认根因，而非继续试错
```

这是 WARNING 不阻塞 commit，和现有复盘提醒机制一致（P2.12）。

**为什么用 retries 而非"改了几轮"**：
- retries 是 `.state.yaml` 里的客观计数，hook 可读
- "改了几轮"是上下文行为，hook 不可观测
- retries >= 2 是试错循环的代理指标——正常 1 次通过，重试 2+ 次说明没定位根因

### 3.3 文档位置

- 软规则：`dispatch-protocol.md` 铁律区
- hook 提醒：`check-retrospective.sh` 扩展

---

## 4. 改动汇总

### 4.1 新增脚本

| 脚本 | 作用 |
|------|------|
| `scripts/check-hotfix.sh` | hotfix 检查（4 项）|
| `scripts/commit-msg-gate.sh` | commit-msg hook 入口，检测 `wf(hotfix):` 调用 check-hotfix.sh |

### 4.2 扩展脚本

| 脚本 | 改动 |
|------|------|
| `scripts/install-hook.sh` | 加装 commit-msg hook（`ln -sf` 到 `.git/hooks/commit-msg`）|
| `scripts/check-p6-evidence.sh` | `ui_affected: true` 时增加 L3 运行时断言关键词检查 |
| `scripts/check-retrospective.sh` | `retries >= 2` 时输出诊断提醒 WARNING |

### 4.3 文档改动

| 文件 | 改动 |
|------|------|
| `WORKFLOW.md` | 风险矩阵后加"hotfix 协议"节 |
| `dispatch-protocol.md` | ① P6 派发模板补 evidence L3 要求 ② 铁律区加"诊断优先" |
| `git-integration.md` | commit message 规范加 `wf(hotfix):` 前缀说明 |
| `orchestrator-template.md` | Hardening 节补 hotfix 流程 + commit-msg hook 说明 |

### 4.4 不改的

| 不改 | 理由 |
|------|------|
| pre-commit-gate.sh | hotfix 不动 .state.yaml，pre-commit hook 不会触发，无需改 |
| .state.yaml 格式 | hotfix 不走状态机 |
| task-files.md | hotfix 产出文件只有 P0-diagnosis.md，不在标准阶段产出列表里 |

---

## 5. 测试计划

### 5.1 新增测试

**`tests/unit/check-hotfix.bats`**：

| # | 用例 | 预期 |
|---|------|------|
| 1 | `wf(hotfix)` + 无 P0-diagnosis.md | 拦截 |
| 2 | `wf(hotfix)` + P0-diagnosis.md 无"命令"行 | 拦截 |
| 3 | `wf(hotfix)` + P0-diagnosis.md 无"修复前" | 拦截 |
| 4 | `wf(hotfix)` + P0-diagnosis.md 无"修复后" | 拦截 |
| 5 | `wf(hotfix)` + 全满足 | 通过 |
| 6 | 非 hotfix commit | 跳过（exit 0）|
| 7 | 无 hotfix 任务目录 | 拦截 |

**`tests/unit/check-p6-evidence-l3.bats`**（或扩展现有 check-p6-evidence.bats）：

| # | 用例 | 预期 |
|---|------|------|
| 1 | `ui_affected: true` + evidence 全是源码引用文本 | 拦截 |
| 2 | `ui_affected: true` + evidence 含 getComputedStyle | 通过 |
| 3 | `ui_affected: true` + evidence 含 screenshot | 通过 |
| 4 | `ui_affected: true` + evidence 含 vision-reports | 通过 |
| 5 | `ui_affected: false` | 跳过 L3 检查 |

**`tests/unit/check-retrospective-diagnosis.bats`**（或扩展现有）：

| # | 用例 | 预期 |
|---|------|------|
| 1 | `retries[P4] = 2` | 输出诊断提醒 WARNING，exit 0 |
| 2 | `retries[P4] = 1` | 无诊断提醒 |
| 3 | `retries[P4] = 3` | 输出诊断提醒 + 复盘提醒 |

**`tests/regression/v0.5.1-hotfix.bats`**：

端到端：模拟 v0.5.1 回归场景
- 空诊断 commit `wf(hotfix):` → 拦截
- 有诊断无修复后输出 → 拦截
- 完整 P0-diagnosis.md → 通过

**`tests/integration/commit-msg-hook.bats`**：

- install-hook.sh 装 commit-msg hook
- `wf(hotfix):` commit 触发 check-hotfix.sh
- 普通 commit 不触发

### 5.2 测试用例计数

新增约 15 个用例（7 + 5 + 3 + 3 - 3 重叠 = 约 15）。

154 → 约 169。

---

## 6. 不做的事

| 不做 | 理由 |
|------|------|
| hotfix 加 .state.yaml | hotfix 价值在于快，状态文件增摩擦 |
| hotfix 派发 subagent | hotfix 通常主 Agent 直接修 |
| 改动文件数硬阈值 | hotfix 定义上就是小范围，阈值武断 |
| evidence 目录结构约定（runtime/ vs static/）| 向后兼容问题，关键词检查更精确 |
| evidence 三级分级（L1/L2/L3）| 只需区分"运行时 vs 非运行时"，三级过度设计 |
| P5 跨文件样式一致性检查 | 项目特定不可泛化（复盘建议 4 否决）|
| 试错循环 hook 硬拦截 | 不可行——retries 是代理指标，硬拦截误杀合理重试 |

---

## 7. 实现顺序

1. `check-hotfix.sh` + `commit-msg-gate.sh` + 单元测试
2. `install-hook.sh` 扩展 + 集成测试
3. `check-p6-evidence.sh` L3 扩展 + 单元测试
4. `check-retrospective.sh` 诊断提醒扩展 + 单元测试
5. 文档改动（WORKFLOW.md / dispatch-protocol.md / git-integration.md / orchestrator-template.md）
6. 回归测试 v0.5.1-hotfix.bats
7. 全量测试 + consistency check + shellcheck
8. 版本号 v0.8.0
