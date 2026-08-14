---
phase: P3
task_id: TAG0011-test-migration
type: test-cases
parent: P2-design.md
trace_id: TAG0011-P3-20260815
status: draft
created: 2026-08-15
agent: test-designer
change_type: refactor
---

# P3 测试设计（回归口径）— agate 测试框架迁移（阶段二，bats → pytest）

> 本文件是 TAG0011（refactor 任务）的 P3 测试设计。采用 **P3 卡片 §refactor 任务：回归测试口径**：
> 重构（bats → pytest）无新增功能行为可断言，测试设计 = **复用/保留既有 749 用例** + 标注每条回归用例
> 覆盖的迁移路径（哪个 bats → 哪个 pytest 文件/批次）；**不新增功能行为断言**。
> 权威基线：P1-requirements.md（12 BDD + 17 批规划）+ P2-design.md（语义映射表 §3.2 + 批次设计 §5，
> 含 BLOCKER-1 `$output` 合并流修正）。本文件只做设计，不写实现代码（P4 分批写）。
> 实测核对：`grep -c '^@test'` 全树 = 756（含 check-windows-smoke.bats 7）；迁移范围 60 文件 / 749 @test。

---

## 1. 回归口径声明

1. **行为契约不变**：本次重构只改变**测试断言载体**（bats `run`/`$status`/`$output` → pytest
   `run_cli`/`CommandResult.returncode`/`CommandResult.output`），**不改变被测对象**（47 个产品 py 脚本、
   3 个 hook 薄壳零改动，TAG0010 已完成）与**断言对象契约**（exit 0/1/2、`GATE ...:` 前缀、
   `AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出、gate-result.json 结构、sha256 字节稳定性）。
2. **复用既有用例**：749 条既有 @test（60 个 .bats）逐条迁移为 pytest 函数，**1 @test → 1 test 函数**
   （P2 §0，可参数化但收集数不减少），不新增功能性质 BDD、不新增行为断言。函数名保留 `bdd-N` 编号
   （`@test "bdd-N ..."` → `def test_bdd_N_...()`），其余按 `test_<前缀>_<序号>_<slug>` 命名（P2 §3.3），
   供 P6 BDD 对照。
3. **等价判定 = 双跑对照**（BDD-6）：每批验收 = 新 pytest 全绿 + 原 .bats 该批全绿 + consistency 0 ERROR，
   直至 bats 整体退役。这是"重构前后行为一致"的机械判定。
4. **流语义回归锁**：bats `$output` = stdout + stderr **合并流**（bats 1.x 固定语义）→ pytest 统一映射为
   `CommandResult.output` 合并流属性（BLOCKER-1）；26 处 `[ -z "$output" ]` 空/非空断言一律基于合并流；
   stderr 特定内容断言（`GATE ...:` 等）先判流归属。批次 1 补 1 条"脚本写 stderr + 合并流断言"正例作为
   流语义回归锁（EB.8 等价物）。
5. **不新增行为断言的例外 = 机制验证等价物**：随载体更换而必须改写/新增的"机制层"断言（见 §3）不是功能
   行为断言，是迁移等价性保障（如 `bats -c` 收集计数 → `pytest --collect-only`；encoding 守卫扫 .py；
   windows_smoke marker 承接冒烟），均已在 P1 BDD-1/4/5/7/8/12 声明范围内。
6. **P3 gate 说明**：refactor 任务跳过 check-tdd-red 红灯步骤（P3 卡 §refactor，测试套件本就全绿）；
   P3 gate = 本文件存在性检查（含 test_code_dir）。回归质量由 P5 全量回归 + P6 regression.log 兜底。

---

## 2. test_code_dir 声明

```yaml
test_code_dir: agate/tests/
```

- 目录结构**不变**（P2 方案 A1 同目录替换）：unit/ regression/ integration/ scripts/ + 根 sanity，
  每个 `*.bats` 同目录替换为 `test_*.py`；`.bats` 与 `test_*.py` 迁移期共存，bats 整体退役时删 `.bats`。
- 新增 `agate/tests/conftest.py`（P2 §3.1 单根 fixture 体系，替代 helpers/ 三文件）。
- `agate/tests/helpers/`（load.bash + fixtures.bash + git-helper.bash）→ **退役**，职责并入 conftest.py。
- `agate/tests/scripts/check-windows-smoke.sh` + `check-windows-smoke.bats` → **退役删除**（批次 17，P1 §6.2）。
- `agate/tests/scripts/count-tests.sh` → **改写**为 pytest 收集计数（脚本路径保留，P2 §3.5）。
- pyproject.toml 追加 `[tool.pytest.ini_options]`（testpaths + markers 注册）+ ruff src 扩展含 tests。

**命名约定契约**（P2 §3.3，`-k` 验证命令的匹配基准）：module 名 `test_<snake_bats_name>.py`
（如 `agate-json-get.bats` → `test_agate_json_get.py`、`sanity.bats` → `test_sanity.py`、
`tests/scripts/check-platform-assumptions.bats` → `tests/scripts/test_check_platform_assumptions.py`）。

---

## 3. BDD → 测试映射（12 条 BDD，P1 §7）

> 映射口径：1:1 或 1:N 明确。N 情形 = BDD 横跨多批/多文件，逐项列迁移批次与 pytest 文件。
> refactor 口径：每条 BDD 的 pytest 用例是既有 bats 用例的**迁移等价物**，不是新增行为断言。

| BDD | 验收点（简述） | 映射（1:1 / 1:N） | 覆盖的 pytest 文件 / 迁移批次 | 迁移路径（bats → pytest） |
|-----|---------------|------------------|-------------------------------|---------------------------|
| **BDD-1** | 全量 pytest 全绿替代 bats，`--collect-only ≥ 749` | 1:N | 全树 60 个 test_*.py（批次 0-16）+ count-tests.sh 改写（P2 §3.5）；含 749 收集数自检用例 | 60 个 .bats → 60 个 test_*.py；check-windows-smoke.bats（7）退役不计 |
| **BDD-2** | consistency 0 ERROR（--strict） | 1:N | 批次 14 `integration/test_consistency.py`（consistency.bats 11）+ 批次 10 `unit/test_check_protocol_consistency.py`（check-protocol-consistency.bats 3）+ 批次 15 `unit/test_env_adapt_docs.py`（CI 断言） | consistency.bats / check-protocol-consistency.bats / env-adapt-docs.bats |
| **BDD-3** | ruff 覆盖全部 py（src 含 tests） | 1:1 | 批次 15 `unit/test_env_adapt_docs.py`（bdd-34 断言目标：shellcheck 3 薄壳收敛 + ruff `agate/` 含 tests） | env-adapt-docs.bats |
| **BDD-4** | Windows CI 冒烟（`-m windows_smoke`）全 PASS | 1:N | 平台敏感用例跨批打 `@pytest.mark.windows_smoke`（P2 §3.4 打标清单，§5 表 W）；CI 配置在 .github/workflows/protocol-tests.yml | 现 check-windows-smoke.sh PLATFORM_KEYWORDS_RE 关键词对应用例 + 每文件第 1 用例 |
| **BDD-5** | 平台假设扫描器覆盖 .py 且 tests/ 全树干净 | 1:1 | 批次 16 `tests/scripts/test_check_platform_assumptions.py`（16）——干净树契约（迁移终态 .bats 退役后 0 命中）+ R1-R5 正例可检出 | tests/scripts/check-platform-assumptions.bats |
| **BDD-6** | 迁移期双跑对照（每批 pytest + 原 bats 双绿） | 1:N | 每批验证命令（§6 批验证命令表）内嵌"原 .bats 对照"；批次 11 回归套件（17）为最终对照锚 | 每批 .bats → 对应 test_*.py 双跑 |
| **BDD-7** | 测试代码显式 encoding=utf-8 | 1:N | 批次 5 `unit/test_agate_scripts_encoding.py`（agate-scripts-encoding.bats 2，守卫扫 `agate/tests/**/*.py`）——**迁移后 test_*.py 全数受检** | agate-scripts-encoding.bats |
| **BDD-8** | py38 兼容 + 平台无关（ruff target + 扫描器全树） | 1:N | 批次 16 test_check_platform_assumptions.py（全树扫描）+ pyproject `target-version=py38`（工具层，非用例）+ BDD-7 同源编码守卫 | check-platform-assumptions.bats / agate-scripts-encoding.bats |
| **BDD-9** | CLI 输出契约与既有数据兼容（exit / GATE 前缀 / 两行输出 / gate-result.json / sha256） | 1:N | 批次 0 `unit/test_agate_workspace_resolve.py`（两行输出，WR.1-WR.9）；批次 3 `unit/test_agate_next_card.py`（sha256 字节稳定性 22）；批次 8 test_check_gate.py（GATE 前缀全集）；批次 5 test_agate_capture_env_baseline.py（gate-result.json）；批次 2 共享工具 | agate-workspace-resolve / agate-next-card / check-gate / agate-capture-env-baseline / agate-json-get 等全部断言载体切换批 |
| **BDD-10** | helpers fixture 行为等价（create_task_dir/git_init 结构一致） | 1:N | 批次 0 `test_sanity.py`（sanity.bats 6，conftest 体系自检）+ `unit/test_helpers_python.py`（helpers-python.bats 3，python_exe 探测）+ 抽查各批依赖 task_dir/git_repo 用例（任务全树） | sanity.bats / helpers-python.bats / fixtures.bash+git-helper.bash → conftest.py |
| **BDD-11** | hook 链测试 pytest 等价（拦截/放行/WARNING/PROD_TOUCHED/dispatch hash/P6 拦截） | 1:N | 批次 12 `unit/test_commit_msg_self_gate.py`（4）+ `integration/test_commit_msg_self_gate_integration.py`（6）+ `integration/test_pre_push_hook.py`（4）；批次 13 `integration/test_pre_commit_hook.py`（48）+ `integration/test_dispatch_context_card.py`（8） | commit-msg-self-gate.bats（unit+integration）/ pre-push-hook.bats / pre-commit-hook.bats / dispatch-context-card.bats |
| **BDD-12** | Windows 冒烟机制决策落地（check-windows-smoke.sh/bats 退役 + CI 引用 marker） | 1:1 | 批次 17 退役批（删除 check-windows-smoke.sh + check-windows-smoke.bats 7，不迁移）；CI pytest job Windows matrix 引用 `-m windows_smoke`；grep 断言 tests/ 无残留 | check-windows-smoke.bats → 退役（冒烟覆盖由 §5 表 W marker 承接） |

---

## 4. 用例覆盖映射（60 bats / 749 @test → 60 test_*.py，按 P2 17 批）

> 覆盖映射 = **逐文件 1:1**（`*.bats` → `test_*.py`，函数级 `@test` → test 函数 1:1 保留），批内 @test 数
> 已实测核对（`grep -c '^@test'`，2026-08-15）。批次 0-16 共 60 文件 / 749 @test；批次 17 为退役批（0 文件）。

### 批次 0 — pytest 基座（3 文件 / 19 @test；交付 conftest.py + pyproject）

| bats（迁移源） | @test | pytest 文件 | 覆盖的迁移路径 / 回归点 |
|---------------|-------|-------------|------------------------|
| `tests/sanity.bats` | 6 | `tests/test_sanity.py` | conftest 体系自检：agate_root 解析（load.bash `_resolve_agate_root` 反推）/ task_dir（create_task_dir 默认全阶段、自定义 phases）/ add_pruning_excuse / git_repo（git_init）+ git_commit+git_stage |
| `unit/helpers-python.bats` | 3 | `unit/test_helpers_python.py` | python_exe 探测（detect_python python3→python 回退；probe_python fail-closed）；**create_python_shim_bin 退役**——pytest 直跑解释器，shim 断言改写为 python_exe fixture 语义 |
| `unit/agate-workspace-resolve.bats` | 10 | `unit/test_agate_workspace_resolve.py` | resolve_workspace 两行输出契约（`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=`，stdout）+ .agate.env 解析（相对/绝对/含空格）+ AGATE_TASKS_DIR 二级源 + CRLF `\r` 污染（bdd-18，含 windows_smoke 打标） |

### 批次 1 — 纯工具无 git（5 文件 / 11 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/agate-changelog-unreleased.bats` | 2 | `unit/test_agate_changelog_unreleased.py` | 纯 stdin/stdout；**1 处 `[ -z "$output" ]` → `assert result.output == ""`（合并流）** |
| `unit/agate-card-inject.bats` | 2 | `unit/test_agate_card_inject.py` | 纯文件读写 |
| `unit/agate-evidence-consistency.bats` | 2 | `unit/test_agate_evidence_consistency.py` | fixtures/ 静态夹具加载（load_fixture）；**1 处 `[ -z "$output" ]` 合并流** |
| `unit/agate-gate-missing-cmds.bats` | 2 | `unit/test_agate_gate_missing_cmds.py` | 纯 stdin；**1 处 `[ -z "$output" ]` 合并流** |
| `unit/agate-gate-p5-count.bats` | 3 | `unit/test_agate_gate_p5_count.py` | 纯 stdin |
| **回归锁（新增，非行为断言）** | +1 | `unit/test_agate_gate_p5_count.py` 或独立 | **流语义回归锁（P2 §5 批次 1 要求）**：构造"脚本写 stderr + bats `$output` 合并流命中"等价场景 → `assert "X" in result.output`（EB.8 等价物），锁定合并流语义，防止后续批映射为 `.stdout` 漂移 |

### 批次 2 — 共享工具（6 文件 / 39 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/agate-json-get.bats` | 8 | `unit/test_agate_json_get.py` | stdin 管道（`run_cli(input=...)`）；JGET.1-8（get/len/index/set/count_prefix/list/escape）；**JGET.7 `[ -z "$output" ]` → 合并流**；JGET.5/6 PROJECT_MODULE env 传入 |
| `unit/agate-md-field-get.bats` | 14 | `unit/test_agate_md_field_get.py` | task_dir；frontmatter/字段读取 |
| `unit/agate-state-get.bats` | 6 | `unit/test_agate_state_get.py` | .state.yaml 文件；**2 处 `[ -z "$output" ]` 合并流** |
| `unit/agate-retreat-state.bats` | 4 | `unit/test_agate_retreat_state.py` | 纯文件；**1 处 `[ -z "$output" ]` 合并流** |
| `unit/agate-state-yaml-check.bats` | 3 | `unit/test_agate_state_yaml_check.py` | .state.yaml；**1 处 `[ -z "$output" ]` 合并流** |
| `unit/agate-read-p5-commands.bats` | 4 | `unit/test_agate_read_p5_commands.py` | 纯 stdin；**2 处 `[ -z "$output" ]` 合并流** |

### 批次 3 — 内容生成工具（3 文件 / 53 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/agate-next-card.bats` | 22 | `unit/test_agate_next_card.py` | **sha256 字节稳定性（22 中 9 个 sha256 断言）**——输出精确等值 `.strip()`/`.rstrip("\n")` 后比较（P2 §3.2 精确等值注意）；2 处平台关键词用例（含 windows_smoke） |
| `unit/agate-inject-card.bats` | 11 | `unit/test_agate_inject_card.py` | task_dir；文件写入 |
| `unit/agate-render-dispatch-prompt.bats` | 20 | `unit/test_agate_render_dispatch_prompt.py` | task_dir + dispatch-context 渲染 |

### 批次 4 — 上下文/归档/回退工具（4 文件 / 37 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/agate-extract-context.bats` | 16 | `unit/test_agate_extract_context.py` | task_dir；1 处平台关键词（windows_smoke） |
| `unit/agate-archive-stale-outputs.bats` | 7 | `unit/test_agate_archive_stale_outputs.py` | **R2.4 flaky（时间戳）**：隔离单跑必过语义保留；git_repo |
| `unit/agate-migrate-workspace.bats` | 9 | `unit/test_agate_migrate_workspace.py` | git + 工作区迁移 |
| `unit/agate-retreat-to.bats` | 5 | `unit/test_agate_retreat_to.py` | git_repo + hook 集成（依赖批次 0 git_repo） |

### 批次 5 — 环境/债务/编码守卫（4 文件 / 42 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/agate-capture-env-baseline.bats` | 15 | `unit/test_agate_capture_env_baseline.py` | git + gate-result.json 结构（EB.7 已捕获 / EB.8 本身崩溃 stderr 归属先判流） |
| `unit/agate-debt-check.bats` | 21 | `unit/test_agate_debt_check.py` | task_dir + git；`GATE DEBT WARNING`（stderr）；**5 处 `[ -z "$output" ]` 合并流** |
| `unit/agate-image-check.bats` | 4 | `unit/test_agate_image_check.py` | **Pillow 可选**：`@pytest.mark.skipif(not PIL)` 运行时跳过（收集数不受影响，BDD-1 ≥749 不破）；运行时造图（tmp_path） |
| `unit/agate-scripts-encoding.bats` | 2 | `unit/test_agate_scripts_encoding.py` | encoding 守卫扫 `agate/tests/**/*.py`——**本文件及全部 test_*.py 自身受检**（BDD-7） |

### 批次 6 — check 状态/裁剪/scope（3 文件 / 69 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/check-state-transition.bats` | 30 | `unit/test_check_state_transition.py` | git_repo + cwd + subprocess 调 py 样板（git show HEAD 断言）；`GATE STATE`（stderr）→ 合并流 |
| `unit/check-pruning.bats` | 29 | `unit/test_check_pruning.py` | task_dir + git；`GATE PRUNING`（stderr）→ 合并流 |
| `unit/check-scope-resolved.bats` | 10 | `unit/test_check_scope_resolved.py` | task_dir |
| 子批 | — | 6a state_transition(30) → 6b pruning(29) → 6c scope(10) | 每子批独立 `-k` 验证（§6） |

### 批次 7 — check 基础 gate（5 文件 / 57 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/check-changelog.bats` | 8 | `unit/test_check_changelog.py` | task_dir + git |
| `unit/check-frontmatter.bats` | 14 | `unit/test_check_frontmatter.py` | task_dir；**2 处 `[ -z "$output" ]` 合并流** |
| `unit/check-state-yaml.bats` | 9 | `unit/test_check_state_yaml.py` | .state.yaml 文件 |
| `unit/check-retrospective.bats` | 10 | `unit/test_check_retrospective.py` | task_dir；**3 处 `[ -z "$output" ]` 合并流** |
| `unit/check-p6-format.bats` | 16 | `unit/test_check_p6_format.py` | task_dir；P6 格式校验 |

### 批次 8 — check-gate 专项（3 文件 / 146 @test，最大批，子批 8a-8h）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/check-gate.bats` | 124 | `unit/test_check_gate.py` | check-gate.py 全 gate 分支（gate_p0..p8 函数边界）；GATE 前缀全集（stderr→合并流）；task_dir + git；`bdd-11/14/28/29` + `test_bdd_1..8` refactor 系列 + `D-drift`/`G-drift`/`TAG0005` + `G_RETREAT`/`G_NC_BINARY`/`G_SUGGEST`/`G_DG_ANCHOR`；1 处平台关键词（windows_smoke） |
| `unit/check-gate-p1-review.bats` | 9 | `unit/test_check_gate_p1_review.py` | P1 review 分支（PG 前缀） |
| `unit/check-gate-p5-diff.bats` | 13 | `unit/test_check_gate_p5_diff.py` | P5 diff 分支（task_dir + git） |
| 子批 | — | 8a G0/G1/G3/G4/OTHER(~13) → 8b G2+BDD1/9/10+CMD_EXEC(~32) → 8c G5(~10) → 8d G6+BDD16+test_bdd_1..8(~20) → 8e G7+DG_ANCHOR+bdd11(~14) → 8f G8(~12) → 8g RETREAT/NC_BINARY/SUGGEST(~15) → 8h DRIFT/TAG0005(~10) | 每子批 ≤32 @test（P2 §5 子批表）；`-k` 增量验证非严格分区（8 子批完成后整文件兜底） |

### 批次 9 — P6 验收链 + vision（4 文件 / 79 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/check-p6-evidence.bats` | 30 | `unit/test_check_p6_evidence.py` | fixtures/ 静态夹具（full-task P6-evidence/）+ Pillow 可选 skipif |
| `unit/check-p6-provenance.bats` | 36 | `unit/test_check_p6_provenance.py` | fixtures/ + git_repo；`GATE PROVENANCE`（stderr）→ 合并流 |
| `unit/agate-vision-blocker.bats` | 2 | `unit/test_agate_vision_blocker.py` | fixtures/ 静态夹具 |
| `unit/ci-gate-backstop.bats` | 11 | `unit/test_ci_gate_backstop.py` | **`bash -c "... 2>&1 || true"` 显式合并 → `.output` 合并流**；git + 平台探测；4 处平台关键词（windows_smoke） |
| 子批 | — | 9a evidence(30) → 9b provenance(36) → 9c vision_blocker(2)+backstop(11) | 每子批独立 `-k`（§6） |

### 批次 10 — TDD 红灯链 + 一致性（4 文件 / 60 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/check-tdd-red.bats` | 43 | `unit/test_check_tdd_red.py` | **TEST_RUNNER 语义 + formatter**：断言对象从 bats/pytest 双跑改为 **pytest 输出解析**（`pytest.sh` formatter 归一）；mock 用 TEST_RUNNER 环境变量指向 fake 脚本；`TDD_CHECK:` stdout / 错误 stderr 先判流归属 |
| `unit/check-tdd-red-formatter.bats` | 13 | `unit/test_check_tdd_red_formatter.py` | FMT.1-12 + bdd-35f（formatter 脚本输出归一化） |
| `unit/dispatch-context-warning.bats` | 1 | `unit/test_dispatch_context_warning.py` | AGATE_ROOT_FAKE 复制薄壳 + dispatch-context 缺失 WARNING（**未复制 agate-next-card.py 场景保留**，等价行为断言） |
| `unit/check-protocol-consistency.bats` | 3 | `unit/test_check_protocol_consistency.py` | 跑一致性脚本（0 ERROR） |
| 子批 | — | 10a tdd_red(43) → 10b formatter(13)+dispatch_warning(1)+consistency(3) | 每子批独立 `-k`（§6） |

### 批次 11 — 回归套件（6 文件 / 17 @test，依赖批次 8）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `regression/v040-dotarchived-exclusion.bats` | 2 | `regression/test_v040_dotarchived_exclusion.py` | .archived 排除（agate-archive-stale-outputs.py） |
| `regression/v060-design-gap.bats` | 4 | `regression/test_v060_design_gap.py` | check-gate P7 DESIGN_GAP frontmatter 配对 |
| `regression/v060-p8-cached.bats` | 3 | `regression/test_v060_p8_cached.py` | check-gate P8 cached（version/CHANGELOG） |
| `regression/v060-p8-internal-only.bats` | 3 | `regression/test_v060_p8_internal_only.py` | check-gate P8 internal_only |
| `regression/v060-r4-cached.bats` | 2 | `regression/test_v060_r4_cached.py` | check-pruning P7 源码文件数 |
| `regression/v060-yaml-indent.bats` | 3 | `regression/test_v060_yaml_indent.py` | task-files.md executor_env YAML 缩进 |

### 批次 12 — hook 消息/推送/安装链（4 文件 / 20 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/commit-msg-self-gate.bats` | 4 | `unit/test_commit_msg_self_gate.py` | 正则消息文本（self-gate-review/skip）；**1 处 `[ -z "$output" ]` 合并流** |
| `integration/commit-msg-self-gate.bats` | 6 | `integration/test_commit_msg_self_gate_integration.py` | git hook 真环境（subprocess 调 bash 薄壳） |
| `integration/pre-push-hook.bats` | 4 | `integration/test_pre_push_hook.py` | git hook；1 处平台关键词（windows_smoke） |
| `unit/install-hook.bats` | 6 | `unit/test_install_hook.py` | git_repo + .gitignore + **ln -sf 软链/Windows 复制模式分支断言**（2 处平台关键词，windows_smoke） |

### 批次 13 — pre-commit hook 专项（2 文件 / 56 @test，依赖批次 8）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `integration/pre-commit-hook.bats` | 48 | `integration/test_pre_commit_hook.py` | hook 薄壳 subprocess 调 bash + git_repo + dispatch-context hash + P6 代码直改拦截 + IT_PT_BINARY/MENTION/T6/PHASE_SPAN/RETREAT/CHANGELOG/P6_CODE；1 处平台关键词（windows_smoke） |
| `integration/dispatch-context-card.bats` | 8 | `integration/test_dispatch_context_card.py` | dispatch-context 卡片 hash（task_dir + git） |
| 子批 | — | 13a binary/mention/t6(~12) → 13b phase_span/retreat/changelog/p6_code(~18) → 13c dispatch/card(~26) | 每子批独立 `-k`（§6） |

### 批次 14 — 一致性/self-gate 集成（2 文件 / 19 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `integration/consistency.bats` | 11 | `integration/test_consistency.py` | 跑一致性脚本 + 锚点表；1 处平台关键词（windows_smoke） |
| `integration/protocol-alignment-review.bats` | 8 | `integration/test_protocol_alignment_review.py` | SELF-GATE 对齐（读协议文件） |

### 批次 15 — 文档/CI 断言（1 文件 / 9 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `unit/env-adapt-docs.bats` | 9 | `unit/test_env_adapt_docs.py` | **断言目标随 pytest 化更新（非新增断言，目标迁移）**：bdd-32「bats 可解析」→「pytest 可收集（--collect-only 全绿）」；bdd-34 shellcheck 3 薄壳 + ruff `agate/`（含 tests）；bdd-33 windows-latest matrix 保留；bdd-16/23/24/25/26/27 不变；3 处平台关键词（windows_smoke） |
| 联动 | — | 本批实施时同步表 E 文档重写（AGENTS.md / tests/README.md / SETUP / platform-notes / scripts/README / handoff-template / protocol-alignment-review / UPGRADING 新章节） | — |

### 批次 16 — 扫描器行为（1 文件 / 16 @test）

| bats | @test | pytest 文件 | 回归点 |
|------|-------|-------------|--------|
| `tests/scripts/check-platform-assumptions.bats` | 16 | `tests/scripts/test_check_platform_assumptions.py` | **make_fixture/assert_hit 模式迁移（tmp_path）**：R1-R5 规则可检出正例（fixture 运行时 fragment 拼接避免源码字面命中）+ "干净树"契约（迁移终态 .bats 退役后全树 0 命中）+ **4 处 `[ -z "$output" ]` → 合并流 `.output`** + 3 处平台关键词（windows_smoke） |

### 批次 17 — Windows 冒烟机制退役批（0 文件 / 0 @test，退役）

| 对象 | @test | 处理 | 回归点 |
|------|-------|------|--------|
| `tests/scripts/check-windows-smoke.sh` | — | **退役删除** | 冒烟由 `@pytest.mark.windows_smoke` marker 承接（§5 表 W） |
| `tests/scripts/check-windows-smoke.bats` | 7 | **退役不迁移** | WSMOKE.1-7 测的是被退役脚本自身的代表选取行为，脚本消失故用例不迁移（P1 §6.2 决策，不属"覆盖减少"） |

**覆盖自检**：批次 0-16 合计 60 文件 / 749 @test（19+11+39+53+37+42+69+57+146+79+60+17+20+56+19+9+16 =
749，与 P1/P2 一致）；批次 17 退役 7 用例不计。pytest 文件数 = **60 个 test_*.py**（46 unit + 6 regression +
6 integration + 1 test_sanity.py + 1 scripts/test_check_platform_assumptions.py）+ 1 个 conftest.py。

---

## 5. pytest 结构设计

### 5.1 conftest.py fixture 清单（批次 0 交付，替代 helpers/ 三文件）

> 所有文本 I/O 显式 `encoding="utf-8"`（BDD-7）；fixture 内容运行时构造，不写字面命中行（BDD-5/8）。
> 迁移源映射见 P2 §3.1 / §6.1。

| fixture / helper | 作用域 | 迁移源 | 语义等价 |
|------------------|--------|--------|----------|
| `agate_root` | session | load.bash `_resolve_agate_root`（反推：从 tests/ 上溯找最近含 `scripts/`+`assets/` 目录；`AGATE_ROOT` env 覆盖优先；解析失败 `pytest.fail` fail-closed） | AGATE_ROOT 解析 |
| `agate_scripts` / `agate_assets` | session | load.bash 常量 | `$AGATE_SCRIPTS` / `$AGATE_ASSETS` |
| `python_exe` | session | fixtures.bash detect_python / probe_python（`shutil.which("python3")` → `"python"` 回退，无则 fail-closed） | `$PYTHON`（**create_python_shim_bin 退役**） |
| `task_dir` | function | fixtures.bash create_task_dir | tmp_path 下写 P0-P8 文件 + `.state.yaml`（`no_state_yaml` 跳过）+ `agent: test` frontmatter + Given 行；参数 `phases` / `risk_level` / `with_evidence` / `legacy_fields` |
| `git_repo` | function | git-helper.bash git_init + git_commit/stage/staged_diff/staged_files | tmp_path 下 git init + user.email/user.name/commit.gpgsign false；方法 `.commit/.stage/.staged_diff/.staged_files` |
| `run_cli` | function | bats `run` + `$status`/`$output`/`$stderr` | `subprocess.run([...], capture_output=True, text=True, encoding="utf-8")` → `CommandResult(returncode, stdout, stderr)`；参数 `cwd=` / `input=` / `env=` |
| `py_path` | function | fixtures.bash py_path | Windows cygpath -m 转换；Linux 恒等返回 |
| 纯函数（`from conftest import ...`） | — | fixtures.bash add_* / git-helper | `add_agent_field` / `add_frontmatter_field` / `add_p1_field` / `add_p2_candidate_count` / `add_pruning_excuse` / `add_evidence_file` / `add_p6_pass` / `add_p6_fail` / `add_p6_need_confirm` / `add_p1_bdd` / `add_p2_review` / `add_given_line` |
| `load_fixture(name)` | — | fixtures.bash 静态夹具 cp | `agate_root / "tests" / "fixtures" / name` 绝对路径（full-task / ui-affected / vision-blocked / high-risk / paused-task） |
| **`CommandResult.output`** | — | P2 §3.1（BLOCKER-1） | **property = `self.stdout + self.stderr` 合并流**，等价 bats `$output`；单流归属才用 `.stdout`/`.stderr` |

**流语义断言规则**（迁移逐断言强制对照，P2 §3.2）：
- 空/非空断言（`[ -z "$output" ]` 26 处）→ `assert result.output == ""` / `!= ""`（合并流，勿映射 `.stdout`）
- stderr 特定内容（`GATE ...:` / `ENV_BASELINE:` / `TDD_CHECK:` 错误 / 用法）→ 先判流归属：确定 stderr → `.stderr`，确定 stdout → `.stdout`，不确定 → `.output`
- `2>&1` 显式合并（ci-gate-backstop 模式）→ 直接 `.output`
- 精确等值 → 统一 `.strip()` / `.rstrip("\n")`（`$(...)` 剥尾部换行 vs subprocess 保留）

### 5.2 marker（windows_smoke）

- **定义**：`@pytest.mark.windows_smoke`，pyproject.toml `[tool.pytest.ini_options]` 注册
  `markers = ["windows_smoke: Windows CI smoke representative"]`（消除 PytestUnknownMarkWarning，P2 §4.4 已实测）。
- **打标清单来源**：现 `check-windows-smoke.sh:32` `PLATFORM_KEYWORDS_RE`
  （`cp1252|CRLF|Windows|win32|symlink|MSYS|py_path|PYTHONIOENCODING|盘符|编码|绝对 bash|复制模式|platform|平台|无bc|无 python3|shim|subprocess|ln 退化|ln 复制`）+ **每文件第 1 个 @test**。
- **实测平台关键词用例分布**（迁移时逐文件对照打标，22 处，不含 check-windows-smoke.bats 自身）：

| 文件 | 平台关键词用例数 |
|------|-----------------|
| `unit/agate-workspace-resolve.bats`（bdd-18 CRLF） | 1 |
| `unit/agate-extract-context.bats` | 1 |
| `unit/agate-next-card.bats` | 2 |
| `unit/check-gate.bats` | 1 |
| `unit/ci-gate-backstop.bats` | 4 |
| `unit/env-adapt-docs.bats` | 3 |
| `unit/helpers-python.bats`（bdd-15/17 无 python3） | 1 |
| `unit/install-hook.bats`（ln 复制模式） | 2 |
| `integration/consistency.bats` | 1 |
| `integration/pre-commit-hook.bats` | 1 |
| `integration/pre-push-hook.bats` | 1 |
| `tests/scripts/check-platform-assumptions.bats` | 3 |

- **使用**：Windows CI `python -m pytest agate/tests/ -m windows_smoke`（BDD-4/BDD-12）；Linux 全量不受影响。

### 5.3 run_cli 工具（P2 §3.1 CommandResult 合并流）

- 签名：`run_cli(*args, cwd=None, input=None, env=None)` → `CommandResult`
- 典型调用：`run_cli(python_exe, str(agate_scripts/"agate-json-get.py"), "get", "exit_code", "1", input='{"exit_code":2}')`（等价 bats `echo '...' | $PYTHON ...`）
- hook/薄壳测试：`run_cli("bash", "-c", "cd '$repo' && AGATE_ROOT='$fake' bash '$fake/scripts/pre-commit-gate.sh'", cwd=...)`（subprocess 调 bash 薄壳，断言其真环境行为，BDD-11）
- `.output` 为合并流 property；`.returncode` 等价 `$status`。

---

## 6. 每批验证命令（17 批）

> 通用口径（BDD-6 双跑对照 + P2 §4.1 gate_commands）：**pytest 新文件全绿 + 原 .bats 该批全绿 +
> consistency 0 ERROR**。`-k` 关键字按 §2 命名约定契约匹配 module 名；专项批按 function 前缀。
> P4 每批实现后必须能跑通本表验证命令，跑不通 = 命名违约（P2 §3.3）。P5 全量 = `python3 -m pytest agate/tests/ -q --tb=no`。

| 批次 | 内容 | pytest 验证命令 | 原 .bats 对照 |
|------|------|----------------|--------------|
| 0 | 基座 | `python3 -m pytest agate/tests/ -k "sanity or helpers or workspace"` | `bats agate/tests/sanity.bats agate/tests/unit/agate-workspace-resolve.bats agate/tests/unit/helpers-python.bats` |
| 1 | 纯工具 | `python3 -m pytest agate/tests/unit/ -k "changelog or card or evidence or gate_missing or gate_p5"` | 原 5 bats |
| 2 | 共享工具 | `python3 -m pytest agate/tests/unit/ -k "json or md_field or state_get or retreat_state or state_yaml or read_p5"` | 原 6 bats |
| 3 | 内容生成 | `python3 -m pytest agate/tests/unit/ -k "next_card or inject_card or render_dispatch"` | 原 3 bats |
| 4 | 上下文/归档/回退 | `python3 -m pytest agate/tests/unit/ -k "extract or archive or migrate or retreat"` | 原 4 bats |
| 5 | 环境/债务/编码 | `python3 -m pytest agate/tests/unit/ -k "capture_env or debt or image or encoding"` | 原 4 bats |
| 6 | 状态/裁剪/scope | `python3 -m pytest agate/tests/unit/ -k "state_transition or pruning or scope"`（子批 6a/6b/6c 各 `-k "state_transition"` / `-k "pruning"` / `-k "scope"`） | 原 3 bats |
| 7 | check 基础 gate | `python3 -m pytest agate/tests/unit/ -k "changelog or frontmatter or state_yaml or retrospective or p6_format"` | 原 5 bats |
| 8 | check-gate 专项 | 整文件 `python3 -m pytest agate/tests/unit/ -k "gate"`；子批 8a-8h 按 §4 子批表 `-k`（如 `-k "g0 or g1 or g3 or g4 or other"` … `-k "drift or tag0005"`），每子批跑通后再整文件 | 原 3 bats（bats -f 子集或整文件） |
| 9 | P6 链 + vision | `python3 -m pytest agate/tests/unit/ -k "p6 or vision or backstop"`（子批 9a/9b/9c 各 `-k "p6_evidence"` / `-k "p6_provenance"` / `-k "vision_blocker or backstop"`） | 原 4 bats |
| 10 | TDD 红灯链 | `python3 -m pytest agate/tests/unit/ -k "tdd or formatter or dispatch or consistency"`（子批 10a `-k "tdd"` / 10b `-k "formatter or dispatch or consistency"`） | 原 4 bats |
| 11 | 回归套件 | `python3 -m pytest agate/tests/regression/` | `bats agate/tests/regression/` |
| 12 | hook 消息/推送/安装 | `python3 -m pytest agate/tests/ -k "commit_msg or pre_push or install_hook"` | 原 4 bats |
| 13 | pre-commit 专项 | 整文件 `python3 -m pytest agate/tests/integration/test_pre_commit_hook.py agate/tests/integration/test_dispatch_context_card.py`；子批 13a `-k "binary or mention or t6"` / 13b `-k "phase_span or retreat or changelog or p6_code"` / 13c `-k "dispatch or card"` | 原 2 bats |
| 14 | 一致性集成 | `python3 -m pytest agate/tests/integration/ -k "consistency or alignment"` | 原 2 bats |
| 15 | 文档/CI 断言 | `python3 -m pytest agate/tests/unit/test_env_adapt_docs.py` | 原 bats |
| 16 | 扫描器行为 | `python3 -m pytest agate/tests/scripts/test_check_platform_assumptions.py` | 原 bats |
| 17 | 退役批 | 无 pytest 命令；`python3 agate/scripts/check-protocol-consistency.py --strict` + `grep` tests/ 下无 `check-windows-smoke.sh` | — |

**全量回归**（P5/P6 兜底）：`python3 -m pytest agate/tests/ -q --tb=no`（exit 0 + `--collect-only ≥ 749`）。
**consistency / ruff / scan**（每批联检）：`python3 agate/scripts/check-protocol-consistency.py --strict` /
`ruff check agate/` / `python3 agate/scripts/check-platform-assumptions.py`（P2 §4.1 gate_commands）。

---

## 7. 回归口径审计清单（P6 对照用）

- [ ] 60 个 .bats → 60 个 test_*.py，逐文件 1:1（§4 覆盖映射表可逐行核对）
- [ ] 每条 `bdd-N` @test → `test_bdd_N_...` 函数名保留编号（P6 逐条 BDD 对照）
- [ ] 26 处 `[ -z "$output" ]` → 合并流 `.output` 断言（批次 1/2/5/7/12/16 分布）
- [ ] 流语义回归锁正例（批次 1：stderr 输出 + `.output` 合并流命中）已写入
- [ ] windows_smoke marker 打标（§5.2 表 W 22 处 + 每文件第 1 用例）
- [ ] Pillow 可选：agate-image-check / check-p6-evidence 用 skipif，收集数不降（BDD-1 ≥749）
- [ ] 迁移期双跑对照（每批验证命令含原 bats）直至 bats 退役
