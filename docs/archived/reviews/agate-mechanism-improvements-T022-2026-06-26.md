# agate 机制改进建议：基于 T022 P0-P8 全链执行证据

> 评审日期：2026-06-26
> 评审者：T022 主 Agent（自我复盘）
> 评审对象：agate 工作流机制（`~/.agate/`）
> 证据基础：T022 P0-P8 全链执行（周期 1 废弃 + 周期 2 有效，最终 v0.2.0 READY）
> 视角：聚焦 agate 机制本身的改进，而非 T022 任务复盘（任务复盘见 `docs/reviews/agate-postmortem-T022-2026-06-26.md`）

---

## 一、问题摘要

T022 暴露了 agate 机制层面的 8 个改进点，按严重度分类：

| 严重度 | 问题 | 浪费 token 占比 |
|--------|------|-----------------|
| 🔴 阻断 | P4 gate 缺少子目标覆盖度检查 | ~50%（周期 1 整体废弃的根因之一）|
| 🔴 阻断 | P6 gate 缺少 BDD 数量对照 | ~50%（周期 1 整体废弃的根因之一）|
| 🔴 阻断 | P8 缺少版本 bump 类型判定规则 | ~5%（用户指出后回退）|
| 🔴 阻断 | P8 bump 后未重跑 P5 gate | ~3%（pre-publish 时才发现）|
| 🟠 高 | P6 验收脚本"写跑分离"边界模糊 | 协议违规但结果正确 |
| 🟠 高 | P6 vision-helper 与 DOM 验证的冲突仲裁缺失 | 2 轮截图重做 |
| 🟠 高 | P7 DEVIATION 升级 BLOCKER 标准缺失 | 核心设计未落地被放行 |
| 🟠 高 | compact 恢复后缺少环境一致性验证 | 1 轮 Playwright 调试浪费 |

**核心发现**：8 个问题中有 4 个是 **gate 设计缺陷**（🔴 阻断级），且这 4 个 gate 缺陷在 T022 中**形成了两条互相放大的失败链路**：

- 链路 1（周期 1 废弃，~50% token）：P4 漏 emit 迁移 → P4 gate 通过 → P5-P8 全部基于不完整实现推进 → P6 验 6/29 BDD 时才发现 → 整体回退
- 链路 2（周期 2 部分返工，~10% token）：P8 bump 选 patch 迁就测试缺陷 → bump 后 P5 gate 才发现测试失败 → 用户指出后回退重做

**改进优先级**：先修复 4 个 🔴 阻断级 gate 缺陷，再修复 4 个 🟠 高优改进点。

---

## 二、🔴 阻断级改进（必须先修）

### 改进 1：P4 gate 增加"P1 子目标覆盖度"检查

**位置**：`state-machine.md` 的 P4 转移规则 + `dispatch-protocol.md` 的可判定门槛表

**现状**：
```
P4 --[P4-implementation/ 下文件非空 AND git log --oneline -1 包含 P4 commit]--> P5
```

**问题**：当前 gate 只能检测"P4 产出了文件"和"P4 commit 存在"，无法检测"P4 产出是否覆盖 P1 的所有需求项/子目标"。

**证据**：T022 周期 1 中，P4 implementer 完成了 3/4 子目标（三胞胎抽 BaseDiagram / useMarkdown 注册模式 / 渲染状态抽 composable），漏了第 4 个（emit 迁移）。P4 gate 通过 → P5-P8 全部基于不完整实现推进 → 整个周期 1 废弃（~17 个 commit，~50% token 浪费）。

**改进**：
```yaml
# state-machine.md P4 转移规则（修订）
P4 --[P4-implementation/ 下文件非空 AND git log --oneline -1 包含 P4 commit AND P1 子目标覆盖率 = 100%]--> P5

# 覆盖率定义：
# - 主 Agent 读 P0-brief.md 的 task 字段和 P1-requirements.md 的范围声明
# - 提取子目标清单（量化验收条件，如"4 个子目标"）
# - 对照 P4 commit message + 文件变更，确认每个子目标有对应实现
# - 覆盖率 < 100% → gate 不通过，回 P4 补做
```

**附加指引**：在 `dispatch-protocol.md` 的 P4 派发 prompt 模板中追加：
```
## P4 派发附加要求
你的产出必须覆盖 P1 的所有子目标。完整子目标清单见 P1-requirements.md 的范围声明。
每个子目标至少对应一个 P4 commit 或一个文件变更。
完成后，在 commit message 或产出文件中列出"已覆盖子目标：[清单]"。
```

**验收标准**：gate 工具（如 `scripts/check-p4-coverage.sh`）能机械判定 P1 子目标清单 vs P4 commit/文件的覆盖率。

---

### 改进 2：P6 gate 增加"P1 BDD 总数 == P6 验收条数"对照

**位置**：`state-machine.md` 的 P6 转移规则 + `dispatch-protocol.md` 的可判定门槛表

**现状**：
```
P6 --[P6-acceptance.md 有效 AND P1 的每条 BDD 条件标记为 PASS 或 FAIL（二值，不允许"调整/跳过/覆盖"）AND 无 FAIL 条件 AND 无未决 NEED_CONFIRM]--> P7
```

**问题**：当前 gate 只检查"P6-acceptance.md 中的 BDD 标 PASS/FAIL"，但**不检查"P1 的 BDD 总数 == P6 验收的 BDD 总数"**。这允许主 Agent 主观挑验部分 BDD 就标 PASS。

**证据**：T022 周期 1 中，P6 验收只验了 6 条 BDD（mermaid 渲染、plantuml 渲染、svg 渲染、toggle、fullscreen、sanitize），commit `8ab1d12a` 标"BDD 验收 6/6 PASS"。但 P1-requirements.md 有 29 条 BDD（9 维度）。23 条 BDD 没被验证，但 P6 gate 通过。

**改进**：
```yaml
# state-machine.md P6 转移规则（修订）
P6 --[
  P6-acceptance.md 有效 AND
  P1 的每条 BDD 条件标记为 PASS 或 FAIL（二值）AND
  P1 的 BDD 总数 == P6-acceptance.md 的验收条数 AND  # 新增
  无 FAIL 条件 AND
  无未决 NEED_CONFIRM
]--> P7

# BDD 总数对照：
# - 主 Agent 统计 P1-requirements.md 的 BDD 条数（grep "^\*\*Given" 或人工计数）
# - 统计 P6-acceptance.md 的验收条数
# - 两者必须一致；不一致 → gate 不通过
```

**附加指引**：在 `dispatch-protocol.md` 的 P6 派发 prompt 中追加：
```
## P6 BDD 覆盖完整性
P6 验收必须**全量对照 P1 的 BDD 条数**，不能挑验。
P1 有 N 条 BDD → P6 必须有 N 条验收结果（PASS 或 FAIL）。
挑验 = gate 不通过。
```

**验收标准**：gate 工具能机械判定 P1 BDD 数 vs P6 验收数。

---

### 改进 3：P8 增加版本 bump 类型判定规则

**位置**：`dispatch-protocol.md` 的 P8 派发 prompt 模板 + `state-machine.md` 的 P8 转移规则

**现状**：P8 发布准备时，patch vs minor vs major 的判定完全靠主 Agent 凭感觉。agate 没有基于 P2 声明的 `packages` / `domains` 和改动性质的版本 bump 判定指引。

**问题**：主 Agent 遇到障碍（测试 hard-code 版本号）时倾向绕过而非修复——选低版本号迁就测试缺陷。

**证据**：T022 周期 2 P8 中，T022 是内部 API 重构（useMarkdown 返回值变了、新增 composable、组件目录结构变了），应 bump minor (0.2.0)。但主 Agent 选了 patch (0.1.68)，理由是 `test_cli.py` hard-code `"0.1."`，minor 会破坏测试。用户指出后回退重做。

**改进**：
```yaml
# dispatch-protocol.md P8 派发 prompt 模板（追加）

## 版本 bump 判定
- P2 packages 声明的改动性质决定 bump 类型：
  - 公共 API 行为变化 / 破坏性变更 → major
  - 加功能 / 内部重构改 API（向后兼容）→ minor
  - 修 bug / 不改 API 行为 → patch
- 测试缺陷不应影响版本号决策：测试 hard-code 版本号 → 修测试，不降级版本
- bump 后必须重跑 P5 gate（版本号变化可能影响版本敏感的测试）

## 判定流程
1. 读 P2-design.md 的 packages/domains 声明
2. 对照 P4 实际改动，判断公共 API 是否变动
3. 按上表选 bump 类型
4. 选 patch 但 P2 声明了新功能/API 变动 → 自动升级为 minor
```

**附加规则**：在 `state-machine.md` 中明确"测试缺陷不构成降级理由"：
```
注意：版本 bump 决策不应受测试缺陷影响。
若 bump 后 P5 gate 因 hard-code 断言失败：
  ✅ 正确做法：修测试（改为读 __version__ 等），保持目标版本
  ❌ 错误做法：降级版本号迁就测试缺陷
```

**验收标准**：P8 派发 prompt 包含 bump 判定规则；主 Agent 在 P8 输出文档中显式声明 bump 类型 + 理由（方便人复核）。

---

### 改进 4：P8 bump 后必须重跑 P5 gate

**位置**：`state-machine.md` 的 P8 转移规则

**现状**：
```
P8 --[每个声明的 package 的发布检查命令 exit 0 + git diff 确认各包 version bump + CHANGELOG]--> READY
```

**问题**：P8 gate 检查的是"发布检查命令 exit 0"，但**不包含"bump 后 P5 回归"**。版本号是全局变量，bump 后可能有版本敏感的测试（如 hard-code 版本字符串）失效。

**证据**：T022 周期 2 P8 中，bump 到 0.2.0 后跑 pre-publish-quick 才发现 2 个 test_cli 测试失败（`assert "0.1." in output`）。如果 P8 转移规则包含"bump 后重跑 P5 gate"，可以在更早的步骤发现。

**改进**：
```yaml
# state-machine.md P8 转移规则（修订）
P8 --[
  bump-version 后重跑 P5 gate（pytest -q exit 0 AND failed==0）AND  # 新增
  每个声明的 package 的发布检查命令 exit 0 AND
  git diff 确认各包 version bump AND
  CHANGELOG 已更新
]--> READY

# 理由：版本号是全局变量，bump 后可能影响任何版本敏感的测试
# P5 gate 在 bump 前跑通不保证 bump 后仍通过
```

**附加指引**：在 `dispatch-protocol.md` 的 P8 派发 prompt 中追加：
```
## P8 bump 后回归
bump-version 后，必须立即重跑 P5 gate 命令。
若因版本号变化导致测试失败：
  ✅ 修测试（不改 __version__ 等动态值的断言）
  ❌ 不降级版本号
```

---

## 三、🟠 高优改进（次优先）

### 改进 5：P6 明确"写跑分离"两阶段边界

**位置**：`dispatch-protocol.md` 的 P6 派发 prompt + `state-machine.md` 的 P6 流程

**现状**：dispatch-protocol 说"写跑分离"——subagent 写脚本，主 Agent 跑。但 P6 的"客观信息查证"（URL、DOM 选择器、API 端点）本身就需要跑 Playwright inspect DOM。边界模糊。

**证据**：T022 周期 2 P6 中，主 Agent 继承 compact 前的 p6-bdd-verify.ts 脚本并直接跑，未重新评估是否应派发 subagent 写。这是降级行为。

**改进**：
```markdown
## P6 Playwright 验收三阶段

### 阶段 A（subagent）：写验收脚本
- 输入：BDD 条件 + dispatch-context.md（主 Agent 已查证的选择器/URL）
- 产出：Playwright 脚本文件
- 返回：脚本路径 + 一句话摘要

### 阶段 B（主 Agent）：跑脚本
- 跑 subagent 写的脚本
- 看 exit code + 摘要
- 必要时做最小修复（改选择器/timeout/URL）属于"跑命令"的一部分

### 阶段 C（主 Agent）：仲裁（如需要）
- vision-helper 报 blocker 但 DOM 验证 PASS → 派第二轮截图 → 仲裁
- 详见改进 6

## 主 Agent 的"inspect DOM"属于查证职责
- 主 Agent 可以跑最小 inspect 脚本（只查 DOM 结构，不做断言）
- 产出 dispatch-context.md 的"选择器清单"
- 这是主 Agent 合法职责，不属于"写脚本"
```

**验收标准**：P6 派发 prompt 明确三阶段；subagent 收到的是"写脚本"任务而非"自查 + 写脚本"。

---

### 改进 6：P6 明确证据优先级（DOM > 交互 > vision 视觉分析）

**位置**：`state-machine.md` 的 P6 转移规则 + `dispatch-protocol.md` 的 P6 派发 prompt

**现状**：P6 gate 要求 `vision-analyst YAML summary.blocker_count == 0`。但 vision-helper 的视觉判断可能误判（截图时机、主题对比度、fullpage 渲染问题），而 DOM 验证（innerHTML 长度、元素存在性）是更可靠的行为证据。agate 没有给出仲裁规则。

**证据**：T022 周期 2 P6 中，第一轮 7 张截图中 3 张被 vision-helper 判为 blocker（"渲染空白"）。实际 DOM 验证：mermaid SVG 7103 字符、plantuml 3026 字符、SVG block 233 字符——三个图表都渲染成功。主 Agent 陷入"信视觉还是信 DOM"的矛盾。

**改进**：
```markdown
## P6 行为验证证据优先级（高→低）

1. **DOM 结构验证**（最可靠）：innerHTML 长度、元素存在性、class 状态
2. **交互响应验证**（可靠）：点击后 class 变化、modal 出现/消失、URL 跳转
3. **vision-helper 视觉分析**（辅助证据）：可被 1/2 覆盖

## 冲突仲裁规则

当 vision-helper 报 blocker 但 DOM 验证 PASS 时：

1. 主 Agent 应补充 DOM 级证据（截图 + page.evaluate 输出）
2. 主 Agent 派发第二轮截图（换主题/换时机/换 viewport）
3. vision-analyst 重新分析第二轮截图
4. 第二轮 blocker_count == 0 → gate 通过
5. 第二轮仍 blocker_count > 0 → 标 [NEED_CONFIRM] 交人判断
6. 禁止主 Agent 自行裁定"视觉误判，行为为准"——必须有第二轮证据或人工确认

## 仲裁记录

主 Agent 在 P6-acceptance.md 中记录仲裁过程：
- 第一轮 vision-helper 结论：blocker=3
- 第二轮（light 主题 + 等待渲染完成）vision-helper 结论：blocker=0
- 仲裁结果：通过
```

**验收标准**：P6 gate 在 vision-helper 报 blocker 时，强制要求第二轮截图或 [NEED_CONFIRM]，不允许主 Agent 自行裁定。

---

### 改进 7：P7 增加 DEVIATION 升级 BLOCKER 的判定标准

**位置**：`state-machine.md` 的 P7 转移规则 + `dispatch-protocol.md` 的 P7 派发 prompt

**现状**：
```
P7 --[! grep -qE '^\s*-?\s*\[BLOCKER\]' P7-consistency.md]--> P8
```

**问题**：当前 gate 只看是否存在 [BLOCKER] 标记。DEVIATION 不阻塞——即使 DEVIATION 涉及 P2 核心设计目标未落地，gate 也通过。

**证据**：T022 P7 发现 DEVIATION-3（useMarkdown 仍 if-else 三分支），实质是 **P2 核心设计未落地**——P2 5.2 明确"原 if/else 三分支 → 新查表路由"，但实现仍是 if/else。但 P7 gate 通过。

**改进**：
```yaml
# state-machine.md P7 转移规则（修订）
P7 --[
  ! grep -qE '^\s*-?\s*\[BLOCKER\]' P7-consistency.md AND
  ! grep -qE '^\s*-?\s*\[DEVIATION-CRITICAL\]' P7-consistency.md  # 新增
]--> P8

# DEVIATION 升级为 DEVIATION-CRITICAL（即升级为 BLOCKER）的条件：
# 1. DEVIATION 对应的 P2 设计项被 P1 BDD 引用为验收条件 → 升级
# 2. DEVIATION 导致某条 BDD 的 PASS 判定不成立（如间接验证替代直接验证）→ 升级
# 3. DEVIATION 是 P2 核心设计目标（非边缘改进）且实现完全未落地 → 升级
```

**附加指引**：在 `architect.md`（P7 角色）的输出规范中明确 DEVIATION 分类：
```
## DEVIATION 分类

DEVIATION 标注必须注明"涉及 P2 哪个设计目标"：
- DEVIATION 涉及 P2 核心设计目标 → 标 [DEVIATION-CRITICAL]（升级为 BLOCKER）
- DEVIATION 涉及行数预算/命名风格等非核心 → 标 [DEVIATION]（保持）
```

**验收标准**：gate 工具能识别 [DEVIATION-CRITICAL] 标记并拒绝通过。

---

### 改进 8：compact 恢复后增加环境一致性验证

**位置**：`state-machine.md` 的"抗中断恢复"步骤

**现状**：state-machine.md 假设"文件状态 = 环境状态"，但 compact 后环境可能已变化（debug backend 停止、entry 删除重建、端口释放）。.state.yaml 记录的 slug/URL/端口在恢复时可能已失效。

**证据**：T022 周期 2 中，compact 恢复后 .state.yaml 记录的 `test_entry_slug: "1x1w9t"`（前序会话创建但因 API 错误被删除重建）。主 Agent 按 .state.yaml 跑脚本，浪费 1 轮 Playwright 调试。

**改进**：
```markdown
## compact 恢复协议（修订）

主 Agent 在单步函数步骤 1 之后增加：

### 步骤 1.5：环境一致性验证

若 .state.yaml 含 p6_context（URL/slug/端口）或类似环境状态字段：

1. curl 验证 debug backend 是否还在运行
   ```bash
   curl -sf --max-time 5 {debug_backend_url}/health
   ```
2. curl 验证 test entry 是否还存在
   ```bash
   curl -sf {api_base}/entries/{slug}
   ```
3. 验证 Chrome CDP 端口是否可用
   ```bash
   curl -sf --max-time 3 http://localhost:{cdp_port}/json/version
   ```
4. 若任一失效：
   - 重新创建对应资源
   - 更新 .state.yaml 的环境状态字段
   - commit 修订
5. 若环境全部失效 → PAUSED 报告人工

## .state.yaml 环境状态字段示例

```yaml
p6_context:
  debug_backend: "http://127.0.0.1:8888"
  test_entry_slug: "zg71s7"
  chrome_cdp_port: 18800
  env_verified_at: "2026-06-26T03:25:00"
```
```

**验收标准**：state-machine.md 增加步骤 1.5；.state.yaml 模板增加 env_verified_at 字段。

---

## 四、改进优先级与依赖关系

```
🔴 阻断级（建议 1-4）—— 必须先修，修复 P4/P6/P8 gate 的设计缺陷
   ↓
🟠 高优（建议 5-8）—— 次优先，修复 P6/P7 验收和恢复协议
   ↓
（执行纪律改进）—— 主 Agent 在协议空白处的决策纪律（如版本 bump 应反映变更性质）
```

**依赖关系**：
- 改进 5（写跑分离）依赖改进 1（P4 子目标覆盖）—— 因为 P4 implementer 的产出粒度决定了 P6 验收脚本的复杂度
- 改进 7（DEVIATION 升级）独立于其他改进
- 改进 8（环境一致性）独立于其他改进

---

## 五、与现有 review 的关系

| 文档 | 视角 | 范围 |
|------|------|------|
| `docs/reviews/agate-postmortem-T022-2026-06-26.md` | T022 任务复盘 | PeekView 项目的 T022 执行过程 |
| `docs/reviews/agate-postmortem-T016-2026-06-20.md` | T016 任务复盘 | PeekView 项目的 T016 执行过程 |
| `~/.agate/docs/reviews/agate-postmortem-T019-2026-06-23.md` | T019 任务复盘 | agate 仓库的 T019 执行过程 |
| `~/.agate/docs/reviews/agate-review-20260626-1.md` | 协议评审 | agate 协议本身的 19 个改进点 |
| **本文件** | agate 机制改进建议 | 基于 T022 证据，提出 agate 机制 8 个具体改进 |

本文件与 `agate-review-20260626-1.md` 的差异：那份是从 agate 仓库整体审计出发（YAML 解析、文档一致性、角色定义），本文件是从 T022 单任务证据出发（gate 设计的具体失败模式）。两者互补，不重叠。

---

## 六、改进实施建议

### 6.1 优先级矩阵

| 改进 | 影响范围 | 实施成本 | 优先级 |
|------|----------|----------|--------|
| 1. P4 子目标覆盖 | 大（多任务）| 中（需修改 dispatch-protocol + state-machine + gate 工具）| 🔴 P0 |
| 2. P6 BDD 数量对照 | 大 | 低（gate 工具加一个 grep + 比较）| 🔴 P0 |
| 3. 版本 bump 判定 | 中 | 低（文档级改动）| 🔴 P0 |
| 4. bump 后重跑 P5 | 小 | 低（state-machine 改一条规则）| 🔴 P0 |
| 5. P6 写跑分离 | 中 | 中（dispatch-protocol 改 P6 派发模板）| 🟠 P1 |
| 6. 证据优先级 | 中 | 中（state-machine 改 P6 规则）| 🟠 P1 |
| 7. DEVIATION 升级 | 中 | 低（architect.md + state-machine 改规则）| 🟠 P1 |
| 8. 环境一致性 | 小 | 低（state-machine 加步骤 1.5）| 🟠 P1 |

### 6.2 实施步骤

1. **第一步**：4 个 🔴 P0 改进（gate 设计缺陷）—— 在 agate 仓库 master 分支独立 PR
2. **第二步**：在 1-2 个后续任务中验证 gate 改进有效（如果再有"子目标遗漏"或"BDD 数量不全"，说明 gate 改对了）
3. **第三步**：4 个 🟠 P1 改进（验收协议和恢复协议）
4. **第四步**：更新 LIMITATIONS.md——把"gate 无法检测某些失败模式"作为已知局限记录

### 6.3 验证机制

每个改进实施后，应在下一个非平凡任务中验证：
- 改进 1：P4 implementer 是否在 commit message 中列出"已覆盖子目标"
- 改进 2：P6-acceptance.md 是否包含全量 P1 BDD（条数一致）
- 改进 3：P8 文档是否显式声明 bump 类型 + 理由
- 改进 4：bump 后 pre-publish 是否因版本敏感测试失败（应能更早发现）
- 改进 7：P7 一致性检查是否升级 [DEVIATION-CRITICAL]

---

## 七、结语

T022 暴露的 agate gate 设计缺陷不是孤立问题——T019（srcdoc 方案未做最小验证就推进到 P6）、T016（subagent 失败后主 Agent 违规降级）也有类似的"机制缺口放大了执行错误"问题。但 T022 是最清晰的证据：周期 1 的 ~50% token 浪费**完全归因于 P4/P6 gate 缺陷**——主 Agent 即使严格按协议执行，也无法被现有 gate 检测"P4 漏子目标"和"P6 BDD 数量不全"。

**核心启示**：agate 的 gate 设计是抗错误的第一道防线。如果 gate 不能拦截某些失败模式，主 Agent 偶尔犯错就会导致整个周期废弃。优先级：先修复 gate，再改进执行纪律。

---

*本 review 基于 T022 单任务证据。所有改进建议均标注为"初步假设，需更多任务验证"。*