---
phase: P2
task_id: TAG0005-mechanism-fixes
type: review
parent: P2-design.md
trace_id: TAG0005-mechanism-fixes-P2-20260813
status: approved
created: 2026-08-13
agent: plan-eng-review
---

# P2 评审 — agate 机制修复批（TAG0005）

> 评审对象：P2-design.md（12 个候选方案，6 处修复设计）。评审基于对协议文件与脚本的代码级核验（非仅读设计文本）。

## 结论

**status: approved** — 阻塞级问题 0 个。6 处修复设计全部可落地、自洽、与代码现状逐条对上，self-host 声明成立。非阻塞建议 5 条（见下）。

## 架构问题（阻塞级）

无。

## 架构问题（非阻塞）

1. **check-debt.sh exit-code 文档漂移未覆盖 scripts/README.md**（§2.6）：设计同步了 check-debt.sh 头注释（L5/L13）与 state-transitions.md L84 / UPGRADING.md L120 定位，但未覆盖 `agate/scripts/README.md` L23 —— 该行仍声明「`--retreat-coverage` … 恒 exit 0」「回退模式恒 0」，依赖加载失败改 exit 2 后即陈旧。建议 §2.6 纳入一行表格同步（属 agate-docs 包，不扩大脚本改动面）。
2. **BDD-9 判定口径需在 P6 固化为「单文件」而非「单处命中」**（§2.3）：模板拆分后 `rg 'Review 角色特别指令' agate/` 将在 dispatch-prompt.md 命中 2 处（`### Review 角色特别指令` 节标题 + 代码块内 `## Review 角色特别指令` 指令文本）——设计已注明「单文件不违反模板一处」，但 P6 验收若用 `rg -c == 1` 会误判 FAIL。建议 P6 断言改用 `rg -l 'Review 角色特别指令' agate/` 判定仅命中 dispatch-prompt.md 单文件。
3. **files_to_read 对 RM-AG0003 的上下文略欠**（§4）：dispatch-protocol.md:105-135 覆盖了改写节，但 implementer 要保证「retry 上限/PAUSED 段未改」（BDD-14）需知道 MAX_RETRY/PAUSED 定义在 state-machine.md（如 P2 --[retry>=MAX]--> PAUSED）。建议补一条 `agate/state-machine.md` retry 规则段引用。低优先级——P6 文本比对兜底。
4. **观察（不登记 DEBT，属 P1 锁定范围外的 pre-existing）**：dispatch-protocol.md 内联模板 L435 硬编码 `assets/execution-roles/{role}.md`（无 `{execution-roles|review-roles}` 占位），评审角色派发时路径语义陈旧。设计 I7 备注缓解了 status 语义分叉，但未修该路径——非本任务引入，记录待未来统一。
5. **观察（既定代价，无需动作）**：C8 backend→plan-eng-review 后所有 backend 任务（含 low）P2 恒需一个方案评审 subagent，编排成本略增——设计 §2.1 已声明为 C8 机械映射的既定代价（frontend 同理），且 backend+high 同角色自动去重，评审总数不增。

## 测试缺口

- **RM-AG0011 缺 formatter 排除的回归用例**（§2.2）：设计只同步 GPC.1/GPC.2，二者 gate_commands 块均不含 formatter 键，aux 排除 `_formatter` 这一新增语义无测试锁定。建议新增一条（如 GPC.3：块含 P5+P5_formatter → 输出 `1 0`，或含 P5_e2e_formatter 仅辅键 → `0 0`），防止后续有人把 `_formatter` 加回计数。非阻塞——read-p5-commands P5C.* 全绿可作间接守卫，但直接断言更稳。
- 其余各处（RP.17/18/19、check-debt 依赖缺失 exit 2、G5_CMD.1/5 主/辅文案、GPC.1/2 双值）测试设计完整，无缺口。

## 锁定决策

- **RM-AG0010（§2.1）**：候选 A —— C8 三处表 backend 行补 plan-eng-review（P2 方案评审）+ 保留 review（P4 后），附去重说明；check-gate.sh P2 分支不动（BDD-2）。与「角色选择决策」L150-152 既有指引自洽。方案 B（复用通用 review 于 P2）会造成职责漂移与 high 行分叉，正确放弃。
- **RM-AG0011（§2.2）**：候选 A —— count.py 输出 `MAIN AUX` 双值；aux 排除 `_formatter`（与 read-p5-commands L29-30 对齐，属计数语义自然范围，非越界）；check-gate.sh P5 WARNING 改主/辅文案，触发条件保持 total>1。方案 B 的结构化收益在本场景不成立。
- **RM-AG0012①（§2.3）**：候选 A —— 模板拆独立块 `### Review 角色特别指令` + render 按 ROLE_DIR 追加（复用既有 sed 惯用式），组装顺序 main→review→阶段追加。Review 指令位置从开头移到末尾语义等价（评审理据不依赖顺序）。方案 B（sed 剥除）硬编码节标题、机制脆弱，正确放弃。
- **RM-AG0012②（§2.4）**：候选 A —— 复用既有测试文件新增 RP.17（exit 2 + stderr「角色文件不存在」），README 计数 16→20（含既有 1 漂移修正，按实际同步）。
- **RM-AG0003（§2.5）**：候选 A —— 自动重试为「不占 retries[Pn] 槽位的前置动作」，短会话 <1min 告警复用 L128 弱信号；「禁止不调整重试」段显式豁免；第 2 次空返回/MAX_RETRY/PAUSED 段不改（BDD-12/14 最强满足）。方案 B 压缩重试上限语义，正确放弃。
- **同类扫描守卫（§2.6）**：候选 A —— check-debt.sh 依赖加载失败 exit 0→2，有意跳过分支（无 retreat 提交）保持 exit 0；与「只读 WARNING 不阻断」定位不冲突（exit 2 暴露工具自身故障，且无脚本调用方，改 exit code 无 hook 波及面——已 grep 核实）。方案 B 的 exit 1 与文档「不阻断」声明冲突，正确放弃。

## 实现就绪度

files_to_read 覆盖 6 处修复的实现上下文（含脚本改动点行号、测试断言同步位置、README 计数表），除上述 NB-3 一处建议补 state-machine.md 外，P4 implementer 可直接按清单实现。candidate_count: 12（6 处 × 2 候选）与正文一致；四字段齐全；gate_commands 1 主 2 辅（P5 全量 bats / P5_consistency / P5_shellcheck）恰为 RM-AG0011 新计数的真实样例；minimal_validation 声明纯代码逻辑 + 4 项现状实测复现，符合 P2 卡片要求。

## 范围核验

§2.2 aux 排除 `_formatter` 属 RM-AG0011「计数语义修复」自然组成部分（消除现状 formatter 被计入的既有偏差，仅 py 内一行过滤，不扩大文件改动面），判定不越 P1 范围锁定。`[PROD_NOT_TOUCHED]`——本评审仅读取 worktree 协议文件与脚本并运行只读 grep/rg 核验，未接触生产环境。
