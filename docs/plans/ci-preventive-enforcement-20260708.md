---
plan_date: 2026-07-08
plan_id: ci-preventive-enforcement
trigger: review-20260708-1530.md（自我更正评审）
severity: high
status: implemented
---

# CI 从 detective 到 preventive：让红 CI 长出牙齿

## 背景

review-20260708-1420.md 诊断 self-gate 机制有"三层缺口"，其中缺口 1 断言"agate 自身 bats 无 CI 门禁"。review-20260708-1530.md 自我更正：**该断言错误**——`protocol-tests.yml`（dc2713e）早已在 push/PR 上跑全量 bats。

真正的问题是：**CI 是事后检测（detective），不是事前阻断（preventive）。** 红 CI 不能阻止红 commit 落地 main。

证据：
- `git log --merges` = 0（全程直推 main，无 PR）
- `gh api repos/randomgitsrc/agate/branches/main/protection` → 404（无分支保护）
- 6e1234b 引入的 4 个红测试随 commit 合入 main 并停留，直到外部评审手动实跑才发现

## 当前 CI 状态（实查）

| job | protocol-tests.yml | protocol-consistency.yml | 重复？ |
|-----|--------------------|--------------------------|--------|
| 全量 bats | `bats`（拆 4 step） | `bats-self-gate`（单 step） | **重复** |
| 一致性检查 | `consistency` | `check` | **重复** |
| shellcheck | `shellcheck` | — | 仅 tests.yml |
| gate backstop | — | `gate-backstop` | **仅 consistency.yml** |

两个 workflow 的触发条件不同：
- `protocol-tests.yml`：`on: [push, pull_request]`（全分支）
- `protocol-consistency.yml`：`on: push to main + pull_request to main`

## 需修的问题（按优先级）

### P0：分支保护——红 CI 必须能阻断合入

**根因**：直推 main + 无分支保护 = 红 CI 只改徽章颜色、不阻止落地。

**修复**：GitHub 仓库服务端设置（不在代码里）。

Settings → Branches → Add branch protection rule：
- Branch name pattern：`main`
- ☑ Require a pull request before merging
- ☑ Require status checks to pass before merging
  - ☑ Require branches to be up to date before merging
  - Required checks：`bats`、`shellcheck`、`consistency`、`gate-backstop`
- ☑ Do not allow bypassing the above settings

CLI 方式（可复现）：
```bash
gh api -X PUT repos/randomgitsrc/agate/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  --input /tmp/main-protection.json
```
其中 `/tmp/main-protection.json`：
```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["bats", "shellcheck", "consistency", "gate-backstop"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0
  },
  "restrictions": null
}
```

**效果**：即使 self-gate 评审再次假 ✓，红 bats 会使 PR 无法合入 main。假 ✓ 仍可能产生（缺口 2/3 未除），但进不了主干。

**局限**：
- 单人项目强制走 PR 略显重，但这是根治项
- `contexts` 名须首次配置后在 GitHub UI 确认自动补全出的确切名称

### P1：合并 workflow——删除冗余，单一真相源

6e1234b 新增的 `bats-self-gate` 和 `check` job 与 `protocol-tests.yml` 完全重复。两份 workflow 漂移风险高。

**修复**：

1. 把 `gate-backstop` job（唯一新增有效的）并入 `protocol-tests.yml`
2. 删除 `.github/workflows/protocol-consistency.yml`
3. `protocol-tests.yml` 的 `on` 保持 `[push, pull_request]`（比 consistency.yml 的 main-only 更宽，覆盖全分支）

合并后 `protocol-tests.yml` 的 4 个 job：`bats`、`shellcheck`、`consistency`、`gate-backstop`。无重复。

### P2：更正 T-G2.5 事故记录 root_cause

`docs/reviews/incidents/T-G2.5-fake-green-20260708.md` 的 frontmatter：

```yaml
root_cause: structural — three-layer gap (bats not in CI + A4 reads-not-runs + self-authored review)
```

"bats not in CI" 是错误结论（protocol-tests.yml 早已跑 bats）。应更正为：

```yaml
root_cause: structural — CI detective not preventive (no branch protection) + A4 reads-not-runs + self-authored review
```

### P3：A4 honor-system 的机器强制补强（可选，低优先）

review-20260708-1530.md 正确指出 A4 升级是 honor-system。但：
- P0（分支保护）落地后，假 ✓ 产生也进不了主干，危害降级
- A4 的"附实跑输出"要求机器无法强制验证（需解析评审报告格式）
- 成本收益比不高，暂不实施

若未来需要，可探索：self-gate 评审 subagent 在写报告前先跑 `bats ... 2>&1 | tee /tmp/bats-output.txt`，然后把输出文件路径嵌入报告。但这是优化，不是 P0。

### P4：本地 pre-push hook（兜底）

服务端分支保护 + 本地 pre-push hook 双保险。push 前本地跑 bats，挡"忘了跑就 push"。

```bash
cat > .git/hooks/pre-push <<'HOOK'
#!/usr/bin/env bash
echo "pre-push: 运行 agate bats..."
if ! bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/; then
    echo "bats 未全绿，拒绝 push" >&2
    exit 1
fi
HOOK
chmod +x .git/hooks/pre-push
```

局限：`--no-verify` 可绕过；hook 不随仓库分发。仅兜底，不替代 P0。

## 实施顺序

| 步骤 | 内容 | 执行者 | 类型 |
|------|------|--------|------|
| 1 | P1：合并 workflow | 代码提交 | 代码变更 |
| 2 | P2：更正 T-G2.5 root_cause | 代码提交 | 文档修正 |
| 3 | P0：分支保护配置 | 仓库 admin | 服务端设置 |
| 4 | P4：本地 pre-push hook | 各开发者 | 本地设置 |
| 5 | 更新 AGENTS.md CI 节 | 代码提交 | 文档同步 |

步骤 1-2 是代码变更，走 PR（步骤 3 落地后 PR 才能合入，验证闭环）。
步骤 3 是服务端操作，需仓库 admin 权限。
步骤 4 是本地操作，各自安装。

## 不做的事

- **不把 bats 加进 pre-commit-gate.sh**：bats 全量跑约 1-2 分钟，每次 commit 触发太重。pre-commit hook 保持轻量（格式+gate+转移），bats 留给 CI。
- **不追加 protocol-consistency.yml 的 bats-self-gate 和 check job**：已判冗余，删除而非补强。
- **不做 A4 机器强制**：P0 落地后危害降级，成本收益比不高。

## 验证

- [ ] `protocol-consistency.yml` 已删除
- [ ] `protocol-tests.yml` 含 4 个 job（bats / shellcheck / consistency / gate-backstop）
- [ ] T-G2.5 root_cause 已更正
- [ ] `bats agate/tests/` 全绿
- [ ] `python3 agate/scripts/check-protocol-consistency.py` 无 ERROR
- [ ] GitHub 分支保护已启用（`gh api .../protection` 非 404）
- [ ] 推一个红 commit 到 PR → CI 红 → PR 无法合入（实测闭环）
