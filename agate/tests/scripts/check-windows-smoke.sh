#!/usr/bin/env bash
# tests/scripts/check-windows-smoke.sh — Windows bats 冒烟子集验证（TAG0009 v0.45 决策）
#
# 背景：Windows runner 上跑全量 bats（747 用例）约 11.5 分钟，且随测试增长线性上升，
#       阻塞 CI。v0.45 起 Windows bats 从"全量功能验证"降级为"技术路线冒烟"：
#       —— 功能正确性由 Linux 全量 bats 保证（不降级）；
#       —— Windows 只验证每条平台敏感机制至少一个代表用例跑通，证明该技术路线
#          （py_path 转换 / python3 shim / cp1252 编码 / CRLF 行尾 / symlink 复制模式 /
#          盘符路径 / 绝对 bash / 无bc / subprocess 编码等）在 Windows 成立。
#          若某技术路线在 Windows 通过，其余共享同机制（helper/shim/setup）的同类用例
#          应同样通过——差异只是执行时间长短。
#
# 代表选取规则（机械、无人工维护清单，规则即定义）：
#   1. 每个 .bats 文件取第 1 个用例：保证每个文件的 setup / helper 加载在 Windows 可用
#   2. 每个文件中名称含平台敏感关键词的用例：保证每条平台敏感机制有 Windows 代表
#
# 用法：
#   bash check-windows-smoke.sh [--list]   # --list 只打印代表清单（file<TAB>用例列表）不执行
#   环境变量：BATS_BIN（默认 bats）覆盖 bats 命令（测试 mock 用）
#
# 平台无关约束（本脚本会被 check-platform-assumptions.sh 扫描 agate/tests/ 全树）：
#   不使用 tmp 目录字面量、裸 python3、方括号 -L、硬编码 PATH、裸bc。
#   mktemp 依赖系统 TMPDIR，不写死 Unix-only 路径。

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BATS_BIN="${BATS_BIN:-bats}"
PROG="$(basename "$0")"

# 平台敏感关键词：@test 名称含任一关键词即被选为代表（技术路线标记）
PLATFORM_KEYWORDS_RE='cp1252|CRLF|Windows|win32|symlink|MSYS|py_path|PYTHONIOENCODING|盘符|编码|绝对 bash|复制模式|platform|平台|无bc|无 python3|shim|subprocess|ln 退化|ln 复制'

# 把测试名转义成可安全嵌入正则的片段（bats --filter 用）
escape_regex() {
    printf '%s' "$1" | sed 's#[][\^$.*+?(){}|]#\\&#g'
}

# 收集单个文件的代表用例（第 1 个 + 平台关键词用例，去重），
# 输出一行：file<TAB>escaped1|escaped2|...（用例名已转义、已去重）
collect_file() {
    local file="$1"
    local names name esc cases is_first
    names=$(grep -E '^@test "' "$file" | sed -E 's/^@test "(.*)" \{/\1/')
    [ -n "$names" ] || return 0
    cases=""
    is_first=1
    while IFS= read -r name; do
        [ -n "$name" ] || continue
        if [ "$is_first" -eq 1 ]; then
            is_first=0
        elif ! printf '%s\n' "$name" | grep -qE "$PLATFORM_KEYWORDS_RE"; then
            continue
        fi
        esc=$(escape_regex "$name")
        cases="${cases:+$cases|}$esc"
    done <<EOF
$names
EOF
    [ -n "$cases" ] || return 0
    printf '%s\t%s\n' "$file" "$cases"
}

# 收集全部代表清单
collect_all() {
    local f
    for f in \
        "$ROOT/tests"/unit/*.bats \
        "$ROOT/tests"/integration/*.bats \
        "$ROOT/tests"/regression/*.bats \
        "$ROOT/tests/sanity.bats" \
        "$ROOT/tests"/scripts/*.bats; do
        [ -f "$f" ] || continue
        collect_file "$f"
    done
}

if [ "${1:-}" = "--list" ]; then
    collect_all
    exit 0
fi

# 执行模式：xargs -P 并行跑每个文件的代表子集，失败聚合到 FAILS_FILE
tmpdir=$(mktemp -d)
runner="$tmpdir/runner.sh"
fails_file="$tmpdir/fails.txt"
out_file="$tmpdir/out.txt"
trap 'rm -rf "$tmpdir"' EXIT

cat > "$runner" <<'RUNNER'
#!/usr/bin/env bash
entry="$1"
IFS=$'\t' read -r file cases <<< "$entry"
filter="^($cases)$"
if "${BATS_BIN:-bats}" --filter "$filter" "$file" >/dev/null 2>&1; then
    printf 'PASS\t%s\n' "$entry" >> "$OUT_FILE"
else
    printf 'FAIL\t%s\n' "$entry" >> "$OUT_FILE"
    printf '%s\n' "$entry" >> "$FAILS_FILE"
fi
RUNNER
chmod +x "$runner"

export FAILS_FILE="$fails_file"
export OUT_FILE="$out_file"

collect_all | xargs -P 4 -I{} bash "$runner" '{}'

if [ -s "$fails_file" ]; then
    printf '%s: Windows smoke FAILED (%s 个文件含代表子集失败):\n' "$PROG" "$(grep -c . "$fails_file" | tail -1)"
    cat "$fails_file"
    exit 1
fi
printf '%s: Windows smoke passed (%s 个文件代表子集全绿)\n' "$PROG" "$(grep -c . "$out_file" | tail -1)"
