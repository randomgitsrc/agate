---
task_id: agate-evidence-diagnosis-v2
agent: main
date: 2026-07-02
status: 优化方案 v2（待评审）
来源: docs/plans/agate-hotfix-evidence-2026-07-01.md 重新审视 + 用户实际使用场景
---

# evidence 类型检查 + 诊断优先提醒

## 砍掉的部分

### hotfix 协议——不做

**理由**：hotfix 的触发靠 agent 自觉写 `wf(hotfix):` commit message，和 P2.14"直接做"一样是自觉型机制。无法自动判断"什么时候该走 hotfix"。已有 P2.14（微改动）+ 完整 P0-P8（复杂任务）两档够用。新增第三档增加复杂度但无法自动触发。

不新增 check-hotfix.sh / commit-msg-gate.sh / install-hook 扩展。

---

## 保留的部分

### 1. evidence 类型检查（gate 层硬约束）

#### 问题场景

agent 验证 UI 显示问题时，正确做法是用 Playwright 导航到目标页面、交互、截图。但 agent 可能：

1. 不会正确使用工具（导航/滚动/交互复杂）→ 随便截个图
2. 截图看不到问题 → 认为"人判断错了"
3. 回退到读源码 → "源码第 369 行有 display:block"→ 写成 .txt 当证据
4. 用源码引用提交 PASS

#### gate 能堵的

只能堵第 3 步的最终产出——evidence 全是纯文本描述（.md/.txt），没有运行时数据文件。

**堵不住的**（诚实声明）：agent 截了错误页面的 .png（>1KB、md5 唯一），gate 抓不到。这需要主 Agent 人工审查截图内容是否对应 BDD 描述的场景。

#### 设计

check-p6-evidence.sh 扩展，`ui_affected: true` 时：

```bash
# evidence 不能全是纯文本描述（.md/.txt）
# 运行时断言的产出天然是 .json/.log/.png/.yaml——纯文本通常是手写源码分析
NON_TEXT_COUNT=$(find "$EVIDENCE_DIR" -type f -not -name '.*' \
    ! -name '*.md' ! -name '*.txt' 2>/dev/null | wc -l)
if [ "$NON_TEXT_COUNT" -eq 0 ]; then
    echo "GATE P6-EVIDENCE: ui_affected=true 但 evidence 全是纯文本（.md/.txt），缺少运行时数据（.json/.log/.png/.yaml 等）。源码引用不算运行时证据。" >&2
    exit 1
fi
```

**为什么用文件类型而不是关键词**：
- 不绑定技术栈——后端（pytest .log）、前端（screenshot .png）、API（response .json）都适用
- 纯文本（.md/.txt）是"手写描述"的典型载体，运行时工具产出天然是结构化格式
- 已有的 PASS 文件引用检查（L30-40）已要求 `.png/.jpg/.log/.json/.html/.txt/.yaml/.yml`——L3 只在此基础上加"不能全是 .md/.txt"

#### 已有机制不重复

| 已有 | 覆盖 | L3 补的 |
|------|------|---------|
| PASS 必须有文件引用 | 证据文件存在性 | — |
| 截图 >1KB (R1a) | 防空 png | — |
| md5 去重 | 防复制截图 | — |
| vision YAML blocker_count=0 (R1b) | 视觉验证 | — |
| — | — | evidence 不能全是纯文本（防源码分析充数）|

---

### 2. verifier 角色强化（流程层软约束）

#### 问题

verifier.md:64 已写"实跑不是看代码推断"，但 agent 在实际操作中遇到工具困难时仍然回退源码。原因是：角色文件没告诉 agent **遇到工具困难时该怎么办**。

#### 设计

verifier.md 补充两条规则：

```markdown
### 工具困难时的处理（不能回退源码）

遇到无法用工具到达目标页面/状态时（导航复杂、需滚动/交互、桌面软件等）：

1. **不要回退源码分析**——"源码看起来对"不等于"运行时正常"
2. **记录导航尝试**——在 P6-acceptance.md 写明尝试了什么导航步骤、为什么没到达
3. **标 [NEED_CONFIRM]**——交人判断，不要自行判定 PASS
4. **截图必须对应 BDD 场景**——不能截一个通用页面就完事，截图必须展示 BDD 描述的具体状态

"工具返回看不到问题"不等于"没有问题"——可能是工具使用方式错了（没导航到正确页面/没触发交互）。
```

这是软规则（角色文件指引），不是 gate 检查。gate 只能查文件类型，查不了截图内容是否对应场景。

---

### 3. 诊断优先提醒（hook 层，完全保留 v1 设计）

#### 问题

agent 收到 bug 反馈后，不跑诊断命令直接猜测修改，改了不对再猜再改——试错循环。retries >= 2 是试错循环的代理指标。

#### agate 已有的

| 机制 | 覆盖 |
|------|------|
| check-retrospective.sh | retries 超限时提醒"建议复盘"（事后总结）|
| check-state-transition.sh | retries 超限 → PAUSED |

#### 缺的

retries >= 2（未超限但已重试）时没有事中干预——只在超限后总结，没有在重试过程中提醒"该诊断了"。

#### 设计

check-retrospective.sh 扩展：retries[Pn] >= 2 且未超限时输出诊断提醒。

```bash
# 现有：超限时提醒"建议复盘"
# 新增：>= 2 未超限时提醒"建议跑诊断命令"
```

WARNING 不阻塞，和现有复盘提醒一致。

**与已有的区别**：
- 现有：retries 超限 → "建议复盘"（事后）
- 新增：retries >= 2 未超限 → "建议跑诊断命令确认根因"（事中干预）

两者不冲突——超限时两个提醒都输出。

---

## 改动汇总

### 扩展脚本

| 脚本 | 改动 |
|------|------|
| `scripts/check-p6-evidence.sh` | `ui_affected: true` 时增加 L3：evidence 不能全是 .md/.txt |
| `scripts/check-retrospective.sh` | `retries >= 2` 未超限时输出诊断提醒 |

### 文档改动

| 文件 | 改动 |
|------|------|
| `agate/assets/execution-roles/verifier.md` | 补"工具困难时的处理"规则 |
| `agate/dispatch-protocol.md` | 铁律区加"诊断优先"软规则 |

### 不新增的

| 不新增 | 理由 |
|--------|------|
| check-hotfix.sh | hotfix 协议砍掉 |
| commit-msg-gate.sh | hotfix 协议砍掉 |
| install-hook.sh 扩展 | hotfix 协议砍掉 |
| WORKFLOW.md hotfix 节 | hotfix 协议砍掉 |
| git-integration.md wf(hotfix): | hotfix 协议砍掉 |

### 测试

| 文件 | 用例 |
|------|------|
| `tests/unit/check-p6-evidence.bats` 扩展 | 3 个（全 .txt 拦截 / 有 .json 通过 / ui_affected=false 跳过） |
| `tests/unit/check-retrospective.bats` 扩展 | 2 个（retries=2 提醒 / retries=1 不提醒） |

## 实现顺序

1. check-p6-evidence.sh L3 扩展 + 单元测试
2. check-retrospective.sh 诊断提醒 + 单元测试
3. verifier.md 角色强化
4. dispatch-protocol.md 诊断优先软规则
5. 全量测试 + consistency + shellcheck + self-gate
