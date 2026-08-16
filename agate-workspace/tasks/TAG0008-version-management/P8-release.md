---
phase: P8
task_id: TAG0008
type: release
parent: P7-consistency.md
trace_id: TAG0008-P8-20260816
status: draft
created: 2026-08-16
agent: implementer
---

# P8 — 发布准备：agate 版本管理机制（v1）

> trace：TAG0008-P8-20260816（implementer P8 模式，releaser）。上游：P7-consistency.md（approved，
> BLOCKER=0，8/8 DESIGN_GAP 配对）+ P2-design.md（packages: [agate] 单包，gate_commands 固化）+ P1-requirements.md
> （影响面表 2.2 文档层 13 项联动）。本文件只做发布准备（改文件），**未执行 git commit/tag**——由主 Agent
> 在 gate 验证后统一执行 `[PROD_NOT_TOUCHED]`。

---

## 1. bump_type

- **bump_type: minor**（v0.49.0 → v0.50.0）
- **判定理由**（dispatch-context 约束 1）：P2 packages=[agate] 单包；本次为**加功能**（版本管理 6 组件 +
  离线部署包），**向后兼容**（`~/.agate` 软链保留 + 回退 current + legacy 兜底 BDD-30），**不改既有 gate 判定 API**
  （BDD-31：check-gate.py 等 5 个判定脚本零改动）。按语义化版本：加功能向后兼容 = minor。
- 版本号来源：README badge v0.49.0 = 最新 git tag v0.49.0（主 checkout stable，worktree 基于 main 一致）。
  无独立 version 文件（`glob **/version*` 无命中，README badge 即 version 文件——TAG0004/0013 P8 先例）。

## 2. 版本变更确认（version 文件已修改）

| 版本引用位置 | 变更 |
|-------------|------|
| `README.md` L5 version badge | `v0.49.0` → `v0.50.0` |
| `README.zh-CN.md` L5 version badge | `v0.48.0`（历史漂移）→ `v0.50.0`（与 README.md 对齐） |
| `CHANGELOG.md` 顶部 | 新增 `## [0.50.0] - 2026-08-16` 章节（TAG0008 版本管理机制 6 组件 + 离线包 + 文档联动 + 破坏性变更声明） |
| `agate/UPGRADING.md` | 新增 `### v0.50.0` 章节（~/.agate 目录化 / .agate-version 语法 / hook 解析入口迁移 / agate-install 新工具 / BDD-30 存量兼容红线 / 迁移动作小结） |
| 文档中写死版本号处 | 已核对无其他"当前版本"写死（SETUP/scripts README/orchestrator-template 等只写命令不写死版本；agate-summary.py 输出示例为运行时解析非写死） |

- [x] README badge v0.50.0 落盘
- [x] CHANGELOG [0.50.0] 章节落盘
- [x] UPGRADING v0.50.0 章节落盘
- ⚠️ **CHECK 7 瞬态**：badge 已 bump 到 v0.50.0，但最新 git tag 仍是 v0.49.0 → consistency CHECK 7 报 1 ERROR
  （预期，非缺陷）。主 Agent 在 gate 验证后执行 `git tag v0.50.0 && git push origin v0.50.0` → CHECK 7 自愈。

## 3. CHANGELOG 更新确认

- [x] `CHANGELOG.md` 顶部新增 `## [0.50.0] - 2026-08-16` 章节。
- [x] 无 [Unreleased] 需迁移（P8 前 CHANGELOG 顶部即 `[0.49.0]`，无待迁移条目——check-changelog 语义）。
- [x] 本任务变更条目已完整纳入：[0.50.0] 章节含「新增」6 组件（agate-install / agate-resolve / resolve-entry /
  agate-pack-offline / install-offline / summary 语义迁移 + 3 内联脚本归口 + agate_common 集成）、「变更」文档层联动、
  「测试」6 新测试文件 31 BDD 全 PASS、破坏性变更声明（指向 UPGRADING v0.50.0）。
- [x] 与 P7 §3.1 BDD 数一致：P1 31 BDD = P6 pass 31 = P8 CHANGELOG 声明的 31 BDD 全 PASS。

## 4. debt_check

- **debt_check: reviewed**
- 读 `{AGATE_WORKSPACE}/debt/tech-debt.md`（存在，含 DEBT0001 closed）。
- 本任务 P4-review 遗留建议项已登记为新 DEBT 条目（**check-debt.py exit 0 校验通过**）：
  - **DEBT0002**：离线包 compute_sha256 双实现漂移（P4-review-eng INFORMATIONAL 8 / P7 DESIGN_GAP 1.3）→
    建议 agate_common.py 补 hash 工具共享。
  - **DEBT0003**：离线 manifest 未签名（P4-review-cso MEDIUM-2）→ 建议文档明示信任边界（checksum 防损坏
    不防整包替换）+ 可选签名。
  - **DEBT0004**：卸载引用保护扫描限流漏扫无提示（P4-review-cso MEDIUM-3）→ 建议限流边界命中时 stderr WARNING。
- 以上 3 条均为 open / priority medium，不阻断发布（P8 gate：debt_check 字段存在即放行，内容不达标不阻断）。
- DEBT0001（closed，TAG0013 关闭）本任务 CHECK 10 白名单扩展无复发风险（新增脚本名均入白名单）。

## 5. 文档层联动落地（P1 影响面表 2.2 + P7 承接项）

| 文件 | 改动 |
|------|------|
| `README.md` | 快速上手第 1 步新增"版本管理"接入方式（agate-install 流程：latest/指定版本/--check） |
| `README.zh-CN.md` | 同上（中文镜像同步） |
| `agate/SETUP.md` | 新增「环境准备（agent 执行）」节（探测命令 exit code 可判 → 分平台修复 → 验证闭环）+ 前置叙述随版本目录调整 |
| `agate/UPGRADING.md` | 新增 v0.50.0 章节（破坏性变更逐条列） |
| `agate/platform-notes.md` | 新增「latest/current 指针在无符号链接权限时的形态」（文本指针文件 + `.agate-root` 恢复）+ 表格行更新 |
| `agate/AGENTS.md` | 升级/卸载叙述适配版本目录（header + 升级 + 卸载） |
| `agate/WORKFLOW.md` | 安装位置叙述（目录 + 解析） |
| `agate/orchestrator-template.md` | `{agate_root}` 语义：env 最高 → `agate-resolve.py` 解析 → 默认 `~/.agate` |
| `agate/adr.md` | ADR-008 论据复核（gate 脚本"自动跟随升级"改由 resolve-entry 承担）+ 新增 **ADR-009**（~/.agate 版本管理根目录 + resolve-entry） |
| `agate/assets/templates/project.md` | 默认安装位置语义（版本管理根目录 + AGATE_ROOT env 显式覆盖说明） |
| `agate/assets/templates/handoff-template.md` | `~/.agate` 行补版本目录说明（复核，稳定版叙述保留） |
| `agate/scripts/README.md` | 顶部版本管理说明 + 3 hook 薄壳 exec resolve-entry + 安装节 + 新增「版本管理」节（5 脚本）+ summary 描述语义更新 |
| `agate/scripts/check-protocol-consistency.py` | **CHECK 10 SCRIPT_REF_RE 白名单补 `install-offline` / `resolve-entry`**（P7 承接项 2，命名联动，判定逻辑未改） |
| `install.sh` | 兼容保留注释（单软链 + 版本管理替代入口说明） |

- [x] P7 §3.5 三项承接全部落地：① scripts/README 新增 4 脚本 + resolve-entry 说明 ✅ ② SCRIPT_REF_RE 白名单
  补 install-offline/resolve-entry ✅ ③ P1 §2.2 文档层 13 项 ✅
- 复核未改（语义已覆盖）：`agate/assets/execution-roles/verifier.md`、`agate/phase-cards/P6-acceptance.md`
  （均用 `$AGATE_ROOT`/`{agate_root}`，解析语义兼容）；`docs/guides/worktree-dogfooding-guide.md`（稳定版概念保留）。

## 6. consistency 验证

- **命令**：`python3 agate/scripts/check-protocol-consistency.py --strict`（worktree 自己的脚本）
- **结果**：**0 ERROR**（除 CHECK 7 瞬态——badge v0.50.0 领先于 git tag v0.49.0，主 Agent tag 后自愈）；
  **279 WARNING 与 P5 基线一致，未新增**。
- CHECK 10：文档新增脚本名引用（agate-install / agate-resolve / agate-pack-offline / install-offline /
  resolve-entry）均真实存在于 `agate/scripts/` → 无漂移 ERROR；白名单扩展后 install-offline/resolve-entry
  引用可被 CHECK 10 正常校验。
- CHECK 1（YAML 可解析）PASS——UPGRADING/SETUP 新增 YAML 块语法正确。

## 7. 临时资源清单（releaser → 主 Agent 交接）

本任务（TAG0008）执行期间产生的临时服务/进程/数据/开发安装，主 Agent 在 READY 收尾检查时按此清理：

| 类型 | 资源 | 状态 | 清理动作 |
|------|------|------|---------|
| 临时脚本 | `/tmp/opencode/tag0008-mv.sh`（P2 minimal_validation 最小验证脚本，P4 阶段运行） | 已存在，非本 P8 创建 | 可删除（`rm /tmp/opencode/tag0008-mv.sh`） |
| 临时测试数据 | P3/P4/P5/P6 阶段 pytest `tmp_path` 假 HOME 目录、fake ~/.agate、假 repo 等 | pytest tmp_path 自动清理 | 无残留（pytest fixture 自动回收） |
| 临时验证产物 | P6-evidence/ 证据文件（bdd-*.log / manifest-real.txt 等） | 已 commit 为任务产出 | 保留（P6 验收证据） |
| 一致性日志 | `/tmp/opencode/tag0008-consistency-after.log` / `-full.log`（本 P8 临时输出） | 临时 | 可删除（非必须） |
| 开发安装 | 无（本任务未做 editable install / 全局包安装；gate 脚本全部在 worktree `agate/scripts/` 内） | — | 无 |
| 端口/服务 | 无（本任务无 debug server / daemon / 端口占用） | — | 无 |
| 生产环境 | 未触发 `[PROD_NOT_TOUCHED]`——未读改主 checkout / `~/.agate` / 生产数据 | — | 无 |

## 8. Lessons Learned（P8 沉淀）

1. **类别：流程**——版本 bump 使 consistency CHECK 7 进入"badge 领先 tag"瞬态是**预期状态**，不是回归：
   releaser 只能改文件不能 tag，CHECK 7 的红灯要留给主 Agent tag 后自愈。P8-release.md 显式标注该瞬态，
   避免主 Agent 误判为任务失败（对照：TAG0014 P7 DESIGN_GAP 2 的教训）。
2. **类别：文档联动**——README.zh-CN.md 的 badge 长期漂移（v0.48.0 vs README.md v0.49.0）此前无 gate 捕获
   （CHECK 7 只查 README.md）。本次 bump 顺手对齐。教训：中文镜像 badge 需与英文同步维护，或考虑把
   README.zh-CN.md 纳入 CHECK 7 扫描（可选改进）。
3. **类别：安全/债登记**——P4-review 的 INFORMATIONAL/MEDIUM 建议项（sha256 双实现、manifest 签名、扫描限流）
   在 P8 集中登记为 DEBT 条目，避免"评审过了但建议项流失"。教训：P8 debt_check 是评审遗留建议项的正式收口点，
   评审角色应在 P4-review.md 就列出建议项清单（本任务已如此，P4-review.md 遗留建议项 5 组直接可登记）。

## 9. 主 Agent 待执行（releaser 不执行）

1. **gate 验证**：`check-gate.py P8 $TASK_DIR`（bump_type / debt_check / 暂存区 version+CHANGELOG 变更）
2. **重跑 P5 gate**：`python3 -m pytest -q --tb=no`（确认 bump 后测试仍全绿）+ `bash agate/tests/scripts/count-tests.sh`
3. **`git log v0.49.0..HEAD --oneline`** 对照 CHANGELOG 无遗漏
4. **bump-version + commit + tag**：`git tag v0.50.0 && git push origin v0.50.0`（同一 commit 含
   badge+CHANGELOG+UPGRADING+文档联动）
5. **READMEY 收尾**：按 §7 临时资源清单清理；在干净 checkout 跑 consistency 确认 0 ERROR（CI 兜底）
6. **release PR 普通 merge（`--no-ff`）禁止 squash**（tag 需为 HEAD 祖先，AGENTS.md 版本发布流程）

## 10. 门槛对照

- [x] P8-release.md 存在且含 bump_type / debt_check / 版本变更确认 / CHANGELOG 确认 / 临时资源清单
- [x] README badge + CHANGELOG + UPGRADING 章节已更新（版本号变更落地 v0.50.0）
- [x] 文档层联动（SETUP 环境准备节 / scripts README 新脚本清单 / platform-notes 指针说明等）已落地
- [x] check-protocol-consistency.py --strict 0 ERROR（除 CHECK 7 tag 瞬态，279 WARNING 基线未增）
- [x] 未执行任何 git commit/tag
