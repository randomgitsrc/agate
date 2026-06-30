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

## 验证记录

agate 的派发机制于 2026-06-12 在 OpenCode 上完成验证：
- Phase 1（方法 B 派发）✅
- Phase 2（方法 A 自定义角色）❌（issue #29616）
- Phase 3（上下文隔离）✅

完整验证报告存档：`archived/validation-report.md`
