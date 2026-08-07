#!/usr/bin/env bash
# 捕获任务开始前的全量测试失败列表，供 P5 阶段做机械 diff。
# 幂等：任务级已捕获过则直接退出，不重跑。
# 缓存：仓库级按 (commit hash + gate_commands.P5 命令+formatter 集合) 缓存，HEAD 未变则复用。
# 不阻塞：本脚本任何情况下都不应导致调用方 P3/P4 流程失败——
#   捕获失败或无法可靠解析（如项目尚未声明 gate_commands.P5、
#   命令执行异常、无 formatter 无法提取 fail-list）一律只打印 WARNING 到 stderr、
#   不写入任何文件、exit 0（不影响 P3/P4 推进；缺失的后果由 P5 阶段的
#   graceful degradation 承担，见 P2.48——宁可"没有基线"，不可"基线是假的"）。
#
# 重要：不对声明的命令追加任何 flag（不做 v0.23.0 已踩过的"硬编码 -q 假设 pytest"同类错误）。
# 命令必须原样来自 gate_commands.P5（项目自己声明时就该带齐所需参数，本脚本只复用不改写）。
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/gate-result.sh"
set +e

TASK_DIR="${1:?用法: agate-capture-env-baseline.sh TASK_DIR}"
[ -f "$TASK_DIR/pre-task-baseline.md" ] && exit 0

P2_FILE="$TASK_DIR/P2-design.md"
[ -f "$P2_FILE" ] || { echo "ENV_BASELINE: P2-design.md 不存在，跳过基线捕获（P2 未完成前不应到达此步）" >&2; exit 0; }

P5_DATA=$(P2_DESIGN="$P2_FILE" python3 "$SCRIPT_DIR/agate-read-p5-commands.py")
[ -z "$P5_DATA" ] && { echo "ENV_BASELINE: 未在 P2-design.md 找到 gate_commands.P5，跳过基线捕获" >&2; exit 0; }

COMMIT=$(git rev-parse HEAD 2>/dev/null) || { echo "ENV_BASELINE: 非 git 仓库，跳过" >&2; exit 0; }
CACHE_KEY=$(printf '%s\n%s' "$COMMIT" "$P5_DATA" | sha256sum | cut -d' ' -f1)
CACHE_DIR="$(git rev-parse --show-toplevel)/docs/.agate-env-baseline-cache"
CACHE_FILE="$CACHE_DIR/$CACHE_KEY.md"
mkdir -p "$CACHE_DIR"

if [ -f "$CACHE_FILE" ]; then
    cp "$CACHE_FILE" "$TASK_DIR/pre-task-baseline.md"
    echo "ENV_BASELINE: 复用缓存（commit $COMMIT 未变）" >&2
    exit 0
fi

FAIL_LIST=""
PARSE_OK=1
ENTRY_COUNT=$(echo "$P5_DATA" | python3 "$SCRIPT_DIR/agate-json-get.py" len commands)

idx=0
while [ "$idx" -lt "$ENTRY_COUNT" ]; do
    cmd=$(echo "$P5_DATA" | python3 "$SCRIPT_DIR/agate-json-get.py" index commands "$idx" cmd)
    fmt_val=$(echo "$P5_DATA" | python3 "$SCRIPT_DIR/agate-json-get.py" index commands "$idx" formatter)

    fmt_path=""
    if [ -n "$fmt_val" ]; then
        fmt_path=$(resolve_formatter "$fmt_val" "$TASK_DIR") || fmt_path=""
    fi

    if [ -z "$fmt_path" ]; then
        echo "ENV_BASELINE: 命令 '$cmd' 无 formatter，无法提取 fail-list，放弃捕获，不写入任何文件" >&2
        PARSE_OK=0
        break
    fi

    json_result=$(run_test_with_formatter "$cmd" "$fmt_path")

    JSON_EXIT_CODE=$(echo "$json_result" | python3 "$SCRIPT_DIR/agate-json-get.py" get exit_code 0)
    if [ "$JSON_EXIT_CODE" -ge 120 ]; then
        echo "ENV_BASELINE: 命令 '$cmd' 本身崩溃（exit code $JSON_EXIT_CODE），放弃捕获，不写入任何文件" >&2
        PARSE_OK=0
        break
    fi

    CMD_FAIL_LIST=$(echo "$json_result" | python3 "$SCRIPT_DIR/agate-json-get.py" list failed_tests)
    CMD_FAIL_COUNT=$(echo "$CMD_FAIL_LIST" | grep -c . | tail -1)
    JSON_FAILED=$(echo "$json_result" | python3 "$SCRIPT_DIR/agate-json-get.py" get failed 0)
    JSON_ERRORS=$(echo "$json_result" | python3 "$SCRIPT_DIR/agate-json-get.py" get errors 0)
    SUMMARY_COUNT=$((JSON_FAILED + JSON_ERRORS))

    if [ "$SUMMARY_COUNT" -eq 0 ]; then
        echo "ENV_BASELINE: 命令 '$cmd' 无失败，跳过" >&2
        idx=$((idx + 1))
        continue
    fi

    if [ "$CMD_FAIL_COUNT" -ne "$SUMMARY_COUNT" ]; then
        echo "ENV_BASELINE: 命令 '$cmd' 汇总计数($SUMMARY_COUNT)与明细提取数($CMD_FAIL_COUNT)不一致，" >&2
        echo "  说明当前 runner 的明细行格式未被 formatter 识别，放弃捕获" >&2
        PARSE_OK=0
        break
    fi
    FAIL_LIST+="$CMD_FAIL_LIST"$'\n'
    idx=$((idx + 1))
done

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
