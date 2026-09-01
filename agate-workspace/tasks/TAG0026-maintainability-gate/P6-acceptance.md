---
phase: P6
task_id: TAG0026
type: acceptance
parent: P5-verification.md
trace_id: TAG0026-P6-20260830
status: draft
created: 2026-08-30
agent: verifier
# ── v2.0 机器汇总 ──
pass: 13
fail: 0
ui_affected: false
---

# P6-acceptance — TAG0026 维护性反模式 gate（RM-AG0046）验收报告

## 1. 验收方法

`[PROD_NOT_TOUCHED]` 全程只读验收：不修任何代码，所有 git 写操作（init/add/commit）仅在
`/tmp` 下新建的临时仓库内完成、用后销毁，worktree 仓库零 git 写操作。

- **判定依据**：P1-requirements.md §7 的 13 条 BDD 逐条对照判定锚；铁律为先验证后结论，
  每条 PASS 的依据是证据文件里的真实命令输出（含命令行与 EXIT_CODE），不是代码推断。
- **检测器行为类 BDD-1..6/11/12/13**：在临时 git 仓库中实际运行 worktree 自己的
  `python3 agate/scripts/check-maintainability.py {tmp_task_dir}`（CLI 重放），场景按 BDD
  Given 子句构造，输出原样落盘 `P6-evidence/bdd-N.log`。
- **P4 三重门槛类 BDD-7..10**：实际运行 worktree 自己的
  `python3 agate/scripts/check-gate.py P4 {tmp_task_dir}`，单一临时仓库单调演化四态
  （登记缺失 → 数量不足 → 评审未 approve 三变体 → 三重满足），gate 子进程 cwd 指向临时
  仓库使其 `_git`/检测数据源全部落在临时仓库；工具（check-gate.py / check-maintainability.py）
  均为 worktree 版本，非 `~/.agate` 稳定版。
- **平台无关 BDD-11**：口径对齐 P3 `test_bdd_11_path_separator_normalized` 的 Linux 侧——
  CLI 实跑断言 violations 文件字段为 `/` 归一形态 + `_norm_rel` 两种分隔符归一等价；
  真实 Windows 分隔符行为由 Windows CI windows_smoke 用例覆盖（按平台分支）。
- **P5 证据复用**：全量回归证据引用 `(../P5-test-results/unit.md)`（p5_pass_commit=f7e7b9f，
  P5→P6 间无非产出文件改动，审计 7 允许复用）；13 条功能性行为证据全部为本阶段独立重放
  产出，未复制 P3/P5 测试输出。
- **证据路径约定**：PASS 行括号内路径相对 `P6-evidence/`。

## 2. BDD 逐条验收结果

- PASS BDD-1: god-file 跨越检测——临时仓库 900 行文件 staged 新增 250 行后 1150 行，violations 含该文件 god-file 违规，god_file_count=1，detail 为 before=900 after=1150 threshold=1000，CLI exit 1 (bdd-1.log)
- PASS BDD-2: god-file 不误伤存量——1200 行存量文件本次 diff 仅真实修改 5 行（numstat 5/5 核验），before/after 均达阈值以上未跨越阈值线，violations 不含该文件，god_file_count=0，exit 0 不阻断 (bdd-2.log)
- PASS BDD-3: fuzzy-boundary Python 检测——staged 新增裸 except 行于第 14 行，violations 含该文件与新增行号，输出 fuzzy-boundary: base.py:14 且命中正则，fuzzy_boundary_count=1，exit 1 (bdd-3.log)
- PASS BDD-4: fuzzy-boundary 不误伤存量——存量裸 except 行已 commit、不在本次 diff 新增行中（新增行仅为 x_8/x_9 两处修改），violations 不含该存量行，fuzzy_boundary_count=0，exit 0 (bdd-4.log)
- PASS BDD-5: 阈值可配置——同一 480→520 staged 变化在配置 god_file_threshold 为 500 时触发违规且 detail 含 threshold=500，删除配置文件后默认 1000 下同一变化不触发，双向对照证明配置生效 (bdd-5.log)
- PASS BDD-6: 配置缺失兜底——无 maintainability.yaml 时检测器用默认阈值 1000 与默认正则集正常判定，god_file_count=1 与 fuzzy_boundary_count=1 均为客观值，stderr 为空、无报错、无静默跳过 (bdd-6.log)
- PASS BDD-7: 三重门槛登记缺失阻断——violations 3 条（前置核验输出 3 条 fuzzy-boundary）、known-violations.md 不存在、P4-review approved 且 agent=review，门槛 a 命中，stderr 提示需登记 known-violations.md，gate_p4 exit 1 (bdd-7.log)
- PASS BDD-8: 登记数量硬校验——violations 3 条而登记仅 2 条行首数字行，门槛 b 命中，stderr 提示登记条目数 2 小于 violation 数 3、登记不完整，exit 1，不是有文件就过 (bdd-8.log)
- PASS BDD-9: 数量对齐但评审未 approve 仍阻断——登记 3 条与 violations 3 条对齐后三变体全部阻断：P4-review.md 不存在 exit 1、status=draft exit 1、agent=main exit 1，均输出既有检查的真实阻断消息，不能靠数量对齐单独放行 (bdd-9.log)
- PASS BDD-10: 三重门槛全满足才放行——violations 3 条、登记 3 条、P4-review approved 且 agent=review，三重齐全 gate_p4 exit 0 放行且无阻断消息；known-violations 登记内容不进入 provenance 审计范围（未新增第八道审计） (bdd-10.log)
- PASS BDD-11: 平台无关性——god-file violation 的 file 字段输出为 `/` 归一形态、无反斜杠，`_norm_rel` 将 `src\big.py` 与 `src/big.py` 归一到同一相对路径（worktree 单源实现），同一 diff 场景两种分隔符表示时检测结果一致 (bdd-11.log)
- PASS BDD-12: 移动代码假阳性诚实处理——含裸 except 的 4 行块从文件中部移动到末尾，diff 构成删除行加新增行，新增行照判 violation（fuzzy-boundary: mover.py:18，行号大于原位置 11-14），未被自动识别为移动而忽略；同场景登记 1 条、数量对齐、评审 approve 后 gate_p4 exit 0，该 violation 经 known-violations 三重门槛正常吸收 (bdd-12.log)
- PASS BDD-13: 数据源与挂载阶段对齐——同一临时仓库两侧对照：P4 语境（代码 staged）时检测器读到代码 diff 并产生客观判定（fuzzy-boundary: p4feat.py:6，exit 1）；P6 语境（代码已 commit、暂存区无代码 diff）时不产生 violation（计数 0/0，exit 0），证明检测器挂载在 P4 而非 P6 (bdd-13.log)

**Summary**: 13/13 PASS, 0 FAIL

## 3. 验收时的事实记录

- 本报告全部结论基于验收时实跑输出；无 FAIL 项，无"修复后 PASS"情形。
- 场景构造失败与重跑记录（诚实留痕，最终均以有效场景重放判定）：BDD-2 首次 heredoc 转义
  错误致 legacy.py 未修改即跑（作废）；BDD-7..10 前两次 bash 场景构造目录未就位、staged
  diff 为空（作废，改用 Python 场景构造脚本）；BDD-12 首次 except 块上下文对称、git 锚定
  为未变上下文致 except 行不在新增行中（作废，改复刻 P3 场景构造）；BDD-11 一次脚本笔误
  修复后重跑。全部重跑注记见 `P6-progress.md` 与各证据日志内 `# 注` 行。
- BDD-9 三个变体与 BDD-7/8/10 在同一临时仓库同一 staged 状态下依序演化，violation 数=3 的
  前置核验（检测器 3 条 fuzzy-boundary 输出）保存在 `bdd-7.log`，被 bdd-8/bdd-10 结论引用。
