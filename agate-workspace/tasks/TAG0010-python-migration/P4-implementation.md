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

---

# P4 实现记录 — 批次 2c（check-pruning / agate-capture-env-baseline py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 2 个 .py（迁移源 .sh 保留，未改动）

| 新建 | 迁移源 | 依赖 |
|------|--------|------|
| `agate/scripts/check-pruning.py` | `check-pruning.sh` | `agate_common.run_git`（try/except 兜底 None）+ `agate-md-field-get.py`（env FILE，sys.executable subprocess） |
| `agate/scripts/agate-capture-env-baseline.py` | `agate-capture-env-baseline.sh` | `agate_common.resolve_formatter / run_test_with_formatter / run_git` + `agate-read-p5-commands.py`（env P2_DESIGN，sys.executable subprocess） |

- 全部 `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：exit 0/1/2 语义 + stderr 输出格式（GATE PRUNING / ENV_BASELINE 消息逐字节一致，已手动 sh vs py 实测 diff 验证）
- `$(...)` 剥尾换行 → `.rstrip("\n")`（agate-md-field-get / agate-read-p5-commands stdout 均处理）
- check-pruning.py：`grep -qw 'P{phase}'` 词匹配 → `phase in phases_declared.split()`；`grep -c '^override:'` → `re.findall(..., MULTILINE)`；`grep -qE` → `re.search(..., MULTILINE)`；P2.9 产出文件 glob → `glob.glob` + `os.path.isfile` + basename；git 路径归一 `realpath -m`/`realpath --relative-to` → `os.path.realpath`/`os.path.relpath`
- agate-capture-env-baseline.py：`sha256sum | cut` → `hashlib.sha256().hexdigest()`；`agate-json-get.py` 6 处取数 → `json.loads` 直接等价（见偏离点）；`cp` → `shutil.copyfile`；`mkdir -p` → `os.makedirs(exist_ok=True)`；缓存文件格式（frontmatter + fail-list code block）与 sh 逐字节一致（差异仅 generated_by 后缀，见偏离点）

### 改动 4 个 bats 文件（调用点 .sh → .py，`@test` 数不变）

- `unit/check-pruning.bats`：29 处调用改 py（`run "$PYTHON" "$AGATE_SCRIPTS/check-pruning.py"`，P2.6a/b 的 `bash -c` 内联改为 `'$PYTHON' '.../check-pruning.py'`）；24 个 @test 名 + 头部注释脚本名改 .py（29 用例不变）
- `regression/v060-p8-internal-only.bats`：3 处调用改 py + 注释脚本名（3 用例不变）
- `regression/v060-r4-cached.bats`：2 处 `bash -c` 内联调用改 py + 注释（2 用例不变）
- `unit/agate-capture-env-baseline.bats`：15 处调用改 py（含 EB.11 的 `env GIT_DIR=...` 形态改 `"$PYTHON"`；EB.4-15 的 `bash -c` 内联改 `'$PYTHON'`）；头部注释 + setup_git_repo_with_p2 内注释（15 用例不变）
- `tests/helpers/git-helper.bash` L3：注释脚本名 `.sh` → `.py`

### 其他引用核查（确认无需改动）

- `unit/dispatch-context-warning.bats` L35：`cp "$AGATE_ROOT/scripts/check-pruning.sh"` 复制到 fake root 供**仍为 sh 的 pre-commit-gate.sh**（批次 3 才 py 化）调用，保持 .sh 复制不变
- `unit/check-gate-p5-diff.bats` L14：`generated_by: agate-capture-env-baseline.sh` 为 make_baseline fixture 手写基线文档头，非调用点 → 不改
- `agate/scripts/pre-commit-gate.sh` L207 / `agate-summary.sh` L46/62 / `agate-summary.py` L28/33：仍引用 .sh（批次 3/4 迁移对象），非本批次范围
- `check-protocol-consistency.py` 锚点表（CHECK8/CHECK9 的 check-pruning.sh 条目）：.sh 仍存在，锚点不 ERROR → 不改（随批次 4 文档引用同步）

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`：check-pruning.py / agate-capture-env-baseline.py 均编译通过
- 手动 sh vs py 输出 diff（多场景实测，stderr + exit code 逐字节一致）：
  - check-pruning.py：缺 risk_level → 8 条错误全量一致；happy path → exit 0；P7 裁剪 + 6 源码文件（真实 git repo）→ 「源码文件数 ≤ 5，实际=6」；P7 + coupling_checklist → exit 0；P8 + internal_only + reason → exit 0；P8 无 internal_only → exit 1；implicit_coupling → exit 1；legacy-fields（--legacy-fields）→ exit 1；YAML 块式 phases（P2.52）→ exit 0；P2.9 产出文件 + 无 override → exit 1；无 P1 文件 → exit 2
  - agate-capture-env-baseline.py：EB.1 幂等 → 无输出 exit 0；EB.2 P2 缺失 → WARNING；EB.3 无 P5 → WARNING；EB.4 捕获写入缓存+任务文件（失败数=3 逐字节一致）；EB.5 缓存复用（commit 未变）；EB.6 commit 变 → 重捕获；EB.7 命令集合变 → 重捕获；EB.8 崩溃 exit 127 → 不写文件；EB.9 计数不一致 → 不写文件；EB.10 多命令合并去重（3 条）；EB.11 非 git 仓库 → WARNING 不写文件；EB.13/EB.15 pytest/vitest formatter fail-list 提取；EB.14 无 formatter → 不写文件
  - 缓存 key 与 sh `printf '%s\n%s' | sha256sum | cut -d' ' -f1` 逐字节一致（实测同一 commit+P5_DATA 下 sh/py 输出同 hex）

## 偏离点

[DEVIATION: agate-capture-env-baseline.py 不再 subprocess 调 `agate-json-get.py`（sh 版 6 处 `echo "$P5_DATA" | python3 agate-json-get.py ...`），改为 `json.loads` 直接等价取数（exit_code / failed_tests / failed / errors / commands 长度）——agate-json-get.py 本身就是 JSON 提取工具，py 版已是 Python 无需再经子进程；行为等价（已实测），属实现层面等价替换]

[DEVIATION: agate-capture-env-baseline.py 的缓存文件 `generated_by:` 字段写 `.py` 后缀（sh 版写 `agate-capture-env-baseline.sh`）——与新脚本名一致（batch 1a/1b/1c/2a/2b 同款先例）；`check-gate.sh` P5 diff 只读 `captured_at_commit:`，不消费该字段；bats 无断言依赖 → 不改 fixture]

> 实现说明（非 DEVIATION）：check-pruning.py 的 `phases` 词匹配用 `phases_declared.split()` 集合成员判定（等价 sh `grep -qw`）——md-field-get 输出的 phases 是空格连接列表，`-w` 整词语义与 split 一致；`source_count` 的正则 `re.search` 逐行判定等价 sh `grep -cvE`（含 TASKS_BASE_REL 空串时 `^/` 模式与 sh 逐字节一致）。

---

# P4 实现记录 — 批次 2d（check-p6-evidence py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 `agate/scripts/check-p6-evidence.py`（迁移源 .sh 保留，未改动）

| 新建 | 迁移源 | 依赖 |
|------|--------|------|
| `agate/scripts/check-p6-evidence.py` | `check-p6-evidence.sh` | `agate-md-field-get.py`（env FILE，sys.executable subprocess）+ `agate-image-check.py`（env IMG_PATH / env SCREENSHOTS_DIR，sys.executable subprocess） |

- `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：exit 0/1/2 语义 + stderr 输出格式（GATE P6-EVIDENCE / WARNING 前缀逐字节一致，已 15 个场景手动 sh vs py diff 验证）
- `$(...)` 剥尾换行 → `.rstrip("\n")`（agate-md-field-get / agate-image-check stdout 均处理）
- grep → re / pathlib：`grep -cE '^\s*- (PASS|FAIL)'` → `re.findall(MULTILINE)` 计数；`grep -E '^\s*- PASS\b'` 逐行 + S2 结构判定正则（`\([^()]*[^()\s]\.[a-zA-Z0-9]+[^)]*\)`，等价 sh `[^()[:space:]]`）→ `re.findall` + `ref_re.search`
- `find ... -type f -not -name '.*'`（递归）→ `_find_files`（os.walk，隐藏名跳过）；`stat -c%s`/`stat -f%z` → `os.path.getsize`（失败回退 0）
- 截图格式判定：`command -v file` → `shutil.which("file")`，`file -b --mime-type` 前缀匹配 `image/`；无 file 时 magic bytes fallback（PNG `\x89PNG` / JPEG `\xff\xd8` / GIF8 / WebP RIFF…WEBP），读前 12 字节等价 sh `head -c 12 | od -t x1 | tr -d ' \n'` 比对
- `md5sum | sort | uniq -d` → `hashlib.md5` + `Counter`；md5 详情（`printf '%-2s'` 无尾换行 vs sh `printf '%s'`）与重复哈希按 basename 排序语义一致（sh `grep "^${hash}"` 在按 "hash  path" 排序的列表上匹配 → 按 path 排序）
- ahash：`grep -q "SKIP_NO_PILLOW"` → `in` 判定；`grep -c . | tail -1` 行计数 → `splitlines()` 非空行；`sort -u | grep -c .` → `set()` 去重计数。Pillow 缺失时 agate-image-check ahash 的 SKIP 走 stderr + exit 1，py 版 stdout 为空 → 同 sh `|| echo ""` 吞掉语义，不打印 ahash 段 Pillow 警告（sh 本就不可达分支，保留判定结构）
- `ls -A` 非空判定 → `os.listdir`；`AGATE_SKIP_IMAGE_CHECKS` 语义（`${VAR:-0}` = 1 跳过方差/相似度、仍做小图/md5）原样保留

### 修改 `agate/tests/unit/check-p6-evidence.bats`（调用点 .sh → .py，`@test` 数不变）

- 30 处 `run bash "$AGATE_SCRIPTS/check-p6-evidence.sh"` → `run "$PYTHON" "$AGATE_SCRIPTS/check-p6-evidence.py"`（fixtures.bash `$PYTHON`，不裸写 python3）
- 30 个 @test 名 + 头部注释脚本名改 .py（含 E.4 内联注释、L5 消费端引用行号 .py:64）

### 其他引用核查（确认无需改动）

- `unit/dispatch-context-warning.bats` L39：`cp .../check-p6-evidence.sh` 复制到 fake root 供**仍为 sh 的 pre-commit-gate.sh**（批次 3 才 py 化）调用，保持 .sh 复制不变（batch 2a/2b/2c 同款先例）
- `integration/consistency.bats` CON.9：`grep -q 'MD5_LIST' / 'md5sum' .../check-p6-evidence.sh` 断言的是迁移源 .sh 内容（.sh 保留、文本仍在）→ 不改（batch 2b agate-debt-check.bats L433 同款先例）
- `agate/scripts/pre-commit-gate.sh` L298、`agate-summary.sh` L46、`agate-summary.py` L25：sh 侧调用点/汇总清单，批次 3/4 迁移对象 → 不改
- `check-protocol-consistency.py` 锚点表（CHECK 8/9 的 check-p6-evidence.sh 条目）：.sh 仍存在，锚点不 ERROR → 不改（随批次 4 文档引用同步）
- `agate-md-field-get.py` L63 注释 / `scripts/README.md` L17 / `tests/README.md` L34：文档与注释引用 → 批次 4（表 B）处理

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`：check-p6-evidence.py 编译通过
- 手动 sh vs py 输出 diff（15 场景，exit code + stderr 逐字节一致）：无 P6 文件（exit 2）/ 无 BDD / PASS 缺引用（含详情行）/ 基本通过 / 无证据目录 / 空证据目录 / UI+screenshots 缺失 / UI+≤1KB 非图（exit 1）/ UI+md5 重复（含 basename 详情）/ UI+纯文本 / UI+不同截图 / 中文文件名 / 无扩展名引用 / 缺引用详情 / md5 重复含空格文件名

## 偏离点

> 无 DEVIATION / DESIGN_GAP。new py 的 usage 消息脚本名后缀 .sh → .py（"用法: check-p6-evidence.py TASK_DIR"），与 batch 1a/1b/1c/2a/2b/2c 同款先例一致；bats 无 no-arg 用例，无断言依赖。

> 范围说明：批次 2d 派发指引原列 check-p6-evidence + check-p6-provenance 两个脚本，本实现仅完成 **check-p6-evidence** 部分（check-p6-provenance 未在本轮做，见主 Agent 调度）。

---

# P4 实现记录 — 批次 2d 后半（check-p6-provenance py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 `agate/scripts/check-p6-provenance.py`（迁移源 .sh 保留，未改动）

| 新建 | 迁移源 | 依赖 |
|------|--------|------|
| `agate/scripts/check-p6-provenance.py` | `check-p6-provenance.sh` | `agate-md-field-get.py`（env FILE，op pass/fail/ui_affected，sys.executable subprocess）+ `agate-vision-blocker.py`（env YAML_PATH，sys.executable subprocess）+ `agate-evidence-consistency.py`（env EVIDENCE_DIR + env P6_FILE，sys.executable subprocess） |

- `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：exit 0/1/2 语义 + stderr 输出格式（GATE PROVENANCE / WARNING 前缀逐字节一致，已 12 个场景手动 sh vs py diff 验证）
- `$(...)` 剥尾换行 → `.rstrip("\n")`（三个被调 py 的 stdout 均处理；`|| echo` 失败回退语义按 returncode 判定）
- grep → re：`PASS_COUNT`/`P6_BODY_STRICT`/`P1_BDD`/预判计数均用逐行 `re.search`（`^\s*- PASS\b` / `^\s*- (PASS|FAIL) BDD-[0-9]` / `^#### BDD-[0-9]` / `^\s*- (PASS|FAIL)\b`，多行模式逐行语义一致）
- 审计 1a 括号提取链路：`sed 's/(vision:[^)]*)//g'` → `re.sub`；`grep -oE 'screenshots/[^ ),]+'` → `re.findall`；行末括号回退 `grep -oE '\([^)]+\)$'` → `re.search`；`IFS=',' read` 切分 → `split(",")`；`sed 's|^P6-evidence/||'` 三级前缀剥离 → `re.sub(r"^(P6-evidence|p6-evidence|evidences)/", "")`
- `find ... -type f -not -name '.*'`（递归）→ `_find_files`（os.walk，隐藏名跳过）；审计 5 的 `find ... -name '*.log'` → `_find_log_files`（名称以 .log 结尾，递归）
- 审计 2：`sed '/<!-- AGATE_CARD_START -->/,/<!-- AGATE_CARD_END -->/d'` + `sed '/^---$/,/^---$/d'`（删第一对 `---` 定界 frontmatter 块）→ 逐行状态机 + 首对 `---` 区间删除（含未闭合时删到 EOF 的 sed 语义）
- 审计 4 vision 引用：`grep -oE '\(vision:\s*[^)]+\)' | sort -u` → 逐行 `re.findall` + `sorted(set(...))`（grep 逐行语义，`\s` 不跨行）；`sed 's/^.*vision:\s*//' | tr -d ' )'` → `re.sub` + `replace`
- 审计 5：`tail -1` → 读全文 `splitlines()` 取末行；`grep -qE '^EXIT_CODE: [0-9]+$'` → `re.match`；`grep -qF "$LOG_BASENAME"` → `in p6_text` 子串判定
- `get_agent`：`sed -n '/^---$/,/^---$/p' | grep '^agent:' | sed 's/^agent:\s*//' | head -1` → 首对 `---` 间 `re.match(r"^agent:\s*(.*)")` 取首个
- 协作规范 case 模式（*-dispatch-context*.md / *-dispatch-prompt-*.md / *-progress.md / *-paused-resolution.md）→ `_SKIP_AGENT_CHECK` 正则元组
- 审计 6：`echo "$INCONSISTENCY" | sed 's/^/  - /'` → `splitlines()` 逐行前缀

### 修改 `agate/tests/unit/check-p6-provenance.bats`（调用点 .sh → .py，`@test` 数不变）

- 36 处 `run bash "$AGATE_SCRIPTS/check-p6-provenance.sh"` → `run "$PYTHON" "$AGATE_SCRIPTS/check-p6-provenance.py"`（fixtures.bash `$PYTHON`，不裸写 python3）
- 36 个 @test 名 + 头部注释脚本名改 .py；`setup()` 的 `create_python_shim_bin` shim **保留**（本文件 PV_BDD19.1/PV_BDD20.1 仍调 `check-gate.sh`，其内部裸 python3 需 shim 兜底）

### 其他引用核查（确认无需改动）

- `unit/dispatch-context-warning.bats` L34：`cp .../check-p6-provenance.sh` 复制到 fake root 供**仍为 sh 的 pre-commit-gate.sh**（内部 `bash .../check-p6-provenance.sh`）调用，保持 .sh 复制不变（batch 2a/2b/2c + check-p6-evidence 同款先例）
- `unit/check-p6-evidence.bats` L48 注释 `文件存在性由 check-p6-provenance.sh 验证` → 已同步改 .py（引用面）
- `agate/scripts/pre-commit-gate.sh` L198、`agate-summary.sh` L46、`agate-summary.py` L26、`ci-gate-backstop.py` L262：sh 侧调用点/汇总清单，批次 3/4 迁移对象 → 不改
- `check-protocol-consistency.py` 锚点表（CHECK 8/9 的 check-p6-provenance.sh 条目）：.sh 仍存在，锚点不 ERROR → 不改（随批次 4 文档引用同步）
- `tests/README.md` L36、`scripts/README.md` L18、`agate-md-field-get.py` L63 注释、`platform-notes.md`/`phase-cards/P6-acceptance.md`/`verifier.md`/`dispatch-protocol.md` 等文档与注释引用 → 批次 4（表 B）处理

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`：check-p6-provenance.py 编译通过
- 手动 sh vs py 输出 diff（12 场景，exit code + stderr 逐字节一致）：基本通过 / PASS 缺引用（含详情行）/ dispatch-context 预判 / P1 BDD>P6（挑验）/ P1 无标准 BDD / UI 缺 vision 引用 / vision YAML blocker!=0 / vision YAML 通过 / 日志 EXIT_CODE=1 矛盾 / 日志缺 EXIT_CODE 跳过 / evidence JSON 矛盾（含 前缀）/ frontmatter pass+fail 不一致 WARNING / 嵌套括号 nth(1) / 逗号分隔多引用缺一 / agent 缺字段 exit2 / 充数证据文件 / 无 P6 文件

## 偏离点

> 无 DEVIATION / DESIGN_GAP。三点记录：
> 1. new py 的 usage 消息脚本名后缀 .sh → .py（"用法: check-p6-provenance.py TASK_DIR"），与 batch 1a/1b/1c/2a/2b/2c/2d 同款先例一致；bats 无 no-arg 用例，无断言依赖。
> 2. sh 版 `get_risk_level()` 定义但从未被调用（死代码）——未迁移，其余逐条等价。
> 3. 审计 3 frontmatter pass/fail 非数字时 sh 侧 `$((PASS_FM + FAIL_FM))` 在 `set -e` 下硬失败（exit 1）；py 版显式捕获 ValueError 输出 GATE PROVENANCE 诊断后 exit 1（fail-closed 语义等价，无 bats 覆盖该畸形输入）。

---

# P4 实现记录 — 批次 2e（check-tdd-red py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 `agate/scripts/check-tdd-red.py`（迁移源 .sh 保留，未改动）

| 新建 | 迁移源 | 依赖 |
|------|--------|------|
| `agate/scripts/check-tdd-red.py` | `check-tdd-red.sh`（216 行） | `agate_common.resolve_formatter / run_test_with_formatter`（try/except ImportError 兜底 exit 3）+ `agate-read-gate-commands.py`（env GATE_FILE，sys.executable subprocess） |

- `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：exit 0（真红灯/B 类）/ 1（A 类）/ 2（绿灯）/ 3（无运行器）+ stdout/stderr 消息逐字节一致（已 12 场景手动 sh vs py diff 验证，见下）
- 测试运行器探测链原样保留：`$TEST_RUNNER` → gate_commands.P3*（P2-design.md）→ which pytest → exit 3；`TEST_RUNNER` 优先于 gate_commands.P3（TDD.G3）；`PROJECT_MODULE` 覆盖 gate_commands.project_module（TDD.F12）；`AGATE_TDD_TIMEOUT` 超时语义（exit 124 → 红灯 exit 0，TDD.TIMEOUT）
- `$(...)` 剥尾换行 → `json.loads`（agate-read-gate-commands.py stdout 直接 parse，空 JSON `"{}"`/ValueError → 空命令回退）
- **`run_test_with_formatter` / `resolve_formatter` 直接 import agate_common**（P2 批次 0 公共库，原 sh source gate-result.sh）——不重新实现；formatter 仍是 bash 脚本 → `bash <fmt_path> <exit_code>` subprocess 保留在公共库内
- `command -v pytest` → `shutil.which("pytest")`（无 PATH 时 None → exit 3，TD.1b/TDD.F8 语义保持）
- JSON 字段提取不再逐字段子进程调 agate-json-get.py，改为 `json.loads` 内联等价（get / len / count_prefix 语义逐一对应，见偏离点）
- 无 formatter 的 A/B 判定（RM-AG0002/TPV0090-M4）：exit 1 + raw_output 编译/import 关键词（Traceback|SyntaxError|ImportError|ModuleNotFoundError）→ A 类；import/name_errors 前缀匹配 `project_module` → B 类；syntax/errors>0 → A 类；failed>0 → classic red-light（TDD.F1/F3/F4/F5/F11/F12/bdd-30/31/35/36/37）

### 修改 `agate/tests/unit/check-tdd-red.bats`（调用点 .sh → .py，@test 数 43 不变）

- 37 处 `run env ... bash "$AGATE_SCRIPTS/check-tdd-red.sh"` → `"$PYTHON" "$AGATE_SCRIPTS/check-tdd-red.py"`（fixtures.bash `$PYTHON`，不裸写 python3）；含 `bash -c` 无、`env -u PATH` 两处、`TEST_RUNNER=... AGATE_TDD_TIMEOUT=2 run ... "$task_dir"` 位置参数一处
- TD.1b/TDD.F8 的 `env -u PATH "$(command -v bash)" ...sh` → `env -u PATH "$PYTHON" ...py`（$PYTHON 为绝对解释器路径，env -u PATH 下仍可定位，语义不变）+ 注释同步（"脚本内 shutil.which pytest 仍失败"）
- @test 名内脚本名 `.sh` → `.py`（TD.1/1b/2-8、TDD.N1-N4、TDD.G1-G5、TDD.F1-F12、bdd-30/31/35/36/37）
- `check-tdd-red-formatter.bats`（13 用例）**无改动**：其全部调用点是 formatter 脚本本身（`bash "$FORMATTER_DIR/xxx.sh"`，仍是 sh、非本批次迁移对象），全文无 check-tdd-red 调用点

### 其他引用核查（确认无需改动）

- `unit/check-gate.bats` L454/470：断言的是 `check-gate.sh` P3 分支输出含 "check-tdd-red.sh" 字符串——check-gate.sh 未迁移（批次 3），输出不变 → 不改
- `unit/ci-gate-backstop.bats` L112-143：通过 `AGATE_TDD_RED_SCRIPT` env 指向 mock bash 脚本测试 `ci-gate-backstop.py` 的 P3 兜底分支——ci-gate-backstop.py 未迁移（批次 4）、默认仍指向 scripts/check-tdd-red.sh（.sh 保留存在），mock 语义不变 → 不改
- `agate/scripts/ci-gate-backstop.py` L176 默认值 `scripts/check-tdd-red.sh`、`agate-summary.sh` L62 / `agate-summary.py` L33 `_DRIFT_SCRIPTS`、`check-protocol-consistency.py` L572 锚点表：sh 侧调用点/汇总清单，批次 3/4 迁移对象 → 不改
- `agate/tests/README.md` L43 覆盖度表格（check-tdd-red.sh 43）：留待批次 4 文档引用同步（表 B）处理（batch 1b/1c/2a/2b/2c/2d 同款先例）

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`：check-tdd-red.py 编译通过
- 手动 sh vs py 输出 diff（12 场景，exit code + stdout/stderr 逐字节一致）：
  - 绿灯（"5 passed" exit 0）→ exit 2 + "no red-light"；经典红灯（无 formatter "2 failed, 5 passed" exit 1）→ exit 0 + "red-light (unexpected test failure)"
  - 无 formatter exit 1 + SyntaxError/Traceback → exit 1 + A-class（RM-AG0002 bdd-30）；无 formatter 普通断言 → exit 0（bdd-31）
  - 运行器不存在（exit 127）→ exit 1 + "test runner failed with exit code 127"（TD.1）
  - 无 TEST_RUNNER + 无 TASK_DIR + 无 pytest（env -u PATH）→ exit 3 + "no test runner found"（TD.1b/TDD.F8）
  - 无 formatter ImportError 启发式 → exit 0（TD.4-8 语义）
  - gate_commands.P3 自动读取（TDD.G1）+ formatter pytest.sh classic red-light（TDD.F1，含 abs 路径 formatter TDD.F11）+ 提示行 stderr 内容逐字节一致
  - 多栈 P3 + P3_js（pytest.sh + vitest.sh）→ 2 条 classic red-light + exit 0（TDD.F10）
  - 超时（AGATE_TDD_TIMEOUT=1 + sleep 3）→ exit 0 + 两条"超时"消息（run_test_with_formatter + judge 各一条）（TDD.TIMEOUT）
  - formatter NameError 项目内 → exit 0 + B-class；TypeError → exit 1 + A-class（bdd-35/37）
  - gate_commands 读取失败 / P2 无 gate_commands → 回退 TEST_RUNNER / pytest 链（TDD.G2/G4）

## 偏离点

[DEVIATION: check-tdd-red.py 不再 subprocess 调 `agate-json-get.py`（sh 版 judge_result/collect_commands 共 10+ 处 `echo "$json" | python3 agate-json-get.py get/len/index/count_prefix`），改为 `json.loads` 内联等价——get(key, default) → `data.get(key, default)`（default 原样）、len(key) → `len(data.get(key, []))`、count_prefix(module) → `sum(1 for e in ... if e.get("module","").startswith(prefix))`。行为逐场景实测与 sh 一致；batch 2c agate-capture-env-baseline.py 同款先例]

[DEVIATION: check-tdd-red.py 的 `from agate_common import ...` 失败（独立目录缺公共库）→ stderr 提示 + exit 3——sh 版 source gate-result.sh 失败会在 set -e 下 exit 1。语义差异仅在"复制单脚本到独立目录且缺 agate_common.py"场景，bats 无覆盖；check-debt.py（batch 2a）同款处理先例]

> 实现说明（非 DEVIATION）：py 版 judge_result 的 classic red-light 提示行（stderr）与 TDD_CHECK 主消息（stdout）的**顺序**可能因流缓冲与 sh 不同（终端 2>&1 下 stderr 先显示）——bats 的 `$output` 合并两流、断言均为子串判定，顺序无关；两流各自内容逐字节一致。

[SCOPE+]: `unit/check-tdd-red.bats` 的 `setup()` python3 shim（TAG0009 BDD-16/17）在 py 版下已无作用——脚本经 `$PYTHON` 直调 + 内部 `sys.executable`，不再裸调 python3。按最小实现原则保留不动（batch 2b check-state-transition.bats / 2a check-retrospective.bats 同款先例），记录供后续清理]

> 范围说明：批次 2e 派发指引原列 check-tdd-red.bats + check-tdd-red-formatter.bats 两个测试文件，formatter 文件实际无 check-tdd-red 调用点（纯 formatter 直测），故未改动（见上）。

---

# P4 实现记录 — 批次 2f-1（check-gate.py 迁移第一部分：框架 + P0/P1/P2/P3/P4 分支）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 `agate/scripts/check-gate.py`（迁移源 .sh 保留，未改动；P5-P8 分支下一批追加）

| 新建 | 迁移源 | 依赖 |
|------|--------|------|
| `agate/scripts/check-gate.py` | `check-gate.sh`（488 行） | `agate_common.run_git`（try/except 兜底本地 subprocess）+ `agate-md-field-get.py`（env FILE，need_confirm_resolved / suggest_resolved）+ `agate-gate-missing-cmds.py`（env GATE_FILE），均 sys.executable |

- `#!/usr/bin/env python3`；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：`check-gate.py PHASE TASK_DIR [OLD_PHASE]`；exit 0/1/2 语义 + stderr 输出格式（GATE P0-P4 / WARNING / 回退抵达 / 未知阶段 消息逐字节一致，已 61 个场景手动 sh vs py diff 验证）
- 整体结构：`main()` 内回退检测（OLD_PHASE 数字 > PHASE → exit 2）+ `handlers` dict 分发；每分支一个 `gate_pN(task_dir)` 函数
- **本批只挂 P0-P4**：P5-P8 未实现，按派发指引不留 TODO 空壳；未实现阶段落入 sh `*)` 的「未知阶段」兜底（exit 2），下一批追加真分支
- `$(...)` 剥尾换行 → `.rstrip("\n")`（agate-md-field-get / agate-gate-missing-cmds stdout 均处理）
- P1/P2/P4 的 review frontmatter `status:`/`agent:` 提取：`_frontmatter_field` 复刻 sh `sed -n 's/\r$//; /^---$/,/^---$/p'` + `grep '^field:'` + `sed 's/^field:\s*//'` + `head -1`（CRLF 容错由 `splitlines()` 剥 `\r` 承担，M6/bdd-14 语义）
- P1 流 C：`need_confirm_resolved`/`suggest_resolved` 逐条匹配用 `set(resolved_fm.split("\n"))` 等价 `grep -qFx -- "$desc"`（整行精确匹配）；desc 提取复刻 sed 三连替换（SUGGEST 剥前缀 + 尾部反引号 + 尾部 `]`）
- P2：candidate_count 首行数字提取（`re.match(r"^candidate_count:")` + `re.search(r"[0-9]+")`）等价 `grep -E | grep -oE | head -1`；design_trivial/follows_existing_pattern 降 MIN_CANDIDATES；`command -v` → `shutil.which`；四字段计数 + 权衡/选择理由 nudge
- P4：`git diff --cached --name-only` → `run_git`（cwd=当前目录，同 sh 在 repo 内执行）；暂存区排除正则 `(^|/)P[0-8]-.*\.md$|(^|/)\.state\.yaml$` 原样迁移（逐行 `.rstrip("\r")`，check-state-transition.py 同款 tr -d '\r' 处理）

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`（含 `-W error::SyntaxWarning`）编译通过
- 手动 sh vs py 输出 diff：**61 个场景 exit code + stderr 逐字节一致**，覆盖：
  - P0（1）/ P1（21，含缺 review、agent=main、无 BDD、NEED_CONFIRM 未解决/已解决/反引号包裹、SUGGEST 去重/不匹配、CRLF 行尾、rejected、typo 兜底 1/2、inline NEED_CONFIRM、无声明、缺 status、正文 approved 对抗绕过）/ P2（23，含无设计、0/1/2 候选、缺 candidate_count、缺 review、rejected、agent=main、缺 agent、缺四字段、无权衡、选择+理由、design_trivial、follows_existing_pattern、缺命令 WARNING、全命令可执行、frontmatter 四字段、candidate_count 优先级/正文/frontmatter-only/非数字）/ P3（2）/ P4（9，含无 review、rejected、agent=main、缺 agent、仅 .md、.py、混合、md+yaml+py）/ 回退抵达 3 + 非回退 2 / 未知阶段 1
- `check-protocol-consistency.py`：0 ERROR（全部通过）

## 偏离点

> 无 DEVIATION / DESIGN_GAP。三点记录：
> 1. new py 的 usage 消息脚本名后缀 .sh → .py（"用法: check-gate.py PHASE TASK_DIR"）——与 batch 1a/1b/1c/2a-2e 同款先例一致；sh `${1:?用法: check-gate.sh ...}` 的 no-arg 行为（exit 1）等价保留
> 2. P5-P8 阶段本批未实现，落入「未知阶段」兜底（exit 2）——sh 版 P5/P6/P8 本身也 exit 2、P7 exit 0，尚未实现阶段与 sh 的 exit code 有差异（P7 例外），下一批追加后消除；bats 的 P5-P8 调用点仍指向 .sh，不受影响
> 3. `_frontmatter_field`/`_frontmatter_lines` 在首个 `---` 块未闭合（全文只有一个 `---`）时按 sed 语义读到文件尾；与 check-p6-provenance.py `get_agent` 同款实现，bats 无此类畸形输入用例

---

# P4 实现记录 — 批次 2f-2（check-gate.py 迁移第二部分：追加 P5/P6/P7/P8 分支）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 扩展 `agate/scripts/check-gate.py`（P5-P8 分支补齐，sh 迁移源未改动）

- 在既有 `gate_p0`-`gate_p4` 之后追加 `gate_p5`/`gate_p6`/`gate_p7`/`gate_p8` 四个函数，`handlers` dict 挂 P5-P8；模块 docstring 更新为「P0-P8 全部分支已实现」
- 新增 helper：`_gate_p5_count`（调 `agate-gate-p5-count.py`，env GATE_FILE，失败回退 (0,0)）；`_to_int`（失败回退 0，对应 bash 算术错误按 0 处理）；`_to_int_or_none`（非数字返回 None，对应 bash `[ x -lt y ]` 非整数报错→条件为 false 的语义，用于 P7 DESIGN_GAP 配对避免畸形 frontmatter 误拦截）
- **P5**：`GATE P5: 需从 P2-design.md gate_commands.P5 动态读取`（exit 2）+ 多命令 WARNING（main+aux 总数 >1，T060 教训）+ pre-task-baseline.md vs fail-list.txt 机械 diff（`captured_at_commit:` 缺失→exit 2；新增失败→拦截 exit 1；预存失败→known-failures.md 存在且登记条目数足够才放行）。fail-list 提取复刻 `sed -n '/```fail-list/,/```/p' | sed '1d;$d' | grep -v '^$'`（含无闭合 fence 时 sed 读到文件尾再 `$d` 的边界）；`comm -13/-12` → sorted set 差集/交集
- **P6**：change_type=refactor → `regression_pass: true` + `P6-evidence/regression.log` 硬校验；pass/fail frontmatter 汇总（新格式，BDD-16）vs 正文 grep 严格计数回退（旧格式，BDD-18，行首 `- PASS|FAIL ... BDD-N`，`\b` 词边界）；FAIL≠0 或 TOTAL=0 → exit 1；P6-evidence/ 非空校验；最终 exit 2。**不调 check-p6-evidence.py / check-p6-provenance.py**——与 sh 版一致（sh check-gate.sh P6 同样不调，provenance 审计由 pre-commit-gate.sh / ci-gate-backstop.py 单独执行）
- **P7**：blocker_count/deviation_critical_count frontmatter（新格式，BDD-19）vs 正文 grep + 非计数行排除正则回退（旧格式，M4 `(:|：)` 全角冒号）→ >0 拦截；design_gap_count/design_gap_reviewed_count frontmatter（新格式，BDD-20，reviewed≥count）vs 数量相减回退（旧格式）；T090 关键词 WARNING；R2.3 P4/P7 DESIGN_GAP 转抄交叉核对（P4-implementation.md + P4-implementation/ 目录递归）；N3 跨文件引用 WARNING；exit 0
- **P8**：bump_type/debt_check 字段存在性（exit 1）；version 文件变更双路径（暂存区 `--stat` + 最近 LOOKBACK commit，AGATE_VERSION_FILES 可配）WARNING；CHANGELOG 双路径（CHANGELOG_FILE 可配）WARNING；tag 存在性检查（VERSION_TAG_PREFIX 可配，从暂存区 CHANGELOG diff 提取首个版本号）WARNING；最终 exit 2。git 命令均走 `_git`（run_git，cwd=当前目录，同 sh 在 repo 内执行）；`HEAD~N` 存在性用 `rev-parse` returncode 判定

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`（含 `-W error::SyntaxWarning`）编译通过
- 手动 sh vs py 输出 diff：P5（7 场景：缺/有 P2-design 多命令 WARNING、baseline 损坏、new fails 拦截、无 known-failures 拦截、登记不足/足够、干净 exit 2）/ P6（6 场景：旧格式 FAIL>0、新格式干净、新格式 FAIL>0、证据为空、refactor 缺回归证据、refactor 满足）/ P7（7 场景：新格式干净、BLOCKER>0、DEVIATION-CRITICAL、reviewed<count、旧格式 R2.3 遗漏转抄、旧格式干净、N3 WARNING）/ P8（5 场景：缺 bump_type、缺 debt_check、无暂存 WARNING×2、version 暂存、tag 存在/不存在）——**exit code + stderr 逐字节一致**
- `check-protocol-consistency.py`：未重跑（主 Agent 验证阶段执行；本批只动 check-gate.py 内部，未改协议文档/其他脚本，依赖表不变）

## 偏离点

> 无 DEVIATION / DESIGN_GAP。一点记录：
> 1. `_to_int`/`_to_int_or_none` 对非数字 frontmatter 字段（P6 pass/fail、P7 blocker 等）按「算术比较失败→条件为 false」处理，与 bash `[ x -gt 0 ]`/`$((x+1))` 的非整数报错口径一致（畸形输入下 sh 报错 false/直接 exit 1，py 回退为 0 或 None，均不误拦截；P6 非数字 pass/fail sh 会在 `$((...))` 崩溃 exit 1，py 回退 0 → TOTAL=0 拦截，同为阻断语义）

---

# P4 实现记录 — 批次 2f-3（check-gate.bats 全部调用点 .sh → .py）

## implementation_dir

```
implementation_dir: agate/tests/unit/check-gate.bats
```

## 本批次改动清单

> 本轮只改 bats 测试文件的调用点/脚本名引用（check-gate.py 本体的 P0-P8 分支已由批次 2f-1/2f-2 完成）。未跑任何 bats（主 Agent 验证）。

### 修改 `agate/tests/unit/check-gate.bats`（调用点 .sh → .py，`@test` 数不变）

- 全局替换 `check-gate.sh` → `check-gate.py`（187 处，含 @test 名、头部注释、调用点）
- 调用形态同步改为 `$PYTHON`（fixtures.bash `$PYTHON`，不裸写 python3）：
  - 直接调用：`run bash "$AGATE_SCRIPTS/check-gate.sh"` → `run "$PYTHON" "$AGATE_SCRIPTS/check-gate.py"`（P0-P8 全 phase，共 152 处）
  - 嵌套调用：`bash -c "cd '$repo' && bash '$AGATE_SCRIPTS/check-gate.sh' ..."` → `bash -c "cd '$repo' && '$PYTHON' '$AGATE_SCRIPTS/check-gate.py' ..."`（P4/P8 共 16 处，批次 2a/2b/2c 同款先例）
  - env 形态：`run env LC_ALL=C LANG= bash "$AGATE_SCRIPTS/check-gate.sh"` → `run env LC_ALL=C LANG= "$PYTHON" "$AGATE_SCRIPTS/check-gate.py"`（1 处）
- 断言体不动（无断言引用脚本名字符串；L1365 的 `grep -q 'P2-review.md frontmatter status 非 approved' "$AGATE_ROOT/scripts/check-gate.py"` 是 grep 被测 .py 源码内容，非脚本名断言）
- `setup()` 的 `create_python_shim_bin` shim **保留**（本文件 BDD-16/17 语义：py 版内部经 `$PYTHON` 直调 + `sys.executable`，已无裸 python3；保留无副作用，批次 2a/2b 同款先例）

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `grep -c 'check-gate\.sh'` → 0 残留；`check-gate.py` 187 处
- `bats -c` 解析通过（124 用例，与 count-tests.sh 基线一致）
- `grep 'bash.*check-gate\.py'` 复查：仅剩 16 处 `bash -c "..."` 嵌套包装（内层已为 `'$PYTHON' '.../check-gate.py'`），无 `bash "$AGATE_SCRIPTS/check-gate.py"` 裸 bash 调用残留

## 偏离点

> 无 DEVIATION / DESIGN_GAP。@test 名/注释内脚本名后缀 .sh → .py（批次 1a-2f 全链同款先例），非断言依赖。

---

# P4 实现记录 — 批次 2f-3 后半（check-gate.bats 以外其余文件调用点 .sh → .py）

## implementation_dir

```
implementation_dir: agate/tests/
```

## 本批次改动清单

> 本轮只改其余 bats 测试文件的 `check-gate.sh` 调用点（check-gate.bats 已由批次 2f-3 前半完成）。未跑任何 bats（主 Agent 验证）。

### 修改 7 个 bats 文件（调用点 .sh → .py，`@test` 数不变，断言体不动）

| 文件 | 处数 | 形态 |
|------|------|------|
| `regression/v060-p8-cached.bats` | 3 | 嵌套 `bash -c "cd '$repo' && bash '.../check-gate.sh' P8 'task'"` → `bash -c "cd '$repo' && '$PYTHON' '.../check-gate.py' P8 'task'"`（check-gate.bats 嵌套形态同款） |
| `regression/v060-design-gap.bats` | 4 | `run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"` → `run "$PYTHON" "$AGATE_SCRIPTS/check-gate.py" P7 "$dir"` |
| `unit/check-gate-p1-review.bats` | 9 | `run bash "$AGATE_ROOT/scripts/check-gate.sh" P1 "$TASK_DIR"` → `run "$PYTHON" "$AGATE_ROOT/scripts/check-gate.py" P1 "$TASK_DIR"` |
| `unit/check-gate-p5-diff.bats` | 13 | `run bash "$AGATE_SCRIPTS/check-gate.sh" P5 "$dir"` → `run "$PYTHON" "$AGATE_SCRIPTS/check-gate.py" P5 "$dir"` |
| `unit/check-retrospective.bats` | 1 | RT_BDD21.1 的 `run bash "$AGATE_SCRIPTS/check-gate.sh" P1 "$dir"` → py |
| `unit/check-p6-format.bats` | 1 | F_BDD18.1 的 `run bash "$AGATE_SCRIPTS/check-gate.sh" P6 "$dir"` → py |
| `unit/check-p6-provenance.bats` | 2 | PV_BDD19.1 / PV_BDD20.1 的 `run bash "$AGATE_SCRIPTS/check-gate.sh" P7 "$dir"` → py |

合计 **33 处**调用点。全部用 fixtures.bash 的 `$PYTHON`（探测 python3|python），不裸写 python3。

### 其他引用核查（确认无需改动，`grep -rn 'check-gate\.sh' agate/tests/` 残留 17 处全部为有意保留）

- `tests/README.md` L31：覆盖度表格文档引用 → [SCOPE+] 批次 4（表 B）处理
- `integration/commit-msg-self-gate.bats` L51-52：check-gate.sh 仅作 **CSG.5 的触发文件**（验证 `agate/scripts/*.sh` 改动触发 self-gate hook），非调用/执行引用 → 不改
- `integration/pre-commit-hook.bats` L1158：@test 名「hook runs check-gate.sh」——pre-commit-gate.sh 此时仍为 sh（批次 3 才 py 化），hook 确实跑 check-gate.sh，名字仍准确 → 不改
- `integration/consistency.bats` CON.12（L61-62）：grep 迁移源 .sh 内容断言（NO_NEED_CONFIRM/SUGGEST 锚点，.sh 保留、文本仍在）→ 不改（CON.9 check-p6-evidence / batch 2b agate-debt-check L433 同款先例）
- `unit/check-state-transition.bats` L402 / `unit/check-retrospective.bats` L44 / `unit/check-p6-format.bats` L80-81 / `unit/check-p6-provenance.bats` L94/349/547：@test 名 / 注释提及，非调用点 → 不改
- `unit/dispatch-context-warning.bats` L33：`cp .../check-gate.sh` 复制到 fake root 供**仍为 sh 的 pre-commit-gate.sh**（批次 3 才 py 化）调用，保持 .sh 复制不变（batch 2a-2e 同款先例）
- `unit/agate-debt-check.bats` L12/566-567：注释 + grep 迁移源 .sh 内容断言（debt_check 锚点，.sh 保留）→ 不改

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `grep -rn 'check-gate\.sh' agate/tests/`：残留 17 处全部为上述有意保留项（文档引用 / @test 名注释 / 触发文件 / .sh 内容静态断言 / 批次 3 范围），无调用点残留
- `grep -rn 'check-gate\.py'` 对照：33 处新增调用点 + check-gate.bats 187 处 = 220 处
- `bash -n` 对 bats `@test "name" {` 语法本就报错（原始未改文件同样报错，批次 1e 先例），不适用；真实验证以主 Agent 的 bats 运行为准

## 偏离点

> 无 DEVIATION / DESIGN_GAP。

---

# P4 实现记录 — 批次 3a（pre-commit-gate.py 主程序，承载调度逻辑）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 `agate/scripts/pre-commit-gate.py`（迁移源 pre-commit-gate.sh 保留，未改动；薄壳化是批次 3d）

| 新建 | 迁移源 | 依赖 |
|------|--------|------|
| `agate/scripts/pre-commit-gate.py`（520 行） | `pre-commit-gate.sh`（404 行） | `agate_common`（write_gate_result / read_state_phase / read_state_task_id / resolve_agate_root / resolve_workspace / run_git）+ 12 个子脚本（sys.executable）：check-state-yaml / check-state-transition / check-gate / check-p6-provenance / check-pruning / check-scope-resolved / agate-next-card / check-frontmatter / check-p6-format / check-retrospective / check-changelog / check-p6-evidence + agate-state-get.py helper（phase_stdin） |

- `#!/usr/bin/env python3`；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：hook 无参数运行；exit 0/1；`GATE P{n} (...)` / `GATE WARNING` / `GATE STATE-YAML` 输出格式；全部写 stderr（同 sh）
- 承载逻辑（sh 版逐段对应，均已在 py 侧实现）：
  1. **REPO_ROOT**：`git rev-parse --show-toplevel`（失败回退 cwd）+ `os.path.realpath` 归一（等价 sh realpath -m）
  2. **AGATE_ROOT**：`resolve_agate_root(__file__)`（env 优先 → 脚本真实路径上溯 → 复制模式 `.agate-root` 恢复）
  3. **工作区**：`resolve_workspace(repo_root)` → tasks_dir（等价 agate-workspace-resolve.sh source 语义）
  4. **收集暂存 .state.yaml**（根 + 任务级，S1 数组化：空格路径不切词）
  5. 每个 state file：格式校验（check-state-yaml）→ phase 变更检测（`git diff --cached` 逐行 `^\+.*phase:`）→ 状态转移（check-state-transition）→ 读 phase/task_id（agate_common）→ **OLD_PHASE**（`git show HEAD:STATE_REL` 经 stdin 管道进 agate-state-get.py phase_stdin，`$(...)` 剥尾换行 → rstrip）→ 反推 TASK_DIR → phase-产出一致性 WARNING（2f）→ 非 gate 阶段跳过 → **PROD_TOUCHED 三步检测**（只扫新增行 `^+[^+]`、剥 `+`、AGATE_CARD 块删除，锚点关键字存活）→ frontmatter schema（2g.2）→ P6 格式归一化（check-p6-format --fix + git add）→ **check-gate**（2>&1 合并捕获）→ **write_gate_result**（agate_common）→ P6 provenance / pruning / scope（gate_exit≠1 时跑）→ **dispatch-context hash 校验**（agate-next-card.py + sha256，CRLF 归一化）→ retrospective → CHANGELOG（P8）→ P6 evidence（P6/P7）→ B3 / E3 → gate 结果处理（0/1/2 三态）
  6. **扫描暂存 P{n}-*.md 一致性**（无 .state.yaml 变更的任务也检查，section 3，WARNING 不拦截）
- **fail-closed**：agate_common import 失败（缺 pyyaml → agate_common 自身 exit 1；agate_common.py 缺失 → GATE ERROR + exit 1）；子脚本缺失/执行失败 → 非零阻断（不运行 sh 兜底）
- **软链调用场景**（git 经 `.git/hooks/pre-commit` 软链调起）：`SCRIPT_DIR` 用 `os.path.realpath(__file__)` 解析 + `sys.path` 显式插入——sh 版 readlink -f 语义等价，避免子脚本/公共库定位失败
- 子脚本调用统一封装：`_run_script_rc`（stdout/stderr 透传或 stderr 抑制）/ `_run_script_capture`（merge 合并 2>&1 / suppress / stdin 输入），等价 sh 的 `bash x.sh args` / `2>/dev/null` / `2>&1` / 管道四种形态

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`：pre-commit-gate.py 编译通过
- 手动功能核对（临时 git repo，非 bats）：
  - P1 缺 review → `GATE P1 (...): 未通过` + check-gate stderr + exit 1
  - P1 完整（requirements + review + dispatch-context 嵌入卡片）→ `GATE P1: 需主 Agent 手动判断` + exit 0 + `.gate-result.json` 写入（phase/task_id/exit_code/runner=pre-commit-hook/prev_commit_sha 字段齐全）
  - 缺 dispatch-context（产出已暂存）→ `GATE: subagent 派发阶段产出 commit 需提供 P1-dispatch-context-{role}.md` + exit 1
  - PROD_TOUCHED 正向 → `GATE: [PROD_TOUCHED] 检测到生产环境接触...commit 中止` + exit 1
  - 空格路径任务 + task_id 非法 → `GATE STATE-YAML: .state.yaml 格式错误` + exit 1（S1 空格不切词）
  - 回退 P2→P1 → check-gate 检测「回退抵达」+ exit 2 不拦截（OLD_PHASE 管道正确）
  - P4 暂存代码文件缺 dispatch-context → `GATE: ... P4-dispatch-context-{role}.md` + exit 1（E3/P4 分支）
  - section 3：暂存 P2 产出但 phase=P1 → `GATE WARNING: 暂存了 P2 产出但 phase=P1` + exit 0
  - 真实 git commit 经软链 hook → 提交成功 + `.gate-result.json` 落盘
  - `check-protocol-consistency.py`：未重跑（主 Agent 验证阶段执行；本批只动 pre-commit-gate.sh → 新增 py，锚点表 CHECK8/9 的 pre-commit-gate.sh 条目 .sh 仍存在，不 ERROR；批次 4 文档引用同步时统一处理）

## 偏离点

[DEVIATION: 2p dispatch-context hash 校验的提示消息脚本名后缀改 .sh → .py（"重新调 agate-next-card.py P2 复制到 dispatch-context 文件" / "调 agate-next-card.py P2 嵌入 dispatch-context 模板"）——sh 版写 agate-next-card.sh；与新脚本名一致（batch 1a-2f 同款先例）。bats 不断言该消息正文]

[DEVIATION: PROD_TOUCHED 检测的 `git diff --cached -- "$TASK_REL"` 传相对路径（sh 同款）——py 版用 run_git 直传，无需 awk 前缀过滤（TASK_REL 非暂存名过滤，sh 的 `tr -d '\r' | awk prefix | grep -q .` 守卫等价实现为 `any(f.startswith(prefix) for f in _staged_name_only())`）]

> 实现说明（非 DEVIATION）：`_extract_card` 复刻 `sed -n '/START/,/END/p' | sed '1d;$d' | tr -d '\r'` 语义（区间含标记行 + 首末行删除 + CR 剥离，未闭合读到 EOF）。`_staged_name_only` 每处调用都是独立 git 子进程——sh 同样每处重跑 `git diff --cached`，行为一致（P6 --fix 的 git add 会改变后续暂存集，独立调用保持语义）。

---

# P4 实现记录 — 批次 3b（commit-msg-self-gate / pre-push-gate / install-hook py 化）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

### 新建 3 个 .py（迁移源 .sh 保留，未改动；薄壳化是批次 3d）

| 新建 | 迁移源 | 依赖 |
|------|--------|------|
| `agate/scripts/commit-msg-self-gate.py` | `commit-msg-self-gate.sh`（37 行） | `agate_common.run_git`（ImportError/SystemExit 降级本地 subprocess） |
| `agate/scripts/pre-push-gate.py` | `pre-push-gate.sh`（28 行） | `agate_common.run_git`（同上降级） |
| `agate/scripts/install-hook.py` | `install-hook.sh`（93 行） | `agate_common.run_git`（同上降级）+ `os.symlink`/`shutil.copyfile`/`os.chmod` |

- 全部 `#!/usr/bin/env python3` shebang；文件读写显式 `encoding="utf-8"`；Python 3.8+（无 match / str.removeprefix）
- CLI 契约与 sh 版等价：hook 无参数（pre-push / install-hook）或 1 参数（commit-msg-self-gate COMMIT_MSG_FILE，缺参 → 用法错误 exit 1，同 sh `${1:?}`）+ exit 语义（commit-msg/pre-push 永不阻断 exit 0；install-hook 非 git 仓库 / AGATE_ROOT 缺脚本 → stderr + exit 1）
- commit-msg-self-gate.py：self-gate 触发面 grep（`^(agate/scripts/.*\.(sh|py)|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$` 逐行 `re.match` + `line.rstrip("\r")`）→ commit message 扫 `^self-gate-skip:\s*\S+` / `^self-gate-review:\s*\S+`（`re.MULTILINE`）→ 均未命中则 6 行 WARNING 写 stderr（已与 sh 版输出字节 diff 验证 IDENTICAL）+ exit 0；commit message 读取失败回退空串（同 `cat 2>/dev/null || true`）
- pre-push-gate.py：`AGATE_ALIGNMENT_REVIEW_THRESHOLD` 关键字保留（默认 20，env 覆盖；非数字回退 20——提示型永不阻断，sh 的 `-gt` 硬失败场景降级为不中断）；stdin 逐行 split（local_ref/local_sha/remote_ref/remote_sha 4 字段）→ `local_sha` 空跳过 → `remote_sha`=40 个 0 → 新分支提示 → 否则 `git diff <remote>..<local> -- 'agate/*.md'` 统计首字符 `+`/`-` 行数（含 `--- a/` / `+++ b/` 头行，与 `grep -cE '^[+-]'` 一致，sh/py 实测同为 22）→ 超阈值 3 行提示（stdout）+ exit 0
- install-hook.py：AGATE_ROOT 优先级保持 sh 原语义 **argv[1] > env AGATE_ROOT > ~/.agate**（**不用 `resolve_agate_root`**——其 env 优先 + 脚本路径上溯语义与「默认 ~/.agate 稳定版」契约不同，见偏离点）；`git rev-parse --show-toplevel` 失败 → 「不在 git 仓库中」stderr + exit 1；`_ln_sf` 复刻 `ln -sf`（先 unlink 既有再 symlink；OSError → `shutil.copyfile` 退化为复制模式）→ `os.path.islink` 判定（同 sh `[ -L ]`）；pre-commit 复制模式写 `.agate-root` 兜底标记（仅 pre-commit，同 sh）；`_backup`（`shutil.copyfile` 到 `.bak.{int(time.time())}`，仅非软链既有 hook）；`_chmod_x`（既有 mode `| 0o111` 追加执行位，Windows 失败忽略）；`.gitignore` 检测（`^\s*[*]*\.state\.yaml` 逐行 match → 3 行 WARNING + 空行，stdout）

### 引用面核查（确认本次无需改动）

- `tests/unit/commit-msg-self-gate.bats` / `tests/unit/install-hook.bats` / `tests/integration/pre-push-hook.bats` / `tests/integration/commit-msg-self-gate.bats` / `protocol-alignment-review.bats`：当前仍调用 `.sh`（`.sh` 保留可跑），调用点改 `.py` 属后续薄壳批次（3d）+ 测试改造，不在本批范围
- `install-hook.sh` 消息正文写「重跑 install-hook.sh」（复制模式提示）——install-hook.py 原样保留该文本（.sh 薄壳化后用户仍以 `install-hook.sh` 名调用，语义保持）

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `py_compile`：3 个新 py 均编译通过
- 手动功能核对（临时 git repo + monkeypatch，非 bats）：
  - commit-msg-self-gate.py：非 agate 触发面 → exit 0 无输出；缺参 → 用法错误 exit 1；agate/scripts/*.py / *.sh / agate/*.md 触发 → 6 行 WARNING 写 stderr + exit 0（**与 sh 版输出字节 diff IDENTICAL**）；`self-gate-review:` / `self-gate-skip:` 命中 → 无输出 exit 0
  - pre-push-gate.py：新分支（ZERO_SHA）→ 「新分支」提示 + exit 0；无 agate/*.md 改动 → 无输出 exit 0；8→12 行改动 threshold=2 → 3 行 WARNING + exit 0（改动行数 22 与 sh `grep -cE '^[+-]'` 实测一致）
  - install-hook.py：正常安装 → pre-commit/commit-msg/pre-push 三个软链指向 .sh（readlink 验证）；既有非软链 pre-push → `.bak.{epoch}` 备份 + 替换软链；monkeypatch `os.symlink` 抛 OSError（模拟 Windows 无符号链接权限）→ 复制模式 + `.agate-root` 标记 + 「复制模式」提示 + exit 0；非 git 仓库 → 「不在 git 仓库中」+ exit 1；AGATE_ROOT 缺 pre-commit 源 → 错误 + exit 1；缺 commit-msg 源 → 「跳过 commit-msg hook 安装」提示 + 继续 + exit 0；`.gitignore` 忽略 `.state.yaml` → 3 行 WARNING

## 偏离点

[DEVIATION: 三个新 py 的 `run_git` 均带本地 subprocess 降级（`except (ImportError, SystemExit)`）——agate_common 缺 pyyaml 时其模块顶部 `sys.exit(1)` 是 **SystemExit**（`Exception` 捕获不到，批次 3a pre-commit-gate.py 注释已指明该行为），若不捕获会让 **WARNING-only 的 commit-msg-self-gate / pre-push-gate 从"提示型"退化为阻断型**（exit 1）。本批降级为本地实现以保持「永不拦截」契约（对比 pre-commit-gate.py：阻断型 gate 才 fail-closed）。公共库可用时仍走 `agate_common.run_git`（公共库 import 复用成立）]

[DEVIATION: install-hook.py 的 AGATE_ROOT 解析**不用** `agate_common.resolve_agate_root`——安装器语义是「argv[1] > env > ~/.agate 稳定版」（sh 原文 `${1:-${AGATE_ROOT:-$HOME/.agate}}`），而 resolve_agate_root 是「env 优先 → 脚本真实路径上溯」（服务于 hook 软链自定位）。两者契约不同：若用 resolve_agate_root，worktree 场景会把 AGATE_ROOT 解析成 worktree 自身而非 ~/.agate 稳定版，破坏"安装指向稳定版"的设计。逐行保留 sh 语义]

> 实现说明（非 DEVIATION）：pre-push-gate.py 对 `git diff` 改动行计数统计**含** `--- a/` / `+++ b/` 头行（`line[:1] in ("+","-")`）——与 sh `grep -cE '^[+-]'` 语义逐字节一致（grep 也会命中头行），实测 8→12 行场景 sh/py 同为 22。install-hook.py 的 `_ln_sf` 在复制模式下对 commit-msg / pre-push 不写 `.agate-root` 标记（同 sh：标记仅 pre-commit 复制模式写入）。

# P4 实现记录 — 批次 3d（3 个 hook 脚本改写为薄壳）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

把 3 个 hook .sh 覆盖为薄壳（~15 行/个），原逻辑全部删除（py 侧单份维护，不保留双份）。薄壳只做「AGATE_ROOT 自定位 + python 探测 + exec py 主程序 + exec 失败 fail-closed 阻断」。保持 `#!/usr/bin/env bash` + `set -u`（`-euo pipefail` 改为 `-u`——薄壳无管道/命令链，无需 `-e -o pipefail`）。

| 文件 | 行数（404/37/28 → 20/20/21） | exec 目标 |
|------|------|-----------|
| `agate/scripts/pre-commit-gate.sh` | 20 | `pre-commit-gate.py`（错误消息保留 `PROD_TOUCHED` / `PROD_NOT_TOUCHED` 锚点关键字） |
| `agate/scripts/commit-msg-self-gate.sh` | 20 | `commit-msg-self-gate.py`（self-gate 触发面 grep 逻辑在 py 侧） |
| `agate/scripts/pre-push-gate.sh` | 21 | `pre-push-gate.py`（薄壳注释保留 `AGATE_ALIGNMENT_REVIEW_THRESHOLD` 关键字：`# AGATE_ALIGNMENT_REVIEW_THRESHOLD 阈值在 pre-push-gate.py 内维护`） |

- AGATE_ROOT 自定位逐字采用 P2 §3.3 模板（`readlink -f` 解析软链后 dirname 两次取本体根；复制模式 `.agate-root` 标记恢复）
- python 探测 `python3 → python`；exec 失败 → `GATE ERROR` + 提示安装 python3 + pyyaml + `exit 1`（fail-closed，不运行 sh 兜底逻辑）

## 自查结果（自查 ≠ P5 gate）

- 未跑任何 bats（按派发指引，由主 Agent 验证）
- `bash -n`：3 个薄壳均通过语法检查
- 行数核对：pre-commit-gate.sh 20 行 / commit-msg-self-gate.sh 20 行 / pre-push-gate.sh 21 行

## 偏离点

无。

# P4 实现记录 — 批次 3e（修复 2 个因薄壳化过时的 bats 用例）

## implementation_dir

```
implementation_dir: agate/tests/
```

## 本批次改动清单

批次 3d 把 3 个 hook .sh 改写为薄壳后，2 个 bats 用例的 setup/断言仍按「旧 sh 调度版」设计而失败。本批只改这 2 个 bats 文件（不改 py / 薄壳 / 其他文件）：

### 1. `agate/tests/integration/pre-commit-hook.bats` #42（worktree 自定位）

- 删除隔离本体的 `gate-result.sh` 标记文件（薄壳不再 source 它）
- 在 `workflow_root/scripts/` 新增带标记的 `pre-commit-gate.py`（`print("WORKTREE_SOURCED")`），断言软链 hook 输出含 `WORKTREE_SOURCED`——证明薄壳 `readlink -f` 自定位到软链目标的真实目录并 exec 了那里的 py
- 删除已无用的「最小可 gate 场景」（P1 任务 setup）——标记 py 直接输出并 exit 0，不再需要构造 gate-result 加载路径
- 保留 Windows skip 分支（无 POSIX 软链，自定位场景无法验证）

### 2. `agate/tests/unit/dispatch-context-warning.bats` #25（B3-warning）

- fake root 复制改为 py 依赖：`pre-commit-gate.sh`（薄壳入口）+ `pre-commit-gate.py` + `agate_common.py` + 被调用 py 的完整 transitive 闭包（check-state-yaml / check-state-transition / agate-state-get / check-frontmatter / check-p6-format / check-gate / check-p6-provenance / check-pruning / check-scope-resolved / check-retrospective / check-changelog / check-p6-evidence + agate-state-yaml-check / agate-frontmatter-check / agate-md-field-get / agate-gate-missing-cmds / agate-gate-p5-count / agate-vision-blocker / agate-evidence-consistency / agate-image-check / agate-changelog-unreleased / agate-json-get）
- 删除全部 .sh 复制（gate-result.sh / check-*.sh / check-state-yaml.sh 等——薄壳不 source 不调用）
- **不复制 `agate-next-card.py`**（保留 B3 WARNING 路径意图，断言不变：输出含 `dispatch-context`）

## 自查结果（自查 ≠ P5 gate）

- `bats agate/tests/integration/pre-commit-hook.bats`：48/48 绿
- `bats agate/tests/unit/dispatch-context-warning.bats`：1/1 绿

## 偏离点

[DEVIATION: #25 除 fake root 换 py 依赖外，**setup 的 `task_id: T001` 必须改为合法格式 `TAG0001`**（含目录名）——旧 sh 的 `check-state-yaml.sh` 在 fake root 缺 `agate-state-yaml-check.py` 时因 `python3` 报错 → ERRORS 空 → fail-open 放行；py 版 `check-state-yaml.py` 对校验器缺失是 fail-closed（exit 1），且 `T001` 本身就不符合 task_id 格式（T + 2 大写 + 数字），会先在步骤 2a 拦截、根本到不了 2n.1 B3 WARNING。派发指引未预见此点，为让断言可达必须修正 setup]

# P4 实现记录 — 批次 3f（锚点表同步：check-frontmatter 条目改指 py）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

批次 3d 薄壳化 pre-commit-gate.sh 后，CHECK 9 报 1 个 WARNING（`check-frontmatter.sh 未被任何流程文件调用`）。同步 `check-protocol-consistency.py` 的 `SCRIPT_ALIGNMENT_ANCHORS` 里 check-frontmatter 条目，使其指向 py 迁移后的真实路径：

| 字段 | 改前 | 改后 |
|------|------|------|
| `script` | `agate/scripts/check-frontmatter.sh` | `agate/scripts/check-frontmatter.py` |
| `callers` | `agate/scripts/pre-commit-gate.sh` | `agate/scripts/pre-commit-gate.py` |

只改这 1 个条目，其余锚点（check-*.sh 尚在）与逻辑均不动（批次 4 统一同步）。

## 自查结果（自查 ≠ P5 gate）

- `python3 agate/scripts/check-protocol-consistency.py`：0 ERROR、1 WARNING（CHECK9-coverage：`gate 脚本 agate/scripts/check-frontmatter.sh 未纳入 CHECK 9 锚点表`）

## 偏离点

[DEVIATION: 派发指引预期改后回到 0 WARNING，实测为 1 WARNING（CHECK9-coverage）——CHECK9-callers 已修复（pre-commit-gate.py 含 check-frontmatter.py 调用点，grep 确认），但**迁移源 `check-frontmatter.sh` 仍保留在磁盘**（批次 1a 约定「迁移源 .sh 保留，未改动」），反向覆盖扫描（`check_anchor_coverage` 遍历 `check-*.sh`）发现它不再被锚点表覆盖。此为批次 4「统一同步锚点 + 迁移源 .sh 删档」前的已知中间态，按本批次约束（只改 1 个锚点条目、不改逻辑）不处理]

# P4 实现记录 — 批次 4a（consistency 锚点表全面同步）

## implementation_dir

```
implementation_dir: agate/scripts/
```

## 本批次改动清单

批次 0-3 全部 30 脚本 py 化后，`check-protocol-consistency.py` 锚点表仍引用旧 `.sh` 路径。按 P2 §3.5 同步锚点数据（只改路径/关键字列表，不动检查逻辑）：

1. **V06_KEYWORD_ASSERTIONS**（4 条涉 sh → py）：
   - `check-gate.sh` → `check-gate.py`（DESIGN_GAP / --cached 两条）
   - `check-pruning.sh` → `check-pruning.py`（P2 不可裁剪 / --cached 两条）
   - 改动前 grep 确认 py 含关键字：check-gate.py 含 DESIGN_GAP×15 / --cached×6；check-pruning.py 含 P2 不可裁剪×2 / --cached×4
2. **SCRIPT_ALIGNMENT_ANCHORS**（全部 check-*.sh → check-*.py）：check-pruning×6 / check-state-transition×2 / check-gate×6 / check-scope-resolved / check-p6-evidence×4 / check-p6-provenance×3 / check-retrospective / check-changelog / check-state-yaml / check-tdd-red / check-p6-format（含 callers 改指 pre-commit-gate.py）/ check-debt / check-platform-assumptions；**pre-commit-gate.sh / pre-push-gate.sh 两条保留 sh 路径**（薄壳含 PROD_TOUCHED / AGATE_ALIGNMENT_REVIEW_THRESHOLD 关键字，grep 确认）
3. **GATE_SCRIPT_EXEMPT**：移除 gate-result.sh / install-hook.sh / agate-changes.sh / agate-summary.sh / agate-init.sh（全部已 py 化或并入 agate_common.py，stale 清理）；新增 `check-protocol-consistency.py`（自身命中 check-*.py glob 但无锚点 → 必须豁免）+ `pre-commit-gate.py`（调度编排，无单一 gate 判定逻辑）
4. **check_anchor_coverage glob**：`check-*.sh` → `check-*.py`（+ pre-commit-gate.sh + **pre-commit-gate.py** + ci-gate-backstop.py 显式追加）

## 自查结果（自查 ≠ P5 gate）

- `python3 agate/scripts/check-protocol-consistency.py`：**0 ERROR、0 WARNING**
- `python3 agate/scripts/check-protocol-consistency.py --strict`：**0 ERROR、0 WARNING**（exit 0）

## 偏离点

[DEVIATION: 派发指引改动清单 2 仅列路径同步，实测 4 条关键字在 py 迁移中被改名（旧 sh 大写常量 → py 小写/中文等价物），同步改锚点关键字使 CHECK 9 仍可对齐：
- check-pruning.py：`SOURCE_FILE_COUNT`（sh 变量名）→ `源码文件数`（py docstring + 错误消息字面量，grep 命中×2）
- check-p6-evidence.py：`VARIANCE_WARNING` → `variance_warning`（py 局部变量）、`AHASH_LIST`/`AHASH_DUPES` → `ahash_list`/`ahash_dupes`
关键字仍存活在 py 中（P2 原则），仅形态从 sh 大写常量变为 py 标识符；锚点表关键字与 py 实际内容对齐。
另注：check-p6-format 的 callers 从 pre-commit-gate.sh 改指 pre-commit-gate.py（薄壳 sh 不再含 check-p6-format 调用，py 含，CHECK9-callers 判定需真实调用路径）。批次 3f 遗留的 check-frontmatter.sh CHECK9-coverage WARNING 随 glob 改 `check-*.py` 消失（.sh 迁移源不再被反向扫描，符合预期，删档在后续批次）]

---

# P4 实现记录 — 批次 4b（pyproject.toml ruff 规则集 + bdd-34 断言改造）

## implementation_dir

```
implementation_dir: 项目根（pyproject.toml）+ agate/tests/unit/env-adapt-docs.bats
```

## 本批次改动清单

### 1. 新建 `pyproject.toml`（项目根）

按 P2 §3.4 规则集原样落地（ruff 0.16.3 实测生效）：

- `target-version = "py38"`（BDD-8：ruff 拒绝 3.10+ 语法）
- `line-length = 120`
- `src = ["agate/scripts"]`
- `select`：E4/E7/E9/F/W/I/UP/B/SIM/C4/RUF/PLW
- `ignore`：BLE001（fail-closed 宽捕获有意）/ PLW1510（显式捕获 returncode）/ SIM115（一次性 read）/ RUF001-003（Unicode 混淆，中文注释误报）

### 2. 改造 `agate/tests/unit/env-adapt-docs.bats` bdd-34（P2 §3.6 断言级）

原断言（shellcheck `-S warning *.sh` 0 error）改为两块，探测不可用即跳过：

1. **shellcheck 覆盖面收敛到 3 hook 薄壳**：`shellcheck -S warning pre-commit-gate.sh commit-msg-self-gate.sh pre-push-gate.sh`（仍探测 `command -v shellcheck|shellcheck.exe`，不可用 skip）
2. **新增 ruff 断言**：`ruff check agate/scripts/`（从项目根执行，探测 `command -v ruff`，不可用 skip）

实现为单 @test 内两段独立探测 + 运行；两者均不可用时 skip。测试用例数保持 9 不漂移（count-tests.sh 口径）。

### 3. ruff 违规修复（P2 §3.4 边界内，行为保持）

首次 `ruff check agate/scripts/` 报 **327 error**（47 个 py 均有涉及，UP032 f-string ×~180 为主），全部在 P2 §3.4 边界内处理：

- **`--fix` 自动修 261 处**：UP032 f-string 化 / F401 未用 import / F541 空 f-string / I001 import 排序 / W291 行尾空格 / W292 文件尾换行 / UP031 percent→format / UP015 / SIM905 / SIM114 / C401 set comprehension
- **`--fix --unsafe-fixes` 再修 52 处**：SIM102 嵌套 if 折叠 / SIM103 return 条件直接 / SIM105 contextlib.suppress / SIM108 三元 / SIM110 any() / SIM201 / RUF005 列表拼接→展开
- **手工极小调整 14 处**（--unsafe-fixes 未覆盖，行为保持）：
  - PLW2901 ×6：`for line/ref` 循环体覆写 → 循环变量改名 `raw_line`/`raw_ref`，覆写仍落到 `line`/`ref`
  - SIM102 ×4：含注释/多语句的嵌套 if → `and` 合并（注释保留）
  - E741 ×3：`l` 歧义变量名 → `ln`
  - F841 ×1：pre-commit-gate.py 未用的 `agate_root = resolve_agate_root(...)` → 裸调用（grep 确认无其他引用）
  - RUF059 ×2：未用解包 `rc_diff`/`ci_output` → `_rc_diff`/`_ci_output`

## 自查结果（自查 ≠ P5 gate）

- `ruff check agate/scripts/`：**All checks passed**（exit 0，pyproject.toml 生效）
- `shellcheck -S warning pre-commit-gate.sh commit-msg-self-gate.sh pre-push-gate.sh`：**0 error**
- `bats agate/tests/unit/env-adapt-docs.bats`：**9/9 绿**（含改造后 bdd-34；PATH 含 ruff 时 ruff 断言实际执行）
- `grep -c "^@test" env-adapt-docs.bats`：9（用例数不漂移）

## 偏离点

[DEVIATION: 派发指引「本机 ~/.venvs/agate-dev/ 有 ruff，可设 PATH 或直接用命令」——该 venv 不在默认 PATH（`command -v ruff` 为空），bats 的 bdd-34 在默认 PATH 下会跳过 ruff 断言（shellcheck 段仍执行）。ruff 断言需 PATH 含 ruff 才实际运行（P5 gate 的 `P5_ruff` 命令同样依赖 PATH 配置）。已用 `PATH=~/.venvs/agate-dev/bin:$PATH` 验证 ruff 断言真执行且通过，非"跳过即绿"的假阳性]

---

# P4 实现记录 — 批次 4b 后半（SG.6 断言过时修复）

## implementation_dir

```
implementation_dir: agate/tests/integration/protocol-alignment-review.bats
```

## 本批次改动清单

批次 4a 把 `check-protocol-consistency.py` CHECK 9 锚点表全部改为 `check-*.py` 后，`integration/protocol-alignment-review.bats` SG.6 测试仍用 `find "$AGATE_SCRIPTS" -name 'check-*.sh' -o -name 'pre-commit-gate.sh'` 收集脚本清单——找到 check-changelog.sh（迁移源仍在）但锚点表里是 check-changelog.py → grep 失败，SG.6 红。

修改（仅 SG.6 一个用例，`@test` 数不变）：

1. `find` 匹配改为 `-name 'check-*.py' -o -name 'pre-commit-gate.sh' -o -name 'pre-commit-gate.py'`——与批次 4a `check_anchor_coverage` glob（`check-*.py` + pre-commit-gate.sh + pre-commit-gate.py）对齐，其中 pre-commit-gate.sh 薄壳作为命中锚点保留项、pre-commit-gate.py 为调度编排豁免项
2. 注释同步为「仓库中所有 check-*.py + pre-commit-gate.sh 薄壳」

## 自查结果（自查 ≠ P5 gate）

- `bats agate/tests/integration/protocol-alignment-review.bats`：**8/8 绿**（含修复后 SG.6）
- `grep -c "@test"` 不变（8 用例）

## 偏离点

> 无 DEVIATION / DESIGN_GAP。SG.7 的 commit-msg-self-gate.sh 断言不受影响（该脚本作为 3 个 hook 薄壳之一保留 sh，本次仅对 SH/check-*.py 匹配）。
