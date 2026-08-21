# TAG0018 交接单 — agate 原生支持 DSH 平台

> 本交接单供 worktree session 的 agent 按此启动 TAG0018 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0018**：agate 原生支持 DSH 平台（deepseek-harness）。

**一句话**：把 DSH 变成 agate 官方支持的第三个平台——`assets/templates/dsh/` 提供 orchestrator agent-preset + agate-protocol skill 模板，SETUP.md 增加「步骤 2-DSH」符号链接接入章节，platform-notes.md 增加 DSH 平台条目，`tests/unit/test_dsh_preset.py` 回归测试守护 preset 必填配置。

**已完成的前置工作（本交接单起草前）**：
- DSH 支持草稿在 `agate-copy`（工作区副本）中经过**实机验证**（2026-08-21，DSH GUI @127.0.0.1:23701）：
  - preset 软链安装 → 热发现（无需重启）→ 选择器出现「agate 编排者 · 自定义」→ 设置持久化为默认 → 新会话以 agate 编排者人格启动（探针回复实证"我是 agate 编排 Agent：负责 P0–P8 全流程管理…"）
  - **发现并修复真实 bug**：agent.cordis.yml 的 tool-fs-search 行缺必填配置 `sampleOverCapGlobResults`（DSH schemastery 必填无默认值）→ preset 挂载失败 → DSH fail-closed 拒绝创建会话；对照 standard preset 修复为 `config: { sampleOverCapGlobResults: false }`
- 回归测试 `tests/unit/test_dsh_preset.py` 已按 TDD 红/绿验证（移除修复 → 测试红；恢复 → 5 用例全绿）

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agate/.worktrees/agate-TAG0018` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agate`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是 worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。这是有意的：改造期间工具稳定，改造对象变化。
- **⚠️ gate 工具 ≠ 检查对象**：`check-protocol-consistency.py` **必须用 worktree 自己的**（检查 worktree 里的协议文件）；`agate-summary.py` 在 worktree 跑显示主 checkout 上下文，不代表 worktree 状态。
- **编排/派发类工具一律用 `~/.agate/scripts/` 稳定版**（agate-inject-card.py 等有 AGATE_ROOT 自解析逻辑，worktree 内相对路径调用会读到 worktree 正在被修改的协议卡片副本——TAG0016 教训）。
- **hook 在共享 git 目录**：worktree 的 `.git` 是文件（指向主 checkout `.git`），hook 实际在主 checkout 的 `.git/hooks/`，worktree commit 时自动触发。

**已完成的 setup（worktree 已可独立使用）**：
- 依赖齐全：bash 5.2 / python 3.12 / pyyaml / pytest 9.0.3 / shellcheck
- 基线验证：全量 pytest 全绿 + consistency 0 ERROR（--strict-errors-only）
- commit hook：指向 `~/.agate`（稳定版），worktree commit 自动触发
- orchestrator 注册：`.opencode/agents/orchestrator.md` + `.claude/agents/orchestrator.md`（均软链到 `~/.agate/orchestrator-template.md`，双平台）
- 工作区解析：`agate_common.py` 输出 worktree 自己的 `agate-workspace/`
- 任务数据：TAG0018 P0-brief + .state.yaml phase=P0 在 worktree 的 `agate-workspace/tasks/`

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

**交付物清单（草稿已在 `agate-copy`，P4 时按 P1 BDD 落位）**：
1. `agate/assets/templates/dsh/agent.cordis.yml` —— DSH orchestrator agent-preset（persona 薄身份 + 工具行；**含 `tool-fs-search config.sampleOverCapGlobResults: false`**）
2. `agate/assets/templates/dsh/preset.yml` —— preset 显示名「agate 编排者」
3. `agate/assets/templates/dsh/SKILL.md` —— agate-protocol skill（DSH 适配层：工具映射 + 4 食谱 + 平台注意）
4. `agate/SETUP.md`「步骤 2-DSH」章节 —— 符号链接接入命令（对齐 Claude/OpenCode 步骤 2 形态）
5. `agate/platform-notes.md` DSH 平台条目 —— 能力差异表 + 已知注意
6. `agate/tests/unit/test_dsh_preset.py` —— 5 用例回归测试（YAML 结构 / tool-fs-search 必填配置 / preset.yml 字段 / SKILL frontmatter / SETUP 章节在位）

**核心约束（不可违反）**：
1. **Linux 现状是基线**——全量 pytest 全绿是回归底线，每个修复都必须保持全绿
2. **不发明新结构**——平台接入 = SETUP.md 文档化符号链接 + 唯一 install-hook.py；无 platforms/ 目录、无 install-dsh.py（曾起草后废弃）
3. **测试平台无关**——test_dsh_preset.py 只校验仓库内文件，不依赖真实 DSH 实例（CI 无 DSH）
4. **SELF-GATE 触发**——改动 `agate/**/*.md` 与 `agate/scripts/*.py`、`SELF-GATE.md` 均触发 self-gate

## 4. 关键验证命令

```bash
# 全量测试（必须全过才能 commit；分片跑，每片外层 timeout）
python3 -m pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -q -p no:cacheprovider --basetemp=/home/kity/oclab/dsh-workspace/ptmp

# 新回归测试单独跑
python3 -m pytest agate/tests/unit/test_dsh_preset.py -v

# 一致性检查（0 ERROR 才行；用 worktree 自己的）
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only

# 用例数不漂移（只增不减）
bash agate/tests/scripts/count-tests.sh
```

**⚠️ 解释器注意**：用系统 python（`/usr/bin/python3`）跑 pytest——pytest 以模块形式装在系统 python，裸 `pytest` 命令 PATH 里通常找不到。本环境沙箱对 `/tmp` 只读，pytest 需 `--basetemp` 指向可写目录 + `-p no:cacheprovider`。

## 5. 阶段推进纪律（硬约束）

- **commit 时 phase = 本 commit 产出所在阶段**（P1 产出 → phase=P1 再 commit，commit 后再推进），否则 pre-commit 会用下一阶段 gate 拦截
- **TDD**：先写失败测试确认红，再实现确认绿
- **SELF-GATE**：触发文件入暂存区时，commit message 须含 `self-gate-review:` 路径或 `self-gate-skip:` 理由
- **commit message 前缀**：`wf(TAG0018-P{N}): ...` 风格
- **同类扫描（P0-brief 强制要求）**：P1 必须 grep 全仓确认无其他平台目录先例；SETUP.md/platform-notes.md 的平台章节形态对齐（可读 TAG0017 前各版本 diff 确认演进方向）
- **不并行 bash**：单步串行；长命令外层 timeout；读文件用 read/grep/glob 工具

## 6. 任务编号与状态

- task_id: `TAG0018`（RM-AG0030，roadmap 已登记 scheduled）
- 分支：`feat/TAG0018-dsh-platform`（worktree `.worktrees/agate-TAG0018`）
- 当前阶段：P0（.state.yaml phase=P0）

## 7. 已知风险与止损

| 风险 | 止损 |
|------|------|
| DSH 平台机制随版本变化（preset schema 等）| 文档标注「待实机验证」项；测试只校验仓库内文件，不绑定 DSH 版本 |
| 沙箱只读区误伤 gate（worktree 对 DSH 会话只读）| 任务工作区放可写位置；SKILL.md 平台注意已标注 |
| 全量 pytest 慢（~100s+）| 分片跑，每片 timeout；先跑 unit 再 regression/integration |
| 草稿内容与 BDD 漂移（草稿在 agate-copy 已实机验证过）| P4 时以 P1 BDD 为准重新核对，不直接搬运草稿 |

## 8. 完成后

1. 确认 pytest 全绿 + 0 consistency ERROR + count-tests 不漂移
2. SELF-GATE review（protocol-alignment-review 派发）
3. **release PR 必须普通 merge（--no-ff），禁止 squash merge**（agate-summary.py 依赖 tag 祖先关系）
4. 版本引用文件清单：README badge / CHANGELOG / UPGRADING 章节
5. roadmap 回写：RM-AG0030 → done

## 9. 交接确认

- P0-brief 四字段齐全（task/issues/known_risks/env_constraints）✅
- worktree 基线验证完成（pytest 全绿 + consistency 0 ERROR）✅
- 实机验证证据：DSH GUI 会话「AI助手角色与职责说明」= agate 编排者人格（2026-08-21 09:03，探针回复实证）✅
