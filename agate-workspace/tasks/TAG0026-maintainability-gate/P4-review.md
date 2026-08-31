---
phase: P4
task_id: TAG0026
parent: P4-implementation.md
trace_id: TAG0026-P4-review-20260830
created: 2026-08-30
agent: review
type: review
status: approved
implementation_dir: agate/scripts/
---

# P4-review — TAG0026 维护性反模式 gate（RM-AG0046）实现评审

> 评审对象：P4-implementation.md（M1-M8）。评审角色：review（偏执 Staff Engineer，只审不写）。
> 本评审由两轮完成：核查项 1-7/9 由前轮 reviewer 完成（锚点登记于 P4-progress.md `[review]` 前缀条目），
> 因会话中断由本轮 reviewer 接替收尾（核查项 8/9 抽查/10 + 3/7 补齐，`[review2]` 前缀条目）。
> git 纪律：全程只读（diff/show/log/status），无 worktree git 写操作；未改任何实现/测试文件。

## 评审结论

**approved** —— M1-M8 逐项落地且与 P2-design/P3 测试契约逐字对齐；测试修复严格限于主 Agent
授权的探测路径/机械笔误/场景构造三类（断言行机械验证零改动）；范围无 [SCOPE+]；未发现阻塞项。

## 逐项结论（1-10）

1. **返回约定兼容 — 过**（前轮已核 + 本轮抽查确认）：新步骤只 `return 1`
   （gate_p4 门槛 a :944-950 / 门槛 b :953-958），无新增 `return 2`（`return 2` 仅属既有
   ③ agent 缺失态，G7 用例守护）；挂载点在 ④ staged 代码检查（:930 返回点）之后、骨架
   WARNING（:970-988）之前（:932-968）；门槛 c 复用既有 ①②③（注释 :959-961，不重复实现，
   BDD-9/10 由步骤顺序天然保证）；三跳过场景（violations 空 / ImportError 降级 :966-968 /
   git_ok False :962-964）各自 WARNING 后继续向下至 `return 0`（:990）——与 gate_p4 加入前
   行为完全一致（R1 等价性，182 条 gate 回归佐证）。

2. **挂载注释字面脚本名 — 过**（前轮已核 + 本轮抽查确认）：`check-gate.py:162-164` import
   区注释与 :932 门槛步骤注释均含字面 `check-maintainability.py`，满足 M3 callers 字面校验。

3. **检测器契约 — 过**（前轮已核；本轮 3.1/3.2 补齐收尾）：
   - import 区 / 兜底 / cwd=repo_root 已核（前轮锚点）；
   - 本轮补：gate_p5 :1041-1047 数量对齐与门槛 b 同构参照确认；
   - **3.1 DESIGN_GAP 同源性核**：check-gate.py:162-185 的 except 分支 importlib 按路径加载
     （`spec_from_file_location("check_maintainability", dirname(__file__)+"/check-maintainability.py")`
     → `module_from_spec` → `exec_module`）与 `agate-risk-score.py:46-54 _load_script` 同源——
     同一 importlib.util 四步机制，仅为内联形态（无 name 替换参数——连字符文件名本就没有
     合法模块名，行为等价）；与 P4-implementation.md §3.1 申报"agate-risk-score.py _load_script
     同源机制"一致，申报与落地无出入；
   - **3.2 可加载性互证**：gate 测试 13 条 in-process 用例（`_load_gate_module`）成功加载
     check-gate.py 并消费 `check_maintainability` 符号（G6 :372-387 monkeypatch 生效即为证明）。

4. **M3/M4 漂移登记 — 过**（前轮已核 + 本轮抽查）：锚点登记
   `check-protocol-consistency.py:753`（script=agate/scripts/check-maintainability.py，
   keywords=god_file_count/fuzzy_boundary_count，callers=check-gate.py）+ `_DRIFT_SCRIPTS`
   第 8 项（`agate-summary.py:50`）；前轮实测 worktree
   `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` → exit 0
   （323 WARNING 0 ERROR），grep maintainability 零命中——CHECK9 无新告警，锚点登记生效。

5. **M5 模板与配置 — 过**（前轮已核 + 本轮抽查）：模板语义反转引用块 + 样例行首 `| # |`
   （known-violations-template.md:16，不命中 count_kf_entries 行首数字列正则，R8 成立）；
   maintainability.yaml 关键键（`god_file_threshold: 1000` :2 / python :4 / typescript :7）
   与 P2 §3.5 逐字一致，含"仅供参考可配置"注释（R9）。

6. **M6/M7 卡片 — 过**（前轮已核 + 本轮抽查）：P4 卡 :112 评审 checklist（RM-AG0046，
   字面 check-maintainability.py，判断权在评审角色）与 :150 gate 规则 exit 1 条目（三跳过
   场景不阻断）与实际 gate 行为逐字对应；P6 卡 :230 复跑提醒非阻断（BDD-13 挂载说明）。

7. **CLI exit 语义 — 过**（本轮核）：`check-maintainability.py main()`（:279-299）——
   用法缺失 → exit 1（:282-283）；git 不可用 → WARNING + exit 0（:286-288，与 gate 侧
   降级语义一致，不把"检测未跑"误报为"有 violation"）；violations 非空 → exit 1（:297-298）；
   空 → exit 0（:299）。exit code 唯一判定，输出仅为 P6 复跑可读摘要，无消费方耦合 returncode
   与文本（G10 CLI 用例 :192-211 断言形态与此一致）。

8. **测试修复授权范围 — 过**（本轮核，机械验证）：HEAD = 2225634（P3 提交）即原红灯态
   基线，`git diff HEAD` 即授权修复全量（两测试文件合计约 530 行 diff，全读）。
   **机械验证**：diff 中被增删改的 `assert` 行 = 0（grep `^[-+].*assert` 空）；无任何
   skip/xfail 标记增改 → **不存在"改断言凑绿"**。改动逐项归类：
   - **探测路径（授权类 A）**：`_gate_p4_source()` parent 二级→三级
     （unit→tests→agate，gate 测试 :46-66）；收集期探测同补三级 parent 并改
     `spec_from_file_location` 按路径加载（检测器测试 :33-55）；`_load_mod()` 改
     importlib 按路径加载（:64-75，保留 del sys.modules 新鲜语义）；
     `_load_gate_module` 删多余 Path import（纯 hygiene）；
   - **机械笔误（授权类 B）**：`td`→`_td` 共 9 处（G1/G2×2/_bdd9_case/BDD-9×3/BDD-10/
     G5a/G5b×5/G5c/G6×2/G7——改回 `_repo_with_staged` 实际返回的任务目录，语义即原意图，
     纯 NameError 修复）；G10 的 `repo/"task"`→`repo.path/"task"`、`cwd=str(repo)`→
     `cwd=str(repo.path)`、`_god_scenario` 未用返回值 `_` 前缀（GitRepo 无 `__truediv__`/
     需字符串路径/纯 hygiene）；
   - **场景构造（授权类 C）**：`_staged_code` 增 `dirty=` 参数（G1/G2b/G7 改 dirty=True，
     满足其自身 docstring/断言要求的"violations 非空"前提；G5a 合规基线不动）；G10 条目
     形状用例 fz.py 改 A 态新增（原中间 commit 会把已暂存 big.py@1150 收进 HEAD 使
     god-file 场景消失——注释 :151-152 留档）；G6 两例 `monkeypatch.chdir(repo.path)`
     （in-process 无 ④ 步子进程 cwd，只读 diff 锚定）；G10 CLI 清场景补 `git reset -q`
     （暂存态非空时不可能 exit 0，BDD-13 同机制）；G10 fail-closed 的 fake run_git 改返
     `(128, "")` 元组（原 fake 返回裸对象属从未执行过的死代码，真实契约 =
     `(returncode, stdout)` 元组；**断言不变**：git_ok is False / violations == []）；
   - **ruff hygiene**：未用解包 `_` 前缀 + 删未用导入（HEAD 基线自带 20 项，非本轮引入，
     不属断言语义）。
   全部 ∈ 授权范围（探测路径 / 机械笔误 / 场景构造），无第四类。

9. **断言-实现对应抽查 — 过**（本轮核，3 条关键断言）：
   - **BDD-8 数量对齐**：gate 测试 :170-171（"known-violations" in output + exit 1，G1）、
     :194-195（"登记" or "数量" + exit 1，G2）、:208-209（G2 反向 0 条分支）vs 实现
     门槛 a（:943-950 存在性：isfile 失败 → stderr "…需登记 known-violations.md…" → 1）+
     门槛 b（:953-958 `count_kf_entries(_read_text(...)) < len(violations)` → stderr
     含 "登记条目数(N) < violation 数(M)，登记不完整" → 1）——存在性与数量对齐两断言
     逐字对应，count_kf_entries 复用 agate_common 单源；
   - **G10 dict 四键**：检测器测试 :134-139（`set(result.keys())` 严格相等 + 类型断言）
     vs `check-maintainability.py:271-276` 返回 dict 恰四键同键名；条目键（:165
     god-file {type,file,detail} / :168 fuzzy-boundary {type,file,line,detail}）vs 构造点
     （:181-183 / :224-226）一致；
   - **BDD-7 登记缺失**：G1 用例（gate 测试 :162-171，无登记文件 + violations 非空 → 1）
     vs 门槛 a :943-949 fail-closed（isfile 才放行，登记文件存在性由 gate 亲查不信任
     评审侧）；模板注释含 "known-violations" 字面（known-violations-template.md 路径在
     stderr 提示中 :947）——三者闭环。

10. **范围限定 M1-M8 — 过**（本轮核）：`git status --short` / `git diff HEAD --name-only`
    全清单 vs P4-implementation.md §1/§6 逐项比对——agate/ 协议本体改动 7 文件
    （check-maintainability.py 新增、check-gate.py、check-protocol-consistency.py、
    agate-summary.py、known-violations-template.md 新增、phase-cards P4/P6）全部 ∈ M1-M7；
    代码级 agate-workspace 改动仅 maintainability.yaml（M8）；两个测试文件 = 主 Agent
    授权修复（核查项 8 已单独审）；其余改动均为任务工作区编排文件（progress/dispatch-
    context/.state/active-tasks/gate-events，非协议产出物）。`check-gate.py` 本任务 diff
    （+64 行）内无新增 [DESIGN_GAP]（:974 处 DESIGN_GAP 注释属 TAG0007 骨架步既有提交）；
    实现侧 §5 范围声明无 [SCOPE+] 成立。无越界文件。

## 阻塞 / 非阻塞问题

- 无阻塞（BLOCKER = 0）。
- 无非阻塞 DEBT 新增（[DESIGN_GAP] §3.1 已申报且落地一致，经核查项 3 收尾确认，不立新条）。

## 锁定决策

- P4 实现通过本评审（status: approved），可进入 P4 gate 判定（27 passed + 182 gate 回归
  + ruff 0 error + consistency 0 ERROR，口径见 P4-implementation.md §2）。
- 测试文件授权修复（主 Agent 定夺 2026-08-30）经本轮机械验证（断言行零改动）追认为
  合规修复，后续阶段不再追溯。
- 门槛 a/b 的 stderr 文案（"known-violations" / "登记"）与 P3 测试断言为契约对，
  后续任何一侧修改须同步评审。
