---
phase: P2
task_id: TAG0013-script-consistency
type: design
parent: P1-requirements.md
trace_id: TAG0013-P2-20260816
status: draft
created: 2026-08-16
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 6
packages: [agate-scripts, agate-tests, agate-protocol-docs, agate-consistency]
domains: [backend, cli]
ui_affected: false
---

# P2 方案设计 — agate 脚本一致性批（RM-AG0015 / RM-AG0017 / RM-AG0018 剩余）

> 上游：P1-requirements.md（approved，11 条 BDD）+ P1-review.md（approved，§4 注 1/2 待本阶段措辞修正）。
> 范围锁定：只覆盖三条子需求；不改 P1 / 不改代码 / 不 commit。方案须覆盖全部 11 条 BDD。

---

## 1. 影响域分析

### 改什么（3 个脚本 + 3 个测试文件 + PROTOCOL_DIRS 声明）

| 文件 | 改动点 |
|------|--------|
| `agate/scripts/check-protocol-consistency.py` | 新增 CHECK 10（`check_script_name_refs` 函数 + `SCRIPT_REF_RE` + 扫描面/豁免清单常量）；`PROTOCOL_DIRS` 从 `("agate/assets/",)` 扩展为 `("agate/assets/", "agate/phase-cards/", "agate/rules/")`；`CHECKS` 列表追加 `("CHECK 10 ...", check_script_name_refs)` |
| `agate/scripts/commit-msg-self-gate.py` | `_SELF_GATE_RE` 追加 `|README\.md|AGENTS\.md` 分支（L38-40）；stderr 提示文案同步补 README.md/AGENTS.md（L77） |
| `agate/scripts/check-retrospective.py` | `if warnings:` 块内追加 DEBT/roadmap 登记提醒行（L93 后） |
| `agate/tests/unit/test_check_protocol_consistency.py` | 新增 CHECK 10 相关用例（漂移 ERROR / 豁免 / 扫描面边界 / PROTOCOL_DIRS） |
| `agate/tests/unit/test_commit_msg_self_gate.py` | 新增 ≥3 用例（README 触发 / AGENTS 触发 / CHANGELOG 豁免） |
| `agate/tests/unit/test_check_retrospective.py` | 新增 2 用例（有异常 → DEBT+roadmap 提醒；无异常 → 空输出不回归） |

### 不改什么（明确边界）

- **REF_RE（CHECK 2 死链检查）不动**：REF_RE 与 CHECK 10 语义互补不重叠（P1 §2 已识别），保持各自独立。
- **CHECK 3/4/6/7/8/9 不动**：CHECK 9 锚点表不加 CHECK 10 锚点（CHECK 10 无脚本实现逻辑，不进 `SCRIPT_ALIGNMENT_ANCHORS`；P4 若拆独立脚本才需走 CHECK 9 反向覆盖——本设计不拆，见 §2）。
- **NARRATIVE_DIRS 不重组**：保持 `("docs/plans/", "docs/reviews/", "docs/design-notes/", "docs/tasks/", "archived/", "agate-workspace/tasks/", "CHANGELOG.md")` 现状（见 §9 决策记录）。
- **docs/ 与 agate-workspace/ 不纳入 CHECK 10 扫描面**：P1 §4 已定（非协议文件），保持。
- **check-retrospective.py 的 exit 0 / warnings 收集逻辑不动**：只加一行提醒。

### 风险在哪

1. **CHECK 10 误报**（增量性破坏）：方案依赖 5 类豁免 + 叙事降级 + 扫描面精确枚举。已实测当前 0 漂移（见 §6 最小验证），豁免清单按 P1 §4.4 锁定。
2. **PROTOCOL_DIRS 扩展激活 CHECK 3 严格面 + CHECK 10 扫描面**：phase-cards/rules 本就不在 NARRATIVE_DIRS（非叙事），CHECK 2（`check_internal_refs`）对其**本就 ERROR 级**，扩展前后行为不变；本次变更真正激活的是 **CHECK 3**（`check_line_refs` 只扫 `is_protocol_file`，对 phase-cards/rules 新严格扫 `.md L\d+`）与 **CHECK 10** 新扫描面——实测 phase-cards/rules **0 处** `.md L\d+` 引用、`scripts/` 前缀引用 3 处均真实存在 → 无新增 ERROR（BDD-4）。
3. **self-gate 误触发/漏触发**：正则改动是纯锚定扩展，精确名锚定天然豁免 CHANGELOG；既有 4 用例覆盖 `agate/scripts/*` 与 `agate/*.md`，锚定扩展不改变这些分支的匹配（`^` 锚定根级名，`agate/...` 分支互斥）。
4. **RT.1 空输出回归**：提醒行只写在 `if warnings:` 块内，无异常时 `warnings` 为空 → 不输出（既有 RT.1 断言锁定）。
5. **SELF-GATE 触发**：本任务改 3 个脚本 + 3 个测试 + 协议文档 → 提交时需 `self-gate-review:` 路径（P0-brief known_risks）。

---

## 2. RM-AG0015：CHECK 10（协议文档面脚本名引用漂移 gate）

### 设计目标（P1 锁定，直接采用）

- 扫描面 = **协议文档面**：`PROTOCOL_FILES`（11 文件）+ `PROTOCOL_DIRS`（`agate/assets/` + 新增 `agate/phase-cards/` + `agate/rules/`）+ 根级 `README.md`/`AGENTS.md` + `agate/AGENTS.md` + `agate/CONTEXT.md` + `agate/UPGRADING.md` + `agate/scripts/README.md` + `CHANGELOG.md`（叙事降级）。**不含** docs/ 与 agate-workspace/。
- 引用形式 3 类：裸名 / `scripts/` 相对前缀 / `agate/scripts/`·`~/.agate/scripts/` 全路径。
- 豁免 5 类 + 叙事降级（见候选方案一细节）。
- 增量性：当前 0 漂移，落地后不产生新 ERROR。

### 候选方案

#### 候选方案 A（采纳）：CHECK 10 内联为 check-protocol-consistency.py 第 10 个 CHECK 函数

**结构**（与 CHECK 1-9 完全同构）：

1. **`SCRIPT_REF_RE`**（新增模块级常量，取自 P1 §4.4 计数正则，可复现 378/595）：
   ```python
   SCRIPT_REF_RE = re.compile(
       r"\b(check-[a-z0-9-]+\.(?:py|sh)|agate-[a-z0-9-]+\.(?:py|sh)|agate_[a-z0-9-]+\.(?:py|sh)|"
       r"install-hook\.(?:py|sh)|pre-commit-gate\.(?:py|sh)|commit-msg-self-gate\.(?:py|sh)|"
       r"pre-push-gate\.(?:py|sh)|count-tests\.sh|ci-gate-backstop\.py)\b"
   )
   ```
   - 注意：该正则是**已知脚本名形状白名单**（`check-*` / `agate-*`（连字符与下划线两形）/ hook / install-hook / count-tests / ci-gate-backstop）。**`agate_[a-z0-9-]+\.(?:py|sh)` 下划线形状覆盖 `agate_common.py`（非阻塞 1 修订）**——扫描面内 10 个文件引用该库（WORKFLOW / UPGRADING / scripts-README / CHANGELOG / handoff-template / platform-notes / LIMITATIONS / orchestrator-template / SETUP / AGENTS），旧白名单无下划线形状时这些引用不产生 token；若该库日后改名/退役将**全部漏检**（正是 RM-AG0015 要防的漂移）。**声明：库文件也在漂移检测范围内**（当前 0 漂移不受影响，agate_common.py 真实存在 → token 合法）。formatter 名（pytest.sh 等）天然不匹配 → 豁免②自动满足；`gate-result.sh` 等退役名也不匹配白名单，靠豁免⑤防未来改名。匹配到的 token 再对照 `agate/scripts/` 实际文件，命中即合法。
   - 全路径/前缀形式自动覆盖：`agate/scripts/check-gate.py` 中 `\b` 边界使 `check-gate.py` 独立成 token 被捕获，无需拆前缀。

2. **扫描面常量**：新增 `SCRIPT_REF_SCAN_FILES`（显式文件集）与 `SCRIPT_REF_SCAN_DIRS`（目录集）：
   ```python
   SCRIPT_REF_SCAN_FILES = PROTOCOL_FILES | {
       "AGENTS.md", "agate/AGENTS.md", "agate/CONTEXT.md",
       "agate/UPGRADING.md", "agate/scripts/README.md",
   }
   SCRIPT_REF_SCAN_DIRS = PROTOCOL_DIRS          # 复用扩展后的 ("agate/assets/", "agate/phase-cards/", "agate/rules/")
   ```
   - CHANGELOG.md 单独加入（叙事降级，见下）。
   - 遍历方式：`SCRIPT_REF_SCAN_FILES` 逐个读（`root / relpath`），`SCRIPT_REF_SCAN_DIRS` 用 `rglob("*.md")`；`rel()` 统一正斜杠。

3. **`check_script_name_refs(root, rep)`** 函数：
   - 对扫描面内每个文件逐行 `SCRIPT_REF_RE.finditer`；token 命中后解析：
     a. token ∈ `agate/scripts/` 实际文件名 → 合法，跳过；
     b. token == `count-tests.sh` → 校验 `agate/tests/scripts/count-tests.sh` 存在（豁免④，同名不同目录场景）；
     c. token ∈ 3 hook 薄壳（`pre-commit-gate.sh`/`commit-msg-self-gate.sh`/`pre-push-gate.sh`）→ 豁免③（防未来薄壳改型）；
     d. token ∈ formatters 目录名（`agate/assets/formatters/` 下实际文件名）→ 豁免②（真实存在于 assets/ 不在 scripts/）。**⚠️ forward-defense（防未来白名单放宽），当前不可达**：formatters 实际文件名（pytest.sh / go-test.sh / vitest.sh / generic-*.sh）与 README 示例名 `my-runner.sh` **均不匹配** SCRIPT_REF_RE 白名单形状（无 check-/agate-* /hook 前缀）→ 永不产生 token → 本分支当前不可达（BDD-3 ②天然成立）。保留此目录比对作**前向防御**；`my-runner.sh` 因不匹配白名单**天然豁免**，不显式加入豁免集合。P3 不应为不可达分支写测试。
     e. 文件 == `agate/UPGRADING.md` → 整文件跳过（豁免①，先于行级扫描判断）；
     f. 文件 == `agate/scripts/README.md` 且 token ∈ {`gate-result.sh`, `agate-workspace-resolve.sh`, `check-windows-smoke.sh`} → 豁免⑤（退役名）。
   - 未命中豁免 → 漂移：`rep.error("CHECK10-scriptref", ...)`（loc=`relpath:lineno`）。若文件是叙事文件（`is_narrative_file` 命中，当前仅 CHANGELOG.md 在扫描面内）→ **聚合为单条 WARNING**（同一文件合并报告一次，避免 CHANGELOG 155 处历史名刷屏，见 §9 决策记录 2）。
   - 零漂移 → `rep.ok("CHECK10-scriptref")`。

4. **`CHECKS` 列表追加 + main() 状态匹配修正（BLOCKER-1 修复，必改）**：
   - `CHECKS` 追加：`("CHECK 10 协议文档脚本名引用漂移", check_script_name_refs)`。
   - **main() CHECK 状态循环（L810-816）必须同步修正，否则 CHECK1/CHECK10 前缀碰撞**：现逻辑 `key = "CHECK" + title.split()[1]`（CHECK 1 → `key="CHECK1"`）+ `e["check"].startswith(key)`，而 CHECK 10 的 report id 为 `"CHECK10-scriptref"`，实测 `"CHECK10-scriptref".startswith("CHECK1")` 为 True → CHECK 10 一报 ERROR/WARNING，CHECK 1 状态行即被误标 ❌/⚠️（`CHECK 1  YAML 代码块可解析`）。**修订**：将状态匹配改为 `e["check"].split("-")[0] == key`（或等价 `e["check"].startswith(key + "-")`），两者对 CHECK1-yaml / CHECK10-scriptref / CHECK9-align 均正确，且不改变既有 CHECK 1-9 判定。**这是设计范围内的 main() 微调，随本次 commit 一起落**——不再声明「无需改 main()」。

**优点**：与 CHECK 1-9 同构，改动面最小；复用 Report/iter/rel/is_narrative_file 基础设施；`--json` 输出自动包含 CHECK 10；不需要动 CHECK 9 锚点表、dispatch-protocol、pre-commit-gate.py 的调用链。
**风险/权衡**：文件增大（+~60 行）；若未来脚本名形状超出白名单（新增非 check-*/agate-* 前缀脚本），该脚本名不会被检测——接受（与 P1 §4.4 计数口径一致，新脚本必然形如 check-*/agate-*，白名单可随新脚本前缀扩展）。

#### 候选方案 B（否决）：拆独立脚本 `check-script-refs.py`

将 CHECK 10 逻辑抽成独立 `agate/scripts/check-script-refs.py`，由 `check-protocol-consistency.py` 在 run_all_checks 中 subprocess 调用（或并入 pre-commit-gate 调度）。

**优点**：check-protocol-consistency.py 体积不膨胀；单文件单职责。
**风险/权衡**：
- 新脚本是 `check-*.py` → 命中 CHECK 9 反向覆盖（`check_anchor_coverage`）→ 必须加进 `SCRIPT_ALIGNMENT_ANCHORS`（P1 §2 隐含项）→ 锚点表 +~1 条，且需 dispatch-protocol.md / 文档面新增引用（本身又成为 CHECK 10 的扫描对象，循环引用）；
- subprocess 调用引入进程边界，退出码/JSON 聚合要额外处理；
- 独立脚本自身也会被文档面引用 → 新增引用源，增加 0 漂移维护面；
- 与 CHECK 1-9 的「一个文件跑全部一致性」心智模型不一致。
**选择理由**：改动面显著大于方案 A，收益仅「体积不膨胀」（非问题）。P1 SUGGEST 已倾向方案 A，方案 B 无相对优势 → **否决**。

### BDD 覆盖

- BDD-1（0 漂移通过）：实测协议文档面当前 0 漂移 → CHECK 10 PASS + 整体 0 ERROR。✓
- BDD-2（引用不存在脚本 → ERROR）：phase-cards 等协议文件含 `check-nonexistent-script.py` → 白名单命中 + 未豁免 → `rep.error` + exit 1，loc 含文件名:行号。✓
- BDD-3（豁免 5 类）：①UPGRADING 整文件 ②formatters 名（含 my-runner.sh 示例名）③3 hook 薄壳 ④count-tests.sh（tests/scripts 落点）⑤scripts/README 退役名 3 个。✓
- BDD-4（phase-cards/rules 入 PROTOCOL_DIRS）：`PROTOCOL_DIRS` 扩展；实测无 `.md L\d+`、scripts/ 前缀引用均存在 → 不新增 ERROR。**影响面精确表述（非阻塞 3）**：CHECK 2 对 phase-cards/rules 本就严格（非叙事，扩展前后行为不变）；本次变更真正激活的是 CHECK 3 严格面（`.md L\d+`）+ CHECK 10 扫描面。✓
- BDD-5（叙事文件至多 WARNING；docs/ 非扫描面无输出）：CHANGELOG（NARRATIVE_DIRS 覆盖集）聚合 WARNING 不 ERROR；docs/superpowers 等不在扫描面 → 无输出。✓

### 测试策略（评审 §3 缺口 7/8 纳入，供 P3 执行）

- **BDD-1/4 夹具选型（缺口 7）——推荐 (a) 测试内构造最小假协议树**：在 pytest `tmp_path` 下建 `agate/scripts/`（含 `check-gate.py` / `agate_common.py` / `count-tests.sh` 等假文件）+ 协议 md（`agate/WORKFLOW.md` 含 `check-gate.py` 合法引用、`agate/phase-cards/` 含 `check-nonexistent-script.py` 漂移引用），直接调 `check_script_name_refs(root, rep)` 断言 `rep.errors` / `rep.ok`。隔离性好、不依赖真实 worktree、无 CHANGELOG 聚合 WARNING 干扰。不采用 (b) 真实 worktree 集成断言：会混入既有 277 条 WARNING 基线（CHANGELOG 聚合），断言口径复杂化（须写清「0 ERROR 而非 0 输出」）。P3 沿用 `test_check_protocol_consistency.py` 现有 `_load_cpc` importlib 加载模式，在内存假树对象上跑 CHECK 10。
- **BLOCKER-1 回归断言（缺口 8）**：新增用例断言「CHECK 10 报 ERROR/WARNING 时 CHECK 1 状态行独立」——复刻 main() 状态循环判定（对 `_load_cpc` 加载的 `CHECKS` 标题求 `key`，再对 `rep.errors`/`rep.warnings` 用修订后表达式 `e["check"].split("-")[0] == key` 判定）：
  - 场景 A：仅 `rep.error("CHECK10-scriptref", ...)` → CHECK 1 状态行仍 ✅（不被 CHECK10 污染）；CHECK 10 状态行 ❌。
  - 场景 B：仅 `rep.warning("CHECK10-scriptref", ...)` → CHECK 1 仍 ✅；CHECK 10 ⚠️。
  - 同时断言旧逻辑 `startswith(key)` 在该场景会把 CHECK 1 误标（显式锁定回归根因）。

---

## 3. RM-AG0017：`_SELF_GATE_RE` 扩展

### 候选方案

#### 候选方案 A（采纳）：根级精确名锚定

```python
_SELF_GATE_RE = re.compile(
    r"^(agate/scripts/.*\.(sh|py)|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md|README\.md|AGENTS\.md)$"
)
```

- `^...|README\.md|AGENTS\.md` 锚定**仓库根级精确名**；CHANGELOG.md 天然不在其列（无需额外排除逻辑）。
- 既有分支（`agate/scripts/.*` / `agate/*.md` / `agate/*/*.md` / `SELF-GATE.md`）保持不变 → 既有 4 用例不回归。
- stderr 提示文案（L76-77）同步从 `（agate/scripts/*.sh / agate/scripts/*.py / agate/*.md / SELF-GATE.md）` 补上 `README.md / AGENTS.md`，保证提示与触发面一致。

**优点**：改动最小（1 行正则 + 1 行文案）；精确匹配零误报；符合 P1 §2「CHANGELOG 天然豁免」建议。
**风险/权衡**：未来若新增根级协议文档（如 CONTRIBUTING.md）需手动扩正则——当前无此需求，YAGNI（P1 §5 表只列 README/AGENTS）。

#### 候选方案 B（否决）：宽松 glob + 显式排除 CHANGELOG

如 `^(...|SELF-GATE\.md|[A-Za-z0-9_-]+\.md)$` 匹配根级任意 md，再显式 `if path == "CHANGELOG.md": continue`。

**优点**：未来新根级协议文档自动覆盖。
**风险/权衡**：实测该模式会把 `NOTICES.md`（LICENSE 致谢文档，非协议面）也判为触发文件 → 误触发 self-gate WARNING；排除逻辑需在匹配循环里加条件分支，可读性下降；与「触发面 = 协议文档」的语义不符。
**选择理由**：方案 B 引入误报 + 额外排除逻辑，而方案 A 精确满足 P1 要求且零风险 → **否决**。

### BDD 覆盖

- BDD-6（README.md 触发）：正则命中 → WARNING，exit 0。✓
- BDD-7（AGENTS.md 触发）：同上。✓
- BDD-8（CHANGELOG.md 不触发）：精确名锚定不含 CHANGELOG → 无输出。✓
- BDD-9（既有 4 用例不回归）：既有分支未动。✓

---

## 4. RM-AG0018 剩余：check-retrospective.py 登记提醒行

### 候选方案

#### 候选方案 A（采纳）：`if warnings:` 块内追加独立提醒行

```python
if warnings:
    sys.stderr.write("GATE RETRO: 建议复盘 — 检测到异常模式：\n")
    for w in warnings:
        sys.stderr.write(f"  - {w}\n")
    sys.stderr.write("  请在版本 bump 前写简版复盘（docs/releases/v{version}-retrospective.md）\n")
    sys.stderr.write("  复盘发现的新缺口请登记 DEBT/roadmap（技术债清单 / 路线图）\n")
```

- 仅在 `warnings` 非空时输出 → RT.1 空输出约束不破（BDD-11）。
- 提醒行同时含 **DEBT** 与 **roadmap** 两词 → BDD-10 断言可定位。
- exit 0 不变（L95）。

**优点**：独立行、职责清晰；不改变既有文案（既有测试断言 `重试超限`/`override`/`SCOPE+` 子串不受影响）。
**风险/权衡**：多一行 stderr（仅异常场景）——可接受。

#### 候选方案 B（否决）：改写既有「请在版本 bump 前写简版复盘」行为 DEBT/roadmap 合并行

如改成 `  请在版本 bump 前写简版复盘（...）并把新缺口登记到 DEBT/roadmap\n`。

**优点**：少一行输出。
**风险/权衡**：把「写复盘」与「登记缺口」两个动作混在一行，语义变糊；若既有测试断言该行原文（当前无）则回归风险；DEBT/roadmap 两词同现于一句中仍可断言但脆弱。
**选择理由**：方案 A 独立行更清晰、零回归风险 → **否决**。

### BDD 覆盖

- BDD-10（有异常 → DEBT+roadmap 提醒，exit 0）：重试超限/SCOPE+/override 任一触发 warnings → 提醒行输出。✓
- BDD-11（无异常 → 空输出 + exit 0）：提醒行在 `if warnings:` 内 → 无异常不输出，既有 RT.1 用例锁定。✓

---

## 5. gate_commands（P2 固化）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/ -q --tb=short"
  P5: "python3 -m pytest agate/tests/ -q --tb=no"
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py"
  P5_count: "bash agate/tests/scripts/count-tests.sh"
```

- **P5_consistency 不用 `--strict`**：当前基线已有 277 条 WARNING（agate-workspace/tasks 叙事引用等，`--strict` exit 2），CI（protocol-tests.yml L122）也是非 strict——gate 判据为 **0 ERROR**。
- P5_count：测试用例计数防漂移。**基线 = 751（以 count-tests.sh 输出为准，实测「总计：751 个测试用例」）**；新增用例后数字须 **≥ 751** 且保持同一口径（count-tests.sh collect-only 口径）。不采用 749 交接值（P0 时点值，已过时）。
- ui_affected=false → 无 P5_e2e。

---

## 6. files_to_read（P4 implementer 资源地图）

```yaml
files_to_read:
  - path: agate/scripts/check-protocol-consistency.py
    why: 主改动对象。重点 L52-65（PROTOCOL_FILES/PROTOCOL_DIRS）、L74（NARRATIVE_DIRS）、L238（REF_RE，参照其语法写 SCRIPT_REF_RE）、L765-782（CHECKS + run_all_checks）、L810-816（main() CHECK 状态循环——本次改状态匹配，BLOCKER-1）、L11-18（模块 docstring——补 CHECK 10 行，非阻塞 5）、L100-151（Report/iter_md_files/rel/is_narrative_file 复用）
  - path: agate/scripts/commit-msg-self-gate.py
    why: _SELF_GATE_RE（L38-40）扩展 + stderr 文案（L76-77）同步
  - path: agate/scripts/check-retrospective.py
    why: warnings 输出块（L89-93）追加提醒行
  - path: agate/tests/unit/test_check_protocol_consistency.py
    why: 现有用例模式（_load_cpc importlib 加载模块）；在其上追加 CHECK 10 用例
  - path: agate/tests/unit/test_commit_msg_self_gate.py
    why: git_repo fixture + _run_csg helper 模式；追加 README/AGENTS/CHANGELOG 3 用例
  - path: agate/tests/unit/test_check_retrospective.py
    why: task_dir fixture + _run_retro 模式；追加提醒行 2 用例
  - path: agate/tests/conftest.py
    why: git_repo / task_dir / run_cli / bash / python_exe fixture 定义（新用例直接用，无需自建）
```

## 7. env_constraints（确认 P0-brief）

```yaml
env_constraints:
  debug_env: "本环境为 Linux；Windows 靠 CI matrix（pytest -m windows_smoke）。三处改动均为纯 Python + 文件系统/git 调用，无 Unix 假设，Windows CI 冒烟可跑。"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py（0 ERROR）；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0013-script-consistency/"
  isolation_check: "测试全部用 pytest tmp_path fixture（conftest create_task_dir）与独立 git_repo，不触碰真实仓库；验证方式 = 全量 pytest 绿 + count-tests.sh 通过 + consistency 0 ERROR"
  self_gate: "本任务改脚本+测试+协议文档，commit 需 self-gate-review: 路径（SELF-GATE.md）"
```

## 8. minimal_validation

```yaml
minimal_validation:
  assumption: "CHECK 10 扫描面 + 5 类豁免下协议文档面当前 0 漂移；PROTOCOL_DIRS 扩展不新增 CHECK 2/3 ERROR；_SELF_GATE_RE 精确名锚定零误报"
  method: "纯代码逻辑，无外部系统依赖。依赖内部函数/数据转换：SCRIPT_REF_RE（取自 P1 §4.4 计数正则）、agate/scripts/ 与 agate/assets/formatters/ 与 agate/tests/scripts/ 目录枚举、is_narrative_file（NARRATIVE_DIRS startswith）、git diff --cached --name-only（commit-msg 侧）。验证方式为在 worktree 用 python 脚本复现 CHECK 10 扫描逻辑 + 正则候选表比对，不依赖浏览器/外部服务。"
  result: "confirmed"
  note: |
    实测（worktree 内 python 模拟）：
    1. 扫描面（PROTOCOL_FILES + EXTRA + 扩展后 dirs + CHANGELOG）用 SCRIPT_REF_RE 提取 → 非 CHANGELOG 漂移 = 0（增量性成立）；CHANGELOG 155 处历史 .sh 名漂移（降级 WARNING，聚合防刷屏）。
    2. phase-cards/rules 无 `.md L\d+` 引用（grep 0 命中）、`scripts/` 前缀引用 3 处均真实存在 → PROTOCOL_DIRS 扩展安全。
    3. _SELF_GATE_RE 候选比对：精确名锚定 A 命中 README.md/AGENTS.md、豁免 CHANGELOG.md、不命中 NOTICES.md/README.zh-CN.md/docs/agate-workspace；宽松 glob B 误命中 NOTICES.md → 选 A。
    4. 当前基线：consistency 0 ERROR / 277 WARNING（--strict exit 2，故 gate 用非 strict）；count-tests.sh = 751。
```

## 9. design 决策记录

1. **CHECK 10 留内联（候选 A），不拆独立脚本**：改动最小、复用现有 CHECKS 机制、无 CHECK 9 锚点循环引用。否决理由见 §2。
2. **CHANGELOG（叙事文件）漂移聚合为单条 WARNING，不逐条报**：P0-brief 提到「按文件性质分严格/宽松（debt/进行中 task 应严格）」——评估结论：CHANGELOG 的 155 处历史 .sh 名是**既有事实**（v0.46.0 前的迁移史），逐条 WARNING 会刷屏且对"未来新增引用"无拦截价值；未来协议面新增的裸名引用由 ERROR 级兜底（扫描面含 phase-cards/rules/assets）。聚合 1 条 WARNING 保留可见性、零噪音。**NARRATIVE_DIRS 不重组、不读 .state.yaml 区分进行中/已完成**（实现复杂度高、收益低——进行中 task 在 agate-workspace/ 非协议面，本就不在 CHECK 10 扫描范围，其漂移由协议面 ERROR 兜底）。记入本决策，不扩范围。
3. **PROTOCOL_DIRS 扩展为 3 目录**（assets + phase-cards + rules）：phase-cards/rules 是主 Agent 每轮必读的协议文件，其脚本名裸引用必须 ERROR 级（RM-AG0015 修复方向 ②）。实测无新增 CHECK 2/3 ERROR。
4. **count-tests.sh 豁免走「同名不同目录」落点解析**：白名单正则命中 `count-tests.sh`，解析时校验 `agate/tests/scripts/count-tests.sh`（不校验 `agate/scripts/` 下）——避免把真实存在的测试脚本误报为漂移（P1 §2「同名不同目录」场景）。
5. **提示文案同步**：self-gate 触发面的 stderr 文案与正则同改，避免「提示说 A、实际匹配 B」的文档-行为漂移。
6. **main() CHECK 状态匹配修正（BLOCKER-1）**：CHECK 10 加入后 `startswith(key)` 有 CHECK1/CHECK10 前缀碰撞 → 状态匹配改为 `e["check"].split("-")[0] == key`（或等价 `startswith(key + "-")`）。属本次设计范围内的 main() 微调，随本次 commit 一起落；同时补模块 docstring 的 CHECK 10 行（非阻塞 5）。

## 10. 评审非阻塞观察处理（P1-review §4）

1. **注 1（my-runner.sh 描述不精确）**：P1-requirements.md BDD-3 ②将 my-runner.sh 描述为「真实存在于 assets/ 不在 scripts/」，实测 `agate/assets/formatters/` 无 my-runner.sh 实体文件，仅作示例名出现在 `formatters/README.md` L108。**处理（随非阻塞 2 修订）**：my-runner.sh 与 formatters 实际文件名**不匹配 SCRIPT_REF_RE 白名单形状 → 天然豁免**，不显式加入豁免集合；保留 formatters 目录比对作**前向防御**（防未来白名单放宽，见 §2 步骤 3.d 的 forward-defense 标注）。不修改 P1-requirements.md（需主 Agent 批准），措辞修正落在本设计 + P3 测试命名。
2. **注 2（§4.4「PROTOCOL_FILES 11 + CONTEXT」括号笔误）**：计数时根 README 已剔出归 README/AGENTS 桶，实际为 10 agate 协议文件 + CONTEXT = 104。**处理**：本设计 §2 扫描面沿用「PROTOCOL_FILES（11 文件）作为常量集 + 追加文件」的**实现口径**（11 = 常量真实元素数，与计数桶无关），并在 P3 用例/文档中避免重述「11 + CONTEXT = 104」句式。
3. **注 3（UPGRADING 整文件豁免已定）**：按整文件实现，无歧义。✓

## 11. 实现完成标志（P3/P5 验收对照）

1. `check-protocol-consistency.py`：`SCRIPT_REF_RE`（含 `agate_[a-z0-9-]+\.(?:py|sh)` 下划线形状） + `SCRIPT_REF_SCAN_FILES/DIRS` + `check_script_name_refs` + `CHECKS` 追加 CHECK 10；**main() CHECK 状态循环改用 `e["check"].split("-")[0] == key`（或 `startswith(key + "-")`）判定（BLOCKER-1 修复）**；**模块 docstring（L11-18）补一行「CHECK 10  协议文档脚本名引用漂移」（非阻塞 5，随 BLOCKER-1 main() 改动一起落）**；`PROTOCOL_DIRS` 含 phase-cards/rules；运行 `python3 agate/scripts/check-protocol-consistency.py` → CHECK 10 显示 ✅ PASS 且 **0 ERROR**。
2. `commit-msg-self-gate.py`：`_SELF_GATE_RE` 含 `README\.md|AGENTS\.md`，stderr 文案同步。
3. `check-retrospective.py`：warnings 存在时输出含「DEBT」「roadmap」的提醒行；无 warnings 时输出为空。
4. 测试：三个测试文件新增用例全绿；既有用例不回归；全量 `python3 -m pytest agate/tests/` 绿；`count-tests.sh` 数字 ≥ 当前且口径说明更新。
5. ruff / shellcheck 通过（py 变更 ruff，hook 薄壳未动则 shellcheck 无新增）。
