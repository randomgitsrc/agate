# P3 progress (test-designer, A+B+C+D four-stream TDD test design)

- [x] 读角色定义 test-designer.md：TDD 红灯先行、BDD→测试 1:1 映射、覆盖正常路径+边界+异常、分阶段落盘（T016 教训）
- [x] 读 P3-dispatch-context-test-designer.md：约束 12 条（594 硬约束/不允许净新增/15 文件改写而非删减/3 个 regression 摩擦锚点/2 个不动 fixture/P3 只跑 unit+regression/UI 任务判断/按流 A→B→C→D 组织/嵌套≤3 层/语义真实性边界/分阶段落盘/不改实现代码）
- [x] 读 P0-brief.md：A+B+C+D 范围、9 条硬约束
- [x] 读 P1-requirements.md：28 条 BDD 全文（流 A 15 / 流 B 5 / 流 C 4 / 流 D 4）+ F1-F19 摩擦表 + §9 语义真实性边界
- [x] 读 P2-design.md 全文（649 行）：§3.1 流 A 五小节（schema/双读工具/校验器/pre-commit 挂载/fixture 重写+594 配平机制）、§3.2 流 B、§3.3 流 C、§3.4 流 D、§5 gate 命令、§6 files_to_read、§7 minimal_validation、§9 BDD 覆盖映射表、§13 FIND-1/3/5/7 修订详情
- [x] 读 P2-review.md：approved + 8 条 FIND；FIND-1（presence 判别契约方案②）/ FIND-4（ui_affected 归一化 .lower()）/ FIND-5（单行全角冒号块非 dict 硬拦截）/ FIND-7（594 配平核算口径）与本阶段测试设计直接相关
- [x] 读 agate/tests/README.md：bats helper 加载顺序、fixture 约定、count-tests.sh 用法
- [x] 读 agate/scripts/agate-state-yaml-check.py + tests/unit/agate-state-yaml-check.bats：校验器范式参照（pyyaml + schema + 错误行输出，无错误输出空；check-state-yaml.sh 薄壳：非空输出 exit 1）
- [x] 客观查证：count-tests.sh 基线实测 594（sanity 6 另计）；15 受影响文件 @test 数逐一实测（check-gate 101/check-pruning 29/check-p6-provenance 38/check-p6-evidence 28/check-tdd-red 38/check-gate-p1-review 9/check-scope-resolved 11/check-retrospective 11/check-p6-format 12/agate-extract-context 15/v060-design-gap 4/v060-p8-internal-only 3/v060-r4-cached 2/pre-commit-hook 42/consistency 11，合计 354，与 dispatch-context objective_info 一致）

## 基建（跨流共享，先行）

- [x] 读 agate/tests/helpers/fixtures.bash 全文：`create_task_dir`（写 P1/P2/P6 fixture 逻辑）/ `add_p1_field` / `add_p2_candidate_count` / `add_pruning_excuse` 等 helper 现状（v0.35 写正文）
- [x] 读 agate/scripts/agate-md-field-get.py 全文（47 行，3 op 纯正则）：确认现有 `re.search` 全文扫描不区分 frontmatter/正文位置——这意味着"简单把字段挪进 frontmatter"对现有正则读取路径通常"意外兼容"，真正的 TDD 红灯必须来自"新 op 不存在"或"新值格式旧正则无法匹配"（如带引号值、YAML bool 类型）两类场景，纯粹的"挪位置"不产生红灯
- [x] 改造 `fixtures.bash`：新增 `add_frontmatter_field <file> <field> <value>`（在 `---...---` 块内插入/更新 key，无块则新建）；`create_task_dir` 新增 `--legacy-fields` 选项（默认关闭 = v2.0 新格式，risk_level/phases 写入 frontmatter；打开 = v0.35 旧格式，写正文，供 BDD-9 测试用）；`add_p1_field` / `add_p2_candidate_count` 改为调用 `add_frontmatter_field`（P2-design.md §3.1.5 明确要求）
- [x] 验证：`bash -n fixtures.bash` 语法通过；`source` 后手工冒烟测试 `add_frontmatter_field` 4 种场景（已有块插入/无块新建/文件不存在/更新已有 key）全部符合预期
- [x] 验证：fixture 改造后跑 `bats agate/tests/unit/ agate/tests/regression/`（改动前 baseline），516 用例全绿，0 回归——证实"字段挪进 frontmatter"对现有正则读取路径确实无害，符合 P2-design §7 minimal_validation assumption 2 的判断

## 流 A（BDD-1..15）

- [x] 新增 `agate/tests/unit/check-frontmatter.bats`（10 个 @test：CF.1-10），覆盖 BDD-2/4/5/6(×3)/7/8/12 + FIND-1（P7 文件只有 blocker_count 时仍走 P7 schema，不被判别契约误判为旧格式）+ FIND-5（单行全角冒号块非 dict 硬拦截）
- [x] 逐条验证真红灯：9/10 因 `agate-frontmatter-check.py` / `check-frontmatter.sh` 不存在而失败（B 类：脚本未写）；1 条（CF.9）初版因"任意非空 stderr 即通过"设计过松（`agate-frontmatter-check.py` 本身文件名含 "frontmatter" 字样导致误报文件不存在的错误信息也被判定为"通过"），已收紧断言（新增 `!= *"No such file"*` 排除条件），复测后全部 10 条真红灯
- [x] 改写 `agate/tests/unit/agate-md-field-get.bats`（6 个既有 @test 内容重写，数量保持 6 不变）：MDF.1（BDD-1，frontmatter 读取）/ MDF.2（BDD-9，旧格式回退）/ MDF.3（BDD-10，带引号值证明 dict 优先而非文本首现巧合——真红灯）/ MDF.4（BDD-3，块式列表）/ MDF.5（BDD-1，新 op candidate_count——真红灯，unknown op exit 2）/ MDF.6（BDD-1，新 op packages——真红灯）
- [x] 关键设计教训记录：BDD-10（frontmatter 优先于正文同名字段）如果用"未加引号的普通值"测试，会因为 frontmatter 物理上总是位于文件正文之前、而现有 `agate-md-field-get.py` 用无锚定的 `re.search` 取第一个匹配，导致旧代码"巧合正确"（不构成真红灯）——必须用旧正则无法匹配的值格式（带引号字符串）才能证明"是 dict 优先级逻辑而不是文本顺序巧合"。这是本阶段发现的设计陷阱，已记录于 P3-test-cases.md §2 BDD-10 行
- [x] 改写 `agate/tests/unit/agate-state-yaml-check.bats`（3 个既有 @test，数量保持 3）：SY.1 重写为单测试内两段 run（BDD-25 TAG0001 通过 + BDD-26 T001 拒绝），SY.2/SY.3 补充新格式 task_id 前缀但保持原有必填/枚举校验回归职责不变。验证：SY.1 真红灯（现行 `^T\d+$` 接受 T001、拒绝 TAG0001，与 BDD-25/26 要求相反）
- [x] 改写 `agate/tests/unit/check-changelog.bats`（8 个既有 @test，数量保持 8）：CL.6/CL.7/CL.8 从"短前缀 T060 变体测试"改为"完整新格式 task_id TAG0001 测试"（BDD-27）。验证：3 条全部真红灯（现行 `grep -oE 'T[0-9]+'` 对 TAG0001 提取为空，下游匹配必然失败）
- [x] 594 配平：从 check-gate.bats/check-p6-format.bats/check-p6-provenance.bats/check-scope-resolved.bats/check-retrospective.bats 共移减 10 条概念重复断言（逐条理由见 P3-test-cases.md §1），配平新增的 check-frontmatter.bats 10 条，`count-tests.sh` 实测回落 594
- [x] 轻改写（不改变行为，只加 BDD 追溯注释/测试名前缀，@test 数不变）：check-pruning.bats（29，含 1 条改为显式 `--legacy-fields` 验证 BDD-9）/ check-p6-evidence.bats（28）/ check-tdd-red.bats（38，BDD-15 回归标注）/ check-gate-p1-review.bats（9）/ agate-extract-context.bats（15，FIND-1 决策"保持 grep 不改路由"回归确认）
- [x] gate_commands 无回归确认（BDD-15）：check-tdd-red.bats 全部 PYX.\* 用例（gate_commands 读取工具族）未改动、全绿，回归锚定
- [x] 语义真实性边界声明确认（BDD-14）：P2-design.md §10 全文核对，已存在显式声明，无需新增 @test（记录理由于 P3-test-cases.md §2）

## 流 B（BDD-16..20）

- [x] 读 check-gate.sh P6/P7 分支（L236-298）+ check-p6-format.sh（60 行）+ check-p6-provenance.sh 相关审计段落，确认现有实现细节（P6：`grep -ciE '^\s*- (PASS|FAIL)'` 计数；P7：BLOCKER 用非计数行排除正则、DESIGN_GAP 用数量相减）
- [x] check-gate.bats 内新增 G_BDD16.1（BDD-16，P6 frontmatter pass/fail 汇总——正文刻意不写任何 PASS/FAIL 行以制造与旧版 grep 计数的真实分歧，避免"body 恰好也对"的假红灯陷阱）——验证真红灯
- [x] check-p6-format.bats 内新增 F_BDD17.1（BDD-17，characterization，现有脚本已支持合规格式识别）+ F_BDD18.1（BDD-18，check-gate.sh 审计口径不把总结行计入逐条计数——验证真红灯，现行 FAIL 正则 `^\s*- FAIL([[:space:]:：]|$)` 会误将 `- FAIL: 0` 总结行计为 1 条真实 FAIL）
- [x] check-p6-provenance.bats 内新增 PV_BDD19.1（BDD-19，P7 frontmatter blocker_count=0 判定通过——正文刻意保留一条行首 `[BLOCKER]` 历史痕迹迫使旧版正则误判为真实 BLOCKER，制造真实分歧）+ PV_BDD20.1（BDD-20，reviewed<count 应拦截——验证真红灯，现行数量相减对"0 GAP+1 REVIEWED"场景算出负数、被 `-gt 0` 判断放过）
- [x] 改写 regression/v060-design-gap.bats（4 个既有 @test，数量保持 4）：R2.1/R2.2/R2.3/R2.3b 全部改为 frontmatter 声明 design_gap_count/design_gap_reviewed_count 的版本（摩擦锚点改写为测 frontmatter 版行为，P2-design.md §3.1.5 要求）；4 条均为 characterization（body/frontmatter 声明一致），作为 P4 实现后的回归安全网
- [x] 594 配平贡献：F7→(F_BDD17.1)/F11→(F_BDD18.1)/PV.5→(PV_BDD19.1)/PROV_MULTI.3→(PV_BDD20.1) 四条移减+新增，详见 §1 配平表

## 流 C（BDD-21..24）

- [x] 读 check-gate.sh P1 NEED_CONFIRM 分支（L69-98）+ check-scope-resolved.sh（45 行），确认现有逐条正则匹配/SCOPE+ 跨文件扫描逻辑
- [x] check-retrospective.bats 内新增 RT_BDD21.1（BDD-21，P1 frontmatter need_confirm_resolved 覆盖具体描述后不再阻塞——验证真红灯，现行 check-gate.sh 完全不读该字段）
- [x] check-scope-resolved.bats 内新增 SC_BDD22.1（BDD-22，frontmatter scope_resolved 非空列表使闭环判定通过——验证真红灯，现行脚本只扫正文 `[SCOPE_RESOLVED]` 散文标记）
- [x] BDD-23（发现性标记保持散文）确认为"负向验证"：check-scope-resolved.bats 的 SC.2/SC.3/SC.4/SC.6/SC.7 与 integration/pre-commit-hook.bats 的 IT_PT_\*/IT_PT_T6.\* 系列均未改动、全绿——证明 v0.35 散文扫描行为在 v2.0 下不受影响，符合 P1 隐含需求 #12/P2-design §3.3.2 的"不迁移"边界
- [x] BDD-24（角色卡/模板可复制样例）判定为"无 P3 阶段可执行断言对象"（模板/角色卡文本改造是 P4 交付物，P3 阶段实现未写、模板未改，不存在可失败的程序行为可供断言）——已在 P3-test-cases.md §4 详细说明验证方式改为 P6 阶段人工 + `yaml.safe_load` 双重核对，不违反"覆盖全部 28 条 BDD"要求（覆盖=已声明验证方法，不等于强行编造程序断言）
- [x] 594 配平贡献：SC.5b→(SC_BDD22.1)/RT.SCOPE_PROGRESS→(RT_BDD21.1) 两条移减+新增，详见 §1 配平表

## 流 D（BDD-25..28）

- [x] 读 agate-state-yaml-check.py:39（`^T\d+$`）+ check-changelog.sh:14（`grep -oE 'T[0-9]+'`），确认流 D 硬切改动点
- [x] agate-state-yaml-check.bats SY.1 改写完成（见流 A 记录，BDD-25/26 同落于此文件——流 D 硬切点物理上就是流 A 已改写文件的一部分，这也印证了 §6 "四流互不阻塞"里 BDD-25/26/27 与流 A/B/C 无共享实现依赖，只是恰好落在同一份既有测试文件里）
- [x] check-changelog.bats CL.6/7/8 改写完成（见流 A 记录，BDD-27）
- [x] BDD-28（本 task 自身 T001 全程 v0.35 gate 通过）判定为"运行时不变式，非 worktree bats 断言对象"——已在 P3-test-cases.md §5 说明理由（T001 是 worktree 外部既成事实，验证载体是主 Agent 每阶段 gate 记录，不是新协议测试套件内的断言；强行编造会与 BDD-26 表述冲突）

## 收尾核验

- [x] 全量重跑 `bats agate/tests/unit/ agate/tests/regression/`：516 个 @test（unit+regression 子集），493 ok / 23 not ok，23 条逐一核对与预期红灯清单完全一致（CF.1-10、MDF.3/5/6、SY.1、CL.6/7/8、G_BDD16.1、F_BDD18.1、PV_BDD19.1、PV_BDD20.1、RT_BDD21.1、SC_BDD22.1），**0 条非预期失败**（确认改造未引入意外回归）
- [x] 全量核验 `bats agate/tests/integration/consistency.bats agate/tests/integration/pre-commit-hook.bats`（P3 gate 不含 integration，但仍需语法/逻辑健全）：53/53 全绿，0 语法错误
- [x] `bash agate/tests/scripts/count-tests.sh` 最终实测：**594**（与改造前基线一致，BDD-11 达标）
- [x] 逐个 `.bats` 文件用 `bats <file>` 实跑验证（非 `bash -n`，因为 `.bats` 的 `@test { }` 语法不是纯 bash、`bash -n` 会对所有文件误报——已确认这是全库通用现象非本次改造引入）：全部可正常解析执行，无 A 类错误（语法错误/第三方 import 失败）
- [x] 写 P3-test-cases.md：test_code_dir 声明、28 条 BDD 逐条映射（按流 A/B/C/D 分组）、594 配平表（10 条移减+10 条新增逐一对照）、按流独立性说明（约束 8）、UI 任务判断（约束 7，非 UI）、语义真实性边界自检（约束 10）、嵌套约束自检（约束 9）
