---
phase: P4
task_id: T001
type: review
parent: P4-implementation.md
agent: review
status: rejected
---

# T001 — P4 代码实现评审（review，偏执 Staff Engineer 视角）

> 被评审对象：`git diff 293924f..HEAD -- agate/scripts/`（流 A+B+C+D+fixture修复累计 diff，11 个脚本文件，620 行新增/70 行删除）
> 评审依据（优先级）：`P4-dispatch-context-review.md`（派发指引）> `agate/assets/review-roles/review.md`（角色定义）> `P2-design.md` §3.1-3.4（设计依据）> `P4-implementation.md`（实现记录 + 4 条 DESIGN_GAP）> `AGENTS.md`（脚本安全约定）
> 评审方式：全量读 diff + 关键结论实测复现（不轻信 implementer 自述）；shellcheck -S warning 对本次改动文件重跑复核（0 警告，与自查一致）。
> 结论：**1 个 CRITICAL（可复现）→ status: rejected**；另有 4 项非阻塞发现（INFORMATIONAL，供 implementer 下一轮一并处理）。

---

## Pass 1（CRITICAL）— 正确性与"数据未校验直接放行"风险

### [CRITICAL] agate/scripts/agate-frontmatter-check.py（新建）

**问题**：只捕获 `yaml.YAMLError`，未捕获 `yaml.safe_load` / 后续 `_check()` 可能抛出的其他异常
（尤其 `RecursionError`——深度嵌套结构解析会撞 Python 递归栈上限，`RecursionError` 继承自
`RuntimeError`，**不是** `yaml.YAMLError` 的子类，`except yaml.YAMLError` 捕不到）。而调用方
`check-frontmatter.sh` 是这样处理 Python 侧异常的：

```bash
ERRORS=$(FILE="$FILE" python3 "$SCRIPT_DIR/agate-frontmatter-check.py" 2>/dev/null || true)
if [ -n "$ERRORS" ]; then ... exit 1; fi
exit 0
```

`agate-frontmatter-check.py` 一旦在 `main()` 内部（无论是 `yaml.safe_load(block)` 解析阶段，还是
之后 `_check()` 内 `_value_depth()` 的递归深度校验阶段）抛出未捕获异常，Python 进程会非零退出并把
traceback 打到 stderr——`2>/dev/null` 把它丢了，`|| true` 把非零 exit code 也吞了，`ERRORS` 变量因为
崩溃发生在任何 `print()` 之前而是**空字符串** → `[ -n "$ERRORS" ]` 为假 → **exit 0（放行）**。

也就是说：这个校验器存在的目的就是拦住格式错误/超深嵌套的 frontmatter（`MAX_DEPTH=3` 校验本来就是
干这个的），但恰恰是"深到能让解析器自己崩溃"的输入，会绕过全部校验静默通过——这正是 Pass 1 要抓的
"看似有校验、实则未校验直接放行"类问题，且是本次新增的核心 gate 机制（BDD-2/4/5/6/7/8/12 全部依赖
这条链路）。

**已实测复现**（非推测）：

```bash
$ python3 -c "
import yaml
print(issubclass(RecursionError, yaml.YAMLError))"
False

$ python3 -c "
depth = 2000
s = '[' * depth + '1' + ']' * depth
import yaml
yaml.safe_load(s)"
# 抛 RecursionError，不是 yaml.YAMLError

# 端到端复现（构造一个深嵌套 risk_level 字段的 P1-requirements.md）：
$ bash agate/scripts/check-frontmatter.sh /tmp/.../P1-requirements.md
$ echo $?
0   # ← 应该报错（risk_level 既非法枚举值，又违反 MAX_DEPTH=3），实际"通过"
```

**Fix（任选其一，建议 A+B 都做，纵深防御）**：

- **A（必须）**：`agate-frontmatter-check.py` 里把解析和校验的异常处理从"只认 `yaml.YAMLError`"
  改为兜底捕获，例如：
  ```python
  try:
      data = yaml.safe_load(block)
  except yaml.YAMLError as e:
      print(str(e))
      return
  except RecursionError as e:
      print("{}: frontmatter 嵌套过深，解析器递归栈溢出（{}）".format(basename, e))
      return
  ```
  同时把 `_check(basename, schema, data)` 的调用也纳入同一层兜底（`_value_depth` 本身也是无保护
  递归，超深合法 dict/list——不触发 YAMLError 但能在校验阶段自己再炸一次），或者更简单地把
  `main()` 里"读文件之后"的全部逻辑包一层 `try: ... except Exception as e: print(...); return`，
  确保任何未预见异常都转成一行错误输出（从而让 `check-frontmatter.sh` 按预期 exit 1），而不是让
  异常穿透到 shell 层被 `2>/dev/null || true` 悄悄吃掉。同样的 `open(file_path, encoding="utf-8")`
  如果遇到非 UTF-8 内容会抛 `UnicodeDecodeError`，也在这个兜底范围内一并解决。
- **B（建议，纵深防御）**：`check-frontmatter.sh` 侧也不要用 `python3 ... 2>/dev/null || true` 把
  异常和错误信息一起吞掉——至少应该区分"python 正常退出但 stdout 为空（真的没错误）"和"python 非
  零退出（脚本自己崩了）"两种情况，后者也应该 exit 1（fail-closed：校验器自己挂了，不能被解读成
  "格式没问题"）。

---

## Pass 2（INFORMATIONAL）— 代码健康 / 边界稳健性

### [INFO] agate/scripts/check-gate.sh:23, :47（NEED_CONFIRM / SUGGEST 已解决匹配用子串而非整行匹配）

流 C 的"逐条匹配"实现（BDD-21）用 `grep -qF -- "$nc_desc"` / `grep -qF -- "$sg_desc"` 在
`NC_RESOLVED_FM` / `SG_RESOLVED_FM`（frontmatter 换行连接的已解决列表）里查找，这是**子串匹配**
不是整行匹配。如果某条"未解决"描述恰好是某条"已解决"描述文本的子串（例如描述写得比较短、或多条
描述有共同前缀），会被误判为"已解决"（漏判阻塞）。这类文本匹配的松紧问题正是 F14 教训想解决的
"内容对不上却被判定相同"的同类风险，只是这次不是数量维度而是子串维度。

Fix：`grep -qF` 改 `grep -qFx`（要求整行精确相等）——两处（NEED_CONFIRM 一处、SUGGEST 一处）都改。
如果确实需要"部分匹配"语义，建议在 P4-implementation.md 里补一句显式说明，而不是隐式行为。

### [INFO] agate/scripts/agate-md-field-get.py:123-124（`_format_value` 的 bool 分支是死代码）

```python
if field in BOOL_FIELDS:
    return str(value).lower() if isinstance(value, bool) else str(value).lower()
```
两个分支返回值完全一样，`if/else` 没有意义，读者会误以为这里对 bool 类型和非 bool 类型做了不同
处理。不影响行为，但建议简化为 `return str(value).lower()`，减少误导。

### [INFO] agate/scripts/check-changelog.sh（移除 fallback 后，主正则的分隔符集合未同步扩展）

`TASK_ID_SHORT` 去短前缀后完全等同 `TASK_ID`，主正则 `(^|[^0-9])${TASK_ID_SHORT}( |:|$|,|-)`
的合法结尾分隔符集合是 `空格/冒号/行尾/逗号/连字符`，不含句号、括号等常见 CHANGELOG 写法结尾符
（如 `"修复 TAG0001。"` 或 `"(TAG0001)"`）。这条正则本身不是本次改动引入的（P4 未碰这一行），但
本次移除的 `grep -qF "$TASK_ID"` 宽松 fallback 曾经能兜住这些正则覆盖不到的边界写法（副作用是引入
了 CL.7 要拦的误匹配，所以两害相权移除是对的，DESIGN_GAP 已如实记录）。移除后网变窄了：以前能通过
的一些"结尾标点不在分隔符集合里"的合法 CHANGELOG 写法，现在会被拦截（gate 变严，不是变松，方向上
安全，但可能造成误伤合法 commit）。建议下一轮顺手把分隔符集合扩展为 `( |:|$|,|-|\.|\)|\]|;|、|。)`
之类，弥补去掉 fallback 后收窄的覆盖面（不属于本次 CRITICAL，可与其他 INFO 一起排期）。

### [INFO] 流 D 硬切（`agate-state-yaml-check.py` task_id 正则 `^T\d+$` → `^T[A-Z]{2}\d+$`）——上线前需要一份迁移/宽限计划，不属于代码缺陷但请主 Agent 注意

代码本身对 BDD-25/26/P0-brief 的"硬切、不做双格式兼容（F19）"要求实现是对的，flow D 自报的 33 个
既有 fixture 回归也已被第 5 个 commit（`68e4173`，仅改 `agate/tests/**` 字面 task_id 值，未碰
`agate/scripts/`）修复干净，独立复核 `shellcheck -S warning` 对本次全部改动文件 0 警告，与自查一致。

但要提醒：这个正则一旦从 worktree 的 `agate/` 变成真正生效的 `~/.agate`（双工作区约定，
`AGENTS.md` "v2.0 改造期间执行约定"一节），**任何仍用旧格式 task_id 的在途任务目录（包括本任务
T001 自己——`docs/tasks/T001-v2.0-structured/.state.yaml` 的 `task_id: T001` 在新正则下会被判
"格式错误"）**会在下一次 commit 时被 `check-state-yaml.sh` 硬拦截，且当前代码没有任何迁移脚本或
宽限期开关。这不是本次 diff 的代码缺陷（硬切是 P0-brief 已定的设计决策，不是本角色评审范围），
但建议主 Agent 在 P7/P8 推进"把 v2.0 提升为 ~/.agate 正式版本"之前，先确认 T001 自身及其他任何
仍在用的旧格式任务目录有明确的迁移路径（例如批量改名 .state.yaml 的 task_id 字段），避免协议升级
当天所有在途任务集体被硬拦截却无人预料。

---

## 处理规则确认

以上所有修复均只描述"怎么改"，未直接改代码；CRITICAL 一处 → 按角色定义"处理规则"映射为
`status: rejected`；INFORMATIONAL 四处不阻塞，供 implementer 下一轮修复 CRITICAL 时顺手一并处理。

## 返回主 Agent

File: `docs/tasks/T001-v2.0-structured/P4-review.md`
Status: rejected
一句话结论：`agate-frontmatter-check.py` 对非 `yaml.YAMLError` 异常（已实测用 `RecursionError` 复现）没有兜底，会导致格式校验器崩溃后被 shell 层 `2>/dev/null || true` 吞掉，端到端表现为"应报错的坏格式 frontmatter 被静默放行（exit 0）"，需 implementer 补兜底异常处理后重新评审。
