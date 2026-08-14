---
phase: P1
task_id: TAG0011-test-migration
type: problems
parent: P0-brief.md
trace_id: TAG0011-P1-20260815
status: draft
created: 2026-08-15
agent: analyst
# ── v2.0 机器字段 ──
risk_level: high
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-tests, agate-test-helpers, agate-test-scripts, agate-protocol-docs, agate-ci]
domains: [backend, cli]
change_type: refactor
# 能力需求声明（analyst.md 三态）
# requires_minimal_validation: Windows 真机行为（pytest 在 windows-latest 的冒烟子集）本地 Linux 无法验证
capability_requirements:
  - need: pytest 运行环境
    why: 迁移后的测试运行器——全量 pytest 是验收①的判定对象
    available:
      - "系统 python3 已装 pytest 9.0.3（python3 -m pytest 可跑）"
      - "开发 venv ~/.venvs/agate-dev/ 目前无 pytest，需 pip install pytest（network: full 可装）"
    status: available
  - need: ruff 静态检查
    why: 验收③——py 代码静态检查（TAG0010 已接入，pyproject.toml 规则集已就位）
    available:
      - "~/.venvs/agate-dev/（ruff 0.16.3）"
    status: available
  - need: Windows CI 冒烟执行
    why: 验收④——pytest 在 Windows 真机的技术路线冒烟无法本地 Linux 验证
    available:
      - "GitHub Actions windows-latest matrix（executor_env.network: full）"
    status: available
requires_minimal_validation: true
---

# P1 需求基线 — agate 测试框架迁移（阶段二，bats → pytest）

> 本文件是 TAG0011 的需求基线（"活基线"）。后续阶段发现新隐含需求时由主 Agent 增补并标 `[SCOPE+ from Pn]`。
> 需求权威来源：`P0-brief.md` + `docs/reviews/agate-python-migration-analysis-20260814.md`（§6 阶段二建议，注意其"建议延迟"的结论已被用户否决——用户明确要全转 Python）+ TAG0010（阶段一已完成，v0.46.0）。
> **基线修订（2026-08-15，BLOCKER-1 修复）**：§6.2 Windows 冒烟决策由 SUGGEST 升级为既定——`check-windows-smoke.sh` **退役**，冒烟由 `@pytest.mark.windows_smoke` marker 承接；`check-windows-smoke.bats`（7 用例）随之退役不迁移。迁移范围 61 文件/756 @test → **60 文件/749 @test**，BDD-1 计数断言随改为 ≥ 749。P1 为活基线，允许此类口径修订。

## 1. 需求复述

**核心需求**：把 agate 测试框架从 bats 全面迁移到 pytest——58 个 .bats（count-tests 口径 727 @test）+ 526 行 helpers 迁移为 pytest 用例与 fixture，配合 TAG0010 产品逻辑 Python 化，达成 agate 测试侧也全 Python（平台无关 + 统一生态）。同时完成协议文档全量重写与 CI 同步（用户确认归本任务）。TAG0010 已完成（v0.46.0，产品脚本全部 py 化，bats 测试已改为直调 py），本任务是紧随其后的阶段二。

**范围锁定**（P0-brief 已确认，不可扩张）：
- **测试用例**：58 个 .bats（46 unit + 6 regression + 6 integration，727 @test）→ pytest。**注意**：全量迁移范围实际上覆盖 60 个 .bats / 749 @test——除 count-tests 口径的 58 个外，还有 `sanity.bats`（6）+ `tests/scripts/check-platform-assumptions.bats`（16）两个文件也在 tests/ 下（count-tests.sh 不计它们），必须一并迁移才能达成"pytest 全绿替代 bats"的验收①。`tests/scripts/check-windows-smoke.bats`（7）测 check-windows-smoke.sh 自身的代表选取行为，随脚本**退役**（§6.2 决策，冒烟由 pytest marker 承接），不在迁移范围。`count-tests.sh` 是统计工具，不在迁移范围（见 §6.3）。
- **helpers**：526 行（load.bash 48 + fixtures.bash 412 + git-helper.bash 66）→ pytest conftest.py fixture 体系。
- **测试脚本工具**：`check-windows-smoke.sh` **退役**（§6.2 决策，pytest marker 承接冒烟）；`count-tests.sh` **改写为 pytest 收集计数**（§6.3）。
- **协议文档全量重写**（用户确认归本任务）：platform-notes / SETUP / UPGRADING / dispatch / git-integration / CI workflow——完整清单见 §5 表 E。
- **明确不做**：不新增/删除协议功能；不改产品脚本（TAG0010 已完成）；不引入除 pytest 外的测试生态依赖（如 tox/nox）。

**目标状态（验收口径）**：pytest 全绿替代 bats（60 个 .bats / 749 @test 全迁移 + check-windows-smoke.bats 退役，bats 退役）；consistency 0 ERROR；ruff 静态检查覆盖全部 py；Windows CI 冒烟通过（`-m windows_smoke`）；平台假设扫描器覆盖 .py；测试代码平台无关（Linux 全量 + Windows 冒烟）。

## 2. 隐含需求识别（逐维度）

> 本任务是测试框架迁移，无 UI。按 analyst.md 隐含需求清单逐维度过，并补 agate 特有依赖。

### 2.1 数据维度：既有测试夹具必须保留行为契约
- `tests/fixtures/`（full-task / ui-affected / vision-blocked / high-risk / paused-task 五组静态 Gold 任务）是 P6 证据/vision 类测试的静态夹具，**内容与字段语义不变**，pytest 侧只需改加载方式（相对路径读取）。
- `BATS_TEST_TMPDIR` 临时目录语义 → pytest `tmp_path` fixture（每个测试独立目录）。
- bats 的 `run`/`$output`/`$status` 断言语义 → pytest 封装 helper（subprocess 调用 + 输出捕获）。**这是迁移的核心映射**：不能逐条硬翻译，要写迁移映射表（§4.1），否则 727 条断言逐一改写会失控。

### 2.2 前端/展示维度：CLI 输出契约是测试断言对象
- 测试断言的是脚本的 exit code（0/1/2）与 `GATE ...:` 前缀输出、`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行解析输出、gate-result.json 结构——这些契约**在阶段一已固定，本任务不改契约，只改断言载体**（bash `[[ $output == *...* ]]` → pytest `assert "..." in result.stdout`）。
- bats 的 `setup()`/`teardown()` 生命周期 → pytest fixture（函数级 / 会话级 AGATE_ROOT）。

### 2.3 多端维度：测试框架的"端"= 平台 + CI
- **平台**：Linux 全量跑（功能正确性）、Windows 冒烟跑（平台敏感机制代表用例）——这是测试平台无关原则的核心。pytest 自身全平台，但**平台敏感断言**（symlink 复制模式 / CRLF / cp1252 / py_path / shim）需要保留——不是"bats 能跑所以 Windows 行"，而是 pytest 下这些机制的测试要有等价物（§6）。
- **CI**：protocol-tests.yml 的 bats job → pytest job；check-windows-smoke.sh **退役**，Windows 冒烟 job 用 `-m windows_smoke` marker（§6.2 决策）；shellcheck/ruff/consistency/gate-backstop job 保持不变。
- **hook 链**：pre-commit/commit-msg/pre-push 三个 sh 薄壳保留（TAG0010 已定）；pre-commit-hook.bats（48）测的就是薄壳调 py 的行为，迁移后断言对象仍是 `bash pre-commit-gate.sh` 的 exit 行为——**hook 测试是"shell 薄壳在真环境的行为"测试，pytest 用 subprocess 调 bash 即可，不需要 bats**。

### 2.4 边界维度：平台边界与失败路径
- **Windows 冒烟选取逻辑**：check-windows-smoke.sh 用 `@test` 名称正则选代表（第 1 个 + 平台关键词）——**决策已定（§6.2）**：脚本退役，改用 **pytest marker**（`@pytest.mark.windows_smoke`）逐用例标注，Windows CI 跑 `-m windows_smoke`。
- **编码**：所有测试的文本读写 `encoding="utf-8"`（沿用阶段一纪律）。
- **路径**：MSYS/Git Bash 路径（`/c/...`）→ `py_path` helper 已有，pytest 在 Windows 用原生 python 跑，路径处理策略需在 P2 定（Windows 冒烟下 subprocess 调 py 脚本的路径形式）。
- **bats 特有工具**：`bats -c`（只计数）、`BATS_TEST_TMPDIR`、`@test` 名称——迁移后无等价物，相关断言（如 env-adapt-docs bdd-32 "bats 可解析"）需改写为 pytest 收集等价断言。
- **Pillow 依赖**：agate-image-check.py 的像素方差/ahash 测试用 Pillow（可选依赖）——pytest 侧保持可选性，缺 Pillow 时 skip（等价现 bats 的行为）。

### 2.5 兼容维度：测试套件本身的机制不破坏
- **平台假设扫描器**：check-platform-assumptions.py 扫描扩展名过滤（`.bats/.bash/.sh/.py`）——**迁移后 tests/ 全树 .bats 减少、.py 增多**，扫描器的"干净树契约"（tests/ 全树 0 命中）在 pytest 终态仍须成立；其规则集 R1-R5 已覆盖 .py（TAG0010 完成）。**须确认 pytest 测试代码自身不引入平台假设**（测试约定：不裸 python3、不硬编码 PATH、不 /tmp、symlink 分支断言）。
- **count-tests.sh**：是 `grep -c '^@test'` 统计——pytest 化后其统计对象消失。**需评估**：改写成 pytest 收集计数（`pytest --collect-only -q | tail -1`），或退役该脚本。P0 口径"58 个 .bats / 727 @test"依赖它，文档多处引用（§5 表 E）。
- **一致性检查**：check-protocol-consistency.py 的锚点表不涉及测试文件路径（只查协议文档/脚本），迁移后不受影响——但 **AGENTS.md 测试约定章节、tests/README.md 覆盖度表**描述 bats 的文件需重写（§5）。
- **测试用例数语义**：迁移不减少覆盖——迁移后收集数 **749**（756 基线 − 7：check-windows-smoke.bats 测的是被退役脚本自身的行为，退役不属"覆盖减少"），Windows 冒烟覆盖由 marker 承接（BDD-4/BDD-12），这是 BDD 验收点。

### 2.6 测试维度（agate 特有隐含依赖）
- **sanity.bats**（6）是框架自检（load.bash/fixtures.bash/git-helper.bash 能 load）——迁移后对应"conftest.py fixture 体系自检"，须有等价 pytest 冒烟。
- **helpers-python.bats**（3）测 fixtures.bash 的 detect_python / probe_python——迁移为 conftest 的 python 探测 fixture 测试。
- **env-adapt-docs.bats**（9）是文档/CI 断言（shellcheck/ruff/windows-latest matrix/.gitattributes）——迁移后**部分断言要改目标**（如 bdd-34 的 shellcheck 收敛 + ruff；bdd-32 的 "bats 可解析" → "pytest 可收集"）。
- **check-windows-smoke.bats**（7）测 check-windows-smoke.sh 本身的代表选取行为——**退役**（§6.2 决策已定：脚本退役故其测试对象消失，7 用例不迁移）。
- **P6 视觉验收**：P6 的截图/vision YAML 由 vision-analyst 角色处理（非本任务），但 check-p6-evidence.bats / check-p6-provenance.bats / agate-vision-blocker.bats 依赖 fixtures/ 静态夹具与 Pillow——迁移后夹具加载方式改。

## 3. 测试现状清单（60 个 .bats / 749 @test 迁移范围，按被测脚本分组）

> 口径说明：count-tests.sh 统计 unit/regression/integration 三目录 = 58 文件 / 727 @test；全量迁移范围另加 sanity.bats（6）+ tests/scripts/check-platform-assumptions.bats（16）= **60 文件 / 749 @test**；`tests/scripts/check-windows-smoke.bats`（7）测 check-windows-smoke.sh 自身选取行为，随脚本**退役**（§6.2 决策，冒烟由 pytest marker 承接），不在迁移范围。
> 分组 = 批次规划的基础（用户强制要求）。@test 数以 `grep -c '^@test'` 逐文件实测（2026-08-15）。

### 表 A：unit（46 文件 / 625 @test）

| 被测脚本（py） | 测试文件 | @test | 依赖模式 |
|----------------|---------|-------|---------|
| agate_common.py（resolve_workspace） | unit/agate-workspace-resolve.bats | 10 | 无 git；两行输出契约 |
| agate-changelog-unreleased.py | unit/agate-changelog-unreleased.bats | 2 | 纯 stdin/stdout |
| agate-card-inject.py | unit/agate-card-inject.bats | 2 | 纯文件 |
| agate-evidence-consistency.py | unit/agate-evidence-consistency.bats | 2 | fixtures/ 静态夹具 |
| agate-gate-missing-cmds.py | unit/agate-gate-missing-cmds.bats | 2 | 纯 stdin |
| agate-gate-p5-count.py | unit/agate-gate-p5-count.bats | 3 | 纯 stdin |
| agate-image-check.py | unit/agate-image-check.bats | 4 | Pillow（可选）；运行时造图 |
| agate-inject-card.py | unit/agate-inject-card.bats | 11 | create_task_dir |
| agate-json-get.py | unit/agate-json-get.bats | 8 | 纯 stdin |
| agate-md-field-get.py | unit/agate-md-field-get.bats | 14 | create_task_dir |
| agate-next-card.py | unit/agate-next-card.bats | 22 | 字节稳定性 sha256 |
| agate-read-p5-commands.py | unit/agate-read-p5-commands.bats | 4 | 纯 stdin |
| agate-render-dispatch-prompt.py | unit/agate-render-dispatch-prompt.bats | 20 | create_task_dir |
| agate-retreat-state.py | unit/agate-retreat-state.bats | 4 | 纯文件 |
| agate-retreat-to.py | unit/agate-retreat-to.bats | 5 | git + hook 集成 |
| agate-state-get.py | unit/agate-state-get.bats | 6 | .state.yaml 文件 |
| agate-state-yaml-check.py | unit/agate-state-yaml-check.bats | 3 | .state.yaml 文件 |
| agate-vision-blocker.py | unit/agate-vision-blocker.bats | 2 | fixtures/ 静态夹具 |
| agate-archive-stale-outputs.py | unit/agate-archive-stale-outputs.bats | 7 | git + 时间戳（flaky R2.4） |
| agate-capture-env-baseline.py | unit/agate-capture-env-baseline.bats | 15 | git + gate-result.json |
| agate-debt-check.py / check-debt.py | unit/agate-debt-check.bats | 21 | create_task_dir + git |
| agate-extract-context.py | unit/agate-extract-context.bats | 16 | create_task_dir |
| agate-migrate-workspace.py | unit/agate-migrate-workspace.bats | 9 | git + 工作区 |
| check-changelog.py | unit/check-changelog.bats | 8 | create_task_dir + git |
| check-frontmatter.py | unit/check-frontmatter.bats | 14 | create_task_dir |
| check-gate.py | unit/check-gate.bats | 124 | create_task_dir + git（最大单文件） |
| check-gate.py（P1 review） | unit/check-gate-p1-review.bats | 9 | create_task_dir |
| check-gate.py（P5 diff） | unit/check-gate-p5-diff.bats | 13 | create_task_dir + git |
| check-p6-evidence.py | unit/check-p6-evidence.bats | 30 | fixtures/ 静态夹具 + Pillow |
| check-p6-format.py | unit/check-p6-format.bats | 16 | create_task_dir |
| check-p6-provenance.py | unit/check-p6-provenance.bats | 36 | fixtures/ 静态夹具 + git |
| check-protocol-consistency.py | unit/check-protocol-consistency.bats | 3 | 跑一致性脚本 |
| check-pruning.py | unit/check-pruning.bats | 29 | create_task_dir + git |
| check-retrospective.py | unit/check-retrospective.bats | 10 | create_task_dir |
| check-scope-resolved.py | unit/check-scope-resolved.bats | 10 | create_task_dir |
| check-state-transition.py | unit/check-state-transition.bats | 30 | create_task_dir + git |
| check-state-yaml.py | unit/check-state-yaml.bats | 9 | .state.yaml 文件 |
| check-tdd-red.py | unit/check-tdd-red.bats | 43 | create_task_dir + formatter |
| formatters（pytest.sh 等） | unit/check-tdd-red-formatter.bats | 13 | formatter 脚本 |
| ci-gate-backstop.py | unit/ci-gate-backstop.bats | 11 | git + 平台探测 |
| commit-msg-self-gate.sh/.py | unit/commit-msg-self-gate.bats | 4 | 正则（消息文本） |
| dispatch-context（缺失 WARNING） | unit/dispatch-context-warning.bats | 1 | create_task_dir |
| 文档/CI 断言（TAG0004） | unit/env-adapt-docs.bats | 9 | 读文档/CI 文件 |
| helpers fixture（探测/shim） | unit/helpers-python.bats | 3 | fixtures.bash 机制 |
| install-hook.py | unit/install-hook.bats | 6 | git + .gitignore |
| agate-scripts-encoding（守卫） | unit/agate-scripts-encoding.bats | 2 | 扫全 .py |

### 表 B：regression（6 文件 / 17 @test）

| 被测脚本 | 测试文件 | @test | 回归点 |
|----------|---------|-------|--------|
| agate-archive-stale-outputs.py | regression/v040-dotarchived-exclusion.bats | 2 | .archived 排除 |
| check-gate.py（P7 DESIGN_GAP） | regression/v060-design-gap.bats | 4 | frontmatter 配对 |
| check-gate.py（P8 cached） | regression/v060-p8-cached.bats | 3 | version/CHANGELOG |
| check-gate.py（P8 internal_only） | regression/v060-p8-internal-only.bats | 3 | internal_only |
| check-pruning.py（P7） | regression/v060-r4-cached.bats | 2 | 源码文件数 |
| task-files.md executor_env YAML | regression/v060-yaml-indent.bats | 3 | YAML 缩进 |

### 表 C：integration（6 文件 / 85 @test）

| 被测对象 | 测试文件 | @test | 依赖模式 |
|----------|---------|-------|---------|
| commit-msg-self-gate hook | integration/commit-msg-self-gate.bats | 6 | git hook |
| check-protocol-consistency.py | integration/consistency.bats | 11 | 跑一致性脚本 |
| dispatch-context 卡片 hash | integration/dispatch-context-card.bats | 8 | create_task_dir + git |
| pre-commit-gate.sh 薄壳 + 调度链 | integration/pre-commit-hook.bats | 48 | git hook + 12 子脚本（最大单文件之一） |
| pre-push-gate.sh 薄壳 | integration/pre-push-hook.bats | 4 | git hook |
| SELF-GATE 对齐 | integration/protocol-alignment-review.bats | 8 | 读协议文件 |

### 表 D：sanity + scripts（2 文件 / 22 @test；check-windows-smoke.bats 退役，见 §6.2）

| 被测对象 | 测试文件 | @test |
|----------|---------|-------|
| helpers 体系（load/fixtures/git-helper） | tests/sanity.bats | 6 |
| check-platform-assumptions.py 扫描器行为 | tests/scripts/check-platform-assumptions.bats | 16 |

## 4. 迁移批次规划（17 批，每批 3-6 个 .bats，粒度 1 轮可完成）

> **批次设计原则**：按被测脚本分组；每批 3-6 个文件；**批次要小**（用户明确"任务过重→subagent 卡死"，粒度必须 1 轮可完成）。三个单文件超大批（check-gate.bats 124、pre-commit-hook.bats 48）标为"专项批"，P4 内部按功能域拆分子任务逐步验证。
> **每批验证口径**：该批 pytest 新文件全绿 + 原 .bats 该批文件仍绿（迁移期双跑对照，P0 known_risks 要求）+ consistency 0 ERROR。
> **依赖**：批次 0（pytest 基座 + conftest）是一切的前置；其余批彼此独立可并行（但不并行 bash，串行推进）。

| 批次 | 内容（迁移 .bats → test_*.py） | 文件数 | @test | 依赖前置 | 验证命令 |
|------|-------------------------------|--------|-------|---------|---------|
| **0 — pytest 基座** | sanity.bats + helpers-python.bats + agate-workspace-resolve.bats；**交付 conftest.py**（AGATE_ROOT 解析 / tmp_path fixture / task_dir fixture / git_repo fixture / run_script helper）+ pyproject [tool.pytest.ini_options] | 3 | 19 | 无 | `python3 -m pytest agate/tests/ -k "sanity or helpers or workspace"` + 原 3 bats 对照 + `python3 agate/scripts/check-protocol-consistency.py` |
| **1 — 纯工具（无 git）** | agate-changelog-unreleased.bats + agate-card-inject.bats + agate-evidence-consistency.bats + agate-gate-missing-cmds.bats + agate-gate-p5-count.bats | 5 | 11 | 批次 0 | `python3 -m pytest agate/tests/unit/ -k "changelog or card or evidence or gate_missing or gate_p5"` + 原 5 bats 对照 |
| **2 — 共享工具** | agate-json-get.bats + agate-md-field-get.bats + agate-state-get.bats + agate-retreat-state.bats + agate-state-yaml-check.bats + agate-read-p5-commands.bats | 6 | 39 | 批次 0 | `python3 -m pytest agate/tests/unit/ -k "json or md_field or state_get or retreat_state or state_yaml or read_p5"` + 原 6 bats 对照 |
| **3 — 内容生成工具** | agate-next-card.bats（字节稳定性 22）+ agate-inject-card.bats + agate-render-dispatch-prompt.bats | 3 | 53 | 批次 0 | `python3 -m pytest agate/tests/unit/ -k "next_card or inject_card or render_dispatch"` + 原 3 bats 对照 |
| **4 — 上下文/归档/回退工具** | agate-extract-context.bats + agate-archive-stale-outputs.bats + agate-migrate-workspace.bats + agate-retreat-to.bats | 4 | 37 | 批次 0（retreat-to 依赖 hook） | `python3 -m pytest agate/tests/unit/ -k "extract or archive or migrate or retreat"` + 原 4 bats 对照 |
| **5 — 环境/债务/编码守卫** | agate-capture-env-baseline.bats + agate-debt-check.bats + agate-image-check.bats + agate-scripts-encoding.bats | 4 | 42 | 批次 0（Pillow 可选） | `python3 -m pytest agate/tests/unit/ -k "capture_env or debt or image or encoding"` + 原 4 bats 对照 |
| **6 — check 状态/裁剪/scope** | check-state-transition.bats + check-pruning.bats + check-scope-resolved.bats | 3 | 69 | 批次 0 | `python3 -m pytest agate/tests/unit/ -k "state_transition or pruning or scope"` + 原 3 bats 对照 |
| **7 — check 基础 gate（非 check-gate 主文件）** | check-changelog.bats + check-frontmatter.bats + check-state-yaml.bats + check-retrospective.bats + check-p6-format.bats | 5 | 57 | 批次 0 | `python3 -m pytest agate/tests/unit/ -k "changelog or frontmatter or state_yaml or retrospective or p6_format"` + 原 5 bats 对照 |
| **8 — check-gate 专项（P1/P2/P4/P6/P7/P8 分支）** | check-gate.bats（124，最大单文件）+ check-gate-p1-review.bats + check-gate-p5-diff.bats | 3 | 146 | 批次 0；P4 内部按 check-gate.py 的 gate 阶段拆子任务逐轮验证 | `python3 -m pytest agate/tests/unit/ -k "gate"`（P4 分阶段跑 `-k "gate_p1"` / `-k "gate_p5"` / `-k "gate_p7"`）+ 原 3 bats 对照 |
| **9 — P6 验收链 + vision** | check-p6-evidence.bats + check-p6-provenance.bats + agate-vision-blocker.bats + ci-gate-backstop.bats | 4 | 79 | 批次 0（Pillow 可选；静态夹具） | `python3 -m pytest agate/tests/unit/ -k "p6 or vision or backstop"` + 原 4 bats 对照 |
| **10 — TDD 红灯链 + 一致性** | check-tdd-red.bats + check-tdd-red-formatter.bats + dispatch-context-warning.bats + check-protocol-consistency.bats | 4 | 60 | 批次 0（formatter 脚本） | `python3 -m pytest agate/tests/unit/ -k "tdd or formatter or dispatch or consistency"` + 原 4 bats 对照 |
| **11 — 回归套件** | regression/ 6 个 v0xx-*.bats | 6 | 17 | 批次 8（依赖 check-gate/check-pruning 迁移） | `python3 -m pytest agate/tests/regression/` + 原 6 bats 对照 |
| **12 — hook 消息/推送/安装链** | unit/commit-msg-self-gate.bats + integration/commit-msg-self-gate.bats + integration/pre-push-hook.bats + unit/install-hook.bats | 4 | 20 | 批次 0（git hook） | `python3 -m pytest agate/tests/ -k "commit_msg or pre_push or install_hook"` + 原 4 bats 对照 |
| **13 — pre-commit hook 专项** | integration/pre-commit-hook.bats（48，最大单文件之一）+ integration/dispatch-context-card.bats | 2 | 56 | 批次 8（hook 调度 12 子脚本已迁移） | `python3 -m pytest agate/tests/integration/ -k "pre_commit or dispatch"` + 原 2 bats 对照 |
| **14 — 一致性/self-gate 集成** | integration/consistency.bats + integration/protocol-alignment-review.bats | 2 | 19 | 批次 0 | `python3 -m pytest agate/tests/integration/ -k "consistency or alignment"` + 原 2 bats 对照 |
| **15 — 文档/CI 断言** | unit/env-adapt-docs.bats（9，断言目标随 pytest 化更新） | 1 | 9 | 批次 0；随 §5 文档重写联动 | `python3 -m pytest agate/tests/unit/test_env_adapt_docs.py` + 原 bats 对照 |
| **16 — 扫描器行为** | tests/scripts/check-platform-assumptions.bats（16，规则集已覆盖 .py） | 1 | 16 | 批次 0 | `python3 -m pytest agate/tests/scripts/test_check_platform_assumptions.py` + 原 bats 对照 |
| **17 — Windows 冒烟机制（退役批）** | tests/scripts/check-windows-smoke.bats（7）→ **退役**（§6.2 决策已定）：随 check-windows-smoke.sh 退役，不做迁移；冒烟覆盖由 `@pytest.mark.windows_smoke` marker 承接，Windows CI 跑 `python -m pytest agate/tests/ -m windows_smoke` | 0 | 0 | 无（退役批，不依赖批次） | 退役；BDD-12 检查 tests/ 下无 check-windows-smoke.sh 且 Windows CI 冒烟 job 引用 marker |

**批次覆盖自检**：17 批合计 = 60 个文件 / 749 @test（19+11+39+53+37+42+69+57+146+79+60+17+20+56+19+9+16 = 749；批次 17 为退役批 0 文件 0 用例，不计入），全部 46 unit + 6 regression + 6 integration + sanity + check-platform-assumptions.bats（scripts 1 个）恰好一次不重不漏；check-windows-smoke.bats 退役不在迁移范围。

**批次依赖图**：批次 0 → 全部；批次 8 → 批次 11；批次 13 依赖批次 8；批次 1-16 除上述外彼此独立（批次 17 为退役批，无依赖；按约定串行推进，每批全量 pytest 绿）。

> 注：批次 13/14/15 单文件或双文件属"专项批"（文件体量大、1 轮即满），符合"粒度 1 轮可完成"的更高优先级约束（P0-brief 已确认该排序）。批次 0 是唯一必须先行批（交付 conftest 基座，一切测试依赖它）。

## 5. 文档重写清单（用户确认归本任务）

### 表 E：协议文档 / CI 全量引用清单（2026-08-15 逐文件实测）

| 文件 | 需改内容 |
|------|---------|
| agate/platform-notes.md | Windows 章节 5 处 .sh 引用 + `bash install-hook.sh` + 复制模式前提 + 第 96 行「bats（仅开发者）」表 + 第 145/146 行「bats 安装麻烦」「CI 仅 ubuntu」→ 改为 pytest 表述（Windows 用 `python -m pytest`，无需 bats） |
| agate/SETUP.md | 测试运行命令 bats → pytest；pyyaml 强制安装（已随 TAG0010）→ 补 pytest 安装说明 |
| agate/UPGRADING.md | **新增本版本迁移章节**：bats→pytest 是破坏性变更（用户/外部直接跑 bats 的项目受影响），逐条列；第 133/150 行「count-tests.sh / check-windows-smoke.sh 不在迁移范围」表述更新为：check-windows-smoke.sh 已退役（pytest marker 承接冒烟）、count-tests.sh 改写为 pytest 收集计数（§6）；第 172/185 行「bats job 增 windows-latest」描述改 pytest |
| agate/dispatch-protocol.md | 第 875/878 行「pytest/bats 结果」表述 → 统一 pytest |
| agate/git-integration.md | 第 55 行 `chore: 升级 pytest` 示例保留（已是 pytest，无 bats 引用）——核查确认仅此一处 |
| .github/workflows/protocol-tests.yml | bats job → pytest job（Linux 全量 + Windows 冒烟）；check-windows-smoke.sh 调用 → **退役**，Windows 冒烟 job 改用 `python -m pytest agate/tests/ -m windows_smoke`；count-tests 步骤（若有）→ pytest 收集计数；shellcheck 收敛到 3 薄壳（已随 TAG0010）+ ruff job 保留 |
| AGENTS.md（仓库根） | 「测试约定」章节：bats 命令 → pytest；「开发命令」bats/count-tests → pytest；测试平台无关原则中 check-windows-smoke.sh 描述更新为「退役，marker 机制承接」 |
| agate/tests/README.md | 快速开始/覆盖度表/CI 章节/目录结构——从 .bats 改为 .py；count-tests.sh 引用更新；R2.4 已知风险（archive flaky）标注迁移后是否仍适用 |
| agate/scripts/README.md | 第 81 行「agate-next-card.bats 的 9 个 sha256 测试」→ 改 pytest 文件引用 |
| agate/assets/templates/handoff-template.md | 第 33/34/49/60/73/80/101/107 行 bats 命令/依赖 → pytest |
| agate/assets/review-roles/protocol-alignment-review.md | 第 23 行「变更是否有对应 bats 测试」「bats 全量实跑输出」→ pytest；第 41 行 `.bats` fixture 引用 |
| agate/assets/formatters/README.md | 第 53 行「bats | generic-tap.sh」表格行（保留，formatters 支持多框架，bats 仍是可用 formatter 之一）——评估保留或删除 |
| agate/tests/scripts/count-tests.sh | 统计对象消失 → 改写成 pytest 收集计数（`python3 -m pytest --collect-only -q | tail -1` 或等价）；§6.3 已定改写，不再与 Windows 冒烟决策绑定 |
| agate-workspace/archived/plans/agate-test-plan-2026-07-01.md | count-tests.sh 第 23 行引用的「附录 A」目标已归档（git log 显示已 archive）——count-tests.sh 的漂移提示需改为指向现行 pytest 口径 |
| docs/reviews/*（历史评审） | **不做全量重写**（历史记录，保留 .bats 引用） |

> 计数口径：以上为逐文件 `rg` 实测。P4 文档批次按此清单逐文件同步。

## 6. helpers 迁移方案 + Windows 冒烟评估

### 6.1 helpers → pytest fixture 映射（526 行）

| helpers 文件 | 行数 | 迁移目标 |
|--------------|------|---------|
| load.bash | 48 | → conftest.py 会话级 fixture：`AGATE_ROOT` 解析（保留 `_resolve_agate_root` 的反推逻辑：找最近的 scripts/ + assets/ 目录）；`AGATE_SCRIPTS`/`AGATE_ASSETS` 常量；`AGATE_ROOT` 校验失败 fail-closed |
| fixtures.bash | 412 | → conftest.py fixture 集合：`task_dir`（create_task_dir 等价，基于 tmp_path + 写 P0-P8 文件/.state.yaml + agent: test frontmatter + Given 行）；`python`/`detect_python`（probe_python 语义：python3 → python 回退）；`py_path`（Windows MSYS 路径转换，Linux 直接返回）；`git_repo` + `git_commit`/`git_stage`/`git_staged_diff`/`git_staged_files`（git-helper 迁移）；`add_frontmatter_field`/`add_p1_field`/`add_p2_candidate_count`/`add_pruning_excuse`/`add_evidence_file`/`add_p6_pass`/`add_p6_fail`/`add_p1_bdd`/`add_p2_review` 等 helper → pytest fixture/函数 |
| git-helper.bash | 66 | → conftest.py `git_repo` fixture（git_init 等价：临时目录 + git init + user 配置 + gpgsign false）+ git 命令封装 |
| 平台敏感机制 | — | `create_python_shim_bin`（bats 特有的 python3 shim）——**pytest 下不再需要**（pytest 直接用 python 解释器跑 subprocess），该机制退役；`probe_python` 保留（hook 薄壳语义，helpers-python.bats bdd-17 已测） |

**迁移映射表（bats 断言 → pytest 断言）**：

| bats 语义 | pytest 等价物 |
|-----------|---------------|
| `run <cmd>` + `$status` / `$output` | conftest `run_cli(cmd, *args, **kwargs)` helper → 返回对象（`.returncode` / `.stdout` / `.stderr`，subprocess.run + `encoding="utf-8"` + `capture_output=True`） |
| `[ "$status" -eq N ]` | `assert result.returncode == N` |
| `[[ "$output" == *"X"* ]]` | `assert "X" in result.stdout`（或 stderr） |
| `setup()`/`teardown()` | pytest `autouse` fixture 或函数级 fixture |
| `BATS_TEST_TMPDIR` | pytest `tmp_path` fixture |
| `skip` 条件（平台分支） | `pytest.mark.skipif`（Windows 软链/Linux 断言分平台） |
| `load ../helpers/load.bash` | conftest.py 自动加载（无需每文件 load） |
| `create_task_dir P0 P1 ...` | `task_dir` fixture（参数化 phases/risk_level/with_evidence） |
| `@test "bdd-N ..."` | `def test_bdd_N_...()`（保留 bdd 编号，便于 P6 对照） |

### 6.2 Windows 冒烟机制评估（已定：退役 check-windows-smoke.sh → pytest marker）

**现状**：check-windows-smoke.sh 对每个 .bats 选"第 1 个用例 + 平台关键词用例"作 Windows 技术路线冒烟（v0.45 决策，全量 Windows bats 太慢）。

**评估**（P0-brief 已知风险要求"若 pytest 全平台可跑，评估退役；若 Windows 性能仍需，保留"）：
- **pytest 全平台原生可跑**（无需 bats-core 安装、无 TAP/`@test` 名称正则依赖），Windows runner 直接 `python -m pytest` 即可——**bats 版的"代表选取脚本"（按 @test 名称正则 grep）失去存在必要**。
- **但 Windows 全量 pytest 是否仍慢**：迁移后测试数量不变（749 用例等价物，756 − 7 退役），Windows 全量跑仍有分钟级耗时。为控制 CI 时间，建议**保留"Windows 只跑代表子集"的思路，但用 pytest 原生 marker 替代脚本选取**：
  - 平台敏感用例标 `@pytest.mark.windows_smoke`（等价现关键词：cp1252 / CRLF / Windows / symlink / py_path / 复制模式 / shim / PYTHONIOENCODING 等）；
  - Windows CI 跑 `python -m pytest agate/tests/ -m windows_smoke`；
  - Linux CI 跑全量（marker 不影响）。
- **决策（已定，P1 修订采纳）**：`check-windows-smoke.sh` **退役**，`check-windows-smoke.bats`（7 用例，测脚本选取行为）**随之退役**；冒烟覆盖由 pytest marker 承接。理由：a) pytest 原生全平台，bats 版选取脚本是"为 bats 性能问题设计的一次性适配器"，其测试对象（脚本本身）消失；b) marker 机制更直接、无脚本维护面；c) P0-brief 已授权"pytest 全平台可跑则退役"。

### 6.3 count-tests.sh 评估
- 统计对象（`^@test`）随 bats 退役消失 → 改写为 pytest 收集计数（`python3 -m pytest --collect-only -q | tail -1` 提取 collected 数），或退役。
- 建议：改写为 pytest 收集计数脚本（保留"用例数不漂移"的守护职责），因为它还被 handoff-template/AGENTS.md/UPGRADING 引用；P2 定实现。

## 7. BDD 验收条件

> 每条独立可二值判定（PASS/FAIL）。覆盖 P0-brief 的 5 条验收标准 + 硬约束。

### 迁移完整性
#### BDD-1: 全量 pytest 全绿替代 bats（验收①）
> 计数口径修订（P1 活基线，BLOCKER-1）：756 → **749**。`check-windows-smoke.bats`（7 用例）测的是 check-windows-smoke.sh 自身的代表选取行为，该脚本随 pytest 化退役（§6.2 决策），7 用例不迁移；冒烟覆盖由 `@pytest.mark.windows_smoke` marker 承接（BDD-4/BDD-12），退役的 7 用例不属"覆盖减少"。
- Given 迁移完成（60 个 .bats / 749 @test 全部迁移为 pytest；check-windows-smoke.bats 随脚本退役；bats 整体退役）
- When 运行 `python3 -m pytest agate/tests/`（Linux 全量）
- Then exit 0，全部用例 PASS，且 `--collect-only` 收集数 ≥ 749（迁移 749 用例覆盖不减少 + marker 承接 Windows 冒烟）

#### BDD-2: consistency 0 ERROR（--strict）（验收②）
- Given 协议文档重写完成（§5 表 E）
- When 运行 `python3 agate/scripts/check-protocol-consistency.py --strict`
- Then exit 0，无 ERROR 无 WARNING

#### BDD-3: ruff 静态检查覆盖全部 py（验收③）
- Given 测试代码全部为 .py，且 pyproject.toml 规则集已并入 [tool.ruff] 的测试路径（src 含 agate/tests）
- When 运行 `ruff check agate/`（按 pyproject.toml 规则集）
- Then exit 0，无 error 级违规

#### BDD-4: Windows CI 冒烟通过（验收④）
- Given CI Windows matrix 执行 pytest 冒烟子集（`-m windows_smoke` marker 或等价）
- When 运行冒烟子集
- Then 全部代表用例 PASS，无平台机制（复制模式/CRLF/编码/py 探测/路径）失败

#### BDD-5: 平台假设扫描器覆盖 .py 且测试树干净（验收⑤）
- Given 扫描器规则集已覆盖 .py（TAG0010 完成），且迁移后的 pytest 测试代码平台无关
- When 对 `agate/tests/` 全树运行 check-platform-assumptions.py
- Then exit 0（无 Unix 假设命中）；且含 R1-R5 假设的 .py/.bats fixture 能被检出（非空转）

#### BDD-6: 迁移期双跑对照（P0 known_risks「每批 pytest 绿 + 原 bats 对照」）
- Given 任一迁移批次完成
- When 同时运行该批 pytest 新文件 + 原 .bats 文件
- Then 两者全部 PASS（迁移期过渡保障，直至 bats 整体退役）

### 平台与硬约束
#### BDD-7: 测试代码显式 encoding=utf-8
- Given 迁移产生的测试 py 代码
- When 运行 encoding 守卫（agate-scripts-encoding 等价物，扫 agate/tests/**/*.py）
- Then 无 `open()`/`read_text()`/`subprocess.run(text=True)` 缺 `encoding=` 的违规

#### BDD-8: 测试代码兼容 Python 3.8+ 且平台无关
- Given 迁移产生的测试 py 代码
- When 以 py38 target 静态检查（ruff target-version=py38）+ 扫描器扫全树
- Then 无 3.9+/3.10+ 专属语法；无 R1-R5 平台假设命中

#### BDD-9: CLI 输出契约与既有数据兼容（迁移不破坏断言对象）
- Given 既有测试夹具（tests/fixtures/ 静态 Gold、.state.yaml、P{n}-*.md）
- When 迁移后的 pytest 用例按原接口读写/执行
- Then 断言对象（exit 0/1/2、`GATE ...:` 前缀、`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出、gate-result.json 结构、sha256 字节稳定性）与 bats 时代一致

#### BDD-10: helpers fixture 行为等价
- Given helpers 已迁移为 conftest.py fixture
- When 运行 sanity/helpers-python 的 pytest 等价物 + 抽查依赖 task_dir/git_repo 的用例
- Then create_task_dir/git_init 等 fixture 产出与 bats 时代结构一致（P0-P8 文件、.state.yaml、frontmatter、Given 行、git 配置）

#### BDD-11: hook 链测试在 pytest 下等价
- Given pre-commit/pre-push/commit-msg 薄壳保留（TAG0010 已定）
- When 运行 pre-commit-hook / pre-push-hook / commit-msg-self-gate 的 pytest 等价物
- Then 断言行为（exit 拦截/放行、WARNING、PROD_TOUCHED、dispatch-context hash、P6 代码直改拦截）与 bats 时代一致

#### BDD-12: Windows 冒烟机制决策落地（§6.2）
- Given §6.2 决策已定（退役 check-windows-smoke.sh + check-windows-smoke.bats → pytest marker）
- When 检查 tests/ 下无 `check-windows-smoke.sh`（无残留，含 P4 退役提交）；Windows CI 冒烟用 `-m windows_smoke`
- Then 冒烟机制无 bats 依赖；Windows CI 冒烟 job 引用 pytest 命令

## 8. 待确认清单

[NO_NEED_CONFIRM]

无阻塞性待确认项。以下为有倾向的审计痕迹项（主 Agent 可直接采纳，不阻塞推进）：

- [DECIDED: check-windows-smoke.sh **退役**（P1 修订采纳，原 SUGGEST 升级为既定决策，§6.2 理由 a/b/c）：冒烟由 `@pytest.mark.windows_smoke` marker 承接；check-windows-smoke.bats（7 用例）随之退役，BDD-1 计数口径 756 → 749（60 文件/749 迁移范围）]
- [SUGGEST: count-tests.sh **改写为 pytest 收集计数**（`python3 -m pytest --collect-only` 提取 collected 数），保留"用例数不漂移"守护职责（handoff/AGENTS/UPGRADING 多处引用，退役会造成引用链断裂）]
- [SUGGEST: 测试文件命名 `test_*.py` 同目录替换 `*.bats`（unit/regression/integration/scripts 目录结构不变），P6 BDD 对照用 `test_bdd_N_*` 函数名保留编号]
- [SUGGEST: 平台敏感用例 marker 清单 = 现 check-windows-smoke.sh 的 PLATFORM_KEYWORDS_RE 关键词对应用例（cp1252/CRLF/Windows/symlink/py_path/复制模式/shim/PYTHONIOENCODING 等），P4 迁移时逐文件打标]
- [SUGGEST: ruff 的 src 从 `["agate/scripts"]` 扩展为 `["agate/scripts", "agate/tests"]`，让测试 py 也在静态检查范围内（验收③一致性）]

## 9. 裁剪说明 + 能力声明

- **risk_level: high**——727→749 断言全量改写（756 基线 − 7 退役）是数周密集工作 + 高回归风险（P0 known_risks 定级）；影响面横跨测试全树、helpers、文档、CI 全链；与 TAG0010 同级。
- **phases: [P1, P2, P3, P4, P5, P6, P7, P8]**——无裁剪。P2 必须产出迁移映射表 + 批次细化方案；P3 设计每批 TDD 红绿灯（新 pytest 先红后绿）；P4 按 17 批逐步实现（批次 17 为退役批，不实现；每批独立可验收）；P5 每批验证 + 全量；P6 逐条 BDD 对照（12 条 ≥1）；P7 一致性（packages 跨文件交叉核对 + 文档引用清单）；P8 发布（UPGRADING 破坏性变更章节 + version badge + tag）。
- **domains: [backend, cli]**——测试框架（backend）+ CLI 工具链断言（cli）。无 frontend/mcp/security 影响。
- **change_type: refactor**——测试框架迁移不改变产品行为，符合 refactor 语义（frontmatter schema 仅支持 refactor）。
- **capability_requirements**：见文件头 frontmatter。pytest（available：系统 python3 已装 9.0.3，venv 需 pip install）+ ruff（available）+ Windows CI（available）均不阻塞；`requires_minimal_validation: true`（Windows 冒烟行为本地 Linux 无法验证，P2 architect 须产出 `minimal_validation:` 块）。
- **P1 基线保护**：本文件为需求基线，后续阶段不直接修改；确需变更走 `[BASELINE_CHANGE: 理由]` + 主 Agent 批准流程。

## 10. SCOPE+ 处理

> 活基线预留节。后续阶段发现新隐含需求时由主 Agent 增补并标 `[SCOPE+ from Pn]`；P7 一致性审查后登记 `[SCOPE_RESOLVED: ...]`。
