---
phase: P2
task_id: TAG0011-test-migration
type: design
parent: P1-requirements.md
trace_id: TAG0011-P2-20260815
status: draft
created: 2026-08-15
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 9
packages: [agate-tests, agate-test-helpers, agate-test-scripts, agate-protocol-docs, agate-ci]
domains: [backend, cli]
ui_affected: false
---

# P2 方案设计 — agate 测试框架迁移（阶段二，bats → pytest）

> 输入基线：P1-requirements.md（12 BDD + 17 批规划 + 表 A-E，approved）+ P0-brief.md +
> 实测：60 个 .bats / 749 @test（unit 625 + regression 17 + integration 85 + sanity 6 +
> scripts/check-platform-assumptions 16；check-windows-smoke.bats 7 用例随脚本退役）。
> 本设计把 P1 的影响面与批次规划落成可分批执行、可验证、可判定的实现导航。
> **唯一产出**：本文件。不修改代码/测试，不 commit。
> 本版修订：吸收 P2-review BLOCKER-1（§3.2 `$output` 合并流语义修正，bats `$output` = stdout + stderr
> 合并流）+ N1-N5（子批 `-k` 穷举说明、count-tests 显式传参、命令替换/反向断言补行）。

## 0. 核心设计约束（来自 P1，本设计全部遵循）

- **迁移范围**：60 个 .bats / 749 @test 逐批迁移为 pytest 用例（BDD-1 口径 `--collect-only ≥ 749`）；
  `check-windows-smoke.sh` + `check-windows-smoke.bats` **退役**（BDD-12，冒烟由 marker 承接）；
  `count-tests.sh` **改写**为 pytest 收集计数（§6.3 决策）；文档/CI 按表 E 重写。
- **1 @test → 1 test 函数**（可参数化，但不得少于 1 收集项）：保证 `--collect-only` 计数可审计、P6 BDD 对照可追溯。
- **函数名保留 bdd 编号**：`@test "bdd-N ..."` → `def test_bdd_N_...()`；其余 `@test` 名按 `test_<前缀>_<序号>_<slug>` 命名。
- **测试代码自身平台无关 + 编码干净**：迁移产出的 test_*.py 会被 `check-platform-assumptions.py` 全树扫描
  （R1-R5 零命中，BDD-5/BDD-8）与 encoding 守卫扫描（BDD-7）——fixture 内容一律运行时构造，不写字面命中行；
  所有文本 I/O 显式 `encoding="utf-8"`。
- **迁移期双跑对照（BDD-6）**：每批验证 = 新 pytest 全绿 + 原 .bats 该批全绿，直至 bats 整体退役。
- **batch 验证命令的 `-k` 关键字 = 命名约定契约**：`-k` 匹配 module/function 名，命名必须与 P1 批次表一致（见 §3.3）。

---

## 1. 候选方案

> 场景类型：系统架构型迁移（测试框架全树跨语言 + helpers + CI + 文档全链）。四组设计决策点各列候选，
> 全部真实可行、各有维度取舍；P1 已锁定的 DECIDED/SUGGEST（同目录替换、check-windows-smoke 退役、
> count-tests 改写、marker 承接冒烟、ruff src 扩展）对方案 A 是硬约束，候选差异在**目录拓扑**与
> **组织方式**上。

### 1.1 目录结构候选（3 个）

#### 方案 A1（推荐）：同目录 `test_*.py` 替换 `.bats`，保留目录树

`agate-json-get.bats` → `unit/test_agate_json_get.py`；`sanity.bats` → `test_sanity.py`；
`tests/scripts/check-platform-assumptions.bats` → `tests/scripts/test_check_platform_assumptions.py`。
unit/regression/integration/scripts 目录结构**不变**，`.bats` 与 `test_*.py` 迁移期共存，bats 整体退役时删 `.bats`。

- 优点：
  - 与 P1 表 A-D / 批次表一一对应，P4 按表定位零歧义；`-k` 关键字直接匹配 module 名（`agate_json_get` 含 `json`）
  - 迁移期双跑对照（BDD-6）天然成立：新旧文件同目录，按批次跑各自命令即可
  - pytest 根 `conftest.py` 一个点覆盖全部子目录（自动递归生效），无每目录重复加载
  - 文档引用（tests/README.md 覆盖度表、scripts/README.md）的路径映射是最低成本的 `s/\.bats/.py/`
- 风险：迁移期目录含两种后缀文件，`check-platform-assumptions.bats` 的"干净树"断言（BDD-8）扫描全树时
  需容忍过渡态（过渡期存在 .bats 属正常，退役后归零）
- 工作量：0 额外目录迁移成本；每批仅新建 test_*.py + 最终批量删 .bats

#### 方案 A2：独立 `tests_py/` 平行目录

`agate/tests_py/unit/...`、`agate/tests_py/integration/...`，原 tests/ 保持纯 bats。

- 优点：目录语义纯净（tests/ = bats，tests_py/ = pytest），过渡期不混放；pytest `testpaths` 明确
- 缺点：**与 P1 批次表/S表 1:1 对应破碎**（每文件路径多一层前缀，文档引用两棵树）；双跑对照要跨树；
  `conftest.py` 反推 AGATE_ROOT 需多一跳；最终合并多一次搬迁操作
- 结论：过渡期"看起来干净"的收益远小于映射/双跑/最终搬迁的额外复杂度，否决

#### 方案 A3：双轨并行保留到底（新 pytest 全绿后才一次性退役全部 bats）

目录用 A1，但 .bats **不随批次删**，全部迁移完成后一次性删除。

- 优点：bats 兜底期最长，任意时刻可回退跑 bats
- 缺点：迁移后期 .bats 与 .py 长期双份维护（改门禁时两处改）；count-tests.sh 改写前"727"与"749"两套口径
  长期并存易漂移；BDD-1 的"bats 整体退役"被拖到最末，风险点后置
- 结论：A1 的"每批验证后保留该批 .bats 直至任务收尾"已满足 BDD-6 兜底，无需整体拖到最后；否决

### 1.2 fixture 组织候选（2 个）

#### 方案 B1（推荐）：单根 `agate/tests/conftest.py`

所有 fixture + helper 函数集中一个文件（~350 行，与 fixtures.bash 412 行同量级），镜像 load.bash +
fixtures.bash + git-helper.bash 三文件职责：

- 会话级：`agate_root`（AGATE_ROOT 解析，fail-closed）、`agate_scripts`、`python_exe`（python3→python 探测）
- 函数级：`task_dir`（create_task_dir 等价）、`git_repo`（git_init 等价）+ git 封装、`run_cli`（`run`/`$status`/`$output` 等价）、`py_path`、`windows_smoke` 判断
- 纯函数（非 fixture）：`add_frontmatter_field`/`add_p1_bdd`/`add_pruning_excuse`/`add_p2_review`/`add_evidence_file`/`add_p6_pass`/`add_p6_fail` 等——pytest 测试直接 `from conftest import ...`（pytest 自动把 conftest 所在目录加入 sys.path）

- 优点：单点维护，与 bats 三文件"全局 helper"语义一致；pytest 自动递归加载，所有 test_*.py 零样板；
  与 P1 §6.1 映射表一一对应
- 风险：文件偏大 → P4 批次 0 一次性交付，之后各批只增 fixture 时逐次追加（每次 diff 小）；helper 若
  与门禁逻辑耦合需关注 import 顺序

#### 方案 B2：分层 conftest（tests/conftest.py + unit/integration/regression 各自 conftest）

- 优点：各目录可覆写 fixture，作用域更细
- 缺点：AGATE_ROOT/git_repo/run_cli 等公共 fixture 需每层重声明或 import 传播，重复面大；与本任务"批量
  机械迁移"不匹配（分层只对个别特殊需求有价值）；P1 批次表要求"每批独立可验证"，分层反而增加每批样板
- 结论：本任务无需要覆写 fixture 的目录差异（unit/regression/integration 的差异是测试内容而非 fixture 语义），否决

### 1.3 Windows 冒烟 marker 候选（2 个）

#### 方案 C1（推荐，P1 DECIDED）：`@pytest.mark.windows_smoke` 逐用例显式标注

平台敏感用例（PLATFORM_KEYWORDS_RE 关键词对应用例：cp1252/CRLF/Windows/symlink/py_path/复制模式/
shim/PYTHONIOENCODING/编码/无bc/无 python3/ln 退化 等）逐一加 marker；Windows CI 跑
`python -m pytest agate/tests/ -m windows_smoke`；Linux 跑全量不受影响。
pyproject.toml `[tool.pytest.ini_options] markers` 注册避免 PytestUnknownMarkWarning（§4 minimal_validation 已实测）。

- 优点：选取逻辑显式、可审计（marker 即清单）；无正则命名耦合；退役脚本的选取规则天然转化为 P4 迁移
  时的打标清单；Linux CI 无 marker 开销
- 风险：打标遗漏 → P4 迁移时逐文件对照 PLATFORM_KEYWORDS_RE 清单打标 + BDD-4/BDD-12 验收兜底
- 工作量：~每文件 1-3 处装饰器，机械可做

#### 方案 C2：关键词正则自动选取（保留 check-windows-smoke.sh 的"规则即定义"）

pytest conftest 里按函数名正则动态决定是否入选冒烟。

- 优点：无人工打标，规则即定义
- 缺点：**pytest 的 `-m` 选择器只认 marker 不认正则**——自动选取需自定义 plugin（`pytest_collection_modifyitems`
  按名称过滤），多一层自研机制维护面；函数名 slug 化的名称与 bats 原名不完全一致，正则匹配面漂移风险更高
- 结论：与 P1 DECIDED（退役脚本、marker 承接）直接冲突，且自研 plugin 违背"除 pytest 外不引入测试生态依赖"，
  否决

### 1.4 count-tests.sh 候选（2 个）

#### 方案 D1（推荐，P1 §6.3 SUGGEST）：改写为 pytest 收集计数

`tests/scripts/count-tests.sh` 正文改为探测 `python3|python` + `pytest --collect-only -q` 提取收集数
（`grep -oE '[0-9]+ tests? collected'` 取末行），保留"用例数不漂移"守护职责，脚本路径与引用（AGENTS.md /
handoff-template / UPGRADING / tests/README.md）不变。

- 优点：守护职责延续（handoff/AGENTS/UPGRADING 多处引用不产生引用链断裂）；749 口径与 BDD-1 一致，
  迁移期数值单调逼近 749 可视作进度条
- 风险：`--collect-only` 输出格式跨 pytest 版本稳定（实测 9.0.3 输出 `N tests collected in X.XXs`）；
  Windows 无 pytest 时脚本 fail-closed 明确报错（同现脚本缺 bats 语义）
- 工作量：~30 行改写

#### 方案 D2：退役 count-tests.sh

- 缺点：AGENTS.md「开发命令」、handoff-template、tests/README.md、UPGRADING 多处引用断裂，P1 §5 表 E 的
  引用同步面不降反升；"用例数不漂移"守护失去工具支撑（靠人工数）
- 结论：维护面反而更大，否决

### 1.5 权衡与选择理由

| 决策点 | 选择 | 理由（否决候选一句话） |
|--------|------|------------------------|
| 目录结构 | A1 同目录替换 | A2 破碎 1:1 映射 + 双跑/搬迁成本；A3 双份维护拖后退役 |
| fixture 组织 | B1 单根 conftest | B2 分层重复样板，本任务无目录级覆写需求 |
| Windows 冒烟 | C1 显式 marker | C2 需自研 plugin，违 P1 DECIDED + 依赖约束 |
| count-tests | D1 改写收集计数 | D2 断引用链 + 丢守护 |

**方案总纲**：同目录 `test_*.py` 替换 + 单根 `conftest.py` + 显式 `windows_smoke` marker + count-tests 改写。
P4 implementer 按 P1 批次 0-16 逐批推进（批次 17 为退役批，不实现），每批验证 = pytest 新文件全绿 +
原 .bats 对照全绿 + consistency 0 ERROR。

---

## 2. 影响域分析

### 改什么

- `agate/tests/`：60 个 .bats → 60 个 test_*.py（46 unit + 6 regression + 6 integration + test_sanity.py +
  scripts/test_check_platform_assumptions.py）；新增 `agate/tests/conftest.py`；`.bats` 随任务收尾退役删除
- `agate/tests/helpers/`：load.bash + fixtures.bash + git-helper.bash → conftest.py fixture 体系（三文件退役；
  `create_python_shim_bin` 机制退役，P1 §6.1）
- `agate/tests/scripts/count-tests.sh`：改为 pytest 收集计数（脚本路径保留）
- `agate/tests/scripts/check-windows-smoke.sh` + `check-windows-smoke.bats`：**退役删除**（P1 §6.2 DECIDED）
- `pyproject.toml`：新增 `[tool.pytest.ini_options]`（testpaths + markers 注册）；`[tool.ruff] src` 扩展
  `["agate/scripts", "agate/tests"]`
- `.github/workflows/protocol-tests.yml`：bats job → pytest job（Linux 全量 + Windows `-m windows_smoke` 冒烟）；
  ruff job 扫 `agate/`（含 tests）；shellcheck/consistency/gate-backstop 不变
- 协议文档（P1 §5 表 E）：platform-notes / SETUP / UPGRADING / dispatch-protocol / git-integration / AGENTS.md /
  tests/README.md / scripts/README.md / handoff-template / protocol-alignment-review / formatters/README（评估）/
  archived plans 引用指向

### 不改什么（边界）

- **产品脚本零改动**：47 个 `.py`（含 3 个 hook 薄壳）不改任何行为（TAG0010 已完成，本任务只改测试载体）
- **静态夹具**：`tests/fixtures/`（full-task/ui-affected/vision-blocked/high-risk/paused-task）内容与字段语义不变，
  只改加载方式（conftest 相对路径读取）
- **CLI 输出契约**：exit 0/1/2、`GATE ...:` 前缀、`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行、gate-result.json
  结构、sha256 字节稳定性——断言对象不变，只改断言载体
- **hook 链**：pre-commit/pre-push/commit-msg 三个 sh 薄壳保留（TAG0010 已定），hook 测试用 pytest subprocess
  调 bash 薄壳验证其真环境行为
- **扫描器/一致性/backstop 脚本**：check-platform-assumptions.py / check-protocol-consistency.py / ci-gate-backstop.py
  不改（其扩展名过滤已含 .py，TAG0010 完成）
- **formatters**（pytest.sh 等）保持：P3 gate 的 check-tdd-red 仍用 formatter 归一化 pytest 输出（TD 系列测试
  改测 pytest 输出解析，见批次 10）

### 风险点

- 749 条断言机械改写引入语义偏差 → 双跑对照 + bdd 编号函数名 + 迁移映射表（§3.2）
- 测试代码自身触发扫描器 R1-R5 / encoding 守卫 → §3.1 平台无关纪律 + BDD-5/7/8 gate
- 批次 8/13 单文件超大批 subagent 卡死 → §5 子批表 + 逐子批验证命令
- `-k` 关键字与函数命名脱钩 → §3.3 命名约定契约 + 每批验证命令自校验
- count-tests 改写后口径漂移 → D1 提取正则 + BDD-1 `--collect-only ≥ 749` 兜底

---

## 3. 设计方案主体

### 3.1 conftest.py fixture 体系设计（批次 0 交付物）

> 职责：替代 load.bash + fixtures.bash + git-helper.bash。所有文本 I/O 显式 `encoding="utf-8"`。

**会话级 fixture：**
- `agate_root`：AGATE_ROOT 解析（保留 `_resolve_agate_root` 反推逻辑——从 `tests/` 逐级上溯找最近含
  `scripts/` + `assets/` 的目录；`AGATE_ROOT` 环境变量显式覆盖优先）；解析失败 pytest.fail（fail-closed，等价
  load.bash L33-38）
- `agate_scripts` / `agate_assets`：`agate_root / "scripts"` / `"assets"`（等价 load.bash 常量）
- `python_exe`：探测 `python3` → `python`（shutil.which 顺序，等价 detect_python / probe_python 语义；Windows
  原生 python 下直接命中）

**函数级 fixture：**
- `task_dir`：create_task_dir 等价——基于 `tmp_path`，写 P0-P8 文件 + `.state.yaml`（`--no-state-yaml` 跳过）+
  `agent: test` frontmatter + Given 默认行；参数化 `phases` / `risk_level` / `with_evidence` / `no_state_yaml` /
  `legacy_fields`（BDD-9 回退测试用）。**返回 tmp_path 下的真实目录**（等价 `mktemp -d` 语义，pytest 自动清理）
- `git_repo`：git_init 等价——tmp_path 下 `git init -q` + user.email/user.name/commit.gpgsign false 配置；
  提供 `.commit(msg)` / `.stage(path)` / `.staged_diff()` / `.staged_files()` 方法（等价 git_commit/git_stage/
  git_staged_diff/git_staged_files）
- `run_cli`：`run`/`$status`/`$output` 等价——`subprocess.run([...], capture_output=True, text=True,
  encoding="utf-8")`，返回 `CommandResult(returncode, stdout, stderr)`；参数 `cwd=`（等价 bats `cd`）、
  `input=`（等价 stdin 管道）、`env=`；封装对 `python_exe` + `agate_scripts` 脚本的调用（等价
  `"$PYTHON" "$AGATE_SCRIPTS/x.py"`）
  - **`CommandResult.output` = `stdout + stderr` 合并流属性**（bats `$output` 语义，BLOCKER-1 修正）：
    实现为 `property`（返回 `self.stdout + self.stderr`），供 `[ -z "$output" ]` / `[[ "$output" == *"X"* ]]`
    等价断言使用；仅当断言明确只关心单流（如 stderr 内容归属）才用 `.stdout`/`.stderr`（见 §3.2 流语义规则）
- `py_path`：Windows 下 cygpath -m 转换（等价 py_path helper；hook 薄壳测试 subprocess 调 bash 时用）；
  Linux 恒等返回

**纯函数（测试 `from conftest import ...` 引用）：**
- `add_agent_field` / `add_frontmatter_field` / `add_p1_field` / `add_p2_candidate_count` / `add_pruning_excuse` /
  `add_evidence_file` / `add_p6_pass` / `add_p6_fail` / `add_p6_need_confirm` / `add_p1_bdd` / `add_p2_review` /
  `add_given_line`（保留，含 `add_frontmatter_field` 的 frontmatter 块解析/替换逻辑）
- 静态夹具加载 helper：`load_fixture(name)` → 返回 `agate_root / "tests" / "fixtures" / name` 的绝对路径
  （等价 bats `cp "$AGATE_ROOT/tests/fixtures/full-task/..." "$repo/..."`）

**退役机制**：`create_python_shim_bin` 退役——pytest 用 `python_exe` 直接跑解释器，无需 bats 特有的 shim
（P1 §6.1）；hook 薄壳测试断言对象改为"bash 薄壳 exec py 主程序"的真实行为（BDD-11）。

**迁移期过渡约定**：conftest.py 在批次 0 一次性交付核心 fixture；后续批次若发现缺 fixture（如某批需要新的
task_dir 变体），在对应批次追加（P4 implementer 标 `[DESIGN_GAP]` 上报，P7 审查）。

### 3.2 bats 语义 → pytest 映射表（迁移核心，逐断言对照而非硬翻译）

| bats 语义 | pytest 等价物 |
|-----------|---------------|
| `load ../helpers/load.bash` | 根 conftest.py 自动加载（无每文件 load 语句） |
| `run bash -c "..."` / `run "$PYTHON" "$AGATE_SCRIPTS/x.py" ...` | `run_cli(python_exe, str(agate_scripts/"x.py"), ...)` 或 `run_cli("bash", "-c", ...)`（薄壳/hook 测试） |
| `$status -eq N` / `-ne N` | `assert result.returncode == N` |
| `$output`（**stdout + stderr 合并流**，bats 1.x 固定语义，本地实测 `echo out; echo err >&2` → `$output` 含两行） | `result.output`（§3.1 合并流属性）——**凡断言未显式区分流，一律基于合并流** |
| `[[ "$output" == *"X"* ]]` | `assert "X" in result.output`（合并流；脚本 `sys.stderr.write` 的内容如 `GATE ...:` / `ENV_BASELINE:` 同样命中） |
| `[[ "$output" != *"X"* ]]`（反向断言） | `assert "X" not in result.output`（合并流；N5 补行） |
| `[[ "$output" == "X" ]]` / `[ -z "$output" ]` | `assert result.output.strip() == "X"` / `assert result.output == ""`——**空/非空判断必须基于合并流**，映射为 stdout-only 会静默反转语义（BLOCKER-1） |
| `$stderr`（`run --separate-stderr` 独立捕获） | 本仓库 tests 全树无 `$stderr` 引用；需要流归属判定时：内容写 stderr → `assert "X" in result.stderr`，写 stdout → `assert "X" in result.stdout`（见下方流语义规则） |
| `output=$(cmd)` 命令替换直接捕获（不经 `run`） | `result = run_cli(...)` → 断言 `result.output`（合并流；`$(...)` 剥尾部换行而 subprocess 捕获保留，精确比较前统一 `.strip()` / `.rstrip("\n")`；N4 补行） |
| `bash -c "cmd 2>&1 \|\| true"`（ci-gate-backstop.bats 显式合并模式） | `run_cli("bash", "-c", "cmd 2>&1 || true")` → 断言 `result.output`（`2>&1` 在合并流语义下无额外作用，可保留可去掉） |
| stdin 管道（`echo '{}' \| x.py`） | `run_cli(..., input='{"...":...}')` |
| `setup()` 每文件前置 | conftest 函数级 fixture（`task_dir`/`git_repo`）或 `autouse`（需 PATH 前置的批内自管） |
| `BATS_TEST_TMPDIR`（每测试独立目录） | `tmp_path` fixture |
| `mktemp -d "$BATS_TEST_TMPDIR/xxx-XXXXXX"` | `tmp_path / "xxx"`（pytest 每次测试新目录） |
| `git_init` + `git_commit`/`git_stage`/`git_staged_diff`/`git_staged_files` | `git_repo` fixture + 方法 |
| `cd "$repo"` 后执行 | `run_cli(..., cwd=repo)` |
| `$PYTHON`（detect_python） | `python_exe` fixture |
| `py_path` 路径转换 | `py_path` fixture（Linux 恒等 / Windows cygpath -m） |
| `skip` 平台分支 | `pytest.mark.skipif(sys.platform == "win32", ...)`（Linux/Windows 分支断言） |
| `@test "bdd-N ..."` | `def test_bdd_N_...()`（保留编号，P6 对照） |
| `@test "PREFIX.N ..."` | `def test_prefix_N_...()` |
| `run grep -q ...` / `[ "$status" -eq 0 ]`（读文件断言） | `assert "X" in (agate_root / path).read_text(encoding="utf-8")` |
| `create_python_shim_bin` | 退役（pytest 直跑解释器） |
| `bats -c` 收集计数 | `pytest --collect-only -q`（count-tests 改写，§3.5） |

**流语义迁移规则（BLOCKER-1 修正，P4 逐断言强制对照）：**
- **凡断言"输出为空/非空"**（`[ -z "$output" ]` / `[[ -n "$output" ]]`）→ 一律基于**合并流**
  `assert result.output == ""` / `assert result.output != ""`。全树 **26 处** `[ -z "$output" ]`
  分布：批次 1（gate-missing-cmds / evidence-consistency / changelog-unreleased 各 1）、批次 2
  （state-yaml-check 1 + json-get 1 + retreat-state 1 + state-get 2 + read-p5 2，共 7）、批次 5
  （debt-check 5）、批次 7（frontmatter 2 + retrospective 3，共 5）、批次 12（commit-msg-self-gate 1）、
  批次 16（check-platform-assumptions 4）、批次 17 退役（check-windows-smoke 1，不迁移）——映射为
  `result.stdout == ""` 会使"stderr 有内容"的用例**静默通过**，语义与 bats 相反。
- **凡断言 stderr 特定内容**（`GATE ...:` 前缀 / 用法 / WARNING 等，脚本经 `sys.stderr.write` 输出，
  如 RP.17「角色文件不存在」、EB.7「已捕获」、EB.8「本身崩溃」、check-pruning `GATE PRUNING`、
  check-p6-provenance `GATE PROVENANCE`、agate-debt-check `GATE DEBT WARNING`）→ **先判流归属**：
  内容确定写 stderr → `assert "X" in result.stderr`，确定写 stdout → `assert "X" in result.stdout`；
  **不确定时统一用合并流 `.output`**（与 bats `$output` 等价，双跑对照不漂移）。
- **`2>&1` 显式合并**（ci-gate-backstop.bats 模式）→ pytest 侧直接用 `.output`，无需再显式合并。
- **精确等值注意**：`$(...)` 命令替换剥尾部换行，pytest 捕获保留——精确 `==` 比较前统一
  `.strip()` / `.rstrip("\n")`。

**断言对象契约（不变）**：exit 0/1/2、`GATE ...:` 前缀（脚本写 stderr，经 `$output` 合并流断言）、
`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出（stdout，合并流中含）、gate-result.json 结构、
sha256 字节稳定性（BDD-9）。

**平台无关纪律（迁移产出的 test_*.py 必须满足，否则扫描器/守卫拦截）：**
- 不写裸 `python3` 命令字面量（用 `python_exe` fixture）；不做 `/usr/bin`/`/bin` PATH 字面；不写 `[[ -L ]]` 单平台
  断言（symlink 测试按平台分支断言：Linux 断言软链，Windows 断言复制模式 + WARNING）；不用 `/tmp` 字面
  （用 `tmp_path`）；fixture 的假设内容一律运行时 fragment 拼接（复用现 check-platform-assumptions.bats 的
  `make_fixture` 模式，字符串分段拼装避免源码字面命中）
- 所有 `open()`/`read_text()`/`subprocess.run(text=True)` 显式 `encoding="utf-8"`（BDD-7）
- ruff `target-version = "py38"`：禁 `match`/`str.removeprefix` 等 3.9+/3.10+ 语法（BDD-8）

### 3.3 命名约定（`-k` 关键字 = 批次验证命令契约）

module 名：`test_<snake_bats_name>.py`（`agate-json-get.bats` → `test_agate_json_get.py`；
`sanity.bats` → `test_sanity.py`）。function 名：`test_<bdd编号或前缀>_<序号>_<slug>`。**P1 批次验证命令的
`-k` 关键字全部按 module 名匹配**（如 `-k "json"` 命中 `test_agate_json_get`；`-k "next_card or inject_card or
render_dispatch"` 命中对应 module）——P4 每批实现后必须能跑通 P1 表给出的验证命令，跑不通 = 命名违约。
专项批（8/13）的子批 `-k` 按 function 名前缀匹配（§5 子批表）。

### 3.4 Windows 冒烟 marker 方案

- **打标清单**：P4 迁移时逐文件对照 `check-windows-smoke.sh` 的 `PLATFORM_KEYWORDS_RE` 关键词
  （cp1252/CRLF/Windows/symlink/py_path/复制模式/shim/PYTHONIOENCODING/编码/无bc/无 python3/ln 退化 等），
  对应 @test 迁移的函数加 `@pytest.mark.windows_smoke`；每文件第 1 个 @test（代表该文件 setup/helper 加载）
  也打标（保留"每文件至少一个代表"语义）。
- **pyproject.toml 注册**：`[tool.pytest.ini_options] markers = ["windows_smoke: Windows CI smoke representative"]`，
  消除 PytestUnknownMarkWarning（已实测，§4）。
- **CI**：Windows matrix 跑 `python -m pytest agate/tests/ -m windows_smoke`（BDD-4/BDD-12）；
  Linux 跑全量，marker 不参与过滤。
- **验收**：BDD-4（Windows 冒烟全 PASS）+ BDD-12（tests/ 下无 check-windows-smoke.sh + CI 引用 marker）。

### 3.5 count-tests.sh 改写方案

```bash
# tests/scripts/count-tests.sh（正文改写，路径/引用保留）
set -euo pipefail
TESTS_DIR="$(cd "$(dirname "$0")/.." && pwd)"   # agate/tests/ 绝对路径（N3：显式传参，不依赖 cwd/testpaths 相对 rootdir 解析）
PY="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)"
if [ -z "$PY" ]; then
    echo "count-tests: 找不到 python3/python（pytest 未安装则无法计数）" >&2
    exit 1
fi
# 收集数（仅统计 pytest 收集的测试项；单元/回归/集成/sanity/scripts 全树）
count=$("$PY" -m pytest --collect-only -q "$TESTS_DIR" 2>/dev/null | grep -oE '[0-9]+ tests? collected' | tail -1 | grep -oE '[0-9]+' || true)
echo "=== pytest 用例覆盖度自检 ==="
echo "总计：${count:-0} 个 pytest 用例（collect-only）"
echo ""
echo "目标：≥ 749（TAG0011 迁移基线，BDD-1）；迁移期数值单调逼近 749。"
echo "如果此数字与 docs/plans/agate-test-plan-2026-07-01.md 附录 A 的口径不一致"
echo "→ 文档漂移，需要更新（附录 A 已归档，口径以 BDD-1 749 为准）。"
```

### 3.6 CI 同步方案（protocol-tests.yml）

- `bats` job → `pytest` job（保留 ubuntu/windows 双 matrix）：
  - Linux：`pip install pyyaml pytest` + `python3 -m pytest agate/tests/`（全量，移除 bats 安装）
  - Windows：`pip install pyyaml pytest` + `python -m pytest agate/tests/ -m windows_smoke`
    （`PYTHONIOENCODING: utf-8` 保留；删除 check-windows-smoke.sh 调用）
- `ruff` job：`ruff check agate/scripts/` → `ruff check agate/`（含 tests，BDD-3）
- `platform-scan`/`shellcheck`/`consistency`/`gate-backstop`：保持不变（shellcheck 仍扫 3 hook 薄壳；
  扫描器/一致性/backstop 对 pytest 用例无新面）
- 删除 bats 安装步骤（Linux apt bats / Windows git clone bats-core）

### 3.7 文档重写联动（P1 §5 表 E）

按表 E 逐文件在 P4 批次推进中联动（重点批次 15 的 env-adapt-docs + 收尾一致性确认）：
- 命令表述：`bats ...` → `python3 -m pytest ...`；count-tests 描述 → pytest 收集计数；check-windows-smoke 描述
  → "退役，marker 承接"
- UPGRADING 新增**本版本迁移章节**：bats→pytest 破坏性变更逐条列（用户/外部直接跑 bats 的项目受影响）
- tests/README.md：快速开始/覆盖度表/CI 章节/目录结构全量改 .py；R2.4 已知风险（archive flaky）迁移后重评
- formatters/README.md 的 `bats | generic-tap.sh` 行：**保留**（formatters 支持多框架，generic-tap 仍可用）
- archived plans 的 count-tests 漂移提示 → 指向现行 pytest 口径（BDD-1 749）

---

## 4. gate_commands / files_to_read / env_constraints / minimal_validation

### 4.1 gate_commands（P2 固化，P4-P6 不得修改）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/ -q"           # 测试运行器（pytest 收集渐进增长，check-tdd-red 读取）
  P5: "python3 -m pytest agate/tests/ -q --tb=no"   # 紧凑输出模式
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict 2>&1 | tail -20"
  P5_ruff: "ruff check agate/ 2>&1 | tail -20"
  P5_scan: "python3 agate/scripts/check-platform-assumptions.py 2>&1 | tail -20"
  P5_ci: "python3 agate/scripts/ci-gate-backstop.py 2>&1 | tail -20"
```

- P3 用 `-q`（紧凑）供 check-tdd-red 红灯判定；formatter 用既有 `pytest.sh`（P3_formatter 不另声明，check-tdd-red
  按 gate_commands.P3 自动读取 TEST_RUNNER 语义）。**注意**：TDD 红灯在"迁移等价"语境下语义=新写 pytest 用例
  相对既有脚本必须全绿；若红说明测试自身写错（与 bats 契约不符）→ 修测试而非修脚本（P3 test-designer 细化）。
- `ui_affected: false` → 无需 P5_e2e。
- P5 主命令 = pytest 全量；P5_consistency/ruff/scan/ci 为 BDD-2/3/5/验收④辅助 gate。
- **project_module**：`agate`（pytest 项目模块前缀，供 check-tdd-red B 类 import 错误检测）。

### 4.2 files_to_read（实现导航，控制 P4 上下文——只列必须参考的）

```yaml
files_to_read:
  - path: agate/tests/helpers/load.bash
    why: conftest.py 会话级 fixture 迁移源（AGATE_ROOT 反推 / fail-closed / 常量）
  - path: agate/tests/helpers/fixtures.bash
    why: task_dir + 全部 add_* helper 迁移源（create_task_dir 结构/选项语义/frontmatter 写入）
  - path: agate/tests/helpers/git-helper.bash
    why: git_repo fixture 迁移源（git_init/commit/stage/staged_diff/staged_files 语义）
  - path: agate/tests/scripts/check-windows-smoke.sh:32
    why: PLATFORM_KEYWORDS_RE 关键词清单（windows_smoke 打标清单来源，退役前抄录）
  - path: agate/tests/scripts/count-tests.sh
    why: 改写成 pytest 收集计数的迁移源（路径/引用保留，正文替换）
  - path: pyproject.toml
    why: 追加 [tool.pytest.ini_options]（testpaths/markers）+ ruff src 扩展
  - path: .github/workflows/protocol-tests.yml
    why: CI 同步（bats job → pytest job + Windows marker 冒烟 + ruff 扫 agate/）
  - path: agate/tests/unit/agate-json-get.bats
    why: 纯 stdin 工具类的代表迁移样板（run_cli input= 用法）
  - path: agate/tests/unit/check-state-transition.bats
    why: git_repo + cwd + subprocess 调 py 的代表样板（git show HEAD 断言）
  - path: agate/tests/integration/pre-commit-hook.bats:1-70
    why: hook 薄壳 subprocess 调 bash 的代表样板（setup 装 hook/ln -sf/写 dispatch-context）
  - path: agate/tests/scripts/check-platform-assumptions.bats
    why: make_fixture/assert_hit 模式（扫描器行为测试迁移样板 + 干净树契约）
  - path: agate/tests/unit/check-tdd-red.bats
    why: TEST_RUNNER/formatter 语义（TD/TDD/F 系列断言目标随 pytest 输出调整）
  - path: agate/tests/fixtures/full-task/.state.yaml
    why: 静态夹具加载（task_dir 需复刻 .state.yaml 结构契约）
  - path: agate/scripts/check-gate.py:188-710
    why: 批次 8 分阶段子批映射依据（gate_p0..gate_p8 函数边界 = 子批切分线）
```

### 4.3 env_constraints（继承 P0-brief + P1，不弱化）

```yaml
env_constraints:
  debug_env: "本环境 Linux（python3 3.12.3 + pytest 9.0.3 系统级可用；dev venv ~/.venvs/agate-dev/ 需 pip install pytest，network: full；ruff 0.16.3 @ venv）；Windows 用 CI matrix 冒烟 + 静态分析验证"
  python_min: "3.8+（ruff target-version=py38；禁 match/str.removeprefix 等 3.9+/3.10+ 语法，BDD-8）"
  encoding: "所有测试 py 文本读写显式 encoding='utf-8'（BDD-7，encoding 守卫扫描）"
  pytest: "pytest 9.0.3（系统）；pyproject [tool.pytest.ini_options] testpaths/markers 注册"
  pyyaml: "强制依赖（既有 gate 依赖，测试侧间接依赖）"
  isolation_check: "tmp_path 每测试独立目录；worktree 隔离；~/.agate 稳定版禁止改动（测试用 worktree 自身 agate/ 作 AGATE_ROOT）"
  windows: "pytest 原生全平台；windows_smoke marker 冒烟；PYTHONIOENCODING utf-8（CI）；hook 薄壳测试用 Git Bash 的 bash + py_path 转换"
  pillow: "可选依赖（agate-image-check.py 像素/ahash 测试）；缺 Pillow 时 pytest.mark.skipif 跳过（等价现 bats 行为），跳过不影响收集数（BDD-1 ≥749）"
```

### 4.4 minimal_validation（P1 已标 requires_minimal_validation: true，必须产出）

> 在 `/tmp/opencode/p2-mv/` 实测（python3 3.12.3 + pytest 9.0.3）。

```yaml
minimal_validation:
  - assumption: "pytest 收集/选择机制：test_*.py 收集、-k 关键字过滤、-m marker 过滤、--collect-only 计数可用"
    method: "写 3 个最小 test_*.py（含 windows_smoke marker + 无 marker + 普通函数），跑 --collect-only / -k / -m"
    result: "confirmed"
    note: "实测：3 tests collected；`-m windows_smoke` → 1 passed, 2 deselected；`-k 'no_marker or plain'` → 2 passed, 1 deselected；--collect-only 末行 `N tests collected in X.XXs` 可被 count-tests 正则提取"
  - assumption: "windows_smoke 自定义 marker 需在 pyproject 注册，否则 PytestUnknownMarkWarning"
    method: "注册前后各跑一次 -m windows_smoke 对比 warnings"
    result: "confirmed"
    note: "实测：未注册 → PytestUnknownMarkWarning（marker 仍生效但告警）；[tool.pytest.ini_options] markers 注册后 → 无告警，1 passed。pyproject 必须含 markers 注册"
  - assumption: "tmp_path fixture 提供每测试独立目录（等价 BATS_TEST_TMPDIR 语义）"
    method: "测试函数内建子目录写 .state.yaml 后断言存在"
    result: "confirmed"
    note: "实测：tmp_path/'task'/'state.yaml' 写入 + exists() 断言通过，pytest 自动清理"
  - assumption: "AGATE_ROOT 反推逻辑（找最近含 scripts/+assets/ 的目录）在 conftest 可用"
    method: "从 agate/tests/ 上溯执行 _resolve_agate_root 等价逻辑"
    result: "confirmed"
    note: "实测：从 /agate/tests 上溯命中 /agate（含 scripts/+assets/）——conftest 会话级 fixture 用同逻辑解析 worktree 自身 agate/"
  - assumption: "Windows 真机行为（windows_smoke 冒烟在 windows-latest 的实跑）本地 Linux 无法验证"
    method: "标 CI Windows matrix 冒烟验证（BDD-4/BDD-12），本地以 marker 注册 + 打标清单 + CI 配置声明兜底"
    result: "confirmed"
    note: "与 P1 capability_requirements 一致：Windows 真机行为无法本地模拟，靠 CI matrix + BDD 验收"
```

---

## 5. 批次迁移设计（P1 17 批逐批细化；批次粒度 ≤1 轮可完成）

> 批次 0-16 每批通用验证口径（BDD-6）：新 test_*.py 全绿 + 原 .bats 该批全绿 + consistency 0 ERROR。
> 批次 17 为退役批（无迁移）。**P4 串行推进，每批一个 round**。`-k` 关键字均按 §3.3 module 名契约匹配。

### 批次 0 — pytest 基座（前置，无依赖；交付 conftest.py + pyproject）

- 交付：`tests/conftest.py`（§3.1 全量核心 fixture + helper）+ `pyproject.toml` 追加 `[tool.pytest.ini_options]`
  （testpaths=["agate/tests"]、markers=["windows_smoke: ..."]）+ ruff `src` 扩展 `["agate/scripts", "agate/tests"]`
- 迁移：`sanity.bats`(6) → `test_sanity.py`（conftest 体系自检：agate_root/task_dir/git_repo 可 load）+
  `helpers-python.bats`(3) → `test_helpers_python.py`（python_exe 探测语义，无 shim）+
  `agate-workspace-resolve.bats`(10) → `test_agate_workspace_resolve.py`（两行输出契约 + CRLF）
- 验证：`python3 -m pytest agate/tests/ -k "sanity or helpers or workspace"` + `bats agate/tests/sanity.bats
  agate/tests/unit/agate-workspace-resolve.bats agate/tests/unit/helpers-python.bats` + consistency
- **子批**：0a 交付 conftest + pyproject（跑 test_sanity 自检）→ 0b helpers/workspace 迁移

### 批次 1 — 纯工具（无 git，5 文件 / 11 @test）

- `test_agate_changelog_unreleased.py` + `test_agate_card_inject.py` + `test_agate_evidence_consistency.py`
  （fixtures/ 静态夹具） + `test_agate_gate_missing_cmds.py` + `test_agate_gate_p5_count.py`
- **流语义回归锁（BLOCKER-1，评审测试缺口落地）**：本批含 3 处 `[ -z "$output" ]`（gate-missing-cmds /
  evidence-consistency / changelog-unreleased）——按 §3.2 规则迁移为 `assert result.output == ""`；并补 1 条
  "脚本写 stderr + 断言 `$output` 合并流"正例（EB.8 等价物：脚本 stderr 输出 + `assert "X" in
  result.output`）作为合并流语义的回归锁
- 验证：`python3 -m pytest agate/tests/unit/ -k "changelog or card or evidence or gate_missing or gate_p5"` +
  原 5 bats + consistency

### 批次 2 — 共享工具（6 文件 / 39 @test）

- `test_agate_json_get.py`（stdin） + `test_agate_md_field_get.py` + `test_agate_state_get.py` +
  `test_agate_retreat_state.py` + `test_agate_state_yaml_check.py` + `test_agate_read_p5_commands.py`
- 验证：`python3 -m pytest agate/tests/unit/ -k "json or md_field or state_get or retreat_state or state_yaml or read_p5"` + 原 6 bats + consistency

### 批次 3 — 内容生成工具（3 文件 / 53 @test）

- `test_agate_next_card.py`（sha256 字节稳定性 22） + `test_agate_inject_card.py` + `test_agate_render_dispatch_prompt.py`
- 验证：`python3 -m pytest agate/tests/unit/ -k "next_card or inject_card or render_dispatch"` + 原 3 bats + consistency

### 批次 4 — 上下文/归档/回退工具（4 文件 / 37 @test）

- `test_agate_extract_context.py` + `test_agate_archive_stale_outputs.py`（R2.4 flaky 保留，隔离单跑必过）
  + `test_agate_migrate_workspace.py` + `test_agate_retreat_to.py`（依赖 git_repo + hook 集成）
- 验证：`python3 -m pytest agate/tests/unit/ -k "extract or archive or migrate or retreat"` + 原 4 bats + consistency

### 批次 5 — 环境/债务/编码守卫（4 文件 / 42 @test）

- `test_agate_capture_env_baseline.py`（git + gate-result.json） + `test_agate_debt_check.py` +
  `test_agate_image_check.py`（Pillow 可选，`@pytest.mark.skipif(no PIL)`） + `test_agate_scripts_encoding.py`
  （守卫扫 `agate/tests/**/*.py`，**注意：本测试自身也须通过守卫——迁移后的 test_*.py 全数受检**）
- 验证：`python3 -m pytest agate/tests/unit/ -k "capture_env or debt or image or encoding"` + 原 4 bats + consistency

### 批次 6 — check 状态/裁剪/scope（3 文件 / 69 @test）

- `test_check_state_transition.py`（git_repo + cwd 样板） + `test_check_pruning.py` + `test_check_scope_resolved.py`
- 子批（≥60 批细化）：6a state_transition(30) → 6b pruning(29) → 6c scope(10)，每个子批独立 `-k` 验证
- **流语义要点（BLOCKER-1）**：state_transition / pruning 的 gate 失败内容（`GATE STATE` / `GATE PRUNING` /
  `缺 risk_level` / `P2 不可裁剪` / `隐式耦合` 等）由脚本写 **stderr**，bats `$output` 合并流断言——迁移
  一律用 `result.output`（§3.2 流语义规则），勿映射为 `.stdout`
- 验证：`python3 -m pytest agate/tests/unit/ -k "state_transition or pruning or scope"` + 原 3 bats + consistency

### 批次 7 — check 基础 gate（5 文件 / 57 @test）

- `test_check_changelog.py` + `test_check_frontmatter.py` + `test_check_state_yaml.py` +
  `test_check_retrospective.py` + `test_check_p6_format.py`
- 验证：`python3 -m pytest agate/tests/unit/ -k "changelog or frontmatter or state_yaml or retrospective or p6_format"` + 原 5 bats + consistency

### 批次 8 — check-gate 专项（3 文件 / 146 @test，最大批）

- `test_check_gate.py`（check-gate.bats 124）+ `test_check_gate_p1_review.py`（9）+ `test_check_gate_p5_diff.py`（13）
- **子批表（P1-review 非阻塞 1 要求的落地；每子批 ≤32 @test，按 check-gate.py gate_p0..p8 函数边界切分）**：

| 子批 | 覆盖（check-gate.bats @test 前缀） | 约 @test | 验证命令（-k 按 function 前缀） |
|------|-------------------------------------|----------|--------------------------------|
| 8a | G0 / G1 / G3 / G4 / G_OTHER | ~13 | `python3 -m pytest agate/tests/unit/test_check_gate.py -k "g0 or g1 or g3 or g4 or other"` |
| 8b | G2（含 G2.* / G_BDD1.1 / G_BDD9.1 / G_BDD10.1 / G_CMD_EXEC） | ~32 | `... -k "g2 or bdd1 or bdd9 or bdd10 or cmd_exec"` |
| 8c | G5（含 G5.1 / G5_CMD） | ~10 | `... -k "g5"` |
| 8d | G6（含 G6.* / G_BDD16.1 / test_bdd_1..8 系列） | ~20 | `... -k "g6 or bdd16 or bdd_1 or bdd_2 or bdd_3 or bdd_4 or bdd_5 or bdd_6 or bdd_7 or bdd_8"` |
| 8e | G7（含 G7.* / bdd-11 / G_DG_ANCHOR） | ~14 | `... -k "g7 or dg_anchor or bdd_11"` |
| 8f | G8（含 G8.* / R5 关联留批次 11） | ~12 | `... -k "g8"` |
| 8g | G_RETREAT / G_NC_BINARY / G_SUGGEST | ~15 | `... -k "retreat or nc_binary or suggest"` |
| 8h | D-drift / G-drift / TAG0005 BDD | ~10 | `... -k "drift or tag0005"` |

- 每子批完成即跑该子批验证命令 + 对应原 bats 子集（`bats -f` 或整文件）；全部 8 子批完成后跑整文件 + 原 bats + consistency
- 备注：`test_check_gate_p1_review.py`/`test_check_gate_p5_diff.py` 各自独立文件，随 8b/8c 子批同批迁移
- **`-k` 非穷举分区（N1，已吸收）**：8a-8h 的 `-k` 未覆盖 `PG.P2REVIEW` / `bdd-14` / `bdd-28` / `bdd-29`
  前缀（`test_pg_p2review_*` / `test_bdd_14_*` 等）——由"8 子批完成后整文件跑"兜底，P4 勿据此认为子批
  `-k` 已覆盖 124 个 @test 全数；子批 `-k` 是**增量验证而非严格分区**（N2：8b `-k "bdd1"` 会连带命中 8d
  的 `test_bdd_1_*`，重叠无害），按"子批 `-k` 跑通 + 对应原 bats 子集"执行即可

### 批次 9 — P6 验收链 + vision（4 文件 / 79 @test）

- `test_check_p6_evidence.py`（fixtures/ 静态夹具 + Pillow 可选） + `test_check_p6_provenance.py`
  （fixtures/ + git_repo） + `test_agate_vision_blocker.py` + `test_ci_gate_backstop.py`
- 子批：9a evidence(30) → 9b provenance(36) → 9c vision_blocker(2)+backstop(11)
- **流语义要点（BLOCKER-1）**：provenance 断言 `GATE PROVENANCE:...`（stderr 源）；ci-gate-backstop 多处
  `bash -c "... 2>&1 || true"` 显式合并流——均用 `result.output` 合并流（§3.2 流语义规则），backstop 的
  `bash -c "cmd 2>&1 || true"` 包装按 §3.2 映射行原样保留
- 验证：`python3 -m pytest agate/tests/unit/ -k "p6 or vision or backstop"` + 原 4 bats + consistency

### 批次 10 — TDD 红灯链 + 一致性（4 文件 / 60 @test）

- `test_check_tdd_red.py`（43，TEST_RUNNER 语义 + formatter）+ `test_check_tdd_red_formatter.py`（13）+
  `test_dispatch_context_warning.py`（1）+ `test_check_protocol_consistency.py`（3，跑一致性脚本）
- **重点**：TD/TDD/F 系列断言对象从 bats/pytest 双跑改为**pytest 输出解析**（`pytest.sh` formatter 归一只用
  pytest 输出）；mock 用 `TEST_RUNNER` 环境变量指向 fake 脚本（现模式保留）
- **流语义要点（BLOCKER-1）**：check-tdd-red 的 `TDD_CHECK: ...` 结论走 stdout `print`，错误/用法走 stderr——
  断言前先判流归属（stdout 用 `.stdout`，stderr 用 `.stderr`，不确定用合并流 `.output`，§3.2 规则）
- 子批：10a tdd_red(43) → 10b formatter(13)+dispatch_warning(1)+consistency(3)
- 验证：`python3 -m pytest agate/tests/unit/ -k "tdd or formatter or dispatch or consistency"` + 原 4 bats + consistency

### 批次 11 — 回归套件（6 文件 / 17 @test，依赖批次 8）

- 6 个 `test_v0xx_*.py`（v040-dotarchived-exclusion / v060-design-gap / v060-p8-cached / v060-p8-internal-only /
  v060-r4-cached / v060-yaml-indent）
- 验证：`python3 -m pytest agate/tests/regression/` + `bats agate/tests/regression/` + consistency
- 每文件 ≤4 @test，按文件推进即可

### 批次 12 — hook 消息/推送/安装链（4 文件 / 20 @test）

- `test_commit_msg_self_gate.py`（unit，正则消息文本）+ `test_commit_msg_self_gate_integration.py` +
  `test_pre_push_hook.py` + `test_install_hook.py`（git_repo + .gitignore）
- 验证：`python3 -m pytest agate/tests/ -k "commit_msg or pre_push or install_hook"` + 原 4 bats + consistency

### 批次 13 — pre-commit hook 专项（2 文件 / 56 @test，依赖批次 8）

- `test_pre_commit_hook.py`（48）+ `test_dispatch_context_card.py`（8）——subprocess 调 bash 薄壳 + git_repo +
  dispatch-context hash 校验（setup 用 ln -sf 装 hook 等价逻辑）
- **子批表（按 function 前缀）**：

| 子批 | 前缀 | 约 @test | 验证命令 |
|------|------|----------|----------|
| 13a | IT_PT_BINARY / IT_PT_MENTION / IT_PT_T6 | ~12 | `... -k "binary or mention or t6"` |
| 13b | IT_PHASE_SPAN / IT_RETREAT / IT.9 / IT_CHANGELOG / IT_P6_CODE | ~18 | `... -k "phase_span or retreat or changelog or p6_code"` |
| 13c | 其余（card hash 等） | ~26 | `... -k "dispatch or card"` |

- 每子批跑对应 `-k` + 原 bats 对应子集；全批完成后整文件 + consistency

### 批次 14 — 一致性/self-gate 集成（2 文件 / 19 @test）

- `test_consistency.py`（11）+ `test_protocol_alignment_review.py`（8）
- 验证：`python3 -m pytest agate/tests/integration/ -k "consistency or alignment"` + 原 2 bats + consistency

### 批次 15 — 文档/CI 断言（1 文件 / 9 @test，随表 E 文档重写联动）

- `test_env_adapt_docs.py`：断言目标随 pytest 化更新——bdd-32「bats 可解析」→「pytest 可收集
  （--collect-only 全绿）」；bdd-34 shellcheck 3 薄壳 + ruff `agate/`（含 tests）；bdd-33 windows-latest matrix
  保留；bdd-16/26/27/23/24/25 不变
- **联动**：本批实施时同步表 E 文档重写（AGENTS.md / tests/README.md / SETUP.md / platform-notes.md /
  scripts/README.md / handoff-template / protocol-alignment-review / UPGRADING 新章节）
- 验证：`python3 -m pytest agate/tests/unit/test_env_adapt_docs.py` + 原 bats + consistency --strict 0 ERROR

### 批次 16 — 扫描器行为（1 文件 / 16 @test）

- `tests/scripts/test_check_platform_assumptions.py`：make_fixture/assert_hit 模式迁移（tmp_path）；
  "干净树"断言在迁移终态（.bats 退役后）全树 0 命中；R1-R5 正例可检出
- 验证：`python3 -m pytest agate/tests/scripts/test_check_platform_assumptions.py` + 原 bats + consistency

### 批次 17 — Windows 冒烟机制退役批（0 文件 / 0 @test）

- 删除 `check-windows-smoke.sh` + `check-windows-smoke.bats`；windows_smoke marker 打标已在各批完成；
  CI pytest job Windows matrix 引用 `-m windows_smoke`（BDD-12）
- 验证：`python3 agate/scripts/check-protocol-consistency.py --strict` + grep tests/ 下无 check-windows-smoke.sh

### 批次覆盖自检（对齐 P1）

17 批合计 = 60 文件 / 749 @test（批次 17 退役不计）；全部 46 unit + 6 regression + 6 integration + sanity +
scripts 恰好一次。批次 0 → 全部；批次 8 → 批次 11；批次 13 依赖批次 8。

---

## 6. 实现完成的标志（可判定标准）

| 标志 | 判定方式 |
|------|---------|
| 全量 pytest 全绿替代 bats | `python3 -m pytest agate/tests/` exit 0 + `--collect-only ≥ 749`（BDD-1）；tests/ 下无 .bats 残留 |
| consistency 0 ERROR 0 WARNING | `python3 agate/scripts/check-protocol-consistency.py --strict` exit 0（BDD-2） |
| ruff 覆盖全部 py | `ruff check agate/` exit 0（src 含 tests，BDD-3/BDD-8） |
| Windows 冒烟 | CI windows-latest `python -m pytest agate/tests/ -m windows_smoke` 全 PASS（BDD-4） |
| 扫描器覆盖 .py 且测试树干净 | `check-platform-assumptions.py` 对 tests/ 全树 0 命中 + R1-R5 正例可检出（BDD-5） |
| 迁移期双跑对照 | 每批 pytest + 原 bats 双绿，直至 bats 退役（BDD-6） |
| 编码守卫 | encoding 守卫对全部 test_*.py 零违规（BDD-7） |
| CLI 契约不破 | exit 0/1/2、GATE 前缀、两行输出、gate-result.json、sha256 与 bats 时代一致（BDD-9） |
| fixture 行为等价 | sanity/helpers-python 等价物 + 抽查 task_dir/git_repo 用例结构与 bats 时代一致（BDD-10） |
| hook 链等价 | pre-commit/pre-push/commit-msg pytest 等价物行为一致（BDD-11） |
| 冒烟机制落地 | tests/ 无 check-windows-smoke.sh；CI 引用 -m windows_smoke（BDD-12） |
| count-tests 改写 | `bash agate/tests/scripts/count-tests.sh` 输出 ≥ 749 |
| 文档/CI 同步 | 表 E 逐文件核对无 bats 残留引用（除 formatters 多框架表保留行） |

---

## 7. 风险与缓解

### 7.1 subagent 卡死风险（TAG0010 实战教训，本任务最高优先级）

| 风险 | 缓解 |
|------|------|
| 批次 8/13 单文件超大批（146/56 @test）一次性迁移 → 上下文爆炸卡死 | §5 子批表落地（≤32 @test/子批，每子批独立 -k 验证）；P1-review 非阻塞 1 已要求 |
| files_to_read 列太多 → P4 implementer 读爆上下文 | §4.2 精化清单（13 项 + 行号范围），只列迁移必须参照的文件 |
| 批次内多文件并行 → bash 通道竞争 abort | P4 严格单文件串行，每文件一个 round；bash 命令一律 `timeout` 包裹 |
| `-k` 关键字与命名契约不符 → 验证命令跑不通卡轮 | §3.3 命名约定 + 每批验证命令自校验；违反先查命名再查代码 |
| 单批验证命令含大输出 → 主 Agent 误判 | gate_commands.P5 紧凑输出（--tb=no）+ 批验证命令按 P1 表原样 |

### 7.2 回归风险

| 风险 | 缓解 |
|------|------|
| 749 条断言机械改写引入语义偏差 | §3.2 迁移映射表逐断言对照（非硬翻译）+ BDD-6 每批双跑对照 + bdd 编号函数名便于 P6 对照 |
| bats `$output`（stdout+stderr 合并）vs pytest 流分离的语义偏差（BLOCKER-1） | §3.2 合并流 `.output` 映射 + 流语义规则（空/非空走合并流、stderr 内容先判流归属）+ 批次 1 回归锁用例（EB.8 等价物） |
| 测试代码自身触发扫描器 R1-R5 / encoding 守卫 | §3.1 平台无关纪律（fixture 运行时构造/无裸 python3/无 /tmp 字面/encoding=utf-8）+ BDD-5/7/8 gate 每批跑 |
| R2.4 archive flaky 迁移后复发 | 隔离单跑必过语义保留；tests/README.md 已知风险表迁移后重评（表 E） |
| 迁移期 .bats 与 .py 双口径用例数漂移 | count-tests 改写（D1）单调逼近 749 可视化；BDD-1 --collect-only ≥ 749 兜底 |
| windows_smoke 打标遗漏 | P4 逐文件对照 PLATFORM_KEYWORDS_RE 抄录清单打标 + BDD-4/BDD-12 验收 |
| ruff 对既有 18 py 无影响但测试 py 新违规 | pyproject src 扩展后 `ruff check agate/` 每批跑；规则集沿用 TAG0010 定稿（不做新规则） |
| Pillow 缺省时 image 测试 skip 但收集数不受影响 | `skipif` 运行时跳过、收集仍计数（实测确认），BDD-1 ≥749 不破 |
| 文档引用链（count-tests/check-windows-smoke 引用）断裂 | count-tests 改写保留路径（D1）；check-windows-smoke 引用在表 E 文档批统一改 marker 表述 |
| P3 迁移等价 TDD 语义混淆（红=测试写错而非脚本 bug） | P3 test-designer 按 §4.1 语义设计；gate_commands.P3 固定 `pytest -q` 不随语义漂移 |
