# 证据：BDD-8 — analyst.md 新增 supplementable vs verification_env 判断树（RM-AG0014 主体）

验收方式：直接打开 HEAD 下的实际协议文件读新增内容，逐条核对 P1-requirements.md 该 BDD 的 Then 子句语义（非关键词存在性检查）。

## Then 子句逐项核对

- Then「该节旁新增一段落」：新增段落紧接在「三态判断规则」（`capability_requirements` 三态说明与「仅 `status: GAP` 触发 `[CAPABILITY_GAP]`」句）之后，标题 `**判断树：缺的是能力还是环境？**（标三态之前先过这一步）` —— 位置满足「三态判断规则节旁」。
- Then「明确区分：`capability_requirements` 的 supplementable 三态用于『能力』缺失（技能/工具/skill）」：树左枝「缺的是『agent 侧的能力』（看不见图 / 不会用某工具 / 没有某技能）」→ available / supplementable / GAP —— 举例覆盖技能/工具/skill，满足。
- Then「`verification_env` 用于『环境』依赖（跑起来需要的外部运行环境）」：树右枝「缺的是『运行环境』（服务没起 / 端口没通 / 数据库没建 / 依赖没装 / 平台不支持）→ 不走三态，走 verification_env 声明」—— 满足。
- Then「给出一个可操作的自问句（如『缺的是能力还是环境？』）」：树根首行即自问句「缺的是能力还是环境？」，另附**口诀**「换个更强的模型/角色就能做 → 能力问题（三态）；换谁来做都得先把服务起起来 → 环境问题」—— 可操作，满足。
- Then「避免重演 TAG0009 的机制误用」：段末「**把环境问题标成 `supplementable` 是机制误用**（TAG0009 教训：环境问题被错标 supplementable，验证陷入无止损的试错循环），属『不可重试』类，应立即改正声明方式，而不是当环境故障反复重试」—— 显式点名 TAG0009 并给出正确动作，满足。
- 跨文件一致性：与 P1 卡（BDD-5）判断树同结论、同「机制误用」定性；与 dispatch-protocol.md「verification_env 失败处理协议」不可重试类判据（机制误用型不消耗轮次预算）一致，无矛盾表述。

## 实际文件文本摘录（HEAD）

### `agate/assets/execution-roles/analyst.md` L118-135

```markdown
**判断树：缺的是能力还是环境？**（标三态之前先过这一步）

```
缺的是能力还是环境？
├─ 缺的是「agent 侧的能力」（看不见图 / 不会用某工具 / 没有某技能）
│   └─ 走 capability_requirements 三态：
│      ├─ 当前就有 ......................................... available
│      ├─ 当前没有，但能派子角色 / 注入 skill / 换工具补上 .... supplementable
│      │   （必须写清补充方式，写不清等同 GAP）
│      └─ 当前没有且补不上 ................................. GAP → [CAPABILITY_GAP]
└─ 缺的是「运行环境」（服务没起 / 端口没通 / 数据库没建 / 依赖没装 / 平台不支持）
    └─ 不走三态，走 verification_env 声明（P1 卡片「verification_env vs supplementable
       边界判断树」+ dispatch-protocol.md「verification_env 失败处理协议」）
```

**口诀**：换个更强的模型/角色就能做 → 能力问题（三态）；换谁来做都得先把服务起起来 → 环境问题（`verification_env`）。
**把环境问题标成 `supplementable` 是机制误用**（TAG0009 教训：环境问题被错标 supplementable，验证陷入无止损的试错循环），属"不可重试"类，应立即改正声明方式，而不是当环境故障反复重试。

```

## 结论

**PASS** —— 判断树位于三态判断规则旁，能力/环境两侧定义清晰，含可操作自问句与口诀，并显式引 TAG0009 机制误用教训。
