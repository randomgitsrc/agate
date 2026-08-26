# P6-progress.md — TAG0025 verifier 分阶段落盘记录

## 2026-08-25T22:42:53Z 读取输入
- 已读 verifier.md 模式二（P6验收）、P6-dispatch-context-verifier.md、P1-requirements.md（16条BDD）、P5-test-results/unit.md、env-rename-handoff.md、P0-brief.md
- 确认本任务 ui_affected: false，全部证据为文本类命令输出，不涉及 Playwright/vision

## BDD-1~3（品牌声明）已独立实跑，均 PASS
- BDD-1: head -15 README.md 命中 'Agateon (formerly agate)'
- BDD-2: head -15 README.zh-CN.md 命中中文品牌声明句
- BDD-3: CHANGELOG.md [Unreleased] 段 + TAG0025 条目均命中

## BDD-4~10（7处URL+批次原子性+全仓残留扫描）已独立实跑，均 PASS
- BDD-4~8: 逐文件逐行核对，5个文件7处均指向 randomgitsrc/agateon，无旧URL残留
- BDD-9: 5文件 git log -1 SHA 一致（751f421a...），批次原子性成立
- BDD-10: pytest 权威判定 test_bdd_10_repo_wide_residual_scan_zero_after_exemptions PASSED（已知盲区规则同P5）

## BDD-11（用户放行确认）人工记录类证据已产出，PASS
- 引用 env-rename-handoff.md 六、版本记录 + 本次会话复核摘要，写入 bdd-11-confirmation-record.md

## BDD-12~16（改名验收锚+remote迁移）已重新实跑，均 PASS
- BDD-12: curl -sI 实测 HTTP/2 301 + Location 指向新仓
- BDD-13: git ls-remote 返回有效 40位 SHA
- BDD-14: gh api 搜索首位命中 randomgitsrc/agateon
- BDD-15: 主checkout与worktree remote -v 均为新仓URL，worktree复用主.git/config
- BDD-16: 主checkout与worktree各fetch一次，均exit 0

## 产出与自检
- P6-acceptance.md 已写（16 PASS / 0 FAIL，frontmatter pass=16/fail=0/ui_affected=false）
- P6-evidence/ 下16个证据文件全部产出，均被至少一条PASS行引用
- gate预检：check-p6-format.py --fix exit0；check-p6-evidence.py exit0；check-p6-provenance.py exit2（仅WARNING：P4-implementation.md缺agent字段，非阻塞、非本报告问题）；check-gate.py P6 exit2（正常信息性返回，FAIL=0/NC=0/P6_TOTAL=16）

---

## 第 2 轮（P6 验收重跑，2026-08-26）

### 背景
第 1 轮 P6.5 judge 判 needs-revision（15 PASS / 1 FAIL：BDD-10）。根因：P1-requirements.md
BDD-10 当时只正式授权 5 类豁免，判定实际依赖测试文件 `_is_exempt()` 里未经基线授权的第 6 类
"自我豁免"（测试文件自身路径）。P1-requirements.md 已补齐第 6 类豁免的 [BASELINE_CHANGE] 正式
授权（第二处标注）。旧 P6-acceptance.md/P6-evidence/ 已被 agate-archive-stale-outputs.py 归档至
.archived/20260826-065343-P6/，本轮从零重新产出，不引用归档内容。

### 16 条 BDD 全部独立重新实跑（不复用归档证据）
- BDD-1/2/3：README.md/README.zh-CN.md 首屏品牌声明 + CHANGELOG [Unreleased]/TAG0025 条目，
  重新 head/grep 实测，均 PASS
- BDD-4~8：install.sh/agate-install.py/agate-changes.py/README.md×2/README.zh-CN.md×2 共 7 处
  URL，重新逐文件逐行 sed+grep 核对（新URL存在 + 旧URL word-boundary 扫描无命中），均 PASS
- BDD-9：重新 git log -1 逐文件比对 SHA 一致（751f421a...），并额外用 git show --stat **完整不
  截断输出**（本轮修复第1轮 judge 指出的截断问题），明确列出全部6个核心文件条目在同一commit
- BDD-10（本轮重点）：pytest 权威判定 test_bdd_10_repo_wide_residual_scan_zero_after_exemptions
  重新执行 PASSED（exit 0）；额外独立手工 grep 交叉核对（不依赖pytest代码路径，手工拼出与P1
  正文6类对应的排除正则）同样0残留；证据文件明确写出"现在6类豁免均已在P1-requirements.md正式
  授权"，不用"已知盲区"措辞
- BDD-11：重新核对 env-rename-handoff.md 版本记录内部一致性 + 与P0/P1/P2交叉核对，人工复核记录
  独立重写，PASS
- BDD-12~16：curl/git ls-remote/gh api search/git remote -v/git fetch 全部重新实跑，均 PASS

### 产出与自检
- P6-acceptance.md 覆盖式重新产出（16 PASS / 0 FAIL，frontmatter pass=16/fail=0/ui_affected=
  false，agate-md-field-set --list 确认字段已正确写入）
- P6-evidence/ 16个证据文件全部本轮重新产出（非归档引用），均被恰好一条PASS行引用
- PASS 行格式改为单行不换行（check-p6-evidence.py 的 ref_re 按行匹配，多行wrap会导致证据引用
  检测不到 —— 本轮排查发现并修正此格式问题）
- gate预检：check-p6-format.py --fix exit 0；check-p6-evidence.py exit 0（16条BDD证据目录非空）；
  check-p6-provenance.py exit 2（仅WARNING：P4-implementation.md缺agent字段，P4阶段遗留、非本轮
  产出、非阻塞、与BDD-10无关）；check-gate.py P6 exit 2（信息性：FAIL=0/NC=0/P6_TOTAL=16）
