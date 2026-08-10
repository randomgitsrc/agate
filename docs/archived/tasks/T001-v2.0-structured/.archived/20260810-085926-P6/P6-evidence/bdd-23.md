# BDD-23: 发现性标记（SCOPE+/PROD_TOUCHED/DESIGN_GAP）本体保持散文

## P5 测试证据（全部回归绿灯，边界确认"不改动即通过"）
- `check-scope-resolved.bats` SC.2/SC.3/SC.4/SC.6/SC.7（散文扫描回归，5 用例）
- `pre-commit-hook.bats` 的 IT_PT_* / IT_PT_T6.* 系列（PROD_TOUCHED 行首锚定回归）
- P5 全量结果：`bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
  agate/tests/sanity.bats` → 600/600 全绿，含以上全部用例

## 本次验收独立复现
### 代码层面确认发现性标记检测逻辑未被结构化替换
```
$ grep -n "PROD_TOUCHED\]" agate/scripts/pre-commit-gate.sh
131:  echo "GATE: [PROD_TOUCHED] 检测到生产环境接触...commit 中止"
135:  echo "GATE: 不合规的 PROD_TOUCHED 标记格式...须用行首 [PROD_TOUCHED] 或 [PROD_NOT_TOUCHED] 声明"

$ grep -n "SCOPE+\]\|for f in" agate/scripts/check-scope-resolved.sh
18:for f in "$TASK_DIR"/*.md; do
37:# 发现性标记本体（[SCOPE+]）保持散文不迁移（BDD-23），但"已解决"状态改为结构化
45:  echo "GATE SCOPE: ...有 [SCOPE+]，P1 frontmatter scope_resolved 非空..."
```
PROD_TOUCHED 仍是行首锚定字符串检测；SCOPE+ 仍是跨文件 `for f in "$TASK_DIR"/*.md` 散文扫描
——两者均未被结构化替换，源码内注释明确标注"发现性标记本体保持散文不迁移（BDD-23）"。

### 重跑相关测试确认行为与 v0.35 一致（非引用旧结果，本次独立重跑）
```
$ bats agate/tests/unit/check-scope-resolved.bats agate/tests/integration/pre-commit-hook.bats
1..62
...
ok 46 IT_PT_T6.3 任务产出文件含行首 [PROD_TOUCHED]（步骤1）→ 拦截（回归）
ok 47 IT_PT_T6.4 任务产出文件含 [PROD_NOT_TOUCHED]（负向声明）→ 不拦截（回归）
...
62/62 全绿
```
PROD_TOUCHED 行首锚定仍触发中止、SCOPE+ 仍被跨文件扫描识别，与 v0.35 行为一致。

## 判定
PASS
