# Platform Notes — 各平台适配说明

不同 Agent 平台对 agate 的支持程度不同，本文记录已知情况。

---

## OpenCode

| 能力 | 状态 | 说明 |
|------|------|------|
| task 工具派发 subagent | ✅ 可用 | 使用方法 B（general subagent + prompt 注入角色文件）|
| 自定义角色（--custom-role）| ❌ 不可用 | issue #29616，subagent 无法加载自定义角色 |
| 本地开发环境 | ✅ 完整 | P3-P8 全部阶段可执行 |

**推荐方式（方法 B）**：派发时在 prompt 里直接写入角色定义文件路径，让 subagent 自己读取。不使用 `--custom-role` 参数。

---

## Claude Code

| 能力 | 状态 | 说明 |
|------|------|------|
| task 工具派发 subagent | ✅ 可用 | Task tool 支持独立上下文 |
| 本地开发环境 | ✅ 完整 | P3-P8 全部阶段可执行 |

---

## Claude Project 会话（claude.ai）

| 能力 | 状态 | 说明 |
|------|------|------|
| task 工具 | ❌ 不可用 | 纯对话环境，无 task 工具 |
| 本地开发环境 | ❌ 受限 | 网络受限，npm/pip 安装受影响 |

**适用范围**：仅适合 P0-P2（设计规划阶段）。P3-P8 需交接给 OpenCode/Claude Code 执行。

**典型工作方式**：用 Claude Project 完成 P0-P2 并 push 到 main，再切换到 OpenCode 执行 P3-P8。

---

## Codex / Hermes / OpenClaw 等

待补充——如有使用经验，欢迎 PR。

---

## Hardening-roadmap 跨平台适配（v0.4+）

hardening-roadmap 设计的核心 gate 机制（pre-commit hook + CI backstop）是 **git 协议级**的，所有平台统一可用。但配套能力有平台差异：

| 机制 | OpenCode | Claude Code | Codex | 说明 |
|------|---------|-------------|-------|------|
| pre-commit hook | ✅ 全功能 | ✅ 全功能 | ✅ 全功能 | git 机制本身，与平台无关 |
| `check-p6-provenance.sh` 审计 | ✅ | ✅ | ✅ | 纯 bash + 文件系统 |
| `agent:` 字段协作规范 | ✅ | ✅ | ✅ | 文件级 metadata |
| `risk=high` 自审 WARNING | ✅ | ✅ | ✅ | hook 输出 exit 2 |
| CI backstop（gate 重跑 + git blame WARNING）| ⚠️ 自实现 | ⚠️ 自实现 | ⚠️ 自实现 | 仅 GitHub Actions 提供开箱实现 |
| 独立 git author 追踪（P2.10 根治）| ❌ | ❌ | ❌ | Phase 3 平台功能未实现 |
| `~/.agate` 软链接 | ✅ | ✅ | ✅ | 文件系统级，无平台差异 |

**CI backstop 说明**：`.github/workflows/protocol-consistency.yml` 的 `gate-backstop` job 用 GitHub Actions 实现。在自建 CI（Gitea/GitLab/本地）跑 agate 时：
- 需要等价实现：`git push` 后重跑 `scripts/check-gate.sh` + 调用 `ci-gate-backstop.py`
- 不实现 CI backstop 也能用——只是失去 `--no-verify` 绕过 hook 的兜底审计

**Codex 兼容性**：Codex subagent max_depth=1 与 P2.1 强制派发独立 subagent（risk=high）的兼容性：
- Codex 单层任务工具无法"再派发"——这种情况下 P2 review 必须由主 Agent 自己跑（agent=main）
- `check-p6-provenance.sh` 会对 `risk=high` + `agent=main` 输出 WARNING（exit 2 不阻塞）
- 升级到 Codex 多层派发（待官方发布）后兼容自动生效

---

## 验证记录

agate 的派发机制于 2026-06-12 在 OpenCode 上完成验证：
- Phase 1（方法 B 派发）✅
- Phase 2（方法 A 自定义角色）❌（issue #29616）
- Phase 3（上下文隔离）✅

完整验证报告存档：`archived/validation-report.md`
