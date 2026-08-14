---
phase: P2
task_id: TAG0009-tests-platform-neutral
type: review
parent: P2-design.md
trace_id: TAG0009-tests-platform-neutral-P2-20260813
status: approved
created: 2026-08-13
agent: plan-eng-review
---

# P2 Review — TAG0009 测试套件平台无关化（复评轮）

## 评审结论

**Status: approved**

上轮 needs-revision 的两处缺陷已由 architect 修订并复核通过（本复评独立实证验证），其余设计点与上轮锁定决策维持有效。修订内容未破坏其余章节（§2.3 shim / §2.5 symlink / §2.8 bc→awk / §5 gate_commands 抽查一致）。

---

## 缺陷 1 复核：§2.4 TD.1b/TDD.F8 修复机制与 exit 语义（已解决）

- **设计现状**（§2.4 锚点，P2-design.md L167）：改平台无关构造 **`env -u PATH`**（清除 PATH，不硬编码 Unix 路径），不再覆盖 PATH；`TEST_RUNNER` 指向不存在路径（→ exit 1，A-class）的既有语义由 TD.1 单独覆盖，明确"勿重复造"。
- **独立实证**：
  - `env -u PATH bash agate/scripts/check-tdd-red.sh` → **exit 3** ✓（与 `env -i PATH="/usr/bin:/bin"` → exit 3 等价，设计声明成立）
  - `env TEST_RUNNER="/nonexistent/fake-pytest" bash agate/scripts/check-tdd-red.sh` → **exit 1**（A-class error 127）
- **与用例断言对照**：TD.1b（check-tdd-red.bats L48-51）断言 `3 or 1`，TDD.F8（L380-383）断言 `3`——`env -u PATH` 构造下均成立 ✓；TD.1（L43-46）已断言 TEST_RUNNER=/nonexistent → exit 1，语义由 TD.1 覆盖、设计已注明不重复 ✓。
- **联动一致**：BDD-11 覆盖表（L243）、§5 P3 说明（L300）、§8 minimal_validation 修订记录均同步为 `env -u PATH`，无残留矛盾。

## 缺陷 2 复核：§2.1 R2 正则 + 计数（已解决）

- **设计现状**（§2.1 表格锚点，P2-design.md L98）：R2 正则改半角 `)` 且前字符类含引号——`(^\|[[:space:]]\|[=(\"'])python3([[:space:]]\|$)`；实测列标注 **110 行 25 文件**。
- **独立实证**：按设计表正则原样对 `agate/tests/` 全树（*.bats/*.bash/*.sh）grep → **110 行 / 25 文件** ✓。
- **与 §8 / P1 对照**：§8 minimal_validation（L374-380）同样为 110 行 25 文件，并记录修订轨迹（全角 `）` → 半角 `)` + 含引号前字符类，消除与"前字符类必须含引号（否则漏检 ci-gate-backstop 7 例）"经验教训的矛盾）；实测 25 文件与 P1 §8 清单（unit 21 + integration 2 + regression 2）逐文件吻合 ✓。无 "98 行" 残留。

## 回归抽查（修订未破坏其余设计点）

- **§2.3 harness shim**（L137-163）：`create_python_shim_bin` 内嵌绝对路径、探测时排除 `$BATS_TEST_TMPDIR` 避免自解析循环；9 + 1 注入清单与 P1 I1 的 41 例 script-side 失败文件一致；BDD-17 Linux 不劣化论证成立 ✓。
- **§2.5 symlink 平台分支**（L171-177）：install-hook.bats 两处拆 Linux 真软链 + Windows 复制模式（复用 L43 ln mock 先例）；[SCOPE+] pre-push-hook.bats L11 按同类平台分支处理、不改 P1 范围 ✓。
- **§2.8 bc→awk**（L210-215）：awk 求和实证空输入→0、单值→1、多值 2+1→3 ✓；原 `bc 2>/dev/null || echo 0 | tail -1` 管道优先级隐患属实（实际 L128 代码与设计"原"注释一致）；无 bc 模拟环境验证方案成立 ✓。
- **§5 gate_commands**（L286-300）：P3 `"bats"` 配合 TEST_RUNNER 逐文件红灯确认可执行；P5 = 全量 bats + consistency --strict + shellcheck + 扫描器（1 主 + 多辅）与 dispatch 要求一致 ✓。

## 锁定决策（上轮有效，修订后维持）

- 候选 A（harness shim + 静态扫描器 gate + 批量修测试）方向锁定，与 P1 SUGGEST-1/P1-review 判定一致。
- TD.1b/TDD.F8 用 `env -u PATH` 构造"PATH 无 python"，exit 3 语义保持（实证）；TEST_RUNNER 不存在路径 → exit 1 由 TD.1 覆盖，不重复。
- R2 正则半角 `)` + 前字符类含引号，实测口径 110 行 25 文件，P4 照此实现。
- scan-exempt 标记只豁免 R4（/tmp）样例文本、不豁免 R1/R2/R3——BDD-9 负向用例已写入设计（§2.1 L106 / BDD-9 表 L241 / 完成标准 L268）。
- [SCOPE+] pre-push-hook.bats L11 归 BDD-8 同类闭环；产品脚本 17 文件裸 python3 根治另立 TAG0010+。

## 评审依据（本复评独立实证）

- §2.4：`env -u PATH` → 3；`env -i PATH="/usr/bin:/bin"` → 3；TEST_RUNNER=/nonexistent → 1。与 §8 及上轮实测一致。
- §2.1 R2：设计表正则原样全树实测 110 行 25 文件，与 P1 §8 25 文件清单逐文件一致。
- §2.8：awk 求和三场景实证；agate-extract-context.sh L128 原文核验。

## 复审结论

上轮两处缺陷均已按 P2-review 复审要求修正且实证成立；其余章节修订未引入回归。本复评通过，**status: approved**，可进入 gate 检查与 P3。
