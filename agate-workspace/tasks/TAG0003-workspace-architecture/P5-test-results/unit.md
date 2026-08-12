---
phase: P5
task_id: TAG0003-workspace-architecture
type: test-results
parent: P2-design.md
agent: verifier
created: 2026-08-12
---

# TAG0003 — P5 技术验证结果

> 角色：verifier（P5 模式，只读验证，未修改任何 agate/ 文件）。
> 验证对象：worktree `agate/`（dev/workspace @ 9aaab53 P4 commit）。
> 命令来源：P2-design.md §5 `gate_commands.P5`（4 条全部执行，非子集）。
> 环境标记：`[PROD_NOT_TOUCHED]` 只读跑测试/检查，未接触生产环境，`~/.agate` 稳定版未动。

## 汇总

| 命令 | 结果 | exit |
|------|------|------|
| P5 全量 bats（sanity + unit + regression + integration） | ok=631 / not ok=0，failed=0 | 0 |
| P5_consistency（check-protocol-consistency.py） | 0 ERROR，CHECK 1-4/6-9 全 PASS | 0 |
| P5_shellcheck（-S warning） | 0 告警 / 0 错误（无输出） | 0 |
| P5_count（count-tests.sh） | 总计 625 用例，与 P4-review 基线一致，无漂移 | 0 |

**failed 计数：0**（预存失败：无；全部 4 条命令 exit 0）。

## P5 全量 bats（gate_commands.P5）

命令：`bats --formatter tap agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ 2>&1 | tail -30`

- 测试输出签名：plan `1..631`；`ok` 行计数 = 631；`not ok` 行计数 = 0。
- failed 计数 = 0。

末尾 30 行（tail -30）：

```
ok 602 IT_PT_BINARY.7 暂存 diff 含 [PROD_NOT_TOUCHED] 确认未接触（负向+描述）→ 不中止
ok 603 IT_PT_MENTION.1 正文句中提及 [PROD_TOUCHED]（非行首声明）→ 不误报（T090 修复）
ok 604 IT_P6_CODE.1 phase=P6，暂存 P6-evidence/ 下截图 → 不拦（证据文件例外）
ok 605 IT_P6_CODE.1b phase=P6，暂存 evidences/ 下截图 → 不拦（T090 白名单修复）
ok 606 IT_P6_CODE.2 phase=P6，暂存项目源码文件 → exit 1 硬拦截
ok 607 IT_P6_CODE.3 phase=P4，暂存源码文件 → 不拦（回归）
ok 608 IT_P6_CODE.4 phase=P5，暂存源码文件 → 不拦（回归）
ok 609 IT_P6_CODE.5 phase=P2，暂存源码文件 → WARNING 而非硬拦截（回归，现有行为不变）
ok 610 IT_RETREAT.1 agate-retreat-to.sh 在装了真实 hook 的仓库里，每一步都真的过 hook 校验
ok 611 IT_RETREAT.2 中途一步的 commit 被 hook 拒绝时，agate-retreat-to.sh 明确报告停在哪步且不继续
ok 612 IT_PT_T6.1 P8 dispatch-context 含 AGATE_CARD 注入块（[PROD_TOUCHED] 说明文本）→ 不误拦
ok 613 IT_PT_T6.2 任务产出文件含句中 [PROD_TOUCHED]（非 AGATE_CARD 块内）→ 不拦截（T090 修复）
ok 614 IT_PT_T6.3 任务产出文件含行首 [PROD_TOUCHED]（步骤1）→ 拦截（回归）
ok 615 IT_PT_T6.4 任务产出文件含 [PROD_NOT_TOUCHED]（负向声明）→ 不拦截（回归）
ok 616 IT_CHANGELOG_P54: P4 commit without CHANGELOG → no CHANGELOG WARNING
ok 617 IT_CHANGELOG_P54b: P8 commit without CHANGELOG → CHANGELOG WARNING
ok 618 IT_GATE_REAL.1: hook runs check-gate.sh and writes real .gate-result.json
ok 619 HOOK_EVIDENCE_WARNING: P6 截图触发低方差 WARNING → commit 不应被拦截（T086 修复）
ok 620 pre-commit hook: AGATE_ROOT 未设时自定位到脚本自身本体（worktree 支持，T086）
ok 621 pre-push hook: 新分支首次推送提示跳过检测
ok 622 pre-push hook: 大改动触发提示
ok 623 pre-push hook: 无 agate/*.md 改动时零匹配 → 不报整数表达式错误（T086 回归）
ok 624 SG.1 角色文件 protocol-alignment-review.md 存在且含必需 frontmatter
ok 625 SG.2 角色文件含 A1-A6 审查清单
ok 626 SG.3 角色文件含 NEEDS_HUMAN_REVIEW 闭环规则 + HUMAN_CONFIRMED 标记
ok 627 SG.4 SELF-GATE.md 含派发模板
ok 628 SG.5 SELF-GATE.md 含检查清单
ok 629 SG.6 CHECK 9 锚点表覆盖全部 11 个 gate 脚本
ok 630 SG.7 commit-msg-self-gate.sh 存在且可执行
ok 631 SG.8 SELF-GATE.md 含递归终止条件
```

`EXIT_CODE: 0`

## P5_consistency（补充命令 1）

命令：`python3 agate/scripts/check-protocol-consistency.py`

```
================================================================
  agate 协议结构一致性检查 (P3-1)
================================================================
  ✅ PASS  CHECK 1  YAML 代码块可解析
  ✅ PASS  CHECK 2  仓库内文件引用存在
  ✅ PASS  CHECK 3  协议文件无硬编码行号
  ✅ PASS  CHECK 4  gate_commands 键集合一致
  ✅ PASS  CHECK 6  LICENSE 与 gstack 归属
  ✅ PASS  CHECK 7  version badge 与 git tag
  ✅ PASS  CHECK 8  v0.6 关键词存在性
  ✅ PASS  CHECK 9  协议-脚本结构对齐
----------------------------------------------------------------

  🎉 全部检查通过，协议结构一致性无问题。
```

结果：**0 ERROR**（达标）。

`EXIT_CODE: 0`

## P5_shellcheck（补充命令 2）

命令：`shellcheck -S warning agate/scripts/*.sh`

结果：**0 输出 = 0 error / 0 warning**（达标）。

`EXIT_CODE: 0`

## P5_count（补充命令 3）

命令：`bash agate/tests/scripts/count-tests.sh`

```
=== 测试用例覆盖度自检 ===
  unit/agate-archive-stale-outputs.bats                7 个 @test
  unit/agate-capture-env-baseline.bats                15 个 @test
  unit/agate-card-inject.bats                          2 个 @test
  unit/agate-changelog-unreleased.bats                 2 个 @test
  unit/agate-evidence-consistency.bats                 2 个 @test
  unit/agate-extract-context.bats                     15 个 @test
  unit/agate-gate-missing-cmds.bats                    2 个 @test
  unit/agate-gate-p5-count.bats                        2 个 @test
  unit/agate-image-check.bats                          4 个 @test
  unit/agate-inject-card.bats                         11 个 @test
  unit/agate-json-get.bats                             8 个 @test
  unit/agate-md-field-get.bats                         6 个 @test
  unit/agate-migrate-workspace.bats                    9 个 @test
  unit/agate-next-card.bats                           20 个 @test
  unit/agate-read-p5-commands.bats                     4 个 @test
  unit/agate-render-dispatch-prompt.bats              16 个 @test
  unit/agate-retreat-state.bats                        3 个 @test
  unit/agate-retreat-to.bats                           5 个 @test
  unit/agate-state-get.bats                            6 个 @test
  unit/agate-state-yaml-check.bats                     3 个 @test
  unit/agate-vision-blocker.bats                       2 个 @test
  unit/agate-workspace-resolve.bats                    9 个 @test
  unit/check-changelog.bats                            8 个 @test
  unit/check-frontmatter.bats                         10 个 @test
  unit/check-gate.bats                               100 个 @test
  unit/check-gate-p1-review.bats                       9 个 @test
  unit/check-gate-p5-diff.bats                        13 个 @test
  unit/check-p6-evidence.bats                         28 个 @test
  unit/check-p6-format.bats                           14 个 @test
  unit/check-p6-provenance.bats                       36 个 @test
  unit/check-protocol-consistency.bats                 3 个 @test
  unit/check-pruning.bats                             29 个 @test
  unit/check-retrospective.bats                       10 个 @test
  unit/check-scope-resolved.bats                      10 个 @test
  unit/check-state-transition.bats                    30 个 @test
  unit/check-state-yaml.bats                           9 个 @test
  unit/check-tdd-red.bats                             38 个 @test
  unit/check-tdd-red-formatter.bats                   12 个 @test
  unit/ci-gate-backstop.bats                           8 个 @test
  unit/commit-msg-self-gate.bats                       4 个 @test
  unit/dispatch-context-warning.bats                   1 个 @test
  unit/install-hook.bats                               5 个 @test
  regression/v040-dotarchived-exclusion.bats           2 个 @test
  regression/v060-design-gap.bats                      4 个 @test
  regression/v060-p8-cached.bats                       3 个 @test
  regression/v060-p8-internal-only.bats                3 个 @test
  regression/v060-r4-cached.bats                       2 个 @test
  regression/v060-yaml-indent.bats                     3 个 @test
  integration/commit-msg-self-gate.bats                6 个 @test
  integration/consistency.bats                        11 个 @test
  integration/dispatch-context-card.bats               8 个 @test
  integration/pre-commit-hook.bats                    42 个 @test
  integration/pre-push-hook.bats                       3 个 @test
  integration/protocol-alignment-review.bats           8 个 @test
===
总计：625 个测试用例
```

结果：**总计 625**，与 P4-review 基线一致（基线 624 + MW.9 = 625，无漂移）。注：dispatch-context 客观信息里写的「基线 624」为 MW.9 加入前的快照；P4-review（approved）已确认 625 为预期基线。

`EXIT_CODE: 0`

## 结论

- gate_commands.P5 全部 4 条命令已执行：**全量 bats（631 ok / 0 failed，exit 0）+ consistency（0 ERROR）+ shellcheck（0）+ count-tests（625 无漂移）**。
- 未修改任何 agate/ 文件（只读验证）。
- 环境标记：`[PROD_NOT_TOUCHED]`。

`EXIT_CODE: 0`
