#!/usr/bin/env bash
# 捕获任务开始前的全量测试失败列表，供 P5 阶段做机械 diff。
# 幂等：任务级已捕获过则直接退出，不重跑。
# 缓存：仓库级按 (commit hash + gate_commands.P5 命令集合) 缓存，HEAD 未变则复用。
# 不阻塞：本脚本任何情况下都不应导致调用方 P3/P4 流程失败——
#   捕获失败或无法可靠解析（如项目尚未声明 TEST_RUNNER/gate_commands.P5、
#   命令执行异常、fail-list 提取行数与汇总计数对不上）一律只打印 WARNING 到 stderr、
#   不写入任何文件、exit 0（不影响 P3/P4 推进；缺失的后果由 P5 阶段的
#   graceful degradation 承担，见 P2.48——宁可"没有基线"，不可"基线是假的"）。
#
# 重要：不对声明的命令追加任何 flag（不做 v0.23.0 已踩过的"硬编码 -q 假设 pytest"同类错误）。
# 命令必须原样来自 gate_commands.P5（项目自己声明时就该带齐所需参数，本脚本只复用不改写）。
set -uo pipefail

TASK_DIR="${1:?用法: agate-capture-env-baseline.sh TASK_DIR}"
[ -f "$TASK_DIR/pre-task-baseline.md" ] && exit 0

P2_FILE="$TASK_DIR/P2-design.md"
[ -f "$P2_FILE" ] || { echo "ENV_BASELINE: P2-design.md 不存在，跳过基线捕获（P2 未完成前不应到达此步）" >&2; exit 0; }

P5_CMDS=$(P2_DESIGN="$P2_FILE" python3 -c '
import re, sys, os
content = open(os.environ["P2_DESIGN"]).read()
if not content.endswith(chr(10)):
    content += chr(10)
m = re.search(r"^gate_commands:[ \t]*\n((?:  .*\n|\s*\n)*)", content, re.MULTILINE)
if not m:
    sys.exit(0)
for line in re.findall(r"^  (P5\w*):\s*(.+)$", m.group(1), re.MULTILINE):
    print(line[1].strip().strip("\"").strip(chr(39)))
')
[ -z "$P5_CMDS" ] && { echo "ENV_BASELINE: 未在 P2-design.md 找到 gate_commands.P5，跳过基线捕获" >&2; exit 0; }

COMMIT=$(git rev-parse HEAD 2>/dev/null) || { echo "ENV_BASELINE: 非 git 仓库，跳过" >&2; exit 0; }
CACHE_KEY=$(printf '%s\n%s' "$COMMIT" "$(echo "$P5_CMDS" | sort)" | sha256sum | cut -d' ' -f1)
CACHE_DIR="$(git rev-parse --show-toplevel)/docs/.agate-env-baseline-cache"
CACHE_FILE="$CACHE_DIR/$CACHE_KEY.md"
mkdir -p "$CACHE_DIR"

if [ -f "$CACHE_FILE" ]; then
    cp "$CACHE_FILE" "$TASK_DIR/pre-task-baseline.md"
    echo "ENV_BASELINE: 复用缓存（commit $COMMIT 未变）" >&2
    exit 0
fi

FAIL_PATTERN="${TEST_FAIL_PATTERN:-[0-9]+ failed}"
FAIL_LIST=""
PARSE_OK=1
while IFS= read -r cmd; do
    [ -z "$cmd" ] && continue
    OUT=$(eval "$cmd" 2>&1) || true
    SUMMARY_COUNT=$(echo "$OUT" | grep -oE "$FAIL_PATTERN" | grep -oE '[0-9]+' | tail -1)
    if [ -z "$SUMMARY_COUNT" ]; then
        echo "ENV_BASELINE: 命令 '$cmd' 输出中未找到可识别的失败汇总行，放弃捕获，不写入任何文件" >&2
        echo "$OUT" | tail -5 >&2
        PARSE_OK=0
        break
    fi
    CMD_FAIL_LIST=$(echo "$OUT" | grep '^FAILED ' | sed 's/^FAILED //; s/ - .*//')
    CMD_FAIL_COUNT=$(echo "$CMD_FAIL_LIST" | grep -c . | tail -1)
    if [ "$CMD_FAIL_COUNT" -ne "$SUMMARY_COUNT" ]; then
        echo "ENV_BASELINE: 命令 '$cmd' 汇总计数($SUMMARY_COUNT)与明细提取数($CMD_FAIL_COUNT)不一致，" >&2
        echo "  说明当前 runner 的明细行格式未被本脚本识别，放弃捕获" >&2
        PARSE_OK=0
        break
    fi
    FAIL_LIST+="$CMD_FAIL_LIST"$'\n'
done <<< "$P5_CMDS"

[ "$PARSE_OK" -eq 0 ] && exit 0

FAIL_LIST=$(echo "$FAIL_LIST" | grep -v '^$' | sort -u)
FAIL_COUNT=$(echo "$FAIL_LIST" | grep -c . | tail -1)

{
  echo "---"
  echo "captured_at_commit: $COMMIT"
  echo "generated_by: agate-capture-env-baseline.sh"
  echo "---"
  echo "# 任务前环境基线"
  echo ""
  echo "失败数：$FAIL_COUNT"
  echo ""
  echo '```fail-list'
  echo "$FAIL_LIST"
  echo '```'
} > "$CACHE_FILE"

cp "$CACHE_FILE" "$TASK_DIR/pre-task-baseline.md"
echo "ENV_BASELINE: 已捕获，失败数=$FAIL_COUNT" >&2
exit 0
