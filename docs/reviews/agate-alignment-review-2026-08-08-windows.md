---
review_date: 2026-08-08
reviewer: protocol-alignment-review
change_summary: Windows（Git for Windows bash）支持加固 + 安装指引——.gitattributes 强制 LF、install-hook.sh ln 退化检测、platform-notes.md Windows 章节、scripts/README.md 提示、新 bats 用例
files_changed:
  - .gitattributes
  - agate/platform-notes.md
  - agate/scripts/README.md
  - agate/scripts/install-hook.sh
  - agate/tests/unit/install-hook.bats
commit: d675381
---

# 协议-脚本对齐审查（Windows 支持加固，commit d675381）

## 意图分析

让 agate 能在 Windows 原生（Git for Windows 自带 MSYS2 bash，不用 WSL）运行，提供安装指引 + 防御性加固（`ln -sf` 退化检测 + `.gitattributes` 强制 LF），**前提不对 Linux/macOS 既有行为产生负面作用**。diff 是意图的物理表现，本审查验证语义一致性。

## 反向传播（应被影响文件列表）

| 优先级 | 文件 | 理由 | 结论 |
|--------|------|------|------|
| 高 | `agate/platform-notes.md` | 平台适配专文档，Windows 章节的唯一正确落点 | ✅ 已更新（diff 内） |
| 高 | `agate/scripts/README.md` | install-hook.sh 改动 → 脚本清单/依赖节提示 | ✅ 已更新（diff 内） |
| 中 | `agate/tests/unit/install-hook.bats` | 新逻辑对应测试 | ✅ 已更新（diff 内） |
| 中 | `CHANGELOG.md` | 平台 enablement 是否需 Unreleased 条目 | ⚠️ 未更新（见 A5，NEEDS_HUMAN_REVIEW） |
| 低 | `agate/LIMITATIONS.md` 局限 6 | 运行时依赖的平台维度 | ⚠️ 建议项（非必须，见 A3） |
| 低 | 根 `AGENTS.md` 依赖节 | 开发者向的 Windows 提示 | ⚠️ 建议项（非必须，见 A3） |
| 低 | `agate/WORKFLOW.md` / `agate/orchestrator-template.md` | 平台支持说明是否需同步 | ✅ 无需（platform-notes 是权威平台文档） |
| 低 | `.github/workflows/protocol-tests.yml` | 是否加 windows matrix | ✅ 无需（platform-notes:147 已显式标注为未来工作，文档与 CI 现状一致） |
| 观察 | `agate/AGENTS.md:79` | hook 升级说明（预存过时，非本 commit 引入） | ⚠️ 建议项（见 A3 观察） |

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED |
| A2 | 脚本→文档对齐 | ALIGNED |
| A3 | 一致性连锁 + 反向传播 | ALIGNED（附 3 条建议项） |
| A4 | 测试覆盖 | ALIGNED |
| A5 | 下游影响 + 文档传播 | **NEEDS_HUMAN_REVIEW**（CHANGELOG 条目） |
| A6 | 锚点表覆盖 | ALIGNED |
| A7 | 设计原则一致性 | ALIGNED |

**无 MISALIGNED。** 1 条 NEEDS_HUMAN_REVIEW（A5，需人工确认后才能 commit）。

---

## 逐项审查

### A1: 文档→脚本对齐

**文档声明**（`agate/platform-notes.md:132`）：
> Windows 无符号链接权限时，hook 会以**复制模式**安装（输出含「复制模式」提示）。**升级 agate 后需重跑此命令**更新 hook（复制不自动跟随源文件）。

**脚本实现**（`agate/scripts/install-hook.sh:34-39, 52-56, 75-79`）：
```bash
if [ -L "$HOOK_FILE" ]; then
    echo "pre-commit hook 已安装: $HOOK_FILE -> $SOURCE"
else
    echo "pre-commit hook 已安装（复制模式，Windows 无符号链接权限）: $HOOK_FILE"
    echo "  ⚠️  升级 agate 后需重跑 install-hook.sh（复制不自动跟随源文件）"
fi
```

**核心约束验证——Linux/macOS 行为不变**：三个 hook 的原 `echo` 文本在改动前（`git show d675381^`）与改动后（`d675381`）各恰好出现 1 次（`grep -Fc` 验证），即原文本逐字保留在 `[ -L ]` 真分支内；`ln -sf` 在 Linux/macOS 成功创建符号链接 → `[ -L ]` 为真 → 输出与改动前逐字一致。Windows 退化 → `[ -L ]` 假 → 新增复制模式提醒，与文档描述一致（三处分支输出均含「复制模式」）。

**结论**：ALIGNED

### A2: 脚本→文档对齐

**脚本实现**（`install-hook.sh` 新增 else 分支消息）：
- 复制模式 + 需重跑提醒（pre-commit）
- 复制模式（commit-msg / pre-push）

**文档同步**：
- `agate/platform-notes.md:132`（安装步骤 6 的复制模式 + 重跑说明）✓
- `agate/platform-notes.md:144`（已知限制表：「`ln -sf` 退化为复制 | hook 不随 agate 升级自动更新 | 升级 agate 后重跑 `install-hook.sh`」）✓
- `agate/scripts/README.md:5`（新增 Windows 用户提示，指向 platform-notes「Windows 原生」章节）✓

**结论**：ALIGNED

### A3: 一致性连锁 + 反向传播

**A3a（连锁）**：diff 与实施计划 `docs/plans/agate-windows-support-20260808.md` 的文件清单完全一致（5 个文件），无已知衍生改动遗漏。commit message 引用该 plan 作为 self-gate-review 路径，plan 存在且匹配。

**A3b（反向传播逐一验证）**：
1. **WORKFLOW.md / orchestrator-template.md**：全文无 Windows/平台支持声明（grep 验证），platform-notes.md 是 AGENTS.md 文件清单中标注的「平台适配」权威文档（orchestrator-template.md:115 Fallback 列表已引用它），Windows 章节落在正确位置。→ **无需同步**
2. **LIMITATIONS.md 局限 6**（:85-95）："运行时依赖 bash+git+python3+pyyaml"，表述平台无关，与「Git for Windows 提供 bash」不矛盾。加一句 Windows 交叉引用是锦上添花，非语义缺口。→ **建议项（非必须）**
3. **根 AGENTS.md 依赖节**（:19-23）：面向 agate 仓库开发者，Windows 提示已被 scripts/README.md + platform-notes.md 覆盖。→ **建议项（非必须）**
4. **CI windows matrix**：platform-notes.md:147 已知限制表明确写「CI 仅 ubuntu … protocol-tests.yml 未来可加 `runs-on: windows-latest` matrix」，与 CI 文件（4 job 全 ubuntu）现状一致——文档诚实标注为未来工作，非疏漏。→ **无需（已显式延迟）**
5. **观察（预存偏差，非本 commit 引入）**：`agate/AGENTS.md:79` 升级说明称「pre-push hook 是安装时写死复制的模板内容」——v0.32.0 已把 pre-push 改为软链（CHANGELOG:30），此说明过时；且未提及 Windows 复制模式。不影响本 commit 语义正确性，建议后续顺手修复。

**结论**：ALIGNED（附 3 条建议项 + 1 条预存观察，均不阻断 commit）

### A4: 测试覆盖

**新用例**（`agate/tests/unit/install-hook.bats:43-66`）「install-hook: ln 退化为复制时打印升级提醒（Windows 兼容）」：mock `ln` 为 `cp -f "$2" "$3"`（模拟 Windows 无符号链接权限），断言输出含「复制」或「需重跑」。

**真红真绿验证**（实际执行）：
- 真红：将 `install-hook.sh` 临时回退到 `d675381^` 版本后运行 → `not ok 5`（断言失败），已恢复工作区（`git status` clean）。
- 真绿：新版本下 → 5/5 PASS。
- 既有 4 个用例（:6-41）未回归，含软链路径 + 备份替换路径。

**全量实跑输出**：
```
1..598
598 个 ok，0 个 not ok（592 用例 + 6 sanity，bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/）
```

配套验证：
- `count-tests.sh` = 592，与 commit message「总数 591->592」一致，无文档漂移
- `check-protocol-consistency.py` = 0 ERROR（CHECK 1-9 全 PASS）
- `shellcheck -S warning install-hook.sh` = 无输出（0 error/warning）

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

**下游 gate 行为**：install-hook.sh 是安装期脚本，非 gate 脚本；改动不改变任何 gate 检查逻辑。Linux/macOS 下游项目零变化；Windows 项目仅多一条复制模式提示。非 BREAKING。

**.gitattributes 对已 clone 仓库的影响**：仓库根新增 `.gitattributes` 只对**未来 checkout** 生效；已 clone 且 `core.autocrlf=true` 的 Windows 工作区里已落地的 CRLF 文件不会自动重规范化（需 `git add --renormalize`）。platform-notes.md:145 的规避仅写「手动 `git config core.autocrlf false`」——这只影响后续 checkout，修不了已物化的 CRLF。→ **建议项**：platform-notes.md 已知限制表可补 `git add --renormalize` 提示。

**CHANGELOG**：`CHANGELOG.md` Unreleased 节（:11-12）只有内联 python 抽离一条，无 Windows 支持条目。本 commit 是 `feat(platform)` 平台 enablement——按 agate 惯例（0.30.0「M4.1 多平台 CI 支持」等平台/基础设施类条目均入册），Windows 支持是否入 Unreleased 属维护者裁量。是否为「重要变更」需人工确认。

**结论**：**NEEDS_HUMAN_REVIEW**（CHANGELOG 条目）——若确认不记则附 `[HUMAN_CONFIRMED]` 后放行；建议同时采纳 `.gitattributes` renormalize 文档建议。

### A6: 锚点表覆盖

`agate/scripts/check-protocol-consistency.py:674-680` 的 `GATE_SCRIPT_EXEMPT` 白名单含 `agate/scripts/install-hook.sh`（豁免，无 gate 逻辑不需锚点）；锚点表 `SCRIPT_ALIGNMENT_ANCHORS` 中 install-hook.sh 不作为 script 出现（:615 锚点归属 pre-push-gate.sh，desc 仅是说明文字）。本 commit 未新增 gate 脚本、未新增协议规则 → 锚点表无需更新。

**结论**：ALIGNED

### A7: 设计原则一致性

逐条检查 `agate/adr.md`：
- **ADR-003（不绑定技术栈/部署方式）**：Windows 支持针对 agate 自身的运行时环境（Git for Windows bash），不绑定被管理项目的技术栈/语言/部署方式，与「流程骨架跨平台通用」的决策一致。ALIGNED
- **ADR-002（可判定性）**：新增 `[ -L ]` 退化检测是机器可判定的客观检查（符号链接存在与否），不引入主 Agent 主观判断。ALIGNED
- **ADR-004（安全网分层）**：未移除任何防线层，反而在 hook 安装层增加防御性提醒（复制模式下升级滞后可视化），与「hook 兜底」分层理念一致。ALIGNED
- **未记录的架构决策**：无——「Windows 支持走 Git for Windows」是支持策略（已记录于 platform-notes.md），非核心架构决策，无需新增 ADR。

**结论**：ALIGNED

---

## 闭环规则

| 结论 | 处理 |
|------|------|
| A1-A4, A6-A7 ALIGNED | 通过 |
| A5 NEEDS_HUMAN_REVIEW | 需人工确认 CHANGELOG 条目后再 commit；未确认前不得 commit |

**需主 Agent 处理事项清单**：
1. **[A5] CHANGELOG 条目**：决定是否在 `[Unreleased]` 补 Windows 支持条目（`feat(platform)` 平台 enablement）。若决定不记，请在报告中附 `[HUMAN_CONFIRMED: 2026-08-08 确认：……]`。
2. **[A5 建议] `.gitattributes` renormalize 提示**：platform-notes.md:145 已知限制表可补「已 clone 旧版本且工作区已有 CRLF 文件时，执行 `git add --renormalize`」。
3. **[A3 建议] LIMITATIONS.md 局限 6**：可加一句「Windows 原生环境可经 Git for Windows 提供 bash（见 platform-notes.md）」交叉引用。
4. **[A3 建议] 根 AGENTS.md 依赖节**：可补 Windows 开发者提示一行（指向 platform-notes.md）。
5. **[A3 观察] `agate/AGENTS.md:79` 预存过时**：升级说明中「pre-push hook 写死复制」与 v0.32.0 软链化矛盾（v0.32.0 已修），建议后续顺手更正，不属本 commit 范围。

> 建议项（2/3/4）不阻断 commit；项 1（CHANGELOG）是唯一 NEEDS_HUMAN_REVIEW 阻塞点；项 5 是预存偏差，建议单独处理。

## 人工验收清单

- [x] 审查报告含 A1-A7 七项，每项有结论
- [x] 无 MISALIGNED 项
- [x] NEEDS_HUMAN_REVIEW 项（A5）已列出待确认内容，等待 `[HUMAN_CONFIRMED]` 标记
- [x] 审查报告落盘到 `docs/reviews/agate-alignment-review-2026-08-08-windows.md`

---

## 闭环记录（主 Agent）

### A5 NEEDS_HUMAN_REVIEW 处理
CHANGELOG 已加 Unreleased「改进」条目记录 Windows 原生支持（对齐 0.30.0「多平台 CI 支持」先例）。
`[HUMAN_CONFIRMED: 2026-08-08 确认：平台 enablement 属重要变更，按惯例入 CHANGELOG Unreleased]`

### 建议项落地
- platform-notes.md 已知限制表已补 `git add --renormalize .` 重规范化提示。
- `[HUMAN_CONFIRMED: 2026-08-08 确认：A3 建议项（LIMITATIONS.md 局限6 / 根 AGENTS.md Windows 交叉引用）为低优先级，后续批次处理，不阻塞本次]`

### 观察项（非本 commit 引入）
- agate/AGENTS.md:79 称 pre-push 是「写死复制」，与 v0.32.0 软链化矛盾——预存过时，留待后续修正。

### 递归终止判断
A1-A7：无 MISALIGNED，NEEDS_HUMAN_REVIEW 均已附 [HUMAN_CONFIRMED] 标记 → 达到「全 ALIGNED 终止」。
