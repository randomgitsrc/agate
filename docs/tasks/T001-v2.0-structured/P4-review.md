---
phase: P4
task_id: T001
type: review
parent: P4-implementation.md
agent: review
status: approved
---

# T001 — P4 代码实现复审（review，偏执 Staff Engineer 视角，第 2 轮 / 复审）

> 被评审对象：`git diff 68e4173..e566303 -- agate/scripts/`（本次修复轮 diff，4 个文件，
> 57 行新增 / 32 行删除：`agate-frontmatter-check.py`、`check-frontmatter.sh`、
> `agate-md-field-get.py`、`check-gate.sh`）。**不是重新审查整个 P4**，上一轮已审过、
> 本次未改动的代码不在本轮范围内。
> 评审依据（优先级）：`P4-dispatch-context-review-rereview.md`（本轮派发指引）>
> `agate/assets/review-roles/review.md`（角色定义）> 上一轮 `P4-review.md`（rejected 版本，
> git 历史 `git show 68e4173`... 该 commit 未含此文件，实为工作区未 commit 的对照基线，
> 全文已读，见下方逐条核对）> `P4-implementation.md`"## Review 修复"小节。
> 评审方式：全量读本次 diff + 独立复现 CRITICAL 修复前后行为差异（不采信 implementer/主
> Agent 自述）+ 独立重跑相关 bats 文件 + shellcheck 复核。
> 结论：**CRITICAL 已妥善修复，2 个 INFO 修复质量合格，未发现新引入问题 → status: approved**。

---

## CRITICAL 复审：agate-frontmatter-check.py 异常处理

### 修复内容核对

读 `agate/scripts/agate-frontmatter-check.py` 修复后全文（L193-239 `main()`）：`try` 块从
`open(file_path, ...)` 读文件开始，一路包到 `_check()` 调用和 `print("\n".join(errors))`，
覆盖了上一轮指出的全部三个风险点：
1. `open()` 的 `UnicodeDecodeError`（非 UTF-8 文件）
2. `yaml.safe_load(block)` 的 `RecursionError`（内层仍保留更具体的 `except yaml.YAMLError`
   优先分支，未被外层兜底吞掉具体错误信息，纵深合理）
3. `_check()` 内 `_value_depth()` 无保护递归可能再次触发的 `RecursionError`

外层 `except Exception as e: print(...)` 兜底，不再让异常穿透到 shell 层。`check-frontmatter.sh`
同步做了 Fix B：`set +e` 捕获 python 进程 exit code，非 0（脚本自己崩溃，兜底也没接住的情形）
fail-closed `exit 1` 并打印 stderr；ERRORS 非空（兜底捕获后 print 出来的一行）走原有判断路径,
同样 `exit 1`。两层防御分工清楚：Fix A 处理"预期内的异常类型"（占多数场景，python exit 0 +
stdout 有错误信息），Fix B 处理"任何未被 Fix A 接住的意外崩溃"（python 非 0 退出）。

### 独立复现（不采信自述，本轮自己重新构造）

用上一轮 review 报告给出的构造方式（`"[" * 2000 + "1" + "]" * 2000` 嵌套 `risk_level`）在
scratchpad 重新生成 fixture `P1-requirements.md`：

```
$ bash agate/scripts/check-frontmatter.sh /tmp/.../P1-requirements.md
GATE FRONTMATTER: .../P1-requirements.md frontmatter 格式错误：
  - P1-requirements.md: frontmatter 处理异常（maximum recursion depth exceeded while calling a Python object）
EXIT_CODE=1
```

同一 fixture 用 `git show 68e4173:agate/scripts/{agate-frontmatter-check.py,check-frontmatter.sh}`
还原出的修复前脚本重跑，确认 `EXIT_CODE=0`（放行）——**修复前后行为差异独立复现，exit 0 →
exit 1，与 implementer/主 Agent 自述一致，非误报**。

额外独立验证（派发指引未强制要求，本轮主动补做，用于确认兜底范围完整性）：
- `UnicodeDecodeError`（非 UTF-8 字节的 `risk_level` 值，注意须用精确文件名
  `P1-requirements.md` 才会进入 schema 判定分支，本轮排查中确认了这一点）：
  `check-frontmatter.sh` 正确输出
  `'utf-8' codec can't decode byte 0xff in position 16: invalid start byte`，`exit 1`。
- Fix B 的 fail-closed 分支单独验证（用一个总是以 `sys.exit(1)` 崩溃、且崩溃点在
  `main()` 假设的 try 保护范围之外的模拟脚本替换）：`check-frontmatter.sh` 正确输出
  `frontmatter 校验器异常退出（exit 1），fail-closed 拦截` 并转发 stderr 内容，`exit 1`。
  这也顺带验证了"若某未来改动在 Fix A 的 try 块之外引入新异常源（如 `os.environ["FILE"]`
  的 `KeyError`，目前确实在 try 块外），Fix B 仍能兜底 fail-closed"——两层防御在结构上是
  真正独立、而非表面上叠了两层实际只有一层生效。

### 额外检查：宽泛捕获本身是否引入新问题

- 未发现裸 `except:`（`grep -n "except:" agate-frontmatter-check.py check-frontmatter.sh`
  无匹配），实际写法均为 `except ImportError` / `except yaml.YAMLError as e` /
  `except Exception as e`，符合"不误捕 `BaseException` 子类（`KeyboardInterrupt`/
  `SystemExit`）"的预期（`Exception` 基类本就不含这两者，本次未见规避该边界的写法）。
- `except Exception` 捕获范围内的代码路径（读文件、YAML 解析、字段校验、递归深度计算）都是
  纯计算/IO 读操作，无副作用、无需要"硬失败"的系统级操作（如写文件、网络请求），兜底捕获后
  转成一行错误信息 + gate 侧 fail-closed exit 1，不存在"该让 pre-commit 硬失败的严重系统
  错误被静默吞掉"的风险——反而是本次修复要解决的问题本身（相反方向的静默放行）。
- 结论：兜底捕获范围合理，未引入新的吞错误风险。

**CRITICAL 判定：已妥善修复，独立复现确认，无新引入问题。**

---

## INFO 复审

### `agate-md-field-get.py` 死代码清理

`_format_value` 的 bool 分支从 `str(value).lower() if isinstance(value, bool) else
str(value).lower()` 简化为 `return str(value).lower()`——两个分支原本返回值完全相同，属于
纯化简，无行为变化。独立重跑 `bats agate/tests/unit/agate-md-field-get.bats`：**6/6 全绿**
（MDF.1-6），无回归。判定：合格。

### `check-gate.sh` NEED_CONFIRM/SUGGEST 匹配收紧为整行精确匹配

`grep -qF` → `grep -qFx`，两处（L86 NEED_CONFIRM 分支、L106 SUGGEST 分支，均在本次 diff 内）。
独立重跑 `bats agate/tests/unit/check-gate.bats agate/tests/unit/check-retrospective.bats
agate/tests/unit/check-gate-p1-review.bats`：**122/122 全绿**，无 `not ok`。另外核查了全仓库
对 `need_confirm_resolved`/`suggest_resolved` 字段的引用（`grep -rn`），确认唯一使用该字段的
测试 fixture 是 `check-retrospective.bats` 的 `RT_BDD21.1`（`need_confirm_resolved: ["z 的
边界条件需确认"]` 对应正文 `[NEED_CONFIRM] z 的边界条件需确认`，字面完全相等），且
`P2-design.md` §3.3.1 设计原文本就要求"**逐条匹配**：正文每条 NEED_CONFIRM 的描述须在
`need_confirm_resolved` 列表中找到对应项"——这个表述语义上就是精确匹配单条描述，`grep -qFx`
比之前的子串匹配 `grep -qF` 更贴合设计意图，不是收紧后产生新分歧。implementer"未发现回归、
无需 DESIGN_GAP"的结论可信。判定：合格。

---

## 未处理范围（确认与上一轮一致，非本轮判定依据）

- `check-changelog.sh` 分隔符集合扩展、流 D 硬切上线迁移计划——两项均在派发指引第 4 条明确
  排除在本轮复审范围外，本轮不作为 approve/reject 依据，维持"待后续排期"状态。

## 回归基线复核（独立重跑，与主 Agent 结论一致）

- `bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/
  agate/tests/sanity.bats`：**600/600**，无 `not ok`。
- `bash agate/tests/scripts/count-tests.sh`：**594**，与文档一致。
- `shellcheck -S warning agate/scripts/check-frontmatter.sh agate/scripts/check-gate.sh`：
  **0 警告**。
- `git diff 68e4173..e566303 --stat -- agate/scripts/`：改动范围严格限于派发指引允许的
  4 个文件，无越界改动。

## 处理规则确认

本轮复审未发现需要"只说怎么改"的新增修复项——CRITICAL 与 2 个 INFO 均已妥善处理，独立复现/
重跑均通过，未引入新的 CRITICAL 或回归。按角色定义"通过 / 无 BLOCKER" → `status: approved`。

## 返回主 Agent

File: `docs/tasks/T001-v2.0-structured/P4-review.md`
Status: approved
一句话结论：CRITICAL（frontmatter 校验器异常处理不完整导致坏格式静默放行）已用双层防御（应用层
兜底捕获 + shell 层 fail-closed）妥善修复，独立复现确认 exit 0 → exit 1，2 个 INFO 修复均为
安全的纯化简/精确匹配收紧，无回归，approve。
