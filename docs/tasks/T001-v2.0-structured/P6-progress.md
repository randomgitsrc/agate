# P6 验收进度追踪（verifier subagent 分阶段落盘）

## 完成

- 已读：verifier.md 角色定义、P6-dispatch-context-verifier.md 派发指引、P1-requirements.md（28 BDD）、
  P2-design.md §9/§10、P3-test-cases.md（BDD→测试映射）、P4-implementation.md（7 处 DESIGN_GAP）、
  P5-test-results/unit.md（600/600 全量 TAP）、task-files.md 模板。
- 28 条 BDD 逐条验收：对有 P5 测试覆盖的引用 `ok N` 行 + 摘录断言意义；对无独立断言或需强化确认的
  BDD（2/4/5/6/7/9/10/11/12/13/14/15/16/18/19/20/21/22/23/24/25/26/27/28）独立重跑真实命令复现，
  证据写入 P6-evidence/bdd-01.md..bdd-28.md（29 个文件，均含实质命令输出/复现步骤，无 1 行充数）。
- 自查步骤（按派发指引第 10 条执行 `bash ~/.agate/scripts/check-p6-format.sh --fix ...`）意外暴露一个
  严重、100% 可复现的真实缺陷：check-p6-format.sh 的 --fix 模式会破坏 P6-acceptance.md 自身合法
  frontmatter 的 pass:/fail: 字段（产出非法 YAML），且该脚本被 pre-commit-gate.sh 无条件自动调用、
  发生在 frontmatter schema 校验之后不会被重新校验。已确认此 sed 逻辑与 ~/.agate（v0.35.0）版本
  逐字节相同（diff 验证），非本次 v2.0 改造引入的新缺陷，而是流 B 新增 frontmatter 字段与既有
  --fix 逻辑碰撞暴露的潜伏缺陷。据此将 BDD-17 判定为 FAIL（其余 27 条 PASS），未擅自修复代码。
- P6-acceptance.md 最终 frontmatter：pass: 27, fail: 1, ui_affected: false。
- 自查通过：check-frontmatter.sh exit 0（本文件自身 schema 合规）、check-p6-format.sh --check exit 0、
  check-p6-evidence.sh exit 0、check-p6-provenance.sh exit 0。check-gate.sh P6 如实 exit 1（FAIL=1），
  这是预期的诚实结果，不代表验收角色失败。
