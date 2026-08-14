# P4-progress — implementer batches

## 批次 0（公共库）— committed 165a31c

- [x] 新建 agate_common.py（数据流 7 函数 + resolve_workspace + 3 hook 工具 + main）
- [x] ci-gate-backstop.py resolve_tasks_dir 改调 agate_common.resolve_workspace
- [x] 3 个 bats 改调用（agate-workspace-resolve 10 / helpers-python 3 / ci-gate-backstop 11）
- [x] P4 review approved（0 BLOCKER）
- [x] 全量 733 bats 绿 + count-tests 727 + consistency 0 ERROR

## 批次 1a（4 check 脚本）— committed 6e33c04

- [x] check-changelog / check-frontmatter / check-state-yaml / check-scope-resolved → py
- [x] 4 bats 调用点改 py（41 用例绿）
- [x] 全量 733 bats 绿 + count-tests 727 + consistency 0 ERROR

## 批次 1b（3 脚本）— committed 9cb6fd5

- [x] check-p6-format / agate-archive-stale-outputs / agate-extract-context → py
- [x] 3 bats 调用点改 py（39 用例绿）
- [x] 全量 733 bats 绿 + count-tests 727 + consistency 0 ERROR

## 批次 1c（2 脚本）— committed 15fd59f

- [x] agate-next-card / agate-render-dispatch-prompt → py
- [x] 5 bats 引用面调用点改 py（42 用例绿）
- [x] 全量 733 bats 绿 + count-tests 727 + consistency 0 ERROR

## 批次 1d（3 脚本）— committed 6060acf

- [x] agate-summary / agate-changes / agate-migrate-workspace → py
- [x] agate-migrate-workspace.bats 调用点改 py（9 用例绿）；summary/changes 无 bats（手动 diff 0 差异）
- [x] 修 bdd-5 检查器豁免二进制 open（`"rb"/"wb"`）——TAG0004 遗留缺陷
- [x] 全量 733 bats 绿 + count-tests 727 + consistency 0 ERROR
- 注：本批 subagent 3 次空返回（migrate-workspace）→ 采用"implementer 不跑 bats、主 Agent 验证"策略后成功

## 批次 1e（check-platform-assumptions）— committed 5ddf396

- [x] 扫描器 py 化（R1-R5 + docstring 豁免 + .py 扩展名）
- [x] BDD-6 前置验证：排除自身后对既有 py 扫描 0 命中
- [x] bats 14→16 用例（新增 2 条 docstring 豁免）
- [x] 全量 735 bats 绿（scripts 23 含新增 2）+ count-tests 727 + consistency 0 ERROR
- 注：本批 subagent 1 次空返回 → 拆 py 与 bats 两步 + 不跑 bats 策略

## 批次 2（复合 11 脚本）— 全部完成

- [x] 2a（0faaed4）：check-retrospective / agate-inject-card / check-debt → py；修 inject-card 占位符错误消息未透传
- [x] 2b（8b8fbc6）：check-state-transition / agate-retreat-to → py；MAX_RETRY_MAP 并入 agate_common
- [x] 2c（236ac80）：check-pruning / agate-capture-env-baseline → py
- [x] 2d（3e86a65）：check-p6-evidence / check-p6-provenance → py
- [x] 2e（5ee8b88）：check-tdd-red → py（复用 agate_common formatter）
- [x] 2f（3547b62）：check-gate → py（P0-P8 全分支 + 187 处调用点）；修 bdd-5 read_text 误判自定义函数
- 每批全量 bats 全绿 + count-tests 727 + consistency 0 ERROR

## 批次 3（hook 链 4 个）— 完成

- [x] 3a（3547b62 前部分）：pre-commit-gate.py 主程序（526 行，调度/PROD_TOUCHED/dispatch-context hash/write_gate_result）
- [x] 3b：commit-msg-self-gate.py + pre-push-gate.py + install-hook.py
- [x] 3d：3 个 hook sh 薄壳化（20/20/21 行）
- [x] 3e：修 2 个薄壳化过时测试（pre-commit-hook #42 / dispatch-context-warning #25）
- [x] 3f：锚点表 check-frontmatter 条目同步 py（0 ERROR，1 coverage WARNING 属批次 4 中间态）
- 批次 3 专项 85/85 绿 + 全量 733 绿 + count-tests 727 + consistency 0 ERROR

## 批次 4（收尾）— 待办

- [ ] consistency 锚点表剩余 15 条涉 sh → py
- [ ] 文档引用同步（表 B：SETUP/UPGRADING/README/scripts/README.md/tests/README.md）
- [ ] SETUP pyyaml 强制化 + UPGRADING 新章节
- [ ] scripts/README.md 重写 + pyproject.toml ruff 规则集落地
- [ ] CI 同步（shellcheck→ruff、check-platform-assumptions.py 扫描）
