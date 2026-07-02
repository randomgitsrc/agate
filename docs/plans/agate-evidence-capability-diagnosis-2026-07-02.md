---
task_id: agate-evidence-capability-diagnosis
agent: main
date: 2026-07-02
status: 设计文档（待评审）
来源: docs/archived/plans/agate-hotfix-evidence-2026-07-01.md 重新审视 + 用户实际使用场景反馈
---

# evidence 类型检查 + 能力使用提醒 + 诊断优先

## 问题全貌

agent 在 P5/P6 验证阶段遇到工具/能力/环境限制时，不是标 `[NEED_CONFIRM]` 或 `[CAPABILITY_GAP]` 交人判断，而是自行降级到"读代码推断"→ 判 PASS。具体表现：

| 场景 | agent 做了什么 | 根因 |
|------|---------------|------|
| UI 显示 bug | 随便截个图 → 看不到问题 → 回退源码分析 | 不会用 Playwright 导航/交互 |
| 需要视觉判断（颜色/布局） | 文本模型不提 vision-analyst → 目测代码 → 判 PASS | 忘了/不知道要派 vision subagent |
| 需要 E2E 测试 | 不会写 Playwright 脚本 → 写个 .txt 说"代码看起来对" | 工具能力不足 |
| 需要 API 验证 | 不会用 curl/httpie → 读代码说"逻辑应该对" | 工具能力不足 |
| 需要桌面软件验证 | agent 没有桌面交互能力 → 读代码判 PASS | 环境能力缺口 |
| 测试跑不通 | 不分析原因 → 换个测法/注释掉 → "绿了" | 诊断能力不足 |

**共同模式**：agent 遇到能力/工具/环境限制 → 不标 `[NEED_CONFIRM]` / `[CAPABILITY_GAP]` → 自行降级到"读代码推断" → 判 PASS。

## agate 已有机制

| 机制 | 覆盖 | 缺口 |
|------|------|------|
| P0-brief `executor_env`（platform/has_task_tool/has_local_runtime/network） | 声明环境能力 | agent 不主动检查就忘了 |
| P1 `capability_requirements`（available/supplementable/GAP） | 声明能力需求 | P1 声明了但 P5/P6 agent 忘了用 |
| `[CAPABILITY_GAP]` 标记 | 能力缺失时 PAUSED | agent 不标就没人知道 |
| verifier.md:64 "实跑不是看代码" | 软规则 | 没说"遇到工具困难时怎么办" |
| `[NEED_CONFIRM]` | 拿不准时交人 | agent 不标就没人知道 |
| check-p6-evidence.sh PASS 文件引用 | 证据文件存在性 | 不检查文件内容是"运行时数据"还是"源码分析" |
| R1a 截图 >1KB / md5 去重 | 防空 png / 防复制截图 | 不防"纯文本源码分析充数" |

**核心缺口**：agate 有声明机制（P0/P1 声明能力），有降级标记（`[CAPABILITY_GAP]` / `[NEED_CONFIRM]`），但缺执行时的强制检查——agent 在 P5/P6 实际跑验证时，没人提醒它"你声明的能力用了吗？遇到困难标 NEED_CONFIRM 了吗？"

## 设计

### 1. gate 层：evidence L3 检查（硬约束）

#### 修改文件

`agate/scripts/check-p6-evidence.sh`

#### 逻辑

`ui_affected: true` 时，P6-evidence/ 下不能全是 `.md` / `.txt` 纯文本文件——至少有一个结构化数据文件（`.json` / `.yaml` / `.yml` / `.log` / `.png` / `.jpg` / `.html`）。

```bash
# L3 检查：evidence 不能全是纯文本描述
# 纯文本（.md/.txt）是手写源码分析的典型载体
# 运行时工具产出天然是结构化格式（.json/.log/.png/.yaml）
NON_TEXT_COUNT=$(find "$EVIDENCE_DIR" -type f -not -name '.*' \
    ! -name '*.md' ! -name '*.txt' 2>/dev/null | wc -l)
if [ "$NON_TEXT_COUNT" -eq 0 ]; then
    echo "GATE P6-EVIDENCE: ui_affected=true 但 evidence 全是纯文本（.md/.txt），缺少运行时数据（.json/.log/.png/.yaml 等）。源码引用不算运行时证据。" >&2
    exit 1
fi
```

放在现有 R1a 截图检查之后、md5 去重之后。

#### 为什么用文件类型不用关键词

- 不绑定技术栈——后端（pytest .log）、前端（screenshot .png）、API（response .json）都适用
- 纯文本（.md/.txt）是"手写描述"的典型载体
- 已有的 PASS 文件引用检查（L30-40）已要求 `.png/.jpg/.log/.json/.html/.txt/.yaml/.yml`——L3 只在此基础上加"不能全是 .md/.txt"

#### 诚实声明

L3 只堵"纯文本源码分析"，堵不住"错误截图 + 源码分析混搭"。后者需要主 Agent 人工审查截图内容——gate 查不了截图语义。

### 2. 派发层：P5/P6 派发 prompt 加能力检查提醒

#### 修改文件

`agate/assets/templates/dispatch-prompt.md` P5/P6 派发追加节

#### 逻辑

在现有 P5/P6 派发追加节开头加能力检查提醒：

```markdown
## 能力使用检查（P5/P6 必读）
1. 读 P1-requirements.md 的 capability_requirements 字段——这些能力你都用了吗？
2. 读 P0-brief.md 的 executor_env——你的环境支持什么？不支持什么？
3. 遇到无法用工具完成的验证（导航复杂/交互困难/需要视觉判断）：
   - 不要回退源码分析——"源码看起来对"不等于"运行时正常"
   - 标 [NEED_CONFIRM] 交人判断
   - 在 P6-acceptance.md 记录你尝试了什么、为什么没成功
4. 需要视觉判断的 BDD（颜色/布局/显示效果）→ 必须派 vision-analyst，不能目测代码
5. "工具返回看不到问题"≠"没有问题"——可能是工具使用方式错了（没导航到正确页面/没触发交互）
```

同步到 `agate/dispatch-protocol.md` P5/P6 派发追加节。

### 3. 角色层：verifier.md 补工具困难处理

#### 修改文件

`agate/assets/execution-roles/verifier.md`

#### 逻辑

在"认知模式"节之后、"行为验证证据优先级"节之前，新增：

```markdown
### 工具困难时的处理（不能回退源码）

遇到无法用工具到达目标页面/状态时（导航复杂、需滚动/交互、桌面软件等）：

1. **不要回退源码分析**——"源码看起来对"不等于"运行时正常"
2. **记录尝试**——在 P6-acceptance.md 写明尝试了什么导航步骤、为什么没到达
3. **标 [NEED_CONFIRM]**——交人判断，不自行判 PASS
4. **能力对账**——对照 P1 capability_requirements，声明的能力都用了吗？没用的为什么没用？

常见误判：
- "工具返回看不到问题"≠"没有问题"——可能是工具使用方式错了（没导航到正确页面/没触发交互）
- "模型不支持图片"≠"可以跳过视觉验证"——要派 vision-analyst subagent
- "Playwright 脚本跑不通"≠"功能没问题"——要分析脚本失败原因或标 NEED_CONFIRM
```

### 4. hook 层：诊断优先提醒

#### 修改文件

`agate/scripts/check-retrospective.sh`

#### 逻辑

现有：retries 超限时提醒"建议复盘"（事后总结）。

新增：retries[Pn] >= 2 且未超限时输出诊断提醒（事中干预）。

```python
# 现有逻辑：超限时 print(f'{phase}={len(attempts)} (MAX={phase_max})')
# 新增逻辑：>= 2 且 < MAX 时 print(f'{phase}={len(attempts)} (建议诊断)')
```

输出格式：
```
GATE RETRO: P{n} 重试 {N} 次——建议跑诊断命令确认根因，而非继续试错
```

WARNING 不阻塞，和现有复盘提醒一致。超限时两个提醒都输出。

#### 与已有的区别

| 触发条件 | 输出 | 性质 |
|----------|------|------|
| retries >= MAX（现有） | "建议复盘" | 事后总结 |
| retries >= 2 且 < MAX（新增） | "建议跑诊断命令" | 事中干预 |

## 不做的事

| 不做 | 理由 |
|------|------|
| hotfix 协议 | 触发靠 agent 自觉写 commit message，和 P2.14 一样是自觉型机制，无法自动判断 |
| check-hotfix.sh / commit-msg-gate.sh | hotfix 砍掉，不需要 |
| evidence 关键词检查 | 硬编码技术栈关键词（getComputedStyle 等）不通用 |
| 截图内容语义检查 | gate 查不了截图语义，需要主 Agent 人工审查 |
| 强制 capability_requirements 对账 gate | P1 声明的能力和 P6 使用的能力之间无法自动匹配（能力名不标准化） |

## 变更文件清单

| 文件 | 改动 |
|------|------|
| `agate/scripts/check-p6-evidence.sh` | ui_affected=true 时增加 L3：evidence 不能全是 .md/.txt |
| `agate/scripts/check-retrospective.sh` | retries >= 2 未超限时输出诊断提醒 |
| `agate/assets/templates/dispatch-prompt.md` | P5/P6 派发追加节加能力检查提醒 |
| `agate/dispatch-protocol.md` | P5/P6 派发追加节同步 |
| `agate/assets/execution-roles/verifier.md` | 补"工具困难时的处理"规则 |
| `CHANGELOG.md` | 标注变更 |

## 测试计划

### check-p6-evidence.bats 扩展

| ID | 描述 | 期望 |
|----|------|------|
| E.14 | ui_affected=true + evidence 全是 .txt | exit 1，含"纯文本" |
| E.15 | ui_affected=true + evidence 有 .txt + .json | exit 0 |
| E.16 | ui_affected=true + evidence 有 .txt + .png | exit 0 |
| E.17 | ui_affected=false + evidence 全是 .txt | exit 0（跳过 L3） |

### check-retrospective.bats 扩展

| ID | 描述 | 期望 |
|----|------|------|
| RT.7 | retries[P4]=2（MAX=3，未超限） | exit 0 + 含"诊断"提醒 |
| RT.8 | retries[P4]=1（未重试） | exit 0 + 无"诊断"提醒 |
| RT.9 | retries[P3]=2（MAX=2，超限） | exit 0 + 含"复盘"+ 含"诊断" |

## 实现顺序

1. check-p6-evidence.sh L3 扩展 + 单元测试
2. check-retrospective.sh 诊断提醒 + 单元测试
3. verifier.md 角色强化
4. dispatch-prompt.md + dispatch-protocol.md P5/P6 能力检查提醒
5. 全量测试 + consistency + shellcheck + self-gate
