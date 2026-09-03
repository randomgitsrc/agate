---
phase: P2
task_id: TAG0031
type: design
parent: P1-requirements.md
trace_id: TAG0031-P2-20260904
status: draft
created: 2026-09-04
agent: architect
candidate_count: 2
packages: [agate-scripts, agate-tests, agate-docs]
domains: [backend]
ui_affected: false
dispatch_plan: {mode: static-batch, parallel_limit: 3, batches: [{id: version-mgmt, complexity: medium}, {id: test-isolation, complexity: low}, {id: gate-robustness, complexity: medium}]}
---

# P2-design.md — TAG0031 DEBT 存量修复批

方案覆盖 P1 锁定的 15 条 BDD（7 条 DEBT：DEBT0002/0003/0004/0007/0016/0017/0018 + 同类扫描登记
BDD-14 + 登记闭合 BDD-7/15）。P1 已按文件域分三簇（版本管理域 / 测试隔离 / check-gate.py 健壮性），
本设计沿用该切分，逐簇给出具体改动点。

## 1. 影响面梳理（改什么 / 不改什么 / 风险在哪）

### 1.1 改什么

**簇 A：版本管理域（DEBT0002/3/4）**

| 文件 | 改动点 | 关联 BDD |
|---|---|---|
| `agate/scripts/agate_common.py` | 紧邻 `resolve_workspace`（L551-580）之后新增 `compute_sha256(path)`：文件=内容哈希，目录=按 `f.relative_to(p).as_posix()` 字典序排序逐文件 sha256 拼接再整体 sha256——与现状两侧实现逐字节一致，直接复用已 import 的 `hashlib`/`Path`（L20/L28） | BDD-1 |
| `agate/scripts/agate-pack-offline.py` | 删除本地 `def compute_sha256`（L51-60），改 `from agate_common import compute_sha256`；`build_manifest`（L75 调用点）不变 | BDD-1/2 |
| `agate/scripts/install-offline.py` | 删除本地 `def compute_sha256`（L85-94），`verify_checksums`（L111 调用点）改用 agate_common 版本；**需处理 pyyaml 引导时序问题，见 1.3 风险 R1** | BDD-1/2 |
| `agate/scripts/agate-install.py` | `_find_references`（L230-260）返回值改为 `(refs, hit_limit)` 二元组：`depth > _SCAN_MAX_DEPTH` 触发 `dirs[:] = []` 时置 `hit_limit=True`；`.agate-version` 命中但 mtime 超窗跳过时同样置 `hit_limit=True`；`_cmd_uninstall`（L284-317）解包后，`hit_limit` 为真时立即 stderr 输出 WARNING（不论 `refs` 是否为空，都要提示——BDD-4 要求"卸载判定不因漏扫误判为无引用"，WARNING 与卸载结果是否放行是两件独立的事） | BDD-4/5 |
| `agate/UPGRADING.md`（~L505-520，「④ 新工具」小节） | 新增信任边界说明段落："checksum 校验防损坏，不防整包替换；bundle 提供者需可信" | BDD-3 |
| `agate/scripts/README.md`（~L65-75，`install-offline.py` 行） | 同上信任边界说明，追加到该行下方或表格后的说明段 | BDD-3 |
| 新增测试 | `test_agate_pack_offline.py`/`test_install_offline.py` 补 hash 一致性用例；新增 `agate/tests/regression/test_offline_bundle_roundtrip.py`（pack→install→卸载全流程，`subprocess.run` mock 网络/git，`HOME` 重定向临时 `AGATE_HOME`，见 §4 `gate_commands.P5_offline_bundle`） | BDD-2 |

**簇 B：测试隔离（DEBT0007）—— 不改产出代码，仅验证 + 登记**

| 文件 | 改动点 | 关联 BDD |
|---|---|---|
| （无代码改动） | `check-pruning.py:84-100` 的 `_staged_source_count` 隔离修复已由 TAG0024 commit `e2357fc` 落地；`test_check_pruning.py` 现有 4 个用例（`test_p2_6e_...`/`test_p2_52_...`/`test_p2_52b_...`/`test_p2_6f_...`，L214/338/354/370）均已带 `env={"GIT_CEILING_DIRECTORIES": str(tmp_path)}` 隔离且实测全绿——本次只需重跑确认 + 把结果落到 P5 证据 | BDD-6 |
| `agate-workspace/debt/tech-debt.md` | DEBT0007 条目 `status: open → closed`，追加 `closed_at` + closure 说明 + evidence 追加块（格式复用 DEBT0005/6 先例，L110-158） | BDD-7 |

**簇 C：check-gate.py 健壮性（DEBT0016/17/18）**

| 文件 | 改动点 | 关联 BDD |
|---|---|---|
| `agate/scripts/check-gate.py`（顶部 import，L42-46） | `from agate_common import read_vision_tri_state, run_git` 追加 `resolve_workspace`，ImportError 分支追加 `resolve_workspace = None` | DEBT0016 前置 |
| `agate/scripts/check-gate.py` gate_p4（L985-987） | `code_map_file` 推导改为：`run_git(["rev-parse", "--show-toplevel"], cwd=task_dir)` 取 `project_root` → `resolve_workspace(project_root)` 取 `workspace` → `os.path.join(workspace, "agents", "CODE-MAP.md")`；`run_git`/`resolve_workspace` 任一为 `None`（agate_common 不可用，WARNING 分支非阻断）时回退原 `dirname(dirname(...))` 算术，不新增阻断面 | BDD-8/9 |
| `agate/scripts/check-gate.py` gate_p4（L990） | `"## 新增文件核对表" not in _read_text(...)` 改为 `not re.search(r"^##\s+新增文件核对表", _read_text(...), re.MULTILINE)`（沿用 `agate_common.py:890` UI 设计标题判定同款正则风格，`re` 已 import） | BDD-10/11 |
| `agate/scripts/check-gate.py`（L78-165 降级 stub 块） | 新增模块级哨兵 `_AGATE_COMMON_MISSING = object()`；`read_rules_yaml`/`count_p7_markers`/`count_p6_pass_fail`/`count_code_map_lines` 四个 stub 改为 `return _AGATE_COMMON_MISSING`（不再返回 `None`/`(0,0)`/`0`） | BDD-12/13 前置 |
| `agate/scripts/check-gate.py` gate_p1（L687）/ gate_p6（L1084）/ gate_p7（L1144, L1238） | 四个调用点各自在使用返回值前先判 `is _AGATE_COMMON_MISSING`：命中则 `sys.stderr.write("GATE Px: 安装破损：agate_common 不可导入，无法读取 <字段>\n"); return 1` | BDD-12 |
| 新增/修改测试 | `test_check_gate.py` 补：①非标准两级嵌套场景（BDD-9）；②「新增文件核对表」自指假阴性场景（BDD-10）+ 真实标题存在场景（BDD-11）；③四个消费点在 `agate_common` 不可导入模拟下显式 `return 1`（BDD-12）+ 正常导入时全量既有测试逐字节不变（BDD-13） | BDD-8~13 |

**跨簇共享写入（不属于任一 batch，由主 Agent 在三簇均返回后统一处理，避免并行写冲突）**

| 文件 | 改动点 | 关联 BDD |
|---|---|---|
| `agate-workspace/debt/tech-debt.md` | DEBT0002/3/4/16/17/18 六条 `status: open → closed`（BDD-15）；DEBT0007 单独登记（BDD-7，见簇 B）；新增 ≥2 条 open DEBT（同类扫描：`task_dir` 类路径推导非本体 2 处 + 「新增文件核对表」子串判定同款、风险更高的 `check-gate.py:881` 一处，BDD-14） | BDD-7/14/15 |

### 1.2 不改什么

- **`agate-pack-offline.py`/`install-offline.py` 除 `compute_sha256` 外的其余函数**（`build_manifest`/`pack_offline`/`load_manifest`/`_validate_manifest`/`install_wheels`/`_copy_tree`/`install_bundle` 等）：DEBT0002 范围仅锁定 hash 工具本体，其余打包/安装逻辑不动，降低回归面。
- **`agate-install.py` 的 `_find_references` 扫描算法本体**（跳过目录集合 `_SCAN_SKIP_DIRS`、深度阈值 4、mtime 窗口 365 天数值本身）：DEBT0004 只加 WARNING 提示，不改变扫描范围/阈值，避免"顺手调优"引入新行为。
- **DEBT0003 的签名体系**（minisign/GPG）：P1 已按 `[SUGGEST]` 定案为文档优先，P0-brief out-of-scope 明确排除，本次仅补文档信任边界说明，不实现签名校验。
- **`check-pruning.py:84-100` 的 `_staged_source_count` 生产代码**：TAG0024 已修复，本次不重复改动，只补验证证据。
- **`check-gate.py` 的其余 20+ 个降级 stub**（`count_design_gap`/`reconcile_*`/`parse_gate_commands_block` 等，L107-165）：DEBT0018 evidence 明确点名的仅 4 个"关键读取器"，`reconcile_*` 一族有显式设计意图声明 fail-open 是既定设计（L79 注释），不在本次改造范围。
- **`check-retrospective.py:74` / `agate-render-dispatch-prompt.py:191` 的 `dirname(dirname(...))` 用法**、**`check-gate.py:881` gate_p2 的子串判定**：P1 同类扫描已判定"本次不处理，登记新 DEBT"（BDD-14），本次只做登记动作，不修代码。
- **`agate_common.py` 的 `import yaml` 强依赖结构**（模块级 `except ImportError: sys.exit(1)`）：虽然 1.3 节 R1 发现的问题根源在此，但改造该结构影响全仓所有 agate_common 消费方（30+ 处 yaml 使用点分散在 5 个函数中），超出"低风险脚本健壮性修复"的既定范围，本次不动；改在 `install-offline.py` 局部承担引导责任（见 R1 缓解措施）。

### 1.3 风险在哪

**R1（新发现）：`compute_sha256` 迁移到 `agate_common.py` 后，`install-offline.py` 的离线 bootstrap 前提被打破**

[SCOPE+] 发现：`compute_sha256` 迁移到 `agate_common.py` 后，`install-offline.py` 的引导流程会出现
         pyyaml 组件"先 `pip install` 后 checksum 校验"的顺序缺口（其余组件均全部 checksum
         通过后才被使用，仅 pyyaml 例外）
         必须做的理由：不修复会打破 BDD-26"checksum 不匹配 → 该组件的任何内容都不会被落地/执行"
         这一字面不变量在 pyyaml 组件上的适用性，属于设计阶段发现的、P1 未预见的必须处理项
         影响：需在 `_ensure_agate_common` 内补一道 pip install 前的内联 checksum 校验（见下方
         缓解设计）；packages: [agate-scripts]；不新增 BDD 编号，作为 BDD-1/2 的机制细化处理

- 现状：`install-offline.py` 当前顶部只 `import hashlib/json/os/re/shutil/subprocess/sys` + `Path`，零外部依赖——这是刻意设计，因为它要在"可能未安装 pyyaml 的内网机器"上跑，且其 `main()` 执行顺序是**先 `verify_checksums()`（L228，需要 `compute_sha256`）再 `install_wheels()`（L237，才会把 bundle 自带的 pyyaml wheel 装上）**。
- 若把 `compute_sha256` 直接改成 `from agate_common import compute_sha256`，而 `agate_common.py` 顶部是 `import yaml` 失败即 `sys.exit(1)`（硬依赖，L30-34）——在真正没有预装 pyyaml 的目标机器上，`verify_checksums()` 执行前的 `import agate_common` 会直接让整个安装器崩溃，且这一步刚好发生在"给它装 pyyaml"（`install_wheels`）之前，构成先有鸡还是先有蛋的死锁：**离线安装器的核心存在理由（在没有 pyyaml 的机器上引导安装）被这次合并破坏**。
- **缓解设计**：`install-offline.py` 新增一个内部引导函数（不叫 `compute_sha256`，不违反 BDD-1「全仓只 1 处定义」的字面断言）——`_ensure_agate_common(bundle_dir, manifest)`：先探测 `import yaml` 是否可用；可用则直接 `import agate_common` 返回模块引用。不可用时分三步：①先用一行内联 `hashlib.sha256(Path(wheel_path).read_bytes()).hexdigest()` 单独校验 `manifest["components"]["pyyaml"]["sha256"]` 这一个文件级 hash（`wheel_path = Path(bundle_dir) / manifest["components"]["pyyaml"]["path"]`；这不是"compute_sha256 的另一份实现"——一次性、单文件、不对外暴露为函数，只是 `_ensure_agate_common` 自身的引导前置检查，不违反 BDD-1「全仓仅 1 处 compute_sha256 定义」）；不匹配 → stderr 报错（指明 pyyaml 组件）+ `return None` / 由调用方 exit 非 0，**不执行 `pip install`**；②内联校验通过后才执行 `pip install --no-index --find-links <bundle_dir>/wheels pyyaml`（bundle 自带 wheel，不联网，不改变"整包受 DEBT0003 已文档化的信任边界覆盖"这一既有假设）；③成功后 `import agate_common` 并返回模块引用。`verify_checksums()` 改为先调 `_ensure_agate_common(bundle_dir, manifest)` 拿到模块引用，再逐组件（含 pyyaml 在内一并重复校验，保持 `verify_checksums` 单一入口逻辑不特判某个组件）调用 `agate_common_mod.compute_sha256(p)`。约 5-8 行改动量。
- **代价确认**：修复后 pyyaml 的 wheel 与其余组件享有同等的"先校验后使用"顺序——`_ensure_agate_common` 内联校验通过才 `pip install`，不再存在"先执行、后校验"的缺口，BDD-26"checksum 不匹配则不落地"的字面不变量对 pyyaml 组件同样成立。`verify_checksums()` 阶段会对 pyyaml 再校验一次（幂等，同一文件同一 hash，无副作用，非重复实现）。唯一残留差异是这一步内联校验用的是原生 `hashlib` 调用而非 `agate_common.compute_sha256`（因为此刻 `agate_common` 尚不可导入，属于引导阶段的物理限制），但两者对同一输入产出同一结果（`compute_sha256` 对文件路径的分支就是 `hashlib.sha256(p.read_bytes()).hexdigest()` 这一行，逻辑完全等价），不构成校验强度弱化，无需接受额外残留风险。
- **回归覆盖**：①原有用例——模拟 `yaml` 不可导入（如 `monkeypatch.setitem(sys.modules, "yaml", None)` + `importlib.reload` 或子进程隔离 `PYTHONPATH`），验证 `_ensure_agate_common` 引导路径可用、`verify_checksums` 最终仍能跑通；②新增用例——构造 checksum 不匹配的 pyyaml wheel（篡改 bundle 内 wheel 文件内容或 manifest 里对应的 `sha256` 值），mock `subprocess.run`，断言 `_ensure_agate_common` 在 `pip install` 之前就 stderr 报错并返回非成功结果，且全程 mock 的 `subprocess.run` 未被调用（用"未被调用"断言校验"校验先于安装"这一顺序本身，而不只是校验最终结果）。两项均列入簇 A 的 BDD-2 测试补强，不新增 BDD 编号（机制细节，不改变 BDD-1/2 描述的外部可观察行为）。

**R2：DEBT0018 fail-closed 只覆盖"旧格式回退"分支，新格式（frontmatter 计数字段存在）时不会触达**

- `count_p6_pass_fail`（gate_p6 L1084）与 `count_p7_markers`/`count_code_map_lines`（gate_p7 L1144/L1238）均只在 `_md_field_get(...)` 频段字段为空（旧格式）时才被调用；新格式（frontmatter `pass`/`fail`/`blocker_count` 等字段已声明）时这三个函数根本不会执行。
- 缓解：BDD-12 的测试用例必须显式构造**旧格式**（无 frontmatter 计数字段）的 P6-acceptance.md/P7-consistency.md，才能命中降级哨兵分支；`read_rules_yaml`（gate_p1 L687）无此限制，是无条件调用点，测试构造更直接。P3/P4 阶段需注意这一差异，不要写出"新格式下也能测出 fail-closed"的错误测试（会假绿）。

**R3：DEBT0016 的 `run_git`/`resolve_workspace` 双依赖降级路径**

- gate_p4 的 CODE-MAP 分支本身是 WARNING-only（不 `return 1`，见 L988-993），若 `agate_common` 不可导入（`run_git`/`resolve_workspace` 均为 `None`），设计选择"回退旧算术"而非"报错阻断"——因为这不是 DEBT0018 evidence 点名的 4 个"关键读取器"之一，保持 fail-open 与既有 WARNING 语义一致，避免把一个非阻断分支意外升级为阻断（超出 P1 授权范围）。
- 缓解：BDD-9 测试需覆盖"非标准两级嵌套 + agate_common 可用"场景（验证走 `resolve_workspace` 分支能正确解析），不要求覆盖"agate_common 不可用 + 非标准嵌套"的组合（P1 未要求，且该组合本身处于两个独立风险的交集，超出本次范围）。

**R4：`agate_common.py` 新增 `compute_sha256` 后的调用方安全性**——目录遍历用 `p.rglob("*")` 不过滤符号链接/特殊文件，与现状两侧实现完全一致（不引入新行为），非本次新增风险，仅确认迁移后维持原样。

**R5：三簇并行实现的文件重叠面**——`check-pruning.py` 与 `check-gate.py` 均属 gate 脚本但改动点不重叠（前者簇 B 只读验证不改代码，后者簇 C 改判定逻辑），`agate_common.py` 被簇 A（新增 `compute_sha256`）与簇 C（追加 import `resolve_workspace`）同时触达——**同一文件不同区域**（簇 A 插入点紧邻 `resolve_workspace` 定义处 L580 之后，簇 C 只改 `check-gate.py` 自己的 import 列表，不改 `agate_common.py` 本体），无行级冲突，但建议两簇合并 commit 前跑一次全量 diff 确认无重复插入。`debt/tech-debt.md` 是三簇 + BDD-14/15 共享的单文件，按 1.1 节「跨簇共享写入」表统一在三簇返回后由主 Agent 一次性处理，不进入 `dispatch_plan.batches` 并行范围。

## 2. 候选方案

### 候选方案 1（选定）：三簇静态拆批并行实现 + 簇内技术方案如上

**方案**：按 `dispatch_plan.batches` 派 3 个 P4 implementer 并行处理 version-mgmt / test-isolation / gate-robustness 三簇（文件域基本不重叠，见 1.3 R5），`debt/tech-debt.md` 登记动作作为三簇返回后的收尾步骤单独处理，不进入并行范围。

**优点**：
- 三簇改动点、测试用例、影响文件几乎互不相交（唯一交集是 `agate_common.py` 的不同区域，已在 R5 确认无冲突），并行不需要额外协调开销。
- 每簇复杂度均为 low/medium，符合「派发编排机制」任务粒度基准（单批产出 ≤3 文件）；version-mgmt 簇改 4 个脚本 + 2 个文档 + 1 个新测试文件，略超单批 3 文件基准，但改动点集中且逻辑强关联（同一 DEBT0002 的 hash 合并 + 同一批次的 DEBT0003/4），按"改动点关联度"而非机械计数拆分更合理，仍判定 medium 而非 high。
- 单元测试实测总耗时仅 34.63s（`-n auto`，见 §4 说明），并行拆批不是为了压缩测试时间，而是压缩 implementer 的上下文体量与 P4 阶段的等待时间。

**风险/工作量**：
- 需要主 Agent 在三簇返回后额外做一次 `debt/tech-debt.md` 合并写入（多写一步，但避免了三个 subagent 同时改同一文件的合并冲突风险，净收益为正）。
- 三簇各自的 P4-implementation.md 会分散在多个文件，P7 一致性检查需要逐簇核对（P1 已判定 P7 不可裁剪，此项工作量本就存在，不因拆批新增）。

### 候选方案 2（备选，权衡后否决）：单批顺序实现（一个 implementer 依次处理全部 7 条 DEBT）

**方案**：不设 `dispatch_plan`，派一个 P4 implementer 按 P0-brief 的 Phase 1/2/3 顺序依次改完版本管理域→测试隔离→check-gate.py 健壮性，产出单份 P4-implementation.md。

**优点**：
- 协调最简单，不需要主 Agent 管理批次汇总与共享文件写入时序。
- 天然避免 R5 提到的 `agate_common.py` 并发编辑风险（顺序执行不存在"同时改同一文件"的问题）。

**缺点（相对候选 1 的实质劣势，非稻草人）**：
- 单 implementer 需要一次性加载三簇全部上下文（`files_to_read` 清单 ≥15 个文件片段），显著增加单次 P4 派发的上下文体量，与 architect.md「控制 P4 implementer 上下文体量」的设计目标相悖。
- 三簇之间无数据依赖（version-mgmt 的 hash 合并结果不影响 gate-robustness 的判定逻辑），顺序执行没有换来正确性收益，纯粹是并行度的浪费——总耗时（人工等待）比候选 1 长，且不能提前发现某一簇设计缺陷（如候选 1 中新发现的 R1 pyyaml 引导问题，若顺序实现到该簇时才发现，无法与其余两簇的返回并行，止损轮次消耗更集中）。

**选择理由**：本任务三簇文件域独立性强（P0-brief 本就按文件域分 Phase 1/2/3，且判定"仅测试关联，无代码顺序依赖"），候选 1 的并行拆批在实质维度（上下文体量、止损并行度）优于候选 2，且 R5 已确认唯一共享文件的并发写入风险可控（不同区域插入 + 收尾统一登记）。选定候选 1。

## 3. gate_commands（P2 固化，P4-P6 不得修改）

```yaml
gate_commands:
  P3: "python3 -m pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -v"
  P3_formatter: "pytest.sh"
  P5: "python3 -m pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -n auto -q --tb=no"
  P5_formatter: "pytest.sh"
  P5_timeout_seconds: 120
  P5_consistency: "python3 agate/scripts/check-protocol-consistency.py --strict-errors-only"
  P5_consistency_timeout_seconds: 60
  P5_shellcheck: "shellcheck -S warning agate/scripts/*.sh"
  P5_shellcheck_timeout_seconds: 60
  P5_offline_bundle: "python3 -m pytest agate/tests/regression/test_offline_bundle_roundtrip.py -q --tb=no"
  P5_offline_bundle_timeout_seconds: 90
  project_module: "agate"
```

**说明**：
- 四个 P5 系列 key（`P5`/`P5_consistency`/`P5_shellcheck`/`P5_offline_bundle`）各自独立声明，不用 `&&` 串联——遵循 dispatch-context 强制约束（DEBT0016/17/18 改 `check-gate.py` 本体，`P5_consistency` 若被 `P5` 失败短路会掩盖 consistency 层的真实结果）。
- `P5_consistency` **必须用 worktree 自己的 `check-protocol-consistency.py`**，不是 `~/.agate` 稳定版（HANDOFF-TAG0031.md §2/dogfooding 工作流铁律：稳定版只扫到主 checkout 的协议文件，扫不到 worktree 正在改的 `check-gate.py`）。
- `P5_offline_bundle` 单独一个 key 覆盖 BDD-2（离线包 pack→install→卸载全流程回归），测试内部用 `monkeypatch` 隔离 `HOME`/`AGATE_REPO_URL`（临时 `AGATE_HOME` 目录，非 `~/.agate`，对齐 P1 `verification_env` 声明）+ mock `subprocess.run`（git worktree add / pip download，同 `test_agate_pack_offline.py` 既有网络隔离手法，不联网）。
- `P5_timeout_seconds`/`P5_consistency_timeout_seconds`/`P5_shellcheck_timeout_seconds` 取值依据本 worktree 实测（2026-09-04，本机）：`pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -n auto -q --tb=no` 实测 34.63s（1412 passed, 2 skipped）；`check-protocol-consistency.py --strict-errors-only` 实测 1.057s；`shellcheck -S warning agate/scripts/*.sh` 实测 0.043s。三者均按「三档基准表」的"单元测试类 120s"档位就近取整（`consistency`/`shellcheck` 实测秒级，仍按同档 60s 留够 CI 机器变慢的余量，不采用更低档位——本仓无"构建类"以外场景适用更细分档位）；`P5_offline_bundle` 因涉及 `subprocess`/文件系统 IO mock 且是新写测试，给 90s（unit 类档位内上浮，覆盖 mock 开销与首次运行的不确定性）。
- **`P3` 不声明 `timeout_seconds`**：按 architect.md「`{key}_timeout_seconds` 字段规则」第 1 点，`P3` 继续走既有 `AGATE_TDD_TIMEOUT` 环境变量机制（默认 120s），`timeout_seconds` 字段只服务非 P3 key，不重复声明。
- 未声明 `P5_e2e`：`ui_affected: false`，无前端改动。

## 4. files_to_read（P4 实现导航，按簇归类）

```yaml
files_to_read:
  # 簇 A：版本管理域（DEBT0002/3/4）
  - path: agate/scripts/agate_common.py:1-36
    why: 已 import 的 hashlib/Path，compute_sha256 插入点紧邻其后
  - path: agate/scripts/agate_common.py:551-580
    why: resolve_workspace 定义（compute_sha256 建议插入位置：紧邻其后）
  - path: agate/scripts/agate-pack-offline.py:23-60
    why: compute_sha256 现有实现（迁移源 1），确认排序键 f.relative_to(p).as_posix() 必须原样保留
  - path: agate/scripts/install-offline.py:20-95
    why: compute_sha256 现有实现（迁移源 2）+ 顶部零依赖 import 现状（R1 引导设计的前提）
  - path: agate/scripts/install-offline.py:97-247
    why: verify_checksums/install_wheels/main 的执行顺序（R1 依赖此顺序设计 _ensure_agate_common）
  - path: agate/scripts/agate-install.py:1-63
    why: 模块 docstring（HOME 重定向测试隔离机制）+ agate_common 降级 fallback 写法参照
  - path: agate/scripts/agate-install.py:230-320
    why: _find_references 限流扫描 + _cmd_uninstall 消费点，WARNING 插入位置
  - path: agate/tests/unit/test_agate_pack_offline.py:1-60
    why: 网络隔离 mock 手法参照（subprocess.run mock，跨调用幂等）
  - path: agate/tests/unit/test_install_offline.py
    why: install_bundle/verify_checksums 既有单测覆盖现状，避免与新增用例重复
  - path: agate/UPGRADING.md:505-520
    why: DEBT0003 信任边界文档插入点（④ 新工具小节）
  - path: agate/scripts/README.md:60-80
    why: DEBT0003 信任边界文档插入点（install-offline.py 行）

  # 簇 B：测试隔离（DEBT0007，仅验证，不改代码）
  - path: agate/scripts/check-pruning.py:60-100
    why: _staged_source_count 现状实现（TAG0024 已修复，确认 cwd=task_dir 已生效）
  - path: agate/tests/unit/test_check_pruning.py:214-420
    why: BDD-6 涉及的 4 个既有回归用例现状（已带 GIT_CEILING_DIRECTORIES 隔离）

  # 簇 C：check-gate.py 健壮性（DEBT0016/17/18）
  - path: agate/scripts/check-gate.py:30-166
    why: agate_common import + 降级 stub 块，DEBT0018 sentinel 改造范围 + DEBT0016 需追加 resolve_workspace import
  - path: agate/scripts/check-gate.py:975-996
    why: gate_p4 CODE-MAP 路径推导（DEBT0016）+ 新增文件核对表判定（DEBT0017）
  - path: agate/scripts/check-gate.py:1074-1098
    why: gate_p6 count_p6_pass_fail 消费点（仅旧格式回退分支触达，见 R2）
  - path: agate/scripts/check-gate.py:1128-1245
    why: gate_p7 count_p7_markers + count_code_map_lines 两处消费点（同 R2 旧格式限制）
  - path: agate/scripts/agate_common.py:875-906
    why: extract_bdd_titles/parse_ui_design_section 的 re.MULTILINE 标题匹配写法参照（DEBT0017 沿用同款风格）
  - path: agate/tests/unit/test_check_gate.py
    why: 既有 gate_p1/p4/p6/p7 测试组织方式参照，新增用例插入位置

  # 共享
  - path: agate-workspace/debt/tech-debt.md:40-158
    why: DEBT0002/3/4 现状条目 + DEBT0005/6 closed 登记格式样例（status/closed_at/evidence 追加块）
  - path: agate-workspace/debt/tech-debt.md:568-700
    why: DEBT0007/16/17/18 现状条目全文（closure_criteria 逐条对照）
```

## 5. env_constraints

```yaml
env_constraints:
  debug_env: "系统 python3（/usr/bin/python3）跑 pytest/pyyaml；ruff 用 ~/.venvs/agate-dev/bin/ruff（本任务不改 ruff 相关规则，非必用）；consistency 必须用 worktree 自己的 check-protocol-consistency.py（非 ~/.agate 稳定版），见 §3 P5_consistency 说明"
  isolation_check: "离线包回归（P5_offline_bundle）用 pytest monkeypatch 隔离 HOME 到 tmp_path，构造临时 AGATE_HOME 目录（非 ~/.agate，避免污染稳定版）；agate-pack-offline.py/install-offline.py 的 git/pip 调用全程 mock subprocess.run，不联网、不实际 pip download（同 test_agate_pack_offline.py 既有网络隔离手法）"
  self_gate: "本任务改 agate/scripts/*（agate_common.py/agate-pack-offline.py/install-offline.py/agate-install.py/check-gate.py），触发 SELF-GATE，commit message 须含 self-gate-review: 或 self-gate-skip:（AGENTS.md/SELF-GATE.md）"
```

## 6. minimal_validation

```yaml
minimal_validation:
  assumption: "纯代码逻辑，无外部系统依赖（浏览器/网络/第三方服务）"
  method: "本任务全部依赖内部函数/数据转换的正确性，已在设计阶段逐一读代码确认（非纸面推演）：
    ① agate_common.resolve_workspace（L551-580）的 .agate.env 优先级解析逻辑已读取确认；
    ② agate_common.run_git（L50-64）的 OSError 兜底行为已确认（cwd 不存在时返回 (1, '')，
    支撑 DEBT0016 gate_p4 降级路径设计）；
    ③ install-offline.py 的 verify_checksums→install_wheels 执行顺序已逐行确认（L228→L237），
    据此发现并设计了 R1 的 pyyaml 引导方案（涉及删除/迁移 compute_sha256 这一‘请求会流向哪个兜底
    分支’的验证，按 architect.md 强制要求已完成）；
    ④ check-gate.py 的 count_p6_pass_fail/count_p7_markers/count_code_map_lines 三个消费点
    仅在旧格式回退分支触达（L1084/L1144/L1238 均在 if frontmatter字段为空 的 else 分支内）已逐行
    确认，据此在 R2 标注测试构造约束，避免 P3/P4 写出假绿测试；
    ⑤ tech-debt.md 的 DEBT0005/DEBT0006 closed 登记格式（status/closed_at/evidence 追加块）已
    读取作为 BDD-7/15 的格式依据。"
  result: confirmed
  note: "无需起服务/浏览器/网络验证。唯一接近‘外部系统行为’的是 pip install（DEBT0002 R1 引导
    方案），但验证手段是本地 --no-index --find-links 读取 bundle 自带 wheel（无网络请求，行为由
    pip 本地文件系统解析决定，非外部服务调用）；回归测试用 mock subprocess.run 隔离，不依赖真实
    pip 网络行为。"
```

## 7. 实现完成的标志

- 簇 A：`grep -rn "def compute_sha256" agate/scripts/*.py` 只命中 1 处（`agate_common.py`）；`pytest agate/tests/regression/test_offline_bundle_roundtrip.py` 通过；`agate-install.py uninstall` 在限流边界命中场景下 stderr 含 WARNING 关键字，未命中场景下无该 WARNING；`agate/UPGRADING.md`/`agate/scripts/README.md` 含"checksum 防损坏不防整包替换"字样。
- 簇 B：`pytest -k "test_p2_6e_prune_p7_coupling_checklist_exit_0 or test_p2_52_yaml_list_phases_exit_0 or test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0 or test_p2_6f_staged_source_count_uses_task_repo_not_outer_cwd_repo_exit_0"` 4 项全 PASS；`debt/tech-debt.md` DEBT0007 `status: closed`。
- 簇 C：`check-gate.py` 的 `gate_p4`/`gate_p1`/`gate_p6`/`gate_p7` 相关新增/修改测试全绿；全量 pytest（`P5`）无新增失败（BDD-13 逐字节不变）；`P5_consistency`/`P5_shellcheck` 0 ERROR/0 error。
- 收尾：`debt/tech-debt.md` 中 DEBT0002/3/4/16/17/18 均 `status: closed` + 新增 ≥2 条 open DEBT（BDD-14）；`P5` 全量绿 + `P5_consistency` 0 ERROR + `P5_shellcheck` 0 error + `P5_offline_bundle` 绿，四项均独立通过。
