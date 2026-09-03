# P0-brief — TAG0029 gate 命令解析器修复批（RM-AG0056 + DEBT0023/0027）

> 本文件由主 Agent 亲自填写（P0 阶段产出）。来源：TAG0028 复盘（DEBT0027/RM-AG0056）+ TAG0026 评审（DEBT0023）。
> 三处同源指向 `agate-read-gate-commands.py` 解析器 + `check-tdd-red.py` judge 分支——**强合并单 task**（拆开并行必冲突）。

## task

"修复 gate 命令解析器与 TDD 红灯判定的三个关联缺口：① **DEBT0027（high）**——`agate-read-gate-commands.py` 值清洗 `strip(chr(34)).strip(chr(39))` 不剥离值内 `# 注释` 与残留引号（值不以引号结尾时只剥开头引号，残留结尾引号+注释尾巴），消费方 `bash -c` 执行 unterminated quote 语法错误（exit 2），`check-tdd-red` judge 分支可能把该输出误判为红灯可推进（**假绿灯：测试根本没跑却被当红灯证据放行，验收真实性受威胁**）；② **RM-AG0056**——平台假设扫描器（R2 规则 `(^|[\s=(\'\"])python3([\s]|$)`）静态扫描无法区分'测试代码里的命令调用'（应禁止裸 python3）与'fixture 模拟平台日志的数据面内容'（command 字段模拟真实日志本应含 `python3 -m pytest`），cmdstream fixture 17 处裸 python3 被命中破坏 TAG0011 bdd-8「tests 树 0 命中」，P5 全量 pytest 红灯回 P4 fix3 才闭环；且扫描器不在 P3/P4 gate_commands 常驻面，回归到 P5 全量才暴露；③ **DEBT0023（low）**——`agate-read-gate-commands.py` 收集侧 `key.startswith('P3')` 把所有 P3* 非元键静默收集为 TDD 测试命令执行，`is_gate_meta_key` 只精确匹配 `_formatter/_timeout_seconds` 后缀，P3_xxx 不被豁免，协议层无机械防护（TAG0026 靠'禁用 P3_xxx 键'约定规避）。"

### scope

- **Phase 1（解析器值清洗 + 假绿灯修复，DEBT0027）**：`agate-read-gate-commands.py` 值清洗剥离行内注释（首个未转义 ` #`）并校验引号闭合——输出纯命令或报解析错误（exit 非 0 + stderr），不再产出带残渣命令串；`check-tdd-red.py` 的 `run_test_with_formatter` 执行失败（exit 127 / 语法错误 exit 2 / 命令不可解析）不得计入红灯证据，judge 分支仅在测试运行器正常退出时才判定红灯可推进（关联 A/B 类盲区语义，扩展覆盖语法错误类）
- **Phase 2（P3* 键收集收紧，DEBT0023）**：`agate-read-gate-commands.py` 收集侧收紧（P3 仅精确键 + 白名单后缀）或 `is_gate_meta_key` 扩展协议级辅助键约定；P2 卡 gate_commands 节写明 P3_xxx 键禁止声明及其原因；补 read-gate-commands 单测锁定收集行为
- **Phase 3（平台假设扫描器数据面豁免 + 常驻面，RM-AG0056）**：R2 规则扫描区分代码面与 fixture 数据面（fixture 目录/文件声明豁免机制）；扫描器纳入 P3/P4 gate_commands 常驻面（回归不再等到 P5 全量）；cmdsream fixture 17 处裸 python3 恢复真实日志形态
- **测试**：`agate/tests/` 新增 pytest——带行内注释 gate_commands 解析出纯命令 + `bash -c` 执行不报 unterminated quote（DEBT0027 closure ①）；check-tdd-red 对语法错误判 exit 1（A 类）不再误判红灯（closure ②）；read-gate-commands P3* 键收集行为锁定（DEBT0023 closure）；R2 扫描器对 fixture 数据面豁免（RM-AG0056 closure）

### out-of-scope

- `check-gate.py` 其余健壮性缺口（DEBT0016/17/18——归 TAG0031）
- 平台假设扫描器的规则语义扩展（本次只做数据面豁免 + 常驻面，不改 R2 规则本体判定逻辑之外的扫描面）
- cmdstream 检测引擎本体（RM-AG0055 已交付，不动）
- TAG0011 bdd-8「tests 树 0 命中」测试本身的语义调整（回归保持绿即可，不改其断言意图）

## known_risks

- "同类/影响面预判：`agate-read-gate-commands.py` 是 P2/P3/P5 gate 消费链共享解析器（check-tdd-red / check-gate 都 import），收紧收集侧须先 grep 全部消费方，确认 P3 精确键 + 白名单后缀不会漏掉合法用法（如 P3_e2e / P3_formatter / P3_timeout_seconds 属元键豁免）"
- "DEBT0027 假绿灯是验收真实性风险（high）：修复 check-tdd-red judge 分支时须先补'语法错误 → exit 1'失败测试确认红（TDD），再改实现——语义修正类修复必须先补真实场景测试（TAG0027 复盘教训）"
- "RM-AG0056 fixture 豁免机制须防矫枉过正：豁免不能做成'含 fixture 字样就跳过'的宽匹配（会被真代码借用豁免），须绑定 fixture 目录/文件声明 + 单测锁定"
- "扫描器纳入 P3/P4 常驻面是行为变更：新 CHECK 上线前先全量扫描确认存量零命中（DEBT0025 流程，本任务 Phase 3 落地时同步执行）——若存量有命中，先登记清单再启"

## env_constraints

- 本任务改 `agate/scripts/*`（agate-read-gate-commands.py / check-tdd-red.py / 平台假设扫描器）+ `agate/phase-cards/P2-design.md`（gate_commands 节 P3_xxx 禁止声明）→ **触发 SELF-GATE**，commit message 须含 `self-gate-review:` 或 `self-gate-skip:`
- 用系统 python（`/usr/bin/python3`）跑 pytest/pyyaml；ruff 用 `~/.venvs/agate-dev/bin/ruff`
- 基线验证用 `--strict-errors-only`（DEBT0012）；编排/派发类工具用 `~/.agate` 稳定版，不用 worktree 相对路径（TAG0016 教训）
- 关联 DEBT0025 流程（新 CHECK 上线前全量扫描）：本任务 Phase 3 若新增扫描面，先扫存量再启用

## executor_env

- worktree：`.worktrees/agate-TAG0029`（分支 `feat/TAG0029-gate-parser-fix`），构建流程见 `docs/guides/worktree-dogfooding-guide.md`，交接单 `HANDOFF-TAG0029.md` 按模板全 9 节填写
- 任务目录：`agate-workspace/tasks/TAG0029-gate-parser-fix/`
- **merge 模式**：完成 PR 后 worktree 自行 git-to-main（三路并行 TAG0029/30/31，文件域已隔离互不冲突；PR 提出后主 Agent review 复核）
