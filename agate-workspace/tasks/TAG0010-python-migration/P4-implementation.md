---
phase: P4
task_id: TAG0010-python-migration
type: implementation
parent: P3-test-cases.md
trace_id: TAG0010-P4-20260814
status: draft
agent: implementer
---

# P4 实现记录 — 批次 0（公共库）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 agate/scripts/agate_common.py

按 P2 §3.1 模块设计实现，替代 `gate-result.sh` + `agate-workspace-resolve.sh` 的函数库：

- **数据流函数（gate-result.sh 迁移）**：
  - `write_gate_result(phase, task_id, exit_code, output)`：写 `.gate-result.json`（结构不变）+ 追加 `.gate-history.jsonl`；`output` 用 `json.dumps` 转义（替代 agate-json-get.py escape）；`prev_commit_sha` 用 `git rev-parse HEAD`（失败回退 "pre-commit"）
  - `read_state_phase(state_file)` / `read_state_task_id(state_file)`：yaml.safe_load 读 frontmatter，文件不存在返回 `""`
  - `has_staged_phase_change(state_file)`：`git diff --cached --name-only` + `line.rstrip("\r")` + `^\+.*phase:` 检查
  - `has_staged_phase_output()`：staged 文件名匹配 `P[0-9]+-.*\.(md|yaml)$`
  - `resolve_formatter(fmt, task_dir=None, agate_root=None)`：绝对路径 → `task_dir/.agate/formatters/` → `agate_root/assets/formatters/`
  - `run_test_with_formatter(cmd, fmt_path, timeout_secs=None)`：subprocess 超时 + JSON 结构（含 raw_output），保留 exit 124 语义
- **工作区解析（agate-workspace-resolve.sh 迁移）**：
  - `resolve_workspace(project_root)`：`.agate.env` → env `AGATE_TASKS_DIR` → 默认 `{root}/agate-workspace`；`Path.resolve()` 归一；utf-8 + CRLF 剥离
  - 执行模式 main：`AGATE_WORKSPACE=`/`AGATE_TASKS_DIR=` 两行输出（bats 直调契约）
- **hook 公共工具**：
  - `resolve_agate_root(script_path)`：readlink 解析 + 复制模式 `.agate-root` 恢复
  - `probe_python()`：python3 → python（shutil.which）
  - `run_git(args, cwd=None)`：subprocess 封装，utf-8 + errors=replace，返回 (returncode, stdout)

### 修改 agate/scripts/ci-gate-backstop.py

- `resolve_tasks_dir` 改调 `agate_common.resolve_workspace`（消除对 agate-workspace-resolve.sh 的 bash subprocess）；`ImportError` 时退回 env/default（旧 AGATE_ROOT 向后兼容，同原 fallback 语义）
- `_find_bash`/`_bash_cmd` **保留不动**（批次 2 随各被调脚本 py 化才删）；`run_gate` 的 check-gate.sh → check-gate.py 切换**不做**（批次 2）

### 修改 3 个 bats 文件

- `unit/agate-workspace-resolve.bats`：10 处调用 `bash agate-workspace-resolve.sh` → `"$PYTHON" agate_common.py`；两行输出契约与 CRLF 剥离（bdd-18）断言保留
- `unit/helpers-python.bats`：bdd-17 重构为 `agate_common.probe_python` 语义（python3→python 回退 + 无 python 返回空 → fail-closed 阻断）；bdd-13/15 断言保留
- `unit/ci-gate-backstop.bats`：workspace 解析相关断言改后绿（调用方式本就为 py，断言体不变；本批次确认改后绿）

## 自查结果（自查 ≠ P5 gate）

- `bats unit/agate-workspace-resolve.bats`：10/10 绿
- `bats unit/helpers-python.bats`：3/3 绿
- `bats unit/ci-gate-backstop.bats`：11/11 绿
- 全量 `bats agate/tests/unit/`：625/625 绿
- `count-tests.sh`：727 不漂移
- `check-protocol-consistency.py`：0 ERROR
- `agate-scripts-encoding.bats` bdd-5：新 py 全部显式 encoding=utf-8 通过
- `py_compile`：agate_common.py / ci-gate-backstop.py 均编译通过

## 边界与实现说明

- `write_gate_result` 的 JSON 字段结构完整复刻 gate-result.sh（phase/task_id/exit_code/timestamp/output/runner/prev_commit_sha），history 行字段同 sh（phase/task_id/exit_code/timestamp/prev_commit_sha）
- `run_test_with_formatter`：用 subprocess `timeout` 参数替代 GNU timeout 二进制探测（行为等价：保留 exit 124 超时语义）；stdout/stderr 合并（stderr=STDOUT）；formatter 用 `bash <fmt_path> <exit_code>` 子进程调用（formatters 仍为 sh，非本批次迁移对象）
- `resolve_workspace` 不创建任何目录（同 agate-workspace-resolve.sh 边界）
- pyyaml fail-closed：模块顶部 try/except ImportError → stderr 提示 + exit 1（同 agate-state-get.py L18-21 模式）
- Python 3.8+ 兼容：无 match / str.removeprefix；全部文件读写显式 `encoding="utf-8"`

## DESIGN_GAP

[DESIGN_GAP: P2 §3.1 写 "gate-result.json（6 字段结构不变）"，但 gate-result.sh 实际写 7 字段（phase/task_id/exit_code/timestamp/output/runner/prev_commit_sha）。实现按 sh 实际结构保留 7 字段（CLI 契约"结构不变"的判定对象是 sh 现状，ci-gate-backstop 读 phase/exit_code/timestamp/prev_commit_sha 均不受影响），未按"6 字段"裁剪]

## 已知后续（不在本批次）

- `_bash_cmd`/`_find_bash` 于批次 2 随 check-gate.py / check-tdd-red.py / check-p6-provenance.py 落地逐个删除
- 批次 3 薄壳 `resolve_agate_root` / `probe_python` 供 pre-commit-gate.py 等复用
- gate-result.sh / agate-workspace-resolve.sh 的 sh 版本在本批次保留（批次 1-3 各调用方 py 化后才删档）

---

# P4 实现记录 — 批次 1a（check-changelog / check-frontmatter / check-state-yaml / check-scope-resolved py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 4 个 .py（迁移源 .sh 保留，未改动）

| 新建 | 迁移源 | 依赖既有 py（subprocess + sys.executable） |
|------|--------|------------------------------------------|
| `agate/scripts/check-changelog.py` | `check-changelog.sh` | `agate-changelog-unreleased.py`（env CHANGELOG_FILE） |
| `agate/scripts/check-frontmatter.py` | `check-frontmatter.sh` | `agate-frontmatter-check.py`（env FILE） |
| `agate/scripts/check-state-yaml.py` | `check-state-yaml.sh` | `agate-state-yaml-check.py`（env STATE_FILE） |
| `agate/scripts/check-scope-resolved.py` | `check-scope-resolved.sh` | `agate-md-field-get.py scope_resolved`（env FILE） |

- 全部 `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）；pyyaml fail-closed 由依赖 py 自带（无新增 yaml import）
- CLI 契约与 sh 版逐字节等价（exit 0/1/2 语义 + stderr 输出格式，已手动 diff 验证）

### 改动 4 个 bats 文件（调用点 .sh → .py，`@test` 数不变）

- `unit/check-changelog.bats`：8 处 `run bash .../check-changelog.sh` → `run "$PYTHON" .../check-changelog.py`（含 @test 名）
- `unit/check-frontmatter.bats`：CF.10 2 处调用改 py（其余用例本就直调 agate-frontmatter-check.py）
- `unit/check-state-yaml.bats`：9 处调用改 py
- `unit/check-scope-resolved.bats`：10 处调用改 py

### 其他引用核查（确认无需改动）

- `unit/dispatch-context-warning.bats` L31/36/37 的 `cp "$AGATE_ROOT/scripts/check-*.sh"` 是复制到 fake root 供**仍为 sh 的 pre-commit-gate.sh**（批次 3 才 py 化）调用，本批次保持 .sh 复制不变
- `integration/consistency.bats` / `pre-commit-hook.bats`：仅注释/@test 名提到脚本，非调用点；consistency 锚点表路径随批次 4 同步（本批次 .sh 仍存在，锚点不 ERROR）
- `unit/agate-debt-check.bats`：grep 无本批脚本引用

## 自查结果（自查 ≠ P5 gate）

- `bats unit/check-changelog.bats`：8/8 绿
- `bats unit/check-frontmatter.bats`：14/14 绿
- `bats unit/check-state-yaml.bats`：9/9 绿
- `bats unit/check-scope-resolved.bats`：10/10 绿
- `check-protocol-consistency.py`：0 ERROR（全部通过）
- `py_compile`：4 个新 py 均编译通过

## 偏离点

[DESIGN_GAP: 批次 1a 的 bats 自查发现并处理一个 sh→py 语义差异——sh 命令替换 $(...) 会剥掉子进程输出尾部换行，而 Python subprocess capture 不剥。check-scope-resolved.py 的 agate-md-field-get scope_resolved 空结果时 print 仍输出 "\n"，sh 版 $(...) 收尾为空串落到正文回退判定，py 版若直接判非空会误走 frontmatter 分支（SC.4 红）。实现采用 .rstrip("\n") 等价 sh $(...) 语义；check-changelog.py 的 agate-changelog-unreleased 输出同样处理]

> 实现说明（非 DESIGN_GAP）：check-changelog.py 的 post-bump 模式分支（check-changelog.sh L20-24）在本批 4 个 bats 无直接用例覆盖，已手动与 sh 版逐字节对比验证（含"无版本段落" fail 分支 exit 1 + stderr）。

---

# P4 实现记录 — 批次 1b（check-p6-format / agate-archive-stale-outputs / agate-extract-context py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 3 个 .py（迁移源 .sh 保留，未改动）

| 新建 | 迁移源 |
|------|--------|
| `agate/scripts/check-p6-format.py` | `check-p6-format.sh` |
| `agate/scripts/agate-archive-stale-outputs.py` | `agate-archive-stale-outputs.sh` |
| `agate/scripts/agate-extract-context.py` | `agate-extract-context.sh` |

- 全部 `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix，walrus 未用）
- CLI 契约与 sh 版等价：exit code、stdout/stderr 输出格式、归档目录命名（`.archived/{YYYYmmdd-HHMMSS}-{PHASE}`）、breadcrumb 追加语义，均已与 sh 版实测 diff 核对（见偏离点说明 2 项脚本名后缀）
- check-p6-format.py：--check 用 `re.IGNORECASE` 候选 + 严格大写/BDD 编号双正则；--fix 的 6 段 sed 归一化按行等价实现（`(\s|:|：|$)` alternation 保留全角冒号兼容，同 sh M5 修法）；frontmatter 切分语义（首行 `---` + 其后首条 `---` 起始行闭合）逐字节对齐
- agate-archive-stale-outputs.py：`_OUTPUTS` dict 替代 `_outputs_for` case；P6 专属 P6-evidence/ 连带归档；`.retreat-history.md` 追加模式（含 FAIL 摘要 code block 结构）与 sh 逐字节一致
- agate-extract-context.py：grep 管道 → 逐行正则等价；`grep -c ... || echo 0` 的无匹配双行 quirk 原样保留（见偏离点）；`grep -A5 | head -6` 多匹配 `--` 分隔语义复刻；P6 failed 求和用 `re.findall` 累加；P5 implementation_dir 顺序（P4-implementation.md 文件优先 + 目录递归）与 grep -rh 一致

### 改动 3 个 bats 文件（调用点 .sh → .py，`@test` 数不变）

- `unit/check-p6-format.bats`：16 处 `run bash .../check-p6-format.sh` → `run "$PYTHON" .../check-p6-format.py`（含 `env LC_ALL=POSIX LANG=` 两处）；`@test` 名内脚本名同步改 .py（15 个）。F_BDD18.1 的 `check-gate.sh`（批次 2）不动
- `unit/agate-archive-stale-outputs.bats`：setup 的 `ARCHIVE_CMD` 改 .py + 7 处 `run bash "$ARCHIVE_CMD"` → `run "$PYTHON" "$ARCHIVE_CMD"`
- `unit/agate-extract-context.bats`：16 处 `run bash .../agate-extract-context.sh` → `run "$PYTHON" .../agate-extract-context.py`（含 EC.16 的 `env PATH=...` 一处）+ 头部注释改 .py

### 其他引用核查（确认无需改动）

- `unit/check-state-transition.bats` L500：断言的是 check-state-transition.sh（批次 2，未迁移）stderr 中的 `agate-archive-stale-outputs.sh` 字符串，非调用点，sh 版输出不变 → 不改
- `unit/agate-debt-check.bats` L489-490：fixture git commit message 正文提到 `check-p6-format.sh`，非调用点 → 不改
- `regression/v040-dotarchived-exclusion.bats`：仅注释提到 `agate-archive-stale-outputs.sh` → 不改
- `agate/scripts/check-state-transition.sh` L115 / `agate-retreat-to.sh` L18 / `pre-commit-gate.sh` L183：仍引用 .sh（批次 2/3 迁移目标，本批次不动）

## 自查结果（自查 ≠ P5 gate）

- `bats unit/check-p6-format.bats`：16/16 绿
- `bats unit/agate-archive-stale-outputs.bats`：7/7 绿
- `bats unit/agate-extract-context.bats`：16/16 绿
- 3 个 .py `py_compile` 均编译通过；`bats unit/agate-scripts-encoding.bats`（bdd-5 全 py 显式 encoding 扫描）2/2 绿
- 手动 sh vs py 输出 diff：extract-context 各 phase 探针 / archive 归档目录与 breadcrumb / check-p6-format fix 行为均与 sh 版等价（差异仅脚本名后缀）

## 偏离点

[DESIGN_GAP: 新 py 的 usage/错误消息中脚本名后缀改 .sh → .py（如 "用法: agate-extract-context.py PHASE TASK_DIR [--write]"、"未找到 P1-dispatch-context-*.md"）——sh 版消息写的是 .sh 后缀；为与新脚本名一致而改（batch 1a check-changelog.py 同款先例）。bats 只断言 exit code 不断言消息正文，P5 可复验]

[SCOPE+]: `agate/tests/README.md` L35/59/96 仍引用 3 个脚本的 .sh 名（覆盖度表格 + R2.4 已知风险描述）——按派发指引"README 文档引用不擅自改"，留待批次 4 文档引用同步（表 B）处理]

> 实现说明（非 DESIGN_GAP）：agate-extract-context.py 的 `_grep_count` 复刻了 sh `grep -c ... || echo 0` 无匹配时输出双行 "0\n0" 的 quirk（实测 sh 确实输出 `- BDD 条件数: 0\n0`），为保 CLI 契约逐字节等价而保留；P6 空 P5-test-results 时实测 sh 输出 "P5 failed 参考: 0"（无 set -e 中断），py 同样返回 0。

---

# P4 实现记录 — 批次 1c（agate-next-card / agate-render-dispatch-prompt py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 2 个 .py（迁移源 .sh 保留，未改动）

| 新建 | 迁移源 |
|------|--------|
| `agate/scripts/agate-next-card.py` | `agate-next-card.sh` |
| `agate/scripts/agate-render-dispatch-prompt.py` | `agate-render-dispatch-prompt.sh` |

- 全部 `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：exit 0/1/2 语义 + stdout 字节稳定（next-card 用 `Path.read_bytes()` 逐字节透传卡片，sha256 硬保证不破坏）+ stderr 输出格式
- agate-next-card.py：readlink -f + dirname → `os.path.realpath`；Q1 前缀剥离（`_rel_card`，先直接剥离、失败再归一化 `\\`→`/` + 盘符小写）复刻 bash 参数替换语义；`$(...)` 剥尾换行无涉及（输出直接 buffer 透传）
- agate-render-dispatch-prompt.py：sed 管道（范围打印 + 行删除 + 首个 ``` 围栏块抽取）→ `_range`/`_drop`/`_extract_code_block` 正则等价（`/START/,/END/p` 的 END 从 START 后一行开始找的 GNU sed 语义实测复刻）；sed s 替换 → str.replace 字面替换（esc_repl 的 `&|/\\` 转义在字面替换下不再需要）；`$(...)` 剥尾换行 → `.rstrip("\n")`（批次 1a 范式）

### 改动 5 个 bats 文件（调用点 .sh → .py，`@test` 数不变）

- `unit/agate-next-card.bats`：setup `CARD_CMD` 改 .py + 全部调用点 `bash "$CARD_CMD"` → `"$PYTHON" "$CARD_CMD"`；symlink 场景 `ln -sf .../agate-next-card.py` + `"$PYTHON" "$link_dir/card"`；NC_ROOT.2 复制 .py + AGATE_ROOT 覆盖调用；bdd-21/22 的 `bash -c` 内联调用改 py（22 用例不变）
- `unit/agate-render-dispatch-prompt.bats`：18 处 `run bash .../agate-render-dispatch-prompt.sh` → `run "$PYTHON" .../agate-render-dispatch-prompt.py` + RP.16 命令替换、bdd-20 `env AGATE_ROOT` 两处同步改（20 用例不变）
- `unit/agate-inject-card.bats`：L57 `expected_body=$(bash .../agate-next-card.sh P1)` → `"$PYTHON" .../agate-next-card.py`（inject-card.sh 内部仍调 .sh，产出等价，hash 对比保持有效）
- `integration/pre-commit-hook.bats`：L49 卡片嵌入调用 + L1191 `card_content` 生成改 py
- `integration/dispatch-context-card.bats`：L45 卡片嵌入调用改 py

### 其他引用核查（确认无需改动）

- `unit/dispatch-context-warning.bats` L44：`# Do NOT copy agate-next-card.sh` 是注释（模拟 fake root 无该脚本供 pre-commit-gate.sh 降级），非调用点 → 不改
- `unit/agate-migrate-workspace.bats` L152：fixture 卡片正文提到 `agate-next-card.sh`，非调用点 → 不改
- `integration/pre-commit-hook.bats` L28/1253、`integration/dispatch-context-card.bats` L21/97：`generated_by: agate-next-card.sh` 为 fixture 文档头文本，非调用点 → 不改
- `agate/tests/README.md` L32/33：覆盖度表格仍引用 2 个脚本 .sh 名 → 留待批次 4（表 B）文档同步

## 自查结果（自查 ≠ P5 gate）

- `bats unit/agate-next-card.bats`：22/22 绿
- `bats unit/agate-render-dispatch-prompt.bats`：20/20 绿
- 涉及面抽查：`bats unit/agate-scripts-encoding.bats`(2/2) + `unit/dispatch-context-warning.bats` + `unit/agate-inject-card.bats` + `unit/agate-migrate-workspace.bats` + `integration/dispatch-context-card.bats` + `integration/pre-commit-hook.bats` 全绿（合计 121/121）
- 手动 sh vs py 输出 diff：next-card 全 P0-P8 body sha256 一致；render 全 phase × (architect/implementer/review-role/rollback) 与 sh 逐字节一致（唯一差异 = 渲染产物 header 中脚本名 .sh → .py，见偏离点）
- 2 个 .py `py_compile` 均编译通过

## 偏离点

[DESIGN_GAP: 新 py 的渲染产物 header / usage 错误消息中脚本名后缀改 .sh → .py（"用法: agate-render-dispatch-prompt.py ..."、"本文件是 agate-render-dispatch-prompt.py 的渲染产物"、"GATE: agate-next-card.py ..."）——sh 版写 .sh 后缀；为与新脚本名一致而改（batch 1a/1b check-changelog.py / agate-extract-context.py 同款先例）。bats 只断言 exit code 与子串，不断言脚本名，P5 可复验]

[SCOPE+]: `agate/tests/README.md` L32/33 仍引用 2 个脚本的 .sh 名（覆盖度表格）——按派发指引"README 文档引用不擅自改"，留待批次 4 文档引用同步（表 B）处理]

> 实现说明（非 DESIGN_GAP）：agate-render-dispatch-prompt.py 对 sed `s` 替换采用 str.replace 字面替换——esc_repl 在 sh 中只为防止 `&`/`|`/`/`/`\` 被 sed 当替换元字符解释，字面替换下无此问题，行为等价（bdd-20 的 `&` 目录路径实测逐字节一致）。`_range` 的 END 从 START 之后一行开始查找复刻了 GNU sed 实测语义（START 行自身匹配 END 模式时范围仍延伸到下一处 END），P2 §3.2 无额外约束。

# P4 实现记录 — 批次 1e（check-platform-assumptions bats 改造对接 py 扫描器）

## implementation_dir

```
implementation_dir: agate/tests/scripts/check-platform-assumptions.bats
```

## 本批次改动清单

> 本轮只改 bats 测试文件（py 扫描器 `agate/scripts/check-platform-assumptions.py` 已由前一轮完成并提交）。未跑任何 bats（主 Agent 验证）。

### 改造 `scripts/check-platform-assumptions.bats`（14 → 16 用例，只增不减）

1. **调用点 .sh → .py**：6 处 `run bash .../check-platform-assumptions.sh <target>` → `run "$PYTHON" "$AGATE_SCRIPTS/check-platform-assumptions.py" <target>`——其中 assert_hit 函数内 1 处（被 BDD-2/3/4/5/6 与 3 条 scan-exempt 负向复用）+ BDD-8 全树、BDD-9 dirty、BDD-9 clean、目录扫描、scan-exempt-R4 各 1 处。用 fixtures.bash 的 `$PYTHON`（探测 python3|python），不裸写 python3
2. **test_bdd_1 断言改 py 语义**：被测对象文件 `.sh` → `.py`；原"无 `-P` / `--perl-regexp`"（POSIX ERE）改为"纯 re 引擎、无外部命令调用"——新增 `grep -nE 'subprocess|os\.system|os\.popen'` exit 1（py 逐行扫描仅标准库）；`--perl-regexp` 断言保留
3. **test_bdd_9_directory_scan 扩展名过滤断言加 .py**：新增 `dirty.py` fixture（同含 R1 命中文本）→ 断言输出含 `dirty.py`；`dirty.bats` 命中、`ignored.txt` 忽略断言保留
4. **新增 2 条 docstring 豁免用例**（P2 BLOCKER-1）：
   - `test_bdd_9_docstring_exempts_r2_python_sample`：docstring 块（`"""` 三行）内 python3 示例 → exit 0 零命中（docstring 与 # 注释同类豁免）
   - `test_bdd_9_docstring_exemption_does_not_cover_bare_python3`：docstring 块 + 块外一行裸 python3 → exit 1 且输出含 R2
   - ⚠️ 两条 fixture 文本均用 fragment 拼接（`local q='"""'` / `py='python'` / `ver='3'` / `"${py}${ver}"`），测试文件自身任何一行不出现 R1-R5 字面命中（含注释用全角括号规避 R2）
5. **头注释同步**：L2/L3 被测对象标 TAG0010 py 化；用法/扩展名过滤（*.bats/*.bash/*.sh/*.py）与 R2 docstring 豁免、退出码 2（目标不存在）契约描述同步

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- 用 py 扫描器直扫全部 fixture 场景核对断言：docstring 块内 → exit 0 零命中；块外裸 python3 → exit 1 含 R2；干净 fixture（shebang/command -v/env/@test 标题/注释行/BATS_TEST_TMPDIR）→ exit 0；scan-exempt R4 豁免 / R1、R2、R3 不豁免 → 全部符合断言
- 目录扫描直扫验证：dirty.bats + dirty.py 命中 R1、ignored.txt 忽略
- 全树自扫 `check-platform-assumptions.py agate/tests` → exit 0（0 命中），保证 BDD-8 干净树断言成立（py 版扩展名过滤含 *.py 后仍成立）
- 本 bats 文件自身直扫 → 0 命中（保持"干净"约束）
- 结构校验：16 条 @test 定义、花括号配平（bash -n 对 bats `@test "name" {` 语法本就报错，原始文件同样如此，非本次回归；真实验证以主 Agent 的 bats 运行为准）

## 偏离点

[DEVIATION]: 派发指引 test_bdd_1 建议的断言"`grep -n -- 'grep' <py>` → exit 1"与 py 实际内容不符——py 源码 docstring（L6 "不依赖 grep/find 子进程"）与注释（L95 "等价 sh 的 grep 2>/dev/null"）含字面 `grep`，该 grep 会 exit 0。改为断言真实语义"纯 re 引擎、不调用外部命令"（`grep -nE 'subprocess|os\.system|os\.popen'` → exit 1），覆盖并强化了原意图（py 不依赖外部 grep）。`--perl-regexp` 断言保留]

> 实现说明（非 DEVIATION）：docstring 用例的 fixture 用 make_fixture 逐行写入——`"""` 行（`local q='"""'` 变量）直接传参，块内示例行含缩进（`"    ${py}${ver} ..."`），与 py `_docstring_state` 的 `"""` 奇偶次切换语义逐行核对。测试文件自注释用"块内 python3（文档非可执行代码…）"全角括号收尾，规避 R2 正则对 ASCII 空格后续字符的匹配（沿用原文件 L11/L67 同款写法）。

---

# P4 实现记录 — 批次 2a（check-retrospective / agate-inject-card / check-debt py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 3 个 .py（迁移源 .sh 保留，未改动）

| 新建 | 迁移源 | 依赖 |
|------|--------|------|
| `agate/scripts/check-retrospective.py` | `check-retrospective.sh` | `agate-state-get.py retries_over`（sys.executable subprocess + env STATE_FILE） |
| `agate/scripts/agate-inject-card.py` | `agate-inject-card.sh` | `agate-next-card.py PHASE`（sys.executable）+ `agate-card-inject.py`（env DC_FILE / CARD_FILE） |
| `agate/scripts/check-debt.py` | `check-debt.sh` | `agate_common.resolve_workspace` / `agate_common.run_git` + `agate-debt-check.py`（FILE env / --covered-hashes argv） |

- 全部 `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：exit 0/1/2 语义 + stderr 输出格式（GATE RETRO / GATE DEBT / GATE DEBT WARNING / AGATE_CARD 已注入）
- `$(...)` 剥尾换行 → `.rstrip("\n")`（agate-state-get retries_over、agate-next-card 卡片全文、agate-debt-check stdout 均处理）
- check-debt.py 覆盖模式的依赖加载失败：`from agate_common import ...` 的 ImportError → stderr 报「缺少 agate-workspace-resolve.sh…」+ exit 2（保留 sh 版消息，test_bdd_16 断言不变）
- `git log --all --format=%H%x09%s --grep=^retreat:` → `run_git`（2>/dev/null || true 语义由 returncode 判定等价）

### 改动 3 个 bats 文件 + 2 处引用面（调用点 .sh → .py，`@test` 数不变）

- `unit/check-retrospective.bats`：9 处 `run bash .../check-retrospective.sh` → `run "$PYTHON" .../check-retrospective.py` + 5 个 @test 名 + 头部注释（10 用例不变）
- `unit/agate-inject-card.bats`：setup `INJECT_CMD` 改 .py + 13 处 `run bash "$INJECT_CMD"` → `run "$PYTHON" "$INJECT_CMD"`（含无参数 / 缺 TASK_DIR 两处）+ 头部注释（11 用例不变）
- `unit/agate-debt-check.bats`：11 处 `run bash .../check-debt.sh` → `run "$PYTHON" .../check-debt.py`；4 处 `bash -c "cd ... && bash '.../check-debt.sh'"` → `bash -c "cd ... && "$PYTHON" '.../check-debt.py'"`；test_bdd_16 的 `cp` + 调用改 py；@test 名 + 头部注释（21 用例不变）
- `integration/pre-commit-hook.bats` L1261：`bash .../agate-inject-card.sh` → `"$PYTHON" .../agate-inject-card.py`
- `unit/agate-card-inject.bats` L4：注释引用 `agate-inject-card.sh` → `.py`

### 其他引用核查（确认无需改动）

- `unit/dispatch-context-warning.bats` L38：`cp .../check-retrospective.sh` 复制到 fake root 供**仍为 sh 的 pre-commit-gate.sh**（批次 3 才 py 化）调用，保持 .sh 复制不变
- `agate/scripts/pre-commit-gate.sh` L284 / `check-state-transition.sh` L15（注释）等 sh 侧调用点：非本批次范围（批次 3 迁移对象），不改
- `check-protocol-consistency.py` 锚点表（L552 check-retrospective.sh / L670 check-debt.sh）：.sh 仍存在，反向覆盖扫描只扫 `check-*.sh` + pre-commit-gate.sh + ci-gate-backstop.py，不 ERROR → 不改
- `tests/README.md` L42 / `agate/scripts/README.md` / `agate-summary.sh` 等文档与汇总脚本引用：留待批次 4 文档引用同步（表 B）处理

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`：3 个新 py 均编译通过
- 手动功能核对（与 sh 版输出/exit code 对照）：
  - check-retrospective.py：无异常 → exit 0 无输出；P2 retries=3 → exit 0 + 「重试超限（P2=3 (MAX=3)）」；SCOPE+（design 文件）→ 触发；dispatch-prompt 排除 / AGATE_CARD 块内 SCOPE+ → 不触发；override → 触发
  - agate-inject-card.py：注入后 AGATE_CARD 块 sha256 与 agate-next-card.py P1 全文一致；无参数/缺 TASK_DIR/缺 dispatch-context/无占位符 → exit 1；旧格式 dispatch-context.md 兼容注入；多 role 文件全注入
  - check-debt.py：FILE 模式合法条目 → exit 0 无输出；缺 evidence / 非法枚举 → exit 1 + 「GATE DEBT: … 条目格式错误」；文件不存在 → exit 0；--retreat-coverage 无条目 → WARNING（exit 0）/ 有条目 → 无 WARNING；无 retreat 提交 → exit 0 无输出；复制到独立目录缺 agate_common → exit 2 + 「缺少 agate-workspace-resolve.sh」

## 偏离点

[DEVIATION: check-debt.py 覆盖模式依赖加载失败的判定对象从「agate-workspace-resolve.sh 文件缺失」变为「agate_common 不可导入」——agate-workspace-resolve.sh 已被 agate_common.py 取代（批次 0）。失败语义等价（依赖缺失 → exit 2 + 需主 Agent 自判），stderr 消息保留 sh 版原文以维持 test_bdd_16 断言不变]

> 实现说明（非 DEVIATION）：`bash -c "cd ... && "$PYTHON" '.../check-debt.py'"` 的引号形态与原始 `bash '.../check-debt.sh'` 的裸字形态等价——`$PYTHON` 为探测出的解释器绝对路径（无空格），外层 shell 展开后为单个 token，已用真实 git repo 实测 bash -c 字符串可正常执行。

---

# P4 实现记录 — 批次 2b（check-state-transition / agate-retreat-to py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 2 个 .py（迁移源 .sh 保留，未改动）

| 新建 | 迁移源 | 依赖 |
|------|--------|------|
| `agate/scripts/check-state-transition.py` | `check-state-transition.sh` | `agate_common.MAX_RETRY_MAP` / `agate_common.run_git` + `agate-state-get.py`（phase_stdin stdin / phase / retries_over） |
| `agate/scripts/agate-retreat-to.py` | `agate-retreat-to.sh` | `agate_common.MAX_RETRY_MAP` + `agate-state-get.py phase` / `agate-retreat-state.py`（check_retreat / write_retreat）/ `agate-archive-stale-outputs.py`（批次 1b 已 py 化） |

- 全部 `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：exit 0/1 语义 + stderr 输出格式（GATE STATE / GATE RETREAT 消息逐字节一致）
- `$(...)` 剥尾换行 → `.rstrip("\n")`（agate-state-get 各子命令 stdout、agate-retreat-state check_retreat stdout）
- check-state-transition.py：`git show | agate-state-get.py phase_stdin` 管道 → `run_git` + subprocess（input=stdin 传入）；`git diff --cached` 的 `tr -d '\r'` 剥离 → 逐行 `.rstrip("\r")`；`grep -qF "$STATE_BASENAME"` 子串匹配 → `any(basename in line)`；`grep -oE '[0-9]+' || echo "0"` → 正则无匹配回退 0；检查 4 的 `_find_stale` 用 `_STALE_OUTPUTS` dict（与 agate-archive-stale-outputs.py `_OUTPUTS` 保持一致）
- agate-retreat-to.py：`grep -vE '^${TASK_DIR#./}/'` 暂存区外文件过滤 → 去 `./` 前缀后 `startswith(task_dir + "/")`（路径字面前缀判定，等价安全）；`git commit ... || { 报错; exit 1 }` → returncode 判定；归档/状态子进程一律 `sys.executable`

### 修改 `agate/scripts/agate_common.py`

- 新增模块级常量 `MAX_RETRY_MAP = "P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2"`（**单一数据源**，见下）——check-state-transition.py / agate-retreat-to.py 均 `from agate_common import MAX_RETRY_MAP`（`_DEFAULT_MAX_RETRY_MAP` 别名），两脚本仍支持环境变量 `MAX_RETRY_MAP=` 覆盖（同 sh `${MAX_RETRY_MAP:-...}` 语义）

### 改动 3 个 bats 文件（调用点 .sh → .py，`@test` 数不变）

- `unit/check-state-transition.bats`：30 处 `bash '$AGATE_SCRIPTS/check-state-transition.sh'` → `'$PYTHON' '$AGATE_SCRIPTS/check-state-transition.py'`；20 个 @test 名 + 头部注释脚本名改 .py（30 用例不变）
- `unit/agate-retreat-to.bats`：setup `RETREAT_CMD` 改 .py + 5 处 `bash '$RETREAT_CMD'` → `'$PYTHON' '$RETREAT_CMD'` + 头部注释（5 用例不变）
- `integration/pre-commit-hook.bats`：IT_RETREAT.1/2 两处调用 + 2 个 @test 名 + 2 处注释改 .py

### 其他引用核查（确认无需改动）

- `unit/dispatch-context-warning.bats` L32：`cp .../check-state-transition.sh` 复制到 fake root 供**仍为 sh 的 pre-commit-gate.sh**（批次 3 才 py 化）调用，保持 .sh 复制不变
- `unit/agate-debt-check.bats` L433：`grep -q 'DEBT' .../agate-retreat-to.sh` 断言的是迁移源 .sh 内容（.sh 保留，DEBT 提醒文本仍在）→ 不改
- `agate/scripts/pre-commit-gate.sh` L88 / `agate-summary.sh` L46 等 sh 侧调用点：非本批次范围（批次 3/4 迁移对象），不改
- `agate/tests/README.md` L40 覆盖度表格：留待批次 4 文档引用同步（表 B）处理（批次 1b/1c/2a 同款先例）

## MAX_RETRY_MAP 归属说明

按派发指引特殊要点 1，**放 `agate_common.py`（模块级常量，单一数据源）**，两脚本从 agate_common import——避免连字符文件名 import 问题（check-state-transition.py 的 `import check_state_transition` 需下划线映射，不可行）。`check-retrospective.py`（批次 2a）仍有自己的模块级 `MAX_RETRY_MAP` 字面值，未并入 agate_common（非本批次范围，记录供后续统一）。

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`：check-state-transition.py / agate-retreat-to.py / agate_common.py 均编译通过
- 手动功能核对（与 sh 版 exit code / 输出对照）：
  - check-state-transition.py：无暂存 → exit 0；新文件未暂存 → exit 0；回退 P3→P1 → exit 1 +「回退跳变 P3→P1（差 2），强制 PAUSED」；retries[P2]=3 + PAUSED → exit 0；`MAX_RETRY_MAP` env 覆盖 P2 max=1 → exit 1 +「P2=1 (MAX=1)」；回退 P6→P5 产出未归档 → exit 1 + 含「agate-archive-stale-outputs.sh」提示（ST_ARCHIVE.1 断言依赖，消息保留 sh 原文）
  - agate-retreat-to.py：目标 phase 不低于当前 → exit 1 +「不是回退」；目标非法 → exit 1；暂存区外文件 → exit 1 + 文件列表；路径 retry 超限 → exit 1 +「超限」；P6→P4 全流程 → exit 0 + 2 个独立 commit（`retreat: P6 -> P5` / `retreat: P5 -> P4`）+ phase P4 + retries 追加 + P6 归档 +「共 2 步」+ DEBT 提醒

## 偏离点

[DESIGN_GAP: check-state-transition.py 检查 4 的提示消息保留 sh 原文「退回前须先跑：bash agate/scripts/agate-archive-stale-outputs.sh P{old} {task_dir}」——sh 版消息指向 .sh（.sh 保留、仍可跑），且 `unit/check-state-transition.bats` ST_ARCHIVE.1 断言 `[[ "$output" == *"agate-archive-stale-outputs.sh"* ]]`；改为 .py 会破坏 bats 断言。保持 CLI 契约（消息字节不变），后续随文档同步批次（表 B）一并更新]

[SCOPE+]: `unit/check-state-transition.bats` 的 `setup()` python3 shim（TAG0009 BDD-16/17）在 py 版下已无作用（脚本经 `$PYTHON` 直调 + 内部 `sys.executable`，不再裸调 python3）——按最小实现原则保留不动（批次 2a check-retrospective.bats / agate-debt-check.bats 同款先例），记录供后续清理]

> 实现说明（非 DESIGN_GAP）：agate-retreat-to.py 对 `git commit` 失败（含 pre-commit hook 拒绝）在 `if rc != 0` 分支报「已停在 P{old}」并 exit 1——与 sh `|| { ...; exit 1 }` 语义一致；hook 拒绝场景的集成行为由 IT_RETREAT.2（真实 hook 仓库）在主 Agent 侧验证。
