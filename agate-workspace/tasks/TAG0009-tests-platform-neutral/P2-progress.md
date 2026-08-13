
## P2 architect 执行进度

### 2026-08-14 初始
- [x] 读取 dispatch-context（P2 派发指引）
- [x] 读取 architect.md 角色定义
- [x] 读取 P0-brief.md（env_constraints: Linux debug + Windows 模拟环境）
- [ ] 读取 P1-requirements.md
- [x] 读取 P1-requirements.md（29 BDD + I1-I10 + SUGGEST 1-5 + SCOPE+ 观察）
- [ ] 读取 P1-review.md
- [ ] 读取/核验各测试文件（check-tdd-red.bats / install-hook.bats / helpers / product scripts / CI yml）
- [x] 读取 P1-review.md（approved，覆盖维度标注）
- [x] 读取 fixtures.bash / load.bash（helper 挂载点已确认：fixtures.bash 被 load.bash source）
- [ ] 核验 check-tdd-red.bats PATH 15 处 + TD.1b/TDD.F8 场景
- [ ] 核验 install-hook.bats [[ -L ]] 2 处 + L43 mock 先例
- [ ] 核验 agate-extract-context.sh L128 bc
- [ ] 核验 check-state-transition.sh script-side python3
- [ ] 核验 protocol-tests.yml CI 现状
- [ ] 最小验证：harness PATH shim

### 2026-08-14 续（上次空返回后重跑）
- [x] 重读 dispatch-context（9 设计选型点 + gate_commands 补充 + 双最小验证要求）
- [x] 重读 architect.md / P0-brief / P1-requirements（29 BDD）/ P1-review（approved）
- [x] 读取 fixtures.bash / load.bash（helper 挂载点）
- [x] 核验 check-tdd-red.bats（PATH 15 处：TD.1b L49、TDD.F8 L381、TDD.G1 L164、TDD.G5 L227、TDD.F1 L245、TDD.F2 L260、TDD.F3 L279、TDD.F4 L296、TDD.F11 L315、TDD.F12 L333、TDD.F5 L351、TDD.F6 L367、TDD.F9 L404、TDD.F10 L435、TD.FAIL_HINT L451；TD.1b/TDD.F8 为"PATH 无 python"场景）
- [x] 核验 install-hook.bats（[[ -L ]] 2 处 L26/L38 + readlink L27/L39；L43-65 ln mock 先例）
- [x] 核验 agate-extract-context.sh L128（`paste -sd+ | bc 2>/dev/null || echo 0 | tail -1`——注意存在 paste 顺序问题，bc 改 bash 原生后一并验证）
- [x] 核验 check-state-transition.sh script-side python3（L36/L41/L78 三处 `python3 "$SCRIPT_DIR/agate-state-get.py"`）
- [x] 核验 protocol-tests.yml（bats 仅 ubuntu；shellcheck/consistency/gate-backstop 已 windows matrix 用 python+PYTHONIOENCODING=utf-8）
- [x] 核验 env-adapt-docs.bats bdd-34（L54 `shellcheck` 裸调用）与 bdd-33 windows-latest 断言
- [x] 核验 agate-next-card.bats L104（cd /tmp）与 bdd-21（L191 AGATE_ROOT='C:\proj\agate' 反斜杠模拟）
- [x] 核验 check-scope-resolved.bats L8（/tmp/nonexistent 逻辑路径）
- [x] 核验 check-tdd-red-formatter.bats L97/L105（/tmp 在 vitest mock 输出字符串，fixture 样例）
- [x] 核验 ci-gate-backstop.bats（python3 7 处 + 中文关键词 真红灯/绿灯/SKIP 断言）
- [ ] 最小验证 1：harness PATH shim
- [ ] 最小验证 2：扫描器模式集 fixture
- [x] 最小验证 1：harness PATH shim（CONFIRMED：shim 3 次 python3 调用全解析；无 python3 时 P4→P2 非法回退静默 exit 0 复现 41 例根因；注入 shim 恢复 exit 1）
- [x] 最小验证 2：扫描器模式集（CONFIRMED：R1=15 行 / R2=25 文件 98 行（与 P1 §8 一致）/ R3=3 处（含 pre-push-hook 新增）/ R4=6 处（2 逻辑+4 样例，scan-exempt 标记豁免生效）/ R5=0）
- [x] 产出 P2-design.md（candidate_count=2、四字段、29 BDD 全覆盖表、files_to_read、gate_commands.P5=全量 bats+consistency+shellcheck+扫描器、minimal_validation 双 CONFIRMED + 纯代码逻辑声明）
- [x] 自检通过：无行首 - PASS/- FAIL；frontmatter 机器字段齐全；[SCOPE+] 3 条观察已标注

### 2026-08-14 plan-eng-review（评审轮）
- [x] 读取 P2-dispatch-context-plan-eng-review + plan-eng-review.md 角色 + P2-design.md + P1-requirements + P1-review
- [x] 核验 §2.1 扫描器模式集（实证）：R1=15 ✓ / R2（设计表原样含全角））→0 命中 ✗；改半角 `)` 且字符类含引号 `[=(\"]` →110 行 25 文件；不含引号 `[=(]` →98 行——设计表"25 文件 98 行"与"前字符类必须含引号（否则漏检 ci-gate-backstop 7 例）"经验教训自相矛盾（含引号应为 110）✗ / R3=3 ✓（含 pre-push-hook L11）/ R4=6 ✓ / R5=0 ✓
- [x] 核验 §2.4 TD.1b/TDD.F8 修复（实证）：TEST_RUNNER=/nonexistent → **exit 1**（A-class 127）非 3；当前 `env -i PATH="/usr/bin:/bin"` → exit 3；`env -u PATH` → exit 3（平台无关替代成立）——设计"exit 语义保持：TDD.F8 期望 3"与所提 TEST_RUNNER 机制矛盾 ✗
- [x] 核验 §2.4 TDD.G/F 13 处移除 PATH：这些用例用 `-u TEST_RUNNER + TASK_DIR`（gate_commands.P3 绝对路径），不依赖 PATH 找 runner，移除 PATH 覆盖安全 ✓
- [x] 核验 §2.3 shim：9 产品脚本对应 .bats 文件全部存在（check-state-transition/check-frontmatter/check-state-yaml/check-changelog/agate-debt-check/check-p6-provenance/check-retrospective/check-scope-resolved/agate-inject-card + check-tdd-red.bats）✓
- [x] 核验 §2.8 bc→awk：awk 空输入→0、2+1→3、单值→1（实证 ✓）；原始 bc 管道优先级隐患属实（`|| echo 0 | tail -1` 绑定歧义）✓
- [x] 核验 §2.9 CI：现有 windows matrix 模式（python + PYTHONIOENCODING=utf-8）确认 ✓；bats 仅 ubuntu ✓；安装步骤"P5 定稿"已显式声明（I7 supplementable）✓
- [x] 核验 helper 挂载点：fixtures.bash 被 load.bash source（L43）✓；detect_python 放置合理
- [x] 核验 §2.6 scan-exempt：check-tdd-red.bats L139/148、formatter L97/105 的 /tmp 均在 mock 输出字符串（R4 实测命中），行尾加 `# scan-exempt:` 机制可行 ✓
- [ ] 写 P2-review.md（结论：needs-revision——2 处具体可验证缺陷：①R2 正则全角）笔误 + 计数矛盾 ②TDD.F8 TEST_RUNNER 机制 exit 语义不成立）
- [x] 写 P2-review.md（status: needs-revision——2 处可验证缺陷：①R2 全角）笔误+计数矛盾 ②TDD.F8 TEST_RUNNER 机制 exit 语义不成立；锁定决策 8 项）
- [x] 自检：无行首 - PASS/- FAIL；Header status 已改；结论引用锚点（§2.4/§2.1/§2.3/§2.6/§2.8/§2.9/§8/BDD-9/BDD-11/12）
## P2 修订轮 progress（architect）
2026年 08月 14日 星期五 00:57:23 CST

- 已读 dispatch-context / architect.md / P2-review.md / P2-design.md / P0-brief.md
- 复核缺陷 1（exit 语义）：实测 env -u PATH → exit 3；TEST_RUNNER=/nonexistent → exit 1（与 review §8 一致）
- 复核缺陷 2（R2 正则）：实测半角 ) 且前字符类含引号 → 110 行 25 文件（与 review 一致，纠正原表 98 行）

- 修订完成：§2.4 改 env -u PATH（TD.1b/TDD.F8，exit 3 语义保持）；§2.1 R2 正则半角 )+含引号前字符类，计数 98→110 行 25 文件（实测复核）
- BDD-11/§5 P3 说明/§8 note 同步更新；BDD-9 补 scan-exempt 只豁免 R4 负向用例（P2-review 建议）
- 自检：grep 确认缺陷 1/2 已修正、无全角 ）python3、无 98 行残留、无行首 - PASS/- FAIL、29 BDD 计数不变
[PROD_NOT_TOUCHED]

## P2 复评轮 progress（plan-eng-review）
- [x] 读取 dispatch-context / plan-eng-review 角色 / P0-brief / P2-design.md（修订版）/ 上轮 P2-review.md / P1-requirements
- [x] 复核缺陷 1（§2.4）：实证 `env -u PATH bash agate/scripts/check-tdd-red.sh` → exit 3 ✓（与 env -i PATH="/usr/bin:/bin" 等价）；TEST_RUNNER=/nonexistent → exit 1（A-class 127）✓；TD.1b L48-51 断言 `3 or 1`、TDD.F8 L380-383 断言 `3` 与设计声明一致 ✓；TD.1 L43-46 已覆盖 TEST_RUNNER→exit 1，设计注明"勿重复造" ✓
- [x] 复核缺陷 2（§2.1 R2）：设计表正则半角 `)` + 前字符类含引号 `[=(\"']`，按设计表原样 grep 全树实测 = 110 行 25 文件 ✓，与 §8 minimal_validation（110 行 25 文件）一致，25 文件与 P1 §8 清单逐文件吻合 ✓
- [x] 回归抽查：§2.3 shim（内嵌绝对路径/9+1 注入清单）✓；§2.5 symlink 平台分支（L43 mock 复用 + [SCOPE+] pre-push L11）✓；§2.8 bc→awk（awk 空→0/单→1/2+1→3 实证，原 L128 管道优先级隐患属实）✓；§5 gate_commands（P3 "bats" / P5 全量 4 项）✓
- [x] 无残留：P2-design.md 无 "98 行"、无全角 `）` R2 正则、110 行计数 §2.1/§8 自洽
- [x] 写 P2-review.md（status: approved）
[PROD_NOT_TOUCHED]
