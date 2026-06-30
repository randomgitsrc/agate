#!/usr/bin/env bash
# check-state-yaml.sh — .state.yaml 格式校验（P2.15）
# 检查 .state.yaml 是否符合 state-machine.md 协议模板
# exit 0 = 格式正确; exit 1 = 格式错误; exit 2 = 无 .state.yaml

set -euo pipefail

STATE_FILE="${1:?用法: check-state-yaml.sh STATE_FILE}"

[ ! -f "$STATE_FILE" ] && exit 2

# 用环境变量传参，避免 shell 变量注入 Python 代码（M2 修复）
# 2>&1 保留 stderr，让 YAML 解析错误信息可见（M1 修复）
ERRORS=$(STATE_FILE="$STATE_FILE" python3 -c "
import yaml, sys, re, os

state_file = os.environ['STATE_FILE']
valid_phases = 'P0 P1 P2 P3 P4 P5 P6 P7 P8 PAUSED READY DONE'.split()

try:
    with open(state_file) as f:
        data = yaml.safe_load(f)
except yaml.YAMLError as e:
    # 只取错误行，不输出完整 traceback
    print(f'YAML 解析错误: {e}')
    sys.exit(0)

errors = []

if data is None:
    errors.append('文件为空')
    print('\n'.join(errors))
    sys.exit(0)

# 必填字段
for field in ('task_id', 'phase', 'status'):
    if field not in data:
        errors.append(f'缺必填字段: {field}')

# task_id 格式：T + 数字
task_id = data.get('task_id', '')
if task_id and not re.match(r'^T\d+\$', str(task_id)):
    errors.append(f'task_id 格式错误: {task_id}（应为 T + 数字，如 T001）')

# phase 合法值
phase = str(data.get('phase', ''))
if phase and phase not in valid_phases:
    errors.append(f'phase 非法值: {phase}（合法值: {\" \".join(valid_phases)}）')

# retries 必须是 dict，且每个值是列表
retries = data.get('retries', {})
if retries:
    if not isinstance(retries, dict):
        errors.append(f'retries 应为 dict，实际为 {type(retries).__name__}')
    else:
        for key, val in retries.items():
            if not re.match(r'^P\d+\$', str(key)):
                errors.append(f'retries key 格式错误: {key}（应为大写 P + 数字，如 P2）')
            if not isinstance(val, list):
                errors.append(f'retries[{key}] 应为列表，实际为 {type(val).__name__}')

if errors:
    print('\n'.join(errors))
" 2>/dev/null || true)

if [ -n "$ERRORS" ]; then
    echo "GATE STATE-YAML: .state.yaml 格式错误：" >&2
    echo "$ERRORS" | while IFS= read -r line; do
        [ -n "$line" ] && echo "  - $line" >&2
    done
    exit 1
fi

exit 0
