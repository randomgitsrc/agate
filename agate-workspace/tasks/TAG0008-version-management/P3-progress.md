## test-designer offline

### 输入文件读取
- [x] P3-dispatch-context-test-designer-offline.md（批次 offline：BDD-22~29；1:1 BDD 映射；测试落 worktree `agate/tests/unit/`；不实际联网/pip download；每文件第 1 用例 windows_smoke；红灯须 B 类）
- [x] ~/.agate/assets/execution-roles/test-designer.md（1:1 BDD→测试；带 Examples 表参数化；P3 红灯须真失败）
- [x] P1-requirements.md BDD-22~29（pack-offline bundle+manifest / manifest 字段 / 失败路径非0不产坏包 / install-offline 平台核对 / checksum 校验 / wheels 离线安装 / 版本目录+hook+验证 / --skip 勾选）+ I-8/9/10
- [x] P2-design.md §4.7（pack-offline 流程 + 3 失败路径；install-offline 流程 + 平台核对 + checksum + wheels + 建版本目录 + hook 指向 + 勾选）、§3.2 gate_commands（P5 全量 `pytest -q --tb=no`）、§7 MV（pip download --platform 可行 / sha256 hashlib 标准库）、§8.3 批次依赖（offline 依赖 resolve-chain 的 agate_common）
- [x] P0-brief.md（内网离线部署包：外网打包器 + 内网一键安装器 + 勾选 + checksum 校验；git 不打包；平台维度按目标平台拉取；与在线模式共用 agate-resolve/hook 逻辑）
- [x] AGENTS.md 项目约定（dogfooding 双工作区纪律；测试平台无关原则：禁裸 python3 / 禁裸 /tmp / 禁假设 POSIX symlink 语义）
- [x] conftest.py fixtures（agate_root / agate_scripts / python_exe / run_cli / task_dir / git_repo / tmp_path）
- [x] test_install_hook.py 参照（run_cli + python_exe 模式；AGATE_HOOK_COPY_MODE=1 复制模式；os.readlink 平台分支断言）
- [x] check-tdd-red.py + pytest.sh formatter（B 类判定：import_errors >0 且无 syntax → exit 0；errors>0 无 import → exit 1 A 类 → 测试必须走"模块不存在 → ModuleNotFoundError"路径，不能用 subprocess FileNotFoundError）
- [x] 查证：`agate/scripts/agate-pack-offline.py` / `install-offline.py` 均不存在（只有 install-hook.py）→ 被测模块未实现，B 类红灯成立

### 关键设计决策
1. **加载方式**：测试用 `importlib.util.spec_from_file_location` 从 `agate_scripts/` 加载脚本为模块；文件不存在 → helper 抛 `ModuleNotFoundError`（"被测模块未实现"），走 B 类判定（import_errors 匹配 ModuleNotFoundError → check-tdd-red exit 0）。不用 subprocess（FileNotFoundError 归为 A 类）。
2. **契约接口**（P3-test-cases-offline.md 明示给 P4）：
   - agate_pack_offline：compute_sha256 / build_manifest / pack_offline / PackOfflineError / main
   - install_offline：load_manifest / check_platform / verify_checksums / install_wheels / install_bundle / main
3. **网络/pip 隔离**：pip download / pip install / git checkout 全部 `unittest.mock.patch` 掉；checksum 用真实 hashlib 算 tmp_path 小文件；平台核对/checksum 校验纯逻辑直接测。
4. **平台无关**：hook 指向断言平台分支（Linux os.readlink 软链 / Windows is_file + .agate-root 标记）；AGATE_HOOK_COPY_MODE=1 模拟复制模式。
5. **观察**：P2 §3.2 gate_commands.P5_unit 未含 offline 两个测试文件（可能遗漏），但 P5 全量命令 `pytest -q --tb=no` 会覆盖；不在本批修改 P2（gate_commands 已固化）。
## test-designer resolve

- [x] 读 dispatch-context-test-designer-resolve.md（派发指引：本批 BDD-9~14/15~19/20/21/30/31，只写 3 个新测试文件，复用既有模式）
- [x] 读 test-designer.md 角色定义
- [x] 读 P1-requirements.md（BDD-9~21/30/31 细节 + I-1~I-6 + 影响面 2.3）
- [x] 读 P2-design.md（§4.1 四层解析 / §4.2 .agate-version 语法 / §4.3 resolve-entry / §4.4 归口 / §4.6 summary）
- [x] 读 P0-brief.md（形态/已知风险/env_constraints）
- [x] 读 P2-review.md（决策点 2/3 + 测试缺口 1/5：resolve 完全失败 fail-closed 终态、BDD-31 非 pytest）
- [x] 读既有参照 test_install_hook.py（_make_fake_root / AGATE_HOOK_COPY_MODE=1 / os.readlink 平台分支）+ conftest.py（run_cli/git_repo/agate_scripts/python_exe）
- [x] 读 agate_common.py（resolve_agate_root L76-94 现有语义）、install-hook.py、pre-commit-gate.sh、agate-summary.py（当前 git describe 语义）

### 测试设计要点
- resolve 测试经 run_cli 调 agate_scripts/agate-resolve.py（不存在 → B 类红灯）
- resolve-entry 测试经 run_cli 调 agate_scripts/resolve-entry.py + gate-name 参数（不存在 → B 类红灯）
- 假 HOME 布局：HOME+USERPROFILE 指向 tmp_path 假 home，~/.agate = home/.agate；current/latest 用文本指针（平台无关，Windows-safe）
- P2-review 测试缺口 1 → test_resolve_terminal_failure_fail_closed（无 current/latest/legacy 终态 exit 非 0）
- P2-review 测试缺口 5 → BDD-31 非 pytest 验证（P7 + git log diff），测试用例文档中注明

## test-designer install

### 输入读取
- [x] P3-dispatch-context-test-designer-install.md：批次 install（BDD-1~8），测试文件 test_agate_version_install.py，test_code_dir: agate/tests/unit/
- [x] ~/.agate/assets/execution-roles/test-designer.md：1:1 BDD 映射，测试名引用 BDD 编号，红灯必须
- [x] P1-requirements.md：BDD-1~8 读毕（无参 latest 指针/指定版本 worktree/幂等/current↔latest/卸载+引用保护/--check 分平台）
- [x] P2-design.md §4.5：agate-install 方案（repo 单克隆 + worktree add / 幂等预判 / uninstall 引用保护 + 指针清理 / --check 分平台指引）
- [x] P0-brief.md：环境约束（Linux 实测 + Windows CI 冒烟；不装系统级依赖）
- [x] conftest.py：agate_root / python_exe / run_cli / git_repo / py_path / tmp_path fixture 确认
- [x] 查证：agate-install.py 不存在于 worktree agate/scripts/；系统 python3 有 pytest 9.0.3 + pyyaml；git 2.43 可用

### 测试设计决策
- 接口契约：agate-install.py 支持无参 / <version> / --uninstall <version> / --check；repo 来源用 AGATE_REPO_URL env（P4 实现须支持，测试用它指向本地临时 repo）；HOME env 重定向 ~ 到 tmp_path 防触碰真实 ~/.agate
- BDD-8 pyyaml mock：临时 venv（python -m venv，无 pyyaml）放 PATH 首位——对应"环境缺 pyyaml"（子进程 probe_python 式探测会被拦截；in-process import yaml 也拦不住 venv 内无 yaml）
- 指针断言：_resolve_pointer helper 兼容 POSIX 软链 / Windows 文本指针 / current→latest 链
- windows_smoke：BDD-1（首用例）+ BDD-5/7/8（平台敏感代表）
### 产出 1/2
- [x] P3-test-cases-install.md 已落盘（BDD-1~8 映射表 + 接口契约 + 平台分支 + 红灯预期；test_code_dir: agate/tests/unit/）
- [x] 产出 P3-test-cases-resolve.md（BDD 1:1 映射 + test_code_dir: agate/tests/unit/ + Given 契约 + 红灯确认）
- [x] 产出 3 个测试文件（resolve=8 / summary=2 / hook=5，共 15 函数）
- [x] P2-review 测试缺口 1 落地：test_resolve_terminal_failure_fail_closed（终态 exit 非 0 + 警告不静默）
- [x] BDD-31 决策：非 pytest 验证（P7 + git log diff），P2-review 缺口 5 引用，测试用例文档登记
- [x] BDD-14 参数化三变体（random text / foo: bar / 空文件）
- [ ] 自跑测试确认红灯 → 下一步
- [x] 自跑测试确认红灯：17 failed（B 类），0.48s
  - resolve CLI 类：returncode 2 + "can't open file agate-resolve.py"（模块缺失，B 类）✓
  - summary：旧 git-describe 输出（v0.49.0/main），断言项目解析版本失败（语义未迁移，B 类）✓
  - BDD-15：薄壳 exec 行不含 resolve-entry.py（未改造，B 类）✓
  - BDD-19：复制模式 hook 链走到 GATE ERROR fail-closed（resolve-entry 缺失，B 类）✓
  - 终态用例：失败断言 "v0.99.0" in output（模块缺失故不出现，B 类；P4 后警告应含版本号）✓
  - 无 A 类（无 SyntaxError / fixture 错误 / 断言与 fixture 矛盾）
### 产出 2/2 + 自跑结果
- [x] test_agate_version_install.py 已落盘（8 用例：test_bdd_1~8，名称引用 BDD 编号；windows_smoke 4 处：bdd_1/5/7/8）
- [x] 自跑 `python3 -m pytest agate/tests/unit/test_agate_version_install.py -q --tb=no` → **8 failed**（全红）
- [x] 红灯原因核实为 B 类：agate-install.py 不存在 → run_cli 子进程 returncode=2（python: can't open file）→ 断言失败（如 bdd_2 `assert 2 == 0`），非测试代码 bug
- [x] ruff check 通过（0 错误）
- [x] 未跑全量测试（dispatch 约束 8）；未修改任何功能代码/~/agate/主 checkout

### self-run（2026-08-16，红灯确认）
- 命令：`timeout 90 python3 -m pytest agate/tests/unit/test_agate_pack_offline.py agate/tests/unit/test_install_offline.py -q --tb=short`
- 结果：**11 failed（全部红灯）**，全因 `ModuleNotFoundError: No module named 'agate_pack_offline'/'agate_install_offline' (被测模块未实现: ...)` = B 类（被测模块未实现，非断言矛盾/语法错误）
- check-tdd-red 复现：`TEST_RUNNER="python3 -m pytest <两文件> -q --tb=no" check-tdd-red.py` → **exit 0（红灯可推进）**
- ⚠️ 发现：TAG0008 gate_commands.P3=`python3 -m pytest`（无 P3_formatter、无 --tb=no）时，任何 pytest 红灯输出都含 Traceback → check-tdd-red line 110 判定 A 类（exit 1 拒绝）。**主 Agent 须以 `TEST_RUNNER="python3 -m pytest <批测试文件> -q --tb=no"` 方式跑 check-tdd-red**（与 P3 卡片"不提供 formatter 时退化为 exit-code-only"的既有语义有出入，实测 --tb=no 下走 classic-red → exit 0）。已在本摘要返回给主 Agent。

### 最终自检（2026-08-16）
- 落盘确认：3 个产出文件均存在（P3-test-cases-offline.md / test_agate_pack_offline.py 174 行 / test_install_offline.py 192 行）
- 红灯复跑：`python3 -m pytest <两文件> -q --tb=no` → **11 failed**，全部 B 类（被测模块未实现）
- ruff：两文件 0 error
- P3 自检：无"断言与测试数据矛盾"类失败（全部失败原因 = ModuleNotFoundError 被测模块未实现）
- 平台无关：无裸 python3（测试代码）；无裸 /tmp（tmp_path）；symlink 平台分支断言；每文件第 1 用例 windows_smoke；AGATE_HOOK_COPY_MODE=1 复制模式用例
- [PROD_NOT_TOUCHED] 未接触生产环境 / 未改功能代码 / ~/.agate 与主 checkout 未动
