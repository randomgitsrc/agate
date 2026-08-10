# BDD-22: SCOPE_RESOLVED 状态结构化后闭环门禁仍工作

## P5 测试证据
- `ok 402 SC_BDD22.1 BDD-22: check-scope-resolved.sh 有 SCOPE+ + P1 frontmatter scope_resolved 非空列表 → 闭环判定通过`

## 本次验收独立复现
构造正文含 `[SCOPE+]` 发现性标记（保持散文）+ P1 frontmatter `scope_resolved` 非空列表（对应
"已解决"状态结构化）：
```yaml
---
phase: P1
scope_resolved:
  - 新增校验器触发 CHECK9 覆盖
---
[SCOPE+] 新增校验器触发 CHECK9 覆盖
```
执行：
```
$ bash agate/scripts/check-scope-resolved.sh <TASK_DIR>
GATE SCOPE: P1-requirements.md 有 [SCOPE+]，P1 frontmatter scope_resolved 非空（1 项已解决）
REAL EXIT=0
```
exit=0（通过），错误/提示信息明确引用"P1 frontmatter scope_resolved 非空"作为判定依据，
`[SCOPE+]` 散文标记本体未被要求删除或迁移（BDD-23 的边界在此同时得到印证）。

## DESIGN_GAP 交叉核对（P4-implementation.md 第 342 行）
[DESIGN_GAP]：check-scope-resolved.sh 对"scope_resolved 字段存在但为空列表"与"字段完全不存在"
两种情况未做区分——两者都会落入原有正文 `[SCOPE_RESOLVED]` grep 回退判定，而非把"字段存在但空"
直接判定为拦截。implementer 给出的理由：① agate-md-field-get.py 的 op 输出对两种情况都是空
字符串，仅凭 op 输出无法区分；② P3 测试只覆盖了"非空通过"与"字段完全不存在"两种场景，未覆盖
"存在但空列表"这一中间态；③ 功能后果上二者通常等价（只要正文没有遗留旧式散文标记）。
implementer 同时指出了一个已知风险：若任务显式声明 `scope_resolved: []` 但正文残留旧式
`[SCOPE_RESOLVED]` 散文标记，会被误判通过而非因空列表被拦截——概率极低但存在。
本次验收观察：这个 DESIGN_GAP 不影响 SC_BDD22.1 已验证的场景（非空列表通过），但意味着
"有 SCOPE+ 无 resolved"（字面理解为"字段存在但空"）这一特定组合未被验证为"立即拦截"，
只验证了"字段完全不存在时回退到正文 grep"。这是一个真实存在的语义边界缺口，如实记录，
不影响本条 BDD-22 已测场景的判定。

## 判定
PASS
