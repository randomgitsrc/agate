---
phase: P8
task_id: TAG0019-risk-routing
type: release
parent: P2-design.md
trace_id: TAG0019-P8-20260821
status: draft
created: 2026-08-21
agent: implementer
# ── v2.0 机器字段 ──
bump_type: minor
debt_check: reviewed
packages: [agate-protocol, agate-scripts, agate-tests]
---

# P8 发布记录 — TAG0019 风险分路由（ceremony routing，RM-AG0031）

> 状态标记：`[PROD_NOT_TOUCHED]`。本记录为 releaser（implementer P8 模式）发布准备产出；
> **git commit / tag / bump 由主 Agent 在 gate 验证后亲自执行**（本记录不执行任何 git 操作）。

## 1. bump_type / debt_check

- `bump_type: minor`——v0.57.0 → **v0.58.0**。理由：新增 ceremony 机制功能（ceremony 声明字段 +
  `agate-risk-score.py` + `check-routing.py` + requirements-review 审声明 + M3 验收锚），全部向后兼容
  无破坏性变更（P7 已确认 BLOCKER=0 / DEVIATION-CRITICAL=0；UPGRADING v0.58.0 章节明示"无破坏性变更，
  无需迁移动作"）。
- `debt_check: reviewed`——已核对 `{AGATE_WORKSPACE}/debt/tech-debt.md`（DEBT0001-0017 现存条目）：
  **本任务无新增技术债登记**（grep TAG0019 / check-routing / agate-risk-score 0 命中）。P4 评审遗留
  F4（impact 扫描二进制/大小上限，与 I2 同锚点）与 F6（ci-gate-backstop 不含 check-routing）未登记，
  属 P4-review §4「主 Agent 决定项」且不阻断本次发布（P8 卡：只查留痕存在，不查内容达标、不阻断）。

## 2. 版本号变更确认清单（主 Agent 执行）

| 引用文件 | 现状 | 变更 |
|---------|------|------|
| README.md:5 version badge | `version-v0.57.0-blue` | → `v0.58.0` |
| CHANGELOG.md | 当前头段 `## [0.57.0] - 2026-08-21`（无 [Unreleased] 段） | 在 [0.57.0] 上方新增 `## [0.58.0] - 2026-08-21` 小节（见 §4 草稿） |
| agate/UPGRADING.md:92 | `### v0.58.0 — TAG0019 风险分路由（无破坏性变更）` 章节已存在（docs-sync 先行写入） | **核对一致，无需修改**——内容覆盖 ceremony 字段 + check-routing 挂载 + agate-risk-score + install-hook 重跑提示，与本次实际发布一致 |
| 独立 version 文件 | 无（pyproject.toml 仅 ruff target-version "py38"，无版本字段；agate 无 package.json） | 无需变更；P8 gate「version 文件变更」= README badge |
| git tag | v0.57.0 | 主 Agent 创建 **v0.58.0** 并显式 `git push origin v0.58.0`（`git push` 不带 tag 不推送）；推送后验证 `git ls-remote --tags origin v0.58.0`；release PR 用普通 merge（--no-ff），禁 squash |

## 3. 临时资源清单（主 Agent READY 收尾用）

| 类别 | 条目 | 状态 |
|------|------|------|
| 临时服务/进程 | 无（本任务纯协议/脚本/文档改动，未启动任何 daemon/debug server） | 无 |
| 临时数据 | pytest basetemp `/home/kity/oclab/agate/.ptmp-scratch` | **已清空无残留**（2026-08-22 确认目录空，非 git 提交内容） |
| 开发安装 | 无（未 pip install / 未建 venv / 未 editable install；依赖复用系统 /usr/bin/python3 + 既有 pyyaml） | 无 |
| 测试产物 | `P5-test-results/`（阶段证据，属任务产出随 commit 走，非临时资源） | 保留 |
| 注释 | worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0019`（agate 自身改造 dogfooding 双工作区，随 PR 生命周期，非临时资源） | 保留 |

## 4. CHANGELOG v0.58.0 变更条目草稿（主 Agent 执行时写入 CHANGELOG.md）

```markdown
## [0.58.0] - 2026-08-21

### 新增（TAG0019：风险分路由 ceremony routing，RM-AG0031）

- **ceremony 声明字段**（P1 frontmatter 可选，thin / standard / full，缺省 standard fail-closed）：
  声明 thin 须四要素 checklist（coupling_checklist 流式 + 跳过风险 + P5/P6 保留），缺一回退 standard；
  `ceremony: full` 任务 phases 必须含 P7（P7 不可裁，声明层 + 评审层双重保证）。
- **check-routing.py gate**（pre-commit 链 2j.1）：ceremony 路由校验——声明与算分 tier 单向 fail-closed
  （声明 thin 而算分 standard/full → 拦截）+ thin 四要素 checklist + 非法值 / P1 缺失边界（exit 0/1/2）；
  不声明 ceremony 的存量任务 exit 0 不拦截（向后兼容）；importlib 复用 check-pruning 同源函数（BDD-10）。
- **agate-risk-score.py 客观信号算分**：文件类型 / 敏感路径（词干匹配 + 左锚防误标）/ 改动规模 /
  影响面（反向引用，跳过任务产出文档）四信号 → risk_score / tier（thin|standard|full）+ 逐信号证据行 +
  域映射；提供可 import 的 `score_task(task_dir)` 与 CLI 薄壳；git 通道异常输出 `git_ok: false` 不静默降级。
- **requirements-review 审声明职责**：评审核对「风险分级/裁剪声明（risk_level/ceremony/phases）vs
  暂存区 diff 证据」，不一致 → needs-revision / rejected。
- **M3 验收锚度量协议**：评审轮数 vs 真实发现数双指标 + TAG0018 基线（4 场 LLM 评审 ≈0 净收益）+
  不达标回滚规则（机制文档，M3 主体不在本任务实行）。
- 修复：check-protocol-consistency CHECK 9 锚点表补 check-routing（反向覆盖）；测试注释 `/tmp` 字面
  清理（platform-assumptions 变更文件集 0 命中）。
```

## 5. 发布检查命令表（主 Agent 逐项执行，全部 exit 0）

| 检查项 | 命令 | 预期 |
|--------|------|------|
| P5 全量 | `python3 -m pytest -q --tb=no -p no:cacheprovider --basetemp=<可写且位于 git 仓库外的 basetemp>` | 全绿（1099 passed / 1 环境前提 I1 非缺陷 / 2 skipped；I1 需 git 仓库外 basetemp 转绿） |
| consistency | `python3 agate/scripts/check-protocol-consistency.py --strict-errors-only` | 0 ERROR（318 历史 WARNING 不阻断） |
| platform | `python3 agate/scripts/check-platform-assumptions.py <本任务变更文件集>` | 0 命中 exit 0 |
| count-tests | `bash agate/tests/scripts/count-tests.sh` | 用例数只增不减（≥749 基线 + 本任务新增约 40+） |
| CHECK 7 | `git ls-remote --tags origin v0.58.0` + README badge 数字对照 | tag 到达远端 + badge 一致（tag 创建后验证） |
| git log 对照 | `git log v0.57.0..HEAD --oneline` | 与 CHANGELOG [0.58.0] 小节变更无遗漏 |
| 干净 checkout 一致性 | CI consistency job 或临时 clone 跑 consistency | 0 ERROR（本地 worktree 路径过滤可能掩盖，须 CI/干净 checkout 兜底） |

> 时序注意（DEBT0013）：含 CHECK 7（badge vs tag）的链路在 **commit + tag 创建之后** 再重跑，
> bump 完成、tag 未建中间态 CHECK 7 必然报错属设计使然。

## 6. Lessons Learned

- **importlib 复用优于物理合并**：check-routing 经 importlib 复用 check-pruning 同源函数
  （`_md_field`/`_read_p1`/`_staged_source_count` + coupling_checklist/跳过风险判据）满足 BDD-10 且
  对既有 8 个检查零扰动——方案 B（独立脚本）vs 方案 C（改名合并）对比中，改动面小一个数量级被全程实证。
- **关键词词界/词干取舍是双向往返**（F3 误标 vs F2 漏标）：先 `\b` 整组词界（漏复数/拼接/词干 → 净回退），
  后左锚 `(?<![A-Za-z0-9_])` + 词干 + `\w*`（覆盖形态）——靠 cso 形态用例清单（21 high / 7 low）收敛，
  单一方向修复必然引发另一方向回归，最终形态需双向用例同时锁定。
- **环境敏感断言用等价探针**：`test_bdd_7` 的"非 git 上下文"前提在沙箱内不可构造（可写 basetemp 均在
  git 仓库内），用 `GIT_DIR=/nonexistent` 直接验证 fail-closed 分支（exit 1）与正常上下文（exit 0），
  避免环境前提卡死实现验证。