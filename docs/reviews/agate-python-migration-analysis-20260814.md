# agate 全面转向 Python 分析报告

> 目的：评估"agate 协议本体从 bash 全面转向 Python"的可行性、规模、收益、风险与迁移路径。
> 触发背景：TAG0005+TAG0009 执行复盘确认——78 个 Windows 失败 + 11.7 小时 CI 排障拉锯的根源是 **bash 在 Windows 的 MSYS2 模拟层不成立**。本报告回应用户明确期望（"我期望转 python"）。
> 数据：agate/scripts/ 30 个 .sh（3813 行）+ 18 个 .py（2293 行）、agate/tests/ 58 个 .bats（727 @test）+ 526 行 helpers、git hook 链。

---

## 1. 结论摘要（TL;DR）

| 维度 | 结论 |
|------|------|
| 技术必要性 | **产品逻辑侧：值得**。30 个 sh 中 19 个已调 python，bash 特性依赖浅（0 个 associative array），Python 可覆盖全部逻辑 |
| 硬约束 | **git hook 入口必须保留 sh 薄壳**（shebang 软链机制 + Windows 无 env/python3 可靠解析）|
| 最大成本 | **测试侧：727 个 .bats 重写为 pytest** 是数周工作量，是迁移的最大阻力 |
| 建议路径 | **两阶段**：① 产品逻辑 Python 化（中等成本，消解产品脚本侧结构性平台问题）→ ② 测试框架迁移（高成本，可延迟/部分迁移）|
| 风险 | 高——涉及协议文档、hook、dispatch、consistency 全链；需逐阶段回归 |

---

## 2. 现状：bash 与 Python 的真实分布

### 2.1 产品脚本

| 类别 | 文件数 | 行数 | 说明 |
|------|--------|------|------|
| 纯 bash 逻辑（无 python）| 11 | ~1200 | archive/changes/extract/migrate/next-card/render/summary/p6-format/commit-msg/install-hook/pre-push |
| 已调 python（混合）| 19 | ~2600 | 状态机/frontmatter/YAML/gate 判定等重逻辑已在 .py |
| Python 脚本 | 18 | 2293 | consistency 841 行是最大单文件 |

**关键事实**：agate 早已是"sh 薄壳 + py 逻辑"混合架构。19/30 个 sh 的退出路径最终落在 python 上。sh 层的剩余价值主要是：函数库（gate-result.sh）、git 调用编排、环境探测。

### 2.2 bash 特性依赖（决定迁移难度）

| 特性 | 使用脚本数 | Python 等价 |
|------|-----------|-------------|
| `[[ ]]` | 7 | `==`/`Path` 比较 |
| 数组 `arr=()` / `arr+=()` | 5 | `list` |
| `readarray`/`mapfile` | 1 | `readlines()`/`subprocess` 捕获 |
| **关联数组 `declare -A`** | **0** | —（无不可移植特性）|
| `local` | 12 | 函数作用域天然 |

**结论**：无 bash-only 不可移植特性。全部逻辑可在 Python 等价实现。迁移难度主要在"重写量"而非"特性映射"。

### 2.3 函数库依赖

- `gate-result.sh`（105 行）被 pre-commit-gate/check-tdd-red/agate-capture-env-baseline 3 个脚本 source——提供 `write_gate_result`/`read_state_phase` 等
- `agate-workspace-resolve.sh`（57 行）被 pre-commit-gate/check-debt/agate-migrate-workspace 3 个脚本 source
- Python 化的函数库等价物 = 一个 `agate_common.py` 模块

---

## 3. 必须保留 bash 的硬约束（诚实回答）

### 3.1 git hook 入口（唯一硬约束）

```
.git/hooks/pre-commit → 软链 → ~/.agate/scripts/pre-commit-gate.sh  (#!/usr/bin/env bash)
```

**为什么必须保留 bash 薄壳**：
1. **git 执行 hook 的机制**：git 在 Windows 上通过 Git Bash 的 `sh.exe` 执行 hook 文件。hook 的 shebang `#!/usr/bin/env bash` 由 git 内部解析。
2. **shebang 可靠性**：`#!/usr/bin/env python3` 在 Windows 上依赖 `env` 和 `python3` 在 git 的 PATH 中可解析——这**不可靠**（Windows 命令名是 `python` 非 `python3`；git 的 sh 环境 PATH 有限）。`#!/usr/bin/env bash` 则总能解析（git 自带 bash）。
3. **install-hook 软链机制**：hook 经 `ln -sf` 软链到协议本体，Windows 退化为复制模式。**hook 文件本身必须是 sh**，内部 `exec` python 是安全的。

**结论**：hook 层保留 sh 薄壳（约 15 行：shebang + AGATE_ROOT 自定位 + **复制模式 `.agate-root` 恢复** + exec python 主程序）——复制模式恢复机制（pre-commit-gate.sh 现有 L31-38 的 readlink + `.agate-root` 标记回退）必须在薄壳中保留，否则 Windows 复制安装后 hook 找不到本体。**逻辑全部移到 python**。

### 3.2 其他可 python 化项（非硬约束）

| 项 | 可 python 化？ | 说明 |
|----|---------------|------|
| gate 判定逻辑 | ✅ | check-gate.sh（488 行）→ python，最值得 |
| git 集成 | ✅ | `subprocess.run(["git", ...])`，Python 有统一 subprocess API |
| 环境探测 | ✅ | `shutil.which`/`Path` 跨平台 |
| YAML/frontmatter | ✅ | 已有 pyyaml |
| CRLF/编码 | ✅ | `open(encoding="utf-8", newline="")`，Python 原生 |
| CI workflow | ✅ | 不涉及脚本语言 |
| **测试框架** | ⚠️ 可但贵 | bats→pytest，见 §6 |

---

## 4. 平台收益：Python 如何消解 78 个 Windows 失败

对照 TAG0009 实测的根因分类（复盘报告 §2.1），逐项映射 Python 的消解效果：

| TAG0009 根因 | bash 中的表现 | Python 中的状态 |
|-------------|--------------|----------------|
| `git diff --cached --name-only` 输出 CRLF | grep 匹配失败 | `subprocess` + 显式 `encoding="utf-8"` 处理；Python 处理 `\r\n` 天然 |
| `git rev-parse --show-toplevel` 返回 `C:/` vs `realpath -m` 返回 `/c/` | 路径风格混用 | `Path.resolve()` 统一；无 MSYS 风格问题 |
| Windows python 无法解析 MSYS `/c/...` | 需 py_path 转换 | **消失**：全 Python 无 MSYS 路径 |
| `subprocess.run(["bash",...])` 解析到 WSL | WSL 干扰 | 不需要 bash；用 `sys.executable` 自举 |
| subprocess text=True cp1252 解码中文 | 需 encoding=utf-8 | **需显式 `encoding="utf-8"`**（Windows Python 文本默认是 ANSI 代码页 cp1252/cp936，非 UTF-8）——把"强制 utf-8"列为迁移 gate 规则之一，否则同根因复发 |
| bats 版本导致只跑 72/625 | 框架 bug | **仅阶段二（pytest）消失**；阶段一 bats 仍在 Windows 跑 |
| pyyaml 未装 | CI 环境 | 仍在（Python 依赖 pyyaml，需装，且依赖面扩大，见风险表）|
| `env -u PATH` 找不到 bash | 需绝对路径 | 消失（无 bash 调用）|
| consistency 扫到 bats/ 目录 | CI 目录污染 | **仅阶段二（pytest）消失**；阶段一 bats 仍在 |

**估算（终态 = 阶段一 + 阶段二全部完成）**：实际 Windows 失败约 29 个 / 约 15 类根因（复盘报告 §2.1），其中**产品脚本侧**的结构性平台问题（MSYS 路径/CRLF/WSL/路径风格混用）在 Python 下消除；**测试框架侧**问题（bats 版本、bats/ 目录污染）仅阶段二消除。**不做"90%"量化**——残留类别包括：pyyaml 安装（CI 环境）、软链语义（Windows 无 POSIX 软链，与语言无关）、薄壳自身的 shellcheck 面、git 子进程在 Windows 的进程创建开销（性能问题，非失败）。

**性能**：Python 的收益是**把 `git | grep | sed` 管道合并为单进程**（减少子进程数），而非"Python 启动比 bash 快"——python.exe 解释器启动并不必然快于 bash。git 调用本身的 Windows 进程创建开销不变。**Windows 全量测试依然需要冒烟机制或并行**——这是平台现实，不是语言问题。

---

## 5. 迁移规模（产品逻辑侧）

### 5.1 工作量估算

| 项 | 规模 | 工作量 |
|----|------|--------|
| 19 个混合 sh 的 bash 部分 → py | ~2600 行（19 个混合文件总行数）| 中-高 |
| 11 个纯 bash 脚本 → py | ~1200 行 | 中 |
| gate-result.sh 函数库 → agate_common.py | 105 行 | 低 |
| agate-workspace-resolve.sh → py | 57 行 | 低 |
| 3 个 hook 改 sh 薄壳 + exec（含复制模式恢复）| 每 hook ~15 行 | 低 |
| 协议文档（dispatch/hook/git-integration 等引用）| 全局 grep 更新 | 中 |
| CI workflow | protocol-tests.yml 改 python 调用 | 低 |

**产品逻辑侧估算**：全部 30 个 sh 的 bash 逻辑总量约 3813 行（扣除保留的 hook 薄壳约 45 行）→ 约 3000 行 sh → 约 2000 行 py（Python 更简洁），**总工作量约 3-4 周（含测试适配）**——比初稿的 2-3 周更保守，因 19 个混合文件的 sh 部分几乎都是 bash 逻辑（非薄壳）。

### 5.2 测试侧（最大成本）

| 项 | 规模 | 工作量 |
|----|------|--------|
| 58 个 .bats → pytest | 727 @test | **数周（高）** |
| helpers 526 行 → pytest fixture | — | 中 |
| Windows 冒烟机制 | check-windows-smoke.sh | 保留或退役 |

**测试侧是迁移的真正瓶颈**：727 个 bash 断言链重写为 pytest 断言，是数周密集工作 + 高回归风险。**建议延迟**。

---

## 6. 迁移策略（分两阶段）

### 阶段一：产品逻辑 Python 化（推荐先做）

```
现状: sh 壳 + py 逻辑（19/30 混合）
目标: py 逻辑 + sh 薄壳（仅 hook 入口）
```

**具体步骤**：
1. 建 `agate/scripts/agate_common.py`：替代 gate-result.sh + agate-workspace-resolve.sh 的函数库
2. 逐个把 30 个 sh 的 sh 逻辑迁到 .py（优先 check-gate.sh 488 行、pre-commit-gate.sh 404 行这两个最重的）
3. 3 个 hook 保留 sh 薄壳（~15 行）：shebang + 定位 AGATE_ROOT + **复制模式 `.agate-root` 恢复** + `exec python3 "$AGATE_ROOT/scripts/xxx.py" "$@"`
4. 每迁一个脚本：保留原 .bats 测试（测试调用方式从调 sh 改为调 py），**但约 30-40 个用例需随脚本迁移同步改断言**（check-platform-assumptions.bats 17、env-adapt-docs.bats 9、agate-scripts-encoding.bats 2、helpers-python.bats 3、agate-workspace-resolve.bats 若干——这些专门断言 sh/python 接口与 bash 行为）
5. CI 保持 Linux 全量 + Windows 冒烟，**先不迁测试框架**

**阶段一收益**：
- 产品脚本侧的结构性平台问题（MSYS 路径/CRLF/WSL/路径风格混用）在 Python 下消除
- 测试仍跑 bash（bats 调 py 脚本），测试框架侧问题（bats 版本/目录污染）留待阶段二
- 冒烟机制可保留（Windows 性能仍需要）或退役（待验证）

### 阶段二：测试框架迁移（可选，高成本）

```
现状: bats（58 文件 / 727 @test）
目标: pytest
```

**前提**：阶段一完成、产品全 Python 后，bats 的价值仅是"测 py 脚本"。此时：
- 保留 bats 调 py（改动最小，收益=无 bash 测试代码的平台问题）
- 或迁 pytest（改动大，收益=测试代码也平台无关 + 统一生态）

**建议**：先保留 bats 测 py。只有当"测试代码本身的平台问题"成为新瓶颈时才迁 pytest。

---

## 7. 风险与缓解

| 风险 | 严重度 | 缓解 |
|------|--------|------|
| 协议文档与脚本引用大面积失效 | 高 | 每个脚本迁移后跑 consistency + 全量 bats；文档与代码同步改 |
| **consistency.py 锚点关键字约束** | 高 | CHECK 8/9 锚点表硬编码 `.sh` 路径与关键字（如 `check-gate.sh` 含 `P2 不可裁剪`/`NEED_CONFIRM`、`check-pruning.sh` 含 `coupling_checklist`）——py 版脚本**必须保留这些关键字**或同步更新锚点表，否则 consistency 报 ERROR |
| hook 入口 exec 失败（Python 路径/依赖）| 高 | hook 薄壳加"python 探测 + 失败回退"；保留 sh 逻辑作为 fallback |
| pyyaml 从可选变强制依赖 | 中 | 现仅 state/vision 类 .py 依赖 pyyaml，迁移后**所有 gate 逻辑**依赖——SETUP.md 明确 `pip install pyyaml`，纳入 CI 安装步骤 |
| **编码规范** | 中 | Windows Python 文本默认 ANSI 代码页（cp1252/cp936）——新代码**必须显式 `encoding="utf-8"`**，列为 gate 规则（否则 88d0deb 根因复发）|
| **Python 版本下限** | 中 | 兼容 3.8+（platform-notes 现有下限）——新代码避免 3.9+/3.10+ 语法（`match`、`str.removeprefix` 等），否则用户环境 break |
| 测试回归 | 高 | 阶段一逐脚本迁移 + 每步全量 bats 验证；不批量重写 |
| 兼容性：既有任务数据（.state.yaml 等）| 中 | 格式不变，Python 读写同格式 |
| 性能反直觉：Windows 仍慢 | 低 | 明确"进程数是 Windows 慢的主因"，与语言无关；冒烟机制保留 |
| **文档影响面** | 中 | platform-notes.md Windows 章节（5 处 `.sh` 引用、`bash install-hook.sh`、copy 模式前提）与 UPGRADING.md 需重写；30 个脚本改名/删档对直接调用脚本的用户是破坏性变更，须列 UPGRADING 章节 |

> 附带收益（评审补充）：platform-notes.md 现有"纯 cmd/PowerShell 无 bash：25 个 .sh 无法运行"的限制——Python 化后"无 bash 环境"成为可行选项，是可利用的卖点。

---

## 8. 与复盘的关联

本报告是对复盘结论 §6.3 的展开。复盘确认：
- 11.7 小时排障拉锯 = bash 在 Windows 模拟层不成立（技术） + agate 无外部验证协议（机制）
- Python 化直接消解**技术**根源（bash→Python 平台无关）
- **机制**根源（supplementable 无流程）仍需 agate 协议层面补丁，Python 化不解决

---

## 9. 建议立项范围（若用户拍板）

**立项建议：TAG0010 "agate 产品逻辑 Python 化"**
- P1 范围：30 个 sh → py（hook 薄壳除外），全量 bats 保持绿
- 验收标准：
  ① 全量 bats（bats 调 py）全绿
  ② consistency 0 ERROR（py 版脚本保留锚点关键字或同步更新锚点表）
  ③ shellcheck 仅扫保留的 sh 薄壳；**py 代码用 ruff/pyflakes 静态检查**（补上 shellcheck 的替代 gate，保持"外部客观 gate"纪律）
  ④ Windows CI 冒烟通过
  ⑤ 平台假设扫描器**扩展覆盖 .py**（现只扫 .bats/.bash/.sh，对 py 完全失明——必须先扩展规则集再谈"零命中"；否则该项是空洞验收）
- 明确不做：测试框架迁移（阶段二另立）；协议文档不做全量重写，但**必要的引用同步**（dispatch/hook/git-integration/platform-notes Windows 章节/UPGRADING）计入阶段一范围

---

## 10. 附：关键数据表

| 指标 | 值 |
|------|-----|
| 产品 sh 文件数 / 行数 | 30 / 3813 |
| 产品 py 文件数 / 行数 | 18 / 2293 |
| 已调 python 的 sh | 19 |
| 调 git 的 sh | 14 |
| 用数组语法的 sh | 5 |
| 用关联数组的 sh | 0 |
| 测试 .bats 文件 / @test | 58 / 727 |
| helpers 行数 | 526 |
| hook 数 | 3（pre-commit/pre-push/commit-msg）|
| 必须保留 sh 的位置 | hook 入口薄壳（3 处，~15 行/个）|
| 阶段一预计工作量 | 3-4 周 |
| 阶段二预计工作量 | 数周（可延迟）|
| 阶段一强制 gate | 显式 `encoding="utf-8"` / Python 3.8+ / ruff / 扫描器覆盖 .py |
