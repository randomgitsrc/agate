# TAG0019 P6 验收进度

- [x] 读 verifier 角色 + P6 dispatch-context + P6 卡（注入）
- [x] 读 P0-brief / P1-requirements（15 BDD）/ P2-design（ui_affected: false）
- [x] 读 P5-test-results/（unit.md：1099 passed / 1 failed 环境前提 I1；fail-list.txt）
- [x] 读实现对象：agate-risk-score.py / check-routing.py / check-pruning.py（同源函数）
- [x] 读测试：test_agate_risk_score.py / test_check_routing.py / test_check_frontmatter helper
- [x] 文档断言对象核实：requirements-review.md（BDD-11）、P1 卡 M3 锚（BDD-12）、
      role-system/review-mapping/P2卡/P4卡（BDD-14）、README/summary/WORKFLOW/pre-commit-gate（BDD-15）
- [x] BDD-1..5 实跑 agate-risk-score.py（真实形状 repo + 受控 fixture 仓库）
- [x] BDD-4 对拍：check-routing vs check-pruning 同 repo 均按 >5 拦截（无矛盾）
- [x] BDD-6..10 实跑 check-routing 11 场景矩阵 + frontmatter-check + md-field-get +
      GIT_DIR 探针（git_ok:false fail-closed）；BDD-7 check-pruning 双闸兜底确认
- [x] BDD-13 platform 扫描重跑 exit 0；BDD-15 consistency 重跑 0 ERROR（--root=worktree）
- [x] BDD 映射 pytest 重跑：88 passed / 1 deselected（I1 环境前提）
- [x] 产出 P6-evidence/ 13 个实质证据文件 + test-output.log（主日志 19KB）
- [x] 写 P6-acceptance.md（15 PASS / 0 FAIL，frontmatter pass=15 fail=0 ui_affected=false）
- [x] 预检：check-p6-format --fix exit 0 ✅；check-p6-evidence exit 0 ✅
- [x] 预检：check-p6-provenance 第一轮 exit 1（test-output.log 未被 PASS 行引用）→ 已修（BDD-1 引用）
- [o] 预检：check-p6-provenance 第二轮 exit 1 —— **非 verifier 产出物**：
      P6-dispatch-context-verifier.md（主 Agent 派发文件）第 25 行 `- PASS 行最小格式：...`
      命中审计 2 预判正则 `^\s*- (PASS|FAIL)\b`（AGATE_CARD 块与 frontmatter 已排除）。
      verifier 不擅改主 Agent 派发产物 → 返回主 Agent 附精确修复建议。
- [x] 清理 scratch：/home/kity/oclab/agate/.ptmp-scratch/p6 等已删

## 待主 Agent 处理
1. P6-dispatch-context-verifier.md 第 25 行改措辞（去掉行首 `- PASS` 前缀，如改为
   `- 行格式要求：PASS 行最小格式为 ...` 或把该行并入第 24 行）→ 重跑 check-gate P6。
2. 附注：dispatch-protocol.md:931 遗留旧检查项行（见 P6-acceptance.md 附注，非阻塞）。

## 环境
- worktree: /home/kity/oclab/agate/.worktrees/agate-TAG0019（HEAD=7ae3b7e P5）
- task_dir: .../agate-workspace/tasks/TAG0019-risk-routing
- 一致性检查须 --root=worktree（默认 cwd 会解析到主 checkout 造成 CHECK 9 假 FAIL）