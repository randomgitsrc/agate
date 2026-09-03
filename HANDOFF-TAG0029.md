# TAG0029 交接单 — gate 命令解析器修复批（RM-AG0056 + DEBT0027 + DEBT0023）

> 本交接单供 worktree session 的 agent 按此启动 TAG0029 任务。
> 任务已 P0 立项（.state.yaml phase=P0，P0-brief.md 已就绪）。
> worktree 已完成构建安装与基线验证，可直接开始 P1。

---

## 1. 你要做什么

**TAG0029**：gate 命令解析器修复批。

**一句话**：修复 `agate-read-gate-commands.py` 解析器与 `check-tdd-red.py` judge 分支的三个关联缺口——值清洗不剥离行内注释/残留引号（假绿灯）+ P3* 键静默收集 + 平台假设扫描器 fixture 数据面误伤。

## 2. 工作区布局（双工作区纪律，违反必出事故）

| 路径 | 角色 | 纪律 |
|------|------|------|
| `/home/kity/oclab/agateon/.worktrees/agate-TAG0029` | **本任务 worktree（改造对象）** | 在这里改代码、写阶段产出、跑测试、git commit |
| `/home/kity/oclab/agateon`（主 checkout） | 协议本体 + 任务数据 + `~/.agate` 指向 | **禁止改动**。它是稳定版来源，也是 hook 的 AGATE_ROOT |
| `~/.agate`（软链 → 主 checkout/agate） | **稳定版（开发工具）** | **禁止改动**。跑 gate / 读卡片用它 |

**核心原则（AGENTS.md T001 约定沿用）**：
- **跑 gate 用 `~/.agate`**（稳定版），**改代码/跑测试在 worktree**。
- commit 时 pre-commit hook 用 `~/.agate/scripts/pre-commit-gate.sh` 判定——gate 判定对象是 worktree 里的产出文件，但 gate 工具本身是 `~/.agate`。
- **⚠️ gate 工具 ≠ 检查对象**：`check-protocol-consistency.py` **必须用 worktree 自己的**（`python3 agate/scripts/check-protocol-consistency.py`）；编排/派发类工具用 `~/.agate/scripts/` 稳定版（TAG0016 教训）。
- **hook 在共享 git 目录**：worktree commit 时 hook 自动触发（指向主 checkout `.git/hooks/`）。

**已完成的 setup**：
- 依赖齐全（bash/python3.12/pyyaml/pytest/shellcheck/ruff）
- 基线验证：consistency 0 ERROR（--strict-errors-only）
- orchestrator 注册：`.opencode/` + `.claude/` 软链 → `~/.agate/orchestrator-template.md`
- 工作区解析：`agate_common.py` 输出 worktree 自己的 agate-workspace（须在 worktree 目录内执行）
- 任务数据：TAG0029 P0-brief + .state.yaml phase=P0

## 3. 任务范围（P0-brief 已锁定，P1 细化 BDD）

### 已核实并确认的缺陷/需求（全部有代码证据，见 P0-brief + DEBT 条目）

**DEBT0027（high，假绿灯——验收真实性风险）**：
- `agate-read-gate-commands.py` 值清洗 `val = raw.strip().strip(chr(34)).strip(chr(39))` 不剥离值内 `# 注释` 与残留引号——值不以 `"` 结尾时 strip(chr(34)) 只剥开头引号，残留结尾引号 + 注释尾巴
- 消费方 `bash -c` 执行 unterminated quote 语法错误（exit 2），`check-tdd-red` judge 分支可能把该输出误判为红灯可推进（**假绿灯：测试根本没跑却被当红灯证据放行**）
- 触发记录：TAG0028 P2 fix2 只改注释形态（行内→独立行）规避，未修解析器根因

**RM-AG0056（平台假设扫描器 fixture 数据面误伤）**：
- R2 规则 `(^|[\s=(\'\"])python3([\s]|$)` 静态扫描无法区分"测试代码里的命令调用"（应禁裸 python3）与"fixture 模拟平台日志的数据面内容"（command 字段本应含 `python3 -m pytest`）
- cmdstream fixture 17 处裸 python3 被命中破坏 TAG0011 bdd-8「tests 树 0 命中」，P5 全量 pytest 红灯回 P4 fix3 才闭环
- 扫描器不在 P3/P4 gate_commands 常驻面，回归到 P5 全量才暴露

**DEBT0023（low，P3* 键静默收集）**：
- `key.startswith('P3')` 把所有 P3* 非元键收集为 TDD 测试命令；`is_gate_meta_key` 只匹配 `_formatter/_timeout_seconds` 后缀，P3_xxx 不被豁免
- TAG0026 靠'禁用 P3_xxx 键'约定规避，协议层无机械防护

### 核心约束（不可违反）
1. **Linux 现状是基线**——现有全量 pytest 全绿是回归底线，每个改动必须保持全绿
2. **不破坏已有协议语义**——`agate-read-gate-commands.py` 是 P2/P3/P5 gate 消费链共享解析器，收紧收集侧须先 grep 全部消费方；不改 check-gate 返回约定
3. **假绿灯修复走 TDD**（TAG0027 复盘教训）：先补"语法错误 → exit 1"失败测试确认红，再改实现——语义修正类修复必须先补真实场景测试
4. **fixture 豁免防矫枉过正**：豁免须绑定 fixture 目录/文件声明，不能做成"含 fixture 字样就跳过"的宽匹配
5. **新 CHECK/扫描面上线前先全量扫描存量**（DEBT0025 流程）：存量有命中先登记清单再启
6. **范围锁定**——若 P1 分析发现需改动超出 P0-brief 锁定范围，须先停下跟用户确认

## 4. 关键验证命令

```bash
# 在 worktree 根执行：

# 全量测试（必须全绿才算过；分片 + -n auto 并行提速）
python3 -m pytest agate/tests/unit/ -n auto
python3 -m pytest agate/tests/regression/ -n auto
python3 -m pytest agate/tests/integration/ -n auto

# 一致性（0 ERROR 才行；必须用 worktree 自己的脚本）
python3 agate/scripts/check-protocol-consistency.py --strict-errors-only

# shellcheck
shellcheck -S warning agate/scripts/*.sh

# 测试计数（验证文档没漂移）
bash agate/tests/scripts/count-tests.sh

# 单脚本测试（改哪个跑哪个，TDD 先红后绿）
python3 -m pytest agate/tests/unit/test_{具体测试文件}.py
```

## 5. 阶段推进纪律（T001 血泪教训）

- **commit 时 phase = 本 commit 产出阶段**：P1 产出 → phase=P1 再 commit；推进 P2 随 P2 产出同 commit。**不要**先写 phase=P2 再 commit P1 产出
- **改脚本走 TDD**：先写失败测试确认红 → 改脚本确认绿（AGENTS.md「改脚本的工作流」）
- **批量机械改动的 TDD 策略**：先写一个"grep 断言审计"测试作为回归拦截；批量改动后跑该断言 + 全量 pytest 确认绿
- **git 命令加 timeout**、单步串行（AGENTS.md 工具纪律）
- **commit message 含 `wf(TAG0029-P{阶段}):`** 前缀
- **改 `agate/scripts/*` + `agate/phase-cards/P2-design.md` 触发 SELF-GATE**：commit message 需含 `self-gate-review:` 或 `self-gate-skip:`（否则 commit-msg hook WARNING）。协议文档变更需跑 `check-protocol-consistency.py` 确认无 ERROR

## 6. 任务编号与状态

- 任务目录：`agate-workspace/tasks/TAG0029-gate-parser-fix/`（在 worktree 里）
- `.state.yaml`：phase=P0（P1 开始后推进）
- active-tasks.md「待开始」已有 TAG0029 行（⬜ P0）
- roadmap：RM-AG0056 关联本任务（scheduled，2026-09-03 立项）
- **编号体系**：任务用 `TAG0029`。校验器 `^T[A-Z]{2}\d+$`
- **并行提示**：TAG0030（验收盲区）/ TAG0031（DEBT 存量）与本站并行，三路文件域不重叠——但 roadmap/active-tasks/debt 登记行是共享面，只改自己关联的行，不整表重排

## 7. 已知风险与止损

- **解析器消费面广**（P2/P3/P5 gate 消费链）：收紧收集侧先 grep 全部消费方，P3 精确键 + 白名单后缀确认不漏合法用法 → 止损：全量 pytest + 单测锁定收集行为
- **假绿灯修复是语义变更**：judge 分支判定逻辑改动影响验收真实性判定 → 止损：先补失败测试（语法错误→exit 1）确认红再改
- **fixture 豁免宽匹配风险**：豁免被真代码借用 → 止损：绑定 fixture 目录声明 + 单测锁定
- **扫描器纳入常驻面是新面**：存量可能命中 → 止损：先全量扫描登记清单（DEBT0025 流程），分批清理后启用

## 8. 完成后

- P8 gate + READY → 提 PR 合并 main（PR 普通 merge 非 squash，tag 要求）
- **合并前在 PR 里看 CI 结果**——pytest/shellcheck/consistency/gate-backstop 全绿才算过
- **merge 模式：本任务 PR 完成后由主 Agent 综合 merge**（三路并行 TAG0029/30/31，不自行 git-to-main）
- roadmap 回写 RM-AG0056 → done；DEBT0023/0027 登记关闭（closure_criteria 逐条核验）
- 复盘按 agate 自身变更流程归档（合并后在主 checkout 写复盘 + 更新 roadmap/版本）

## 9. 交接确认

- worktree 基线：consistency 0 ERROR（--strict-errors-only）已验
- hooks 就位（指向 `~/.agate` 稳定版）、orchestrator 已注册（双平台）、依赖齐全
- 任务数据就绪：TAG0029 P0-brief + .state.yaml phase=P0
- 交接单位置：`HANDOFF-TAG0029.md`（worktree 根，已 commit）
