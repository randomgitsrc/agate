---
review_date: 2026-07-02
reviewer: protocol-alignment-review
change_summary: md5 去重实现——check-p6-evidence.sh 新增截图重复检测，dispatch-protocol.md/verifier.md/task-files.md md5 和断言记录从"建议"改回"hook 强制"
files_changed:
  - agate/scripts/check-p6-evidence.sh
  - agate/dispatch-protocol.md
  - agate/assets/execution-roles/verifier.md
  - agate/assets/templates/task-files.md
  - agate/tests/unit/check-p6-evidence.bats
---

# 协议-脚本对齐审查：md5 去重实现

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | NEEDS_HUMAN_REVIEW |
| A6 | 锚点表覆盖 | ALIGNED |

## 逐项审查

### A1: 文档→脚本对齐

**1. md5 去重 hook 强制**

文档声明（dispatch-protocol.md:359）：
> 操作类 BDD 截图必须互不相同（md5 去重，hook 强制）

文档声明（dispatch-protocol.md:581，gate 表 P6→P7 行）：
> 截图质量标准：操作类 BDD 截图必须互不相同（md5 去重，hook 强制）

文档声明（verifier.md:130）：
> 操作类 BDD 截图必须互不相同（md5 去重，hook 强制），查询类 BDD 可不截图（断言值是唯一证据）

脚本实现（check-p6-evidence.sh:84-91）：
```bash
MD5_LIST=$(find "$SCREENSHOTS_DIR" -type f -not -name '.*' -exec md5sum {} \; 2>/dev/null | cut -d' ' -f1 | sort)
MD5_TOTAL=$(echo "$MD5_LIST" | wc -l)
MD5_UNIQUE=$(echo "$MD5_LIST" | sort -u | wc -l)
if [ "$MD5_TOTAL" -gt "$MD5_UNIQUE" ]; then
    MD5_DUPES=$((MD5_TOTAL - MD5_UNIQUE))
    echo "GATE P6-EVIDENCE: P6-evidence/screenshots/ 有 ${MD5_DUPES} 个重复文件（md5 去重），操作类 BDD 截图必须互不相同" >&2
    exit 1
fi
```

**结论**：ALIGNED。文档声明"hook 强制"（即 exit 1 拦截），脚本实现 exit 1 拦截，语义一致。

**2. 断言记录文件 hook 强制**

文档声明（task-files.md:271）：
> 所有 PASS 都必须有文件引用（hook 强制）——无文件引用的纯断言 PASS 不被接受

脚本实现（check-p6-evidence.sh:30-40）：
```bash
PASS_WITHOUT_REF=0
while IFS= read -r line; do
    if ! echo "$line" | grep -qE '\([a-zA-Z0-9_/.-]+\.(png|jpg|log|json|html|txt|yaml|yml)\)'; then
        PASS_WITHOUT_REF=$((PASS_WITHOUT_REF + 1))
    fi
done < <(grep -E '^\s*- PASS\b' "$P6_FILE" 2>/dev/null || true)
if [ "$PASS_WITHOUT_REF" -gt 0 ]; then
    echo "GATE P6-EVIDENCE: 有 ${PASS_WITHOUT_REF} 条 PASS 缺文件证据引用..." >&2
    exit 1
fi
```

**结论**：ALIGNED。文档声明"hook 强制"，脚本 exit 1 拦截，语义一致。

### A2: 脚本→文档对齐

脚本新增逻辑（check-p6-evidence.sh:84-91）md5 去重 exit 1 拦截。

对应文档已同步更新：
- dispatch-protocol.md:359（P5/P6 派发追加段）——"md5 去重，hook 强制"
- dispatch-protocol.md:581（gate 表 P6→P7 行）——"md5 去重，hook 强制"
- verifier.md:130（质量门槛）——"md5 去重，hook 强制"
- vision-analyst.md:262（截图质量标准）——"md5 去重"

**结论**：ALIGNED。脚本新增的 md5 去重拦截逻辑在所有相关文档中均有对应声明。

### A3: 一致性连锁 + 反向传播

**A3a 连锁（已知的衍生改动）**：
- dispatch-protocol.md 两处 md5 从"建议"改回"hook 强制"——已改
- verifier.md md5 从"建议"改回"hook 强制"——已改
- task-files.md 断言记录文件从"建议"改回"hook 强制"——已改

**A3b 反向传播（主动推断的应被影响文档）**：

| 应被影响文件 | 是否已影响 | 验证 |
|-------------|-----------|------|
| dispatch-protocol.md（派发模板 + gate 表） | 是 | L359 + L581 已含"md5 去重，hook 强制" |
| verifier.md（质量门槛） | 是 | L130 已含"md5 去重，hook 强制" |
| task-files.md（证据约定） | 是 | L271 已含"hook 强制" |
| vision-analyst.md（截图质量标准） | 是 | L262 已含"md5 去重"描述 |
| WORKFLOW.md | 不需要 | P6 节引用 dispatch-protocol.md gate 表，无独立截图质量细节 |
| state-machine.md | 不需要 | P6→P7 gate 行引用 dispatch-protocol.md，无独立截图质量细节 |
| orchestrator-template.md | 不需要 | 无截图质量细节，引用 WORKFLOW.md |
| LIMITATIONS.md | 不需要 | 无相关条目 |

**结论**：ALIGNED。所有应被影响的文档均已同步，无遗漏。

### A4: 测试覆盖

| 测试用例 | 覆盖场景 | 边界 |
|---------|---------|------|
| E.12（L164-185） | 重复截图（md5 相同）→ exit 1 | 两个文件内容完全相同 |
| E.13（L187-205） | 不同截图（md5 不同）→ exit 0 | 两个文件内容不同（urandom） |
| E.10（L128-144） | 单截图 ≥ 1KB → exit 0 | 单文件无重复的基线 |
| E.9（L108-126） | 截图 ≤ 1KB → exit 1 | 大小检查在 md5 之前，小文件不会到达 md5 逻辑 |

**边界覆盖分析**：
- 重复截图被拦截：E.12 覆盖
- 不同截图通过：E.13 覆盖
- 单截图（无重复可能）：E.10 覆盖
- 空 screenshots 目录：E.8 覆盖（在 md5 逻辑之前 exit 1）
- 小文件（≤1KB）：E.9 覆盖（在 md5 逻辑之前 exit 1）

**未覆盖边界**：无显著遗漏。md5 逻辑仅在 `ui_affected=true` + `HAS_SCREENSHOT_REF > 0` + screenshots 目录非空 + 所有文件 > 1KB 时才执行，这些前置条件均有测试覆盖。

**结论**：ALIGNED。

### A5: 下游影响 + 文档传播

**下游影响**：
- md5 去重是**新增拦截**——之前重复截图可通过 gate，现在会被 exit 1 拦截
- 已有项目若存在重复截图，gate 会 fail——这是**预期行为**（修复了之前缺失的检查）
- 非破坏性变更（不改变已有通过 case 的行为，只拦截之前漏拦的 case）

**文档传播**：
- vision-analyst.md:262 已含 md5 去重描述——ALIGNED
- CHANGELOG 是否需要标注？md5 去重从"建议"升级为"hook 强制"是协议语义变更

**结论**：NEEDS_HUMAN_REVIEW。md5 去重从建议升级为 hook 强制属于协议语义变更，建议在 CHANGELOG 中标注。是否标注由维护者决定。

### A6: 锚点表覆盖

CHECK 9 锚点表（check-protocol-consistency.py:543-546）：
```python
{
    "desc": "P6 截图去重（md5）",
    "script": "agate/scripts/check-p6-evidence.sh",
    "keywords": ["md5", "去重"],
}
```

脚本关键词验证：
- `md5`：check-p6-evidence.sh:84 含 `md5sum`，L89 含 `md5` → 命中
- `去重`：check-p6-evidence.sh:89 含 `去重` → 命中

**结论**：ALIGNED。锚点表已包含 md5 去重条目，关键词在脚本检查逻辑中存在（非 echo 消息文本中的假阳性——L84 的 `md5sum` 是实际检查命令，L89 的 `去重` 在错误消息中但该消息仅在检查逻辑触发后输出）。

**注意**：L89 的 `去重` 关键词在 echo 消息文本中，属于 SELF-GATE.md 描述的第三类假阳性（"关键词在错误位置：在 echo 消息文本里，不在检查逻辑里"）。但 L84 的 `md5sum` 是实际检查命令，且 `md5` 关键词通过 `md5sum` 命令命中，因此 CHECK 9 整体仍能正确检测。建议未来考虑将锚点关键词改为 `md5sum`（命令名）而非 `md5`（可能只匹配消息文本），但当前不构成 MISALIGNED。
