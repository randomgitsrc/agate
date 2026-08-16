## P2 progress — architect

- [x] 读 dispatch-context-architect.md（派发指引）
- [x] 读角色定义 architect.md
- [x] 读 P1-requirements.md（31 BDD + 影响面表 2.1/2.2/2.3 + I-1~I-16）
- [x] 读 P0-brief.md（env_constraints + known_risks）

### P1 要点
- v1 = 6 组件：agate-install / agate-resolve / hook 解析入口 / summary 集成 / agate-pack-offline.py / install-offline.py
- 红线：~/.agate 软链保留；无 .agate-version 回退 current；AGATE_ROOT env 最高；resolve 失败回退 current 绝不静默禁用 gate（BDD-17/18）
- legacy 布局（BDD-30）：无 current/latest 时 ~/.agate 软链目标本身 = AGATE_ROOT
- gate 逻辑不改（BDD-31）；只改解析层
- 影响面 2.1 脚本层 12 项 + 2.2 文档层 14 项 + 2.3 测试层 7 项
- 3 个派发/卡片脚本内联 _agate_root 未走 agate_common（rev2 结论 6）——P2 评估是否归口
- [x] 读设计稿 agate-version-management-20260813.md（§8 决策定稿：dev 存在不默认 / current→latest / 引用即保护 / summary 显示版本+原因 / v1 范围）

### 设计稿要点
- 形态：~/.agate/{repo, dev, vX.Y.Z/..., latest->vX, current}；latest 纯指针
- 版本载体 = git worktree 检出 tag，repo 只 clone 一次
- v1 范围 = install/resolve/hook 解析入口/summary 显示 + 引用保护检查；>= 折中/版本列表/自动清理留 v2
- §3.2 .sh 路线已过时（P0/P1 已更正为 Python 路线）
- [x] 读 AGENTS.md（项目约定：Python 路线 / 测试平台无关 / dogfooding 双工作区 / 改脚本工作流）

### 下一步
- 只读扫描代码：agate_common.py / install-hook.py / 3 hook 薄壳 / agate-summary.py / agate-inject-card.py 等 / check-protocol-consistency.py L765 / 测试文件
- [x] 扫描代码：agate_common.py（resolve_agate_root env优先→上溯→.agate-root）、install-hook.py（argv>env>~/.agate；软链/复制模式）、3 hook 薄壳（自定位→python探测→exec py）、agate-summary.py（git describe 显示仓库自身版本）、agate-inject-card/agate-next-card/agate-render-dispatch-prompt（3 个内联 _agate_root）、check-protocol-consistency.py（CHECK 10 SCRIPT_REF_RE L771：install-offline.py 不在正则白名单→无漂移检查但也不报错；新增脚本须入 scripts/README.md 清单）、ci-gate-backstop.py（_AGATE_ROOT = __file__.parent.parent 上溯）、pre-commit-gate.py L191（resolve_agate_root）
- [x] 扫描测试：test_install_hook.py（6 用例，_make_fake_root / AGATE_HOOK_COPY_MODE=1 复制模式）、conftest.py（fixture 体系）、test_pre_commit_hook.py L1351（bdd-19 复制模式）
- [x] 读 check-gate.py P2 gate（candidate_count 解析 L347、四字段校验 L388、权衡理由 L395、dispatch_plan TAG0014 L292/411、gate_commands 可执行性 WARNING L398）

### 关键设计输入
- resolve_agate_root 语义 = env 优先 → 脚本真实路径上溯 → 复制模式 .agate-root 恢复（agate_common.py L76-94）
- 3 hook 薄壳当前单行 AGATE_ROOT 自定位直接 exec 具体版本 py → 需改为经 resolve-entry
- install-hook.py 不 import agate_common（pyyaml 无关，本地 run_git 降级）——resolve-entry 设计须考虑
- [x] 最小验证（bash /tmp/opencode/tag0008-mv.sh，全部通过）
  [1] git worktree add tag：worktree add <path> <tag> 成功（detached HEAD @ tag）；重复 add 已存在路径 → exit 128 'already exists' → **幂等必须程序先判存在**（BDD-3 依赖此预判，非 git 行为）
  [2] pip download --platform win_amd64/manylinux_2_17_x86_64 --python-version 311 --only-binary=:all: --no-deps → 分别拉到 pyyaml-6.0.3 cp311 win_amd64 / manylinux2014 wheel → **pack-offline 按平台拉 wheel 可行**
  [3] sha256 checksum：64 hex 字符确认 → manifest checksum 计算/校验链路可行

### 结论
- 版本目录 = worktree 检出 tag 确认可行；agate-install 幂等需显式检查版本目录/指针存在
- pip download --platform 按目标平台拉 wheel 确认可行（--only-binary=:all: 保证不拉到源码包）
- sha256 计算用 hashlib 标准库（无外部依赖）

## architect retry2

- [x] 读 dispatch-context（含已内联调研结论）+ architect.md 角色定义
- [x] 读 P1-requirements.md（31 BDD + 影响面表）+ P0-brief + 设计稿 §8 + P2-progress 上一轮结论
- [x] 直接产出 P2-design.md（候选方案 A 采纳：resolve-entry 固定入口 + 版本目录 + 纯指针；候选方案 B 否决：hook 内联解析三份重复）
- [x] 四字段齐全：packages=[agate] / domains=[backend,cli,security] / ui_affected=false / gate_commands（P3/P5/P5_unit/P5_consistency/P5_count）
- [x] dispatch_plan 声明：mode=static-batch, parallel_limit=3, batches=[resolve-chain/install/offline]（high 复杂度硬规则，拆批 + 共享文件 agate_common 后处理声明）
- [x] minimal_validation：3 项已通过（worktree add tag / pip download --platform / sha256）写入
- [x] files_to_read 覆盖影响面表关键联动点（agate_common/install-hook/3 hook/agate-summary/inject-card/check-protocol-consistency/ci-gate-backstop/测试）
- [x] 3 内联脚本归口决策：统一走 agate_common.resolve_agate_root（含 pyyaml 依赖副作用评估）
- [x] ci-gate-backstop 复核决策：不改（CI 语境上溯正确）
- 下一步：自检 grep 关键字段 → 返回

## plan-eng-review
- read dispatch-context (P2 plan-eng-review) + plan-eng-review.md role
- read P2-design.md (308 lines, candidate_count=2, dispatch_plan static-batch 3批)
- read P1-requirements.md (31 BDD, 影响面表 2.1/2.2/2.3, I-1~I-16)
- read P0-brief.md (4组件 v1 范围 + offline + uninstall + env探测)
- read AGENTS.md (项目约定)
- read agate_common.py resolve_agate_root (L76-94), install-hook.py main (L86-148), pre-commit-gate.sh
- verified code: agate_common.py L76-94 (resolve_agate_root env→realpath→.agate-root), install-hook.py L86-148 (argv[1]>env>~/.agate), pre-commit-gate.sh (fail-closed step 4)
- verified: agate-inject-card.py L28-33 inline _agate_root; agate-next-card.py L35 / agate-render-dispatch-prompt.py L32 inline _resolve_agate_root; 3 scripts zero agate_common import ✓ (design §4.4 claim confirmed)
- verified: agate_common.py L27-31 import yaml fail-closed exit 1 ✓
- verified: check-protocol-consistency.py L765-789 CHECK 10 SCRIPT_REF_RE; ci-gate-backstop.py L16 _AGATE_ROOT ✓
- verified: integration/test_pre_commit_hook.py L1351 bdd-19 windows_smoke copy-mode ✓; test_install_hook.py exists
- verified: archived design doc §8 (L152-198) decisions match design citations
- analysis: hook mechanism ambiguity (§4.3 bullet1 vs bullet3 vs §9), env-poisoning of resolve-entry location, files_to_read missing 2 sibling dispatch scripts, uninstall mtime-scan under-protection, resolve-entry total-failure exit undefined, install.sh form undecided
- verdict: no blockers; approved with P3/P4 clarifications
