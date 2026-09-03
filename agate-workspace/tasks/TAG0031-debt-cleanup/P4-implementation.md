---
phase: P4
task_id: TAG0031
parent: P3-test-cases.md
trace_id: TAG0031-P4-20260904
agent: implementer
created: 2026-09-04
implementation_dir: agate/scripts/
---

# P4-implementation.md — TAG0031 DEBT 存量修复批（三簇 + 收尾聚合索引）

> 本文件由主 Agent 轻量拼装（并行批次汇总，无跨批交叉修改，见 dispatch-protocol「派发编排机制」）。
> 三簇 implementer subagent + 1 个收尾聚合 subagent（debt 登记闭合）各自独立产出，主 Agent 未新增
> 实现判断，只做索引汇总 + 全量回归复核。

## 批次文件（对齐 P2 dispatch_plan 三簇 + P2 §1.1「跨簇共享写入」收尾）

| 批次 | 覆盖 DEBT | 改动文件 | 详情文件 |
|------|-----------|----------|----------|
| version-mgmt | DEBT0002/3/4 | `agate_common.py` / `agate-pack-offline.py` / `install-offline.py` / `agate-install.py` / `UPGRADING.md` / `scripts/README.md` | `P4-implementation-version-mgmt.md` |
| test-isolation | DEBT0007 | 无代码改动（TAG0024 已修复，仅验证） | `P4-implementation-test-isolation.md` |
| gate-robustness | DEBT0016/17/18 | `check-gate.py` | `P4-implementation-gate-robustness.md` |
| debt-collection（收尾聚合，非并行批次，三簇返回后独立执行） | 全部 7 条 status 闭合 + BDD-14 新增 2 条（DEBT0028/DEBT0029） | `agate-workspace/debt/tech-debt.md` | 见下「debt 登记收尾」节 |

## 改动文件清单（本次 commit 全部 diff）

```
agate/scripts/agate_common.py       # 新增 compute_sha256（DEBT0002）
agate/scripts/agate-pack-offline.py # 改 import 共享 compute_sha256 + ruff import 排序修正
agate/scripts/install-offline.py    # 改 import 共享 + 新增 _ensure_agate_common 引导函数（R1）
agate/scripts/agate-install.py      # _find_references 返回二元组 + 限流 WARNING（DEBT0004）
agate/UPGRADING.md                  # 信任边界文档（DEBT0003）
agate/scripts/README.md             # 信任边界文档（DEBT0003）
agate/scripts/check-gate.py         # resolve_workspace 权威解析（DEBT0016）+ 整行判定（DEBT0017）
                                     # + fail-closed 4 消费点（DEBT0018）
agate-workspace/debt/tech-debt.md   # 7 条 closed + 2 条新登记（DEBT0028/DEBT0029）
```

## 新增文件核对表

本次无新增文件（`git status --short agate/` 全部为 `M` 修改，无 `??` 新增），无需逐行填表。

## 主 Agent 全量回归复核（三簇 + 收尾聚合后，2026-09-04 本 worktree 实测）

命令：

```bash
timeout 180 python3 -m pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -n auto -q --tb=short
timeout 60 python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
timeout 30 shellcheck -S warning agate/scripts/*.sh
timeout 30 ~/.venvs/agate-dev/bin/ruff check agate/scripts/
```

结果：
- pytest：**1435 passed, 2 skipped, 0 failed**（三簇 21 项目标测试 + BDD-7/15 debt 登记验证测试全部转绿，无回归）
- consistency：**0 ERROR**（329 个既有 WARNING，与本任务改动无关的历史遗留项）
- shellcheck：**0 输出**（无 warning/error）
- ruff：**All checks passed!**（1 条非阻断 info：`agate-pack-offline.py:30` 的 `# noqa: E402` 后追加中文说明文字导致 ruff 的 noqa 语法解析警告，不影响 exit code/检查结果，已记录供 review 阶段判断是否值得顺手清理）

## 已修复的两处意外回归（非本次 7 条 DEBT 范围，均为三簇实现引入后立即发现修复）

1. **encoding 守卫误触发**（P3 阶段）：version-mgmt 簇测试代码字符串字面量单引号 `'rb'` 触发既有
   encoding 守卫，已改双引号修正（详见 P3-gate-diagnosis.md）。
2. **ruff import 排序**（P4 阶段）：`install-offline.py` 新增的 yaml/agate_common 探测导入块触发
   `ruff I001`，已补一空行分隔修正（详见 P4-gate-diagnosis.md）。

两处均已复核确认修复后不影响其余任何已确认通过的实现/测试。

## debt 登记收尾（详情见 `agate-workspace/debt/tech-debt.md`）

- **7 条闭合**：DEBT0002/0003/0004/0007/0016/0017/0018，均 `status: closed` + `closed_at: 2026-09-04` + closure evidence（引用具体 BDD/测试函数名），格式对齐 DEBT0005/DEBT0006 先例
- **2 条新登记**（BDD-14，同类扫描未处理实例）：
  - `DEBT0028`：`check-retrospective.py:74` / `agate-render-dispatch-prompt.py:191` 的 `dirname(dirname(...))` 本地路径推导同款模式（DEBT0016 同类，本次范围锁定只处理 check-gate.py 一处）
  - `DEBT0029`：`check-gate.py:881` gate_p2 bootstrap 骨架声明校验的子串判定（DEBT0017 同类，风险高于本体——触发 `return 1` 阻断性）

## SCOPE+ 状态

P2 阶段发现的 `[SCOPE+]`（R1 pyyaml checksum 顺序问题）已在 P2 commit 时回补 P1 基线
（`[BASELINE_CHANGE]` + `[SCOPE_RESOLVED]`），P4 阶段无新增 `[SCOPE+]`。
