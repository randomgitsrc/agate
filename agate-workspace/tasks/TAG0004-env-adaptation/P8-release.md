---
phase: P8
task_id: TAG0004-env-adaptation
type: release
parent: P7-consistency.md
trace_id: TAG0004-P8-20260813
status: draft
created: 2026-08-13
agent: implementer
---

# P8 发布准备 — TAG0004（agate 脚本健壮性 + 环境适配：Windows 原生兼容 + Linux 基线回归）

- `bump_type: patch`
- 版本号变更确认：**v0.43.0 → v0.44.0**
- `debt_check: none`
- `[PROD_NOT_TOUCHED]` 本阶段仅读 worktree 内产出与仓库文件（P2/P7/P0-brief/CHANGELOG/README/debt 目录），未接触生产环境 / 主 checkout / ~/.agate，无 PROD_TOUCHED 触发。

## 1. bump_type 判定

- **bump_type: patch**（v0.44.0）
- 理由：本任务为 bug 修复 + 环境适配（脚本健壮性、Windows 原生兼容增量、文档与 CI 矩阵），**不改公共 API 行为、无破坏性变更**（现有 714 用例回归全绿 + consistency 0 ERROR + shellcheck 0 error，Linux 基线无回退）。按语义化版本，修复与兼容性增量 → patch。
- 明确声明：Windows 兼容（Q1 路径归一化、Q5 SETUP 文档、CI windows-latest matrix）为**增量适配而非新 API 能力**，不构成 minor；P0-brief 明确"兼容 Windows ≠ 只支持 Windows，Linux 是基线"。

## 2. 版本号变更确认

- 当前版本：v0.43.0（git tag `v0.43.0` + README.md L6 badge `v0.43.0` + CHANGELOG `## [0.43.0] - 2026-08-12`）
- 新版本：v0.44.0
- **version 文件 = README.md badge**（仓库无独立 version.txt；badge 即版本标识）。主 Agent 执行 bump 时改 README.md L6：`v0.43.0` → `v0.44.0`。
- 版本链路：README badge + git tag `v0.44.0` + CHANGELOG `## [0.44.0] - 2026-08-13` 三处一致。

## 3. 受影响 packages（P2-design.md 声明，7 项全覆盖）

| # | package | 改动文件 | 变更内容 |
|---|---------|---------|---------|
| 1 | agate-scripts-sh | pre-commit-gate.sh / check-gate.sh / check-p6-evidence.sh / check-p6-format.sh / check-tdd-red.sh / gate-result.sh / install-hook.sh / agate-next-card.sh / agate-workspace-resolve.sh / agate-render-dispatch-prompt.sh | S1 空格路径数组化、M4/M5 全角冒号 alternation、M9 grep -F 前缀、S2 中文证据文件名、RM-AG0001 反引号容错、RM-AG0002+TPV0090-M4 A/B 判定增强、Q1 路径归一化、M6 CRLF 容错、其他-a/b/c |
| 2 | agate-scripts-py | 13 个 py + agate-frontmatter-check.py | S3 全部文本 open() 加 encoding="utf-8"；M6 frontmatter 提取 CRLF 归一 |
| 3 | agate-phase-cards | P{1,2,3,4,6,7,8}-*.md 七卡 | Q2 补注 git-integration.md 规则 2 语义（phase=本 commit 产出阶段） |
| 4 | agate-docs | agate/SETUP.md | Q5 Windows 章节（AGATE_ROOT 路径/PATH/PYTHONUTF8/CRLF） |
| 5 | agate-gitconfig | .gitignore | Q5 模板预设 `!version.txt` + `dist/` |
| 6 | agate-ci | .github/workflows/protocol-tests.yml | CI windows-latest matrix（bats/shellcheck/consistency/gate-backstop） |
| 7 | agate-tests | 8 个 .bats（含新增） | S1 空格路径 fixture、S2 中文证据、M4/M5 LC_ALL=C 用例、BDD-30/31/35/36/37 check-tdd-red A/B 判定用例、grep 断言审计 |

> P7-consistency.md §3.2 确认：P4 实际改动 48 文件（git diff 03500e7..c8653b8），7 项全覆盖与 P2 声明一致 ✓。

## 4. CHANGELOG [0.44.0] 段内容（草稿，主 Agent 写入 CHANGELOG.md 顶部）

> 以下为新增 `## [0.44.0] - 2026-08-13` 段草稿。Keep a Changelog 格式，按「新增 / 变更 / 文档」组织。**不直接修改 CHANGELOG.md**。

```markdown
## [0.44.0] - 2026-08-13

### 修复（TAG0004 脚本健壮性 + 环境适配：Windows 原生兼容 + Linux 基线回归）

- **S1 pre-commit-gate.sh 空格路径 fail-open 修复**：`STAGED_STATE_FILES` / `PROCESSED_DIRS` 由空格拼接字符串 → bash 数组（L50/57/339/343/350），消除目录/文件名含空格时静默绕过 gate 的 fail-open 风险；新增空格路径 commit 场景 fixture 回归
- **S3 13 个 py 文本 open() 补 encoding="utf-8"**：全部文本读写加 `encoding="utf-8"`（Image.open 与二进制模式除外），修复中文路径/内容在非 UTF-8 locale 下解析失败；新增 grep 断言审计测试作永久回归拦截
- **S2 check-p6-evidence.sh 中文证据文件名支持**：证据引用正则字符类加宽（`\([^()]*[^()[:space:]]\.[a-zA-Z0-9]+[^)]*\)`），中文/含空格文件名正确匹配，维持"必须有扩展名"结构（无扩展名仍拒绝）
- **M4/M5 全角冒号 POSIX locale**：check-gate.sh L356/357 与 check-p6-format.sh L69 的 `[:：]` bracket 改 alternation（`(:|：)`），修复 `LC_ALL=C` 下全角冒号不匹配（与 v0.40.3 L84 修法统一）
- **M6 frontmatter 提取 CRLF 容错**：frontmatter 提取入口（agate-md-field-get.py / agate-frontmatter-check.py / check-gate.sh 8 处 sed / check-frontmatter.sh 链路）统一剥离行尾 `\r`，Windows checkout 的 CRLF md 也能正确提取；不动 .gitattributes，历史 CRLF review 文件不受影响
- **M9 路径正则元字符**：pre-commit-gate.sh 的 `^${TASK_REL}` grep -E 拼接改 grep -F 字面前缀 + `awk index($0,p)==1` 行首锚定（L102/104/133/228/290 共 5 处），目录名含 `[`/`]`/`*` 时不再误判
- **Q1 agate-next-card.sh 路径归一化**：`${CARD_FILE#$AGATE_ROOT/}` 前缀剥离改"先试直接剥离、失败则归一化后剥离"（rel_card + 盘符小写），修复 Windows 盘符/混合斜杠下卡片 hash 校验失败（TQC0001 实测）；Linux 相对路径输出逐字节不变
- **Q2 7 张 phase-cards 补注规则 2 语义**：P1/P2/P3/P4/P6/P7/P8 卡片"更新 .state.yaml phase"步骤对齐 git-integration.md 规则 2——commit 时 phase = 本 commit 产出阶段，下一阶段推进随下一阶段产出同 commit（与已对齐的 P5 卡一致，纯文档，gate 判定逻辑零改动）
- **Q5 SETUP.md Windows 章节 + .gitignore 预设**：SETUP.md 扩展独立 Windows 章节（AGATE_ROOT Unix 风格路径 / PATH 注入风险 / PYTHONUTF8=1 / core.autocrlf 与 CRLF）；.gitignore 模板预设 `!version.txt` + `dist/`
- **RM-AG0001 check-gate.sh P1 反引号盲区**：行首标记正则（`[SUGGEST:` / `[NEED_CONFIRM]` / `[NO_NEED_CONFIRM]`）加可选反引号容错（L69/71/89/109/121/125/129），`` `[SUGGEST: ...]` `` 正确计 WARNING、`` `[NEED_CONFIRM]` `` 正确阻塞
- **RM-AG0002 + TPV0090-M4 check-tdd-red A/B 判定增强**：无 formatter 时不再纯 exit-code-only——exit 1 且输出含 compile/error 关键词判 A 类，普通失败仍判正确红灯；formatter 路径 B 类检测纳入 NameError（pytest.sh 增 name_errors 数组），非 NameError（TypeError 等）仍判 A 类；globals().get() 规避模式保持向后兼容
- **其他-a .agate.env CR 剥离**：agate-workspace-resolve.sh 读取 `.agate.env` 值前 `tr -d '\r'`，Windows 编辑的 CRLF env 文件不再导致路径含 `\r`
- **其他-b 复制模式 AGATE_ROOT 解析回退**：install-hook.sh 复制模式写 `.agate-root` 标记文件，pre-commit-gate.sh readlink 解析失败时读标记兜底，Windows 复制模式 hook 不再静默放行
- **其他-c render-dispatch-prompt sed 转义**：agate-render-dispatch-prompt.sh 替换串转义 `&`/`|`（awk gsub + 反斜杠预处理），AGATE_ROOT 含 `&`/`|` 时替换不再错误

### 新增
- **CI windows-latest matrix**：`.github/workflows/protocol-tests.yml` 新增 `windows-latest` 平台矩阵（bats / shellcheck / consistency / gate-backstop），Windows 原生兼容的唯一兜底验证（本环境为 Linux，不宣称"已实测 Windows"）
- **S3 grep 断言审计测试**：扫描 `agate/scripts/*.py` 文本 `open(`/`read_text(` 必须带 `encoding=`（Image.open 与二进制模式除外），防后续改动漏加 encoding

### 文档
- **SETUP.md Windows 章节**（见上 Q5）
- **Q2 七张阶段卡片规则 2 语义补注**（见上 Q2）

### 变更
- **S1 数组化**：pre-commit-gate.sh 内部结构改动，行为语义不变（见上 S1）

> 版本 badge：README.md `v0.43.0` → `v0.44.0`
```

## 5. debt_check 字段

- `debt_check: none`
- 依据：`{AGATE_WORKSPACE}/debt/tech-debt.md` 不存在（debt/ 目录为空，grep/find 均无匹配）。本任务无回退（retreat）历史（git log 无 `^retreat:` 提交），无待登记技术债。
- 注意：本任务修复的 RM-AG0001 / RM-AG0002 / TPV0090-M4 为 roadmap 归入项，已完成修复闭环，无新增债务。

## 6. 临时资源清单

- **临时服务/进程**：无。P4-P7 未启动任何 debug server / 临时 daemon / 监听端口。
- **临时数据**：无。未创建测试数据库、未写测试占位数据；测试全部走 bats `$BATS_TEST_TMPDIR` 自动清理。
- **开发安装**：无。未做 editable install / 全局包安装（依赖 pyyaml + Pillow 为既有环境，未新增）。
- **可清理项**：`/tmp/opencode` 下存在本任务期间的临时验证日志（LC_ALL=C 实测、S2/Q1/M9 候选正则验证等），可清理。
- **无 [PROD_TOUCHED]**：本任务全部改动在 worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0004` 内，未触碰主 checkout / ~/.agate / 任何生产数据或 API。

## 7. Lessons Learned

| 类别 | 教训 |
|------|------|
| 测试 | **TDD 空返回拆分**：bats 下 grep -c 无匹配时 exit 1 + `|| echo 0` 产生双行输出，必须 `\| tail -1`——空返回的边界要显式测试，否则断言假绿 |
| 环境 | **LC_ALL=C 实测代替猜测**：bracket expression `[:：]` 在 POSIX locale 下不匹配多字节 UTF-8 字符（只匹配首字节），GNU sed 靠 `\3` 回写"碰巧"正确、BSD/busybox 不可移植——locale 行为必须实测验证，不能凭 GNU 单平台假设 |
| 架构 | **跨平台正则不依赖 locale**：Windows/Linux 双平台下，bracket 字符类内的 unicode 区间（`\u4e00-\u9fa5`）与多字节字符不可移植——统一用 alternation（`(:|：)`）与负类加宽（`[^()[:space:]]`），语义等价且平台无关 |

## 8. 主 Agent 后续动作（发布执行清单，非 releaser 执行）

1. 执行 P8 gate：`check-gate.sh P8 $TASK_DIR`（bump_type / debt_check / version 变更 / CHANGELOG 变更）
2. bump-version：README.md L6 badge `v0.43.0` → `v0.44.0`
3. 将 §4 CHANGELOG [0.44.0] 段写入 CHANGELOG.md 顶部
4. 重跑 P5 gate（P2 §4 gate_commands.P5 三命令）确认全绿
5. `git log v0.43.0..HEAD --oneline` 对照 CHANGELOG 无遗漏
6. READY 收尾：.state.yaml phase=READY → DONE；active-tasks.md 更新；git tag `v0.44.0`；bump + CHANGELOG + tag 同一 commit
7. 临时资源清理：参照 §6 清单（/tmp/opencode 日志）
