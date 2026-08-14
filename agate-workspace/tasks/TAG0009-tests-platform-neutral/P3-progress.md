[P3 01:15] 读取 dispatch-context / 角色定义 / P0-brief 完成
— 任务要点：29 BDD 全覆盖；新建扫描器测试 check-platform-assumptions.bats；修改既有测试断言；P3-test-cases.md
[P3] 读取 P2-design / P1-requirements / P2-review 完成
— P2-review approved；TD.1b/TDD.F8 用 env -u PATH；scan-exempt 只豁免 R4；R2 正则 110行25文件口径

## [test-designer-scanner] 步骤进度（2026-08-13）

1. 已读 dispatch-context（目标/约束/输入文件）、test-designer.md、P0-brief.md、AGENTS.md（含 agate/AGENTS.md）
2. 已读 P1-requirements.md（29 BDD）、P2-design.md（§2.1 扫描器 + §3 映射）、P2-review.md（scan-exempt 负向用例）
3. 已读 tests/README.md、count-tests.sh、load.bash、fixtures.bash、sanity.bats、agate-debt-check.bats（bats 1.10.0 已装）
4. 发现关键约束：count-tests.sh 只统计 unit/regression/integration/*.bats → scripts/ 下新增扫描器测试**不造成用例数漂移**
5. 发现扫描器测试文件位于 tests/scripts/，**不在标准 bats 调用路径**（sanity+unit+regression+integration）→ P3-test-cases.md 标注此 gap（需 P4/主 Agent 决定在 CI/platform-scan job 补充调用）
6. 测试文件自身必须是"干净"的（fixture 内容运行时拼接，源码不得含 R1-R5 字面命中）——已设计 fragment 拼接法

7. 已写 agate/tests/scripts/check-platform-assumptions.bats（14 个 @test，覆盖 BDD-1~9 含负向用例）
   - 自净验证：按 R1-R5 模式集 grep 全文件 0 命中（fragment 拼接构造 fixture）
   - 红灯确认：bats 14/14 全红，红因 = 扫描器命令不存在（exit 127，B 类可推进）
8. 已写 P3-test-cases.md（29 BDD 1:1 映射，test_code_dir: agate/tests/，BDD-10/14/27 标注文档断言，
   既有用例改动标注"改动断言"且未实际修改；负向用例 4 个；count-tests 无漂移说明 + 扫描器测试未被标准
   bats 调用覆盖的 Gap 标注）
9. 自检：header 合规、无 - PASS/- FAIL 行首、BDD 1-29 全覆盖、[PROD_NOT_TOUCHED]

## 任务 B：test-designer 拆分支（P3 progress 续）
- [2026-08-14] 已读：dispatch-context、test-designer 角色、P0-brief、P2-design（§2.4-2.8）、P3-test-cases.md（任务 A 产出）
- [2026-08-14] 开始读取 9 个目标测试文件
- [2026-08-14] 已读 9 个目标测试文件 + fixtures.bash + load.bash；确认 PYTHON 尚未导出（P4 加）
- [2026-08-14] 已读 scanner 测试契约（tests/scripts/check-platform-assumptions.bats）——新增用例必须自净（R1-R5 零命中）

- [2026-08-14] [task-B1] 已读 dispatch-context-fix-tddred / P2-design §2.4 / P3-test-cases.md / 目标文件 check-tdd-red.bats（15 处 PATH 命中确认）

- [2026-08-14] [task-B1] 改动完成：TD.1b/TDD.F8 改 env -u PATH（exit 语义不变）；移除 15 处 PATH="/usr/bin:/bin" 覆盖（grep 为 0）；L139/148 加 scan-exempt 标记（内容原样）；自跑 bats 43/43 全绿（改动多为改写，非新行为，如实记录全绿）；[PROD_NOT_TOUCHED]
- [2026-08-14] [task-B2] 已读：dispatch-context-fix-other / P2-design §2.5-2.8 / 8 个目标测试文件 / install-hook.sh / fixtures.bash / git-helper.bash；确认 ci-gate-backstop 10 处命令位置 python3（dispatch 写 7 例 = 7 个失败用例口径，R2 零命中需全 10 处改）
- [2026-08-14] [task-B2] 改动完成：
  1. install-hook.bats：新增「ln 复制模式下 pre-push 以复制安装并提示重跑」用例（复用 L43 mock 先例，断言复制/需重跑 + [ -f ] 不断言 -L）；既有 [[ -L ]] 断言未动（P4 平台分支）
  2. integration/pre-push-hook.bats：新增「ln 复制模式安装输出升级提醒」用例（断言 WARNING 语义 + [ -f ]，不断言 -L；初版误用 $agate_root/scripts/install-hook.sh 不存在的 install-hook.sh → exit 127，改为 $AGATE_ROOT/scripts/install-hook.sh 后绿）
  3. agate-next-card.bats：L104 cd /tmp → cd "$BATS_TEST_TMPDIR"；bdd-21 setup 改平台分支（MINGW/MSYS 正斜杠 C:/proj/agate，其余字面反斜杠 C:\proj\agate，断言 路径：phase-cards/P3-tdd.md）
  4. check-scope-resolved.bats：L8 /tmp/nonexistent- → $BATS_TEST_TMPDIR/nonexistent-
  5. check-tdd-red-formatter.bats：L97/L105 样例文本行尾加 # scan-exempt: 标记（内容原样）
  6. ci-gate-backstop.bats：10 处命令位置 python3 → $PYTHON（全改保 R2 零命中）；5 个含中文关键词断言用例加 output=$(printf '%s' "$output" | tr -d '\r') CRLF 归一化
  7. agate-extract-context.bats：新增 EC.16「P6 failed 求和无bc模拟环境仍正确」——bc 剔除用「前置失败 bc stub」实现（Linux 上 bc 在 /usr/bin，整目录剔除会连 bash/grep 一起丢，shadow stub 效果等同 bc 不可用且确定；已按 R5 回避字面 bc 词）
  8. env-adapt-docs.bats：bdd-34 shellcheck → ${SHELLCHECK:-shellcheck} 探测（改完绿）
- [2026-08-14] [task-B2] 自跑结果：80 ok / 11 not ok。红 = ci-gate-backstop 全 10 例（$PYTHON 未导出，P4 fixtures 导出后绿——如实记录）+ EC.16 1 例（当前 bc 版在 bc stub 下求和=0，P4 bc→awk 后绿）；其余 7 文件全绿（新增复制模式用例/平台分支/scan-exempt 标记/SHELLCHECK 探测均当前绿，按实际记录）
- [2026-08-14] [task-B2] 扫描器自净验证（按 R1-R5 正则模拟）：本 8 文件改动零新命中；残留 R3=install-hook L26/L38 + pre-push L11（P4 平台分支）、R2=formatter L13/L21（python3 -c，非本 B2 范围）+ env-adapt-docs L25（bdd-25 python3，非本 B2 范围）——均属既有假设，记 P4 处理
- [2026-08-14] [task-B2] count-tests：723（新增 3 例：install-hook 复制模式/pre-push 复制模式/EC.16），预期 I10 漂移，P4/P5 同步 tests/README 附录
- [PROD_NOT_TOUCHED]
