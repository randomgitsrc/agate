---
phase: P2
task_id: TAG0008
type: review
parent: P2-design.md
trace_id: TAG0008-P2R-20260816
status: approved
created: 2026-08-16
agent: plan-eng-review
---

# P2 方案评审：agate 版本管理机制（v1）

> 评审对象：P2-design.md（308 行，candidate_count=2，dispatch_plan static-batch 3 批）。
> 基线核对：P1-requirements.md（31 BDD + 影响面表 2.1/2.2/2.3 + I-1~I-16）、P0-brief.md、AGENTS.md。
> 代码核实：agate_common.py / install-hook.py / pre-commit-gate.sh / agate-inject-card.py / agate-next-card.py /
> agate-render-dispatch-prompt.py / agate-summary.py / check-protocol-consistency.py / ci-gate-backstop.py /
> integration/test_pre_commit_hook.py / 归档设计稿 §8。**只读评审，未改任何 worktree 文件。**

## 评审结论

**Status: approved（阻塞问题 0 个）**

方案整体成立：四层解析语义（§4.1）、hook 解析入口（§4.3）、3 脚本归口决策（§4.4）、install/uninstall（§4.5）、
summary（§4.6）、离线闭环（§4.7）与 P1 的 31 BDD 逐条可对账；dispatch_plan（§8）符合 high 复杂度硬规则；
minimal_validation（§7）3 项 confirmed 支撑离线/幂等关键假设。以下非阻塞意见为 P3/P4 落地前须钉死的
契约细节，不改变方案方向。

---

## 关键技术决策点核验（dispatch-context 5 项）

1. **§4.4 3 个内联 `_agate_root` 脚本归口 agate_common**——核实通过。
   - 代码核实：3 脚本当前均为内联解析（agate-inject-card.py:28-33 `_agate_root`；agate-next-card.py:35、
     agate-render-dispatch-prompt.py:32 `_resolve_agate_root`），grep 确认三者**零 `import agate_common`**，
     与设计 §4.4 断言一致。
   - agate_common.py:27-31 顶部 `import yaml` 失败即 exit 1（fail-closed）已核实。
   - 归口引入 pyyaml 依赖：**判定可接受**。orchestrator 派发链路（check-gate/state 读取）全程依赖 pyyaml，
     3 脚本运行场景不会缺 pyyaml；且依赖失败是 exit 1 显式报错（fail-closed），非静默降级。备选"保留内联"
     不采纳理由充分（I-5 解析入口分叉风险）。**结论：归口方案成立**，非阻塞项见「架构问题（非阻塞）5/8」。

2. **§4.3 resolve-entry 设计（install-hook 装固定入口、运行时读 .agate-version、Windows 复制模式 .agate-root 恢复）**
   ——方向正确，但有一处**机制表述矛盾**需在 P3 前钉死：
   - §4.3 bullet 1 说 install-hook 把 resolve-entry.py 装为 `.git/hooks/{pre-commit,...}`；bullet 3 又说
     "3 个 hook 薄壳 `exec ... resolve-entry.py`"。二者二选一。§9 已裁定"延续 TAG0010 既有薄壳结构，
     仅改 exec 目标为 resolve-entry"——即**薄壳保留、exec 目标变更**，bullet 1 是松散表述。
   - 建议 P4 明确：install-hook 仍按现有契约（argv[1] > env > ~/.agate，install-hook.py:87）装 .sh 薄壳；
     薄壳自定位后 exec `resolve-entry.py $(basename $0) "$@"`；resolve-entry 内置 gate-name→gate py 映射
     （pre-commit→pre-commit-gate.py / commit-msg→commit-msg-self-gate.py / pre-push→pre-push-gate.py，
     含 `.sh` 后缀与直接调用场景归一化）。
   - BDD-15 判定措辞"指向 resolve-entry"按字面在薄壳方案下不成立（hook 指向薄壳），测试应断言
     **"hook 固定入口执行链经 resolve-entry、不直接指向具体版本 gate py"**（负向断言保持成立）。
   - Windows 复制模式：薄壳 .agate-root 恢复（pre-commit-gate.sh:6-9 既有分支）+ resolve-entry 内
     resolve_agate_root 的 .agate-root 分支双保险，design §4.3 已覆盖；integration/test_pre_commit_hook.py:1351
     bdd-19 用例已核实存在，改造后回归基线明确。

3. **§4.5 uninstall 引用保护扫描（深度/mtime 限流）**——方向可接受，但**限流参数与"引用即保护"存在静默漏保护风险**：
   - BDD-6（P1:192-195）的保障目标是"被引用的版本永不清理"（归档设计稿 §8.3）。若 mtime/深度限流漏扫
     "老但有效"的项目引用 → 误删被锁版本（security 域，灾难场景）。
   - 建议：扫描默认**穷尽**（$HOME 下按 git 仓库边界剪枝找 `.agate-version`），不设 mtime 限流；或限流生效时
     降级为"无法确认无引用 → 拒绝卸载 + 提示 `--force` 显式覆盖"。P3 须补 bounded-scan 边角用例
     （见「测试缺口 3」）。这是非阻塞契约细节，不改方向——设计 intent（§4.5 + BDD-6）正确。

4. **BDD-30 legacy 布局兜底（无 current/latest 时软链目标 = AGATE_ROOT）**——核实通过，P4 歧义已消除。
   - §4.1 layer 4 与 BDD-30（P1:323-326）完全对齐：legacy 布局下无 current/latest 指针 → 软链目标直接为
     AGATE_ROOT。层序（env → 项目声明 → current → latest → legacy）与 P1 影响面表 2.1 结论 4（agate_common
     resolve 做加法）一致。
   - 存量用户不重装 hook 即不触发新解析（旧薄壳自定位旧 checkout 直连 gate py），BDD-30 成立。
   - 备注（非阻塞）：legacy 用户若**重装 hook 但未迁移**，新薄壳定位到旧 checkout 会找不到 resolve-entry.py
     → fail-closed 阻断 commit。属"升级引导期可接受状态"，UPGRADING.md 应写明迁移顺序。

5. **dispatch_plan 三批依赖声明**——核实通过。
   - static-batch 3 批（resolve-chain / install / offline，均 high），3 ≤ parallel_limit 3 ✓；每批含 id+complexity ✓。
   - high 复杂度 → 必须拆批 ✓；§8.3 显式声明"install/offline 依赖 resolve-chain 的 agate_common 语义"，
     并给出共享文件后处理规则（"先跑 resolve-chain 再并跑其余 / 或主 Agent 统一 merge"）——符合
     dispatch-protocol 并行规则；BDD 全局编号无包归属重复 ✓（agate 单包）。
   - 生效并发 2（resolve-chain 串行先行），不超 parallel_limit；编排可执行。

---

## 架构问题（阻塞级）

- 无。

## 架构问题（非阻塞）

1. **§4.3 hook 安装机制双重表述**（bullet 1 vs bullet 3 vs §9）：以 §9 为准（薄壳保留、仅改 exec 目标），
   但 bullet 1 与 BDD-15 措辞需同步修订，否则 P3 test-designer / P4 implementer 对"装 resolve-entry 本体
   还是装薄壳"可能分叉。建议：修订 §4.3 bullet 1 + BDD-15 判定措辞（见决策点 2）。
2. **薄壳 exec 定位 resolve-entry 的 env 污染**：新薄壳公式 `exec $PY $AGATE_ROOT/scripts/resolve-entry.py`
   中 $AGATE_ROOT 含 env 覆盖（pre-commit-gate.sh:5 既有语义）。env 指向不含 resolve-entry 的自定义根时
   薄壳 fail-closed 阻断。当前集成测试（AGATE_ROOT=checkout，checkout 含新脚本）不受影响，但契约应明确：
   **resolve-entry 的位置用 readlink 自定位（薄壳自身上溯），AGATE_ROOT env 只进 resolve_agate_root 第 1 层**
   （BDD-12 语义），不进薄壳定位。
3. **resolve-entry exec gate py 前应 export AGATE_ROOT=<resolved>**：避免 gate py 二次解析。若二次解析，
   在 cwd/声明与 resolve 时刻不一致时可能与 resolve-entry 结果分叉，且 BDD-12 env 覆盖语义在 exec 链上
   应保持单调。建议 resolve-entry 在 exec 前 `os.environ["AGATE_ROOT"] = resolved_root`。
4. **uninstall 引用保护 mtime 限流风险**：见决策点 3。建议穷尽扫描或限流时 fail-closed + `--force` 兜底。
5. **files_to_read 漏列 2 个同构归口改造文件**：§4.4 归口对象共 3 个脚本，但 files_to_read（§5）只列
   agate-inject-card.py:28-33。agate-next-card.py:35 / agate-render-dispatch-prompt.py:32 同为内联解析改造
   目标（P1 影响面表 2.1 已列），P4 仅凭 files_to_read 导航会漏改。建议补入。
6. **install.sh 形态未定**（§1.2 "作为 agate-install 底层或替换"）→ P4 歧义。建议明确：install.sh 兼容保留
   （软链 + git pull 升级路径不动），agate-install 为新路径，两者并存不互相调用；并声明影响面 2.2 的
   verifier.md / P6-acceptance.md / worktree-dogfooding-guide.md 3 个复核项结论为"无需改"（AGATE_ROOT
   env 语义未变）。
7. **resolve-entry 完全失败（无 current/latest/legacy 可用 root）的退出码未定义**：按薄壳既有 fail-closed
   step 4（pre-commit-gate.sh:18-20 exit 1 阻断）应非 0 阻断，但 §4.1 只写"回退 current（绝不静默禁用）"，
   未覆盖"current 本身不可用"终态。建议显式写死（exit 非 0，hook 阻断 commit），并补测试（见「测试缺口 1」）。
8. **归口后 3 个派发脚本解析变为 cwd 依赖**：resolve_agate_root 扩展后 layer 2 按 cwd 向上找 `.agate-version`
   （§4.1），3 个派发脚本从"安装位置依赖"变为"cwd 依赖"——同一脚本在不同目录运行可能解析到不同版本。
   对 orchestrator 派发语境这是项目级隔离的预期行为，但属行为变化，P7 一致性检查时应核文档叙述。
   （§4.1 layer 2 "cwd（或脚本所在项目根）"双表述建议统一为 cwd——BDD-9/10/20 已钉 cwd 语义。）

## 测试缺口

1. **resolve 完全失败 fail-closed 用例缺失**：BDD-13/14 只覆盖 current 可解析的回退场景，未覆盖
   "无 current/latest/legacy、声明未装"终态 → hook 应 exit 非 0 阻断（对应薄壳既有 fail-closed 语义）。
   P3 应在 test_agate_version_resolve.py 补该终态用例。
2. **BDD-16 项目 A/B 互不干扰的集成用例归属未指定**：设计 §8.4 完成标志 2 有场景，但未落测试文件。
   建议 P3 在 integration/ 下建 A/B 双仓库 + 双版本目录 + 双 hook 用例，验证各自跑对应版本 gate。
3. **uninstall 引用保护 bounded-scan 边角**：BDD-6 只测正常深度引用；"引用位于扫描深度/mtime 边界外"
   的行为（漏扫→误删 or 限流→拒绝）无 BDD 覆盖。P3 补边角用例（若采用"限流即拒绝+--force"方案，
   则断言边界外引用仍阻断卸载）。
4. **P5_unit 定向列表漏离线测试文件**：gate_commands.P5_unit（§3.2）只列 4 个 unit 文件，pack-offline /
   install-offline 测试未列入（全量 P5 会覆盖，但定向跑 P5_unit 时离线相关测试不触发）。建议补入或
   注明"离线测试依赖全量 P5"。
5. **BDD-31 验证手段未落测试**：gate 判定逻辑未改靠 P7 一致性 + git log diff 判定（§8.4 完成标志 7），
   非 pytest。P7 前主 Agent 应明确此验收的执行动作（git log 对照 + check-protocol-consistency 0 ERROR）。

## 锁定决策

- **方案 A（resolve-entry 固定入口 + 版本目录 + 纯指针）锁定**（§2.1）；候选 B 否决理由结构性成立
  （3 份重复解析 DRY 违反 + sh 违背 Python 路线 + I-5 解析入口分叉 + 无法复用为库），§2.3 诚实标注
  "明显更差的陪衬"，理由自洽。candidate_count=2 ✓。
- **3 个派发脚本统一归口 agate_common.resolve_agate_root**（§4.4）：pyyaml 依赖引入经评估可接受
  （orchestrator 链路本就依赖 + fail-closed exit 1 + 已核实 3 脚本当前零 agate_common import，为纯加法）。
- **四层解析语义锁定**（§4.1）：env 最高 → 项目声明（cwd 向上找 .agate-version）→ current/latest →
  legacy 软链目标兜底（BDD-30，P4 歧义已消除）。
- **dispatch_plan static-batch 3 批锁定**（§8）：resolve-chain 先行，install/offline 依赖其 agate_common
  语义，共享文件后处理规则已声明，符合 high 复杂度硬规则。
- **minimal_validation 3 项 confirmed**（§7）：worktree add tag ✓ / 重复 add exit 128 → BDD-3 幂等须程序
  预判 ✓ / pip download --platform 按平台拉 wheel ✓ / sha256 64-hex ✓ → 离线链路与幂等关键假设成立。
- **红线确认**（§1.4）：gate 判定逻辑不改（BDD-31）；agate_common 既有函数只做加法；3 hook 保留 sh 薄壳形态。

## 结论

无阻塞问题，status: **approved**。8 项非阻塞契约澄清 + 5 项测试缺口须在 P3 测试设计与 P4 实现中钉死
（以本文件架构问题编号为准），不改变方案方向与 dispatch_plan。
