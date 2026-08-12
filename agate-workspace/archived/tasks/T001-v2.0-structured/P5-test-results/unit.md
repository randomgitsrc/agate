---
phase: P5
task_id: T001
type: test-results
---

# P5 技术验证结果 — T001

验证时间：2026-08-10T00:24:27Z
工作目录：/home/kity/oclab/agate/.worktrees/v2.0
分支：feat/v2.0

[PROD_NOT_TOUCHED] 本任务全程只改 agate 协议本体的脚本/文档/测试，不涉及任何生产环境/生产数据库/生产 API，本次验证也未触达生产环境。

[NO_NEED_CONFIRM] 本次验证纯只读，无数据删除/迁移等不可逆操作。

## 汇总

| 命令 | 结果 | exit code |
|---|---|---|
| P5 (bats 主命令) | 600/600 ok, 0 not ok | 0 |
| P5_consistency | 8/8 CHECK PASS（CHECK 5 已在脚本中主动删除，见下方说明），0 ERROR | 0 |
| P5_shellcheck | 0 条 warning 级别输出 | 0 |
| P5_count | 594 个测试用例（与 sanity.bats 6 个分开计） | 0 |

**结论：4 个 gate_commands.P5* 命令全部 exit 0，实跑结果与 P2-dispatch-context 给出的『预期结果』一致，未发现新增失败，未发现预存失败。**

---

## 命令 1／4：P5（bats 主命令，全量）

实际执行命令（与 P2-design.md §5 gate_commands.P5 声明一致，未加 tail 截断以便完整留档核证）：
```
bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
```

说明：gate_commands.P5 声明原文带 `| tail -40`，此处为核证完整性保留了未截断的完整 TAP 输出（tail -40 是原命令的一个子集，不会改变 ok/not ok 计数结果）。

统计：ok=600, not ok=0, 计划行 `1..600`, EXIT_CODE=0

完整 TAP 输出（原样保留，供签名校验 grep -cE '^(PASSED|FAILED|passed|failed|ok|not ok)' 识别）：
```
1..600
ok 1 load.bash: AGATE_ROOT 解析正确
ok 2 fixtures.bash: create_task_dir 默认全阶段
ok 3 fixtures.bash: create_task_dir 自定义 phases
ok 4 fixtures.bash: add_pruning_excuse 正确写入
ok 5 git-helper.bash: git_init 创建有效 repo
ok 6 git-helper.bash: git_commit + git_stage 工作
ok 7 ARCH.1 P6 阶段有 P6-acceptance.md + P6-evidence/，归档 P6
ok 8 ARCH.2 P4 阶段调用归档脚本，无需归档
ok 9 ARCH.3 P6-evidence/ 不存在，只有 P6-acceptance.md
ok 10 ARCH.4 同一任务对 P6 归档两次，两份历史证据都保留
ok 11 ARCH.5 P6-acceptance.md 含 FAIL，breadcrumb 正确摘要且不被归档
ok 12 ARCH.6 连续两次归档 P6，breadcrumb 追加而非覆盖
ok 13 ARCH.7 P1 阶段归档 P1-requirements.md + P1-review.md
ok 14 EB.1 任务级已有 pre-task-baseline.md → no-op，exit 0
ok 15 EB.2 P2-design.md 不存在 → exit 0 + WARNING
ok 16 EB.3 gate_commands.P5 未声明 → exit 0 + WARNING
ok 17 EB.4 首次捕获，仓库无缓存 → 真实跑测试命令，写入缓存+任务文件
ok 18 EB.5 缓存命中（同 commit + 同命令集合）→ 不重跑测试命令，直接复制缓存
ok 19 EB.6 缓存未命中（commit 变了）→ 重新真实跑测试命令
ok 20 EB.7 同一 commit 但 gate_commands.P5 命令集合不同 → 视为未命中
ok 21 EB.8 声明命令本身崩溃 → 不写任何文件，stderr 有 WARNING，exit 0
ok 22 EB.9 汇总计数与明细提取数不一致 → 不写任何文件，exit 0
ok 23 EB.10 gate_commands.P5 声明 2 条命令，各自有失败 → 合并去重
ok 24 EB.11 非 git 仓库 → exit 0 + WARNING
ok 25 EB.12 缓存文件存在但内容损坏（非合法 frontmatter）→ P5 diff 优雅降级
ok 26 EB.13 P5 + P5_formatter: pytest.sh → fail-list 从 JSON 提取
ok 27 EB.14 P5 无 formatter → WARNING，不写文件
ok 28 EB.15 vitest P5 + P5_formatter: vitest.sh → fail-list 提取
ok 29 IC.1 注入卡片到占位符之间
ok 30 IC.2 无占位符 → 非零退出
ok 31 CL.1 提取 Unreleased 区域内容
ok 32 CL.2 无 Unreleased → 空
ok 33 EC.1 PASS 但 evidence 标 FAIL → 输出不一致
ok 34 EC.2 无不一致 → 空
ok 35 EC.1: rejects missing arguments
ok 36 EC.2: rejects invalid phase
ok 37 EC.3: rejects nonexistent task dir
ok 38 EC.4: P1 extracts P0-brief fields
ok 39 EC.5: BDD-1 边界（FIND-2 grep 不改路由）：P2 extracts P1 domains（frontmatter 声明）and BDD count
ok 40 EC.6: P3 extracts P2 structured fields
ok 41 EC.7: P6 extracts BDD ID list and failed reference
ok 42 EC.8: P7 extracts PASS/FAIL counts
ok 43 EC.9: --write mode appends to dispatch-context file
ok 44 EC.10: P4 extracts P2 fields and P3 BDD count
ok 45 EC.11: P5 extracts gate_commands and implementation_dir
ok 46 EC.12: P8 extracts packages and BLOCKER/DEVIATION
ok 47 EC.13: gate-diagnosis reference auto-appended
ok 48 EC.14: P5 extracts implementation_dir from package subdirectories
ok 49 EC.15: P6 extracts failed count from package subdirectories
ok 50 GMC.1 提取命令 token 输出 key:token
ok 51 GMC.2 命令含 / 或 = 的 token 跳过
ok 52 GPC.1 统计 P5 命令数
ok 53 GPC.2 无 gate_commands 块 → 0
ok 54 IMG.1 variance 无 Pillow → SKIP_NO_PILLOW # skip Pillow 已安装，跳过无 Pillow 分支
ok 55 IMG.2 variance 非图像 → -1
ok 56 IMG.3 ahash 无 Pillow → stderr+exit 1 # skip Pillow 已安装，跳过无 Pillow 分支
ok 57 IMG.4 ahash 合法图片 → 输出 64 位 hash（Pillow 已装时）
ok 58 注入后 dispatch-context 内 AGATE_CARD 块 sha256 与卡片原文一致
ok 59 注入后其他内容保持不变（只替换 AGATE_CARD 块）
ok 60 P1 下多个 dispatch-context-{role}.md 全部注入
ok 61 TASK_DIR 不存在 dispatch-context 时 exit 1
ok 62 无参数时 exit 1
ok 63 缺 TASK_DIR 时 exit 1
ok 64 过渡期兼容：旧格式 P{N}-dispatch-context.md 也可注入
ok 65 dispatch-context 无 AGATE_CARD 占位符时 exit 1（非静默成功）
ok 66 IC_IDEMPOTENT.1: 重复调用（卡片内容未变）应 exit 0
ok 67 IC_IDEMPOTENT.2: 重复调用且卡片内容变化时应更新为新卡片
ok 68 IC_MISSING.1: 无 AGATE_CARD 占位符时 exit 1
ok 69 JGET.1 get 取标量键 + 默认值
ok 70 JGET.2 get 字符串键默认空串
ok 71 JGET.3 len 取数组长度（默认 0）
ok 72 JGET.4 index 取嵌套数组元素字段
ok 73 JGET.5 set 改写键并重排 JSON
ok 74 JGET.6 count_prefix 统计 module 前缀匹配数
ok 75 JGET.7 list 逐行打印数组每个元素
ok 76 JGET.8 escape json.dumps stdin 原始文本
ok 77 MDF.1 BDD-1: risk_level 从 frontmatter 块读取（字段级 presence 优先）
ok 78 MDF.2 BDD-9: 旧格式（frontmatter 无 risk_level，只在正文）仍通过正则回退正确读取
ok 79 MDF.3 BDD-10: frontmatter 带引号字符串值优先于正文同名字段（证明非文本首现巧合、而是 dict 优先）
ok 80 MDF.4 BDD-3: phases 在 frontmatter 内以块式列表（每行 - Pn）声明 → 解析为空格连接列表
ok 81 MDF.5 BDD-1: 新增 op candidate_count 从 P2 frontmatter 读取（int → str）
ok 82 MDF.6 BDD-1: 新增 op packages 从 frontmatter 列表读取（空格连接）
ok 83 P0: CLI body sha256 == 卡片文件 sha256（防漂移前提）
ok 84 P1: CLI body sha256 == 卡片文件 sha256（防漂移前提）
ok 85 P2: CLI body sha256 == 卡片文件 sha256（防漂移前提）
ok 86 P3: CLI body sha256 == 卡片文件 sha256（防漂移前提）
ok 87 P4: CLI body sha256 == 卡片文件 sha256（防漂移前提）
ok 88 P5: CLI body sha256 == 卡片文件 sha256（防漂移前提）
ok 89 P6: CLI body sha256 == 卡片文件 sha256（防漂移前提）
ok 90 P7: CLI body sha256 == 卡片文件 sha256（防漂移前提）
ok 91 P8: CLI body sha256 == 卡片文件 sha256（防漂移前提）
ok 92 CLI 输出头部三行固定（hook 用作 sha256 校验 marker）
ok 93 字节稳定性：连续两次调用 P3 sha256 一致
ok 94 CWD 在项目目录仍能解析 AGATE_ROOT
ok 95 软链接场景：脚本被 symlink 调用时 readlink -f 解析正确
ok 96 跨 checkout 路径：通过不同根路径调用 CLI 全量 hash 一致（P0-P8）
ok 97 无参数 期望 exit 1
ok 98 2 个参数 期望 exit 1
ok 99 phase=P9 期望 exit 2
ok 100 phase=小写 p3 期望 exit 2（case-sensitive）
ok 101 NC_ROOT.1 AGATE_ROOT 环境变量覆盖
ok 102 NC_ROOT.2 协议目录不在 git 仓库内时仍能工作
ok 103 P5C.1 P2 含 P5 + P5_formatter + P5_js → 输出对象含 commands
ok 104 P5C.2 P2 无 gate_commands.P5 → 输出空（供 bash -z 判定）
ok 105 P5C.3 P2 无 gate_commands 块 → 输出空
ok 106 P5C.4 P5 键双引号值被去除 + suffix/formatter 关联
ok 107 RP.1: rejects missing arguments
ok 108 RP.2: rejects invalid phase
ok 109 RP.3: rejects nonexistent task dir
ok 110 RP.4: placeholder replacement for phase/role/task_id
ok 111 RP.5: P2 selects P2 appendix (minimal validation)
ok 112 RP.6: P4 without --rollback selects P4 normal appendix
ok 113 RP.7: P4 with --rollback selects P4 rollback appendix
ok 114 RP.8: P5/P6 share same appendix (screenshot quality)
ok 115 RP.9: P8 selects P8 appendix (READY check)
ok 116 RP.10: role with special characters produces safe filename
ok 117 RP.11: output file contains render-product header
ok 118 RP.12: --rollback ignored for non-P4 phases
ok 119 RP.13: no residual placeholders except whitelisted
ok 120 RP.14: {agate_root} replaced with actual path
ok 121 RP.15: review-roles detected for review role
ok 122 RP.16: P3 renders P3 self-check appendix
ok 123 RSTATE.1 check_retreat 路径上阶段超限 → 输出 phase:count:limit
ok 124 RSTATE.2 check_retreat 无超限 → 空输出
ok 125 RSTATE.3 write_retreat 追加 retry + 改 phase + 回写
ok 126 RETREAT.1 phase=P6 目标 P4，retry 预算充足，产生 2 个独立 commit
ok 127 RETREAT.2 目标 phase 不低于当前 phase，拒绝执行
ok 128 RETREAT.3 路径上 retry 预算不足，预检查阶段拒绝且不做任何操作
ok 129 RETREAT.4 暂存区含 TASK_DIR 之外的文件，拒绝执行且不误提交
ok 130 RETREAT.5 目标 phase 不是 P0-P8 合法值
ok 131 STGET.1 phase 读 .state.yaml 的 phase
ok 132 STGET.2 phase 空状态文件 → 空串
ok 133 STGET.3 phase_stdin 从 stdin 读 phase
ok 134 STGET.4 task_id 读 .state.yaml 的 task_id
ok 135 STGET.5 retries_over 首个超限阶段
ok 136 STGET.6 retries_over 无超限 → 空输出
ok 137 SY.1 BDD-25/26: 新格式 TAG0001 校验通过；旧格式 T001 硬切拒绝（不兼容双格式）
ok 138 SY.2 缺必填字段 → 缺必填字段: xxx（回归，与流 D 编号规则无关）
ok 139 SY.3 phase 非法值 → phase 非法值（新格式 task_id 下回归，不受流 D 硬切影响）
ok 140 VB.1 读 vision_analysis.summary.blocker_count
ok 141 VB.2 无 blocker_count → -1
ok 142 CL.1 check-changelog.sh 无 CHANGELOG 文件 期望 exit 0
ok 143 CL.2 check-changelog.sh CHANGELOG 无 [Unreleased] 区域 期望 exit 1
ok 144 CL.3 check-changelog.sh [Unreleased] 无 task_id 期望 exit 1
ok 145 CL.4 check-changelog.sh [Unreleased] 含 task_id 期望 exit 0
ok 146 CL.5 check-changelog.sh task_id 在历史版本 期望 exit 1
ok 147 CL.6 BDD-27: CHANGELOG 含完整新格式 task_id TAG0001 → 直接匹配成功
ok 148 CL.7 BDD-27: CHANGELOG 只含 TAG00012（另一任务的更长编号）时 TAG0001 不误匹配
ok 149 CL.8 BDD-27: 旧版短前缀提取（grep -oE 'T[0-9]+'）对新格式 TAG0001 提取为空——直接匹配已消除该摩擦
ok 150 CF.1 BDD-2: P1 frontmatter risk_level 用全角冒号（risk_level：high）→ 校验失败且报错含 risk_level
ok 151 CF.2 BDD-4: P1 frontmatter coupling_checklist 列表项缩进错误 → 校验失败且报错可定位
ok 152 CF.3 BDD-5: P1 frontmatter risk_level 枚举外的值（HIGH）→ 校验失败且提示 low/medium/high
ok 153 CF.4 BDD-6: P1 frontmatter 缺 risk_level（其余必填齐全）→ 校验失败
ok 154 CF.5 BDD-6: P2 frontmatter 缺 candidate_count（其余必填齐全）→ 校验失败
ok 155 CF.6 BDD-6+FIND-1: P7 frontmatter 只含 blocker_count（无任何流 A 字段）仍按 P7 schema 校验，缺 design_gap_count → 报错
ok 156 CF.7 BDD-7: P2 frontmatter candidate_count 类型错误（字符串而非 int）→ 报错含字段名 candidate_count
ok 157 CF.8 BDD-12: P1 frontmatter 字段嵌套深度 > 3 层 → 校验失败
ok 158 CF.9 FIND-5: P1 frontmatter 块仅一行全角冒号纯量（非 dict，无 YAMLError）→ 仍被硬拦截
ok 159 CF.10 BDD-8: check-frontmatter.sh 与 check-state-yaml.sh 同构——非空校验输出 → exit 1；合规文件 → exit 0
ok 160 G0 check-gate.sh P0 立项阶段 期望 exit 2（输出不含『未知』）
ok 161 G1 check-gate.sh P1 缺 P1-review.md 期望 exit 1
ok 162 G2.1 check-gate.sh P2 0 个候选方案 期望 exit 1
ok 163 G2.2 check-gate.sh P2 1 个候选方案 期望 exit 1
ok 164 G2.3 check-gate.sh P2 2 个候选方案 期望 exit 2
ok 165 G2.4 check-gate.sh P2 h5 候选方案不识别（regex 边界）
ok 166 G2.25 check-gate.sh P2 #### 候选方案识别（h4 支持）
ok 167 G2.26 check-gate.sh P2 全角冒号标题 + candidate_count 字段 期望 exit 2（纯强制）
ok 168 G2.27 check-gate.sh P2 缺 candidate_count 字段 期望 exit 1（纯强制）
ok 169 G2.5 check-gate.sh P2 无 P2 文件 期望 exit 1
ok 170 G2.8 check-gate.sh P2 候选方案 ≥2 但无权衡 期望 exit 1
ok 171 G2.9 check-gate.sh P2 候选方案 ≥2 + 含权衡 期望 exit 2
ok 172 G2.9a check-gate.sh P2 design_trivial + 1 候选方案 + 含权衡 期望 exit 2
ok 173 G2.9b check-gate.sh P2 follows_existing_pattern + 1 候选方案 + 含权衡 期望 exit 2
ok 174 G2.10 check-gate.sh P2 有候选方案+权衡+四字段，P2-review.md frontmatter status:rejected 期望 exit 1
ok 175 G2.10a check-gate.sh P2 frontmatter rejected + 正文含 status: approved 字面串 期望 exit 1（对抗绕过）
ok 176 G2.11 check-gate.sh P2 有候选方案+权衡+四字段+frontmatter status:approved 期望 exit 2
ok 177 G_BDD1.1 BDD-1: check-gate.sh P2 四字段经 frontmatter 声明（非正文）仍被门禁正确读取判定
ok 178 G2.13 check-gate.sh P2 有候选方案+权衡+四字段，无 P2-review.md 期望 exit 1
ok 179 PG.P2REVIEW: P2-review.md not found → exit 1
ok 180 G_CMD_EXEC.1: P2 gate_commands 命令不可执行 → WARNING 不阻断 (exit 2)
ok 181 G_CMD_EXEC.2: P2 gate_commands 命令均可执行 → 无 WARNING (exit 2)
ok 182 G3 check-gate.sh P3 检查 P3-test-cases.md 存在（不跑测试）
ok 183 G4.1 check-gate.sh P4 暂存区仅 .md 期望 exit 1
ok 184 G4.2 check-gate.sh P4 暂存区有 .py 代码 期望 exit 0
ok 185 G4.3 check-gate.sh P4 暂存区 .md + .yaml + .py 混合 期望 exit 0
ok 186 G4.4 check-gate.sh P4 暂存区 .py 排除 .md 期望 exit 0
ok 187 G5 check-gate.sh P5 期望 exit 2
ok 188 G5.1 T060: P2 gate_commands.P5 多命令时 P5 输出 WARNING
ok 189 G5_CMD.1 P2 gate_commands 声明 P5+P5_e2e（2 键），其他节含 20 个 bullet -> WARNING 含 2 而非 22
ok 190 G5_CMD.2 P2 gate_commands 只声明 P5（1 键），其他节含 10 个 bullet -> 无 WARNING
ok 191 G5_CMD.3 P2 无 gate_commands 块 -> 无 WARNING，无崩溃
ok 192 G5_CMD.4 P2 gate_commands 声明 P5+P6（1 个 P5 键）-> 无 WARNING（P6 不算 P5 命令）
ok 193 G5_CMD.5 gate_commands 块位于文件末尾且无尾随换行 -> 仍正确计数 2 个 P5 键（回归：末尾换行边界）
ok 194 G6.1 check-gate.sh P6 含 FAIL 行 期望 exit 1
ok 195 G6.3 check-gate.sh P6 全 PASS 但无 BDD 期望 exit 1
ok 196 G6.4 check-gate.sh P6 全 PASS 但无证据目录 期望 exit 1
ok 197 G6.5 check-gate.sh P6 全 PASS + 证据目录非空 期望 exit 2
ok 198 G6.10 check-gate.sh P6 含 [NEED_CONFIRM] 不再拦截（v0.30.3 语义修正）
ok 199 G6.11 check-gate.sh P6 无 [NO_NEED_CONFIRM] 不再 WARNING（v0.30.3）
ok 200 G6.7 check-gate.sh P6 小写 fail: 被计为 FAIL（大小写不敏感）
ok 201 G_BDD16.1 BDD-16: check-gate.sh P6 frontmatter 声明 pass/fail 汇总时门禁基于该汇总判定（非正文 grep 计数）
ok 202 G6.9 check-gate.sh P6 'failure' 不被计为 FAIL
ok 203 G7.1 check-gate.sh P7 含 [BLOCKER] 期望 exit 1
ok 204 G7.2 check-gate.sh P7 含 [DEVIATION-CRITICAL] 期望 exit 1
ok 205 G7.3 check-gate.sh P7 DESIGN_GAP 未配对 期望 exit 1
ok 206 G7.4 check-gate.sh P7 DESIGN_GAP 已配对 期望 exit 0
ok 207 G7.5 check-gate.sh P7 2 GAP + 1 REVIEWED 期望 exit 1
ok 208 G7.6 check-gate.sh P7 空文件 期望 exit 0
ok 209 G7.7 check-gate.sh P7 P4 有 DESIGN_GAP 但 P7 未转抄 期望 exit 1
ok 210 G8.1 check-gate.sh P8 缺 bump_type 期望 exit 1
ok 211 G8.2 check-gate.sh P8 无 version 文件变更（暂存区）期望 WARNING（不阻断）
ok 212 G8.3 check-gate.sh P8 有 version 但 CHANGELOG 无变更 期望 exit 2 (WARNING)
ok 213 G8.4 check-gate.sh P8 全合规 期望 exit 2
ok 214 G8.5 check-gate.sh P8 无 P8 文件 期望 exit 1
ok 215 G8.7 check-gate.sh P8 tag 不存在 期望 WARNING（exit 2，不阻断）
ok 216 G8.8 check-gate.sh P8 tag 存在 期望无 tag WARNING
ok 217 D-drift-1: dispatch-prompt.md 含'返回前自检'
ok 218 D-drift-2: dispatch-prompt.md 含'files_modified'
ok 219 D-drift-4: dispatch-context.md 含 XML 派发指引节（dispatch_guide/目标/约束）
ok 220 D-drift-4b: dispatch-context.md 含 XML 标记（dispatch_guide/objective_info）
ok 221 D-drift-5: dispatch-prompt.md 含'P3 自检'
ok 222 D-drift-6: dispatch-prompt.md 含'修复轮派发追加'
ok 223 G-drift-1: dispatch-protocol.md 含'自查≠gate'关键词
ok 224 G-drift-2: implementer.md 不含'写跑分离'
ok 225 G-drift-3: verifier.md 不含'写跑分离'
ok 226 G_OTHER check-gate.sh 未知阶段 期望 exit 2
ok 227 G2.14 check-gate.sh P2 方案 A（有空格）+ 方案 B 期望 exit 2
ok 228 G_BDD10.1 BDD-10: check-gate.sh P2 candidate_count 在 frontmatter 与正文声明不同值时以 frontmatter 为准
ok 229 G2.17 check-gate.sh P2 候选方案 ≥2 + '选择'标题+正文'理由' 期望 exit 2
ok 230 G2.18 check-gate.sh P2-review agent=subagent + frontmatter status:approved → exit 2
ok 231 G2.19 check-gate.sh P2-review agent=main + frontmatter status:approved → exit 1
ok 232 G2.20 check-gate.sh P2-review 缺 agent 字段 + frontmatter status:approved → exit 2 (WARNING)
ok 233 G7.8 check-gate.sh P7 [BLOCKER]: 0 条（声明）期望 exit 0
ok 234 G7.9 check-gate.sh P7 [BLOCKER]: 0 条 + 实际 BLOCKER 期望 exit 1
ok 235 G2.7 check-gate.sh P2 h2 (##) 候选方案也被识别
ok 236 G8.6 check-gate.sh P8 CHANGELOG_FILE 环境变量覆盖
ok 237 G2.21 check-gate.sh P2 方案 Alpha（多词方案名）期望 exit 2
ok 238 G_BDD9.1 BDD-9: check-gate.sh P2-design.md 旧格式（四字段仅在正文、frontmatter 无这些字段）仍被正确读取
ok 239 G2.24 check-gate.sh P2 方案 1 + 方案 2（数字编号）期望 exit 2
ok 240 G_NC_BINARY.1 P1 含 [NO_NEED_CONFIRM] 期望 exit 2（NC=0，通过）
ok 241 G_NC_BINARY.2 P1 含行首 [NEED_CONFIRM] 描述 期望 exit 1（NC>0）
ok 242 G_NC_BINARY.3 P1 含不合规格式（句中引用）期望 exit 1（步骤 2 拦截）
ok 243 G_NC_BINARY.5 P1 既无正向也无负向声明 期望 exit 2 + WARNING
ok 244 G_NC_BINARY.6 P1 含 [NO_NEED_CONFIRM] 确认无不可逆操作（负向+描述）期望 exit 2
ok 245 G_SUGGEST.1 P1 含 [SUGGEST: X] 无阻塞项 → exit 2（不阻塞）
ok 246 G_SUGGEST.2 P1 含 [SUGGEST: X] + [NEED_CONFIRM] → exit 1（阻塞项仍在）
ok 247 G_SUGGEST.3 P1 含旧标记 [NEED_CONFIRM倾向: X] → exit 1（typo 兜底：旧标记重命名）
ok 248 G_SUGGEST.4 P1 含 [SUGGEST xxx]（漏冒号）→ exit 1（typo 兜底）
ok 249 G_DG_ANCHOR.1 P7 句中 [DESIGN_GAP: xxx]（非行首）不计入 GAP 计数
ok 250 G_DG_ANCHOR.2 P7 行首 [DESIGN_GAP: xxx] 计入 GAP 计数
ok 251 G_RETREAT.1 P1 无 OLD_PHASE（省略）→ 行为不变，P1-review.md 缺失仍 exit 1
ok 252 G_RETREAT.2 P1 OLD_PHASE=P2（回退抵达）→ exit 2，跳过完成度校验
ok 253 G_RETREAT.3 P4 OLD_PHASE=P6（回退抵达，本次 plan 的核心场景）→ exit 2
ok 254 G_RETREAT.4 P6 OLD_PHASE=P7（回退抵达）→ exit 2，即使证据目录不存在
ok 255 G_RETREAT.5 P4 OLD_PHASE=P3（正常推进方向，非回退）→ 仍按原逻辑要求代码文件
ok 256 G_RETREAT.6 OLD_PHASE 与 PHASE 相同（非法/无意义输入）→ 不触发回退检测，走原逻辑
ok 257 P1: 缺 P1-review.md 期望 exit 1
ok 258 P1: P1-review.md agent=main 期望 exit 1
ok 259 P1: P1-review.md 无 BDD 编号引用 期望 exit 1
ok 260 P1: P1-review.md status:approved + agent≠main + 含锚点 期望 exit 2
ok 261 P1: P1-review.md status:rejected 期望 exit 1
ok 262 P1: P1-review.md 缺 status 字段 期望 exit 1
ok 263 P1: frontmatter rejected + 正文含 status: approved 字面串 期望 exit 1（对抗绕过）
ok 264 P1: BDD-21 边界（未结构化解决时仍阻塞）：P1-requirements.md 含 NEED_CONFIRM 期望 exit 1
ok 265 P1: P1-requirements.md 无 NEED_CONFIRM 期望 exit 2
ok 266 PG.1 两份文件均缺失 → 走原有分支，exit 2
ok 267 PG.2 无新增失败、无预存失败 → exit 2
ok 268 PG.3 有新增失败（post 独有）→ exit 1，输出列出具体新增失败 id
ok 269 PG.4 有预存失败（pre/post 都有）、已有 known-failures.md 且登记条目足够 → exit 2
ok 270 PG.5 有预存失败、known-failures.md 不存在 → exit 1
ok 271 PG.6 预存失败已在本任务修复（pre 有、post 无）→ exit 2
ok 272 PG.7 pre-task-baseline.md 的 fail-list 为空（0 个预存失败），post 有失败 → 全部视为新增，exit 1
ok 273 PG.8 fail-list.txt 为空文件（0 个 post 失败），pre 有失败 → 全部视为预存已修复，exit 2
ok 274 PG.9 known-failures.md 存在但登记条目数 < 预存失败数 → exit 1
ok 275 PG.9a known-failures.md 登记条目数 ≥ 预存失败数 → exit 2
ok 276 PG.10 pre-task-baseline.md 缺少 captured_at_commit: → 视为损坏，exit 2
ok 277 PG.11 只有 pre-task-baseline.md 没有 fail-list.txt → 走原有分支，exit 2
ok 278 PG.12 只有 fail-list.txt 没有 pre-task-baseline.md → 走原有分支，exit 2
ok 279 E.1 check-p6-evidence.sh P6 文件不存在 期望 exit 2
ok 280 E.2 check-p6-evidence.sh P6 无 BDD 条目 期望 exit 1
ok 281 E.3 check-p6-evidence.sh PASS 缺文件引用 期望 exit 1
ok 282 E.4 check-p6-evidence.sh PASS 有引用且文件存在（基本格式）
ok 283 E.5 check-p6-evidence.sh 证据目录不存在 期望 exit 1
ok 284 E.6 check-p6-evidence.sh 证据目录完全空（无文件）期望 exit 1
ok 285 E.7 check-p6-evidence.sh 正常通过（无 UI）期望 exit 0
ok 286 E.8 BDD-1/FIND-4: check-p6-evidence.sh ui_affected: true（frontmatter/正文均可）+ 截图目录空 期望 exit 1
ok 287 E.9 check-p6-evidence.sh UI 任务 + 截图 ≤ 1KB 期望 exit 1
ok 288 E.10 check-p6-evidence.sh UI 任务 + 截图 ≥ 1KB 通过 期望 exit 0
ok 289 E.11 check-p6-evidence.sh 多种文件后缀（.log .json .html .txt .yaml）
ok 290 E.12 check-p6-evidence.sh UI 任务 + 重复截图（md5 相同）期望 exit 1 (阻断)
ok 291 E.14 check-p6-evidence.sh PASS 引用带附加内容 (path.png, vision: OK) 期望 exit 0
ok 292 EVID_EXT.1 check-p6-evidence.sh PASS 引用 .pdf 文件 期望 exit 0
ok 293 EVID_EXT.2 check-p6-evidence.sh PASS 引用 .jpeg 文件 期望 exit 0
ok 294 EVID_EXT.3 check-p6-evidence.sh PASS 引用逗号分隔的 2 个证据文件 期望 exit 0
ok 295 EVID_EXT.4 check-p6-evidence.sh PASS 含 nth(1) 嵌套括号 + 单一证据路径 期望 exit 0
ok 296 EVID_EXT.5 check-p6-evidence.sh PASS 括号内容是纯版本号 (v2.0) 期望 exit 0（evidence 层放行）
ok 297 EVID_EXT.6 check-p6-evidence.sh PASS 括号内容是纯描述文字无路径结构 期望 exit 1
ok 298 EVID_EXT.7 check-p6-evidence.sh 现有 png/jpg/log/json/html/txt/yaml/yml 用例保持 exit 0（回归）
ok 299 E.13 check-p6-evidence.sh UI 任务 + 不同截图（md5 不同）期望 exit 0
ok 300 EVIDENCE_NO_REF_DETAIL.1 PASS 缺引用时错误消息含具体 PASS 行
ok 301 EVIDENCE_EMPTY_DETAIL.1 小文件错误消息含具体 basename
ok 302 EVIDENCE_MD5_DETAIL.1 md5 重复错误消息含具体 basename
ok 303 EVIDENCE_MD5_DETAIL.2 md5 重复文件名含空格时错误消息含完整 basename
ok 304 E.15 ui_affected=true + evidence 全是 .md/.txt → exit 1
ok 305 E.16 ui_affected=true + evidence 含 .json → exit 0
ok 306 E.17 ui_affected=false + evidence 全是 .md/.txt → exit 0（非 UI 不检查类型）
ok 307 F1 check-p6-format.sh --check: clean file → exit 0
ok 308 F2 check-p6-format.sh --check: lowercase pass → exit 1
ok 309 F3 check-p6-format.sh --fix: lowercase pass → auto-fix → exit 0
ok 310 F5 check-p6-format.sh --check: no P6 file → exit 0
ok 311 F_BDD17.1 BDD-17: check-p6-format.sh --check 行首 - PASS|FAIL BDD-NN: 格式被识别为有效逐条结果
ok 312 F8 check-p6-format.sh --check: lowercase fail: → exit 1
ok 313 F9 check-p6-format.sh --fix: lowercase fail with space → auto-fix
ok 314 F10 check-p6-format.sh --fix: 'failure' NOT matched (word boundary)
ok 315 F_BDD18.1 BDD-18: check-gate.sh P6 审计口径不把总结行（- PASS: 16，无 BDD 编号）计入逐条 PASS/FAIL 总数
ok 316 F12 check-p6-format.sh --fix: summary line - PASS：34 → **Summary**: PASS: 34
ok 317 PV.1 check-p6-provenance.sh 无 P6 文件 期望 exit 0
ok 318 PV.2 check-p6-provenance.sh PASS 引用不存在的文件 期望 exit 1
ok 319 PV.3 check-p6-provenance.sh (vision: ...) 引用被剥离不当文件路径
ok 320 PV.4 check-p6-provenance.sh 行末多个括号取最后一个（a.png 不存在但 b.png 存在）
ok 321 PV.4b check-p6-provenance.sh 行末多括号 + 全部不存在 期望 exit 1
ok 322 PV_BDD19.1 BDD-19: check-gate.sh P7 frontmatter blocker_count/deviation_count 均 0 时判定通过（不再用非计数行排除正则）
ok 323 PV.5b check-p6-provenance.sh 14 PASS 引用 8 共享证据文件 期望 exit 0
ok 324 PV.6 check-p6-provenance.sh 证据文件未被引用（充数文件）期望 exit 1
ok 325 PV.7 check-p6-provenance.sh .gitkeep 算隐藏文件不计入证据（exit 0）
ok 326 PV.8 check-p6-provenance.sh dispatch-context 含 PASS 预判 期望 exit 1
ok 327 PV.9 check-p6-provenance.sh P1 BDD 标题数 > P6 总数 期望 exit 1
ok 328 PV.10 check-p6-provenance.sh P1 无标准 BDD 标题 期望 exit 1（无过渡期兜底）
ok 329 PV_BDD_COUNT.1 P1 含 3 条 #### BDD-NN，P6 有 3 条 PASS 期望 exit 0
ok 330 PV_BDD_COUNT.4 P1 含 1 条带 Examples 表的 BDD-NN，P6 有 1 条 PASS 期望 exit 0（数据驱动共享编号）
ok 331 PV_BDD_COUNT.5 P1 BDD 编号有间隔（BDD-1,BDD-3，无 BDD-2），P6 有 2 条 PASS 期望 exit 0（按标题计数非 max 编号）
ok 332 PV.11 check-p6-provenance.sh UI + 截图 PASS 缺 vision 引用 期望 exit 1
ok 333 PV.12 check-p6-provenance.sh vision YAML 文件不存在 期望 exit 1
ok 334 PV.13 check-p6-provenance.sh vision YAML blocker_count != 0 期望 exit 1
ok 335 PV.14 check-p6-provenance.sh P6 缺 agent 字段 期望 exit 2（WARNING）
ok 336 PV.15 check-p6-provenance.sh risk=high + P2-review agent=main 期望 exit 0（agent=main 检查已移至 check-gate.sh）
ok 337 PV.17 dispatch-context 含任务上下文节 → 审计 2 放行
ok 338 PV.18 check-p6-provenance.sh PASS 行含嵌套括号描述如 nth(1) → 提取 screenshots/ 路径（exit 0）
ok 339 PV.19 check-p6-provenance.sh PASS 行含嵌套括号 + vision 引用 → 提取 screenshots/ 路径（exit 0）
ok 340 PV.20 check-p6-provenance.sh PASS 行含嵌套括号且路径不存在 → exit 1 + 含具体路径
ok 341 PV.21 审计5: 日志 EXIT_CODE=1 但 P6 声明 PASS → exit 1
ok 342 PV.22 审计5: 日志 EXIT_CODE=0 配 PASS → exit 0
ok 343 PV.23 审计5: 日志缺少 EXIT_CODE 尾行 → WARNING 不阻断
ok 344 PROV_MULTI.1 PASS 行引用 2 个逗号分隔的证据文件，均存在 → exit 0
ok 345 PROV_MULTI.2 PASS 行引用 2 个逗号分隔的证据文件，其中 1 个不存在 → exit 1 + 报告缺失
ok 346 PV_BDD20.1 BDD-20: check-gate.sh P7 frontmatter design_gap_reviewed_count < design_gap_count 时拦截（不再用数量相减的 0-vs-0 歧义判定）
ok 347 PV.DP1: dispatch-prompt file excluded from agent field check
ok 348 PV.24 审计6: evidence JSON shows FAIL but P6 says PASS → exit 1
ok 349 PV.25 审计6: evidence JSON all pass + P6 all PASS → exit 0
ok 350 PV.26 审计6: non-standard evidence JSON (no bdd_results) → silent skip, exit 0
ok 351 PV.27 审计6: P6 says FAIL + evidence JSON says fail → consistent, exit 0
ok 352 PV.28 审计6: agent 字段缺失 + evidence 矛盾 → 仍应 exit 1（不被 agent 检查短路）
ok 353 CHECK 9: EXIT_CODE 锚点存在且关键词匹配
ok 354 CHECK 9: AGATE_ALIGNMENT_REVIEW_THRESHOLD 锚点存在
ok 355 CHECK 9: ci-gate-backstop.py 被纳入 anchor coverage 扫描范围
ok 356 P2.1 check-pruning.sh 缺 risk_level 期望 exit 1
ok 357 P2.2 check-pruning.sh 裁剪 P2 期望 exit 1
ok 358 P2.3a check-pruning.sh 裁剪 P2 + legacy_p2_pruned 期望 exit 1
ok 359 P2.3b check-pruning.sh 裁剪 P2 + design_trivial 期望 exit 1
ok 360 P2.3c check-pruning.sh 裁剪 P2 + follows_existing_pattern 期望 exit 1
ok 361 P2.4 check-pruning.sh 裁剪 P6 期望 exit 1
ok 362 P2.4a check-pruning.sh 裁剪 P6 + no_behavior_change 期望 exit 1
ok 363 P2.5c check-pruning.sh P4 裁剪 期望 exit 1
ok 364 P2.5d check-pruning.sh P5 裁剪 期望 exit 1
ok 365 P2.5 BDD-9: check-pruning.sh 旧格式（--legacy-fields，risk_level 在正文非 frontmatter）risk=high 裁剪 P3 期望 exit 1（回退路径行为与 v0.35 一致）
ok 366 P2.5b check-pruning.sh risk=medium 裁剪 P3 期望 exit 1（P1-8: 仅 low 可裁）
ok 367 P2.6a check-pruning.sh 裁剪 P7，源文件数 > 5 期望 exit 1
ok 368 P2.6b check-pruning.sh 裁剪 P7，源文件数 ≤ 5 + coupling_checklist 通过
ok 369 P2.6c BDD-1: check-pruning.sh 裁剪 P7 + frontmatter implicit_coupling 字段 期望 exit 1
ok 370 P2.6d check-pruning.sh 裁剪 P7 无 coupling_checklist 期望 exit 1
ok 371 P2.6e check-pruning.sh 裁剪 P7 + coupling_checklist 放行
ok 372 P2.7 check-pruning.sh 裁剪 P8 无 internal_only 期望 exit 1
ok 373 P2.7a BDD-1: check-pruning.sh 裁剪 P8 + frontmatter internal_only: true + internal_only_reason 放行
ok 374 P2.8 check-pruning.sh 裁剪理由缺'跳过风险' 期望 exit 1
ok 375 P2.12 check-pruning.sh P6 裁剪无跳过风险 期望 exit 1
ok 376 P2.12a check-pruning.sh P6 裁剪 + no_behavior_change + 跳过风险 期望 exit 1
ok 377 P2.13 check-pruning.sh 裁剪 P8 有 internal_only 无 reason 期望 exit 1
ok 378 P2.14 check-pruning.sh 裁剪 P8 + internal_only + internal_only_reason 期望 exit 0
ok 379 P2.9 check-pruning.sh 裁剪声明 vs 实际有产出文件 + 无 override 期望 exit 1
ok 380 P2.9a check-pruning.sh 裁剪 P2 + override + 产出文件 期望 exit 1 (P2 不可裁)
ok 381 P2.10 check-pruning.sh 无 P1 文件 期望 exit 2
ok 382 P2.11 check-pruning.sh 全合规 (happy path) 期望 exit 0
ok 383 P2.52: YAML list format phases: - P1\n - P2 → parsed correctly
ok 384 P2.52b: YAML list format phases with P3 pruned (risk=low) → pass
ok 385 RT.1 check-retrospective.sh 无异常 期望 exit 0 + 无输出
ok 386 RT.2 check-retrospective.sh retries 超限 期望 exit 0 + 含'重试超限'
ok 387 RT_BDD21.1 BDD-21: check-gate.sh P1 frontmatter need_confirm_resolved 已覆盖具体描述时该 NEED_CONFIRM 项不再阻塞
ok 388 RT.DP1: dispatch-prompt file excluded from SCOPE+ scan
ok 389 RT.4 check-retrospective.sh override 触发 期望 exit 0 + 含'override'
ok 390 RT.5 check-retrospective.sh retries[P3]=2 触发超限（P3 MAX=2）
ok 391 RT.6 check-retrospective.sh retries[P3]=1 不触发（P3 MAX=2 未达）
ok 392 RT.7 句中 [SCOPE+]（非行首）不触发复盘提醒 期望 exit 0 + 无输出
ok 393 RETRO_SCOPE_DC.1 dispatch-context 含 [SCOPE+] 不触发复盘提醒
ok 394 RETRO_SCOPE_CARD.1 AGATE_CARD 块内 [SCOPE+] 不触发复盘提醒
ok 395 SC.1 check-scope-resolved.sh 不存在的 task 目录 期望 exit 2
ok 396 SC.2 check-scope-resolved.sh 无 SCOPE+ 触发 期望 exit 0
ok 397 SC.3 check-scope-resolved.sh 有 SCOPE+ 但无 P1 文件 期望 exit 1
ok 398 P2.53: progress file with [SCOPE+] text does not trigger SCOPE check
ok 399 SC.DP1: dispatch-prompt file excluded from SCOPE+ scan
ok 400 SC.4 check-scope-resolved.sh 有 SCOPE+ 但 P1 无 SCOPE_RESOLVED 期望 exit 1
ok 401 SC.5 check-scope-resolved.sh 有 SCOPE+ + P1 有 [SCOPE_RESOLVED] 期望 exit 0
ok 402 SC_BDD22.1 BDD-22: check-scope-resolved.sh 有 SCOPE+ + P1 frontmatter scope_resolved 非空列表 → 闭环判定通过
ok 403 SC.6 dispatch-context 文件中的 [SCOPE+] 字面引用不触发检查
ok 404 SC.7 句中 [SCOPE+]（非行首）不触发检查 期望 exit 0
ok 405 ST.1 check-state-transition.sh 无 .state.yaml 暂存 期望 exit 0
ok 406 ST.2 check-state-transition.sh 新 phase: P1（首次）期望 exit 0
ok 407 ST.3 check-state-transition.sh 顺序跳 P1→P3（差 2）期望 exit 0
ok 408 ST.4 check-state-transition.sh 回退 P3→P1（差 2）期望 exit 1（强制 PAUSED）
ok 409 ST.5 check-state-transition.sh 回退 P4→P2（差 2）期望 exit 1（强制 PAUSED）
ok 410 ST.6 check-state-transition.sh retries[P2]>=3 + phase 非 PAUSED 期望 exit 1
ok 411 ST.7 check-state-transition.sh retries[P2]>=3 + phase: PAUSED 期望 exit 0
ok 412 ST.8 check-state-transition.sh 终止态 PAUSED/READY/DONE 期望 exit 0
ok 413 ST.9 check-state-transition.sh retries[P3]>=2 + phase 非 PAUSED 期望 exit 1（P3 MAX=2）
ok 414 ST.10 check-state-transition.sh retries[P5]>=2 + phase 非 PAUSED 期望 exit 1（P5 MAX=2）
ok 415 ST.11 check-state-transition.sh 多阶段 retries 不同阈值 期望 exit 0（P2:2 不超, P3:1 不超）
ok 416 ST.12 check-state-transition.sh retries[P2]=3 + retries[P3]=2 期望 exit 1（任一超限）
ok 417 ST.13 check-state-transition.sh 回退 P3→P1（差 2）期望 exit 1（恢复强制 PAUSED）
ok 418 ST.14 check-state-transition.sh 回退 P4→P2（差 2）期望 exit 1（恢复强制 PAUSED）
ok 419 ST.15 check-state-transition.sh PAUSED→P3 恢复 期望 exit 0（验证 old_num 守卫）
ok 420 ST.16 commit gate: P1→P2 推进，P1 产出已 commit → exit 0
ok 421 ST.17 commit gate: P1→P2 推进，P1 产出与 phase 推进在同一 commit → exit 0（模式 B）
ok 422 ST.18 commit gate: P1→P2 推进，P1 产出不存在 → exit 0（产出存在性由 check-gate.sh 检查）
ok 423 ST.19 commit gate: PAUSED→P3 恢复 → 跳过 commit gate
ok 424 ST.20 commit gate: P3→P1 回退 → 跳过 commit gate
ok 425 ST_ARCHIVE.1 回退 P6→P5，P6-acceptance.md 仍在原位（未归档）期望 exit 1
ok 426 ST_ARCHIVE.2 回退 P6→P5，P6-acceptance.md 已被归档（原位不存在）期望 exit 0
ok 427 ST_ARCHIVE.3 回退 P5→P4（P5 不在 self-authored 名单）不受归档检查影响
ok 428 ST_ARCHIVE.4 前进 P4→P5（非回退方向）不触发归档检查
ok 429 ST_ARCHIVE.5 回退 P1->P0（退到起始阶段），P1-review.md 仍在原位 -> 不触发归档检查（与检查 1 一致，P0 是起始阶段）
ok 430 ST_ARCHIVE.6 回退 P2->P1，P2-design.md 已归档但 P2-review.md 仍在原位 期望 exit 1
ok 431 SY.1 check-state-yaml.sh 无 .state.yaml 期望 exit 2
ok 432 SY.2 check-state-yaml.sh 空文件 期望 exit 1
ok 433 SY.3 check-state-yaml.sh 缺 task_id 期望 exit 1
ok 434 SY.4 check-state-yaml.sh task_id 格式错 期望 exit 1
ok 435 SY.5 check-state-yaml.sh phase 非法值 期望 exit 1
ok 436 SY.6 check-state-yaml.sh retries 非 dict 期望 exit 1
ok 437 SY.7 check-state-yaml.sh retries[P1] 非 list 期望 exit 1
ok 438 SY.8 check-state-yaml.sh 全合规 期望 exit 0
ok 439 SY.9 check-state-yaml.sh YAML 语法错 期望 exit 1
ok 440 TD.1 check-tdd-red.sh TEST_RUNNER 指向不存在 + 无 pytest 期望 exit 1
ok 441 TD.1b check-tdd-red.sh 无 TEST_RUNNER + 无 pytest（无 PATH 找不到 pytest）期望 exit 3
ok 442 TD.2 check-tdd-red.sh 测试全绿 期望 exit 2（实现先于测试）
ok 443 TD.3 check-tdd-red.sh 经典红灯（assertion failure）期望 exit 0
ok 444 TD.4 check-tdd-red.sh B 类：项目内 import 失败 期望 exit 0
ok 445 TD.5 check-tdd-red.sh A 类：第三方 import 失败 期望 exit 1
ok 446 TD.6 check-tdd-red.sh A 类：SyntaxError 期望 exit 1
ok 447 TD.7 check-tdd-red.sh 混合：1 failed + 1 B 类 error 期望 exit 0
ok 448 TD.8 check-tdd-red.sh 无 PROJECT_MODULE + ImportError 期望 exit 0（启发式）
ok 449 TDD.N1: TEST_RUNNER without formatter does not add -q
ok 450 TDD.N2: vitest pure assertion failure → red-light exit 0
ok 451 TDD.N3: vitest B-class → exit 0
ok 452 TDD.N4: vitest A-class → exit 0 (exit-code-only without formatter)
ok 453 TDD.G1: BDD-15 回归：gate_commands.P3 保持正文（不迁移 frontmatter）→ auto-read, red-light exit 0
ok 454 TDD.G2: no gate_commands.P3 → TEST_RUNNER still works (backward compat)
ok 455 TDD.G3: TEST_RUNNER env var takes priority over gate_commands.P3
ok 456 TDD.G4: no TASK_DIR → skip gate_commands read, fall back to TEST_RUNNER
ok 457 TDD.G5: gate_commands.P3 with double-quoted value → strip quotes
ok 458 TDD.F1: gate_commands.P3 + P3_formatter → auto-read both, classic red-light exit 0
ok 459 TDD.F2: gate_commands.P3 without formatter → exit-code-only, red-light exit 0
ok 460 TDD.F3: formatter detects B-class (import from project_module) → exit 0 + B-class
ok 461 TDD.F4: formatter detects A-class (SyntaxError) → exit 1 + A-class
ok 462 TDD.F11: absolute path formatter works
ok 463 TDD.F12: PROJECT_MODULE env var overrides gate_commands project_module
ok 464 TDD.F5: formatter detects A-class (import NOT from project_module) → exit 1 + A-class
ok 465 TDD.F6: green light (exit 0) → exit 2
ok 466 TDD.F7: TEST_RUNNER env var still works (backward compat, exit-code-only)
ok 467 TDD.F8: no TEST_RUNNER, no gate_commands.P3, no pytest → exit 3
ok 468 TDD.F9: no formatter → command runs without -q
ok 469 TDD.F10: multi-stack P3 + P3_js → both run, combined result → exit 0
ok 470 TD.FAIL_HINT: classic red-light outputs assertion-mismatch hint
ok 471 TDD.TIMEOUT: 测试命令超时 → exit 0 + 超时提示
ok 472 PYX.1 agate-read-gate-commands.py P2 含 P3 + P3_html_formatter + project_module
ok 473 PYX.2 agate-read-gate-commands.py P2 无 gate_commands → 空 JSON
ok 474 PYX.3 agate-read-gate-commands.py P2 双引号值被去除
ok 475 PYX.4 agate-read-gate-commands.py P2 单引号值被去除
ok 476 PYX.5 agate-read-gate-commands.py P2 末行无换行也能解析
ok 477 PYX.6 agate-read-gate-commands.py GATE_FILE 不存在 → 非零退出
ok 478 FMT.1: generic-exit-only.sh exit 1 → exit_code=1, empty arrays
ok 479 FMT.2: generic-exit-only.sh exit 0 → exit_code=0
ok 480 FMT.3: pytest.sh (2 failed, 5 passed) → failed=2, passed=5, errors=0, failed_tests has 2
ok 481 FMT.4: pytest.sh B-class (ImportError from myapp.foo) → import_errors[0].module=='myapp.foo'
ok 482 FMT.5: pytest.sh A-class (SyntaxError) → syntax_errors non-empty
ok 483 FMT.6: pytest.sh all passed → passed=5, failed=0
ok 484 FMT.7: vitest.sh (11 failed, 6 passed) → failed=11, errors=0, import_errors=[]
ok 485 FMT.8: vitest.sh B-class (Cannot find module '../src/bar') → import_errors[0].module=='../src/bar'
ok 486 FMT.9: vitest.sh A-class (Cannot find module 'react') → import_errors[0].module=='react'
ok 487 FMT.10: go-test.sh cargo format (2 passed, 1 failed) → failed=1, failed_tests contains 'foo::test_bar'
ok 488 FMT.11: generic-tap.sh (2 ok, 1 not ok) → passed=2, failed=1, failed_tests contains 'test gamma'
ok 489 FMT.12: generic-junit-xml.sh (tests=3, failures=1, errors=1) → total=3, failed=1, errors=1, passed=1
ok 490 detect_ci_platform: Gitea 优先于 GitHub 被识别
ok 491 detect_ci_platform: GitLab CI 正确识别
ok 492 detect_ci_platform: 无可识别平台时 SKIP 而非误判
ok 493 backstop P3: 真红灯（exit 0）→ PASS
ok 494 backstop P3: 绿灯（exit 2）→ FAIL
ok 495 backstop P3: 假红灯（exit 1）→ FAIL
ok 496 backstop P3: 无运行器（exit 3）→ WARN 不 FAIL
ok 497 backstop P3: 无 .gate-result.json（--no-verify）时仍执行 check-tdd-red.sh
ok 498 commit-msg-self-gate: .sh 文件触发 self-gate WARNING
ok 499 commit-msg-self-gate: .py 文件触发 self-gate WARNING
ok 500 commit-msg-self-gate: 非 agate .py 文件不触发
ok 501 commit-msg-self-gate: self-gate-review: 路径消除 WARNING
ok 502 B3-warning: 产出暂存缺 dispatch-context → WARNING
ok 503 install-hook: .gitignore 忽略 .state.yaml → WARNING 提醒
ok 504 install-hook: 无 .gitignore → 无 WARNING
ok 505 install-hook: pre-push 是软链指向 pre-push-gate.sh
ok 506 install-hook: 已有非软链 pre-push → 备份并替换为软链
ok 507 install-hook: ln 退化为复制时打印升级提醒（Windows 兼容）
ok 508 R2.1 BDD-20: frontmatter design_gap_count == design_gap_reviewed_count（已全部配对）→ exit 0
ok 509 R2.2 BDD-20: frontmatter design_gap_reviewed_count(0) < design_gap_count(1) → exit 1（未配对）
ok 510 R2.3 P4 有 DESIGN_GAP 但 P7 frontmatter design_gap_count 为 0（未转抄）→ exit 1（交叉核对，回归 R2.3）
ok 511 R2.3b BDD-20: P4 DESIGN_GAP 数量 ≤ P7 frontmatter design_gap_count 且已 REVIEWED → exit 0
ok 512 R5.1 P8 gate 暂存区有 version + CHANGELOG → exit 2（脚本化通过）
ok 513 R5.2 P8 gate 暂存区无 version 文件 → WARNING（P1-6: 降级非阻断）
ok 514 R5.3 P8 gate 暂存区有 version 但 CHANGELOG 无变更 → exit 2 (WARNING)
ok 515 R4.1 裁剪 P8 无 internal_only → exit 1
ok 516 R4.2 BDD-1: 裁剪 P8 + frontmatter internal_only: true + internal_only_reason → exit 0
ok 517 R4.3 BDD-1: 裁剪 P8 + frontmatter internal_only: true 但无 internal_only_reason → exit 1
ok 518 R3.1 裁剪 P7 + 暂存区 6 个源文件 → exit 1（源码文件数 > 5 拦截）
ok 519 R3.2 BDD-1: 裁剪 P7 + 暂存区 3 个源文件 + frontmatter coupling_checklist → exit 0（≤ 5）
ok 520 R1.1 task-files.md executor_env 块 YAML 可解析
ok 521 R1.2 task-files.md executor_env: 顶格（无前导空格）
ok 522 R1.3 task-files.md executor_env 子字段 2 空格缩进
ok 523 CSG.1 非触发文件改动 → 无 WARNING
ok 524 CSG.2 触发文件改动 + 无 review 路径 → WARNING
ok 525 CSG.3 触发文件改动 + 有 review 路径 → 无 WARNING
ok 526 CSG.4 触发文件改动 + self-gate-skip → 无 WARNING
ok 527 CSG.5 agate/scripts/*.sh 改动触发
ok 528 CSG.6 agate/*.md 改动触发
ok 529 CON.1 CHECK 1: YAML 代码块可解析
ok 530 CON.2 CHECK 2: 文件引用存在
ok 531 CON.3 CHECK 3: 无硬编码行号
ok 532 CON.4 CHECK 4: gate_commands 键集合一致
ok 533 CON.5 CHECK 6: LICENSE 归属
ok 534 CON.6 CHECK 7: version badge 同步
ok 535 CON.8 BDD-13: CHECK 9 协议-脚本结构对齐（含新增 check-frontmatter.sh 锚点，37→38）
ok 536 CON.9 CHECK 9: md5 去重锚点已实现
ok 537 CON.10 CHECK 8: v0.6 关键词存在性
ok 538 CON.11 CHECK 9: PROD_TOUCHED 锚点含 PROD_NOT_TOUCHED
ok 539 CON.12 CHECK 9: NEED_CONFIRM 三值锚点存在（v0.30.2 起 SUGGEST）
ok 540 DC.1 dispatch-context-{role}.md 含正确卡片 hash → commit 不因 hash mismatch 被拦
ok 541 DC.2 dispatch-context-{role}.md 卡片被篡改 → hash mismatch
ok 542 DC.3 dispatch-context-{role}.md 空卡片块 → hash mismatch
ok 543 DC.4 派发阶段 (P2) 产出 commit 缺 dispatch-context → exit 1
ok 544 DC.5 P5 产出 commit 缺 dispatch-context → 拦截
ok 545 DC.6 P7 产出 commit 缺 dispatch-context → 拦截
ok 546 DC.7 P8 产出 commit 缺 dispatch-context → 拦截
ok 547 DC.multi 同一阶段多个 dispatch-context 文件 → 逐个校验 hash
ok 548 IT.1 pre-commit-hook 无 .state.yaml 变更 不触发
ok 549 IT.2 pre-commit-hook phase 变更 + gate 通过
ok 550 IT.3 pre-commit-hook 句中提及 [PROD_TOUCHED]（非行首声明）→ 不中止（T090 修复）
ok 551 IT.4 pre-commit-hook .state.yaml phase 变更触发 state-yaml 校验
ok 552 IT.5 pre-commit-hook .state.yaml 格式校验（任何变更都触发）
ok 553 IT.6 pre-commit-hook 多任务：任务级 .state.yaml + P1 产出 → 正常 commit
ok 554 IT.7 pre-commit-hook 多任务：P4 产出但 phase 仍 P3 → WARNING 不拦截
ok 555 IT.8 pre-commit-hook 多任务：phase 变更到 P2 但无 P2-design.md → 拦截
ok 556 IT.9 pre-commit-hook 多任务：裁剪跳阶 P2→P5 无 P3 产出（low 风险）→ 不拦截
ok 557 IT.9b pre-commit-hook 裁剪跳阶 P3 medium 风险 → 拦截（P1-8: 仅 low 可裁 P3）
ok 558 IT.10 pre-commit-hook 向后兼容：根 .state.yaml 仍工作
ok 559 IT.11 pre-commit-hook P2 阶段暂存代码文件 → WARNING
ok 560 IT_PT_BINARY.1 暂存 diff 含行首 [PROD_TOUCHED] 描述 → 中止 commit（步骤 1）
ok 561 IT_PT_BINARY.2 暂存 diff 含 [PROD_NOT_TOUCHED] → 不中止
ok 562 IT_PT_BINARY.3 暂存 diff 含删除行 [PROD_TOUCHED] → 不中止（只扫 ^+ 行）
ok 563 IT_PT_BINARY.4 暂存 diff 含句中引用 [PROD_TOUCHED]（非行首声明）→ 不中止（T090 修复）
ok 564 IT_PT_BINARY.5 暂存 diff 含句中引用 [PROD_TOUCHED]（非行首声明）→ 不中止（T090 修复）
ok 565 IT_PT_BINARY.6 暂存 diff 既无正向也无负向 → 不中止 + 无 WARNING（步骤 3 静默通过）
ok 566 IT_PHASE_SPAN.1 新增 P1/P2 产出文件 phase=P3（历史产出晚提交）→ 不报 WARNING
ok 567 IT_PHASE_SPAN.2 已存在 P1 产出被重新暂存 phase=P3 → 报 WARNING（真实过期）
ok 568 IT_PHASE_SPAN.3 新增 P4 产出文件 phase=P3（提前产出）→ 报 WARNING
ok 569 IT_PHASE_SPAN.4 多任务场景：T001 历史产出晚提交不 WARNING / T002 已存在产出修改报 WARNING / T003 提前产出报 WARNING
ok 570 IT_PHASE_SPAN.5 phase=PAUSED 暂存阶段号不符文件 → 不崩溃、报 WARNING、无 integer expression expected
ok 571 IT_PT_BINARY.7 暂存 diff 含 [PROD_NOT_TOUCHED] 确认未接触（负向+描述）→ 不中止
ok 572 IT_PT_MENTION.1 正文句中提及 [PROD_TOUCHED]（非行首声明）→ 不误报（T090 修复）
ok 573 IT_P6_CODE.1 phase=P6，暂存 P6-evidence/ 下截图 → 不拦（证据文件例外）
ok 574 IT_P6_CODE.1b phase=P6，暂存 evidences/ 下截图 → 不拦（T090 白名单修复）
ok 575 IT_P6_CODE.2 phase=P6，暂存项目源码文件 → exit 1 硬拦截
ok 576 IT_P6_CODE.3 phase=P4，暂存源码文件 → 不拦（回归）
ok 577 IT_P6_CODE.4 phase=P5，暂存源码文件 → 不拦（回归）
ok 578 IT_P6_CODE.5 phase=P2，暂存源码文件 → WARNING 而非硬拦截（回归，现有行为不变）
ok 579 IT_RETREAT.1 agate-retreat-to.sh 在装了真实 hook 的仓库里，每一步都真的过 hook 校验
ok 580 IT_RETREAT.2 中途一步的 commit 被 hook 拒绝时，agate-retreat-to.sh 明确报告停在哪步且不继续
ok 581 IT_PT_T6.1 P8 dispatch-context 含 AGATE_CARD 注入块（[PROD_TOUCHED] 说明文本）→ 不误拦
ok 582 IT_PT_T6.2 任务产出文件含句中 [PROD_TOUCHED]（非 AGATE_CARD 块内）→ 不拦截（T090 修复）
ok 583 IT_PT_T6.3 任务产出文件含行首 [PROD_TOUCHED]（步骤1）→ 拦截（回归）
ok 584 IT_PT_T6.4 任务产出文件含 [PROD_NOT_TOUCHED]（负向声明）→ 不拦截（回归）
ok 585 IT_CHANGELOG_P54: P4 commit without CHANGELOG → no CHANGELOG WARNING
ok 586 IT_CHANGELOG_P54b: P8 commit without CHANGELOG → CHANGELOG WARNING
ok 587 IT_GATE_REAL.1: hook runs check-gate.sh and writes real .gate-result.json
ok 588 HOOK_EVIDENCE_WARNING: P6 截图触发低方差 WARNING → commit 不应被拦截（T086 修复）
ok 589 pre-commit hook: AGATE_ROOT 未设时自定位到脚本自身本体（worktree 支持，T086）
ok 590 pre-push hook: 新分支首次推送提示跳过检测
ok 591 pre-push hook: 大改动触发提示
ok 592 pre-push hook: 无 agate/*.md 改动时零匹配 → 不报整数表达式错误（T086 回归）
ok 593 SG.1 角色文件 protocol-alignment-review.md 存在且含必需 frontmatter
ok 594 SG.2 角色文件含 A1-A6 审查清单
ok 595 SG.3 角色文件含 NEEDS_HUMAN_REVIEW 闭环规则 + HUMAN_CONFIRMED 标记
ok 596 SG.4 SELF-GATE.md 含派发模板
ok 597 SG.5 SELF-GATE.md 含检查清单
ok 598 SG.6 CHECK 9 锚点表覆盖全部 11 个 gate 脚本
ok 599 SG.7 commit-msg-self-gate.sh 存在且可执行
ok 600 SG.8 SELF-GATE.md 含递归终止条件
EXIT_CODE=0
```

---

## 命令 2／4：P5_consistency

```
python3 agate/scripts/check-protocol-consistency.py
```

结果：CHECK 1/2/3/4/6/7/8/9 全部 ✅ PASS，0 个 ERROR。注意：输出中没有 CHECK 5——核实脚本源码 agate/scripts/check-protocol-consistency.py 第 79 行注释明确写着「CHECK 5（协议文件计数声明）已删除：8 文件必读框架不再适用，Phase Card 取代它作为默认入口」，即 CHECK 5 是此前版本主动移除的检查项，非本次运行遗漏或失败。dispatch-context 中『CHECK 1-9 全 PASS』的预期表述与脚本现状（8 项检查、编号非连续）不完全一致，如实记录此差异，供主 Agent 判断是否需要更新表述。

完整输出：
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

EXIT_CODE=0
```

---

## 命令 3／4：P5_shellcheck

```
shellcheck -S warning agate/scripts/*.sh
```

结果：无任何输出，0 条 warning 级别及以上诊断，EXIT_CODE=0

完整输出（含 EXIT_CODE 标记行）：
```
EXIT_CODE=0
```

---

## 命令 4／4：P5_count

```
bash agate/tests/scripts/count-tests.sh
```

结果：总计 594 个测试用例（sanity.bats 的 6 个另计，不含在 594 内），与 P2-dispatch-context 声明的基线一致，EXIT_CODE=0

完整输出：
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
  unit/agate-next-card.bats                           20 个 @test
  unit/agate-read-p5-commands.bats                     4 个 @test
  unit/agate-render-dispatch-prompt.bats              16 个 @test
  unit/agate-retreat-state.bats                        3 个 @test
  unit/agate-retreat-to.bats                           5 个 @test
  unit/agate-state-get.bats                            6 个 @test
  unit/agate-state-yaml-check.bats                     3 个 @test
  unit/agate-vision-blocker.bats                       2 个 @test
  unit/check-changelog.bats                            8 个 @test
  unit/check-frontmatter.bats                         10 个 @test
  unit/check-gate.bats                                97 个 @test
  unit/check-gate-p1-review.bats                       9 个 @test
  unit/check-gate-p5-diff.bats                        13 个 @test
  unit/check-p6-evidence.bats                         28 个 @test
  unit/check-p6-format.bats                           10 个 @test
  unit/check-p6-provenance.bats                       36 个 @test
  unit/check-protocol-consistency.bats                 3 个 @test
  unit/check-pruning.bats                             29 个 @test
  unit/check-retrospective.bats                       10 个 @test
  unit/check-scope-resolved.bats                      10 个 @test
  unit/check-state-transition.bats                    26 个 @test
  unit/check-state-yaml.bats                           9 个 @test
  unit/check-tdd-red.bats                             38 个 @test
  unit/check-tdd-red-formatter.bats                   12 个 @test
  unit/ci-gate-backstop.bats                           8 个 @test
  unit/commit-msg-self-gate.bats                       4 个 @test
  unit/dispatch-context-warning.bats                   1 个 @test
  unit/install-hook.bats                               5 个 @test
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
总计：594 个测试用例

如果此数字与 docs/plans/agate-test-plan-2026-07-01.md 附录 A 不一致
→ 文档漂移，需要更新。
如果文档改了但 .bats 文件没动 → 测试计划空头支票。
EXIT_CODE=0
```

---

## 预存失败

本次全量实跑（bats 600/600、consistency 0 ERROR、shellcheck 0 警告、count-tests 594）未发现任何失败，因此无预存失败需要登记，也无需创建 known-failures.md。

## 未运行全量测试声明

本次已运行全量测试套件（sanity + unit + regression + integration，600 个 @test），非子集。
