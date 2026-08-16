# P6 验收进展（verifier）

## 批次 1/4：install + resolve + summary + hook + offline 全量 CLI 实跑
- BDD-1~8（agate-install）：真实 CLI 全过（latest 指针 / worktree tag / 幂等 / current→latest / 卸载清指针 / 引用保护拒绝 / --check 0 / --check 缺项指引）
- BDD-9~14 + 30（agate-resolve）：真实 CLI 全过（锁定命中 / 向上查找 / 回退 current / env 覆盖 / 未装回退 / 非法+空文件 / legacy 软链）
- BDD-15~19（resolve-entry + install-hook）：真实 CLI 全过（固定入口 / A/B 隔离 / 失败回退不静默 / 切版本免重装 / 复制模式 .agate-root）
- BDD-20/21（agate-summary）：真实 CLI 全过（.agate-version 原因 / 全局 current 原因）
- BDD-22~24（pack-offline）：真实 CLI 全过（真打 bundle + manifest checksum / 失败路径 tag 不存在 exit 1 不产坏包）+ pytest 15 用例
- BDD-25~29（install-offline）：真实 CLI 全过（平台不匹配拒绝 / checksum 篡改拒绝 / 离线装 wheel / 版本目录+指针+验证 / --skip 覆盖）+ pytest 15 用例
- BDD-31：git diff 证明 gate 判定脚本（check-gate/pre-commit-gate.py 等）零改动，仅解析层新增
