---
phase: P3
task_id: TAG0008
type: test-cases
parent: P2-design.md
trace_id: TAG0008-P3I-20260816
status: draft
created: 2026-08-16
agent: test-designer
---

# P3 测试用例 — agate-install（安装 / 卸载 / 环境探测）

> 批次：install（P2 dispatch_plan 批次 2/3）。承接 BDD-1~8，1:1 映射。
> 被测模块：`agate/scripts/agate-install.py`（**P3 阶段尚未实现**——测试当前全部红灯，红灯原因为"模块不存在"，B 类）。
> 测试代码：`agate/tests/unit/test_agate_version_install.py`。
> test_code_dir: agate/tests/unit/

## 0. 接口契约（测试约定的实现接口，P4 必须满足）

> 测试通过 `run_cli(python_exe, <agate_scripts>/agate-install.py, *args, env={...})` 子进程调用。以下为测试侧约定的 CLI/环境契约：

| 输入面 | 契约 | 依据 |
|--------|------|------|
| 无参 | `agate-install` → 装 latest 指针（最新发布 tag 的 worktree）+ current → latest | BDD-1/4 |
| 位置参数 | `agate-install <version>`（如 `v0.48.0`）→ 装指定版本 | BDD-2/3 |
| `--uninstall <version>` | 删版本目录 + worktree remove + 清理/重指指针；有项目引用则拒绝（退出非 0） | BDD-5/6 |
| `--check` | 环境探测 python3/pyyaml/git/bash，全齐 exit 0；缺项非 0 + 分平台修复指引 | BDD-7/8 |
| `AGATE_REPO_URL` env | 版本源仓库（测试指向本地临时 git repo，含 tag；实现做首次 clone 到 `~/.agate/repo`） | 测试隔离用（P2 §4.5 "repo 单克隆"的 URL 来源） |
| `HOME` env | 重定向 `~` 到测试 tmp 目录，`~/.agate` = `<home>/.agate`（防触碰真实 `~/.agate`） | 测试隔离（P2 §4.5 `~/.agate` 布局） |
| 指针形态 | `latest` / `current` 是纯指针：POSIX 软链、Windows 复制模式文本指针；`current` 默认 → `latest` → 版本目录 | BDD-1/4 + platform-notes 先例 |

## 1. BDD 映射表

| BDD | 测试用例 | 关键断言（Then 的可观测信号） |
|-----|----------|------------------------------|
| BDD-1 | `test_bdd_1_latest_pointer_after_noarg_install` | `~/.agate/latest` 存在；POSIX 为软链 / Windows 非目录（纯指针非 checkout 本体）；解析落点 `<home>/.agate/v0.48.0/` 存在且为最新 tag |
| BDD-2 | `test_bdd_2_version_dir_worktree_of_tag` | `~/.agate/v0.48.0/` 目录存在；`git -C ~/.agate/repo worktree list --porcelain` 含该路径；`git -C v0.48.0 rev-parse HEAD` == `git -C repo rev-parse v0.48.0`（检出 tag） |
| BDD-3 | `test_bdd_3_reinstall_idempotent` | 二次 `agate-install v0.48.0` 退出码 0；`worktree list --porcelain` 中版本路径出现次数 == 1（不重复） |
| BDD-4 | `test_bdd_4_current_defaults_to_latest` | `~/.agate/current` 存在；`current` 解析落点 == `latest` 解析落点，均为 `v0.48.0` 目录 |
| BDD-5 | `test_bdd_5_uninstall_removes_dir_and_clean_pointer` | `--uninstall v0.43.0` 退出码 0；`v0.43.0/` 目录不存在；worktree list 不再含该路径；`latest`/`current`（若存在）不悬挂（仍解析到存在的版本目录，此处为 v0.48.0） |
| BDD-6 | `test_bdd_6_uninstall_rejected_when_referenced` | 存在项目 `.agate-version` 声明 `agate: v0.43.0` 时卸载退出码非 0；输出含版本号与引用来源（项目路径或 `.agate-version`）；`v0.43.0/` 仍存在且 worktree list 仍含该路径 |
| BDD-7 | `test_bdd_7_env_check_all_present_exit_0` | `--check` 退出码 0；输出逐项列出 git / bash / yaml(pyyaml) / python3 或 python |
| BDD-8 | `test_bdd_8_env_check_missing_pyyaml_guidance` | mock 缺 pyyaml 时退出码非 0；输出列出缺失项（含 yaml）；含分平台修复指引（Linux：`pip install` pyyaml 类；Windows：PYTHONUTF8 / Git for Windows 类） |

## 2. 前置状态构造（Given 的共性手段）

- **版本源仓库**：`git_repo` fixture（或 `GitRepo(tmp_path/...)`）建本地 repo，`agate/scripts/README.md` 内容变体两次 commit 后打 `v0.43.0` / `v0.48.0` 两个 tag（v0.48.0 为最新）。测试以 `py_path(repo)` 转路径后写入 `AGATE_REPO_URL`。
- **干净 `~/.agate`**：HOME 指向 `tmp_path/home`，该目录初始不存在版本目录（无污染）。
- **安装**：以 HOME + AGATE_REPO_URL 子进程跑 `agate-install`（无参或 `<version>`）。
- **引用项目（BDD-6）**：`<home>/<project>/.agate-version` 写入 `agate: v0.43.0\n`（在 $HOME 扫描范围内）。
- **缺 pyyaml（BDD-8）**：`python_exe -m venv <tmp>/noyaml`（fresh venv 默认无 pyyaml），`PATH = <venv bin> + os.pathsep + 原 PATH`（venv bin 在 Linux 为 `bin/`、Windows 为 `Scripts/`）。`--check` 探测走 `probe_python()`（venv 内 python3/python）→ `import yaml` 失败 → 恰好 pyyaml 缺失，git/bash/python 仍由完整 PATH 命中。

## 3. 平台分支（测试平台无关原则）

- **指针断言**：POSIX（非 win32）断言 `latest` 是 `os.readlink` 可读的软链；Windows 断言 `latest` 非目录（复制模式文本指针）——不假设符号链接语义。
- **worktree 路径匹配**：`worktree list --porcelain` 输出与断言路径均过 `os.path.normcase` 后再匹配（Windows 大小写/分隔符差异容错）。
- **BDD-8 修复指引分支**：`sys.platform == "win32"` 断言 Windows 指引关键词；否则断言 Linux `pip install` 指引。
- **python 探测**：不经手写 `python3`，统一用 conftest `python_exe` fixture（`python3|python` 探测）。
- **windows_smoke**：`test_bdd_1_*`（每文件第 1 用例）+ `test_bdd_5_*` / `test_bdd_7_*` / `test_bdd_8_*`（平台敏感代表：卸载 worktree 清理 / 环境探测 / 分平台指引）。

## 4. 红灯预期

- 现状：`agate/scripts/agate-install.py` 不存在 → 每个用例 `run_cli(python_exe, <缺失脚本>, ...)` 得到 returncode=2（python: can't open file），断言失败 → 8 个用例全红（B 类：被测模块未实现，非测试代码 bug）。
- 自跑命令：`python3 -m pytest agate/tests/unit/test_agate_version_install.py -q --tb=no`。

## 5. 备注

- 本批只覆盖 BDD-1~8；resolve-chain（BDD-9~21/30/31）与 offline（BDD-22~29）批次由并行 subagent 各自产出，不越界。
- `AGATE_REPO_URL` 是测试为隔离引入的环境契约，需在 P4 实现中支持（P2 §4.5 未指明 repo URL 来源，测试侧取最小注入面）。
