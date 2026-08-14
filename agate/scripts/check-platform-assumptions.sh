#!/usr/bin/env bash
# check-platform-assumptions.sh — 平台假设静态扫描器（TAG0009 BDD-1~9）
#
# 扫描测试代码（agate/tests/ 全树）中的 Unix 平台假设，CI 接入阻断新假设。
# 自身仅用 POSIX 工具与 POSIX ERE（禁用 GNU 专用 grep 正则扩展特性），
# Linux 与 MSYS2 双平台行为一致（BDD-1）。
#
# 用法：check-platform-assumptions.sh [target...]
#   target 为文件或目录；目录 target 递归扫描 *.bats / *.bash / *.sh（扩展名过滤）
#   无参数时默认扫描 agate/tests/
#
# 规则：
#   R1 硬编码 PATH（/usr 或 /bin 字面赋值）
#   R2 命令位置裸 python3（豁免 command -v 探测 / env 形式 / shebang / @test 标题 / 注释行）
#   R3 方括号形式 -L 单平台 symlink 断言（[[ -L ... ]] 或 [ -L ... ]）
#   R4 临时目录字面量（豁免 BATS_TEST_TMPDIR 变量名与含 "# scan-exempt:" 标记的行）
#   R5 命令位置裸外部工具（bc 已登记；模式集可扩充 seq/timeout 等）
#
# 输出：命中行形如 `R{n} <file>:<line> <摘要>`（含规则号与命中文件路径）；无命中无输出
# 退出：0 = 无命中；1 = 有命中

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_TARGET="$(cd "$SCRIPT_DIR/.." && pwd)/tests"

# ---- 规则模式集（POSIX ERE） ----
R1_RE='PATH=[^[:space:]]*(/usr|/bin)'
R2_RE="(^|[[:space:]]|[=(\"'])python3([[:space:]]|\$)"
R3_RE='(^|[[:space:]])[[]+[[:space:]]+-L[[:space:]]'
R4_RE="/tmp([[:space:]]|/|\"|'|\$)"
R5_RE="(^|[[:space:]]|[=|(])bc([[:space:]]|\$|[|])"

hits=0

report() {
    local rule="$1" file="$2" line_no="$3" text="$4"
    printf '%s %s:%s %s\n' "$rule" "$file" "$line_no" "$text" >&2
    hits=$((hits + 1))
}

# R2 豁免判定：注释/shebang 行、@test 标题行、command -v 探测形态、env python3 形式
r2_exempt() {
    local line="$1"
    local trimmed
    trimmed="$(printf '%s' "$line" | sed 's/^[[:space:]]*//')"
    case "$trimmed" in
        '#'* | '@test'*) return 0 ;;
    esac
    case "$line" in
        *'command -v python3'* | *'command -v python'*) return 0 ;;
        *'env python3'*) return 0 ;;
    esac
    return 1
}

# 按规则对单个文件跑一次 grep -nE，逐命中做行级豁免判定
scan_rule() {
    local rule="$1" re="$2" file="$3" exempt_rule="$4"
    local matched=""
    matched="$(grep -nE "$re" "$file" 2>/dev/null || true)"
    [ -n "$matched" ] || return 0
    local line_no="" text=""
    while IFS= read -r hit || [ -n "$hit" ]; do
        line_no="${hit%%:*}"
        text="${hit#*:}"
        if [ "$exempt_rule" = "r2" ] && r2_exempt "$text"; then
            continue
        fi
        if [ "$exempt_rule" = "r4" ] && printf '%s\n' "$text" | grep -q '# scan-exempt:'; then
            continue
        fi
        report "$rule" "$file" "$line_no" "$text"
    done <<< "$matched"
}

scan_file() {
    local file="$1"
    scan_rule R1 "$R1_RE" "$file" none
    scan_rule R2 "$R2_RE" "$file" r2
    scan_rule R3 "$R3_RE" "$file" none
    scan_rule R4 "$R4_RE" "$file" r4
    scan_rule R5 "$R5_RE" "$file" none
}

scan_target() {
    local target="$1"
    if [ -d "$target" ]; then
        local file=""
        while IFS= read -r file || [ -n "$file" ]; do
            [ -n "$file" ] && scan_file "$file"
        done < <(find "$target" -type f \( -name '*.bats' -o -name '*.bash' -o -name '*.sh' \) 2>/dev/null)
    elif [ -f "$target" ]; then
        scan_file "$target"
    else
        printf 'FATAL: 目标不存在: %s\n' "$target" >&2
        exit 2
    fi
}

targets=("$@")
if [ "${#targets[@]}" -eq 0 ]; then
    targets=("$DEFAULT_TARGET")
fi

for target in "${targets[@]}"; do
    scan_target "$target"
done

if [ "$hits" -gt 0 ]; then
    exit 1
fi
exit 0
