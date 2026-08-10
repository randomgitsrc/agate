# BDD-21: P1 标记"已解决/已确认"状态结构化

## P5 测试证据
- `ok 387 RT_BDD21.1 BDD-21: check-gate.sh P1 frontmatter need_confirm_resolved 已覆盖具体描述时该 NEED_CONFIRM 项不再阻塞`
- `ok 264 P1: BDD-21 边界（未结构化解决时仍阻塞）：P1-requirements.md 含 NEED_CONFIRM 期望 exit 1`（反面回归，
  确认"未结构化解决"仍然阻塞，避免"结构化机制被滥用导致所有 NEED_CONFIRM 都不阻塞"的退化）

## 本次验收独立复现（正反两面）

### 正面：need_confirm_resolved 覆盖具体描述后不再阻塞
```yaml
---
phase: P1
need_confirm_resolved:
  - z 的边界条件需确认
---
- [NEED_CONFIRM] z 的边界条件需确认
```
（另配 P1-review.md: status approved + agent=requirements-review + 含 BDD 锚点，跨过前置的
P1-review 检查步骤）
```
$ bash agate/scripts/check-gate.sh P1 <TASK_DIR>
GATE P1: P1-review.md approved + agent≠main + 含 BDD 锚点。BDD 编号格式为 #### BDD-NN:
REAL EXIT=2   （P1 gate 成功码）
```

### 反面：同样的 NEED_CONFIRM 但不声明 resolved → 仍阻塞
```yaml
---
phase: P1
---
- [NEED_CONFIRM] z 的边界条件需确认
```
```
$ bash agate/scripts/check-gate.sh P1 <TASK_DIR>
GATE P1: 1 个未解决的 NEED_CONFIRM 项（阻塞）
REAL EXIT=1
```
两组唯一差异是 frontmatter 是否声明 `need_confirm_resolved` 逐条匹配正文描述，结果从
exit 1（阻塞）变为 exit 2（放行）。证明"门禁只把未在 frontmatter 声明 resolved 的
NEED_CONFIRM 计为阻塞，已结构化解决的项不阻塞"（BDD-21 Then），且散文标记本体
（`- [NEED_CONFIRM] ...`）在两种场景下均原样保留未被删除，只是机器判定改读结构化状态。

## 判定
PASS
