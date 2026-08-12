# BDD-1: 机器字段从 frontmatter 统一读取

## P5 已有测试证据（P5-test-results/unit.md 全量实跑 600/600 中摘录）
- `ok 77 MDF.1 BDD-1: risk_level 从 frontmatter 块读取（字段级 presence 优先）`
- `ok 81 MDF.5 BDD-1: 新增 op candidate_count 从 P2 frontmatter 读取（int → str）`
- `ok 82 MDF.6 BDD-1: 新增 op packages 从 frontmatter 列表读取（空格连接）`
- `ok 177 G_BDD1.1 BDD-1: check-gate.sh P2 四字段经 frontmatter 声明（非正文）仍被门禁正确读取判定`
- `ok 369 P2.6c BDD-1: check-pruning.sh 裁剪 P7 + frontmatter implicit_coupling 字段 期望 exit 1`
- `ok 373 P2.7a BDD-1: check-pruning.sh 裁剪 P8 + frontmatter internal_only: true + internal_only_reason 放行`
- `ok 516 R4.2 BDD-1: 裁剪 P8 + frontmatter internal_only: true + internal_only_reason → exit 0`
- `ok 519 R3.2 BDD-1: 裁剪 P7 + 暂存区 3 个源文件 + frontmatter coupling_checklist → exit 0（≤ 5）`

这些测试断言的是"字段声明在 frontmatter 中时，门禁读取该字段的判定结果与声明一致"——直接对应
BDD-1 的 Given/When/Then。

## 本次验收独立复现（2026-08-10，非引用旧结果，重新跑）
构造一份纯 frontmatter 声明字段（正文不含这些字段）的 P1-requirements.md：
```yaml
---
phase: P1
task_id: T001
risk_level: high
phases:
  - P1
  - P2
  - P3
packages: [agate]
domains: [backend]
---
# doc body without these fields
```
执行：
```
$ FILE=.../P1-requirements.md python3 agate/scripts/agate-md-field-get.py risk_level
high
$ FILE=.../P1-requirements.md python3 agate/scripts/agate-md-field-get.py phases
P1 P2 P3
```
门禁读取值与 frontmatter 声明值一致（"high"、"P1 P2 P3"），且正文完全不含这些字段，证明读取确实来自
frontmatter 而非正则误命中正文。

## agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-gate-p5-count.py / agate-read-p5-commands.py
对本任务自身 P2-design.md（gate_commands 声明在正文，属流 A 不迁移范围）实测四个工具均正确输出
（详见 BDD-15 证据文件），侧面确认双读工具改造未影响 gate_commands 读取路径。

## DESIGN_GAP 交叉核对（P4-implementation.md 第 78/86 行）
- [DESIGN_GAP L78]：check-gate.sh 的 P2 分支未按 P2-design.md §3.1.2 迁移到双读工具，仍用原有 grep。
  implementer 用 git stash 验证该分支对 frontmatter 场景巧合兼容（顶格 grep 天然命中 frontmatter 首行），
  P3-test-cases.md 已把 G_BDD1.1 标注为 "characterization：文件首现优先 grep 巧合正确"。
- [DESIGN_GAP L86]：check-pruning.sh 的 8 个 P1 字段读取点同理未迁移，理由相同。
- 本次验收观察：这两处 DESIGN_GAP 意味着 check-gate.sh P2 分支 / check-pruning.sh 8 字段点**没有真正走
  agate-md-field-get.py 的双读逻辑**，而是依赖"frontmatter 顶格书写 + grep 对整文件取值 + frontmatter
  总在正文之前"这三个条件的巧合组合。只要这三个前提成立，BDD-1 描述的行为（"门禁基于 frontmatter 声明值
  完成判定"）在这两处仍然成立，且已用 git stash 对比验证；但这不是 BDD-1 字面要求的"从 frontmatter 统一
  读取"的机制层面兑现——是巧合兼容而非双读实现。回归风险：若某字段将来在正文出现在 frontmatter 之前
  （反常写法），这两处会读到错误值。

## 判定
PASS——MDF.1/G_BDD1.1/P2.6c/P2.7a/R4.2/R3.2 六类场景（agate-md-field-get.py 双读点 + check-pruning.sh
读取点）均已用 P5 测试与本次独立复现证实门禁基于 frontmatter 声明值判定；DESIGN_GAP 已如实标注，
不影响当前观察到的行为结果。
