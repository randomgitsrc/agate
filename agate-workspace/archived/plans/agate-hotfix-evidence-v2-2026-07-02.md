---
task_id: agate-hotfix-evidence-v2
agent: main
date: 2026-07-02
status: 优化方案（待评审）
来源: docs/plans/agate-hotfix-evidence-2026-07-01.md（v1）+ agate 已有机制对照
---

# hotfix-evidence 优化方案

## v1 → v2 变更依据

v1 计划基于 PeekView v0.5.1 复盘，掺杂项目特定信息。v2 逐项对照 agate 已有机制，去掉重复、通用化设计。

## 逐项分析

### 1. hotfix 协议

#### agate 已有的

| 机制 | 覆盖 |
|------|------|
| P2.14"直接做" | 微改动/低风险快速通道：commit message 声明改了什么 + 为什么安全 |
| WORKFLOW.md 风险矩阵 | 微改动→直接做，小改动→裁剪 agate，中改动→完整 P1-P8 |
| P0-P8 完整流程 | 已有 |

#### agate 缺的

**"直接做"和"完整 agate"之间缺一个中间档**——回归 bug 修复需要比"直接做"更严谨（要有诊断证据），但比"完整 P0-P8"更轻量（不走状态机）。

#### v2 设计

**保留 hotfix 协议，但通用化**：

| v1（PeekView 特有） | v2（通用） |
|---------------------|------------|
| P0-diagnosis.md 用中文关键词（"命令："/"修复前"/"修复后"） | 用 YAML frontmatter 结构化字段（`diagnosis_command` / `before` / `after`） |
| 诊断命令例子是 `document.querySelectorAll` | 不给具体例子，只给字段定义 |
| "线上问题不能直接做" | "回归 bug / 外部反馈不能直接做"（不绑定"线上"概念） |
| `wf(hotfix):` commit-msg hook | 保留——hook 机制通用 |

**P0-diagnosis.md 格式**：

```markdown
---
task_id: hotfix-{YYYYMMDD}
agent: main
phase: hotfix
---
## 诊断
diagnosis_command: <实际跑的诊断命令>
before: <修复前输出，证明问题可复现>
after: <修复后输出，证明修复有效>
root_cause: <基于诊断数据的根因，不是猜测>
files_changed: <改动文件列表>
```

check-hotfix.sh 检查 frontmatter 字段存在性，不检查中文关键词。

**与 P2.14 的关系**（保留 v1 设计，措辞通用化）：

| 场景 | 流程 | 要求 |
|------|------|------|
| 微改动/低风险 | 直接做（P2.14）| commit message 声明改了什么 + 为什么安全 |
| 回归 bug / 外部反馈 | hotfix 协议 | P0-diagnosis.md + 诊断命令验证 |
| 复杂任务 | 完整 P0-P8 | 全流程 |

#### 不改的

- commit-msg hook 机制（通用）
- 不走 .state.yaml（hotfix 价值在于轻量）
- 不走 P0-P8

---

### 2. evidence L3 检查

#### agate 已有的

| 机制 | 覆盖 | 位置 |
|------|------|------|
| PASS 必须有文件引用 | ✅ 证据存在性 | check-p6-evidence.sh:30-40 |
| 截图 >1KB | ✅ 防空 png 充数 | check-p6-evidence.sh:73-83 (R1a) |
| md5 去重 | ✅ 防复制截图 | check-p6-evidence.sh:85-92 |
| vision YAML blocker_count=0 | ✅ 视觉验证 | check-p6-provenance.sh (R1b) |
| verifier.md:64 "实跑不是看代码" | ✅ 软规则 | 角色文件 |

#### agate 缺的

**"读源码当证据"的盲区仍然存在**——verifier.md:64 说了"实跑不是看代码"，但 check-p6-evidence.sh 只检查文件引用存在性 + 截图大小，不检查文件内容是不是"运行时数据 vs 源码引用文本"。

#### v1 的问题

v1 的关键词列表（`getComputedStyle` / `getBoundingClientRect` / `page.evaluate` / `screenshot` / `vision-reports` / `blocker_count`）全是前端/Playwright 特有。后端项目的运行时断言是 `pytest` 输出、`curl` 响应、`assert` 语句——硬编码这些关键词会误拦后端项目。

#### v2 设计

**不硬编码技术栈关键词，改为通用约束**：

`ui_affected: true` 时，P6-evidence/ 下不能全是 `.md` / `.txt` 纯文本文件——至少有一个结构化数据文件（`.json` / `.yaml` / `.yml` / `.log` / `.png` / `.jpg` / `.html`）。

理由：
- "读源码当证据"的文件通常是 `.txt` / `.md`（手写描述"源码第 X 行有 Y"）
- 运行时断言的产出天然是 `.json`（API 响应）、`.log`（测试输出）、`.png`（截图）、`.yaml`（vision 报告）
- 这个约束不绑定任何技术栈，后端前端都适用

**检查逻辑**（check-p6-evidence.sh 扩展，`ui_affected: true` 分支内）：

```bash
# L3 检查：evidence 不能全是纯文本描述
NON_TEXT_COUNT=$(find "$EVIDENCE_DIR" -type f -not -name '.*' \
    ! -name '*.md' ! -name '*.txt' 2>/dev/null | wc -l)
if [ "$NON_TEXT_COUNT" -eq 0 ]; then
    echo "GATE P6-EVIDENCE: ui_affected=true 但 evidence 全是纯文本文件（.md/.txt），缺少运行时数据（.json/.log/.png/.yaml 等）" >&2
    exit 1
fi
```

**已有的 PASS 文件引用检查（L30-40）已经要求 `.png/.jpg/.log/.json/.html/.txt/.yaml/.yml` 后缀**——L3 只是在此基础上加"不能全是 .md/.txt"。

#### 不改的

- R1a 截图 >1KB（已有）
- md5 去重（已有）
- R1b vision YAML（已有）
- PASS 文件引用检查（已有）

---

### 3. 诊断优先规则

#### agate 已有的

| 机制 | 覆盖 |
|------|------|
| check-retrospective.sh | retries 超限时提醒"建议复盘" |
| check-state-transition.sh | retries 超限 → PAUSED |
| dispatch-protocol.md 空返回诊断 | 空返回后分析根因 |

#### agate 缺的

**retries >= 2（未超限但已重试）时没有"诊断优先"提醒**。当前 check-retrospective.sh 只在超限时提醒"建议复盘"，不提醒"建议跑诊断命令"。

#### v2 设计

**完全保留 v1 设计——这部分本来就通用**：

1. **软规则**（dispatch-protocol.md 铁律区新增）：
```
收到外部 bug 反馈（用户报告 / SCOPE+ / 视觉验证异常）→ 
  第一步：跑诊断命令获取定量数据
  第二步：根据诊断数据定位根因
  第三步：修改
禁止 猜测→修改→猜测→修改 的试错循环。
```

2. **hook 提醒**（check-retrospective.sh 扩展）：

`retries[Pn] >= 2`（按阶段差异化 MAX 判断未超限但已重试）时输出：
```
GATE RETRO: P{n} 重试 {N} 次——建议跑诊断命令确认根因，而非继续试错
```

WARNING 不阻塞，和现有复盘提醒一致。

**与已有的区别**：
- 现有：retries 超限 → "建议复盘"（事后总结）
- 新增：retries >= 2 未超限 → "建议跑诊断命令"（事中干预）

两者不冲突——超限时两个提醒都输出。

#### 不改的

- check-retrospective.sh 现有超限提醒逻辑
- check-state-transition.sh 重试上限

---

## 改动汇总

### 新增脚本

| 脚本 | 作用 |
|------|------|
| `scripts/check-hotfix.sh` | hotfix 检查（P0-diagnosis.md frontmatter 字段存在性） |
| `scripts/commit-msg-gate.sh` | commit-msg hook 入口，检测 `wf(hotfix):` 调用 check-hotfix.sh |

### 扩展脚本

| 脚本 | 改动 |
|------|------|
| `scripts/install-hook.sh` | 加装 commit-msg hook |
| `scripts/check-p6-evidence.sh` | `ui_affected: true` 时增加 L3：evidence 不能全是 .md/.txt |
| `scripts/check-retrospective.sh` | `retries >= 2` 未超限时输出诊断提醒 |

### 文档改动

| 文件 | 改动 |
|------|------|
| `WORKFLOW.md` | 风险矩阵后加"hotfix 协议"节 |
| `dispatch-protocol.md` | ① P6 派发模板补 evidence L3 要求 ② 铁律区加"诊断优先" |
| `git-integration.md` | commit message 规范加 `wf(hotfix):` 前缀 |
| `orchestrator-template.md` | Hardening 节补 hotfix 流程 |

### 测试

| 文件 | 用例数 |
|------|--------|
| `tests/unit/check-hotfix.bats` | 7（frontmatter 字段缺失/完整/非 hotfix commit） |
| `tests/unit/check-p6-evidence.bats` 扩展 | 3（全 .txt 拦截 / 有 .json 通过 / ui_affected=false 跳过） |
| `tests/unit/check-retrospective.bats` 扩展 | 2（retries=2 提醒 / retries=1 不提醒） |
| `tests/integration/commit-msg-hook.bats` | 3（hotfix commit 触发 / 普通 commit 不触发 / install-hook 幂等） |

## 实现顺序

1. check-hotfix.sh + commit-msg-gate.sh + 单元测试
2. install-hook.sh 扩展 + 集成测试
3. check-p6-evidence.sh L3 扩展 + 单元测试
4. check-retrospective.sh 诊断提醒 + 单元测试
5. 文档改动
6. 全量测试 + consistency + shellcheck + self-gate
