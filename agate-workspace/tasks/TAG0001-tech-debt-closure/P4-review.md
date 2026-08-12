---
phase: P4
task_id: TAG0001-tech-debt-closure
type: review
parent: P4-implementation.md
trace_id: TAG0001-P4-20260812
status: approved
created: 2026-08-12
agent: review
---

# TAG0001 — P4 实现评审（tech-debt 登记闭环 + 归类修正）

> 角色：review（偏执 Staff Engineer）。评审对象：worktree `agate/` 的 P4 实现（core 5 文件 + docs 12 文件集 + 测试 fixture 修复）。
> 输入：P4-dispatch-context-review.md（强制派发指引）+ P2-design.md（对照方案）+ P1-requirements.md（20 BDD）+ P3-test-cases.md（测试契约）+ P4-implementation-core.md / -docs.md（实现记录）。
> 方法：只读评审 + 独立对抗性实测（不修改任何实现文件）。
> 环境：`[PROD_NOT_TOUCHED]`——本次评审仅读文件 + 在 /tmp 与 bats 临时目录跑验证，未写生产环境、未改 `~/.agate`。

## 结论摘要

**status: approved**（0 BLOCKER / 0 CRITICAL，2 条 INFORMATIONAL 观察，不阻断）。

评审通过 Pass 1（数据安全与正确性）+ Pass 2（代码健康）+ 行为不变回归 + DESIGN_GAP 复核，全部符合 P2-design.md D1-D4 方案与 P1 20 条 BDD 契约。核心 schema 校验器、fail-closed 薄壳、回退覆盖比对、P8 留痕检查在对抗性实测下均按契约工作。

---

## Pass 1 — 数据安全与正确性（CRITICAL）

### 1.1 agate-debt-check.py schema 校验器（BDD-5..10）

**必填字段**：`agate/scripts/agate-debt-check.py:81-83`（`if f not in data or data[f] is None`）——缺字段与显式 null 均拦截，实测 `status: null` 报「缺必填字段 status」✓。

**枚举校验**：`agate/scripts/agate-debt-check.py:85-88`，四组枚举（category/status/priority/source）均为 `in` 集合判定，非字典成员报非法值。实测 `category: bug` 拦截 ✓。

**evidence/closure_criteria 非空 list**：`agate/scripts/agate-debt-check.py:98-104`——`list` 类型 + 非空双重判定。实测 `evidence: []` 与 `closure_criteria: []` 均报「不能为空」✓。

**closed 准入（BDD-8）**：`agate/scripts/agate-debt-check.py:111-118`——`task_id` 非空 + `serialize_evidence` 序列化文本同时含 `task_id` 与 `P[56]` 标记。三向实测均正确：
- closed 缺 task_id → 拦截 ✓
- closed 有 task_id 但 evidence 无 P5/P6 → 拦截 ✓
- closed 有 task_id + evidence 含 `docs/tasks/TAG0005/P5-verification.md` → 放行 ✓

**id 唯一性**：`agate/scripts/agate-debt-check.py:179-181`（`seen_ids` 集合）——实测同文件重复 id 拦截 ✓。

**解析安全**：`yaml.safe_load`（`agate/scripts/agate-debt-check.py:33` / `:167` / `:133`）——无 `yaml.load` 反序列化漏洞面；`BLOCK_RE` 正则（`:39`）与 `check-protocol-consistency.py:136` 的 `extract_code_blocks` 同构（`r"```yaml\n(.*?)\n```"`），复用既有提取机制 ✓。无 yaml 块 → `:160-161` no-op（BDD-10 实测：无文件/空文件/纯正文均 exit 0 无输出）✓。

**异常兜底**：YAML 解析失败（`:168-171`）、非 dict 映射（`:174-177`）、读取异常（`:153-157`）均转为错误行而非静默放行，fail-closed 方向正确。实测畸形 YAML 报「YAML 解析失败」、list 顶层报「必须为 key: value 映射」✓。

**边界确认**：`created_at` 未加引号被 `yaml.safe_load` 解析为 `datetime.date` 时，`agate/scripts/agate-debt-check.py:92-94` 有显式豁免（date/datetime 不报类型错误），实测 `created_at: 2026-08-12` 通过 ✓（模板示例同此形态，见 tech-debt-template.md:59/78/98）。

### 1.2 check-debt.sh fail-closed 薄壳（D3）

`agate/scripts/check-debt.sh` FILE 模式复刻 `check-frontmatter.sh:20-40` 契约：
- `[ ! -f "$FILE" ] && exit 0`（`:54`）——文件不存在 no-op ✓
- python 非零退出 → exit 1 + stderr 透传（`:64-69`）——校验器自身崩溃也拦截 ✓
- ERRORS 非空 → exit 1（`:72-78`）——schema 非法拦截 ✓
- 双保险：python 侧 `except FileNotFoundError: return`（agate-debt-check.py:153-154）与薄壳侧 `[ ! -f ]` 互不依赖，无 TOCTOU 单点。

实测 5 种非法输入（dup-id / bad-yaml / empty-list / non-dict / null-status）全部经薄壳转 exit 1 ✓；无文件 exit 0 ✓；无参数 exit 1（`${1:?...}` fail-closed）✓。

**回退覆盖比对（BDD-13/14/15，`check-debt.sh:21-50`）**：
- `git log --all --format='%H%x09%s' --grep='^retreat:'`（`:34`）只读提取，零新增埋点，与 agate-retreat-to.sh 提交格式一致（P2 §2.6 边界）✓
- 覆盖集合：`agate-debt-check.py --covered-hashes`（`:40`）只取 `source: retreat` 条目 evidence 的 7-40 位 hex token（`agate-debt-check.py:123-143`），去重后逐行输出 ✓
- 比对：short（前 7 位）或 full hash 命中即覆盖（`check-debt.sh:45`）✓
- **恒 exit 0**（`:49`）——WARNING 不阻断，符合 P1 SUGGEST #4 / BDD-13 ✓
- tech-debt.md 不存在时 COVERED 为空 → 每条 retreat 都打缺失 WARNING（BDD-13 含未建文件情形）✓ 实测确认。
- 实测三态：① retreat 存在 + 无 tech-debt.md → WARNING + exit 0；② evidence 引用 full 40-char hash → 无 WARNING；③ evidence 引用 short hash → 无 WARNING；④ 空 tech-debt（无 retreat 条目）→ WARNING ✓

### 1.3 P8 debt_check 留痕（BDD-16/17/18，check-gate.sh）

`agate/scripts/check-gate.sh:425-430`——插在 bump_type 检查（`:421-424`）之后、version 检查（`:431`）之前，与 P2 §2.5「bump_type 之后、version 之前」精确一致 ✓。
- 缺失 → exit 1 + `GATE P8: ... 缺 debt_check 字段` ✓
- 存在（值任意含 none/未关闭债务）→ 放行，不因内容拦截（BDD-17）✓
- 既有 P8 行为未误伤：bump_type/version/CHANGELOG/tag 检查原样保留（`:431-475`），G8.1（缺 bump_type 仍 exit 1）、G8.5（无 P8 文件仍 exit 1）实测通过；G8.9（缺 debt_check → exit 1）/ G8.10（`debt_check: none` → exit 2）实测通过（见 §4 回归）。

### 1.4 归类修正同步面（BDD-1..4）

- WORKFLOW.md 目录图含 `debt/` 且 `agents/` 注释去 tech-debt：`agate/WORKFLOW.md:79`（「固定 9 个子目录」）+ `:84`（`├── debt/  # 技术债登记`）+ `:85`（`# agent 输入知识（project.md / memory）`）✓
- 三处 mkdir 同一 9 子目录集字面量：`agate/SETUP.md:114` / `agate/orchestrator-template.md:102` / `agate/state-machine.md:40` 均为 `{roadmap,tasks,agents,archived,reviews,decisions,plans,logs,debt}`——grep 全 worktree 确认无 8 集残留（除 TAG0003 P6-evidence 历史日志 `bdd-01-init.log:16`，属已验收证据存档，不在改动范围）✓
- UPGRADING v0.43.0 节含 `debt/tech-debt.md` 路径、8→9 说明、P8 `debt_check` 字段、回退强制（`agate/UPGRADING.md:92-105`）✓；SETUP 保留 `agents` mkdir（`agate/SETUP.md:113` 的独立 mkdir 行）不冲突 ✓
- TAG0003 口径重验：P1-requirements BDD-1 与 P6-acceptance BDD-1 均含「9 子目录」修订注（P4-implementation-docs.md §10）✓

### 1.5 review 角色卡可发现性（BDD-19/20）

`agate/assets/review-roles/plan-eng-review.md:19` 追加「须用标准 DEBT 条目格式（模板 ... evidence 必填）——强制格式，不强制产出」✓。模板含三分法判据 + 「不登记」合法出口 + 「登记 DEBT 不豁免当前任务」硬规则（`agate/assets/templates/tech-debt-template.md:9-15`）✓。

---

## Pass 2 — 代码健康（INFORMATIONAL）

- **shellcheck**：`check-debt.sh` / `check-gate.sh` / `agate-retreat-to.sh` `shellcheck -S warning` 0 告警 ✓
- **set -euo pipefail**：`check-debt.sh:15` / `check-gate.sh` 既有 / `agate-retreat-to.sh` 既有；FILE 模式 python 调用用 `set +e` + `$?` 捕获（`:59-62`）而非裸命令替换，pipefail 下不误触 exit ✓
- **Python 错误处理**：`agate-debt-check.py` 无裸 `except:` 吞错，所有异常路径均转错误行或 fail-closed 退出 ✓
- **薄壳-校验器契约一致**：FILE 模式经 `FILE` 环境变量传参（`check-debt.sh:60`，shell 注入面为零）；`--covered-hashes` 模式经 argv 传路径（`check-debt.sh:40` 显式 `"$DEBT_FILE"`）——两种模式路径传递与 python 侧读取（`os.environ.get("FILE")` / `sys.argv[1]`）一一对应 ✓
- **临时文件清理**：`PY_STDERR_FILE` 两条退出路径均 `rm -f`（`:67`/`:70`）✓
- **资源泄漏**：无未关闭句柄；`mktemp` 在异常路径前已清理 ✓

**观察 O1（不阻断，建议后续加固）**：`check-debt.sh:22` 的 `$2`（REPO_ROOT）仅用于工作区解析（`:25`），而 `git log`（`:34`）在调用方当前目录执行。若调用方不在 repo 根却传 `$2`，工作区解析与 git log 读取的仓库可能不一致。当前 bats 用例均先 `cd "$repo"` 再调用（`test_bdd_13/14/15`），该路径行为正确；且脚本设计契约是「在项目根运行」（P2 §2.3「REPO_ROOT 取当前目录」），故非阻断。建议后续用 `git -C "$REPO_ROOT" log` 显式锚定（P2 §2.6 零新增埋点原则不受影响）。

**观察 O2（不阻断，设计已接受）**：`--covered-hashes` 的 hex token 启发式（`agate-debt-check.py:40`）可能把 evidence 中非提交哈希的 7+ 位 hex 串误入覆盖集合，造成个别 retreat 被误判已覆盖。此为 P2 §10 已诚实标注的召回局限（触发器非排名工具），非实现缺陷。

---

## 行为不变回归（P5 预跑，非 P5 gate 结论）

| 验证 | 结果 |
|---|---|
| `bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/` | 1..676，**0 not ok**（675 ok + 2 正常 skip），TAP 可解析 |
| `count-tests.sh` | 670（unit/regression/integration）+ 6（sanity）= **676**，与 P2 §8「654 既有 + 22 新增」吻合（P3 后基线） |
| `agate-debt-check.bats`（20 条） | 20/20 绿（含 BDD-1..20 全映射） |
| `check-gate.bats`（113 条） | 113/113 绿（G8.9 红转绿 + G8.10 守卫保持 + G8.1-8.8 无回归） |
| `agate-retreat-to.bats`（5 条） | 5/5 绿（DEBT 提醒行不破坏既有断言） |
| `python3 agate/scripts/check-protocol-consistency.py` | 0 ERROR（CHECK 1-9 全 PASS，含新 check-debt.sh 锚点 CHECK 9） |
| `shellcheck -S warning` 三脚本 | 0 告警 |
| G8 fixture 同步（SCOPE+ #1） | G8.2/3/4/6/7/8 + R5.1-3 均含 `debt_check: none`，既有用例行为保持 exit 2 |

> 注意：count-tests.sh 输出的「总计：670」不含 `sanity.bats`（脚本只扫 unit/regression/integration，`agate/tests/scripts/count-tests.sh:13`），全量 676 = 670 + 6（sanity），与 dispatch-context「既有 654 + 新增 22」口径一致，无漂移。

---

## DESIGN_GAP 复核（dispatch-context 第 7 项）

**[DESIGN_GAP: P3 测试 fixture test_bdd_2 mkdir -p 大括号被引号包裹不展开]**——主 Agent 已标记 REVIEWED，复核结论：**成立**。

1. `test_bdd_2`（`agate/tests/unit/agate-debt-check.bats:37`）已改为显式参数 `mkdir -p "$dir/roadmap" "$dir/tasks" ... "$dir/debt"`——大括号不再被引号包裹，`ls | wc -l == 9` 断言可成立；实测 `$dir` 下建出 9 目录 ✓。
2. `test_bdd_3` SETUP 断言（`:47`）由 `grep 'debt/'` 改为 `grep 'debt'`——SETUP.md:114 只含 `{...,debt}`（无 `debt/` 路径写法），原断言过严会误红；改后与 UPGRADING `debt/tech-debt.md` 断言（`:45`）+ 无 `agents/tech-debt`（`:49`）共同构成 BDD-3 完整判据 ✓。
3. R5.1-3 fixture 补 `debt_check: none`（`agate/tests/regression/v060-p8-cached.bats:10/29/49`）——SCOPE+ #1 同步面延伸，实测 R5 三用例全绿 ✓。

该 DESIGN_GAP 属测试代码缺陷（引号包裹大括号），非协议实现缺陷，修复方向正确且已在 fixture 落地，无残留风险。P4-implementation-core.md:58-59 的声明与实际修复一致。

---

## 检查清单

- [x] 数据安全与正确性（Pass 1）：schema 校验器/薄壳 fail-closed/closed 准入/id 唯一/解析安全——实测通过（§1.1-1.2）
- [x] 回退比对正确性：git log 提取 + source:retreat 覆盖比对 + 文件不存在 WARNING——实测通过（§1.2）
- [x] P8 debt_check 留痕：缺失 exit 1、内容不检、既有 P8 行为未误伤——实测通过（§1.3）
- [x] 归类修正同步：WORKFLOW 目录图/三处 mkdir/UPGRADING/TAG0003 修订注——grep 全 worktree 无遗漏（§1.4）
- [x] 代码健康（Pass 2）：shellcheck 0 / set -euo pipefail / Python 错误处理 / 契约一致（§2）
- [x] 行为不变回归：全量 676 绿 + consistency 0 ERROR + count 基线吻合（§3）
- [x] DESIGN_GAP 审查：REVIEWED 决策成立，fixture 修复已在案（§4）

## 锚点索引（结论引用）

- agate/scripts/agate-debt-check.py:81-83（必填）、85-88（枚举）、98-104（非空 list）、111-118（closed 准入）、179-181（id 唯一）、39（块正则）、153-157（读取兜底）
- agate/scripts/check-debt.sh:54（无文件 no-op）、59-62（set +e + PY_EXIT）、64-69（崩溃 fail-closed）、72-78（ERRORS 拦截）、21-50（回退覆盖比对）
- agate/scripts/check-gate.sh:425-430（P8 debt_check 检查）
- agate/assets/templates/tech-debt-template.md:9-15（判据三分法 + 不登记出口 + 不豁免硬规则）
- agate/WORKFLOW.md:79/84/85（目录规范）、agate/SETUP.md:114、agate/orchestrator-template.md:102、agate/state-machine.md:40（mkdir 9 集）
- agate/UPGRADING.md:92-105（v0.43.0 节）
- agate/assets/review-roles/plan-eng-review.md:19（标准 DEBT 格式）
- agate/tests/unit/agate-debt-check.bats:37/47（DESIGN_GAP 修复）、agate/tests/regression/v060-p8-cached.bats:10/29/49（R5 fixture）

## 环境标记

- `[PROD_NOT_TOUCHED]`——评审过程仅只读 + /tmp 与 bats 临时目录验证，未写入生产环境、未修改任何实现文件、未改动 `~/.agate`。
