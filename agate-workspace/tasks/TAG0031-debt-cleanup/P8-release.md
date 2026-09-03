---
phase: P8
task_id: TAG0031
parent: P7-consistency.md
trace_id: TAG0031-P8-20260904
created: '2026-09-04'
bump_type: patch
agent: implementer
debt_check: reviewed
---

# P8-release.md — TAG0031-debt-cleanup 发布准备声明

> releaser subagent 产出本文件第 1-5、7-8 节时，"延后至三路合并后统一处理"是当时已知信息下的
> 合理判断。主 Agent 随后发现 TAG0029 已实际独立完成标准 P8 发布（v0.67.1，PR #271 已合并入
> origin/main），与用户确认后改为**跟进走标准流程**——见第 6 节「主 Agent 更正」。bump_type/
> debt_check/CHANGELOG 草稿等实质内容不受此影响，直接作为正式发布的依据。

## 1. 前置条件核对（P7-consistency.md）

- P7-consistency.md（TAG0031-P7-20260904）结论：`blocker_count: 0` / `deviation_count: 0` /
  `deviation_critical_count: 0` / `design_gap_count: 1` / `design_gap_reviewed_count: 1`
  （DESIGN_GAP 已完整配对转抄 + REVIEWED 判定，接受）。
- 第 3 节四项跨文件一致性核查（P2 packages↔实际改动 / P1 BDD↔P6 PASS 语义抽查 / P4 实现路径↔
  P2 设计 / debt 登记↔BDD-7/14/15）均引用具体文件/行号锚点，未发现偏离设计意图的实质性问题。
- 第 2 节 SCOPE+ 闭环（R1 pyyaml 引导方案）四环完整（发现→回补→解决→测试覆盖），`[SCOPE_RESOLVED]`
  有效。
- 第 4 节未决项清零：P1 无残留 `[NEED_CONFIRM]`，P6 无 `[BLOCKER]`/`[DEVIATION-CRITICAL]`。
- 结论：具备进入 P8 发布阶段的一致性前提，**前置条件已满足**。

## 2. P2-design.md packages 声明核对

`packages: [agate-scripts, agate-tests, agate-docs]`（P2-design.md:11，与 P1-requirements.md:13
一致）。P7-consistency.md §3.1 已核对三域均有实际改动落地，git 实际提交（P3 `233a4f3` / P4
`9faf19a`）与声明一致，无遗漏域、无越界域：

| package | 改动文件 | 备注 |
|---|---|---|
| agate-scripts | `agate/scripts/agate_common.py`、`agate-install.py`、`agate-pack-offline.py`、`check-gate.py`、`install-offline.py` | 均为 `M`（修改），无新增文件 |
| agate-tests | `agate/tests/unit/test_agate_common.py`、`test_agate_install_uninstall.py`、`test_agate_pack_offline.py`、`test_check_gate.py`、`test_debt_registry_closure.py`、`test_install_offline.py`、`agate/tests/regression/test_offline_bundle_roundtrip.py` | 新增/扩充测试 |
| agate-docs | `agate/UPGRADING.md`、`agate/scripts/README.md` | DEBT0003 信任边界说明段落 |

三个 package 均单一版本管理体系下的同仓库脚本/测试/文档域，本次不涉及独立可发布制品（无
package.json/pyproject 各自版本号），版本 bump 按仓库级 CHANGELOG 版本号统一处理（延后，见 §5）。

## 3. bump_type 判断依据

**bump_type: patch**

依据：
1. 本次改动是 7 条低风险脚本健壮性修复（DEBT0002/0003/0004/0007/0016/0017/0018），均为工具链
   内部实现细节调整（hash 工具去重共享、WARNING 提示补充、文档信任边界说明、gate 脚本判定健壮化、
   测试隔离修复），无新机制/新功能引入。
2. 无破坏性变更：无 API/CLI 参数变化（`compute_sha256` 签名不变，仅迁移位置）；无协议文档面改动
   （P0-brief 已限定"无新机制设计、无协议文档面改动"）；SELF-GATE protocol-alignment-review 已
   确认 A1-A7 全 ALIGNED。
3. 对齐既往同类"工具链批"任务模式（如 TAG0024）——批量修复历史遗留 DEBT、无对外行为契约变更的
   任务归类为 patch 级别。
4. 具体版本号数字不在本次判断范围内（三路并行合并后由主 Agent 统一决定，见 §5）。

## 4. debt_check

**debt_check: reviewed**

已读取 `agate-workspace/debt/tech-debt.md`，逐条核对 status/closure evidence，9 条 DEBT id 清单：

**closed（7 条，本次任务关闭）：**

| DEBT id | 标题（摘） | closed_at | closure 依据 |
|---|---|---|---|
| DEBT0002 | 离线包 compute_sha256 双实现漂移 | 2026-09-04 | `agate_common.py` 新增 `compute_sha256`，pack/install 两侧改 import 共享，全仓仅 1 处定义 |
| DEBT0003 | 离线 manifest 未签名（信任边界未文档化） | 2026-09-04 | UPGRADING.md/scripts/README.md 补"checksum 防损坏不防整包替换"信任边界说明 |
| DEBT0004 | 卸载引用保护扫描限流漏扫且无提示 | 2026-09-04 | `_find_references` 改二元组返回，限流命中时 stderr WARNING |
| DEBT0007 | test_check_pruning.py 依赖真实 git 暂存区 | 2026-09-04 | `_staged_source_count` 隔离修复（TAG0024 `e2357fc` 已落地），本次 4 用例复跑确认全绿 |
| DEBT0016 | gate_p4 CODE-MAP 路径本地推导未调 resolve_workspace | 2026-09-04 | 改调用 `agate_common.resolve_workspace`，BDD-8/9 覆盖标准流+非标准嵌套 |
| DEBT0017 | 「新增文件核对表」子串判定自指假阴性 | 2026-09-04 | 改整行/标题级正则 `re.search(r"^##\s+新增文件核对表", ...)`，BDD-10/11 覆盖 |
| DEBT0018 | agate_common import 降级 stub 返回 0/空致 false-PASS | 2026-09-04 | 4 个消费点改 fail-closed（哨兵值检测→报错+return 1），BDD-12/13 覆盖 |

**open（2 条，本次任务同类扫描新登记）：**

| DEBT id | 标题（摘） | priority | 登记依据 |
|---|---|---|---|
| DEBT0028 | `dirname(dirname(...))` 同款模式另 2 处非本体实例（`check-retrospective.py:74` / `agate-render-dispatch-prompt.py:191`） | low | P1「同类扫描」节第 3 小节，DEBT0016 同类风险，本次范围锁定 check-gate.py 一处 |
| DEBT0029 | `check-gate.py:881` gate_p2 骨架声明标题子串判定（同 DEBT0017 模式，此处触发阻断性 return 1，风险更高） | medium | P1「同类扫描」节第 4 小节，本次范围锁定「新增文件核对表」一处 |

## 5. CHANGELOG 草稿条目（正文文本，不写入 CHANGELOG.md 本体）

> 以下为供主 Agent 在三路合并后采纳/合并的草稿文本，仿照 CHANGELOG.md 现有格式
> （`## [x.y.z] - 日期` + `### 新增/变更/修复`）。**本 P8 未修改 CHANGELOG.md 本体。**

```markdown
## [Unreleased] - TAG0031 草稿（版本号待三路合并后统一确定）

### 修复（TAG0031：历史遗留 DEBT 存量批修复）

- **版本管理域（DEBT0002/0003/0004）**：
  - `compute_sha256` 目录/文件哈希工具收敛到 `agate_common.py` 单点定义，
    `agate-pack-offline.py`/`install-offline.py` 改为共享 import，消除双实现漂移风险；
    `install-offline.py` 新增 `_ensure_agate_common` 引导函数解决 pyyaml 组件"先安装后校验"的
    离线 bootstrap 时序缺口（先内联 checksum 校验通过才 pip install，保持"先校验后使用"顺序）。
  - `UPGRADING.md`/`scripts/README.md` 离线包章节补充信任边界说明："checksum 防损坏、不防整包
    替换，bundle 提供者需可信"。
  - `agate-install.py` 的 `_find_references` 改为返回 `(refs, hit_limit)` 二元组，卸载时若命中
    限流边界（深度>4 / mtime 超窗 / 跳过目录含 .agate-version）向 stderr 输出 WARNING 提示可能
    漏扫旧引用。
- **测试隔离验证（DEBT0007）**：确认 `test_check_pruning.py` 的 `_staged_source_count` 隔离
  修复（TAG0024 已落地）在暂存区含 6+ 无关文件场景下 4 个既有回归用例稳定 exit 0。
- **check-gate.py 健壮性（DEBT0016/0017/0018）**：
  - gate_p4 的 CODE-MAP.md 路径推导改为调用 `agate_common.resolve_workspace` 权威函数，替代
    本地 `dirname(dirname(...))` 算术，覆盖非标准两级嵌套场景。
  - 「## 新增文件核对表」存在性判定由子串包含改为整行/标题级正则，消除自指/dogfooding 场景下
    说明性文字被误判为"已满足"的假阴性。
  - `agate_common` import 降级 stub（4 个关键读取器）改为 fail-closed：安装破损（agate_common
    不可导入）时显式报错并 `return 1`，替代原静默 0/空 false-PASS 降级。
- 新增登记 2 条同类扫描发现的 open DEBT（DEBT0028/DEBT0029，见本文件 §4），不在本次处理范围。
```

## 6. 版本号处理（主 Agent 更正，2026-09-04）

上文声明的"延后至三路合并后统一处理"在 releaser 产出时点尚未发现 TAG0029 已实际独立完成标准
P8 流程（bump 到 v0.67.1 并建 tag、已合并入 origin/main，PR #271）。主 Agent 发现此情况后向
用户确认，用户决定：**TAG0031 改为跟进，同样正常走标准 P8 流程**，不再延后。

处理步骤（主 Agent 亲自执行）：
1. `git merge origin/main` 同步 TAG0029 的 v0.67.1 基线（1 处 P0-brief.md 文本重复冲突已解决，
   tech-debt.md/UPGRADING.md/active-tasks.md 自动合并无冲突）——merge commit `1902abb`
2. 合并后全量 pytest 复核：1445 passed, 2 skipped, 0 failed（较合并前 1435 新增 10 项为 TAG0029
   带入）；consistency 0 ERROR
3. 版本号 bump 到 **v0.67.2**（patch，紧接 v0.67.1），更新 README.md / README.zh-CN.md 徽章 +
   CHANGELOG.md（`[Unreleased]` 或新增段 → `[0.67.2] - 2026-09-04`）+ UPGRADING.md 新增
   `### v0.67.2` 小节，格式对齐 TAG0029/TAG0028 先例
4. commit + `git tag v0.67.2`

§5 的 CHANGELOG 草稿内容作为本次正式 CHANGELOG 条目的基础文本，主 Agent 采纳时按当前 CHANGELOG
既有格式（版本号标题 + 分类小节）转正，不再是"草稿待定"状态。

## 7. 临时资源清单

核对本任务 P1-P8 全程：本任务是纯脚本 + 测试改动，未启动任何调试服务/进程，未创建临时数据库，
未做任何开发环境安装（无 editable install、无全局包安装）。测试执行全程使用 pytest 内建
`tmp_path`/`monkeypatch` fixture 隔离（离线包回归测试用临时 `AGATE_HOME` 目录、mock
`subprocess.run`，不联网、不落地真实文件系统外部状态）。`git status --short` 核对确认本次
P8 唯一新增文件为本文件自身（`P8-release.md`，及派发指引 `P8-dispatch-context-implementer.md`
由主 Agent 写入）。

**清单：空**（无待清理的临时服务/进程/数据/开发安装）。

## 8. 自检

- 产出文件存在且非空：是。
- 未修改 `CHANGELOG.md`/`README.md`（未用 Edit 工具改动，未执行相关写入命令）：确认。
- 未创建 git tag（未执行 `git tag` 命令）：确认。
- `git status --short` 核对：仅新增本文件（`P8-release.md`）及主 Agent 已写入的
  `P8-dispatch-context-implementer.md`，无其他改动。
