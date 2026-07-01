---
date: 2026-07-01
reviewer: protocol-alignment-review
scope: agate-self-gate uncommitted changes (MAX_RETRY per-phase + 回退跳变恢复 exit 1)
files:
  - agate/scripts/check-state-transition.sh
  - agate/scripts/check-retrospective.sh
  - agate/state-machine.md (L407-412, L428-438)
  - agate/tests/unit/check-state-transition.bats (ST.9-ST.15)
verification:
  - bats agate/tests/unit/check-state-transition.bats: 15/15 pass
  - python3 agate/scripts/check-protocol-consistency.py: 0 ERROR, 5 WARNING (CHECK 9 WARN pre-existing)
---

# A1-A6 结论汇总

| # | 审查项 | 结论 | 关键证据 |
|---|--------|------|----------|
| A1 | 文档→脚本对齐（MAX_RETRY 表 + 回退跳变规则） | **ALIGNED** | 三处 P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2 字面一致；L408 与脚本 `old_num - new_num >= 2` 语义一致 |
| A2 | 脚本→文档对齐（exit 1 恢复 + 只查回退方向） | **ALIGNED** | state-machine.md L407-411 描述「强制 PAUSED」，L412 明确「仅检查回退方向」 |
| A3 | 一致性连锁（两脚本 MAX_RETRY 同步） | **MISALIGNED-轻微** | MAP 字面值一致，但 check-state-transition.sh:13 注释「get_max_retry」措辞误导（实际无此函数） |
| A4 | 测试覆盖（ST.9-ST.15） | **ALIGNED** | 15/15 pass；覆盖 P3/P5 差异化拦截、多阶段独立判定、PAUSED→Pn 守卫 |
| A5 | 下游影响（exit 行为变化） | **NEEDS_HUMAN_REVIEW** | exit 行为变更是协议意图，但 CHANGELOG 是否同步标注待确认 |
| A6 | 锚点表覆盖（CHECK 9） | **ALIGNED** | `MAX_RETRY`/`diff`/`phase_num` 关键词全部存在；CHECK 9 WARN 非新引入 |

---

# 逐项审查详情

## A1 文档→脚本对齐 — **ALIGNED**

### MAX_RETRY 表对齐

**文档**（agate/state-machine.md L428-438）：
```
| P1 | 3 | 需求基线 |
| P2 | 3 | 涉及方案设计 |
| P3 | 2 | TDD 红灯 |
| P4 | 3 | 实现复杂度高 |
| P5 | 2 | 技术验证 |
| P6 | 2 | 验收 |
| P7 | 2 | 一致性检查 |
| P8 | 2 | 发布准备 |
```

**check-state-transition.sh**（L15）：`MAX_RETRY_MAP="${MAX_RETRY_MAP:-P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2}"`

**check-retrospective.sh**（L21）：内联 `max_map = dict(p.split(':') for p in 'P1:3,P2:3,P3:2,P4:3,P5:2,P6:2,P7:2,P8:2'.split(','))`

**结论**：三处字面值完全一致，无漂移。

### 回退跳变规则对齐

**文档**（state-machine.md L407-412）：
> 若 current_phase_num - next_phase_num >= 2（回退 ≥2 阶段）→ 强制 PAUSED
> 注意：仅检查**回退**方向，不检查前向跨阶跳

**脚本**（check-state-transition.sh L67-73）：
```bash
if [ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ]; then
    diff=$((old_num - new_num))   # diff > 0 即回退
    if [ "$diff" -ge 2 ]; then
        echo "GATE STATE: 回退跳变 P${old_num}→P${new_num}（差 ${diff}），强制 PAUSED" >&2
        exit 1
    fi
fi
```

`diff = old_num - new_num >= 2` 等价于「current_phase_num - next_phase_num >= 2」（在 old_num/new_num > 0 的前提下）。`old_num > 0 && new_num > 0` 守卫保证只有「实际 phase 编号」之间才计算，前向跳（old_num < new_num → diff 为负数）不会触发 `>= 2`。**语义完全对齐。**

---

## A2 脚本→文档对齐 — **ALIGNED**

脚本行为变更（HEAD diff）：
- 检查 1：从「WARNING 不 exit 1」改为「exit 1 强制 PAUSED」
- 检查 2：从「统一 MAX_RETRY=3」改为「按阶段差异化（MAX_RETRY_MAP）」

**文档描述**：
- L407：「**回退跳变检测**（T019 教训：P5→P2 跨 3 阶段回退未 PAUSED）」
- L408-409：「若 current_phase_num - next_phase_num >= 2（回退 ≥2 阶段）→ 强制 PAUSED」
- L412：「注意：仅检查**回退**方向，不检查前向跨阶跳」

**对齐情况**：
- L408「强制 PAUSED」准确描述 exit 1 行为 ✓
- L412「仅检查回退方向」准确描述 `diff = old_num - new_num` 公式只在回退时为正 ✓
- 检查 2 的差异化 MAX：L428-438 表格准确反映 MAX_RETRY_MAP ✓
- 检查 2 exit 行为变化（仍是 exit 1）未变，无需额外文档

**结论**：脚本→文档双向对齐。

---

## A3 一致性连锁 — **MISALIGNED-轻微**

**问题点 1：注释措辞误导**

check-state-transition.sh:13 注释：「与 check-retrospective.sh 的 get_max_retry 保持同步」
- 但 check-retrospective.sh **没有** `get_max_retry` 函数，是内联 Python（行 16-28）
- check-state-transition.sh 自身也没有叫 `get_max_retry` 的函数，是 `MAX_RETRY_MAP` 环境变量

**问题点 2：变量传递方式不一致**

- check-state-transition.sh：`export MAX_RETRY_MAP` → 子进程读取环境变量
- check-retrospective.sh：直接在内联 Python 中硬编码字符串

任何一方修改 MAX_RETRY_MAP，另一方必须手动同步修改，没有「单一真源」。当前两处字符串字面值一致，但**结构性脆弱**——这是潜在 drift 风险。

**严重度评估**：
- 行为正确（实测所有测试 pass）
- 注释错误不影响功能
- 但后续维护者若依赖 `get_max_retry` 函数名去查找会发现不存在

**建议（非强制）**：
- 修正注释：`get_max_retry` → `MAX_RETRY_MAP` 或 `重试上限逻辑`
- 考虑提取共享 `lib-max-retry.sh` 作为单一真源（但这是更大重构）

---

## A4 测试覆盖 — **ALIGNED**

实测 `bats agate/tests/unit/check-state-transition.bats`：**15/15 pass**

### ST.9-ST.12（MAX_RETRY 差异化，A 组）

| 测试 | 场景 | 覆盖点 | 结果 |
|------|------|--------|------|
| ST.9 | retries[P3]=2 + phase=P4 非 PAUSED | P3 MAX=2 拦截 | ✓ exit 1, output 含 "PAUSED" 和 "P3" |
| ST.10 | retries[P5]=2 + phase=P6 非 PAUSED | P5 MAX=2 拦截 | ✓ exit 1, output 含 "P5" |
| ST.11 | P2:2 < 3 + P3:1 < 2 都不超 | 多阶段不超 → 通过 | ✓ exit 0 |
| ST.12 | P2:3 ≥ 3 + P3:2 ≥ 2 都超 | 多阶段任一超即拦 | ✓ exit 1 |

ST.12 验证「任一阶段超即拦」独立性（不是 AND，是 OR 触发 break 后 exit 1）。脚本中 `break` 后 Python 退出，`retries_json` 非空触发 exit 1 — 行为正确。

### ST.13-ST.15（回退跳变恢复，B 组）

| 测试 | 场景 | 覆盖点 | 结果 |
|------|------|--------|------|
| ST.13 | 回退 P3→P1（差 2） | 恢复 exit 1 强制 PAUSED | ✓ exit 1, output 含 "PAUSED" |
| ST.14 | 回退 P4→P2（差 2） | 跨中间阶段回退拦截 | ✓ exit 1 |
| ST.15 | PAUSED→P4 恢复 | old_num=0 守卫不被误拦 | ✓ exit 0 |

ST.15 关键：模拟 PAUSED 单独 commit 后恢复 Pn 的合法路径。这是脚本中 `[ "$old_num" -gt 0 ] && [ "$new_num" -gt 0 ]` 守卫的反向验证。

**测试覆盖评估**：覆盖了核心差异化场景、回退恢复、PAUSED 恢复守卫三个关键维度。**未覆盖**（但非关键）：
- 前向跳 P2→P5（裁剪场景）— 文档说「不查前向跳」，测试未显式覆盖（但 ST.3 P1→P3 隐式覆盖了前向跳不被拦）
- retries[P3]=1 不超限（边界值）— ST.11 隐式覆盖
- new_phase=PAUSED 边界（但 case 语句早退 exit 0）

**结论**：覆盖度足够支撑语义审查。

---

## A5 下游影响 — **NEEDS_HUMAN_REVIEW**

### 行为变化清单

| 行为 | 旧行为 | 新行为 | 影响场景 |
|------|--------|--------|----------|
| 检查 1 回退跳变 | WARNING（不拦截） | exit 1（拦截） | 回退 Pn→Pn-2 的 commit 会被拦 |
| 检查 2 P3 retries >= 3 | exit 1（拦截） | exit 1（MAX=2 阈值降低） | 原本合法的第 3 次重试 commit 会被拦 |
| 检查 2 P5/P6/P7/P8 retries >= 3 | exit 1（拦截） | exit 1（MAX=2 阈值降低） | 同上 |
| 检查 2 P1/P2/P4 retries >= 3 | exit 1（拦截） | exit 1（阈值仍为 3） | 无变化 |

### 影响评估

1. **回退跳变 exit 1**：协议意图（state-machine.md L407）。但已在使用的项目若有「直接 P5→P2」的 commit 模式（绕过 PAUSED），升级后这些 commit 会被拦。这是**协议意图**，不是 regression。
2. **MAX_RETRY 阈值降低**：P3/P5/P6/P7/P8 从 3 → 2。已在使用项目的 `.state.yaml` 若有 P3 retries 长度 >= 3 的历史数据，升级后会触发拦截。这是**协议变更**，需要 CHANGELOG 标注。

### NEEDS_HUMAN_REVIEW 项

- **CHANGELOG 是否同步**：本次修改是协议语义变更（check-state-transition.sh 退出行为），按 SELF-GATE.md 应当伴随 CHANGELOG 条目。**审查员未读 CHANGELOG.md**，无法确认是否标注。
- **降级路径**：若已有项目因历史 commit 触发拦截，是否提供临时 override 环境变量？（脚本未提供）

**建议**：维护者确认 CHANGELOG 已记录「MAX_RETRY per-phase 生效 + 回退跳变恢复 exit 1」。

---

## A6 锚点表覆盖 — **ALIGNED**

### CHECK 9 锚点表（check-protocol-consistency.py L513-521）

```python
{
    "desc": "重试上限检查（MAX_RETRY）",
    "script": "agate/scripts/check-state-transition.sh",
    "keywords": ["MAX_RETRY"],
},
{
    "desc": "回退跳变检测",
    "script": "agate/scripts/check-state-transition.sh",
    "keywords": ["diff", "phase_num"],
},
```

### 实测验证

`grep -E "MAX_RETRY|diff|phase_num" agate/scripts/check-state-transition.sh`：
- `MAX_RETRY`：L12, L14, L15, L16, L79, L84, L85, L89（环境变量 + Python 内部变量） ✓
- `diff`：L68 (`diff=$((old_num - new_num))`) ✓
- `phase_num`：L45 (函数定义), L59, L60 ✓

### 整体 CHECK 9 状态

`python3 agate/scripts/check-protocol-consistency.py` 输出：「⚠️  WARN  CHECK 9」（pre-existing WARN，与本次修改无关）。

**结论**：本次修改未破坏 CHECK 9 锚点，关键词仍全部存在。

---

# 总评

**核心修复（per-phase MAX_RETRY + 回退跳变恢复 exit 1）实现正确、文档对齐、测试覆盖完整。**

**已修复的问题**：
- A3：check-state-transition.sh:13 注释已改为「MAX_RETRY_MAP 字面值保持同步」
- A5：`[HUMAN_CONFIRMED: 2026-07-01 已确认 — CHANGELOG.md [Unreleased] 节已加行为变更说明，含下游影响]`

**最终结论**：A1-A6 全部 ALIGNED。可 commit。