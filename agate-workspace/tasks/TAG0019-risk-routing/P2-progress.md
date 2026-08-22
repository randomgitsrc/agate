## P2 architect progress (TAG0019)

- [x] 读 P2-dispatch-context-architect.md（派发指引 + P2 卡全文）
- [x] 读 architect.md 角色定义（稳定版）
- [x] 读 P1-requirements.md（15 条 BDD approved，risk_level=medium，phases 全阶段，domains=backend+security）
- [x] 读 P0-brief.md（env_constraints：/tmp 只读 → pytest 需 --basetemp + -p no:cacheprovider；test_cmd 三件套）
- [x] 读 design-risk-routing.md（设计提案：三原则/档位表/M1-M4）
- [x] 读 check-pruning.py 稳定版（_md_field:30-44 / _read_p1:47-53 / _staged_source_count:55-81 / 源码数>5:134-136 / coupling_checklist 流式:141-146 / 跳过风险:154-157）
- [x] diff 确认 worktree 版与稳定版 SAME_SOURCE
- [x] 读 requirements-review.md（裁剪合理性节 :48-52，risk_level 匹配核对 :50 为 D4 落点）
- [x] 消费点验证：frontmatter-check :33/41/43、md-field-get :89-127、summary :37/42、consistency :452-508、README :36、WORKFLOW :296/320、pre-commit-gate :337-339、requirements-review :50、dispatch-protocol :931、role-system :54-70、CONTEXT :11/28/29、analyst :63-66、task-files :127-160、tests/README :31
- [x] P2 最小验证（importlib）：check-pruning 可 import 无副作用（_md_field/_read_p1/_staged_source_count callable）；空暂存区 staged_count=0；带连字符模块 importlib 加载可行 → MINVAL_OK
- [x] 写 P2-design.md（candidate_count=3：扩展不改名/独立 check-routing/改名合并，选独立脚本+import 同源；影响面节：改 2 新脚本+6 注册点+10 文档+测试资产 / 不改 check-gate/state-machine/UPGRADING 历史/M3/M4 / 9 风险各配缓解；gate_commands 带 basetemp+consistency+platform+count-tests）
- [x] 自检：Header 8 字段齐 / candidate_count=3 与正文一致 / 四字段齐全 / files_to_read+env_constraints+minimal_validation 齐 / 影响面节在候选方案前 / status: draft / 33704 字节非空

## 完成（P2-design.md 产出）

## plan-eng-review 评审进度（追加）

- [x] 读 dispatch-context（评审重点 6 项 + 角色定义 + P2 卡全文）
- [x] 读 P2-design.md（主评审对象）/ P1-requirements.md（15 BDD）/ P0-brief.md / design-risk-routing.md / check-pruning.py
- [x] 独立核实复用链：check-pruning _md_field:30-44 / _read_p1:47-53 / _staged_source_count:55-81 存在且 callable，coupling_checklist 判据:142、跳过风险判据:156（worktree/稳定版 7 脚本 cmp SAME）
- [x] 独立核实注册点锚点：frontmatter-check schema:31-50（allowed/enums/types）、md-field-get STRING_FIELDS:121-123、pre-commit-gate 2j:337-339（gate_exit!=1 条件）、summary _DRIFT_SCRIPTS:42、consistency 注册表:448-519、role-system C8:56-63、review-mapping:13-15、requirements-review 裁剪合理性:48-52、dispatch-protocol:931、WORKFLOW:296/320（P8 行 + 2.7 行）、P2 卡评审派发:182-186、P4 卡:84-86、task-files frontmatter:127-160、analyst 样例块:63-66、CONTEXT 词条:11/28/29
- [x] **平台扫描独立实测（阻塞发现）**：`check-platform-assumptions.py <scripts> <tests>` 双 target → RC=1，既有命中 agate-install.py:326,330,396（R2）/ check-platform-assumptions.py:22,38（R3/R1 自伤）/ commit-msg-self-gate.sh:22,35 / pre-commit-gate.sh:21,34 / pre-push-gate.sh:22,35 / pre-commit-gate.py:61 / install-hook.py:128（R2）→ P5_platform 全树双 target 声明基线即红灯；tests-only RC=0（CI 现行基线）
- [x] minval 独立复跑：importlib 加载 check-pruning 三函数 callable、非 git 目录 staged_count=0、带连字符模块（agate-md-field-get.py）可加载 → 设计 minimal_validation 声明成立
- [x] 写 P2-review.md（status: rejected，1 阻塞 + 4 非阻塞 + 测试缺口 + 锁定决策）

## P2 rev1 修订（plan-eng-review rejected：BLK-1 + NB-1~4 + 3 测试缺口）
- [x] 读 P2-dispatch-context-architect-rev1.md（修复目标/约束）
- [x] 读 P2-review.md（BLK-1 证据：agate-install.py:326,330,396 / scanner 自伤 :22,38 / 3 sh hook / pre-commit-gate.py:61 / install-hook.py:128 R2 → 全树双 target 必 exit 1；NB-1~4 + 测试缺口 3 项）
- [x] BLK-1 修复：P5_platform 收窄为变更文件集（2 新脚本 + 5 测试文件，:283）——同步 §0.3 R5（:103 变更文件集 0 命中）+ §4 说明（:288 存量命中不阻塞备查）+ §5（:340）
- [x] NB-1：full→P7 声明层+评审层——§2.2 D2 补 full P7 声明（:208）+ §2.4③ 核对项（:242）+ §2.6 删通常伴随改三重保证（:254-257）
- [x] NB-2：§2.3 错误边界——P1 缺失 exit 2 对齐 check-pruning（:232）+ 算分异常 git_ok:false fail-closed thin exit 1（:233）
- [x] NB-3：§2.1 影响面判据精确化（改动文件集/搜索面/命中判据二值，:179）+ R9 对齐（:107）
- [x] NB-4：files_to_read 补 requirements-review:48-52 / role-system:54-70（:311,313）；§0.2 交代 WORKFLOW:290 权威在 role-system C8 + P3/P7 卡正交不细化 + _GUARD_SCRIPTS 不追加（:90-92）
- [x] 测试缺口 3 项：§3 补分支清单（thin 全过/缺要素/P1 缺失 exit 2/算分异常 fail-closed/对拍+importlib 断言）+ full-P7 文档断言（:266-271）
- [x] 自检：candidate_count=3 未动、四字段未动、minimal_validation confirmed 未推翻、其余 gate_commands key 未动、39816 字节非空

## rev1 完成（修订后待重审）

## plan-eng-review 复审轮（rev2）进度（追加）

- [x] 读 rev2 dispatch-context（增量强制指令）+ 修订版 P2-design.md（341 行，全读）
- [x] BLK-1 复核：P5_platform（:283）= 变更文件集（2 新脚本 + 5 测试文件），非全树；R5（:103 "变更文件集 0 命中"）/ §4 说明（:288 存量命中证据逐条 + 不阻塞备查）/ §5（:340 "存量 scripts 树命中不阻塞"）三处措辞一致
- [x] BLK-1 可执行实测：5 个测试文件路径 3 个已存在（test_check_frontmatter / test_agate_md_field_get / test_pre_commit_hook），4 个新文件（2 脚本 + 2 新测试）P4 产出（预期）；扫描器单文件 target：现存文件 RC=0、不存在 RC=2（fail-closed：P5 时未产出 → 红灯）
- [x] NB-1 复核：D2:208（full→P7 声明层）/ D4:242（评审层核对项）/ §2.6:254-257（三重保证，删"通常伴随"）闭环 ✓；残留 NB-1a：D4 :242 核对条件只覆盖"声明 ceremony: full"，算分 tier=full（无声明）分支的 P7 核对未纳入（非阻塞，建议条件扩为"算分 tier=full 或声明 full"）
- [x] NB-2 复核：:231-233 错误边界闭环（P1 缺失 exit 2 对齐 check-pruning / git_ok:false + thin → exit 1 fail-closed / standard-full 不拦）；微观察：D1 输出描述未显式列 git_ok 键
- [x] NB-3 复核：:179 影响面判据二值可判（对象=暂存区改动文件集、搜索面=repo_root 排除 task_dir/tests、命中=≥1 引用且非 F 自身）；R9:107 同步
- [x] NB-4 复核：files_to_read 补 requirements-review:48-52 / role-system:54-70（:310-313）；§0.2 交代 WORKFLOW:290（权威源 role-system C8 论证成立）+ P3/P7 正交（:91）+ _GUARD_SCRIPTS（:92）
- [x] 全量复评：candidate_count=3 一致 / 四字段齐 / gate_commands 其余 key（P3/P5/P5_consistency/P5_count_tests/P5_timeout_seconds）无回归（无 && 链）/ minimal_validation 未破坏 / 影响面三部分在候选方案前 / 方案 A/B/C 权衡完整
- [x] 写 P2-review.md（覆盖更新，status: approved）
