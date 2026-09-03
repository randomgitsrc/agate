---
phase: P1
task_id: TAG0031
type: problems
parent: P0-brief.md
trace_id: TAG0031-P1-20260904
status: draft
created: 2026-09-04
agent: analyst
# ── v2.0 机器字段 ──
risk_level: medium
phases: [P1, P2, P3, P4, P5, P6, P7, P8]
packages: [agate-scripts, agate-tests, agate-docs]
domains: [backend]
# 跳过风险: 无阶段裁剪——risk_level=medium（非 low）不可裁 P3；受影响源码脚本数≥5
#   （agate_common.py / agate-pack-offline.py / install-offline.py / agate-install.py /
#   check-gate.py，check-pruning.py 视 BDD-6/7 实现方式可能追加）超过 P7 裁剪跳阶阈值
#   （≤5 源文件 + coupling_checklist），故 P7 不裁剪，全阶段保留。
---

## 需求复述

批量关闭 7 条历史遗留 open 技术债（`debt/tech-debt.md` DEBT0002/0003/0004/0007/0016/0017/0018），
按文件域分三簇：

1. **版本管理域**（DEBT0002/3/4，离线包 pack/install/uninstall 相关）：
   - DEBT0002：`agate-pack-offline.py` 与 `install-offline.py` 各自实现了逐字节相同的
     `compute_sha256`（目录 hash 约定：按相对路径排序逐文件 sha256 拼接再整体 sha256）——
     合并为 `agate_common.py` 共享实现，两侧改 import。
   - DEBT0003：离线 manifest 只有 checksum（防损坏），未签名（不防整包替换）——本任务范围
     内以文档明示信任边界为准（P0-brief out-of-scope 已排除完整签名体系实现）。
   - DEBT0004：`agate-install.py` 的 `_find_references`（卸载引用保护扫描）有深度 ≤4 /
     mtime 365 天窗口的限流，边界外引用漏扫时无提示——命中限流边界需 stderr WARNING。
2. **测试隔离**（DEBT0007）：`test_check_pruning.py` 部分用例曾依赖真实 git 暂存区而非隔离
   fixture——**本任务范围经 P1 核实已收窄**（详见下方「P0-brief 时效性质疑」），核心生产代码
   缺陷已被 TAG0024（commit `e2357fc`）修复，本任务聚焦补齐 closure_criteria 剩余项 + debt
   登记闭合。
3. **check-gate.py 健壮性**（DEBT0016/17/18）：
   - DEBT0016：`gate_p4` 的 CODE-MAP.md 路径用本地 `task_dir` 向上两级 dirname 算术推导，
     未调用 `agate_common.resolve_workspace` 权威函数——改为调用权威函数。
   - DEBT0017：`gate_p4`「## 新增文件核对表」用子串 `in` 判定，在自指/dogfooding 场景（正文
     用说明性散文提及该标题字符串）产生假阴性——改整行/标题级正则判定。
   - DEBT0018：`check-gate.py` 的 `agate_common` import 降级 stub（`except ImportError`
     兜底块）对关键读取器（`read_rules_yaml`/`count_p7_markers`/`count_p6_pass_fail`/
     `count_code_map_lines`）返回 `0`/`None`/空，安装破损边缘下消费分支呈 false-PASS——
     改为显式失败（fail-closed）。

全部 7 条 DEBT 均为低风险脚本健壮性修复，**无新机制设计、无协议文档面新增改动**（仅涉及既有
脚本内部实现调整 + 用户可见文档信任边界说明补充）。

## P0-brief 时效性质疑

已核对 P0-brief 时效性，**命中一处轻微漂移**（非严重，记录后继续，不阻塞）：

```
[P0_STALE: DEBT0007（测试隔离）known_risks 第 4 条的『已解决前提』实际已被 TAG0024 部分解决——
check-pruning.py 的 _staged_source_count（L84-100）当前代码在 L88/L98 已对 run_git 传入
cwd=task_dir（git blame 定位到 commit e2357fc，2026-08-25，wf(TAG0024-P4) 提交），且已有回归
测试 test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0（docstring 明确标注
"BDD-30 回归（测试隔离修复）"）。DEBT0007 原始报告命名的三个失败用例
（test_p2_6e_prune_p7_coupling_checklist_exit_0 / test_p2_52_yaml_list_phases_exit_0 /
test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0）均已追加
env={"GIT_CEILING_DIRECTORIES": str(tmp_path)} 隔离手段。实测（2026-09-04，本 worktree）
`pytest -k "test_p2_6e_... or test_p2_52_... or test_p2_52b_... or test_p2_6f_..."` 4 项全部
PASS。tech-debt.md 中 DEBT0007 status 仍为 open，evidence 未引用此修复，登记条目滞后于代码现状。]
```

**严重性判定**：不判定为严重漂移——严重判据 3 条逐条核对：① `task` 目标方案未变（7 条 DEBT 批量
关闭的整体方案仍成立，6/7 条完全未受影响）；② `executor_env` 平台前提未变；③
`known_risks`「已解决前提」命中的是**该 4 条 known_risks 中的第 4 条单条**，且命中方式是「风险的
应对手段已被部分完成」而非「任务整体目标落空」——DEBT0007 本身仍需要完成 closure_criteria 剩余项
（见下）与 debt 登记闭合，不构成"DEBT0007 这一簇已无事可做"。因此按**轻微漂移**处理：记录 +
调整 DEBT0007 子范围的 BDD 设计（从"设计并实现隔离方案"收窄为"验证既有修复的健壮性 + 补齐
closure_criteria 第 2 条的空白验证 + debt 登记闭合"），不回退 P0。

**判定依据补充**（为何认为 GIT_CEILING_DIRECTORIES 方案已满足"任意 basetemp 位置全绿"要求）：
`GIT_CEILING_DIRECTORIES` 阻断 git 向上遍历发现 `.git` 目录的搜索边界于 `tmp_path`——机制上与
外层真实仓库暂存区的**文件数量**无关（无论真实仓库暂存 0 个还是 200 个文件，只要 ceiling 生效，
`git rev-parse --show-toplevel` 都无法越过 ceiling 找到外层仓库，函数按 `repo_root` 为空返回 0），
故不需要额外用"20+ 文件"场景重复验证数值本身，但仍需在 BDD 中显式覆盖（见 BDD-6），把这条论证
落地为可执行回归，避免只停留在推理层面。

其余 3 条 known_risks（DEBT0002 hash 合并影响面 / DEBT0017 TDD 先红后绿 / DEBT0018
fail-closed 消费方确认）均未命中漂移，`executor_env` 的 merge 模式描述已由主 Agent 在 P0-brief
本轮更新（见 P0-brief 自身的「P0-brief 时效性自检记录」节），P1 阶段无需重复处理。

## 隐含需求识别

| 隐含需求 | 为什么必须 |
|---|---|
| `compute_sha256` 合并后跨平台路径排序一致性不能变 | 现有实现用 `f.relative_to(p).as_posix()` 排序键消除 Windows `\\` 分隔符差异；迁移到 agate_common 时必须原样保留该排序键写法，否则 Windows 侧 hash 值漂移，`install-offline.py` 的 checksum 校验会误报（BDD-1/2） |
| fail-closed 改造（DEBT0018）影响下游 gate 消费方 | `check-gate.py` 的 exit code 被 `pre-commit-gate.sh`/`ci-gate-backstop.py`/`agate-next.py` 等多处消费；改动后需确认这些消费方对新增的"安装破损" exit 1 分支无特殊依赖（本任务只改 agate_common 缺失这一异常分支，正常安装路径逐字节不变，风险已收窄，但仍需全量 pytest 覆盖，见 BDD-13） |
| WARNING/信任边界文案是用户可见行为变更 | DEBT0004 新增 stderr WARNING、DEBT0003 新增文档章节，均属用户可感知的行为/文档变更，按 AGENTS.md 版本发布清单应体现在 CHANGELOG（P8 阶段处理，P1 先声明，不在本阶段落地） |
| DEBT0007 debt 登记闭合格式需与既有先例一致 | `tech-debt.md` 中 DEBT0005/DEBT0006 已有 closed 条目的登记格式（status/closed_at/evidence 追加 closure 记录）可直接复用，避免格式不一致（BDD-7） |
| 同类扫描发现的未处理实例需要拦截手段，不能"发现了就算了" | 见「同类扫描」节，转为 BDD-14 显式声明登记新 DEBT 作为拦截手段 |
| SELF-GATE commit 纪律 | 本任务改 `agate/scripts/*`，触发 SELF-GATE（P0-brief env_constraints 已声明），commit message 须含 `self-gate-review:`/`self-gate-skip:`，此项已知悉，不再单独出 BDD（属流程纪律非验收行为） |
| 多端同步（MCP/CLI） | 本任务全部是 CLI 脚本内部实现，无 MCP 端消费面，判定「无」 |
| 存量数据迁移 | 无数据结构变更（manifest.json 字段不变、.agate-version 格式不变），判定「无」 |

## 同类扫描（强制节）

对 7 条 DEBT 涉及的关键符号/模式做全仓 grep，逐条记录命中数量、文件清单与处理判定：

### 1. `compute_sha256` / hash 目录约定（DEBT0002）

```
grep -rn "def compute_sha256\|compute_sha256(" agate/scripts/*.py
```
命中：`agate-pack-offline.py:51`（定义）+ `:75`（调用）、`install-offline.py:85`（定义）+
`:111`（调用），逐字节相同实现（docstring 互相标注"与 pack/install 侧一致"）。仓内另有
`hashlib.sha256` 用于其他不相关用途（`agate_common.py` 事件哈希链 `GENESIS_HASH`、
`agate-capture-env-baseline.py` 缓存 key、`check-events.py`/`check-judge-verdict.py`/
`pre-commit-gate.py` 各自的哈希链/校验用途）——语义不同，不构成"重复实现同一目录 hash 约定"。

**判定**：仅此 2 处构成 DEBT0002 描述的重复，本次处理（合并入 `agate_common.py`），其余
`hashlib.sha256` 用法本次不处理（用途不同，非同一问题）。

### 2. `_find_references` 卸载引用扫描限流（DEBT0004）

```
grep -rn "_find_references\|_SCAN_MAX_DEPTH\|_SCAN_MTIME_WINDOW" agate/scripts/*.py
```
命中：仅 `agate-install.py`（定义 L230 + 调用 L289 + 常量 L62-63），全仓无第二份实现。

**判定**：唯一实例，本次处理，无遗漏。

### 3. `dirname(dirname(...))` 向上两级路径推导模式（DEBT0016 同类扫描）

```
grep -n "dirname(dirname\|dirname(os.path.dirname" agate/scripts/*.py
```
该宽口径命令全仓命中 **14 行**（逐字节实测，与主 Agent 独立复核一致）。14 行按**推导起点**分两类：

**类别 A——以 `task_dir`（任务工作目录，workspace 相对路径）为推导起点**，共 4 行 / 3 个实例：
- `check-gate.py:983`（注释，逐字复述同一算式）+ `check-gate.py:986`（代码本体）：DEBT0016
  本体，`gate_p4` CODE-MAP 路径推导
- `check-retrospective.py:74`：`_scan_debt_roadmap_signal` 用
  `os.path.dirname(os.path.dirname(os.path.abspath(task_dir...)))` 推导 workspace 根，
  定位 `debt/tech-debt.md`/`roadmap/roadmap.md`
- `agate-render-dispatch-prompt.py:191`：`workspace_render = os.path.dirname(os.path.dirname(task_dir))`
  用于渲染 `{AGATE_WORKSPACE}` 占位符

**类别 B——以 `__file__`/`script_path`（脚本自身文件路径，指向 agate 仓库/安装根）为推导起点**，
共 10 行：`agate-advance.py:59`、`agate_common.py:220`（`resolve_hook_root` 的
`real = Path(script_path).resolve()` 兜底链路）、`agate_common.py:662`、`agate-dispatch.py:68`、
`agate-inject-card.py:47`、`agate-next-card.py:50`、`agate-next.py:86`、
`agate-render-dispatch-prompt.py:46`、`check-structure-consistency.py:115`、
`check-yaml-schema.py:147`。4（类别 A）+ 10（类别 B）= 14，与命令实测命中数逐字节对应。

**为何类别 B 不构成同类**：DEBT0016 描述的风险是"workspace 布局非标准嵌套时静默产出错误路径"——
风险成立的前提是推导起点（`task_dir`）本身依赖 workspace 的相对目录层级约定，一旦该约定被打破
（如经由 `.agate.env` 的 `AGATE_WORKSPACE=` 覆盖工作区位置）推导结果就会静默错位。类别 B 的推导
起点是脚本自身在磁盘上的物理路径（`__file__`/`script_path`），锚定的是 agate **仓库/安装根**而非
**任务 workspace**，不随 workspace 布局变化而变化——脚本文件相对仓库根的层级是固定的部署事实，
不存在"workspace 非标准嵌套"这一风险维度。因此类别 B 的 10 处不纳入 DEBT0016 同类判定，也不登记
新 DEBT。

除 DEBT0016 本体外，类别 A 另命中 2 处同款模式（`check-retrospective.py:74` /
`agate-render-dispatch-prompt.py:191`）。

**判定**：类别 A 的 2 处非本体实例**本次不处理**——P0-brief scope 明确锁定"gate_p4 CODE-MAP 路径"
这一处（`agate/scripts/*` domains 内其余脚本的同款模式属于 P0-brief 未列入的范围，擅自扩大属越界）。
按「同类扫描」规则转入回归拦截：见 BDD-14，登记为新 DEBT 候选，不留白。类别 B 的 10 处不构成同类，
不登记、不追踪。

### 4. 「标题字符串子串 `in` 判定」模式（DEBT0017 同类模式，风险更高的一处）

```
grep -n "not in _read_text(" agate/scripts/check-gate.py
```
除 DEBT0017 本体 `check-gate.py:990`（「## 新增文件核对表」）外，另命中 1 处同款模式且**风险更
高**：`check-gate.py:881`（`gate_p2`，`project_phase: bootstrap` 分支的「## 骨架声明」标题存在性
校验）——`"## 骨架声明" not in _read_text(skeleton_file)`，与 DEBT0017 本体同一子串判定缺陷，但
此处触发的是 **`return 1`（阻断性）**，而 DEBT0017 本体只是 WARNING（非阻断）。也就是说，`gate_p2`
的 bootstrap 骨架声明检查比 DEBT0017 描述的场景更容易因假阴性/假阳性判定错误产生真实阻断误判。

**判定**：**本次不处理**——P0-brief scope 明确锁定「新增文件核对表」一处。因风险高于本体，已在
BDD-14 中与 DEBT0016 同类项一并登记为新 DEBT 候选，并在正文加粗提示，避免被误认为"已随 DEBT0017
一并修复"。

### 5. `agate_common` import 降级 stub 消费方（DEBT0018）

```
grep -n "count_p7_markers(\|count_p6_pass_fail(\|count_code_map_lines(\|read_rules_yaml(" agate/scripts/check-gate.py
```
逐一读取上下文确认 4 处消费点（`gate_p1` L687 / `gate_p6` L1084 / `gate_p7` L1144 /
`gate_p7` CODE-MAP 转抄核对 L1238）：均为"降级 stub 返回 `0`/`None`/空 → 消费分支的判定逻辑是
`count > 0` 才 `return 1`"结构——即降级值必然落在"判定为通过"一侧，无一处存在"降级值恰好等于
某个合法业务场景下的真实计数"的情况（因为真实计数 0 的合法场景已由 frontmatter 优先路径覆盖，
仅 `agate_common` 整体不可导入的安装破损态才会落入这些 stub）。

**判定**：4 处消费点均可安全 fail-closed 改造，无遗漏、无合法场景依赖降级静默。`except ImportError`
兜底块中其余 stub（`count_design_gap`/`parse_fail_list_block`/`count_kf_entries`/
`extract_embedded_yaml_blocks`/`parse_ui_design_section`/`candidate_count_value`/
`design_trivial_declared`/`has_keyword`/`extract_bdd_titles`/`has_marker`/`extract_marker_desc`/
`reconcile_*`）不在 DEBT0018 evidence 明确点名的 4 个"关键读取器"范围内（DEBT0018 原文
recommendation 逐字列出 `read_rules_yaml`/`count_p7_markers`/`count_p6_pass_fail`/
`count_code_map_lines`），`reconcile_*` 系列更有显式设计意图声明"对账是叠加层，降级为关闭不影响
原判定语义"（L79 注释），fail-open 是有意为之而非缺陷。**本次不处理**其余 stub——不在 P0-brief
锁定范围，且 `reconcile_*` 一族的 fail-open 是既定设计，扩大改造属于越界重新设计降级策略。

### 6. `_staged_source_count` 真实暂存区依赖（DEBT0007）

已在「P0-brief 时效性质疑」节详述：核心缺陷已被 TAG0024 修复，全仓仅此一处实现
（`check-pruning.py:84-100`），无第二份重复逻辑。**判定**：本次处理范围收窄为验证 + 登记闭合
（见 BDD-6/7），不涉及新增同类实例。

### 7. 离线 manifest 信任边界文档（DEBT0003）

```
grep -n "checksum\|信任边界\|minisign\|GPG" agate/UPGRADING.md agate/scripts/README.md
```
命中：`agate/scripts/README.md:73-74` 仅描述"sha256 checksum"机制本身，未见"信任边界"说明文字；
`agate/UPGRADING.md:516` 同样只描述功能闭环，无信任边界章节。

**判定**：文档缺口确认仍未填补，与 P0-brief 描述一致，无漂移，本次处理（补充信任边界说明段落）。

## BDD 验收条件

### 版本管理域：hash 共享（DEBT0002）

#### BDD-1: compute_sha256 迁移到 agate_common 后两侧结果一致
- Given `agate_common.py` 新增 `compute_sha256(path)`（文件=内容哈希；目录=按相对路径字典序
  排序逐文件 sha256 拼接再整体 sha256，与现状约定逐字节一致）
- When `agate-pack-offline.py` 打包某目录并计算 sha256，`install-offline.py` 对同一目录内容
  重算 sha256 校验
- Then 两侧调用同一个 `agate_common.compute_sha256` 得到相同 hash 值，且全仓 grep
  `def compute_sha256` 只有 1 处定义（`agate-pack-offline.py`/`install-offline.py` 内不再各自
  重复定义）

#### BDD-2: hash 合并后 pack → install → 卸载全流程无行为变化（回归）
- Given 用改造后的 `agate-pack-offline.py` 对本地 worktree（无网络依赖）打包一个 bundle
- When 依次执行 `agate-pack-offline.py` 打包 → `install-offline.py` 安装 → `agate-install.py`
  卸载该版本
- Then 三步均与改造前行为一致：打包产出 `manifest.json`（sha256 字段值不变）、安装 checksum
  校验通过、卸载成功移除版本目录，全程无 checksum 不匹配误报

### 版本管理域：manifest 信任边界（DEBT0003）

#### BDD-3: 离线安装文档明示信任边界
- Given 用户查阅 `agate/UPGRADING.md` 或 `agate/scripts/README.md` 的离线包安装章节
- When 阅读该章节
- Then 文档显式写出"checksum 防损坏、不防整包替换"的信任边界说明（bundle 提供者需可信），
  不给出"checksum 校验通过即完整性/来源均可信"的误导性表述

[SUGGEST: 推荐本次不引入 minisign/GPG 签名实现，仅做文档信任边界说明，理由——P0-brief
out-of-scope 已明确"签名体系完整实现"排除在本任务外，且 P4-review 遗留建议项本身是"评估签名
成本后决定"，评估结论倾向于文档优先（低成本、当前无被利用证据）。若用户认为签名仍需在本任务内
实现，请在 P1 评审前明确指出，否则按此建议推进。]

### 版本管理域：卸载引用保护限流提示（DEBT0004）

#### BDD-4: 限流边界命中时输出 WARNING
- Given `~/.agate` 卸载引用扫描的目标目录树中存在超出扫描边界（深度 > 4，或 `.agate-version`
  文件 mtime 超过 365 天窗口）的项目，该项目的 `.agate-version` 声明了即将卸载的版本
- When 执行 `agate-install.py uninstall <version>`
- Then stderr 输出 WARNING，明确提示"扫描存在深度/时间窗口限流，可能未覆盖全部引用"，卸载判定
  不因此项目被漏扫而误判为"无引用可安全卸载"

#### BDD-5: 未命中限流边界时不产生 WARNING 噪音（边界流，防止过度提示）
- Given `~/.agate` 卸载引用扫描范围内所有 `.agate-version` 文件均在深度 ≤4 且 mtime 365 天窗口内
- When 执行卸载扫描
- Then stderr 不输出限流 WARNING（仅在真实命中限流边界时才提示，避免噪音掩盖真实信号）

### 测试隔离（DEBT0007，范围已按 P0_STALE 收窄）

#### BDD-6: 三个原始用例在暂存区含大量无关文件时稳定 PASS（含既有修复的显式回归覆盖）
- Given 一个真实开发场景：调用进程所在的外层仓库暂存区含 ≥6 个与任务无关的源码文件（模拟
  TAG0015 报告的"协议自身改造任务暂存区体量大"场景，`test_p2_6f_...` 已用 6 个文件复现该模式）
- When 运行 `test_p2_6e_prune_p7_coupling_checklist_exit_0` / `test_p2_52_yaml_list_phases_exit_0`
  / `test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0` / `test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0`
- Then 四个用例在任意 `--basetemp` 位置运行均稳定 PASS（`exit 0`），不受外层仓库暂存区体量影响

#### BDD-7: DEBT0007 debt 登记闭合
- Given `check-pruning.py` 的 `_staged_source_count` 隔离修复（TAG0024 commit `e2357fc`）与
  BDD-6 补充验证均已确认生效
- When 在 `debt/tech-debt.md` 更新 DEBT0007 条目
- Then `status` 改为 `closed`，追加 `closed_at` 与 closure 说明，evidence 追加指向
  `e2357fc`/`test_p2_6f_...` 与本任务 BDD-6 验证记录，登记格式与既有 DEBT0005/DEBT0006 closed
  条目一致（status/closed_at/evidence 补充块）

### check-gate.py 健壮性：CODE-MAP 路径权威解析（DEBT0016）

#### BDD-8: gate_p4 CODE-MAP 路径改用 resolve_workspace（正常流）
- Given `task_dir` 处于标准两级嵌套（`{workspace}/tasks/{task_id}`）
- When `gate_p4` 解析 CODE-MAP.md 路径
- Then 解析结果与 `agate_common.resolve_workspace` 对同一 `project_root` 的解析结果拼接
  `agents/CODE-MAP.md` 后逐字节一致，`gate_p4` 不再本地执行 `dirname(dirname(...))` 路径算术

#### BDD-9: 非标准两级嵌套场景下路径解析仍正确（边界流）
- Given `task_dir` 与 `workspace` 的层级关系非标准两级嵌套（如经由 `.agate.env` 的
  `AGATE_WORKSPACE=` 覆盖工作区位置的场景）
- When `gate_p4` 解析 CODE-MAP.md 路径
- Then 解析结果仍与 `resolve_workspace` 权威函数结果一致，不产出错误/不存在的路径（新增回归
  测试覆盖此场景，满足 DEBT0016 closure_criteria 第 2 条）

### check-gate.py 健壮性：新增文件核对表整行判定（DEBT0017）

#### BDD-10: 自指场景下说明性文字不再被误判为已满足（原假阴性场景，异常流）
- Given `P4-implementation.md` 只包含说明性散文提及"新增了一个标题叫『## 新增文件核对表』的
  小节"（该字符串以叙述文本形式出现，非独立成行的标题）
- When `gate_p4` 判定该文件是否已补充「新增文件核对表」
- Then 判定为**未满足**（触发 WARNING 提示补充「新增文件核对表」），不再被子串 `in` 匹配误判为
  已满足

#### BDD-11: 标题真实存在时判定通过（正常流，防止整行判定引入新假阳性）
- Given `P4-implementation.md` 含独立成行的「## 新增文件核对表」标题（`re.MULTILINE` 行首匹配）
- When `gate_p4` 判定
- Then 判定为已满足，不触发 WARNING

### check-gate.py 健壮性：agate_common 降级 fail-closed（DEBT0018）

#### BDD-12: agate_common 不可导入时相关 gate 分支显式失败（异常流）
- Given 模拟 `agate_common` 整体不可导入（安装破损，如测试中阻断该模块 import）
- When `check-gate.py` 执行 `gate_p1`（judge 强制校验，消费 `read_rules_yaml`）、`gate_p6`
  （PASS/FAIL 计数，消费 `count_p6_pass_fail`）、`gate_p7`（BLOCKER/DEVIATION 计数，消费
  `count_p7_markers`；CODE-MAP 转抄核对，消费 `count_code_map_lines`）
- Then 上述分支输出显式「安装破损：agate_common 不可导入」错误信息并 `return 1`，不再返回
  `0`/`None`/空导致该分支被静默判定为通过

#### BDD-13: agate_common 正常可导入时行为逐字节不变（回归，防止 fail-closed 改造引入新假阳性拒绝）
- Given `agate_common` 正常安装可导入（本任务默认开发环境）
- When 执行上述 `gate_p1`/`gate_p6`/`gate_p7` 分支的全量既有测试
- Then 判定结果与改造前逐字节一致（沿用共享读取器的真实计数结果，全量 pytest 无新增失败）

### 同类扫描回归拦截

#### BDD-14: 同类未处理实例登记为新 DEBT，不遗留空白
- Given 「同类扫描」节确认的 2 类未处理同类实例：① `task_dir` 类（类别 A）本地路径推导，
  非本体的 2 处（`check-retrospective.py:74` / `agate-render-dispatch-prompt.py:191`；类别 B
  的 `__file__`/`script_path` 类 10 处不构成同类，见第 3 小节判定，不登记）；② 标题字符串子串
  判定（`check-gate.py:881` `gate_p2` bootstrap 骨架声明校验，风险高于 DEBT0017 本体）
- When P8 阶段登记 `debt/tech-debt.md`
- Then 新增至少 2 条 open 状态 DEBT 条目（分别对应①②两类），evidence 指向本次 P1 同类扫描
  结论（本文件「同类扫描」节 3/4 小节），避免发现后无跟踪记录

### DEBT 登记闭合（DEBT0002/0003/0004/0016/0017/0018）

#### BDD-15: 六条 DEBT 登记条目闭合，与 BDD-7 共同覆盖任务标题声明的 7 条
- Given DEBT0002（hash 合并，BDD-1/2 验收通过）、DEBT0003（信任边界文档，BDD-3 验收通过）、
  DEBT0004（限流 WARNING，BDD-4/5 验收通过）、DEBT0016（CODE-MAP 路径权威解析，BDD-8/9 验收
  通过）、DEBT0017（新增文件核对表整行判定，BDD-10/11 验收通过）、DEBT0018（agate_common 降级
  fail-closed，BDD-12/13 验收通过）六条 DEBT 对应的代码/文档修复与各自 BDD 均已验证生效
- When 在 `debt/tech-debt.md` 逐条更新这六个条目
- Then 六条条目的 `status` 均由 `open` 改为 `closed`，各自追加 `closed_at` 与 closure 说明，
  `evidence` 追加指向本任务对应 BDD 编号（BDD-1/2、BDD-3、BDD-4/5、BDD-8/9、BDD-10/11、
  BDD-12/13）与实现 commit 的验证记录，登记格式与既有 DEBT0005/DEBT0006 closed 条目一致
  （status/closed_at/evidence 追加块，格式已由 BDD-7 核对一致，直接复用判定）；与 BDD-7
  （DEBT0007 单独登记闭合）共同构成任务标题"批量关闭 7 条历史遗留 open 技术债"的完整验收覆盖
  （7/7 条均有登记闭合验收，不再只有 DEBT0007 一条）

## 待确认清单

`[NO_NEED_CONFIRM]`

DEBT0003 的签名 vs 文档信任边界取舍已用 `[SUGGEST]` 标记（见 BDD-3 后），有明确倾向且不涉及
破坏性变更/业务方向判断，不阻塞推进。除此之外无其他方向性待确认项——7 条 DEBT 的处理方式均有
明确技术方案（P0-brief scope + closure_criteria 已给出），同类扫描的"不处理"项均给出了理由与
回归拦截手段（BDD-14），不构成需要人工拍板的业务判断。

## P2 阶段 [SCOPE+] 回补（主 Agent 亲自写，P1 基线保护规则）

[BASELINE_CHANGE: P2 architect 设计阶段发现 P1 未预见的必须处理项——`compute_sha256` 迁移到
`agate_common.py` 后，`install-offline.py` 的离线 bootstrap 前提被打破（pyyaml 是 manifest 里
唯一"先执行、后校验"的组件，`agate_common.py` 顶部 `import yaml` 失败即 `sys.exit(1)` 硬依赖，
会在真正没装 pyyaml 的机器上导致安装器崩溃）。主 Agent 已核实这一发现的事实基础（`install-offline.py`
L228/L237 执行顺序、`agate_common.py` L30-34 硬依赖、`agate-pack-offline.py` L129 pyyaml 组件的
manifest 结构），确认属实且需要处理。已批准纳入实现范围，不改变 BDD-1/2 描述的外部可观察行为
（本质是 BDD-2「pack→install→卸载全流程无行为变化」验收范围内的机制细化，不新增独立 BDD 编号）。]

[SCOPE_RESOLVED: P2-design.md §1.3 R1「缓解设计」已给出闭环方案——`install-offline.py` 新增
`_ensure_agate_common(bundle_dir, manifest)` 引导函数，在 `pip install` 之前先用内联
`hashlib.sha256` 单独校验 pyyaml wheel 的 manifest checksum，不匹配则报错且不执行 `pip install`；
校验通过后才安装 + `import agate_common`。pyyaml 组件与其余组件同样遵循"先校验、后使用"顺序，
BDD-26 字面不变量对其同样成立。方案已经 plan-eng-review 第 2 轮 approved（复核确认顺序缺口已消除
+ 回归覆盖已补齐 checksum 不匹配场景用例）。]

## 范围声明

`packages: [agate-scripts, agate-tests, agate-docs]`、`domains: [backend]` 已写入文件头
frontmatter。`agate-docs` 对应 DEBT0003 涉及的 `agate/UPGRADING.md`/`agate/scripts/README.md`
文档补充，其余为脚本与测试。不涉及 frontend/mcp/security 域。

## 能力需求声明

```yaml
capability_requirements:
  - need: script-toolchain-dev
    why: 修改 agate/scripts/*.py（compute_sha256 合并/check-gate.py 判定逻辑/降级 stub 改造）
      并跑全量 pytest + consistency + shellcheck 需要标准开发环境
    available:
      - "worktree 环境已确认（系统 python3.12.3 + pytest 9.0.3，HANDOFF-TAG0031.md §9 已验证
        consistency 0 ERROR）"
    status: available

  - need: offline-bundle-regression
    why: DEBT0002/3/4 涉及 pack → install → 卸载全流程回归（BDD-2），需要本地构造一个离线
      bundle 样例并在无网络依赖前提下跑通闭环
    available:
      - "agate-pack-offline.py 支持 --repo 指向本地 worktree 自身（非默认 ~/.agate/repo），
        可离线构造 bundle 样例，不依赖外网 git remote"
      - "agate/tests/unit/test_agate_pack_offline.py 与 test_install_offline.py 已有既存单测
        覆盖二者的函数级行为，作为回归的基础设施补充"
    status: available
```

`verification_env` 声明（DEBT0002/3/4 离线包全流程回归，按判断树属"运行环境准备"而非
"agent 能力"，不误标 supplementable）：

```yaml
verification_env: "本地无网络离线 pack→install→卸载全流程：worktree 内构造临时 AGATE_HOME
  目录（非 ~/.agate，避免污染稳定版）+ agate-pack-offline.py --repo <worktree> 本地打包 +
  install-offline.py --dest-root <临时目录> 安装 + agate-install.py uninstall 卸载闭环"
verification_env_budget: "止损轮次 2（独立计数，不占 retries[P5]）；轮次追踪由主 Agent 在
  P5/P6 dispatch-context 中接续记录"
```

## 裁剪说明

`phases: [P1, P2, P3, P4, P5, P6, P7, P8]`（全阶段保留，无裁剪）：

- **P3 不可裁**：`risk_level: medium`（非 low），按规则仅 low 可裁 P3。
- **P7 不可裁**：裁剪跳阶前置条件要求源文件数 ≤5 + 有 `coupling_checklist`（≥2 已检查耦合点）。
  本任务受影响生产脚本已至少 5 个（`agate_common.py` / `agate-pack-offline.py` /
  `install-offline.py` / `agate-install.py` / `check-gate.py`，`check-pruning.py`/
  `tech-debt.md` 视 BDD-6/7 落地方式可能追加），逼近或超过阈值，且 `check-gate.py` 是核心 gate
  消费方（P0-brief known_risks 已强调），不满足裁剪的低风险前提，保留 P7 一致性检查。
- risk_level 定为 **medium**（不采纳 low）：理由——① DEBT0018 fail-closed 是行为变更（消费方
  从"安装破损时静默 false-PASS"变为"报错 return 1"，属于可观察的错误路径新增）；② DEBT0016/17
  改动的是 `check-gate.py`（核心 gate 消费方）的判定逻辑本体，改动面覆盖 `gate_p1`/`gate_p2`
  （间接，见同类扫描第 4 项标注）/`gate_p4`/`gate_p6`/`gate_p7` 多个分支；③ DEBT0002 hash 合并
  影响离线安装完整性校验链路，误改会导致内网批量误装/误拒。均非纯新增/纯只读，故不采用 low。
- 未声明 `ceremony`（缺省 standard，fail-closed）——本任务无 UI、无新机制设计，但同样无法一次性
  凑满 thin 的四要素（尤其"跳过风险评估"与本任务实际需要的多分支验证不符），不强行薄化。

## judge 声明提醒

本文件 `created: 2026-09-04` 晚于 `judge_required_since`（`agate/rules/dispatch.yaml`
"2026-08-22"），按 RM-AG0039 要求，主 Agent 须在 `.state.yaml` 写入 `judge.enabled: true`
（check-gate P1 机械校验，缺失/未启用 → exit 1）。本节仅作提醒，不在本文件内修改 `.state.yaml`。
