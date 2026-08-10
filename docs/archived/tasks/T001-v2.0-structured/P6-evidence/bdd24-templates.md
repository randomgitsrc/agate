# BDD-24 — 角色卡/模板贴可复制 frontmatter 模板

验证方式：对 task-files.md（P1/P2/P6/P7 四类产出规格）+ analyst.md/architect.md/verifier.md 三个角色卡中的全部 ```yaml 代码块，逐块用 yaml.safe_load 解析验证（剥离 --- 分隔符后按 agate-md-field-get.py 的 _read_frontmatter 同等方式解析）。完整脚本输出见同目录 bdd24-templates.txt。

## 汇总结果
TOTAL=14 个 yaml 代码块，OK=13，FAIL=1（详见 bdd24-templates.txt）

## 唯一失败项核实：非 BDD-24 覆盖范围的通用文档头模板
失败的 block 0（task-files.md）是文件顶部'通用 Header（所有文件必须有）'章节的**通用占位符模板**（`phase: {P1-P8}`、`task_id: {Txxx}` 等大括号占位符），本身设计为文本替换模板而非可直接 yaml.safe_load 解析的字面样例，不是 BDD-24 指向的'迁移字段可复制样例'（后者是 P1/P2/P6/P7 各自小节下方标注'frontmatter（v2.0 机器字段，直接复制到文件头 --- 块）'的专门代码块，对应 block 2/3/4/5，全部 OK）。

## P1/P2/P6/P7 四类迁移字段样例定位核实（task-files.md 独立重新读取）
```
125:**frontmatter（v2.0 机器字段，直接复制到文件头 `---` 块）**：
229:**frontmatter（v2.0 机器字段，直接复制到文件头 `---` 块）**：
312:**frontmatter（v2.0 机器字段，直接复制到文件头 `---` 块）**：
365:**frontmatter（v2.0 机器字段，直接复制到文件头 `---` 块）**：
```

## P6 正文示例格式核实（P4-implementation.md 声明已订正为 - PASS BDD-N: 格式，独立复核）
```
```markdown
## 验收结果（逐条对照 P1 的 BDD）

**BDD 二值规则**：每条 BDD 结果只允许 PASS 或 FAIL，不允许"⚠️ 调整/跳过/覆盖"等中间态。
**截图质量标准**：操作类 BDD 截图必须互不相同（md5 去重），查询类 BDD 可不截图（断言值是唯一证据）。

#### BDD-1: entry 不指定过期时间默认 15 天
- PASS BDD-1: 创建 entry 不填过期 → 实测 15 天后过期（p6-bdd-1.png）
- PASS BDD-1: MCP publish_files 不传 expires → 实测同样生效

#### BDD-2: ...
- FAIL BDD-2: 实测结果与预期不符：... → 触发回 P4

## 验收小结（总结行，不计入逐条 PASS/FAIL 统计）
**Summary**: 28/28 PASS, 0 FAIL，UI 截图 N 张
```
```
确认：P6 正文示例 `- PASS BDD-1: ...` / `- FAIL BDD-2: ...` 已符合流 B 从严格式（行首 - PASS|FAIL BDD-NN），与 BDD-17 一致。

## P7-consistency.md 样例存在性核实（此前 task-files.md 无 P7 章节，P4 新增）
```
## P7-consistency.md 结构（一致性检查）

**frontmatter（v2.0 机器字段，直接复制到文件头 `---` 块）**：
```yaml
---
phase: P7
task_id: T001              # 替换为实际任务编号
type: consistency
parent: P2-design.md
trace_id: T001-P7-20260101 # {task_id}-P7-{YYYYMMDD}
status: draft
created: 2026-01-01
agent: consistency-reviewer
# ── v2.0 机器计数 ──
blocker_count: 0                  # int ≥0（BDD-19）
deviation_count: 0                # int ≥0（BDD-19）
deviation_critical_count: 0       # int ≥0（DEVIATION-CRITICAL）
design_gap_count: 0               # int ≥0（BDD-20）
design_gap_reviewed_count: 0      # int ≥0（BDD-20）
---
```
```

结论：analyst.md/architect.md/verifier.md 三个角色卡的全部 yaml 块（8 个）+ task-files.md 的 P1/P2/P6/P7 迁移字段专用样例（4 个）共 12 个目标样例块全部通过 yaml.safe_load 校验，可直接复制使用；唯一的'FAIL'是不在 BDD-24 覆盖范围内的通用占位符文档头（设计如此，非字面 YAML）。
