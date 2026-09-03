---
status: approved
phase: P1
task_id: TAG0031
parent: P1-requirements.md
trace_id: TAG0031-P1-review-20260904-r2
created: '2026-09-04'
agent: requirements-review
---

# P1-review.md — TAG0031 需求基线独立评审（requirements-review，agent≠main，第 2 轮复评）

> 本轮范围：仅复核第 1 轮判 needs-revision 的两处修订点（同类扫描第 3 小节口径 + DEBT 登记闭合
> 覆盖缺口），其余已通过部分（BDD-1~13 除 BDD-14 引用微调外、P0_STALE、frontmatter、裁剪说明、
> 同类扫描小节 1/2/4/5/6/7）沿用第 1 轮结论，抽查未发现被意外改动。

## 复核点 ①：同类扫描第 3 小节口径（BDD-14 相关）

独立执行正文展示的原始命令：

```
grep -n "dirname(dirname\|dirname(os.path.dirname" agate/scripts/*.py
```

独立复核实测命中 **14 行**，与正文声称的"14 行"逐字节一致（同一组 file:line 清单，无遗漏无多余）：
`agate-advance.py:59`、`agate_common.py:220`、`agate_common.py:662`、`agate-dispatch.py:68`、
`agate-inject-card.py:47`、`agate-next-card.py:50`、`agate-next.py:86`、
`agate-render-dispatch-prompt.py:46`、`agate-render-dispatch-prompt.py:191`、`check-gate.py:983`、
`check-gate.py:986`、`check-retrospective.py:74`、`check-structure-consistency.py:115`、
`check-yaml-schema.py:147`。

按正文的类别 A（`task_dir` 起点）/ 类别 B（`__file__`/`script_path` 起点）拆分独立复核：

- **类别 A**（`check-gate.py:983,986` 同一实例的注释+代码、`check-retrospective.py:74`、
  `agate-render-dispatch-prompt.py:191`）：4 行 / 3 个实例，与正文声称的"4 行 3 实例"一致。已读
  取三处上下文确认推导起点均为 `task_dir`（`check-retrospective.py:74` 用
  `os.path.dirname(os.path.dirname(os.path.abspath(task_dir...)))`；`agate-render-dispatch-prompt.py:191`
  用 `os.path.dirname(os.path.dirname(task_dir))`），判定成立。
- **类别 B**（其余 10 行）：独立读取 `agate_common.py:220`（`real = str(Path(script_path).resolve())`
  → `os.path.dirname(os.path.dirname(real))`）、`agate_common.py:662`（直接对 `script_path` 取
  两级 dirname）、`agate-render-dispatch-prompt.py:46`（`script_real = os.path.realpath(__file__)`
  → 两级 dirname）三处代表性上下文，确认推导起点均为脚本自身文件路径（`__file__`/`script_path`），
  与正文描述一致；其余 7 行（`agate-advance.py:59`/`agate-dispatch.py:68`/
  `agate-inject-card.py:47`/`agate-next-card.py:50`/`agate-next.py:86`/
  `check-structure-consistency.py:115`/`check-yaml-schema.py:147`）通过 grep 输出本身已可判定
  （均直接 `os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` 或
  `os.path.realpath(__file__)` 变体），10 行计数与正文一致。

4（类别 A）+10（类别 B）=14，与命令实测命中数逐字节对应，**口径失真问题已修正**。类别 B 不构成
DEBT0016 同类的论证（风险成立前提是推导起点依赖 workspace 相对层级约定，类别 B 锚定的是 agate
仓库/安装根这一固定部署事实，不随 workspace 布局变化）逻辑自洽，独立核对代码后未发现反例。

**BDD-14 Given 引用**已随第 3 小节同步更新为"类别 A 非本体 2 处 + 类别 B 10 处不构成同类"表述，
与修订后第 3 小节结论一致，无新的不一致。

**结论：复核点①通过。**

## 复核点 ②：DEBT0002/0003/0004/0016/0017/0018 六条登记闭合覆盖（新增 BDD-15）

独立执行 `grep -c '^#### BDD-' P1-requirements.md`，实测 **15**，`#### BDD-NN:` 编号 1~15 连续
不跳号（BDD-1 至 BDD-15 逐条核对标题行存在）。

新增 `#### BDD-15: 六条 DEBT 登记条目闭合，与 BDD-7 共同覆盖任务标题声明的 7 条`：

- Given 子句逐字列出六个 debt id：DEBT0002（关联 BDD-1/2）、DEBT0003（关联 BDD-3）、DEBT0004
  （关联 BDD-4/5）、DEBT0016（关联 BDD-8/9）、DEBT0017（关联 BDD-10/11）、DEBT0018（关联
  BDD-12/13），六者均已在正文中显式点名，逐一对应各自代码/文档验收 BDD，无遗漏、无张冠李戴。
- Then 子句明确"六条条目 `status` 均由 `open` 改为 `closed`，各自追加 `closed_at` 与 closure
  说明，`evidence` 追加指向对应 BDD 编号与实现 commit"，可二值判定（登记条目改后逐条核对
  status/closed_at/evidence 是否落地）。
- 登记格式对齐先例：独立核对 `agate-workspace/debt/tech-debt.md` 中 DEBT0005/DEBT0006 的 closed
  条目结构（`status: closed` + `closed_at` + evidence 追加 closure note 块），与 BDD-15/BDD-7
  引用的格式描述一致。

BDD-15 与 BDD-7（DEBT0007 单独登记闭合）合计覆盖全部 7 个 debt id 的登记闭合验收，与任务标题
"批量关闭 7 条历史遗留 open 技术债"目标对齐，**第 1 轮发现的"仅 1/7 条有登记闭合验收"缺口已补齐**。

**结论：复核点②通过。**

## 沿用部分（抽查，未重新展开逐项复核）

- BDD-1~13（除 BDD-14 已在复核点①单独核实）：抽查标题行与第 1 轮引用逐一比对，未发现被意外
  改动的迹象；BDD 编号连续、格式 `#### BDD-NN:` 未变。
- P0_STALE 判定（DEBT0007 轻微漂移分类）：正文「P0-brief 时效性质疑」节文字未变，沿用第 1 轮
  结论（合理，不阻塞）。
- frontmatter 声明（`risk_level: medium` / `phases: [P1..P8]` / `packages` / `domains: [backend]`）：
  抽查未变。
- 裁剪说明（P3/P7 不可裁理由）：抽查未变，沿用第 1 轮"理由充分"结论。
- 同类扫描小节 1/2/4/5/6/7：抽查未变，沿用第 1 轮独立复核结论（均一致）。

## 结论

评审结论：**approved**（详见 frontmatter `status` 字段）。

第 1 轮 needs-revision 指出的两处缺口——① 同类扫描第 3 小节口径与独立 grep 不一致（14 vs 3，
BDD-14 相关）；② DEBT0002/3/4/16/17/18 六条登记条目缺显式登记闭合 BDD——本轮均已独立复核确认
修正到位：第 3 小节改为宽口径 14 行按 `task_dir`/`__file__` 两类拆解（4 行 3 实例 vs 10 行），
与展示的 grep 命令逐字节对应；新增 BDD-15 补齐六条 DEBT 的登记闭合验收，与 BDD-7 共同构成 7/7
覆盖。BDD-1~13（除 BDD-14 引用同步微调）、P0_STALE、frontmatter、裁剪说明、同类扫描小节
1/2/4/5/6/7 抽查确认未被意外改动，沿用第 1 轮通过结论。P1 需求基线本轮复评通过。
