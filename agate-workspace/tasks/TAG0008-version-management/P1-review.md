---
phase: P1
task_id: TAG0008
type: review
parent: P1-requirements.md
trace_id: TAG0008-P1R2-20260816
status: approved
created: 2026-08-16
agent: requirements-review
---

# P1 需求基线复核评审 — TAG0008 agate 版本管理机制（v1）【复核轮】

评审对象：`P1-requirements.md`（378 行，rev2，31 BDD，status: revised）
评审基准：`P0-brief.md`（6 组件锁定范围 + known_risks）、`AGENTS.md`（测试平台无关等约定）
评审角色：requirements-review（独立视角，只审不写）
复核轮定位：上一轮评审给出 status=needs-revision（5 处修订 + 影响面表 4 处缺口 = 9 项），本轮逐项核实落实 + 全清单复核。

## 一、上轮 9 项复核判定（逐条已落实 + 证据）

| # | 上轮意见 | rev2 落实情况 | 判定 |
|---|----------|--------------|------|
| 1 | BDD-28（现 BDD-30）legacy 回退机制语义不清 | BDD-30 Then 显式定义兜底规则：**"将 `~/.agate` 软链目标（旧 checkout 的 `agate/` 子目录）直接解析为 AGATE_ROOT（即"legacy 软链目标本身 = AGATE_ROOT"）"**，Given 明示"无版本目录、无 `.agate-version`、无 current/latest 指针"——无 current 场景的解析锚点已消除，P4 实现无歧义 | **已落实**（L326） |
| 2 | I-8 打包失败路径无 BDD | 新增 **BDD-24**：三失败场景（tag 不存在 / pip download 网络失败 / 目标平台 wheel 缺失）共用同一失败契约（退出码非 0 + stderr 指明原因 + 不产可用 bundle），注明"逐一独立运行，P6 可逐场景验收"；I-8 引用"验收见 BDD-24" | **已落实**（L290-294） |
| 3 | BDD-23（现 BDD-25）平台不匹配 Then 双可选项弱化二值性 | BDD-25 Then 收敛为**单信号 fail-closed**：输出平台不匹配警告（须含 platform 字段值 + 当前机器平台）+ 退出码非 0（拒绝安装），无双可选项 | **已落实**（L296-299） |
| 4 | I-1 空文件场景未显式覆盖 | BDD-14 Given 显式补空文件变体（"**或为空文件**——空文件归入"非法格式"统一处理"），对应 I-1 三要素全验收 | **已落实**（L234-237） |
| 5 | I-11 引用保护无验收 BDD | 新增 **BDD-6**：项目 `.agate-version` 仍引用 v0.43.0 时 `--uninstall` 被拒绝（退出码非 0 + stderr 警告含版本号与引用来源 + 目录仍存在）；I-11 引用"验收见 BDD-6"；与 BDD-5（无引用才删）形成对照 | **已落实**（L192-195） |
| 6 | 影响面表 §2.1 漏 3 脚本 | §2.1 已补 `agate-inject-card.py` / `agate-next-card.py` / `agate-render-dispatch-prompt.py` 三行（均标注"复核：内联 `_agate_root` 非走 agate_common，P2 评估是否统一"）；§2.4 结论 6 同步补注 | **已落实**（L85-87、L131） |
| 7 | 影响面表 §2.2 漏 2 文档 | §2.2 已补 `agate/adr.md`（L241 ADR-008 论据复核）+ `agate/assets/templates/project.md`（L16 默认安装位置语义复核） | **已落实**（L106-107） |
| 8 | §2.3 测试路径前缀不实（unit/） | 已修正为 `agate/tests/integration/test_pre_commit_hook.py` / `test_commit_msg_self_gate_integration.py` / `test_pre_push_hook.py` / `test_dispatch_context_card.py` | **已落实**（L122） |
| 9 | test_agate_summary.py 表述"需查"含糊 | 已改为"不存在（全仓 grep `agate-summary`/`agate_summary` 于 tests/ 零命中，rev2 实查确认）｜**新增**" | **已落实**（L119） |

**复核证据（worktree 实查）**：
- 3 脚本全部存在且含内联解析：`agate-inject-card.py` L28 `_agate_root()`、`agate-next-card.py` L35 `_resolve_agate_root()`、`agate-render-dispatch-prompt.py` L32 `_resolve_agate_root()`（grep 命中）→ §2.1 新增行属实。
- `agate/adr.md` L241 实查含"和 `~/.agate` 软链接让 gate 脚本自动跟随升级是同一套机制"；`agate/assets/templates/project.md` L16 实查含"如果你的 agate 没装在默认位置 `~/.agate`"→ §2.2 新增行属实。
- 4 个测试文件 glob 实查均在 `agate/tests/integration/` → 前缀修正属实。
- `test_agate_summary.py` glob 全 tests/ 树零命中 → "新增"表述属实。

## 二、BDD 评审（31 条逐条判定，复核轮）

> 判定键：退出码 + 文件/软链存在 + worktree list + manifest 字段值 + stderr 输出，全部客观可测、可二值判定。
> 覆盖维度：数据✓/✗ 前端✓/✗ 多端✓/✗ 边界✓/✗ 兼容✓/✗（本任务无前端，前端维度 ✗-N/A）。

### agate-install（BDD-1 ~ BDD-8）
- BDD-1（无参建 latest 纯指针）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✗ 兼容✓（软链保留）。二值：latest 存在 + 解析指向 vX.Y.Z/。
- BDD-2（指定版本 worktree 检出 tag）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✗ 兼容✗。`git worktree list` 可查证，二值明确。
- BDD-3（重复安装幂等）: **PASS**。数据✗ 前端✗-N/A 多端✗ 边界✓ 兼容✗。退出码 0 + worktree 不重复，对应 I-12。
- BDD-4（current 默认 → latest）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✗ 兼容✓。与 BDD-11 语义一致。
- BDD-5（卸载删目录 + 清理指针）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✓（latest/current 悬空指针）兼容✗。与 BDD-6 对照构成"无引用删 / 有引用拒"闭环。
- BDD-6（项目引用时卸载被拒）【上轮修订 5，复核通过】: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✓（被锁版本）兼容✓（§8.3 引用即保护）。退出码非 0 + stderr 警告（版本号 + 引用来源）+ 目录仍存在，三信号均二值可测。
- BDD-7（探测全齐 exit 0）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✗ 兼容✗。逐项结果输出可测。
- BDD-8（缺项非 0 + 分平台修复指引）: **PASS**。数据✓ 前端✗-N/A 多端✓（Linux/Windows 双指引）边界✓ 兼容✗。对应 I-13；平台分支断言符合平台无关原则。

### agate-resolve（BDD-9 ~ BDD-14）
- BDD-9（项目锁定命中）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✗ 兼容✗。AGATE_ROOT + 版本号，二值明确。
- BDD-10（cwd 向上查找）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✓（目录层级）兼容✗。asdf 模式核心行为。
- BDD-11（无声明回退 current→latest + 原因）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✗ 兼容✓（存量无声明项目）。原因标注可测。
- BDD-12（AGATE_ROOT env 最高优先）: **PASS**。数据✓ 前端✗-N/A 多端✓（env 契约）边界✗ 兼容✓（既有 env 语义不破坏）。优先级链显式。
- BDD-13（声明未装 → 回退 current + 警告 + exit 0）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✓ 兼容✗。对应 I-2 红线（不静默禁用）；与 BDD-17 fail-closed 语义一致。
- BDD-14（非法格式 + 空文件 → 回退 + 警告）【上轮修订 4，复核通过】: **PASS**。数据✓（非法格式/未知工具前缀/空文件三要素）前端✗-N/A 多端✗ 边界✓ 兼容✗。I-1 三要素全验收，空文件归入非法格式统一处理，二值清晰。

### hook 解析入口（BDD-15 ~ BDD-19）
- BDD-15（install-hook 装固定解析入口）: **PASS**。数据✓ 前端✗-N/A 多端✓（解析入口机制）边界✗ 兼容✓（切版本不重装）。对应 I-3。
- BDD-16（项目 A/B 版本隔离互不干扰）: **PASS**。数据✗ 前端✗-N/A 多端✓ 边界✗ 兼容✗。核心需求验收，可测。
- BDD-17（resolve 失败 hook 回退 current 跑 gate，不静默放行）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✓ 兼容✗。对应 I-2/known_risk #1，fail-closed 明确。
- BDD-18（切版本不重装 hook）: **PASS**。数据✓ 前端✗-N/A 多端✓ 边界✗ 兼容✓。核心需求验收。
- BDD-19（Windows 复制模式解析入口可用）: **PASS**。数据✓ 前端✗-N/A 多端✓ 边界✗ 兼容✓（TAG0004 先例复用）。`AGATE_HOOK_COPY_MODE=1` 模拟 + `.agate-root` 恢复，符合平台无关原则。

### summary 集成（BDD-20 ~ BDD-21）
- BDD-20（显示项目版本 + .agate-version 原因）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✗ 兼容✗。对应 I-6 语义迁移。
- BDD-21（显示全局 current 回退原因）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✗ 兼容✓。二值明确。

### 离线部署包（BDD-22 ~ BDD-29）
- BDD-22（pack-offline 产出 bundle + manifest）: **PASS**。数据✓ 前端✗-N/A 多端✓（--platform）边界✗ 兼容✗。对应 I-8 主路径。
- BDD-23（manifest 字段可解析）: **PASS**。数据✓（platform + sha256 非空）前端✗-N/A 多端✗ 边界✗ 兼容✗。对应 I-9 打包侧。
- BDD-24（打包失败路径非 0 退出 + 不产坏包）【上轮修订 2，复核通过】: **PASS**。数据✓ 前端✗-N/A 多端✓（目标平台维度）边界✓（tag 不存在/网络失败/wheel 缺失）兼容✗。三场景共用同一失败契约、各自独立可跑，退出码非 0 + stderr 原因 + manifest 缺失/不完整均可二值判定；对应 I-8 后半句，P6 逐场景可验收。多场景单条属显式声明的设计取舍（见「非阻塞观察 1」）。
- BDD-25（平台不匹配警告 + 拒绝安装）【上轮修订 3，复核通过】: **PASS**。数据✓ 前端✗-N/A 多端✓（平台维度）边界✓ 兼容✗。已收敛为单信号 fail-closed（警告含 platform 字段值 + 当前机器平台 + exit 非 0），对应 I-10，二值性恢复。
- BDD-26（checksum 不匹配拒绝安装）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✓（篡改）兼容✗。对应 I-9 校验侧，exit 非 0 + 指出组件。
- BDD-27（wheels 离线安装成功）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✗ 兼容✓（离线场景）。对应 P0-brief 离线部署。
- BDD-28（安装完成建版本目录 + hook 指向 + 验证闭环）: **PASS**。数据✓ 前端✗-N/A 多端✓（Linux 软链/Windows 复制）边界✗ 兼容✗。对应 P0-brief 内网安装器。
- BDD-29（--skip-python / --skip-pillow 勾选覆盖）: **PASS**。数据✓ 前端✗-N/A 多端✗ 边界✓（跳过分支）兼容✗。对应 P0-brief 勾选语义。

### 向后兼容红线（BDD-30 ~ BDD-31）
- BDD-30（存量单软链用户不受破坏）【上轮修订 1，复核通过】: **PASS（判定主体）**。数据✗ 前端✗-N/A 多端✗ 边界✓（legacy 无指针布局）兼容✓（存量单软链）。Then 已定义"`~/.agate` 软链目标本身 = AGATE_ROOT"的兜底规则，消除了上轮指出的 P4 实现歧义；与 BDD-11（有 current 时回退 current）通过 Given 分支互补、不矛盾。多断言 Then 为正负信号组合（详见「非阻塞观察 2」），仍二值可测。
- BDD-31（gate 判定逻辑本身未改）: **PASS**。数据✗ 前端✗-N/A 多端✗ 边界✗ 兼容✓（红线：只改解析层不动判定逻辑）。`git log/diff` 可证。

**BDD 编号/格式核查**：`#### BDD-NN:` 格式统一，BDD-1 ~ BDD-31 连续不跳号（grep 复核 31 条锚点）；每条单一 Given-When-Then（BDD-24 三场景为显式声明的单条共用契约，见观察 1）；无中间态判定词。

## 三、隐含需求覆盖（I-1 ~ I-16，五维度复核）

- **数据维度**：I-1（语法规范 + 空文件，BDD-9/14）、I-9（manifest checksum 闭环，BDD-23/26）、I-11（uninstall 指针清理 + 引用保护，BDD-5/6）→ **覆盖**
- **前端维度**：本任务无前端 → **N/A**（反模式自检已声明）
- **多端维度**：I-3（解析入口间接 exec + env 最高，BDD-12/15）、I-4（Windows 复制模式，BDD-19）、I-10（平台核对 fail-closed，BDD-25）→ **覆盖**
- **边界维度**：I-2（解析失败回退不静默禁用，BDD-13/17）、I-8（打包失败路径，BDD-24 ✓）、I-12（重复安装幂等，BDD-3）、I-13（探测缺项，BDD-8）、I-16（worktree 载体，BDD-2/3/5）→ **覆盖**
- **兼容维度**：I-5（agate_common 统一解析 + 3 脚本归口 P2 评估）、I-6（summary 语义迁移，BDD-20/21）、I-7（文档全联动，影响面表 §2.2）、I-14（新增测试 + 平台无关，影响面表 §2.3）、I-15（install.sh 兼容保留 + BDD-30）→ **覆盖**

覆盖结论：I-1 ~ I-16 逐条可回溯到 BDD 或影响面表，上轮唯一缺口（I-8 失败路径）已由 BDD-24 闭环。

## 四、裁剪评审

- **phases: [P1, P2, P3, P4, P5, P6, P7, P8]**：frontmatter 与 §6 正文一致，无跳过项，理由 = P0-brief known_risk #7（走完整 P0-P8）→ **充分**
- **risk_level=high**：hook 改造影响所有下游项目 + `~/.agate` 单软链→目录迁移影响存量用户 + Windows 软链退化 + 离线包平台/校验复杂度，与 P0-brief known_risks 逐条对应 → **匹配**
- **capability_requirements 三态**：git-worktree=available ✓；windows-runtime=supplementable（CI matrix + 模拟，诚实声明未实测）✓；external-network=available ✓；pyyaml/pillow=available ✓。无 GAP、未设 requires_minimal_validation → **正确**

## 五、P1 纯净性

- BDD-27 When 含 `pip install --no-index --find-links wheels/`：源自 P0-brief 锁定范围，**可接受**。
- BDD-19 提及 `AGATE_HOOK_COPY_MODE=1`：既有测试机制概念（platform-notes 先例），**非新掺方案**。
- BDD-30 Then 的 legacy 兜底规则：是对"向后兼容红线"的行为定义（做什么），非实现绑定（怎么写），**可接受**。
- 其余 BDD 描述 CLI 命令 + 系统行为 + 客观信号，无"调用 resolve()"类实现绑定 → **纯净**（L333-340 反模式自检逐条属实）。

## 六、影响面表专项复核（rev2 补齐项核实）⭐

上轮 4 处联动点缺口（known_risk #6 红线）已全部补齐，抽样实查：

1. **3 脚本**（agate-inject-card / agate-next-card / agate-render-dispatch-prompt）：§2.1 已列，实查 3 文件均含内联 `_agate_root`/`_resolve_agate_root`（env → 上溯两级），标注"P2 评估统一走 agate_common" → **属实，行动项明确**
2. **2 文档**（adr.md / templates/project.md）：§2.2 已列，实查 adr.md L241 / project.md L16 与表注内容逐字匹配 → **属实**
3. **测试路径前缀**：4 个文件 glob 实查均在 `agate/tests/integration/` → **修正属实**（P7 交叉核对基线不再落空）
4. **test_agate_summary.py**：标"新增"，glob 全 tests/ 零命中 → **表述属实**

其余上轮已复核通过的联动点（pre-commit-gate.sh 薄壳单行自定位 / install-hook.py 三级契约 / agate_common.resolve_agate_root / ci-gate-backstop.py `_AGATE_ROOT` 上溯 / agate-summary.py git describe / check-protocol-consistency.py L765）维持原判定，无变化。§2.4 关键扫描结论 6（3 脚本内联解析）与新增影响面行一致。

## 七、非阻塞观察项（不构成打回，P2 设计期参考）

1. **BDD-24 三 Given 场景合为单条**：严格按"每条单一 GWT / 多场景拆独立编号"标准，三场景可拆为 BDD-24a/b/c；但三场景共用同一失败契约且已显式声明"逐一独立运行，P6 可逐场景验收"，二值性无歧义——接受为显式声明的取舍，P2 设计时若发现契约分化再拆分。
2. **BDD-30 复合 Then**：含正向信号（legacy 软链目标直接解析为 AGATE_ROOT）与负向红线（无 breakage、无静默禁用）。正信号已消除上轮歧义，负信号靠 gate 退出码可证，仍二值可测——接受。
3. **BDD-8 未显式断言"不自动装系统级依赖"**：P0-brief 明确该约束，但 `--check` 的诊断性输出（指引而非执行）使该约束近乎平凡成立，留 P4 实现约束即可，无需独立 BDD。

## 结论

**Status: approved**

上轮 9 项（5 处修订 + 影响面表 4 处缺口）已全部真实落地且语义正确：legacy 兜底规则（"`~/.agate` 软链目标本身 = AGATE_ROOT"）消除 P4 解析歧义；新增 BDD-6（卸载引用保护）、BDD-24（打包失败路径）均可二值判定且编号连续（29 → 31，BDD-1~31 无跳号）；BDD-14 空文件变体、BDD-25 平台不匹配单信号 fail-closed 修订到位；影响面表 3 脚本 + 2 文档补齐且实查属实，integration/ 路径前缀与 summary 测试"新增"表述修正属实。

完整清单复核通过：31 条 BDD 全部可二值判定、单一 GWT、编号连续；I-1~I-16 覆盖五维度（前端 N/A）；跨条一致性无矛盾（BDD-5/6 有引用拒/无引用删对照、BDD-11/30 有指针/无指针互补、BDD-13/17 fail-closed 一致）；裁剪合理（phases 全阶段 + high 匹配 + 无 GAP）；P1 纯净性良好。P0-brief 6 组件 + 环境探测 + 向后兼容红线全覆盖，[NO_NEED_CONFIRM] 无阻塞项。可推进 P2。

**[PROD_NOT_TOUCHED]**（仅只读评审文档 + 对 worktree 只读 grep/glob 抽查，未修改任何生产文件；仅覆盖产出 P1-review.md）
