---
phase: P4
task_id: TAG0031
parent: P4-implementation.md
trace_id: TAG0031-P4-review-20260904
agent: review
created: 2026-09-04
status: approved
---

# P4-review.md — TAG0031「DEBT 存量修复批」独立评审（review 角色，agent≠main）

评审范围：`git diff HEAD` 覆盖的 8 个文件（`agate_common.py`/`agate-pack-offline.py`/
`install-offline.py`/`agate-install.py`/`check-gate.py`/`UPGRADING.md`/`scripts/README.md`/
`agate-workspace/debt/tech-debt.md`）。逐条核实 dispatch-context 派发的 7 项重点复核项，
均已读实际代码 diff + 自跑全量测试独立复核（未仅采信 P4-implementation 系列的文字描述）。

## 重点复核项 1：R1 pyyaml checksum 前置校验实现是否真的落地

已读 `agate/scripts/install-offline.py` 实际 diff（`git diff HEAD -- agate/scripts/install-offline.py`），
核实 `_ensure_agate_common(bundle_dir, manifest)`（L101-142）的执行顺序：

```
try: import yaml
except ImportError:
    wheel_path = Path(bundle_dir) / pyyaml_comp.get("path", "")
    actual = hashlib.sha256(wheel_path.read_bytes()).hexdigest()      # L127
    if actual != pyyaml_comp.get("sha256"):                          # L132
        stderr 报错 + return None                                    # 不执行 pip install
    subprocess.run(["pip", "install", "--no-index", ...])            # L136-140，校验通过后才执行
import agate_common
return agate_common
```

内联 checksum 比对（`hashlib.sha256(wheel_path...)`）在代码物理位置和执行路径上都严格先于
`subprocess.run(["pip", "install", ...])` 调用——校验不匹配的分支直接 `return None`，函数在
到达 `pip install` 语句之前就已退出，不存在"先装后查"的顺序缺口。`verify_checksums()`
（L153-172）调用 `_ensure_agate_common` 失败时 `raise RuntimeError`，`main()`（L284-291）
捕获并 `return 1`，未静默吞掉引导失败。

与 P2-design.md §1.3 R1 的缓解设计逐条对照一致（内联单文件 hash、非 `compute_sha256` 的
另一份实现、不违反 BDD-1「全仓仅 1 处定义」）。判定：**落地属实，非仅文字声称**。

## 重点复核项 2：DEBT0018 fail-closed 是否严格遵循 P2 R2 风险声明

已读 `check-gate.py` 全部 4 个消费点的实际代码上下文（非仅读 diff 摘要）：

- `gate_p6`（L1129-1139）：`_reader_missing(count_p6_pass_fail)` 检查位于 `else:`
  分支内（`pass_fm != "" and fail_fm != ""` 为假时的旧格式回退分支），新格式（frontmatter
  已声明 `pass`/`fail`）时该分支不会执行，`_reader_missing` 检查也不会触达——与 R2 一致。
- `gate_p7` BLOCKER/DEVIATION 计数（L1195-1206）：同样在 `else:` 旧格式回退分支内
  （`blocker_fm != "" and devcrit_fm != ""` 为假时才触达）——与 R2 一致。
- `gate_p7` CODE-MAP 转抄核对（L1283-1307）：核实与前两者**方向相反**——`_reader_missing
  (count_code_map_lines)` 检查位于 `if cm_count_fm != "" and cm_reviewed_fm != "":`
  内部（字段**已声明**才会执行该分支），逐行读取确认无误——与 R2「注意与前三者相反」的
  声明一致，未见误伤新格式主路径的迹象。

回归守卫复核：`test_tag0031_bdd_13_gate_p6_p7_new_format_unaffected_regression` 独立重跑
**PASSED**（新格式路径判定逐字节不变，不受 fail-closed 改造影响）；4 个 BDD-12 子用例
（`test_tag0031_bdd_12_gate_p1_read_rules_yaml_missing_fail_closed` /
`..._gate_p6_count_pass_fail_missing_fail_closed` / `..._gate_p7_count_markers_missing_fail_closed`
/ `..._gate_p7_count_code_map_lines_missing_fail_closed`）逐一独立重跑均 **PASSED**。

补充核实 `_reader_missing` 的判据设计（L228-238，`getattr(fn, "__module__", None) !=
"agate_common"`）：读 BDD-12 四个测试用例的 mock 手法（如
`mod.read_rules_yaml = lambda rules_root, name: None`），确认是直接替换模块属性为 lambda
（`__module__` 为测试模块名，非 `"agate_common"`），与 ImportError 降级 stub（定义在
check-gate.py 内，`__module__` 同样非 `"agate_common"`）享有相同的可检测路径，判据设计自洽，
无绕过风险。判定：**实现方向与 R2 声明完全一致，无误伤新格式主路径**。

## 重点复核项 3：DEBT0004 的 `_find_references` 返回二元组改造是否影响所有调用方

`grep -rn "_find_references" agate/ --include="*.py"` 全仓核实，生产代码内唯一调用点为
`agate-install.py:295`（`_cmd_uninstall`）：

```python
refs, hit_limit = _find_references(os.path.expanduser("~"), version)
```

已正确解包为二元组，且紧接的 `if hit_limit:` WARNING 输出（L296-300）置于 `if refs:`
拒绝卸载判定（L301）**之前**，符合 P2-design §1.1 簇 A「不论 refs 是否为空都要提示」的要求。
其余命中（`test_agate_install_uninstall.py`/`test_offline_bundle_roundtrip.py`）均为测试文件，
非生产调用方。判定：**无遗漏的旧调用点，无解包成单值导致运行时错误的风险**。

## 重点复核项 4：debt/tech-debt.md 登记闭合质量

已读 7 条 closed 条目（DEBT0002/3/4/7/16/17/18）全文与 2 条新登记（DEBT0028/29）全文：

- 7 条 closure evidence 均引用具体测试函数名（如 `test_bdd_1_compute_sha256_*` /
  `test_bdd_2_pack_install_uninstall_roundtrip_no_behavior_change` /
  `test_bdd_4_find_references_and_uninstall_warn_when_scan_limit_hit` /
  `test_tag0031_bdd_8_gate_p4_code_map_uses_resolve_workspace` 等）或具体 commit
  （`e2357fc`），未见"已修复""已完成"这类空泛表述——已抽样重跑其中数条独立确认为 PASSED
  （见「全量测试自行复核」节），非仅采信文字声称。
- DEBT0028/DEBT0029 编号顺延核实：`grep -c "^## DEBT" agate-workspace/debt/tech-debt.md`
  显示登记至 DEBT0029 为最大编号，此前最大编号为 DEBT0027（DEBT0028/29 之前无跳号），
  两条新条目 `evidence`/`impact`/`recommendation`/`closure_criteria`/`source`/`created_at`
  /`task_id` 字段齐全，`status: open` 与「本次不处理，转入登记」的判定一致。
  DEBT0029 正文对风险高于 DEBT0017 本体（触发 `return 1` 阻断性）做了加粗提示，避免被误认为
  已随 DEBT0017 一并修复——登记质量符合预期。

判定：**登记闭合质量合格，具体依据充分**。

## 重点复核项 5：两处已修复的意外回归是否真的修复到位

- **encoding 守卫引号风格**（P3-gate-diagnosis.md）：`grep -n "'rb'"
  agate/tests/unit/test_agate_common.py` 确认工作区内已无单引号 `'rb'` 残留；独立重跑
  `test_bdd_5_all_test_py_text_io_explicit_encoding` **PASSED**。
- **ruff import 排序**（P4-gate-diagnosis.md）：读 `install-offline.py` 当前 diff 确认
  `import yaml as _yaml_probe` 与 `import agate_common as _agate_common_probe` 之间已有空行
  分隔；独立重跑 `test_bdd_34_shellcheck_three_hook_shells_and_ruff` **PASSED**；
  `~/.venvs/agate-dev/bin/ruff check agate/scripts/` 独立执行 **All checks passed!**。

判定：**两处均已修复到位，未引入新问题**（已被本次全量测试复核一并覆盖，无残留回归）。

## 重点复核项 6：maintainability 检查

独立执行 `python3 agate/scripts/check-maintainability.py agate-workspace/tasks/TAG0031-debt-cleanup`：

```
god_file_count: 0
fuzzy_boundary_count: 0
```

exit 0，无 violations，`known-violations.md` 核对（RM-AG0046）不适用（violations 为空时不构成
approve 前置条件）。判定：**属实**。

## 重点复核项 7：ruff noqa 语法警告是否值得要求顺手清理

`agate-pack-offline.py:30` 的 `from agate_common import compute_sha256  # noqa: E402
TAG0031 DEBT0002：共享单实现`——独立复核：默认 `ruff check`（带缓存）不显示该警告，
`ruff check --no-cache agate/scripts/agate-pack-offline.py` 才能复现：

```
warning: Invalid `# noqa` directive on agate/scripts/agate-pack-offline.py:30: expected code
to consist of uppercase letters followed by digits only (e.g. `F401`)
All checks passed!
```

exit code 仍为 0（`All checks passed!`），不阻断任何 gate；根因是 `# noqa: E402  TAG0031
DEBT0002：共享单实现` 把中文说明文字直接追加在 noqa 指令同一段注释里，ruff 把整个尾巴当作
"noqa code" 解析失败，回退为普通不限定 noqa（仍生效，只是多一条 info 级 lint 自身的警告）。

**评审意见（非阻断，供后续顺手清理，不写入本次 approve 门槛）**：建议把中文说明移到独立注释行，
即：

```python
# TAG0031 DEBT0002：共享单实现
from agate_common import compute_sha256  # noqa: E402
```

改动量 1 行拆分，纯格式修正，不改变导入语义。因不影响 exit code、不影响任何 BDD 验收，
按处理规则本条只记录"怎么改"，不构成 approved/rejected 判定依据，可留给后续任务顺手处理或本任务
下一轮迭代顺带修一下。

## 全量测试自行复核（本次 review 独立执行，非采信 P4-implementation.md 声称）

```bash
timeout 200s python3 -m pytest agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ -n auto -q --tb=short
```
结果：**1435 passed, 2 skipped**（与 P4-implementation.md 声称一致，独立复核确认非虚报）。

```bash
timeout 60s python3 agate/scripts/check-protocol-consistency.py --strict-errors-only
```
结果：**0 ERROR**（329 个既有 WARNING，均为历史遗留叙事文件死链，与本任务改动无关）。

```bash
timeout 30s shellcheck -S warning agate/scripts/*.sh
```
结果：**0 输出**（exit 0）。

```bash
timeout 30s ~/.venvs/agate-dev/bin/ruff check agate/scripts/
```
结果：**All checks passed!**（重点复核项 7 的 noqa info 需 `--no-cache` 才显现，默认调用不可见，
不影响本命令的 exit code）。

补充独立重跑（不依赖全量套件聚合结果，逐条锁定关键测试）：
`test_tag0031_bdd_15_six_debts_registry_closed` PASSED；
`test_bdd_7_debt0007_status_closed_with_closure_fields` PASSED；
`test_bdd_2_pack_install_uninstall_roundtrip_no_behavior_change`（`P5_offline_bundle` 对应测试）
PASSED；`test_tag0031_bdd_11_gate_p4_real_heading_trailing_text_satisfied` PASSED。

## Pass 1（CRITICAL）— 数据安全与正确性

未发现 SQL 注入/字符串拼接进查询（本次改动无数据库交互）、未发现 read-check-write 无约束竞态
（`_ensure_agate_common` 的 checksum-then-pip-install 是单进程顺序执行，非并发共享状态）、未发现
enum/状态值新增后消费方遗漏（DEBT0018 的 4 个消费点已逐一核实覆盖）、未发现 LLM 生成数据未校验
写库（本次改动不涉及 LLM 输出落库）、未发现 TOCTOU（`_ensure_agate_common` 内 checksum 校验与
`pip install` 之间不存在文件被替换的中间态窗口——bundle 目录在安装流程内不会被并发修改，且
`verify_checksums()` 后续会对全部组件包括 pyyaml 再次校验一遍）。**Pass 1 无 CRITICAL 发现**。

## Pass 2（INFORMATIONAL）— 代码健康

- 重点复核项 7 已列出的 ruff noqa 语法警告（INFORMATIONAL，非阻断，见上）。
- 未发现 Python async/sync 混用阻塞 event loop（本次改动脚本均为同步 CLI 工具）。
- 未发现字段/列名变更后消费方未同步更新（`_find_references` 二元组改造的唯一消费方已核实）。
- 未发现 N+1 查询/缺索引/O(n²) 算法新增（`compute_sha256` 目录遍历排序逻辑与迁移前完全一致，
  非本次新增复杂度）。
- 未发现新增资源泄漏/错误被吞：`_ensure_agate_common` 的三个失败分支（manifest 缺 pyyaml 组件 /
  读取 wheel 失败 / checksum 不匹配 / pip install 失败）均有对应 `sys.stderr.write` 提示，未静默
  吞错；`verify_checksums` 引导失败改 `raise RuntimeError`，`main()` 显式捕获处理，非裸吞异常。

前端专项：本次改动 `domains: [backend]`，`ui_affected: false`（P2-design.md frontmatter），
未涉及前端文件，前端专项检查项不适用。

## 结论

7 项重点复核项逐条核实通过，全量测试/consistency/shellcheck/ruff 独立复核结果与
P4-implementation.md 声称一致（非虚报），Pass 1 无 CRITICAL，Pass 2 仅 1 项 INFORMATIONAL
（ruff noqa 语法警告，非阻断，已给出具体修改建议，供后续顺手处理，不构成本次门槛）。

**结论：approved**
