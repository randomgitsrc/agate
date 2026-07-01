#!/usr/bin/env bats
# tests/regression/v060-yaml-indent.bats — 回归测试：task-files.md YAML 缩进
# 触发：b028315 "feat(v0.6): 模型选择" 提交时多打空格，executor_env: 块从 2 空格变成 3 空格
# 影响：YAML 解析失败 → check-protocol-consistency.py CHECK 1 红 → CI 失败

load ../helpers/load.bash

@test "R1.1 task-files.md executor_env 块 YAML 可解析" {
    local file="$AGATE_ROOT/assets/templates/task-files.md"
    # 提取 executor_env 块（前 10 行）
    local block
    block=$(awk '/^executor_env:/,/^[a-z_]+:/' "$file" | head -10)
    # 验证 yaml.safe_load 成功
    echo "$block" | python3 -c "import yaml, sys; yaml.safe_load(sys.stdin)"
}

@test "R1.2 task-files.md executor_env: 顶格（无前导空格）" {
    local file="$AGATE_ROOT/assets/templates/task-files.md"
    # 检查 executor_env: 行不以空格开头
    if grep -nE '^ executor_env:' "$file" >/dev/null 2>&1; then
        echo "executor_env: 行有前导空格" >&2
        return 1
    fi
}

@test "R1.3 task-files.md executor_env 子字段 2 空格缩进" {
    local file="$AGATE_ROOT/assets/templates/task-files.md"
    # 找到 executor_env: 行号
    local line_num
    line_num=$(grep -n '^executor_env:' "$file" | cut -d: -f1)
    # 检查下面几行（platform, has_task_tool, has_local_runtime, network, model_tier）缩进都是 2 空格
    for i in 1 2 3 4 5; do
        local check_line=$((line_num + i))
        local actual_line
        actual_line=$(sed -n "${check_line}p" "$file")
        if ! echo "$actual_line" | grep -qE '^  [a-z_]+:'; then
            echo "第 ${check_line} 行缩进异常: $actual_line" >&2
            return 1
        fi
    done
}
