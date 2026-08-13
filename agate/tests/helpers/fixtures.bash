#!/usr/bin/env bash
# tests/helpers/fixtures.bash — 任务目录夹具构造
# 用法：create_task_dir [phases...] [options...]

# detect_python — 探测可用的 python 解释器（优先 python3，回退 python）
# 平台无关：command -v 探测形态命中扫描器 R2 豁免集（check-platform-assumptions）
detect_python() {
    command -v python3 2>/dev/null || command -v python 2>/dev/null \
        || { echo "FATAL: 找不到 python3/python 解释器" >&2; return 1; }
}
export PYTHON="$(detect_python 2>/dev/null || true)"

# SHELLCHECK — 工具名平台差异探测（Windows 下为 shellcheck.exe，BDD-25）
# 与 PYTHON 同模式：调用方用 ${SHELLCHECK:-shellcheck} 兜底（bdd-34 断言）
export SHELLCHECK="$(command -v shellcheck 2>/dev/null || command -v shellcheck.exe 2>/dev/null || true)"

# create_python_shim_bin [--force] — 建临时 bin 目录 + python3 包装器指向真解释器（BDD-16/17）
# 产品脚本内部裸 python3 在"仅 python 可解析"环境（Windows）下由 shim 兜底解析。
# 返回 bin 路径；调用方 setup() 前置到 PATH。
# 默认：python3 已在 PATH 上原生可解析时返回空串（不遮蔽原生 python3，防 Windows/Linux
# 双平台回归——Windows runner setup-python 已提供 python3 时 shim 纯属多余且 wrapper
# 可能因 MSYS/Windows 路径形式差异 exec 失败）。--force 时无条件创建（供 helpers-python
# 机制测试显式构造"仅 python"环境，BDD-17）。
# 包装器在运行时用 command -v 重新解析真解释器（排除 shim 自身目录，避免自解析循环）。
create_python_shim_bin() {
    local force=0
    if [ "${1:-}" = "--force" ]; then
        force=1
    fi
    if [ "$force" -eq 0 ] && command -v python3 >/dev/null 2>&1; then
        echo ""
        return 0
    fi
    local shim_bin
    shim_bin=$(mktemp -d "$BATS_TEST_TMPDIR/shim-bin-XXXXXX")
    cat > "$shim_bin/python3" <<'EOF'
#!/usr/bin/env bash
# python3 shim 包装器（TAG0009）：运行时解析真解释器，排除 shim 自身目录与测试临时根
# 避免自解析循环/被测试 stub 遮蔽（fakebin 是 BATS_TEST_TMPDIR 下同级目录）
SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLEAN_PATH="$(printf '%s' "$PATH" | tr ':' '\n' | grep -vF "$SELF_DIR" | grep -vF "${BATS_TEST_TMPDIR:-__none__}" | paste -sd:)"
REAL_PY="$(PATH="$CLEAN_PATH" command -v python3 2>/dev/null || PATH="$CLEAN_PATH" command -v python 2>/dev/null)"
if [ -z "$REAL_PY" ]; then
    echo "shim: 找不到 python3/python 解释器" >&2
    exit 127
fi
exec "$REAL_PY" "$@"
EOF
    chmod +x "$shim_bin/python3"
    echo "$shim_bin"
}
#   phases: P0 P1 P2 ... 默认全开
#   选项：
#     --risk-level low|medium|high
#     --with-evidence    添加 P6-evidence/ 空目录
#     --state-yaml       同时写 .state.yaml（默认仅 P0-P8 文件）
#   返回：临时目录路径
#
# 例：
#   dir=$(create_task_dir P0 P1 P3 P4 P5 P6 P7 P8 --risk-level low)

# add_agent_field <file>
# 给 .md 文件加 YAML frontmatter agent: test（如果没有）
add_agent_field() {
    local f="$1"
    if [ -f "$f" ] && ! head -3 "$f" | grep -q '^---$'; then
        local tmp
        tmp=$(mktemp)
        printf -- '---\nagent: test\n---\n\n' > "$tmp"
        cat "$f" >> "$tmp"
        mv "$tmp" "$f"
    fi
}

# add_given_line <file>
# 在 P1 加一个 Given 行（如果还没有）
# 已废弃（v0.20.0 BDD 标准化后无调用者）：Given 行不再计入 BDD 计数，
# 保留代码但不再使用，避免破坏可能存在的下游 fork。新测试请用 add_p1_bdd。
add_given_line() {
    local f="$1"
    if ! grep -qE '^\s*-\s*Given\b' "$f" 2>/dev/null; then
        echo "- Given test precondition" >> "$f"
    fi
}

# add_frontmatter_field <file> <field> <value>
# v2.0（T001 流 A）：在文件的 frontmatter 块（--- ... ---）内插入/更新一个顶层 key。
# 无 frontmatter 块时新建一个（只含该字段）；已有块则在块内替换同名 key 或追加到块尾。
# 供 add_p1_field / add_p2_candidate_count 等 helper 复用，是 fixture 从"正文字段"
# 迁移到"frontmatter 字段"的唯一写入路径（P2-design.md §3.1.5）。
add_frontmatter_field() {
    local file="$1"
    local field="$2"
    local value="$3"

    if [ ! -f "$file" ]; then
        printf -- '---\n%s: %s\n---\n' "$field" "$value" > "$file"
        return
    fi

    if [ "$(sed -n '1p' "$file")" = "---" ]; then
        local end_line
        end_line=$(awk 'NR>1 && /^---$/{print NR; exit}' "$file")
        if [ -n "$end_line" ] && [ "$end_line" -gt 1 ]; then
            if sed -n "2,$((end_line - 1))p" "$file" | grep -q "^${field}:"; then
                sed -i "2,$((end_line - 1))s|^${field}:.*|${field}: ${value}|" "$file"
            else
                sed -i "${end_line}i ${field}: ${value}" "$file"
            fi
            return
        fi
    fi

    # 无合法 frontmatter 块（或块未闭合）→ 在文件头新建一个
    local tmp
    tmp=$(mktemp)
    { printf -- '---\n%s: %s\n---\n' "$field" "$value"; cat "$file"; } > "$tmp"
    mv "$tmp" "$file"
}

create_task_dir() {
    local phases="${@:-P0 P1 P2 P3 P4 P5 P6 P7 P8}"
    local risk_level="medium"
    local with_evidence=0
    local with_state=1
    local legacy_fields=0

    # 解析选项
    local args=()
    while [ $# -gt 0 ]; do
        case "$1" in
            --risk-level)
                risk_level="$2"
                shift 2
                ;;
            --with-evidence)
                with_evidence=1
                shift
                ;;
            --no-state-yaml)
                with_state=0
                shift
                ;;
            --legacy-fields)
                # v0.35 旧格式（BDD-9 回退测试用）：risk_level/phases 写在正文而非 frontmatter
                legacy_fields=1
                shift
                ;;
            --*)
                echo "FATAL: 未知选项 $1" >&2
                return 1
                ;;
            *)
                args+=("$1")
                shift
                ;;
        esac
    done
    phases="${args[@]:-P0 P1 P2 P3 P4 P5 P6 P7 P8}"

    local dir
    dir=$(mktemp -d "$BATS_TEST_TMPDIR/task-XXXXXX")

    # 写 .state.yaml
    if [ "$with_state" -eq 1 ]; then
        # phase 数值 = 第一个非空 phases（如 P0 → 0, P1 → 1）
        local first_phase="P1"
        for p in $phases; do
            first_phase="$p"
            break
        done
        cat > "$dir/.state.yaml" <<EOF
task_id: T001
phase: $first_phase
status: active
retries: {}
EOF
    fi

    # 写 P0-brief.md
    cat > "$dir/P0-brief.md" <<EOF
task: "test task"
known_risks: []
executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
env_constraints:
  debug_env: "echo debug"
EOF

    # 写 P1-requirements.md（带 risk_level + phases + agent frontmatter + Given 默认行）
    # v2.0（T001 流 A，BDD-1）默认把 risk_level/phases 并入 frontmatter 块；
    # --legacy-fields 保留 v0.35 正文写法（BDD-9 双读回退测试专用）
    local phases_csv
    phases_csv=$(echo "$phases" | tr ' ' ',')
    if [ "$legacy_fields" -eq 1 ]; then
        cat > "$dir/P1-requirements.md" <<EOF
---
agent: test
---
risk_level: $risk_level
phases: [$phases_csv]

### 主流程

#### BDD-1: test
- Given test precondition
- When test action
- Then test result
EOF
    else
        cat > "$dir/P1-requirements.md" <<EOF
---
agent: test
risk_level: $risk_level
phases: [$phases_csv]
---

### 主流程

#### BDD-1: test
- Given test precondition
- When test action
- Then test result
EOF
    fi

    # 写其他阶段文件（空文件，足以让脚本"不报缺文件"）
    for p in $phases; do
        case "$p" in
            P2) touch "$dir/P2-design.md" ;;
            P3) touch "$dir/P3-test-design.md" ;;
            P4) touch "$dir/P4-implementation.md" ;;
            P5) touch "$dir/P5-verification.md" ;;
            P6) cat > "$dir/P6-acceptance.md" <<'EOF'
---
agent: test
---
EOF
               ;;
            P7) touch "$dir/P7-consistency.md" ;;
            P8) touch "$dir/P8-release.md" ;;
        esac
    done

    # 给所有 P*.md 加 agent frontmatter（v0.6 provenance 要求）
    for f in "$dir"/P[1-8]-*.md; do
        [ -f "$f" ] || continue
        # 跳过已有 frontmatter 的
        head -3 "$f" | grep -q '^---$' && continue
        tmp=$(mktemp)
        printf -- '---\nagent: test\n---\n\n' > "$tmp"
        cat "$f" >> "$tmp"
        mv "$tmp" "$f"
    done

    # 写 P6-evidence/ 空目录
    if [ "$with_evidence" -eq 1 ]; then
        mkdir -p "$dir/P6-evidence"
    fi

    echo "$dir"
}

# 用法：add_pruning_excuse <task_dir> <phase> <reason> <risk>
# 声明裁剪某阶段 + 写裁剪理由 + 跳过风险
add_pruning_excuse() {
    local dir="$1"
    local phase="$2"
    local reason="$3"
    local risk="$4"
    local p1="$dir/P1-requirements.md"

    # 在 phases 行去掉该 phase
    sed -i "s/$phase,//g; s/,$phase//g; s/$phase//g" "$p1"

    # 加裁剪理由 + 跳过风险
    cat >> "$p1" <<EOF

裁剪 ${phase}: ${reason}
跳过风险: ${risk}
EOF
}

# 用法：add_p1_field <task_dir> <field> <value>
# 在 P1-requirements.md 的 frontmatter 块加/改 YAML 顶层字段（v2.0 T001 流 A，BDD-1）。
# v0.35 时代本 helper 写正文；改造后写 frontmatter（P2-design.md §3.1.5 明确要求）。
add_p1_field() {
    local dir="$1"
    local field="$2"
    local value="$3"
    add_frontmatter_field "$dir/P1-requirements.md" "$field" "$value"
}

# 用法：add_p2_review <task_dir> [status] [agent]
# 创建一个合规的 P2-review.md（status: approved, agent: reviewer-subagent）
# 用于 P2 gate 测试中需要 P2-review.md 存在的场景
add_p2_review() {
    local dir="$1"
    local status="${2:-approved}"
    local agent="${3:-reviewer-subagent}"
    cat > "$dir/P2-review.md" <<EOF
---
status: ${status}
agent: ${agent}
---
P2 review approved.
EOF
}

# 用法：add_evidence_file <task_dir> <rel_path> <content> [size]
# 在 P6-evidence/ 放文件，可指定大小（用于空 png 测试）
add_evidence_file() {
    local dir="$1"
    local rel_path="$2"
    local content="$3"
    local size="${4:-}"
    local full_path="$dir/P6-evidence/$rel_path"

    mkdir -p "$(dirname "$full_path")"
    if [ -n "$size" ]; then
        # 创建指定大小的文件
        head -c "$size" /dev/urandom | base64 | head -c "$size" > "$full_path"
    else
        printf '%s' "$content" > "$full_path"
    fi
}

# 用法：add_p6_pass <task_dir> <bdd_id> <evidence_ref>
# 在 P6-acceptance.md 加一条 PASS
add_p6_pass() {
    local dir="$1"
    local bdd_id="$2"
    local evidence_ref="$3"
    local p6="$dir/P6-acceptance.md"

    echo "- PASS ${bdd_id} (${evidence_ref})" >> "$p6"
}

# 用法：add_p6_fail <task_dir> <bdd_id> [evidence_ref]
# 在 P6-acceptance.md 加一条 FAIL
add_p6_fail() {
    local dir="$1"
    local bdd_id="$2"
    local evidence_ref="${3:-}"
    local p6="$dir/P6-acceptance.md"

    if [ -n "$evidence_ref" ]; then
        echo "- FAIL ${bdd_id} (${evidence_ref})" >> "$p6"
    else
        echo "- FAIL ${bdd_id}" >> "$p6"
    fi
}

# 用法：add_p6_need_confirm <task_dir> <bdd_id>
add_p6_need_confirm() {
    local dir="$1"
    local bdd_id="$2"
    local p6="$dir/P6-acceptance.md"

    echo "- NEED_CONFIRM ${bdd_id}" >> "$p6"
}

# 用法：add_p1_given <task_dir> <text>
# 在 P1-requirements.md 加一行 BDD Given
# 已废弃（v0.20.0 BDD 标准化后无调用者）：Given 行不再计入 BDD 计数，
# 保留代码但不再使用，避免破坏可能存在的下游 fork。新测试请用 add_p1_bdd。
add_p1_given() {
    local dir="$1"
    local text="$2"
    local p1="$dir/P1-requirements.md"

    echo "- Given ${text}" >> "$p1"
}

# 用法：add_p1_bdd <task_dir> [description]
# 在 P1-requirements.md 末尾追加一个 `#### BDD-NN:` 标题行（仅标题，不含 GWT 子行——
# GWT 由调用方自行追加）。NN 为当前最大编号 +1，若无已有 BDD 则从 1 开始。
add_p1_bdd() {
    local dir="$1"
    local desc="${2:-test}"
    local p1="$dir/P1-requirements.md"
    local n
    n=$(grep -cE '^#### BDD-[0-9]' "$p1" 2>/dev/null || echo 0)
    n=$(echo "$n" | tail -1)
    n=$((n + 1))
    echo "#### BDD-${n}: ${desc}" >> "$p1"
}

# 用法：add_p2_candidate_count <task_dir> <count>
# 在 P2-design.md 的 frontmatter 块加/改 candidate_count 字段（v2.0 T001 流 A，BDD-1）。
# 调用方多用 `cat > P2-design.md <<EOF ... EOF` 先整体覆写正文（无 frontmatter），
# 此时 add_frontmatter_field 会在文件头新建一个只含 candidate_count 的 frontmatter 块。
add_p2_candidate_count() {
    local dir="$1"
    local count="$2"
    add_frontmatter_field "$dir/P2-design.md" "candidate_count" "$count"
}
