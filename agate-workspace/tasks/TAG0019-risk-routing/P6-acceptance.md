---
phase: P6
task_id: TAG0019
type: acceptance
parent: P5-verification.md
trace_id: TAG0019-P6-20260821
status: draft
created: 2026-08-21
agent: verifier
# ── v2.0 机器汇总 ──
pass: 15
fail: 0
ui_affected: false
---

# TAG0019 风险分路由（ceremony routing，RM-AG0031）— P6 验收报告

> 状态标记：`[PROD_NOT_TOUCHED]`；非 UI 任务（P2 `ui_affected: false`）。
> 验收口径：P1-requirements.md 15 条 BDD 逐条实跑，仅 PASS/FAIL 二值。验证环境：worktree
> `/home/kity/oclab/agate/.worktrees/agate-TAG0019` + 受控 fixture git 仓库（`/home/kity/oclab/agate/.ptmp-scratch/p6`，
> 可写 basetemp）；所有命令外层 timeout；单步串行。证据均落在 `P6-evidence/`，被对应 PASS 行引用。
> 引用 P5 证据说明：本任务是功能任务（非 refactor），BDD 证据全部为本轮实测产出；P5 全量套件结果
> （1099 passed / 1 环境前提 I1）作为背景已读，未在本报告作"复用"声明。

## 验证方法

对每条 BDD：构造该 BDD Given 所述的暂存区/声明形态（受控 git 仓库 fixture），实跑对应脚本
（`agate-risk-score.py` / `check-routing.py` / `check-pruning.py` / `check-frontmatter.py` /
`agate-md-field-get.py` / `check-platform-assumptions.py` / `check-protocol-consistency.py`），
以 exit code + 实际输出行判定，输出落盘 P6-evidence/。文档断言类 BDD（11/12/14）以目标文件
条文 grep 实取为据。

## BDD 逐条结果

- PASS BDD-1: 算分脚本输出三要素——对真实形状 repo（暂存 agate/scripts/*.py + agate/*.md + tests）实跑 `agate-risk-score.py`，输出同时含 `risk_score: 10`（数值）、`tier: full`（三值之一）、四条逐信号证据行（file-type/sensitive-path/change-size/impact 均带证据文本），且证据与暂存区 diff 内容一致（"agate/phase-cards/P1-requirements.md 属协议本体/gate 逻辑"确为该暂存文件）；git_ok: true；BDD 映射测试组同步佐证（test_agate_risk_score.py 全绿）；主验证日志见 test-output.log (bdd-1-2-risk-score.log, pytest-bdd-mapped.log, test-output.log)
- PASS BDD-2: 文件类型信号分级——A 类（`agate/scripts/foo.py`）file-type: high，B 类（`agate/tests/unit/test_foo.py`）file-type: low，A 信号位评分 3 严格高于 B 的 1（分级可区分）(bdd-1-2-risk-score.log, bdd-2-3-risk-score.log)
- PASS BDD-3: 敏感路径信号与 security 域映射——`auth/login.py` 实跑 sensitive-path: high（命中关键词 auth）且输出 `domain: security` + `domain-markers: [security]`；`src/hello.py` 无关键词则无 security 标注，无双标/漏标 (bdd-2-3-risk-score.log)
- PASS BDD-4: 改动规模信号与 pruning 口径一致——6 个 src 文件暂存：change-size: high（source files=6 > 5），3 个文件：low；同 repo 对拍：check-routing 复用同源 `_staged_source_count` 与 check-pruning 同为 6（>5 口径一致），check-pruning 裁剪 P7 报"实际=6"拦截（exit 1）、check-routing 报"声明薄于算分 tier=full"拦截（exit 1），两处判定不矛盾 (bdd-4-5-risk-score.log)
- PASS BDD-5: 域映射与影响面信号——`core_logic.py` 被 `consumer.py` import 引用：impact: high（module core_logic 被其他文件反向引用）；`isolated.py` 无引用：impact: low（升级/不升级二值可判）；P1 声明 `domains: [security]` 时输出 `domain-markers: [security]` 域映射标注 (bdd-4-5-risk-score.log)
- PASS BDD-6: ceremony 字段合法值声明——frontmatter schema：`ceremony: thin/standard/full` 全部通过（exit 0 无输出），`ceremony: light` 被拦（"非法值 'light'（合法值: thin, standard, full）" exit 1）；字段读取：`agate-md-field-get.py ceremony` 实读得 `thin`（exit 0）；check-routing 兜底：standard/full exit 0、light exit 1；corresponding 单测组（test_check_routing / test_check_frontmatter / test_agate_md_field_get）重跑全绿 (bdd-6-frontmatter.log, bdd-6-7-extra.log, bdd-6-9-routing.log, pytest-bdd-mapped.log)
- PASS BDD-7: fail-closed——thin 四要素全齐（ceremony: thin + coupling_checklist 流式 + 跳过风险: + phases 含 P5/P6）exit 0；缺 coupling_checklist / 缺 跳过风险: / 缺 P5/P6 三种情形均 exit 1 且回退 standard；P5/P6 情形 check-pruning 检查 3（P6 不可裁）+ 检查 5（P5 不可裁）同样拦截（双闸兜底）；算分异常分支实测：`GIT_DIR=/nonexistent` 探针 → git_ok: false + thin → exit 1（fail-closed，不静默放行）(bdd-6-9-routing.log, bdd-6-7-extra.log)
- PASS BDD-8: fail-closed——frontmatter 无 ceremony 字段（存量/新任务）：check-routing exit 0，按 standard 处理不拦截（向后兼容）(bdd-6-9-routing.log)
- PASS BDD-9: 声明 vs 算分单向 fail-closed——声明 `ceremony: thin` 但算分 tier=standard（src 类暂存）→ exit 1 拦截（"声明薄于算分，回退 standard"）；反向（算分 thin 而声明 standard，更保守）→ exit 0 不拦截；拦截方向与 fail-closed 语义一致 (bdd-6-9-routing.log)
- PASS BDD-10: 复用不重造——同一 fixture 对拍：check-routing 与 check-pruning 判定一致（rt_thin_ok 双 exit 0；rt_no_p1 双 exit 2）；源码核查：check-routing 第 56-59 行经 importlib 加载 check-pruning 复用 `_staged_source_count`/`_md_field`/`_read_p1`，无第二份实现 (bdd-10-same-source.log)
- PASS BDD-11: requirements-review 审声明职责——requirements-review.md 检查清单实取：第 53 行「审声明（风险分级/裁剪声明 vs diff 证据）」，第 56 行「声明与实际不一致时结论必须为 needs-revision 或 rejected（不得 approved）」，第 71/91-93 行含逐信号核对记录格式与 `ceremony: full → phases 含 P7` 核对项；职责显式存在 (bdd-11-12-doc-assertions.log)
- PASS BDD-12: M3 验收锚度量协议——P1 卡「M3 验收锚度量协议（BDD-12，机制文档供提取）」条文实取：四要素齐备——①评审轮数指标（P2/P4 派发的 LLM 评审 subagent 轮数含重试轮）②真实发现数指标（排除非阻塞建议与机械可抓项）③TAG0018 基线值（4 场 LLM 评审 ≈0 净收益：17 条非阻塞 + 1 条真实发现且机械检查可抓）④不达标决策规则（「LLM 评审真实发现 ≈ 0 且机械 gate 已覆盖 → 回滚 standard」）(bdd-11-12-doc-assertions.log)
- PASS BDD-13: 平台假设零命中——`check-platform-assumptions.py` 对变更文件集（agate-risk-score.py / check-routing.py + 5 个测试文件）重跑 R1-R5 扫描 0 命中（exit 0）；静态核查：新脚本 git 全经 `agate_common.run_git` 通道、路径 `.replace("\\","/")` 归一、`rstrip("\r")` CRLF 鲁棒，无裸路径/裸解释器/字面 /tmp (bdd-13-platform.log)
- PASS BDD-14: full 档强制评审与 P7 不可裁——四处消费点条文实取：role-system.md:63（plan-eng-review 必须派发 P2 + cso security 域 + P7 不可裁）、review-mapping.md:24、P2-design.md:191（plan-eng-review 硬规则 + cso + P7 不可裁）、P4-implementation.md:95，均含 full 档（tier=full 或 ceremony: full）强制项；requirements-review 核对项含 `ceremony: full → phases 含 P7` (bdd-14-doc-assertions.log)
- PASS BDD-15: 消费点文档同步防漂移——`check-protocol-consistency.py --strict-errors-only --root=worktree` 重跑：0 ERROR（318 WARNING，与 P5 结果一致），CHECK 9 协议-脚本结构对齐 PASS（check-routing.py 已入锚点表）；具名消费点核查：scripts/README.md:37-38（两脚本工具清单）、tests/README.md:32-33（用例映射 11/13）、agate-summary.py:46-47（_DRIFT_SCRIPTS）、WORKFLOW.md:321（gate 表 2.7.1 check-routing 行）、pre-commit-gate.py:338-343（2j check-pruning 与 2j.1 check-routing 并列挂载）均同步反映新机制 (bdd-15-consistency.log)

## 附注（观察记录，不构成 FAIL）

- **dispatch-protocol.md:931 遗留旧行**：P1 评审检查项清单仍为「risk_level 是否与实际风险匹配」单句，
  未如 P2 §2.4 所列升级为「风险分级/裁剪声明 vs diff 证据」对拍行。判据评估：BDD-11 的 Given/When/Then
  判据对象是 requirements-review.md 检查清单与评审产出（已含审声明核对项 + needs-revision/rejected 规则，
  本报告 PASS 行已证）；dispatch-protocol.md 该清单为派发 checklist，其权威性引用角色文件
  （dispatch-protocol.md:927 引 `requirements-review` 角色文件）；check-protocol-consistency 未将其视为
  必须同步的锚点（BDD-15 具名消费点均同步）。故不标 FAIL，如实记录供主 Agent 知悉——如需将该清单行
  升级，属 P7 一致性可覆盖的文档同步收尾项。
- **P5 遗留环境前提 I1**（非本任务缺陷）：`test_bdd_7_thin_score_anomaly_git_ok_false_exit_1` 在沙箱
  必然失败（可写 basetemp 全在 git 仓库内 → run_git 必成功）；其目标行为（git_ok:false + thin → exit 1）
  已由 `GIT_DIR=/nonexistent` 探针在本验收中实测通过（见 BDD-7 PASS 行证据）。
- **其他一致性 WARNING（318 条）**为存量叙事文件引用与历史脚本名引用告警，非本任务引入
  （P5 记录同样 318 WARNING），不阻塞。

## Evidence 清单（P6-evidence/，全部被 PASS 行引用）

- test-output.log（主验证日志，13 个证据文件汇总）— 被小结引用不单独计
- bdd-1-2-risk-score.log / bdd-2-3-risk-score.log / bdd-4-5-risk-score.log（BDD-1..5）
- bdd-6-9-routing.log / bdd-6-7-extra.log / bdd-6-frontmatter.log（BDD-6..9）
- bdd-10-same-source.log（BDD-10）
- bdd-11-12-doc-assertions.log（BDD-11/12）
- bdd-13-platform.log（BDD-13）
- bdd-14-doc-assertions.log（BDD-14）
- bdd-15-consistency.log（BDD-15）
- pytest-bdd-mapped.log（BDD 映射测试重跑：88 passed / 1 deselected，佐证 BDD-1..10）

**Summary**: 15/15 PASS，0 FAIL（BDD 验收通过候选——最终 gate 判定权在主 Agent）