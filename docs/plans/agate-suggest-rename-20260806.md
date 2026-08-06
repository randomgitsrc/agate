# NEED_CONFIRM 三值重命名 plan (v0.30.2)

> 2026-08-06 | 来源：v0.30.1 复盘 — 标记视觉混淆

## 背景

v0.30.1 引入 `[NEED_CONFIRM倾向:]` 作为倾向项标记。问题：
- 与 `[NEED_CONFIRM]` 共享前缀，肉眼/grep 容易混淆
- typo（如 `[NEED_CONFIRM倾 推荐方案]`）debug 时困惑
- 不符合 agate 全英文标记惯例（NEED_CONFIRM、PROD_TOUCHED、SCOPE_RESOLVED 等）

## 设计

### 标记重命名

| 旧 | 新 | 语义 |
|---|---|---|
| `[NEED_CONFIRM] xxx` | `[NEED_CONFIRM] xxx` | 阻塞：等用户决策 |
| `[NEED_CONFIRM倾向: X]` | `[SUGGEST: 推荐 X，理由 Y]` | 不阻塞：主 Agent 可采纳 |
| `[NO_NEED_CONFIRM]` | `[NO_NEED_CONFIRM]` | 无待确认项 |

**核心原则**：两个标记**完全不共享前缀**——`[NEED_CONFIRM]` vs `[SUGGEST:` 没有任何字符重叠。视觉、grep、正则都完全可区分。

### 正则

- 阻塞：`^\s*-?\s*\[NEED_CONFIRM\]`（`]` 紧跟 `NEED_CONFIRM`）
- 倾向：`^\s*-?\s*\[SUGGEST:`（`[SUGGEST:` 后接任意字符，允许中文紧跟）
- 负向：`^\s*-?\s*\[NO_NEED_CONFIRM\]`

为什么不强制 `\s`（空格）：CJK 紧跟冒号是常见写法（`[SUGGEST:推荐X]`），强制空格会让中文写法被静默忽略（不在阻塞、也不在倾向、也不在负向——无声明 WARNING）。倾向正则放宽到 `\[SUGGEST:` 接受中英文两种写法。

### gate 检测逻辑（check-gate.sh P1）

1. **NC_BLOCKING** = grep 阻塞正则 → >0 则 exit 1
2. **NC_SUGGEST** = grep 倾向正则 → >0 则 WARNING 不阻塞
3. **缺失声明 WARNING**：如果 NC_BLOCKING=0、NC_SUGGEST=0、且无 [NO_NEED_CONFIRM] → WARNING
4. **格式不符检测**：用两步 ERE 写法（check-gate.sh 全程用 `grep -E`，不引入 PCRE 依赖）

```bash
# 中间态 1：[SUGGEST 开头但不是 [SUGGEST:
if grep -q '\[SUGGEST' "$P1_FILE" && ! grep -q '\[SUGGEST:' "$P1_FILE"; then
    echo "GATE P1: SUGGEST 格式不符。合法格式：[SUGGEST: 推荐 X，理由 Y]" >&2
    exit 1
fi
# 中间态 2：[NEED_CONFIRM 开头但既不是 [NEED_CONFIRM] 也不是合法 [SUGGEST:
if grep -q '\[NEED_CONFIRM' "$P1_FILE"; then
    # 提取所有 [NEED_CONFIRM 开头的行，去掉合法 [NEED_CONFIRM] 和 [NEED_CONFIRM] 内的子串
    if grep -E '^\s*-?\s*\[NEED_CONFIRM($|[^a-zA-Z\u4e00-\u9fff])' "$P1_FILE" | grep -vE '^\s*-?\s*\[NEED_CONFIRM\]' | grep -q '.'; then
        # 有非法的 [NEED_CONFIRM 变体（如 [NEED_CONFIRM倾向:] 旧标记）
        echo "GATE P1: NEED_CONFIRM 格式不符。v0.30.2 起 [NEED_CONFIRM倾向:] 已重命名为 [SUGGEST: ...]" >&2
        exit 1
    fi
fi
```

实际实现可简化（check-gate.sh 是 bash 不支持 PCRE 命名字符类），用 `LC_ALL=C grep -E` 保证 ASCII 行为：
```bash
# 旧标记 [NEED_CONFIRM倾向:] 检测
if grep -qE '\[NEED_CONFIRM倾向:' "$P1_FILE"; then
    echo "GATE P1: 检测到旧标记 [NEED_CONFIRM倾向:]。v0.30.2 起已重命名为 [SUGGEST: ...]" >&2
    exit 1
fi
```

### 何时用哪个

**`[SUGGEST:]`**（倾向项）：
- 你知道推荐方案，留个底（"如果用户没异议就采纳"）
- 主 Agent 读 P1 时直接采纳推荐，无需问用户
- 仅作为审计痕迹（CI 记录倾向项数量）
- 适用：非破坏性、非业务方向

**`[NEED_CONFIRM]`**（阻塞项）：
- 真无方向，需人定夺
- 涉及破坏性变更（删除数据/迁移 schema/不可逆外部调用）
- 涉及业务方向判断（产品/商业模式/合规）

**`[NO_NEED_CONFIRM]`**（负向）：无待确认项。

### 检测 typo（自动防御）

不引入 PCRE 依赖（check-gate.sh 全程用 `grep -E`）。检测两类旧标记残留：

```bash
# 旧标记 [NEED_CONFIRM倾向:] 残留检测
if grep -qE '\[NEED_CONFIRM倾向:' "$P1_FILE"; then
    echo "GATE P1: 检测到旧标记 [NEED_CONFIRM倾向:]。v0.30.2 起已重命名为 [SUGGEST: ...]" >&2
    exit 1
fi
```

[SUGGEST 写法错误] 检测：`grep -q '\[SUGGEST'`（含任何 SUGGEST）但 `! grep -q '\[SUGGEST:'`（不是合法前缀）→ 报格式不符。

### 全量改动（15 个文件）

1. `agate/scripts/check-gate.sh` - 正则 + 错误信息（4 处）+ typo 兜底检测
2. `agate/scripts/check-protocol-consistency.py` - CHECK 9 锚点 keywords
3. `agate/tests/unit/check-gate.bats` - G_NC_TENDENCY.1/.2 测试名 + fixture → G_SUGGEST.1/.2
4. `agate/tests/integration/consistency.bats` - CON.12
5. `agate/phase-cards/P1-requirements.md` - 分级格式说明
6. `agate/dispatch-protocol.md` - 4 处
7. `agate/state-machine.md` - 2 处
8. `agate/rules/state-transitions.md` - 1 处
9. `agate/WORKFLOW.md` - 1 处
10. `agate/assets/execution-roles/analyst.md` - "何时用 SUGGEST" 整节
11. `agate/assets/templates/task-files.md` - 模板
12. `agate/CONTEXT.md` - 术语表
13. `docs/hardening-roadmap.md` - 状态描述
14. `CHANGELOG.md` - v0.30.2 条目
15. `README.md` - badge v0.30.2

### 测试

- 现有 G_NC_TENDENCY.1/.2 测试名改为 `G_SUGGEST.1/.2`，fixture 改为 `[SUGGEST: X]`
- 新增测试：`[NEED_CONFIRM倾向: X]` 旧标记 → 报格式不符（验证 typo 兜底）
- 新增测试：`[SUGGEST xxx]`（漏冒号）→ 报格式不符

## Self-Review

### 不增加 agent 负担

- 标记数量不变（还是三种：阻塞/倾向/负向）
- 倾向项从"共享前缀的变体"改为"完全独立的标记"——LLM 学习成本反而降低（不需要理解前缀嵌套关系）
- 错误信息更明确（typo 时直接告诉 agent 两种合法格式）

### 向后兼容

- **破坏性变更**：v0.30.1 引入的 `[NEED_CONFIRM倾向:]` 在 v0.30.2 报格式不符。但 v0.30.1 发布 < 24h，实际使用者几乎没有。
- CHANGELOG 明确标注为 BREAKING。

### 风险

- 中间态检测正则需要边界测试（如 `[SUGGEST` 后跟中文括号、空格等）
- grep 性能影响可忽略（仅 P1 文件，单文件正则）

## 不做的

- **不改 P6** 的 NEED_CONFIRM 检测（plan "P6 不同步"，语义不同）
- **不改 ADR-002/006**（T080 retro self-gate-review 的 A7 建议 ADR-008，是更大话题）
- **不改历史文档**：`docs/reviews/agate-t080-retro-self-gate-review-20260806.md` 和 `docs/plans/agate-t080-retro-fixes-20260806.md` 含旧标记引用，作为历史记录保留（不改）
- **不改其他含 `[NEED_CONFIRM]` 的文件**（都是阻塞 NEED_CONFIRM 用法，不涉及倾向项）：
  - `agate/loop-orchestration.md` (L51/54/106) — 硬中断点
  - `agate/role-system.md` (L61) — plan-ceo-review 触发
  - `agate/assets/templates/active-tasks-template.md` (L45) — "无行首 [NEED_CONFIRM]"
  - `agate/assets/execution-roles/verifier.md` — P6 NEED_CONFIRM
  - `agate/assets/execution-roles/architect.md` (L104) — `[DEVIATION]+[NEED_CONFIRM]`
  - `agate/assets/execution-roles/consistency-reviewer.md` (L50) — 未决项清零