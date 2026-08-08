- [protocol-alignment-review.md] 角色定义已读，A1-A7 清单已加载
- [check-tdd-red.sh diff] read_gate_commands→agate-read-gate-commands.py, judge_result/collect_commands/main→agate-json-get.py, 行为等价确认
- [agate-json-get.py] 子命令 get/len/index/set/count_prefix/list/escape，与内联逻辑等价
- [agate-capture-env-baseline.sh diff] read_p5→agate-read-p5-commands.py(对象包装), 循环→agate-json-get, 无块exit0空输出等价
- [agate-read-p5-commands.py] 输出 {"commands":entries} 对象,无gate块exit0空输出——与原数组输出经bash改len commands/index commands后等价
- [check-state-transition.sh diff] get_old/get_new_phase→agate-state-get phase/phase_stdin, retries判定→retries_over；MAX_RETRY死变量移除等价
- [gate-result.sh diff] write_gate_result→agate-json-get escape, read_state_phase/task_id→agate-state-get
- [agate-state-get.py] phase/phase_stdin/task_id/retries_over与内联逻辑等价(含max_map.get(phase,3)默认)
- [agate-retreat-to.sh diff] CURRENT_PHASE→agate-state-get phase, check_retreat/write_retreat→agate-retreat-state.py
- [agate-retreat-state.py] check_retreat/write_retreat 与原内联逻辑逐行等价(含range(cur-1,tgt-1,-1),count+1>limit,setdefault)
- [check-retrospective.sh diff] RETRIES_OVER→agate-state-get retries_over,硬编码MAP作argv传入等价
- [pre-commit-gate.sh diff] OLD_PHASE→\u0024AGATE_ROOT/scripts/agate-state-get.py phase_stdin（该脚本用AGATE_ROOT非SCRIPT_DIR，line26已定义）
- [check-changelog.sh diff] UNRELEASED→agate-changelog-unreleased.py 等价
- [check-p6-provenance.sh diff] get_risk_level/ui_affected→agate-md-field-get, BLOCKER→agate-vision-blocker, 审计6→agate-evidence-consistency 均等价
- [check-pruning.sh diff] RISK_LEVEL/PHASES_DECLARED→agate-md-field-get risk_level/phases，正则逐字等价
- [check-state-yaml.sh diff] ERRORS→agate-state-yaml-check.py 等价(含YAMLError打印+exit0,空文件+exit0,字段校验)
- [agate-md-field-get.py] risk_level/ui_affected/phases 与原内联正则一致
- [agate-state-yaml-check.py] 与原内联逐行等价
- [agate-evidence-consistency.py] 与原审计6内联等价
- [agate-vision-blocker.py] blocker_count读+异常-1 与原内联等价
- [check-p6-evidence.sh diff] ui_affected→agate-md-field-get, variance→agate-image-check variance, ahash→agate-image-check ahash 均等价(PIL缺失路径stdout/stderr行为一致)
- [check-gate.sh diff] MISSING_CMDS→agate-gate-missing-cmds.py, P5_CMD_COUNT→agate-gate-p5-count.py 等价
- [agate-inject-card.sh diff] 注入→agate-card-inject.py(用AGATE_ROOT line10定义) 等价
- [agate-image-check.py/missing-cmds/p5-count/card-inject.py] 均与原内联逐行等价
- [check-protocol-consistency.py diff] CHECK9锚点: check-state-yaml.sh锚点改keywords=state.yaml, 新增agate-state-yaml-check.py锚点keywords=task_id
- [tests/README.md diff] 新增13个工具bats行+check-tdd-red.bats 32→38
- [锚点遍历] check-pruning/state-transition/p6-evidence/p6-provenance/retrospective/changelog/tdd-red/gate 各.sh锚点关键词经重构后仍驻留.sh，锚点未断裂
- [bats全量] 597 ok / 0 not_ok, exit 0；count-tests.sh=591（sanity 独立不计入）
=== AGENTS.md(root) STALE: 8个sh内联python3说法已失效 ===
=== LIMITATIONS.md line92 STALE: 8个gate脚本内联python3调用说法失效 ===
=== scripts/README.md: 新14个.py工具未列入清单(完整性gap) ===
=== role files/task-files/dispatch-prompt: 仅按脚本名引用行为,行为未变,无需更新 ===
=== SELF-GATE.md line16 已含 agate/scripts/*.py 触发模式,新.py正确触发 ===
- [A4] bats全量实跑 597ok/0not_ok exit0; count-tests=591; consistency CHECK1-9全过; shellcheck exit0
- [A5] 各.sh均定义SCRIPT_DIR(除agate-inject-card/pre-commit用AGATE_ROOT已定义); 行为非破坏; CHANGELOG无此重构条目(未发版待决策)
- [A6] 锚点遍历: 各.sh锚点关键词重构后仍驻留; check-state-yaml锚点重指向.py; 不涉及ADR脚本构成约束
- [A7] adr.md 无脚本构成形式ADR; ADR-002/003未违反; 建议可选新增.py工具架构ADR
