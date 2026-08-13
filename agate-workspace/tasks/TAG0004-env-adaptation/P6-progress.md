# P6 验收进度 — TAG0004-env-adaptation

- 角色：verifier（P6 验收模式）
- 时间：2026-08-13
- worktree：/home/kity/oclab/agate/.worktrees/agate-TAG0004
- 输入：P1 37 BDD + P3 测试契约 + P5 全绿记录

## 执行批次记录


### 批次 1：S1/S2/S3/M4/M5/M6/M9 各 BDD bats 单测（37/37 exit 0）
- BDD-1..4（S1 空格路径，pre-commit-hook.bats bdd-1..4）：全 PASS，bats 单测 exit 0
- BDD-5/8（S3 encoding，agate-scripts-encoding.bats）：bdd-5 grep 断言审计 + bdd-8 ASCII 回归，exit 0
- BDD-6/7（S3 中文读写，agate-md-field-get.bats / agate-retreat-state.bats）：exit 0
- BDD-9/10（S2 中文证据文件名，check-p6-evidence.bats）：bdd-9 中文文件名识别合法 + bdd-10 无扩展名拦截，exit 0
- BDD-11（M4 全角冒号 BLOCKER，check-gate.bats）：LC_ALL=C 下总结行不误计，exit 0
- BDD-12/13（M5 check-p6-format.bats）：--fix 全角冒号 line69 归一化 + 半角回归，exit 0
- BDD-14/15（M6 CRLF frontmatter，check-gate.bats / agate-md-field-get.bats）：CRLF 提取不失效 + LF 回归，exit 0
- BDD-16（M6 .gitattributes 无 *.md 强制）：exit 0
- BDD-17（M9 正则元字符，pre-commit-hook.bats）：任务目录含 [ 不静默绕过，exit 0

### 批次 2：其他/Q1/Q2/Q5/RM/TPV0090 各 BDD bats 单测（exit 0）
- BDD-18（.agate.env \r）：agate-workspace-resolve.bats bdd-18，exit 0
- BDD-19（复制模式 AGATE_ROOT）：pre-commit-hook.bats bdd-19，exit 0
- BDD-20（sed & 转义）：agate-render-dispatch-prompt.bats bdd-20，exit 0
- BDD-21/22（Q1 路径归一化，agate-next-card.bats）：Windows 盘符/反斜杠剥离 + Linux 字节不变，exit 0
- BDD-23/24/25（Q2 卡片对齐，env-adapt-docs.bats）：exit 0；另跑 consistency 0 ERROR（p6-bdd-25-consistency.log）
- BDD-26/27（Q5 SETUP Windows + .gitignore 预设）：exit 0
- BDD-28/29（RM-AG0001 反引号，check-gate.bats）：SUGGEST 计入 + NEED_CONFIRM 阻塞，exit 0
- BDD-30/31（RM-AG0002 无 formatter A/B）：编译失败判 A + 普通失败判红，exit 0
- BDD-35/36/37（TPV0090-M4 NameError B 类）：NameError 判 B + globals().get() 回归 + TypeError 判 A，exit 0

### 批次 3：全局类
- BDD-32 全量 bats：714 ok / 0 not ok，exit 0（p6-bdd-32-full.log 56KB）
- BDD-33 CI matrix：protocol-tests.yml 含 windows-latest ×4 job，静态断言 OK（p6-bdd-33-ci.log）
- BDD-34 shellcheck：-S warning 全脚本 0 error，exit 0（p6-bdd-34-shellcheck.log）

### 证据汇总
- P6-evidence/ 共 41 个证据文件，全部末行 EXIT_CODE: 0
- 无 UI（ui_affected: false），无截图，证据全部为命令执行输出

### 自查结果（2026-08-13）
- check-p6-format.sh --fix：exit 0
- check-p6-evidence.sh：37 条 BDD，证据目录非空，exit 0
- check-p6-provenance.sh：exit 0（证据-结论对应、dispatch-context 审计、BDD 对照全部通过）
- grep -cE '^\s*- (PASS|FAIL)' P6-acceptance.md = 37（FAIL=0）
- 每条 PASS 行均有括号证据引用（ASCII 括号，相对 P6-evidence/ 路径）
- P6-evidence/ 共 41 个证据文件，全部末行 EXIT_CODE: 0
- `[PROD_NOT_TOUCHED]` 全程仅操作 worktree 与 /tmp/opencode
