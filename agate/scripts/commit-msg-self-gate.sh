#!/bin/bash
# commit-msg-self-gate.sh — commit-msg hook 薄壳（经 resolve-entry 解析版本后 exec 对应版本 py）
# shebang 用 /bin/bash 而非 /usr/bin/env bash：git-for-windows 的 parse_interpreter 对
# `#!/usr/bin/env bash` 会剥掉 `bash` 参数，以 `env <hook> <msgfile>` 执行（依赖 env.exe +
# MSYS 嵌套 shebang 递归，Windows 上实测 hook 不执行）；`#!/bin/bash` 让 git 直连 bash。
set -u
# 1. 入口根自定位（软链→本体；复制模式 .agate-root 恢复）——resolve-entry 所在安装根。
#    不用 AGATE_ROOT 变量（避免经环境泄漏给 resolve-entry 而绕过项目版本解析，TAG0008）
ENTRY_ROOT="${AGATE_ROOT:-$(dirname "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")")}"
if [ ! -d "$ENTRY_ROOT/scripts" ] \
    && [ -f "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")/.agate-root" ]; then
    ENTRY_ROOT=$(tr -d '\r' < "$(dirname "$(readlink -f "${BASH_SOURCE[0]:-$0}")")/.agate-root")
fi
# 2. python 探测：python3 → python
PY=""
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }; done
# 3. exec 固定解析入口 resolve-entry（读项目 .agate-version → 对应版本 gate py，不随版本变）
if [ -n "$PY" ] && [ -f "$ENTRY_ROOT/scripts/resolve-entry.py" ]; then
    exec "$PY" "$ENTRY_ROOT/scripts/resolve-entry.py" commit-msg "$@"
fi
# 4. exec 失败 → fail-closed 阻断（不运行 sh 兜底逻辑）
echo "GATE ERROR: 无法启动 resolve-entry（python3/python 均不可用或脚本缺失）" >&2
echo "  self-gate 触发面检测无法执行，commit 中止——请安装 python3 + pyyaml" >&2
exit 1
