---
phase: P1
task_id: TAG0005-mechanism-fixes
type: review
parent: P1-requirements.md
trace_id: TAG0005-mechanism-fixes-P1-20260813
status: approved
created: 2026-08-13
agent: requirements-review
---

# P1 评审 — TAG0005-mechanism-fixes（复评轮）

## 评审范围与复核方法

对 analyst 修订后的 P1-requirements.md（16 条 BDD）复评，重点核对上轮两个阻塞项。全部代码/文档证据独立复核：
- `rg -n '>&2;\s*exit 0' agate/scripts/*.sh` 实测（全仓字面扫描）
- `agate/scripts/check-debt.sh` L21-30（依赖加载失败分支）、`agate/scripts/agate-capture-env-baseline.sh` L20-29（跳过语义三处）
- `agate/tests/README.md` L28-66 逐脚本计数表、`agate/tests/unit/agate-render-dispatch-prompt.bats`（17 @test）
- 三处 C8 表 + check-gate.sh P2/P5 + render 脚本 + count.py/read-p5 复核（上轮已过，本轮确认修订未破坏）

## 上轮阻塞项复核

1. **同类扫描证据与实测不符 + BDD-15 判定不精确**（已解决）：
   - §2 证据已更正为「全仓实测 4 处」`>&2;\s*exit 0`——独立实测确为 4 处：`check-debt.sh:26`（`source ... || { echo "GATE DEBT: 无法加载..." >&2; exit 0; }`，错误语义）+ `agate-capture-env-baseline.sh:23/26/28`（「跳过基线捕获」「非 git 仓库，跳过」，显式跳过语义）。修订版证据与实测一致。
   - `check-debt.sh:26` 已明确裁定「同同类，纳入修复」并入 BDD-16，理由充分（依赖加载失败是硬失败，非「有意跳过」分支；静默 exit 0 会让回退覆盖比对被无声跳过）。
   - capture-env-baseline 三处裁定「非同类的有意跳过」成立（脚本头注释声明 best-effort、消息含「跳过」语义、不写文件由 P5 graceful degradation 兜底）。
2. **I8 引用路径已归档**（已解决）：I8 已改指 **agate/tests/README.md 逐脚本计数表**（实时路径）。实测 README L33 `agate-render-dispatch-prompt.sh = 16`，bats 实际 17 @test，1 漂移已存在，与 I8 描述一致；「新增用例后按实际数同步」正确。count-tests.sh L22 陈旧引用标注为 pre-existing、明确不纳入修复范围（避免范围蔓延），处理合理。

## BDD 评审

- BDD-1（RM-AG0010 C8 补 backend P2 评审，三处表同步）：通过。三处 C8 表实测均无 backend P2 触发条目，Then 可二值判定（grep 三表 backend 行含 P2 插入阶段条目）。覆盖维度：多端（跨文件一致性）✓、边界（backend 域非 high）✓。
- BDD-2（check-gate.sh P2 分支不改）：通过。L157-161 无条件要求 P2-review.md 存在+approved+agent≠main，锁定「C8 补评审、非 gate 豁免」方向。覆盖维度：兼容 ✓。
- BDD-3（P5 计数区分主/辅）：通过。count.py L19 `^  (P5\w*):` 合并计数与 Given 一致；Then 描述用户可观察输出形态，不绑定实现格式（P2 定）。覆盖维度：数据 ✓、边界（多键）✓。
- BDD-4（P5 多命令 WARNING 文案区分主/辅）：通过。check-gate.sh L253-257 现输出「N 个 gate_commands.P5 命令」，Then 可二值判定。覆盖维度：数据 ✓、多端（主 Agent 信息可读性）✓。
- BDD-5（仅主命令不输出 WARNING，现状保持）：通过。`-gt 1` 判定下单键不触发，回归守卫合理。覆盖维度：边界（零辅助）✓。
- BDD-6（read-p5-commands 执行枚举不变）：通过。read-p5 L26 为执行枚举（主+辅全输出），I5 回归守卫定位正确。覆盖维度：多端（agate-capture-env-baseline.sh 契约）✓、兼容 ✓。
- BDD-7（执行角色派发 prompt 不含 Review 指令）：通过。render L78 main_block 现无条件含模板 L9-13，Then 可二值判定。以被修复组件为观察单元，非实现绑定。覆盖维度：数据 ✓。
- BDD-8（评审角色派发 prompt 含 Review 指令完整语义）：通过。与模板语义（draft→approved/rejected/needs-revision）对照一致。覆盖维度：数据 ✓、兼容 ✓。
- BDD-9（协议内仅模板一处）：通过。全仓 grep「Review 角色特别指令」仅 dispatch-prompt.md L9-13 一处；docs/plans、archived 为历史快照且排除规则在 Then 已声明。覆盖维度：边界 ✓。
- BDD-10（角色文件不存在 → exit 2 + stderr）：通过。render L66-69 实测 exit 2 + stderr 报错。覆盖维度：边界 ✓、兼容 ✓。
- BDD-11（该行为有 bats 回归锁定）：通过。bats 现 17 @test，无「角色不存在 exit 2」用例，补测试必要性成立；可 grep 新用例断言判定。覆盖维度：数据 ✓。
- BDD-12（空返回策略含「自动重试一次」）：通过。dispatch-protocol.md L105-135 现全手动，Then 要求明确自动重试一次动作，可 grep 判定。覆盖维度：边界 ✓、兼容（自动重试后才进入既有流程）✓。
- BDD-13（短会话 <1min 异常告警）：通过。L128 已有派发耗时弱信号，增量基于该信号扩展；阈值 <1min 可 grep 判定。覆盖维度：边界 ✓、数据 ✓。
- BDD-14（自动重试不改变 retry 上限/PAUSED 规则）：通过。对改造前后 dispatch-protocol.md 对应节 diff 判定，可二值。覆盖维度：兼容 ✓。
- BDD-15（全仓 scripts「stderr 报错后 exit 0」仅剩显式跳过语义，同类扫描守卫）：通过。判定命令 `rg -n '>&2;\s*exit 0' agate/scripts/*.sh` 精确字面扫描（实测 4 处，无跨行变体），Then 区分「跳过语义」（消息含「跳过/不影响推进」，如 capture-env-baseline 三处）与「错误语义」（含「无法加载/缺失/失败」→ FAIL）。可二值判定；修复后 check-debt.sh:26 不再命中，剩余命中均为跳过语义 → PASS。覆盖维度：边界 ✓、兼容（同类扫描守卫）✓。
- BDD-16（check-debt.sh --retreat-coverage 依赖加载失败不再静默 exit 0）：通过。抽查 check-debt.sh L21-30 确认 L26 `source ... || { echo "GATE DEBT: 无法加载..." >&2; exit 0; }` 与 Given 一致；Then 要求非零 exit + stderr 报错，「有意跳过」分支（如无 retreat 提交 L35-37）仍 exit 0 已显式排除。可二值判定（构造 resolver 缺失/加载失败场景断言非零）。与 BDD-15 语义一致：BDD-16 修复后 check-debt.sh:26 不再命中 BDD-15 的字面模式，两守卫不矛盾。覆盖维度：边界（依赖缺失）✓、兼容（有意跳过分支不受损）✓。

## 隐含需求覆盖

- 数据维度：覆盖——I4（WARNING 文案改动同步 G5_CMD.1/.5 断言）、I5（read-p5 不改仅回归守卫）、I6（count 输出格式变化同步消费方 L253）。
- 前端维度：N/A（协议/脚本修复无 UI）；主 Agent 信息可读性由 BDD-4/13 覆盖。
- 多端维度：覆盖——I1（三处 C8 表同步）、I7（assets 模板与内联模板语义一致）、I2（评审角色名留 P2 选型，避免提前锁定设计空间）。
- 边界维度：覆盖——I9（自动重试与既有 retry/PAUSED 衔接）、I10（复用派发耗时弱信号）、BDD-5/10/13/15/16 边界场景。
- 兼容维度：覆盖——I3（gate P2 分支不改）、I14（714 bats 回归底线）、BDD-5/6/14 现状保持守卫；I8 修订后指向实时计数表，兼容文档漂移治理。

## 裁剪评审

- phases: [P1..P8] 无裁剪：合理。5 处修复各有 P2 设计选型（C8 表评审角色名、count 输出格式、条件注入位置、check-debt 修复方式、自动重试语义），P7 需跨文件一致性，全保留必要。
- risk_level: medium：合理。协议本体脚本+文档（SELF-GATE）但均为既有缺陷修复，无安全/数据迁移暴露面。
- capability_requirements：available 判定正确（bats 1.10 / py3.12+pyyaml / shellcheck 均可用），无 GAP、无 supplementable。

## 非阻塞观察

- BDD-16 Given 含「缺失或 source 加载失败」两分支：当前 check-debt.sh 对「文件缺失」走 L27-29 else 分支（消息含「跳过」语义、exit 0）。按 BDD-16 Then「不静默当作成功跳过」，P2/P4 修复时须**同时覆盖 L26 与 L27-29 两分支**（统一按依赖不可用=硬失败处理），而非只改 L26；此点 BDD 语义自洽（Given→Then 对两分支均要求非零），留给 P2 落地，不阻塞 P1。
- BDD-15 Then 依赖对命中行 stderr 消息文本的语义判定（跳过 vs 错误），判定需读取消息文本而非纯 exit code，但判定结果二值、标准在 Then 中显式给出，可执行。

## 结论

**Status: approved**。上轮两个阻塞项均已解决：同类扫描证据已更正（4 处 `>&2;\s*exit 0` 实测一致）、check-debt.sh:26 裁定同同类纳入 BDD-16、BDD-15 收窄为可 grep 二值判定（跳过/错误语义二选一）；I8 已改指 agate/tests/README.md 实时计数表。BDD-1..16 连续（`#### BDD-NN:` 标准格式）、无中间态、无行首 PASS/FAIL；BDD-15 与 BDD-16 语义一致不矛盾；BDD-1..14 未被修订破坏（内容与上轮通过版一致）。

覆盖维度标注：数据✓ 前端(N/A) 多端✓ 边界✓ 兼容✓（详见各 BDD 条目）。
