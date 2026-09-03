---
phase: P6
task_id: TAG0031
type: acceptance
parent: P5-verification.md
trace_id: TAG0031-P6-20260904
status: draft
created: 2026-09-04
agent: verifier
# ── v2.0 机器汇总 ──
pass: 15
fail: 0
ui_affected: false
---

# P6 验收报告 — TAG0031-debt-cleanup

[PROD_NOT_TOUCHED]（本次验收全部命令为本地 pytest / grep 只读操作，未接触 `~/.agate` 或生产服务）
[NO_NEED_CONFIRM]（无涉及数据删除/迁移等不可逆操作）

工作目录：`/home/kity/oclab/agateon/.worktrees/agate-TAG0031`
本任务 `ui_affected: false`，无 vision/截图证据要求，全部走 pytest 断言输出 + grep 日志类证据。
本任务未声明 `change_type: refactor`，走标准验收口径（非回归口径）。

按 dispatch-context 的 BDD↔测试映射，为每条 BDD 单独实跑对应 pytest 用例（`-v` 模式），输出保存到
独立证据文件 `P6-evidence/bdd-{NN}.log`；BDD-14 为非代码断言，用 grep 命令核对 debt 登记，输出存
`P6-evidence/bdd-14.log`。

## 逐条验收结果

- PASS BDD-1: compute_sha256 迁移到 agate_common 后，pack/install 两侧调用同一实现得到一致 hash 值，全仓仅 1 处定义（5 个用例全部 PASSED：文件哈希与 hashlib 一致、目录哈希按相对路径排序拼接、全仓仅 1 处定义、pack 侧 import 共享、install 侧 verify_checksums 使用共享实现）(P6-evidence/bdd-01.log)
- PASS BDD-2: hash 合并后 pack→install→卸载全流程无行为变化（回归），含 R1 pyyaml 引导前置校验缓解方案的 2 个机制细节用例（bootstrap 引导 + checksum 不匹配前置拒绝）(P6-evidence/bdd-02.log)
- PASS BDD-3: `agate/UPGRADING.md`/`agate/scripts/README.md` 均显式写出 checksum 防损坏、不防整包替换的信任边界说明（2 个用例 PASSED）(P6-evidence/bdd-03.log)
- PASS BDD-4: 卸载引用扫描命中深度/mtime 限流边界时，stderr 输出 WARNING 且不误判为可安全卸载 (P6-evidence/bdd-04.log)
- PASS BDD-5: 未命中限流边界时不产生 WARNING 噪音（边界流回归） (P6-evidence/bdd-05.log)
- PASS BDD-6: 四个原始用例（test_p2_6e/test_p2_52/test_p2_52b/test_p2_6f）在暂存区含无关文件场景下稳定 PASS，覆盖既有 TAG0024 隔离修复的显式回归 (P6-evidence/bdd-06.log)
- PASS BDD-7: DEBT0007 在 `debt/tech-debt.md` 登记条目 `status: closed`，含 `closed_at`/closure 说明，`evidence` 追加指向 TAG0024 commit e2357fc 与本任务 BDD-6 验证记录，格式与既有 DEBT0005/DEBT0006 closed 条目一致（断言测试 PASSED） (P6-evidence/bdd-07.log)
- PASS BDD-8: `gate_p4` CODE-MAP 路径改用 `agate_common.resolve_workspace`，标准两级嵌套场景解析结果与权威函数拼接 `agents/CODE-MAP.md` 逐字节一致，不再本地执行 dirname(dirname(...)) 路径算术 (P6-evidence/bdd-08.log)
- PASS BDD-9: 非标准两级嵌套场景（经 `.agate.env` `AGATE_WORKSPACE=` 覆盖）下 `gate_p4` 路径解析仍与 `resolve_workspace` 一致，不产出错误/不存在路径 (P6-evidence/bdd-09.log)
- PASS BDD-10: 自指场景下（P4-implementation.md 仅以说明性散文提及「## 新增文件核对表」字符串）判定为未满足，不再被子串 `in` 匹配误判为已满足 (P6-evidence/bdd-10.log)
- PASS BDD-11: 「## 新增文件核对表」标题独立成行真实存在时判定为已满足，不触发 WARNING（防止整行判定引入新假阳性） (P6-evidence/bdd-11.log)
- PASS BDD-12: 模拟 `agate_common` 不可导入时，`gate_p1`（read_rules_yaml）、`gate_p6`（count_p6_pass_fail）、`gate_p7`（count_p7_markers、count_code_map_lines）4 个消费分支均显式输出「安装破损：agate_common 不可导入」错误信息并 `return 1`，不再静默降级为通过（4 个子用例全部 PASSED，合并入本证据组） (P6-evidence/bdd-12.log)
- PASS BDD-13: `agate_common` 正常可导入时，`gate_p6`/`gate_p7` 新格式分支行为逐字节不变，fail-closed 改造未引入新假阳性拒绝（回归用例 PASSED） (P6-evidence/bdd-13.log)
- PASS BDD-14: `debt/tech-debt.md` 新增 DEBT0028（`dirname(dirname(...))` 类别 A 非本体 2 处实例）与 DEBT0029（`check-gate.py:881` gate_p2 骨架声明标题子串判定，风险高于 DEBT0017 本体）两条条目，均 `status: open`，evidence 指向本任务 P1「同类扫描」节第 3/4 小节结论，未遗留空白（grep 输出确认标题、id、status 字段） (P6-evidence/bdd-14.log)
- PASS BDD-15: DEBT0002/0003/0004/0016/0017/0018 六条 DEBT 登记条目 `status` 均由 `open` 改为 `closed`，各自追加 `closed_at`/closure 说明，`evidence` 追加指向对应 BDD 编号与实现 commit，登记格式与既有 DEBT0005/DEBT0006 closed 条目一致（与 BDD-7 共同覆盖任务标题声明的 7 条 DEBT） (P6-evidence/bdd-15.log)

## 交叉核对

15 条 BDD（BDD-1 至 BDD-15）逐条实跑，PASS=15，FAIL=0，与 P1-requirements.md 全部 BDD 编号一一对应，无遗漏、无重复。

## 与 P5 的区别说明

P5（`P5-test-results/unit.md`）验证的是"1435 passed, 2 skipped, 0 failed"这一技术事实（全量测试转绿）。
本次 P6 逐条为 15 条 BDD 单独重跑对应的具体断言用例（部分用例是 P5 全量套件的子集，但本次独立执行、
独立保存证据，而非复制 P5 汇总数字），确认的是"每条 BDD 描述的具体用户可观察行为是否真的做到"，
而非"测试套件整体是否全绿"。

## 自检

- P6-acceptance.md 存在且非空
- P6-evidence/ 目录存在，15 个证据文件（bdd-01.log ~ bdd-15.log）均非空、非 1 行文本充数（均含
  pytest 完整会话头 + 用例逐条结果 + exit code，或 grep 命中多行 yaml 字段上下文）
- 逐条 PASS/FAIL 结论与实际跑出的测试/grep 结果一致（15 条全部实测 PASSED / grep exit 0 命中）
- frontmatter `pass: 15` / `fail: 0` 与正文逐条统计一致

**Summary**: 15/15 PASS, 0 FAIL
