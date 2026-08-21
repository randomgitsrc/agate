---
phase: P3
task_id: TAG0018
type: test-design
parent: P2-design.md
trace_id: TAG0018-P3-20260821
status: draft
agent: test-designer
test_code_dir: agate/tests/unit/test_dsh_preset.py
---

# P3 测试设计 — TAG0018 agate 原生支持 DSH 平台（TDD 红灯测试先行）

> 一句话摘要：在 5 用例基线（BDD-15 下限）上扩展为 **8 个用例**——新增 BDD-3 persona 薄身份两判据、BDD-7 位置判据（步骤 2 区内）、BDD-9 install-hook.py 调用串三个用例（吸收 P2-review 非阻塞建议 1/2，必做测试增强），并强化用例 6 为 BDD-8 精确命令串断言（P2-design R-1 缓解要求）。当前 8/8 全红（TAG0018 交付物未落位），全部为 B 类红灯（实现缺失）。

## 0. 定位与计数

- **TDD 测试先行**：测试代码先于 P4 实现落位；当前 worktree 中 `assets/templates/dsh/` 不存在、SETUP.md 无任何 DSH 引用——测试必须全红，且失败原因是"实现缺失"而非语法错误。
- **用例数影响**：worktree 基线 1030 → 1030 + 8 = **1038**（只增不减，满足 P2-design §5 P5_count 判据 ≥1030）。派发指引中「新增后 ~1035」为估算值（5 基线 + 3 新增 = 8 文件级用例），硬判据是只增不减。
- **测试代码路径**：`agate/tests/unit/test_dsh_preset.py`（相对 worktree 根；P2-design §5 gate_commands 执行 cwd = worktree 根）。

## 1. 用例清单（8 用例 × BDD 映射 × 红灯预期）

| # | 测试函数 | BDD | 断言要点 | 当前红灯原因（TAG0018 未落位） | 红灯类型 |
|---|---------|-----|---------|------------------------------|---------|
| 1 | `test_dsh_agent_cordis_rows_have_id_and_name` | BDD-1 | 顶层行列表，每行非空 `id`/`name`；`_js_loader` 容忍 `!!js` 自定义标签 | FileNotFoundError：`assets/templates/dsh/agent.cordis.yml` 不存在 | B 类（实现缺失）|
| 2 | `test_dsh_tool_fs_search_has_required_config` | BDD-2 + BDD-17 | tool-fs-search 行 `config.sampleOverCapGlobResults is False`（schemastery 必填无默认值，实机缺陷回归）| 同上 | B 类（实现缺失）|
| 3 | `test_dsh_persona_is_thin_identity` | BDD-3 | persona 行 `config.text` 含 `{agate_root}/orchestrator-template.md` 引用，且**不含**模板首行标题「# Orchestrator（agate 编排 Agent）」（verbatim 判据）| 同上 | B 类（实现缺失）|
| 4 | `test_dsh_preset_yml_has_name_and_description` | BDD-4 | preset.yml 合法 YAML，`name`/`description` 均为非空字符串 | FileNotFoundError：`preset.yml` 不存在 | B 类（实现缺失）|
| 5 | `test_dsh_skill_frontmatter_valid` | BDD-5 | SKILL.md frontmatter `name == "agate-protocol"` 且 `description` 非空 | FileNotFoundError：`SKILL.md` 不存在 | B 类（实现缺失）|
| 6 | `test_dsh_setup_section_and_symlink_commands_present` | BDD-7（标题串）+ BDD-8 + BDD-15 | 「步骤 2-DSH」章节在位 + BDD-8 精确命令串：`mkdir -p ~/.dsh/.agent-presets/agate ~/.dsh/skills/agate-protocol` + 三条独立 `ln -sf ~/.agate/assets/templates/dsh/{agent.cordis.yml,preset.yml,SKILL.md}`（源→模板、目标→`~/.dsh/.agent-presets/agate/` 与 `~/.dsh/skills/agate-protocol/SKILL.md`）| AssertionError：SETUP.md 无「步骤 2-DSH」章节 | B 类（实现缺失）|
| 7 | `test_dsh_setup_dsh_section_within_step_2` | BDD-7（位置判据）| DSH 标题「### 步骤 2-DSH」位于 `## 步骤 2：` 与 `## 步骤 3` 之间（步骤 2 平台章节区内，与既有小节同构）| AssertionError：缺「### 步骤 2-DSH」标题 | B 类（实现缺失）|
| 8 | `test_dsh_setup_section_has_install_hook_call` | BDD-9（前半）| **DSH 章节切片内**含 `python3 ~/.agate/scripts/install-hook.py`（唯一安装脚本调用；章节内断言防其他章节既有 install-hook 引用误命中）| pytest.fail：DSH 章节不存在 | B 类（实现缺失）|

> 说明：用例 2 同时是 BDD-17 回归护栏（红/绿双态可复现：缺 `sampleOverCapGlobResults` → FAIL，在位 → PASS）；用例 6 标题串断言承载 BDD-15「SETUP.md 章节与命令在位」要素。

## 2. 红灯预期

- **8/8 全红**：5 例 FileNotFoundError（`assets/templates/dsh/` 三模板文件未落位，用例 1-5）+ 3 例 AssertionError / pytest.fail（SETUP.md DSH 章节未落位，用例 6-8）。
- **全部为 B 类（实现缺失）**：无 SyntaxError、无第三方 import 失败——依赖仅 stdlib（re）+ pyyaml（P1 能力已验证 pytest 9.0.3 + pyyaml 可用），无网络、无真实 DSH 实例。
- **check-tdd-red.py 预期 exit 0（真红灯）**：P2-design §5 未声明 formatter → pytest 退化为 exit-code-only（非零退出即红灯可推进），精度可接受不阻断。

## 3. BDD-15/16/17 在位互链（派发指引第 ③ 项）

| BDD | 互链方式 |
|-----|---------|
| BDD-15（测试文件存在且 ≥5 用例、pytest 全绿）| 本文件恰 8 用例（≥5）；P4 落位后由 P5 gate_commands.P3 单文件 + P5 全量验证绿；用例 6 断言 SETUP.md 章节/命令在位（BDD-15 覆盖面）|
| BDD-16（测试平台无关）| 测试只校验仓库内文件（`agate_root` fixture + pyyaml 解析 + 文本子串断言）；四条禁止项（不写 /tmp、不假设符号链接语义、不调用 DSH、不依赖主目录/`~/.dsh`）在代码注释与 §4 中显式落实；无 DSH 实例的 CI 环境可跑 |
| BDD-17（回归护栏红/绿可复现）| 用例 2 是缺陷回归：P3 当前红（文件缺失）、P4 实现后绿、P6 变异验证（移除 `config.sampleOverCapGlobResults` → FAIL / 恢复 → PASS）双态可复现 |

其余 BDD 的验证路径（沿用 P2-review「测试缺口」结论，无需新增自动化用例）：BDD-6（SKILL.md 正文映射/平台注意）、BDD-10/11（SETUP.md 说明/使用指引）、BDD-13/14（platform-notes 能力表/互链）由 P6 实跑文本核对；BDD-12 由 P6 + 一致性检查；BDD-9 后半（全仓无 per-platform installer）由 P4 grep 复证 + P6 完成标准 #5；BDD-18 由 P5 三独立 gate 兜底；BDD-19 由 P8 按触发面清单核对。

## 4. 平台无关性约束落实（BDD-16）

| 禁止项 | 落实方式 |
|--------|---------|
| 不写 /tmp | 全部断言只读仓库内文件；无任何临时文件写入（不用 tmp_path——不需要）|
| 不假设符号链接语义 | 不调用 `os.path.islink`、不创建链接；SETUP.md 中的 `ln -sf` 命令串作为**文档文本**被断言，不被执行 |
| 不调用 DSH | 不 spawn 任何 DSH 进程；`~/.dsh` 等仅作为 SETUP.md 文本断言的目标路径字面量 |
| 不依赖主目录路径 | 仓库路径一律经 `agate_root` fixture（conftest 从 tests/ 上溯反推或 AGATE_ROOT 覆盖）解析 |

## 5. 与参考实现（agate-copy 5 用例草稿，非权威）的差异

| 差异点 | 草稿（agate-copy）| 本设计 | 依据 |
|--------|------------------|--------|------|
| 用例总数 | 5 | **8**（+3）| 派发指引（P2-review 建议 1/2 必做）|
| 用例 6（SETUP 章节）| 3 条宽松子串断言（章节名 + 2 路径）| 扩展为 BDD-8 **精确命令串**断言（mkdir -p 全串 + 三条独立 ln -sf 源路径 + 目标路径），且**章节切片内**断言 | P2-design R-1（以 BDD-8 精确命令串为断言基准）+ P2-review 建议 5（三条独立 ln 行）|
| 用例 7（位置判据）| 无 | 新增：`## 步骤 2：` < `### 步骤 2-DSH` < `## 步骤 3` | P2-review 建议 2 + 决策 D-1（h3 置于步骤 2 区内）|
| 用例 8（install-hook）| 无 | 新增：DSH 章节切片内含 `python3 ~/.agate/scripts/install-hook.py` | P2-review 建议 2 + BDD-9 |
| 用例 3（persona 薄身份）| 无 | 新增：正判据（含 `{agate_root}/orchestrator-template.md`）+ 负判据（不含模板首行标题）| P2-review 建议 1 + BDD-3 |

## 6. 完成标准自检

- [ ] 测试代码可收集（无语法错误、无第三方 import 失败）
- [ ] 8/8 用例当前红灯，失败原因均为"实现缺失"（文件不存在 / 断言不满足）
- [ ] 每条断言可追溯至 P1 BDD（§1 映射表）
- [ ] test_code_dir 已声明（frontmatter）
- [ ] 用例数只增不减（1030 → 1038）
