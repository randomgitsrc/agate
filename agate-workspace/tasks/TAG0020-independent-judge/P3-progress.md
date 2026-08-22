# P3 测试设计进度（TAG0020-independent-judge）— agent: test-designer

> 分阶段落盘记录。最终产出 P3-test-cases.md（分工任务 A：只产用例映射文档，不写测试代码）。

## 2026-08-22 进度

### 步骤 1-2：dispatch-context + 角色定义已读
- P3-dispatch-context-test-designer.md（强制指令）：产出 P3-test-cases.md（紧凑表格格式，三列表，≤250 行），10 条 BDD 1:1 映射；test_code_dir 声明；BDD 分组（check-judge-verdict / check-events / agate_common+check-gate P6.5 / 文档断言类）；落盘节奏 = 写完立即追加 P3-progress.md 并返回。
- 角色定义 test-designer.md：BDD→测试 1:1；带 Examples 的 BDD 转参数化；测试名引用 BDD 编号；质量门槛（红灯、可追溯、二值判定）。

### 步骤 3：P1-requirements + P2-design 已读
- P1 10 条 BDD 权威语义（BDD-1 门槛 / BDD-2 历史跳过 / BDD-3 全验 criteria_total / BDD-4 白名单 / BDD-5 Header 字段 / BDD-6 证据交叉核对 / BDD-7 账本哈希链 / BDD-8 预算降级 / BDD-9 exit code 红线 / BDD-10 一致性回归）。
- P2-design §3.8 测试设计要点（权威测试分组）：test_check_judge_verdict.py（BDD-3/4/5/6/8/9）+ test_check_events.py（BDD-7/8）+ test_check_gate.py 增补（gate_p65：BDD-1/2/9/10）+ agate_common 写侧（append_event/read_judge_verdict）+ P3 gate 命令（§5 gate_commands.P3 只跑两个新文件）。
- 分组对照：dispatch 分组（BDD-1/4/5/9→check-judge-verdict 等）与 P2 §3.8 存在 BDD 编号归属差异（如 BDD-1 gate 层判定在 test_check_gate.py）——以 P2 §3.8 为主、dispatch 分组为参考，多重承载行（BDD-4/7/8/9/10）在映射表中注明双文件。

### 产出完成（2026-08-22）
- P3-test-cases.md 已产出（50 行，≤250 行约束满足）：Header 规格复制 + test_code_dir 声明（agate/tests/unit/）+ 测试资产分组概览（5 个测试文件）+ 三列映射表（10 条 BDD 每行一条，1:1 全覆盖，意图 ≤2 行）+ TDD 红灯/gate 说明 + BDD 覆盖对照（10/10）。
- 未写测试代码（分工边界）；测试代码路径与 P3 红灯命令已指向 agate/tests/unit/ 下两个新文件。
- [PROD_NOT_TOUCHED]：全程只写任务目录产出，未改协议本体。
### 2026-08-22 分工任务 B（测试代码）进度（agent: test-designer, revision B）
- 输入已读齐：dispatch-context（强制指令）+ test-designer 角色 + P3-test-cases.md（映射权威）+ P1-requirements（10 BDD）+ P2-design（§3.3/3.4/3.5 校验链 + §3.8 测试要点）+ 风格参考（test_check_pruning / test_check_p6_provenance / conftest）+ 既有 test_check_gate / test_agate_common / test_docs_assertions（增补落点）。
- 前置确认：worktree 无 check-judge-verdict.py / check-events.py（红灯 B 类）；check-gate.py 无 P6.5 handler（未知阶段 exit 2 → gate_p65 测试红）；agate_common 无 append_event/read_judge_verdict/GENESIS_HASH（ImportError 红）；协议文档无 P6.5 条文（文档断言红）；windows_smoke marker 已注册（pyproject.toml L17）。
- **test_check_judge_verdict.py**（新）：29 用例（BDD-1×2 / BDD-3×4 / BDD-4×8 / BDD-5×6 / BDD-6×5 / BDD-8×3 / BDD-9×1），含 2 个正向控制（全部 BDD 覆盖 exit 0 / budget_exhausted 合规 exit 0）+ AGATE_CARD/frontmatter 双排除不误报。已写入 agate/tests/unit/。
- **test_check_events.py**（新）：12 用例（BDD-7×10 / BDD-8×2：3 条 judge_verdict 事件 → exit 1、恰 2 条 → exit 0 边界），含 GENESIS_HASH 常量=sha256(b"") 断言、篡改中间行链断裂、真实行尾追加、未知事件类型不拦截。
- **test_check_gate.py 增补**：+6 用例（BDD-1×1 启用缺 verdict exit 1 / BDD-2×2 无 judge 字段与 enabled:false 早退 exit 0 / BDD-9×2 双脚本失败 exit 1 与全合规 exit 0 / BDD-10×1  judge 产物不干扰 gate_p6 exit 2 回归）。
- **test_agate_common.py 增补**：+5 用例（BDD-7 写侧×3：首行 GENESIS+ts、二次追加链续接、ts 单调兜底；BDD-5 读取侧×2：frontmatter 解析 dict / 缺失返回 None）。
- **test_docs_assertions.py 增补**：+8 用例（BDD-4×2：dispatch-prompt Judge 追加节 / dispatch-protocol 信息隔离节；BDD-8×2：judge.md 三档预算+partial / 账本 budget_exhausted 条文；BDD-10×4：WORKFLOW P6.5 行 / state-machine 挂载 / role-system 名册+status 映射 / AGENTS 角色清单 + P6 卡门槛）。

### 红灯确认（2026-08-22，代码批）
- 全 5 文件写完，自跑红灯（/usr/bin/python3 -m pytest，--basetemp 可写 scratch，用后清理）：
- ① 新文件 test_check_judge_verdict.py + test_check_events.py：41/41 全红（rc=2 = check-judge-verdict.py/check-events.py 未实现 → 'can't open file'，真实 B 类红灯；无 SyntaxError/收集错误）。
- ② 增补 test_check_gate.py(+5 红) / test_agate_common.py(+5 红，ImportError 驱动) / test_docs_assertions.py(+8 红，AssertionError)：19 个新用例全红；既有 176 用例全绿零回归（含 BDD-10 gate_p6 守卫 test_bdd_10_gate_p6_unaffected_by_judge_artifacts_exit_2 保持绿 = 回归锚正确，同时实证 R6 假设：P6.5-* 文件不干扰 gate_p6）。
- 新用例合计 60（29+12+6+5+8），59 红 + 1 绿（回归守卫）。
- 平台扫描自查：已去除头注释中 /tmp 字面（R4 无注释豁免，TAG0019 教训）；解释器一律 python_exe fixture；5 个 -c 片段经 stub agate_common 验证语法与断言自洽（输出逐行匹配）。
- [PROD_NOT_TOUCHED]：只写/只改 5 个测试文件，未触碰被测模块与协议文档。
