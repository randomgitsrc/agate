---
phase: P4
task_id: TAG0010-python-migration
agent: reviewer-batch0
type: review
parent: P4-implementation.md
status: approved
---

# P4-review — 批次 0（公共库 agate_common.py）实现评审

## 结论

**approved** — agate_common.py 与迁移源（gate-result.sh / agate-workspace-resolve.sh）契约等价性经逐函数核对 + 针对性行为验证通过，无 BLOCKER。

## 评审范围与方法

- 对象：`agate/scripts/agate_common.py`、`ci-gate-backstop.py` 的 resolve_tasks_dir 改动、3 个 bats 调用点改动
- 方法：逐函数对照 sh 迁移源核对 + 在临时 git 仓库做行为验证（resolve_workspace 6 场景 parity、write_gate_result 结构、run_test_with_formatter 6 场景、resolve_formatter 优先级、read_state 缺省、has_staged_phase_change/output 等价性）、py_compile 通过
- 未重跑全量 bats（P5 职责）

## 契约等价性核对结果

| 函数 | 核对结果 |
|------|---------|
| `write_gate_result` | ✓ .gate-result.json 7 字段 + 缩进结构与 sh 完全一致；output 用 json.dumps（≡ agate-json-get.py escape）；history 5 字段紧凑行一致；prev_commit_sha 失败回退 "pre-commit" |
| `read_state_phase/task_id` | ✓ 文件不存在/解析失败返回 ""（≡ sh `|| echo ""`） |
| `has_staged_phase_change` | ✓ 逻辑等价（见非阻塞意见 B1） |
| `has_staged_phase_output` | ✓ 正则一致 |
| `resolve_formatter` | ✓ 优先级 绝对→task_dir/.agate/formatters→agate_root/assets/formatters，缺失 None（≡ sh exit 1） |
| `run_test_with_formatter` | ✓ exit_code/124 超时/2>&1 合并/raw_output 回退/formatter 子进程，全场景行为验证通过；超时 JSON 7 键与 fallback JSON 9 键均与 sh 一致 |
| `resolve_workspace` | ✓ 6 场景（默认/相对含空格/绝对/CRLF 最后一条胜/env AGATE_TASKS_DIR/无参默认 cwd）与 sh 输出逐字节一致 |
| `resolve_agate_root` | ✓ env 优先 → readlink 解析 → 复制模式 .agate-root 标记恢复（CRLF 剥离），与设计 §3.3 薄壳语义一致 |
| `probe_python` | ✓ python3→python 顺序，返回解析路径，无 python 返回 None（fail-closed 由调用方承担） |

## 关注点核查

- **Python 3.8+**：无 match / str.removeprefix / walrus / 3.9+ 类型语法；无类型注解（ci-gate-backstop 的 `str | None` 为既有代码，不在本批改动）；全部文件读写显式 `encoding="utf-8"` ✓
- **Windows**：无 /tmp、无 POSIX symlink 硬依赖（resolve_agate_root 复制模式回退齐全）；run_git errors="replace" 兼容非 UTF-8 文件名 ✓
- **pyyaml fail-closed**：模块顶部 try/except ImportError → stderr + exit 1，与 agate-state-get.py L18-21 同模式 ✓
- **ci-gate-backstop 回退语义**：`import agate_common` 的 ImportError（旧 AGATE_ROOT 无此模块 → ModuleNotFoundError ⊂ ImportError）→ 退回 env/default，与旧 fallback 一致；且消除了对 bash 解析器的 subprocess 依赖 ✓
- **DESIGN_GAP（7 vs 6 字段）**：实现按 sh 实际 7 字段保留并在 P4-implementation.md 如实声明——判定对象是 sh 现状（CI 契约），选择正确

## 非阻塞意见

- **B1（has_staged_phase_change 精确匹配 vs sh 子串 grep）**：py 用 `basename in staged`（整行相等），sh 用 `grep -qF "$basename"`（子串）。已证明两者布尔结果逻辑等价（第二段 basename-only diff 存在非空 ⇒ 恰好同名路径被暂存 ⇒ 精确匹配同样成立），且该函数当前无 py 调用方（批次 2/3 才接入）。无需修改。
- **B2（resolve_formatter 默认 agate_root 不读 AGATE_ROOT env）**：sh 默认 `AGATE_ROOT` env 优先，py 默认用模块常量 `_AGATE_ROOT`。符号链接模式下两者重合，复制模式 + AGATE_ROOT env 场景会发散。建议批次 2/3 的 py 调用方显式传 `agate_root`，或让默认值优先读 `os.environ.get("AGATE_ROOT")`。
- **B3（run_test_with_formatter 对 bash 缺失未兜底）**：`executable="bash"` 在 bash 不在 PATH 时抛 FileNotFoundError（未捕获），sh 侧会得 exit 127 走 fallback JSON。当前无 py 调用方、gate 环境必然有 bash，建议后续批次补 `except OSError` 走 fallback。
- **B4（_read_state 对非 dict YAML 会 AttributeError）**：`.state.yaml` 若解析出非 mapping（如顶层标量），`data.get(...)` 崩溃；sh 侧被 `2>/dev/null || echo ""` 掩盖。受 check-state-yaml 约束实际不会出现，仅记录。

## 参考资料

- 评审焦点与范围：P4-dispatch-context-review.md
- 设计基准：P2-design.md §3.1
- 实现自述：P4-implementation.md（DESIGN_GAP 已如实声明）
