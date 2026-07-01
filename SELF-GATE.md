# agate 自身变更的 gate（self-gate）

> agate 改自己的协议文档或脚本时，必须走本流程。
> 和项目侧 agate 流程对等：项目用 check-gate.sh + P2 评审；agate 自身用 CHECK 9 + LLM 语义审查。

## 触发条件

以下任一文件有改动并准备 commit 时：
- `agate/scripts/*.sh`
- `agate/scripts/check-protocol-consistency.py`
- `agate/*.md`（协议文档：WORKFLOW.md / state-machine.md / dispatch-protocol.md 等）
- `agate/**/*.md`（角色文件、模板文件等子目录）
- `SELF-GATE.md`（本文件自身的改动也走 self-gate）

## 检查清单

1. **跑 check-protocol-consistency.py** — 确认 CHECK 1-9 无 ERROR
2. **派发 protocol-alignment-review subagent** — 语义对齐审查（派发模板见下文，角色定义见 `agate/assets/review-roles/protocol-alignment-review.md`）
3. **读审查报告** — MISALIGNED 必须修复，NEEDS_HUMAN_REVIEW 需附 `[HUMAN_CONFIRMED: ...]` 标记
4. **跑全量 bats** — 确认无退化
5. **如果改了 gate 逻辑** — 确认下游项目（如 PeekView）的 gate 仍能跑通

## Layer 0：CHECK 9（脚本结构兜底，自动）

`check-protocol-consistency.py` 的 CHECK 9 扫描协议文档声明的规则，核对对应脚本是否含相关关键词。

```bash
# 手动跑
python3 agate/scripts/check-protocol-consistency.py

# CI 自动跑（每次 push / PR）
```

**局限**：关键词存在 ≠ 语义一致。三类假阳性：
1. 值不匹配（文档说 `=2`，脚本写 `=3`）
2. 语义降级（文档说"强制"，脚本只 `echo 警告`）
3. 关键词在错误位置（在 echo 消息文本里，不在检查逻辑里）

语义一致性由 Layer 1 保证。

## Layer 1：LLM 语义审查（手动派发）

### 派发模板

```
你是 agate 协议-脚本对齐审查员。

## 变更内容
{diff 摘要：哪些文件改了什么}

## 审查范围
读以下文件全文：
- {变更的协议文件}
- {变更的脚本}
- agate/state-machine.md（裁剪表、重试表、转移规则——权威规则源）
- agate/dispatch-protocol.md（gate 表、门槛表——检查项声明源）

## 配套文件提示
根据变更内容，可能还需要读以下文件确认一致性：
- 如果变更涉及 gate 检查逻辑（check-gate.sh），同时读对应的角色文件
  （implementer.md / architect.md / verifier.md）确认角色侧描述是否一致
- 如果变更涉及文件格式/字段（check-pruning.sh / check-state-yaml.sh），
  同时读 assets/templates/task-files.md 确认模板是否一致
- 如果变更涉及 P6 证据格式，同时读 verifier.md 和 vision-analyst.md

## 审查清单
逐项检查 A1-A6（见 agate/assets/review-roles/protocol-alignment-review.md），每项输出：
- 审查项编号
- 文档说了什么（引用原文 + 行号）
- 脚本实现了什么（引用代码 + 行号）
- 结论：ALIGNED / MISALIGNED / NEEDS_HUMAN_REVIEW
- 若 MISALIGNED：具体差异描述 + 建议修复方向

## 产出
写到 docs/reviews/agate-alignment-review-{date}.md
```

### 闭环规则

| 结论 | 处理 |
|------|------|
| ALIGNED | 通过，可 commit |
| MISALIGNED | **必须修复**——修脚本或修文档，修完重审 |
| NEEDS_HUMAN_REVIEW | 附 `[HUMAN_CONFIRMED: 日期 确认：理由]` 标记后可 commit。未确认的等同于 MISALIGNED |

## 递归适用

本机制自身的实施也走 self-gate。任何针对 agate 的变更 plan，实施时都必须走本流程。

如果 self-gate 尚未实现（如还在 plan 阶段），实施者至少手动执行等价检查：
1. 跑现有 check-protocol-consistency.py
2. 人工逐项核对"文档描述的规则 vs 脚本实现"是否一致（对照 A1-A6）
3. 跑全量 bats
