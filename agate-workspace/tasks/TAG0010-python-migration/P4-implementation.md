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
