---
phase: P2
task_id: TAG0024
type: design
parent: P1-requirements.md
trace_id: TAG0024-P2-20260825
status: draft
created: 2026-08-25
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 2
packages: [agate-scripts, agate-rules, agate-docs, agate-tests]
domains: [backend]
ui_affected: false
# ── v2.0 派发编排字段（可选，TAG0014）──
dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: md-field-set-tool, complexity: medium}, {id: check-gate-debt-fixes, complexity: low}, {id: phases-yaml-consistency, complexity: low}]}
---

> 范围重述：本设计覆盖 P1-requirements.md 全部 29 条 BDD（RM-AG0048 一期 BDD-1~19、DEBT0019
> BDD-20~21、DEBT0020 BDD-22~24、RM-AG0049 BDD-25~26、RM-AG0050 BDD-27~28、跨 issue 约束
> BDD-29）。三个 dispatch_plan 批次彼此文件零交叉（见下节改什么——RM-AG0049 相关用例
> 统一落在 `test_check_structure_consistency.py`，不再分散到 `test_check_gate.py`），
> 可并行派发 P4。

## 1. 影响面梳理（改什么 / 不改什么 / 风险在哪）

### 1.1 改什么（逐文件/逐函数落点 + 关联 BDD）

| 文件 | 改动点 | 关联 BDD |
|---|---|---|
| **新增** `agate/scripts/agate-md-field-set.py` | 新建 CLI：`<op> <value>` / `--list` / `<op> --help`；FILE 环境变量传路径（与 get 工具同惯例）；key 白名单 = phases.yaml 全部 task_fields 并集 ∪ task-files.md 通用 Header；value 校验分派见 §3.2；原子写（tempfile.mkstemp 同目录 + os.replace）；证据字段/追加字段拒绝 | BDD-1~6, 9~19 |
| **新增** `agate/scripts/agate-md-field-set-gate-commands.py` | gate_commands 正文 YAML 块专用写入：解析候选块 → key 合法性校验（`agate_common.is_legal_gate_key` + `known_phase_ids`）→ 整块替换正文 `gate_commands:` 块（复用 `agate_common.parse_gate_commands_block` 的块边界正则语义做替换与自校验） | BDD-7, 8 |
| `agate/scripts/check-gate.py` `_check_roadmap_done()`（现第 1181-1202 行） | 新增列数精确匹配校验：`len(cols) != _ROADMAP_EXPECTED_COLS`（=9）时 `continue`，替换现有 `len(cols) < 8` 的宽松判据 | BDD-20, 21 |
| `agate/scripts/check-gate.py` `gate_p8()` 内 `roadmap_path` 构造（现第 1223-1224 行） | 改为 `_git(["rev-parse", "--show-toplevel"])` 解析仓库根后拼接；解析失败（非 git 环境）时 stderr 输出区分性提示，不静默构造错误路径 | BDD-22, 23, 24 |
| `agate/rules/phases.yaml` `id: P4` 的 `outputs`（现第 57-66 行） | 追加一行 `{file: P4-review.md, required: true, status_field: status}` | BDD-25, 26 |
| `agate/rules/phases.yaml` `id: P6.5` 块（现第 88-97 行） | 追加纯注释（`#`），措辞对齐 state-machine.md「挂载于 P6→P7 转移的强门槛子阶段，非独立 phase 值」；**不改字段结构**（`id/outputs/gates/task_fields` 原样保留，脚本消费点不变） | BDD-27, 28 |
| `agate/assets/templates/dispatch-prompt.md`（现第 62-74 行） | 「文件必须以这段 Header 开头（直接复制）」+ 可复制的裸 frontmatter 代码块 → 改为「产出文件字段：用 `agate-md-field-set` 填写」一行式指令；不再展示可被字面复制的围栏示例（去除 P1-gate-diagnosis 的污染源） | BDD-19 |
| `agate/assets/templates/dispatch-context.md` | `### 输入文件` 节后追加固定一行：用 set 填写字段的指引 + "set 失败报告主 Agent，不手改文件" | BDD-19 |
| **新增测试** `agate/tests/unit/test_agate_md_field_set.py` | 覆盖 BDD-1~19（含零协议知识模拟场景 BDD-16、原子写模拟中断 BDD-10） | BDD-1~19 |
| `agate/tests/unit/test_check_gate.py` 追加用例 | DEBT0019 列数精确匹配红/绿用例、DEBT0020 非仓库根 CWD 用例 | BDD-20~24 |
| `agate/tests/unit/test_check_structure_consistency.py`（若存在，否则于既有 S-3 测试文件追加） | phases.yaml P4 outputs 声明存在性用例（BDD-25）+ 核对 P4 outputs 追加后 S-1/S-2/S-3 均 0 mismatch（回归用例，非新增检查逻辑，BDD-26）；RM-AG0049 全部用例落地于本文件，不再分散到 test_check_gate.py（避免与 check-gate-debt-fixes 批次同文件交叉） | BDD-25~26 |

### 1.2 不改什么（显式排除 + 理由）

- **不改 `agate-md-field-get.py`**：BDD-15 的同源要求指向"set 复用 gate 的校验逻辑"，不要求 get/set 互相修改；get 的 `KNOWN_OPS`/字段分类作为**只读依赖**被 set 动态加载引用（见 §3.2），物理文件零改动。
- **不改 `agate-frontmatter-check.py`**：候选方案 A（见 §2）选择动态 `importlib` 加载复用其 `SCHEMAS`/`_check()`，不重写、不迁移、不扩展其 `SCHEMAS` 覆盖范围。若未来需要覆盖 review 类文件的 `status` 枚举，这是独立的后续 DEBT，本任务不动它（避免这个被全仓 pre-commit 依赖的校验器承担超出 P1 锁定范围的改动风险）。
- **不改 `check-judge-verdict.py`**：P6.5-judge-verdict.md 的 `status` 枚举（`_VALID_STATUS`）同样只读引用（importlib 动态取值），不修改该文件；BDD-28 明确要求 judge 判定行为不变。
- **不改 `check-events.py` / gate-events 账本格式**：design note §6.4/§8 已锁定"账本留痕是二期"，一期 set 不产生任何账本写入，BDD-29 覆盖。
- **不改 `check-retrospective.py`**：P1 同类扫描线索 2 已确认该文件用正则匹配、非列索引解析，不受 DEBT0019 缺陷机制影响。
- **不改 `check-protocol-consistency.py` 的判定逻辑**：只作为本次改动的**回归 gate**（P5_consistency key）跑一遍确认无新增不一致，不修改其规则本体。
- **不改 phases.yaml 之外任何阶段的 `id`/`outputs`/`gates`/`retry_cap` 结构**（P4 只追加一行 outputs，P6.5 只追加注释）——不触碰 P1/P2/P3/P5/P6/P7/P8 的既有声明，缩小 S-1~S-6 回归面。
- **不实现 get 工具尚未覆盖的字段类型语义**（`need_confirm_resolved`/`suggest_resolved`/`scope_resolved`/`mechanism_issues`/`execution_issues`/`dispatch_plan`）——BDD-18 已锁定一期明确拒绝，不做覆盖式写入以外的追加/嵌套语义。
- **不做 `.state.yaml` 的 set 化**：design note §8 二期评估项，一期不动状态机文件。
- **不给 gate_commands 专用命令做逐 key 增量写**：design note §5.1.1 已锁定块级整体替换，不实现 diff/patch 语义。

### 1.3 风险在哪（每条配缓解措施）

1. **风险：SCHEMAS 覆盖不全导致部分字段"有白名单资格但无真实校验"**——`agate-frontmatter-check.SCHEMAS` 只覆盖 P1-requirements/P2-design/P6-acceptance/P7-consistency 四类文件的部分字段；`status`/`agent`（review 文件通用字段）与 P6.5 专属的 `criteria_total`/`criteria_passed`/`verdict_evidence` 三个字段在 phases.yaml task_fields ∪ task-files.md 通用 Header 的机械并集下**属于合法白名单 key，但在 SCHEMAS/get 工具的类型分类中都没有对应枚举/类型定义**（已逐个 grep 确认：SCHEMAS 四个 dict 均不含 `status`；get 工具 `KNOWN_OPS` 38 个 op 均不含 `criteria_total`/`criteria_passed`/`verdict_evidence`）。
   **缓解**：对这类"无既有 schema 覆盖"的字段，set 不发明新枚举校验规则，只做**最小类型强校验**（int 用 `int()` 强转失败即拒绝；list 用空格/换行切分），类型依据从消费脚本的**实际用法**读代码确认（`check-judge-verdict.py` 第 9-10 行文档已明确 `criteria_total`/`criteria_passed` 为整数、`verdict_evidence` 按 list 消费），并在代码注释标明来源行号，不凭空定义。`status` 按文件 basename 分派固定枚举表（见 §3.4），来源为 `task-files.md`（通用默认）∪ `dispatch-prompt.md`「Review 角色特别指令」（review 类文件补充值）∪ `check-judge-verdict._VALID_STATUS`（P6.5 专属，importlib 动态取值不手抄）——这是协议文档/既有代码的并集复用，不是 set 自建规则。
2. **风险：importlib 动态加载的模块身份/缓存问题**——若 `agate-md-field-set.py` 与 `agate-md-field-set-gate-commands.py` 各自独立 `spec_from_file_location` 加载同一份 `agate-frontmatter-check.py`，每次进程内只加载一次（各自是独立 CLI 进程，无跨进程状态共享问题），但同一进程内测试套件（pytest）反复 import 不同 op 时需避免重复 `exec_module` 的开销/副作用。
   **缓解**：仿 `check-routing.py` 现有实现（第 38-52 行 `_CACHE` 字典 + `_load_script()`），加载结果模块级缓存，同进程内只 `exec_module` 一次。
3. **风险：DEBT0019 列数常量硬编码（9）未来随 roadmap.md 表格 schema 演进而失效**——若未来 roadmap.md 增删列，`_ROADMAP_EXPECTED_COLS = 9` 需要同步改，且现有 `cols[1]/cols[3]/cols[5]` 索引早已隐含同样的耦合。
   **缓解**：不引入"动态探测表头列数"的额外复杂度（详见 §2.2 候选权衡），仅在新增常量旁写清晰注释说明来源（7 数据列 + split 产生的首尾两个空串 = 9），未来 schema 变更时两处（索引与列数）会同时因同一次代码评审被看到，不构成新增的隐藏耦合。
4. **风险：DEBT0020 修复依赖 git 可执行文件在 PATH 中**——`gate_p8()` 本就已通过 `_git()` 调用 git 做 version/changelog/tag 检查（现第 1240-1284 行），新增的 `rev-parse --show-toplevel` 与既有假设一致，不引入新依赖类型。
   **缓解**：无需额外测试环境准备；非 git 环境（`_git` 返回非 0）时明确输出区分性 stderr（BDD-23），不误判为"无 roadmap.md"。
5. **风险：phases.yaml P4 outputs 追加触发 S-3（YAML→cards 渲染一致）新增不一致**——S-3 逻辑（`check-structure-consistency.py` 第 223-229 行）要求 `outputs[].file` 的文件名字面出现在对应 `phase-cards/P4-implementation.md` 正文中。
   **缓解**：已用 `grep -n "P4-review" agate/phase-cards/P4-implementation.md` 核实该字符串已出现 10 次（现第 90-153 行），追加 outputs 声明后 S-3 检查天然通过，零改动 S-3 代码，风险已消解为"已验证不会触发"（见 §6 minimal_validation）。
6. **风险：候选值校验流程中"深拷贝 frontmatter dict 后调用 `_check()`"若沿用不当可能把无关字段的既有错误一并报出，误导 subagent 以为是本次 set 引入的新错误**。
   **缓解**：`_check()` 返回的错误列表按 `f"{basename}:{field}:"` 前缀过滤，只透传 **本次候选写入的 key** 相关错误行；其余既有字段错误（如果文件本来就有其他字段的历史错误）不在本次 set 调用的错误输出范围内，避免"set 一小步、报错一整页"的体验问题。
7. **风险：`status: approved` 角色白名单基于目录列表动态推导（`{agate_root}/assets/review-roles/*.md`），若目录后续增删文件，白名单随之变化**——这是**有意设计**（自动跟随协议演进、避免手抄清单漂移），但需要明确这不是安全边界（design note §7.1/§7.4 已声明）。
   **缓解**：P2 文档显式记录该依赖关系（见 §3.4），若目录路径解析失败（`resolve_rules_root`/`resolve_agate_root` 异常）→ fail-closed（默认不放行 `status: approved` 写入，只放行 `agent != main` 之外一律拒绝），不因目录读取失败而静默放宽权限。

## 2. 候选方案（≥2 + 权衡 + 选择理由）

> 本任务的核心架构决策集中在 RM-AG0048 的"同源复用路径"——这是唯一需要真实方案比较的问题
> （DEBT0019/20/RM-AG0049/50 均为局部修复，方案空间小，其内部的候选比较已在 §1.3 风险项与
> §3.6/§3.7 落地细节中给出并定案，不重复展开为顶层候选）。

### 候选方案 A（选定）：动态 importlib 复用现有校验器，零改动既有文件

**设计**：`agate-md-field-set.py` / `agate-md-field-set-gate-commands.py` 用与 `check-routing.py`
现有 `_load_script()`（第 41-52 行）**完全相同**的 `importlib.util.spec_from_file_location` 方式，
在运行时动态加载：
- `agate-frontmatter-check.py` → 取其模块级 `SCHEMAS` 字典与 `_check(basename, schema, data)` 纯函数，**逐字节复用**（不复制、不重写）；
- `agate-md-field-get.py` → 取 `BOOL_FIELDS`/`LIST_FIELDS`/`INT_FIELDS`/`STRING_FIELDS`/`NO_FALLBACK_*`/`JSON_FIELDS`/`KNOWN_OPS` 及 `_read_frontmatter`/`_get`/`_format_value`，保证 `--list` 显示的"当前值"与 `agate-md-field-get` 的真实读取结果逐字节一致；
- `check-judge-verdict.py` → 取 `_VALID_STATUS`（P6.5 专属 `status` 枚举）。

`agate_common.py` 的 `read_rules_yaml`/`resolve_rules_root`/`known_phase_ids`/`is_legal_gate_key`/
`split_frontmatter`/`parse_gate_commands_block` 走**普通 import**（无连字符问题，本就是共享库）。

- **数据流**：用户调用 → 读现有 frontmatter（`split_frontmatter`）→ 深拷贝 + 应用候选值 → 若目标文件 basename 命中 `SCHEMAS` → 调用动态加载的 `_check()` 校验 → 无错误 → `yaml.safe_dump` 生成新 frontmatter → 临时文件 + `os.replace` 原子落盘 → 报告剩余缺失（对比 phases.yaml 该阶段 task_fields）。
- **异常路径**：pyyaml 缺失（沿用 get/frontmatter-check 现有 `sys.exit(1)` 兜底一致）；`_load_script` 加载失败（源文件损坏/被删除）→ fail-closed，输出"内部依赖不可用，请联系维护者"并 exit 非 0，不猜测校验结果。
- **优点**：`SCHEMAS`/`_check()`/`KNOWN_OPS` 物理上仍只存在一份，未来任何一处修改（比如给 P2-design.md 加新枚举字段）**自动**对 set 生效，不需要在两处同步——真正消灭"set 说通过、gate 说不通过"的漂移根源。零改动三个既有稳定文件（`agate-frontmatter-check.py`/`agate-md-field-get.py`/`check-judge-verdict.py`），把本已因新脚本 + check-gate.py + phases.yaml + 模板触发 SELF-GATE 的改动面控制在最小。有现成的同代码库先例（`check-routing.py` 已验证可行，见 minimal_validation 的实测复现）。
- **风险**：动态加载增加一层间接性，调试时报错栈会经过 `importlib` 帧（可读性略降，但 `check-routing.py` 已在生产使用，非新增未知风险）；`_load_script` 需要模块级缓存避免重复 `exec_module`（已在 §1.3 风险 2 给出缓解）。
- **工作量**：新增 2 个脚本（预计各 150-250 行）+ 1 个测试文件，无需改动/回归任何既有 gate 脚本的正确性证明。

### 候选方案 B（陪衬但非稻草人）：把 SCHEMAS 与字段分类下沉到 `agate_common.py`，三方改走普通 import

**设计**：新增 `agate_common.py` 顶层常量 `FIELD_SCHEMAS`（=从 `agate-frontmatter-check.SCHEMAS` 搬迁）
与 `validate_frontmatter_fields()`（=从 `_check()` 搬迁），把 `agate-md-field-get.py` 的
`BOOL_FIELDS`/`LIST_FIELDS`/… 字段分类常量也一并搬迁为 `agate_common.py` 的
`FIELD_TYPE_CLASSES`。`agate-frontmatter-check.py`、`agate-md-field-get.py` 改为
`from agate_common import FIELD_SCHEMAS, validate_frontmatter_fields, FIELD_TYPE_CLASSES`（同 M2
迁移 `parse_gate_commands_block`/`known_phase_ids` 时的既定模式）；`agate-md-field-set.py` 同样普通
import，不再需要 `importlib`。

- **优点**：架构分层更"教科书"——`agate_common.py` 本就是本仓库指定的公共库角色（M2 已把
  `parse_gate_commands_block`/`known_phase_ids`/`is_legal_gate_key` 等迁移到此，本方案延续同一
  迁移哲学），消除 `importlib` 的间接性，调用栈更直观。
- **风险/代价**：**必须修改两个既有稳定、gate 关键的校验器**（`agate-frontmatter-check.py` 是
  全仓每次 pre-commit 都会跑的 frontmatter 校验器；`agate-md-field-get.py` 是 `check-gate.py`
  P1-P8 全部分支都在用的字段读取入口）——这两个文件当前不在 P0-brief/dispatch-context 声明的
  改动面内，搬迁常量需要保证**逐字节行为等价**（尤其 `_check()` 与 `MAX_DEPTH`/`_value_depth`
  嵌套深度检查、`_extract_frontmatter_block` 等辅助逻辑是否也要搬、搬多少算"纯数据"搬多少算
  "逻辑"边界不清晰），需要为这两个文件补充独立的**行为不变回归测试**，直接推高本已因
  SELF-GATE 触发而收紧的改动面与测试负担。且这是本任务 5 项 issue 之外的第 6 类改动（协议库
  重构），P1 的 29 条 BDD 均未要求整改 `agate_common.py` 的既有字段分类架构，超出已锁定范围。
- **工作量**：预计比候选 A 多 2-3 倍改动量（2 个既有文件的重构 + 回归证明 + 2 个新脚本）。

### 选择理由

选 **候选方案 A**。核心判据不是"A 更简单"这种空话，而是三点具体的隐含假设差异：

1. **改动面边界**：候选 B 隐含假设"顺手把公共库现代化"是本任务该做的事，但 dispatch-context
   已明确声明改动面为"新增两个脚本 + check-gate.py + phases.yaml + 模板 + 测试"，不含
   `agate-frontmatter-check.py`/`agate-md-field-get.py`。候选 A 严格落在这个边界内。
2. **同源保证的强度相同，但达成路径的风险不同**：两者都能做到"SCHEMAS 物理上只有一份"这一
   BDD-15 核心要求，但候选 A 达成这一目标**不需要改任何一行已有校验逻辑**（用 `importlib` 读
   活对象），候选 B 达成同样目标需要**先证明搬迁后行为完全不变**——后者的验证成本内在地更高，
   且验证失败的后果（frontmatter 校验器行为漂移）影响全仓所有任务而非仅本任务。
3. **既有先例可复用**：`check-routing.py` 已经在生产用 `importlib` 方式复用 `check-pruning.py`
   的 `_md_field`/`_read_p1` 等内部函数（README 式声明"同源复用，无第二份实现"），候选 A 是同一
   模式的第三次应用（第一次是 `check-routing.py` 复用 `check-pruning.py`，第二次是复用
   `agate-risk-score.py`），不是发明新技术；候选 B 目前在本仓库没有"把已有校验器常量搬进
   agate_common"的先例（`parse_gate_commands_block` 等函数是**首次实现即放在** agate_common，
   不是"从别处搬迁"）——照搬"迁移已上线校验器"这类操作的历史成本未知，候选 A 的历史成本已知
   （零起色，`check-routing.py` 一直稳定）。

若未来 set 工具的实际使用暴露出"分散在三个文件里的 schema 定义确实造成维护困难"，可另开
DEBT 走候选 B 的路径重构——但那是后续证据驱动的决策，不是本任务现在就该做的预防性重构
（YAGNI）。

## 3. 详细设计

### 3.1 key 白名单（BDD-17）

```python
# 伪代码，机械并集规则，非抄 design note 举例子集
GENERIC_HEADER_KEYS = frozenset({
    "phase", "task_id", "type", "parent", "trace_id", "status", "created", "agent",
})  # 来源：task-files.md「通用 Header」（纯 prose 文档，无机器可读结构，此处硬编码，
    # 注释标明来源文件路径，供未来该文档改版时人工同步）

def _writable_keys(rules_root):
    phases = read_rules_yaml(rules_root, "phases") or {}
    task_field_union = set()
    for p in phases.get("phases", []) or []:
        task_field_union.update(p.get("task_fields", []) or [])
    return GENERIC_HEADER_KEYS | task_field_union
```

`task_field_union` 运行时从 `phases.yaml` 计算（不手抄各阶段字段列表），phases.yaml 新增
`task_fields` 时白名单自动覆盖（P1 §3 同类扫描已确认的回归拦截手段）。

**排除**：`agent` 虽在 `GENERIC_HEADER_KEYS`，但**永久拒绝 set 写入**（design note §7.2：
"agent 字段不可被 set 改写，防伪造身份"）——`_writable_keys()` 计算出的候选集合还需减去
`{"agent"}` 才是真正可写集合；`--list`/`--help` 对 `agent` 输出"该字段由主 Agent 在派发时填写，
不接受 set 写入"。

**证据字段拒绝**（BDD-9）：`EVIDENCE_FIELDS = get 工具.NO_FALLBACK_INT_FIELDS | {"regression_pass"}`
（动态从加载的 get 模块取值，不手抄 9+1 个字段名）。

**追加/嵌套字段拒绝**（BDD-18）：`APPEND_ONLY_FIELDS = get 工具.NO_FALLBACK_LIST_FIELDS | get 工具.JSON_FIELDS`
（同样动态取值：`need_confirm_resolved`/`suggest_resolved`/`scope_resolved`/`mechanism_issues`/
`execution_issues`/`dispatch_plan`）。

### 3.2 value 校验分派（BDD-1~3, 15）

按目标文件 `basename` + 字段名两级分派：

1. **`basename` 命中 `SCHEMAS`（P1-requirements.md / P2-design.md / P6-acceptance.md /
   P7-consistency.md）且字段在该 schema 的 `types`/`enums` 中** → 深拷贝当前 frontmatter dict，
   应用候选值，调用动态加载的 `_check(basename, SCHEMAS[basename], candidate_fm)`；返回值中
   以 `f"{basename}:{field}:"` 开头的行 → 原样透传为错误信息（**这一步已用真实数据验证**，见
   §6，`candidate_count=0` 时透传消息为 `"P2-design.md:candidate_count: 值 0 小于最小值 1"`，
   与 `check-frontmatter.py`/pre-commit 实际看到的错误文案逐字节一致）。
2. **字段是 `status`** → 按 basename 分派固定枚举表（表来源见 §3.4）；不落 SCHEMAS 路径（SCHEMAS
   四个 schema 均不含 `status` key，已核实）。
3. **字段是 `criteria_total`/`criteria_passed`（P6.5 专属，int）或 `verdict_evidence`（P6.5
   专属，list）** → 无 SCHEMAS 覆盖、无 get 工具 KNOWN_OPS 覆盖（已核实），走最小类型强校验
   （int()/list 切分），类型依据 = `check-judge-verdict.py` 第 9-10 行文档对这三个字段的消费
   方式（读代码确认，非猜测）。
4. **其余字段（`risk_level`/`ceremony`/`ui_render_shape`/`phases`/`test_code_dir`/
   `implementation_dir`/`bump_type` 等，命中 phases.yaml task_fields 但不在 SCHEMAS 覆盖内）**
   → 走 get 工具的 `BOOL_FIELDS`/`LIST_FIELDS`/`INT_FIELDS`/`STRING_FIELDS` 类型分类做类型强校验
   （int 必须数字、bool 必须 true/false、list 按空格切分），**不额外发明枚举**——这些字段目前
   在 check-gate.py 里本来就是"存在性/类型"检查为主（如 `ceremony` 只在 `check-routing.py` 里
   校验 `∈ {thin,standard,full}`，那是**阶段路由**逻辑不是 frontmatter schema，set 不越权做
   路由语义校验，只做格式层拦截）。

### 3.3 gate_commands 正文块（BDD-7, 8）

`agate-md-field-set-gate-commands.py FILE <yaml块或@文件路径>`：
1. `yaml.safe_load` 候选块 → 必须是 `dict`（否则拒绝，"gate_commands 块须为 key: value 映射"）。
2. 逐 key 校验：`agate_common.is_legal_gate_key(key, known_phase_ids(resolve_rules_root(__file__)))`
   （与 `check-gate.py` P2 分支对账逻辑 `_reconcile_p2_fields()` 第 731-756 行**同一函数**，非
   重写）；`_timeout_seconds` 后缀 key 额外校验值为正整数（`is_gate_meta_key` 已识别该后缀，
   本工具补值类型检查，agate_common 本身不做值类型校验）。
3. 全部合法 → 生成标准块文本（`"gate_commands:\n" + "".join(f"  {k}: {v}\n" for k, v in entries)`，
   缩进/格式精确匹配 `agate_common._GATE_KEY_LINE_RE`）→ 用正则（同 `_GATE_COMMANDS_BLOCK_RE`
   边界语义）整块替换正文中既有 `gate_commands:` 块（无既有块则追加到正文末尾）。
4. **自校验**：写入前用 `agate_common.parse_gate_commands_block(新正文)` 反解析一次，断言
   `entries == 候选 entries`（顺序/值均一致）才允许落盘——BDD-7"能正确解析该块"在写入前就
   已验证，不是写完才发现解析不出来。
5. 原子写同 §3.5。

### 3.4 status / agent 角色权限（BDD-3, 4）

```python
# 按 basename 分派的 status 合法枚举（来源逐条标注，均非凭空定义）：
STATUS_ENUM_BY_BASENAME = {
    # task-files.md 通用 Header：status: {draft|approved|rejected|done}
    # + dispatch-prompt.md「Review 角色特别指令」：review 类文件补充 needs-revision
    "P1-review.md": frozenset({"draft", "approved", "rejected", "needs-revision"}),
    "P2-review.md": frozenset({"draft", "approved", "rejected", "needs-revision"}),
    "P4-review.md": frozenset({"draft", "approved", "rejected", "needs-revision"}),
    # P6.5 专属：与 check-judge-verdict.py._VALID_STATUS 同源（importlib 动态取值，非手抄）
    "P6.5-judge-verdict.md": None,  # 运行时替换为动态加载的 _VALID_STATUS
}
DEFAULT_STATUS_ENUM = frozenset({"draft", "approved", "rejected", "done"})  # task-files.md 通用默认
```

角色绑定（BDD-4）：写入 `status: approved`（或任何非 `draft` 值）时，读目标文件**现有**
frontmatter 的 `agent` 字段（选项 A，design note §7.2 已决策，非本阶段新决策）：
- `agent == "main"` → 硬拒绝（与 `check-gate.py` `agent == "main"` 判定逐字节相同的字符串比较，
  见 §1.1 files_to_read 中 check-gate.py 行号引用）。
- `agent` 不在动态列出的 `{resolve_agate_root()}/assets/review-roles/*.md` 文件名集合（去
  `.md` 后缀）内 → 拒绝，提示"该字段按协议应由 review/judge 类角色填写（见 role-system.md），
  当前 agent={x} 不在角色清单内"。**声明**（design note §7.1/§7.4 原文照抄要求）：这一步是
  UX 引导，不是安全边界——绕开 set 直接手写文件不受此约束，真正的防造假仍在 gate 链
  （`agent == main` 检查 + judge + 账本）。
- 均通过 → 允许写入。

**为什么这是"同源"而非"set 自建"**：`agent == "main"` 分支逐字节复用 check-gate.py 现有判定
（唯一真正被 gate 强制执行的规则）；角色白名单分支读的是协议已有的 `assets/review-roles/`
目录（role-system.md 明确声明该目录是"第二层：评审角色"的权威位置，非 set 发明的新清单）。
两个方向都不会产生"set 通过、gate 拒绝"的漂移——只会产生"set 拒绝、gate（如果被绕过）可能
放行"的单向更严格结果，这一不对称性已被 design note §7.1 明确承认并接受（"这是 UX 层的引导 +
早纠错，不是 anti-tamper 安全机制"）。

### 3.5 原子写 / 边界行为（BDD-10~14）

- **原子写**：`fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(FILE)) or ".", prefix=".md-field-set-")`
  → 写入 → `os.replace(tmp, FILE)`（POSIX `rename` 原子，同文件系统内不产生半写状态）；任何
  异常（含 KeyboardInterrupt 模拟进程被杀）在 `os.replace` 之前抛出 → `os.unlink(tmp)` 清理 →
  exit 非 0，原文件字节不变（BDD-10 的"模拟中断"用测试里 monkeypatch `os.replace` 抛异常验证）。
- **文件不存在**（BDD-11）：`--list` 与 `<op> <value>` 均先 `os.path.isfile(FILE)` 检查，不存在
  → 拒绝 + "请先 Write 产出文件，再 set 字段"，**不创建文件**（design note §5.6 已决策）。
- **无 frontmatter**（BDD-12）：`split_frontmatter()` 返回 `(None, 原文全文)` → 在文件头插入
  `"---\n" + yaml.safe_dump({key: value}) + "---\n"` + 原文全文（原文一字节不动，作为新 body 原样
  拼接在新 frontmatter 块之后）。
- **正文残留同名字段**（BDD-13）：写入 frontmatter 后，对**新 body**（即上一步保留的原文）做
  一次 `re.search(rf"^{re.escape(key)}:", body, re.MULTILINE)`；命中 → 额外输出 WARNING
  "检测到正文残留同名字段 {key}，frontmatter 优先，建议清理"，**不修改 body**。
- **check-frontmatter.py 兼容**（BDD-14）：全程用 `yaml.safe_load`/`yaml.safe_dump`
  （`default_flow_style=False, allow_unicode=True, sort_keys=False`）——与
  `agate-frontmatter-check.py._extract_frontmatter_block` + `yaml.safe_load` 是同一 YAML
  语义（均为 pyyaml 标准 safe 系列），互为读写对偶，天然兼容；作为验收锚，实现完成后须对
  set 写出的样本文件实跑 `check-frontmatter.py` 确认 exit 0（P3/P5 测试用例覆盖）。

### 3.6 DEBT0019：roadmap.md 列数完整性校验

```python
_ROADMAP_EXPECTED_COLS = 9  # 7 数据列（id/标题/状态/来源/关联任务/创建/更新）
                             # + split("|") 产生的首尾两个空字符串 = 9
                             # （已用真实 agate-workspace/roadmap/roadmap.md 表头行核实，见 §6）
...
for line in text.splitlines():
    cols = [c.strip() for c in line.split("|")]
    if len(cols) != _ROADMAP_EXPECTED_COLS:
        continue
    rm_id, status, related_task = cols[1], cols[3], cols[5]
    ...
```

替换现有 `len(cols) < 8` 为精确匹配 `!= 9`。任何单元格内含字面 `|` 都会改变 `len(cols)`，从而
被跳过而非错位取值（BDD-20）。既有合法表格（列数恰为 9）行为完全不变（BDD-21，回归覆盖
TAG0023 `test_bdd_5_p8_roadmap_rm_not_done_blocked_exit_1` / `test_bdd_6_..._exit_2` /
`test_bdd_7_roadmap_rm_ag0032_backfilled_done` 三条既有用例，见 files_to_read）。

### 3.7 DEBT0020：roadmap.md 仓库根锚定

```python
def _repo_root():
    rc, out = _git(["rev-parse", "--show-toplevel"])
    if rc != 0:
        return None
    return out.strip()

...
def gate_p8(task_dir):
    ...
    repo_root = _repo_root()
    if repo_root is None:
        sys.stderr.write("GATE P8 WARNING: 仓库根不可得（非 git 仓库环境），跳过 roadmap-done 检查\n")
        roadmap_path = None
    else:
        roadmap_path = os.path.join(repo_root, "agate-workspace", "roadmap", "roadmap.md")
    blocked = _check_roadmap_done(task_id, roadmap_path) if roadmap_path else None
    ...
```

复用现有 `_git()`（第 177-189 行，本身优先走 `agate_common.run_git`）。已实测（见 §6）
`git rev-parse --show-toplevel` 在本 worktree 环境下从仓库根 CWD 与非仓库根 CWD（`agate/scripts`
子目录）调用均正确返回同一 worktree 根路径，且正确处理 git worktree 语义（`.git` 是文件而非
目录，若改用"向上找 `.git` 目录"的文件系统遍历方案会在本任务自身的执行环境下就先错——这正是
候选方案权衡时排除该路径的实测依据，见 §1.3 与设计过程中已否决的路径遍历方案）。既有合法场景
（CWD=仓库根）行为不变（BDD-24，`_git(["rev-parse","--show-toplevel"])` 从仓库根调用返回值
= 仓库根本身，与当前 `os.path.join("agate-workspace", ...)` 相对路径在"CWD=仓库根"场景下的
既有行为等价）。

### 3.8 RM-AG0049：phases.yaml P4 outputs 补全

```yaml
  - id: P4
    ...
    outputs:
      - {file: P4-implementation.md, required: true}
      - {file: P4-review.md, required: true, status_field: status}
```

仅追加一行。已验证（§1.3 风险 5 + §6）不触发 S-1/S-2/S-3 新增不一致：S-1/S-2 只比对
`id`/`name`/`exec_role`（`check-structure-consistency.py` 第 153-179 行），不读 `outputs`；
S-3（第 223-229 行）要求 `outputs[].file` 字面出现在对应阶段卡片正文，`"P4-review.md"` 已在
`phase-cards/P4-implementation.md` 出现 10 次（第 90-153 行），追加声明后天然满足。

### 3.9 RM-AG0050：P6.5 措辞统一

在 `agate/rules/phases.yaml` 的 `id: P6.5` 条目前追加纯注释块（不改变任何可解析字段）：

```yaml
  # 注：P6.5 是挂载于 P6→P7 转移的强门槛子阶段，不是与 P0-P8 平级的独立 phase 值
  # （.state.yaml 的 phase 字段保持 P6 直至 P7）；本条目结构化声明其产出/门槛/重试上限，
  # 供 check-gate.py P6.5 分发与 CLI 调用，口径详见 state-machine.md「状态机定义」节。
  - id: P6.5
    ...
```

`id: P6.5` 结构本身**不删除、不改字段**——`agate_common._DEFAULT_PHASE_IDS`、
`check-gate.py handlers["P6.5"]`、`check-structure-consistency.py` S-2 的 P6.5 特例前缀
解析等 8 个脚本消费点（P1 同类扫描线索 3 已列全）均依赖该结构存在，删除会连锁破坏；本次修复
范围仅是"文档措辞层面消解与 state-machine.md 的表述冲突"，不触碰任何脚本判定逻辑，BDD-28
的"既有判定行为不变"因此是纯注释改动的自然结果（无需额外证明，改动本身不影响任何解析路径）。

### 3.10 BDD-19：模板同步

`dispatch-prompt.md` 第 62-74 行替换为：

```
## 产出文件字段填写
用 `agate-md-field-set` 填写产出文件的 frontmatter 字段（先 `--list` 看本阶段应填字段清单；
set 报错就照提示改；不要手写 frontmatter，不要复制任何示例代码块）。
set 报错但改不明白 → 报告主 Agent，不要绕过 set 直接手改文件。
`phase`/`task_id`/`parent`/`trace_id`/`agent` 由主 Agent 派发时已在 dispatch-context 中给出
具体值，用 `agate-md-field-set` 逐个写入即可；完整字段列表见 `task-files.md`「通用 Header」。
```

`dispatch-context.md` 在 `### 输入文件` 节后追加固定行（放在 `</dispatch_guide>` 之前）：

```
### 产出文件字段
用 `agate-md-field-set FILE --list` 查看本阶段应填字段；`agate-md-field-set FILE <key> <value>`
逐个写入；写入失败照错误提示修正，不要手写 frontmatter；仍失败则报告主 Agent，不要绕开 set。
```

## 4. files_to_read（P4 implementer 导航）

```yaml
files_to_read:
  - path: agate/scripts/agate-md-field-get.py
    why: 整份复用其字段类型分类（BOOL/LIST/INT/STRING/NO_FALLBACK_*/JSON）与 _read_frontmatter/_get，set 与之动态对称
  - path: agate/scripts/agate-frontmatter-check.py
    why: SCHEMAS 字典 + _check() 是 set 校验候选值的直接复用来源（importlib 动态加载，§3.2）
  - path: agate/scripts/check-routing.py:29-63
    why: _load_script() 是本任务复用的 importlib 动态加载既有先例，照此模式写 set 里的加载器（含模块缓存）
  - path: agate/scripts/agate_common.py:637-796
    why: read_rules_yaml/resolve_rules_root/known_phase_ids/is_legal_gate_key/split_frontmatter/parse_gate_commands_block 六个函数普通 import 复用
  - path: agate/scripts/check-gate.py:177-190
    why: _git() 辅助函数，DEBT0020 修复直接复用（避免另起 subprocess 调用方式）
  - path: agate/scripts/check-gate.py:1181-1292
    why: DEBT0019/20 的目标函数 _check_roadmap_done()/gate_p8()，改动落点精确到这段
  - path: agate/scripts/check-gate.py:759-809
    why: gate_p2() 的 status/agent 判定与 _reconcile_p2_fields() 的 gate_commands 校验写法，是 §3.3/§3.4 复用/对齐的参照实现
  - path: agate/scripts/check-judge-verdict.py:50-60
    why: _VALID_STATUS 定义，P6.5 status 枚举同源来源（importlib 动态取值）
  - path: agate/rules/phases.yaml
    why: RM-AG0049（P4 outputs）与 RM-AG0050（P6.5 注释）两处改动落点；同时是 §3.1 key 白名单运行时计算的数据源
  - path: agate/state-machine.md:69-79
    why: RM-AG0050 措辞对齐的权威文本来源，注释文字须与此处一致
  - path: agate/scripts/check-structure-consistency.py:153-266
    why: 确认 RM-AG0049 改动不触发 S-1/S-2/S-3 新增不一致（已验证，实现时仍需附带回归用例）
  - path: agate/assets/templates/dispatch-prompt.md:62-74
    why: BDD-19 的直接改动落点（Header 复制段替换为 set 指引）
  - path: agate/assets/templates/dispatch-context.md
    why: BDD-19 追加"产出文件字段"一行式指引的落点
  - path: agate/assets/templates/task-files.md
    why: GENERIC_HEADER_KEYS 与 status 默认枚举的文档来源
  - path: agate/role-system.md:37-74
    why: status:approved 角色白名单的权威来源说明（assets/review-roles/ 目录角色分层）
  - path: docs/design-notes/design-md-field-set.md
    why: RM-AG0048 一期完整规格（CLI 形态/错误信息格式/边界行为§5.5-5.10/验收锚§10），P1 非强制照搬但本设计已采纳其大部分决策，implementer 需要完整上下文
  - path: agate/tests/unit/test_agate_md_field_get.py
    why: 新测试文件 test_agate_md_field_set.py 的既有测试写法/fixture 约定参照
  - path: agate/tests/unit/test_check_gate.py:1320-1580
    why: DEBT0019/20 需要追加的回归用例紧邻此处既有 roadmap 相关用例（_write_roadmap/_run_gate fixture 复用）
```

## 5. env_constraints（确认/细化 P0-brief）

```yaml
env_constraints:
  debug_env: "本 worktree（/home/kity/oclab/agate/.worktrees/agate-TAG0024）内直接跑 pytest/ruff；
    /tmp 只读，pytest 必须显式 --basetemp 指向仓库内可写目录 + -p no:cacheprovider（P0-brief 已声明，
    本阶段未发现需要加强的额外约束）"
  isolation_check: "本任务不涉及测试/生产环境隔离问题（纯代码逻辑改动，无服务/数据库/外部 API）；
    DEBT0020 的『非仓库根 CWD』测试场景在同一 worktree 内用 pytest tmp_path 构造临时 git repo
    验证（现有 test_check_gate.py 已有 _init_repo_with_task 等 fixture 可直接复用，见 files_to_read）"
  git_worktree_note: "本任务自身运行在 git worktree 环境（.worktrees/agate-TAG0024），DEBT0020 的
    git rev-parse --show-toplevel 方案已在此确切环境下实测验证（§6），不是假设"
```

## 6. minimal_validation

```yaml
minimal_validation:
  assumption: "纯代码逻辑，无外部系统依赖；依赖的内部函数/数据转换见下方逐条验证"
  method: |
    本阶段已用真实代码/真实数据做了 4 项验证（非假设）：
    1. importlib 动态加载可行性：`python3 -c "import importlib.util; ...
       spec_from_file_location('agate_frontmatter_check', 'agate/scripts/agate-frontmatter-check.py')
       ...exec_module...` 实测取到 SCHEMAS（4 个 key）与 _check() 函数，并对
       candidate_count=0 的候选值调用 _check('P2-design.md', SCHEMAS['P2-design.md'], data)
       实际返回 ['P2-design.md:candidate_count: 值 0 小于最小值 1']——证明候选方案 A 的核心
       复用路径（§2 候选 A / §3.2）物理可行，且错误文案与 pre-commit 实际看到的一致。
    2. 同法验证 agate-md-field-get.py 动态加载：实测取到 BOOL_FIELDS/NO_FALLBACK_INT_FIELDS
       等 frozenset 与 _read_frontmatter 可调用函数，验证 §3.1/§3.2 依赖的字段分类可动态取值。
    3. DEBT0020 假设验证：`git rev-parse --show-toplevel` 在仓库根 CWD 与非仓库根 CWD
       （agate/scripts 子目录）下均返回同一路径
       /home/kity/oclab/agate/.worktrees/agate-TAG0024（本 worktree 根，非主仓库路径）——
       证明 §3.7 方案在本任务真实执行环境（git worktree）下可靠，同时排除了"遍历查找 .git
       目录"候选路径的已知缺陷（worktree 的 .git 是文件不是目录，会被那类遍历逻辑误判）。
    4. DEBT0019 列数基准验证：对 agate-workspace/roadmap/roadmap.md 的真实表头行
       `| id | 标题 | 状态 | 来源 | 关联任务 | 创建 | 更新 |` 执行 `line.split("|")`，
       实测长度为 9（7 数据列 + 首尾两个空字符串），确认 §3.6 常量 9 的正确性。
    5. RM-AG0049 影响面验证：grep 确认 "P4-review" 已在 phase-cards/P4-implementation.md
       出现 7 处（第 90-153 行），且读 check-structure-consistency.py 第 153-266 行确认
       S-1/S-2 不读 outputs 字段——排除 §3.8 改动触发 S 系列新增报错的可能性。
  result: confirmed
  note: "5 项验证均已在本阶段用 bash/python3 -c 实际执行完成（非纸面推演），详见上方 method
    逐条描述；无需额外起服务/浏览器/网络，P4 实现阶段可直接按 §3 节的具体代码路径落地。"
```

## 7. gate 命令（在 P2 固化，后续不得修改）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -v"
  P3_timeout_seconds: 250
  P5: "python3 -m pytest agate/tests/ --basetemp=.pytest-tmp -p no:cacheprovider -q --tb=no"
  P5_timeout_seconds: 250
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_shellcheck: "shellcheck agate/scripts/*.sh"
  P5_count: "bash agate/tests/scripts/count-tests.sh"
  P5_ruff: "~/.venvs/agate-dev/bin/ruff check agate/"
  project_module: "agate"
```

**说明**：
- P3/P5 拆成独立 key（不用 `&&` 短路链）：`P5_consistency`/`P5_shellcheck`/`P5_count`/`P5_ruff`
  各自独立执行、独立判定 exit code，任一失败不掩盖其余三个的执行——对齐本次派发指令与
  architect.md「`--strict` 反模式」的强制要求。
- `P5_shellcheck` 范围限定 `agate/scripts/*.sh`（本任务不新增/修改 shell 脚本，此 key 是既有
  三个 hook shell 脚本——`commit-msg-self-gate.sh`/`pre-commit-gate.sh`/`pre-push-gate.sh`——
  的常规卫生检查，防止本次改动间接影响它们时无检测）。
- `P3_timeout_seconds`/`P5_timeout_seconds` 取 250s（非建议档位默认 120s）：已知本仓库全量
  pytest 单线程实测耗时约 165.7s（`.github/workflows/protocol-tests.yml` 注释"165.7s 串行"），
  按经验值 ×1.5 = 248.55s，向上取整为 250s，与「宁高勿低」取值原则对齐，不再向下取整。
- `P5_consistency`/`P5_shellcheck`/`P5_count`/`P5_ruff` 未声明 `_timeout_seconds`（均为秒级
  命令，缺省行为 = 现状，向后兼容，不需要额外声明）。

## 8. 实现完成的标志（供 P3 测试设计 / P5 验证使用）

- `agate-md-field-set.py`/`agate-md-field-set-gate-commands.py` 存在，`test_agate_md_field_set.py`
  覆盖 BDD-1~19 全部 19 条且全部转绿。
- `check-gate.py` 的 `_check_roadmap_done()`/`gate_p8()` 按 §3.6/§3.7 修改后，
  `test_check_gate.py` 新增用例（DEBT0019 列错位不误判 + DEBT0020 非仓库根 CWD 正确解析）
  转绿，且 TAG0023 既有三条 roadmap 用例（BDD-5/6/7）保持转绿（BDD-21/24 的"既有行为不变"
  证据）。
- `phases.yaml` 的 P4 outputs 与 P6.5 注释改动后，`check-structure-consistency.py` 全量跑
  S-1~S-6 均 0 mismatch（BDD-26/28）。
- `dispatch-prompt.md`/`dispatch-context.md` 不再含可被字面复制的 frontmatter 代码围栏
  （grep 确认无裸 ` ```\n---\n` 结构残留），改为 set 一行式指引（BDD-19）。
- `check-gate.py`/`check-events.py` 的 diff 除 `_check_roadmap_done()`/`gate_p8()` 的
  `roadmap_path` 定位相关行外无其他改动（BDD-29，P7 阶段逐行核对）。
- `gate_commands` 全部 key（P3/P5/P5_consistency/P5_shellcheck/P5_count/P5_ruff）独立 exit 0。
