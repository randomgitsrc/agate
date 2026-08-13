---
phase: P2
task_id: TAG0004-env-adaptation
type: design
parent: P1-requirements.md
trace_id: TAG0004-P2-20260813
status: draft
created: 2026-08-13
agent: architect
# ── v2.0 机器字段 ──
candidate_count: 28                # int ≥1，按实际候选数填
packages: [agate-scripts-sh, agate-scripts-py, agate-phase-cards, agate-docs, agate-gitconfig, agate-ci, agate-tests]
domains: [backend, security, cli]
ui_affected: false
---

# P2 方案设计 — agate 脚本健壮性 + 环境适配（Windows 原生兼容 + Linux 基线回归）

## 0. 影响域分析

**改什么**（按 P1 §6 审计范围 46 处位置，本设计逐项落方案）：

| 组 | 文件 | 改动性质 |
|----|------|---------|
| S1 | `agate/scripts/pre-commit-gate.sh` | STAGED_STATE_FILES / PROCESSED_DIRS 由空格拼接字符串 → bash 数组（L50/57/339/343/350） |
| S3 | 13 个 py（P1 §6 清单） | 全部文本 `open()` 加 `encoding="utf-8"`；grep 断言审计测试作回归拦截 |
| S2 | `agate/scripts/check-p6-evidence.sh:37` | 证据引用正则字符类加宽支持中文文件名（保留 `.*` + 扩展名结构） |
| M4 | `agate/scripts/check-gate.sh:356/357` | `[BLOCKER\][:：]?` / `[DEVIATION-CRITICAL\][:：]?` bracket → alternation `(:|：)` |
| M5 | `agate/scripts/check-p6-format.sh:69` | 4 处 sed `[[:space:]:：]` bracket → alternation（与 L84 v0.40.3 修法统一） |
| M6 | frontmatter 提取处（`agate-md-field-get.py` / `agate-frontmatter-check.py` / `check-gate.sh` P1/P2 review status 提取 / `check-frontmatter.sh` 链路） | CRLF 归一化（读取时剥离 `\r`），不改 `.gitattributes` |
| M9 | `agate/scripts/pre-commit-gate.sh:102/133/228` | `TASK_REL` 拼入 `grep -E` 模式 → grep -F 前缀 + 正则过滤（或 re_escape） |
| Q1 | `agate/scripts/agate-next-card.sh:56` | `${CARD_FILE#$AGATE_ROOT/}` 前缀剥离 → 先路径归一化再剥离（Windows 盘符/斜杠/大小写） |
| Q2 | `agate/phase-cards/P{1,2,3,4,6,7,8}-*.md` | mode B 旧写法"更新 phase=Pn→Pn+1" → 补注规则 2 语义（纯文档，参照已对齐的 P5 卡） |
| Q5 | `agate/SETUP.md` + 仓库根 `.gitignore` | 增 Windows 章节；`.gitignore` 模板预设 `!version.txt` + `dist/` |
| RM-AG0001 | `agate/scripts/check-gate.sh:69/71/89/109/121/125/129` | 行首标记正则加反引号容错（`[SUGGEST:` / `[NEED_CONFIRM]` / `[NO_NEED_CONFIRM]`） |
| RM-AG0002 | `agate/scripts/check-tdd-red.sh` + `gate-result.sh` | 无 formatter 时不再纯 exit-code-only：exit 1 + compile/error 关键词 → 判 A 类 |
| TPV0090-M4 | `agate/scripts/check-tdd-red.sh` + formatter | B 类检测纳入 NameError（`errors` 中区分未定义名） |
| 其他-a | `agate/scripts/agate-workspace-resolve.sh:33` | `.agate.env` 值 `tr -d '\r'` |
| 其他-b | `install-hook.sh` 复制模式 + `pre-commit-gate.sh:26` | 复制模式 hook 的 AGATE_ROOT 解析回退（读 `.agate-root` 标记文件） |
| 其他-c | `agate/scripts/agate-render-dispatch-prompt.sh:112-126` | sed 替换串转义 `&`/`|`（用 awk 或转义预处理） |
| CI | `.github/workflows/protocol-tests.yml` | 新增 windows-latest matrix（bats/shellcheck/consistency） |

**不改什么**（明确边界，降低回归风险）：

- **不改 `.gitattributes` 的 md 规则**——历史 CRLF review 文档保持现状（M6 走 frontmatter 提取处容错，见 SUGGEST）
- **不改 commit 顺序 / gate 判定逻辑**（Q2 纯文档补注；P2.64 原子性设计保留）
- **不改 check-tdd-red.sh 的 formatter 机制**（含 formatter 时 A/B 判定逻辑与现状一致，只加 NameError 识别分支）
- **不改 agate 协议语义**（`.state.yaml` 格式、阶段转移规则、角色体系）
- **不改主 checkout `/home/kity/oclab/agate` 与 `~/.agate`**（工作区纪律）

**风险在哪**：

- S1 是最高风险改动（fail-open 静默绕过修复方向反了会引入新回归）→ 需覆盖全部 Linux commit 场景验证（见 §3 验证场景清单）
- M6 CRLF 容错若在 sed 侧实现要防 `\r` 污染字段值（`sed 's/\r$//'` 只剥行尾，不剥行中）
- S2 正则加宽要防过宽放过真缺证据（BDD-10 负面用例兜底）
- Q1 归一化要保证 Linux 字节输出不变（BDD-22）
- 改 phase-cards 触发 SELF-GATE（commit message 需 `self-gate-review:`）

## 1. 候选方案 + 权衡 + 选择理由

> 组织方式：按缺陷组给候选方案，每组 ≥2（Q2 为纯文档、follows_existing_pattern 给 1 个 + 替代对照）。

### 1.1 S1 — pre-commit-gate.sh 空格路径（候选 1-2）

**候选 1A：bash 数组化改造（选定）**
- 做法：`STAGED_STATE_FILES=()` 数组收集；`STAGED_STATE_FILES+=("$REPO_ROOT/$f")`；`for STATE_FILE in "${STAGED_STATE_FILES[@]}"`；PROCESSED_DIRS 同理数组化，`case " $PROCESSED_DIRS "` 改为辅助函数/数组遍历判断
- 优点：彻底消除空格切词 fail-open；bash 数组是原生特性，无额外依赖；语义最清晰
- 风险：改动面在 L50/57/339/343/350 五处，需验证全部调用路径；`set -u` 下未初始化数组要 `+=()` 处理
- 工作量：中（一处脚本，改动集中）

**候选 1B：IFS 换行分隔 + while read 循环**
- 做法：`STAGED_STATE_FILES` 用换行分隔，循环改 `while IFS= read -r`；PROCESSED_DIRS 用 `grep -Fx` 判断成员
- 优点：改动更小（保留字符串变量，只改拼接/消费两处）
- 风险：字符串处理边界多（换行在路径中罕见但理论上存在）；`case` 匹配要整体重写；与现状差异更大
- 工作量：小-中

**选择理由**：选 1A。bash 数组语义明确、是 bash 惯用法，且与 `PROCESSED_DIRS` 的"目录集合成员判断"需求天然匹配（数组遍历比对，无分隔符歧义）。1B 的换行分隔虽改动小，但 PROCESSED_DIRS 的成员判断（原 `case " $PROCESSED_DIRS "`）换行化后反而更绕。

### 1.2 S3 — 13 py encoding（候选 3-4）

**候选 2A：grep 断言审计 + 批量加 encoding（选定，P1 SUGGEST 已采纳）**
- 做法：先加一条 bats 断言审计测试（扫描 `agate/scripts/*.py` 的 `open(`/`read_text(` 必须带 `encoding=`，Image.open 与二进制模式除外）；批量给 13 个 py 的文本 open() 加 `encoding="utf-8"`
- 优点：机械改动单测边际成本低；断言审计作永久回归拦截；与 HANDOFF 建议一致
- 风险：断言正则本身可能误报/漏报（如多行 open()、字符串内出现 open(）；需在 P3 先定好审计正则并验证
- 工作量：小（机械）＋ 一个测试

**候选 2B：逐 py 写单测**
- 优点：每处改动有直接行为验证
- 风险：13 个 py 单测工作量大、维护成本高；多数工具是薄壳，单测边际价值低
- 工作量：大

**选择理由**：选 2A。与 P1 SUGGEST 一致；断言审计 + 全量 bats 兜底足够。审计正则用 `grep -nE 'open\('` 后排除 `encoding=|Image\.open|二进制模式` 的行。

### 1.3 S2 — check-p6-evidence.sh 中文文件名（候选 5-6）

**候选 3A：负类字符集加宽（选定）**
- 正则：`\([^()]*[^()[:space:]]\.[a-zA-Z0-9]+[^)]*\)`
  - `[^()]*` 允许中文/空格/任意非括号字符出现在路径段；`[^()[:space:]]` 保证扩展名前至少一个非空格非括号字符（维持"有文件名"）；`\.[a-zA-Z0-9]+` 维持"必须有扩展名"结构；`[^)]*` 维持原尾部允许（如 `(a.png, vision: OK)`）
- 最小验证（本任务 §4）：中文文件名匹配、`(见截图)` 无扩展名拒绝、ASCII 全量现状用例回归通过
- 优点：改动小（正则一处）；维持"文件名+扩展名"结构（BDD-10 不放松）；中文/空格都支持
- 风险：`[^()[:space:]]` 也会接受部分标点（如 `:`），但原始正则也接受 `-` 等，可接受
- 工作量：小

**候选 3B：显式 CJK 区间加宽**
- 正则：`\([a-zA-Z0-9_/. -\u4e00-\u9fa5]*[a-zA-Z0-9_-\u4e00-\u9fa5]\.[a-zA-Z0-9]+[^)]*\)`
- 优点：语义更精确（只放宽中文/日文假名区间）
- 风险：bracket 里加 unicode 区间在 POSIX locale 下行为不可移植（正是本任务 M4 的教训）；不同平台 sed/grep 对 `\u` 支持不一致；边界（如扩展的中文标点）易漏
- 工作量：中

**选择理由**：选 3A。负类加宽不依赖 locale 对 unicode 区间的解析（规避本任务要修的 M4/M5 同类问题），且天然覆盖中文文件名含空格场景。3B 在 POSIX locale 下的 `\u4e00-\u9fa5` 区间行为不可靠。

### 1.4 M4/M5 — 全角冒号 POSIX locale（候选 7-8）

**候选 4A：bracket 改 alternation（选定，统一 v0.40.3 L84 修法）**
- check-gate.sh:356/357：`[BLOCKER\][:：]?` → `[BLOCKER\](:|：)?`；`[DEVIATION-CRITICAL\][:：]?` → `[DEVIATION-CRITICAL\](:|：)?`
- check-p6-format.sh:69：`[[:space:]:：]` → `([[:space:]]|:|：)`（4 处 sed 统一）
- 最小验证：`LC_ALL=C` 下 alternation 匹配全角冒号 ✓、半角行为不变 ✓
- 优点：与 v0.40.3 L84 修法同构，行为可预期；POSIX locale 下可靠
- 风险：无（语义等价，只是匹配机制从 bracket 改 alternation）
- 工作量：小

**候选 4B：强制 UTF-8 locale**
- 做法：脚本头部 `export LC_ALL=C.UTF-8`（或 POSIX 环境下 `LANG=C.UTF-8`）
- 优点：改动最小（一行）
- 风险：C.UTF-8 不是所有系统都有（busybox / 精简发行版）；改变脚本全局 locale 副作用不可控（影响所有 grep/sed）；Windows Git Bash 的 locale 命名不同——治标不治本
- 工作量：小

**选择理由**：选 4A。根因是 bracket expression 在 POSIX locale 下无法匹配多字节 UTF-8 字符，alternation 是 v0.40.3 已验证的正解；4B 依赖平台 locale 名，不满足 Windows/Linux 双平台要求。

### 1.5 M6 — md CRLF frontmatter 提取（候选 9-10）

**候选 5A：frontmatter 提取处 CRLF 归一（选定，P1 SUGGEST 已采纳）**
- 做法：所有 frontmatter 提取入口统一剥 `\r`——py 侧 `_read()` 后 `text = text.replace('\r\n', '\n')`（或 open 后 `.replace('\r', '')`）；shell 侧 `sed -n '/^---$/...'` 改为先 `tr -d '\r'` 或 `sed 's/\r$//'`
- 涉及入口：`agate-md-field-get.py`（`_read`/`_read_frontmatter`）、`agate-frontmatter-check.py`（`_extract_frontmatter_block`）、`check-gate.sh`（P1/P2 review status 的 `sed -n '/^---$/...'`）、`check-frontmatter.sh` 链路
- 优点：局部、可回归；不动历史 CRLF 文件；Windows checkout 后 md 为 CRLF 也能正确提取
- 风险：入口分散需逐一覆盖（审计范围已列全）；剥 `\r` 只针对行尾
- 工作量：中

**候选 5B：.gitattributes 加 `*.md text eol=lf`**
- 优点：源头解决（checkout 即 LF）
- 风险：.gitattributes 注释明确历史 review 文档为 CRLF 存储，加 `*.md` 会强制重写全部历史文件、污染 PR diff；影响所有仓库（不只本任务）；与 P1 SUGGEST 冲突
- 工作量：小但副作用大

**选择理由**：选 5A。P1 SUGGEST 已明确；5B 会污染历史 CRLF review 文件（BDD-16 不满足）。

### 1.6 M9 — 路径正则元字符（候选 11-12）

**候选 6A：grep -F 前缀 + 正则过滤（选定）**
- 做法：`grep -E "^${TASK_REL}/P[0-8]-.*\.md$"` 改为两级过滤：先 `grep -F "${TASK_REL}/"`（字面前缀匹配，元字符安全），再 `grep -E 'P[0-8]-.*\.md$'`（只对固定部分用正则）
- 最小验证：目录名含 `[`/`]`/`*` 时 grep -F 前缀匹配正确 ✓、非前缀不误匹配 ✓
- 优点：grep -F 是字面匹配，天然免疫正则元字符；改动集中在 L102/133/228
- 风险：两级管道失去行首锚定——`grep -F "${TASK_REL}/"` 可能匹配路径中段（如 `a/tasks/T001/` 也含 `tasks/T001/`）——需用 `awk 'index($0, p)==1'` 或保留 `^` 语义；实测 `awk -v p="$TREL/" 'index($0,p)==1'` 可保持行首
- 工作量：小

**候选 6B：re_escape 转义元字符**
- 做法：`TASK_REL` 用 sed/awk 转义正则元字符后再拼 `grep -E`
- 优点：保持单条 grep -E 模式
- 风险：转义函数本身要处理 `[`/`]`/`*`/`.` 等全部元字符（实测 sed 转义 `[` 时 charclass 陷阱多，易写错）；两处都要正确实现
- 工作量：中

**选择理由**：选 6A。grep -F 免疫性最可靠（无需维护转义表）；行首锚定用 `awk 'index($0, prefix)==1'` 替代 `^` 前缀，避免中段误匹配（实测验证）。6B 的 sed 转义在 charclass 处理上极易踩坑（本设计 §4 实测 3 次失败）。

### 1.7 Q1 — agate-next-card.sh 路径归一化（候选 13-14）

**候选 7A：归一化后剥离（选定）**
- 做法：`REL_CARD="${CARD_FILE#$AGATE_ROOT/}"` 前，先对 CARD_FILE 与 AGATE_ROOT 做归一化：统一 `/` 分隔符（`tr '\\' '/'`）、小写盘符（`sed 's/^\([A-Z]:\)/\L\1/'`）、`realpath -m`（Linux 下消除 `.`/`..`）
- 但 Linux 输出必须不变（BDD-22）：做法是"先试直接剥离，失败再归一化剥离"——Linux 下直接剥离成功 → 字节输出不变；Windows 下直接剥离失败 → 归一化后剥离成功
- 实现：`REL_CARD=$(rel_card "$AGATE_ROOT" "$CARD_FILE")`，函数内先 `rel=${CARD_FILE#$AGATE_ROOT/}`，若 `[ "$rel" = "$CARD_FILE" ]`（剥离失败）则归一化双方再剥离
- 最小验证：Linux 直接剥离 ✓ 字节不变；Windows 混合斜杠/大小写归一化后 ✓
- 优点：Linux 零行为变化（直接剥离优先）；Windows 修复了 TQC0001 实测的 4 次 hash mismatch
- 风险：归一化只在剥离失败时触发，路径语义（盘符）仅存在于 Windows，Linux 永不触发
- 工作量：小

**候选 7B：用 basename 取最后段**
- 做法：`REL_CARD=$(basename "$CARD_FILE")`（只保留文件名）
- 优点：实现最简单
- 风险：输出从 `phase-cards/P2-design.md` 变 `P2-design.md`——**破坏 hash 校验契约**（dispatch-context 里嵌入的卡片 header 用的是 `路径：phase-cards/P2-design.md`）；不满足"相对路径稳定"
- 工作量：小

**选择理由**：选 7A。7B 改变输出格式会破坏 pre-commit-gate.sh 的 hash 校验（L211-215 比较期望相对路径），不可取。7A 保持 Linux 字节不变 + Windows 归一化，是唯一同时满足 BDD-21/22 的方案。

### 1.8 Q2 — phase-cards 对齐（候选 15）

**候选 8A：参照 P5 卡补注规则 2 语义（选定，follows_existing_pattern: [agate/phase-cards/P5-verification.md]）**
- 做法：P1/P2/P3/P4/P6/P7/P8 七张卡的"更新 .state.yaml phase=Pn → Pn+1"步骤，改为与 P5 卡同款语义："**git add 时 .state.yaml 的 phase 保持本阶段，不提前写下一阶段——phase = 本 commit 的产出阶段**；phase 推进随下一阶段产出 commit 一起"。P8 卡的 `phase=READY → DONE` 为终态收尾，补注同规则
- 优点：与 git-integration.md 规则 2（L33）及 P5 卡完全一致；纯文档改动，gate 判定逻辑零改动（BDD-24）
- 风险：改 phase-cards/*.md 触发 SELF-GATE（commit message 需 `self-gate-review:`）
- 工作量：小（7 张卡，每张 1-2 行补注）

**候选 8B：保持现状（不修）**
- 优点：无改动
- 风险：卡片持续引导 mode B 旧写法（先 phase=N+1 再 commit），与规则 2 冲突，TQC0001 已实测导致 2 次真实失败
- 工作量：0

**选择理由**：选 8A。Q2 是 P0-brief 锁定的修复项（known_risk 第 5 条），8B 不解决问题。

### 1.9 Q5 — SETUP Windows 章节 + .gitignore（候选 16-17）

**候选 9A：SETUP.md 增 Windows 章节 + .gitignore 预设（选定）**
- 做法：SETUP.md 在现有「Windows（无 WSL，用 Git for Windows）」小节基础上扩展为独立章节，覆盖：AGATE_ROOT 用 Unix 风格路径（`C:/...` 或 `/c/...`，避免 `\` 转义）、PATH 注入风险（`C:\Program Files\Git` 与 python 的 PATH 顺序）、Git Bash 执行 hook、`PYTHONUTF8=1`（Windows python 默认 UTF-8 需显式）、`core.autocrlf`/CRLF 处理（引 .gitattributes）；仓库根 `.gitignore` 增加 `!version.txt` + `dist/` 相关预设条目
- 优点：文档 + 模板一次到位；platform-notes.md 已有 Windows 原生章节可交叉引用
- 风险：文档细节需准确（与 platform-notes 不矛盾）
- 工作量：中

**候选 9B：只改 platform-notes.md，SETUP 引用**
- 优点：改动最小
- 风险：SETUP.md 是"首次接入指南"，Windows 用户直接看 SETUP 却看不到 Windows 章节，可达性差（BDD-26 要求 SETUP.md 本身覆盖）
- 工作量：小

**选择理由**：选 9A。BDD-26 明确验收对象是 SETUP.md 本身；9B 不满足验收条件。

### 1.10 RM-AG0001 — check-gate.sh 反引号盲区（候选 18-19）

**候选 10A：行首标记正则加反引号容错（选定）**
- 做法：check-gate.sh P1 相关正则 `^\s*-?\s*\[(NEED_CONFIRM\]|SUGGEST:|NO_NEED_CONFIRM\]...)` 全部加可选反引号前缀：`^\s*`*-?\s*\[...`（L69/71/89/109/125/129 六处）
- 具体：`^\s*-?\s*\[` → `^[[:space:]]*`*\s*-?\s*\[` 或在匹配前 `sed 's/^` *//'` 预处理
- 最小验证：反引号包裹的 `` `[SUGGEST: ...]` `` 被计数 ✓、`` `[NEED_CONFIRM]` `` 被识别 ✓
- 优点：修 RM-AG0001 的根因（反引号在标记前阻断行首正则）；与 typo 兜底（L116/121）不冲突
- 风险：`*` 连写易误配（多反引号场景）；只影响 P1 分支
- 工作量：小

**候选 10B：只修 typo 兜底**
- 做法：仅调整 L121/125 的 SUGGEST/NEED_CONFIRM 存在性检查加反引号
- 优点：改动最小
- 风险：计数路径（L69/71/89）仍漏计 → WARNING 数不对、NEED_CONFIRM 仍不阻塞（BDD-29 要求 exit 1 阻塞）；治标不治本
- 工作量：小

**选择理由**：选 10A。BDD-28/29 验收的是计数与阻塞行为本身，10B 只改存在性检查不满足验收。

### 1.11 RM-AG0002 + TPV0090-M4 — check-tdd-red.sh A/B 判定（候选 20-21）

**候选 11A：无 formatter 关键词判定 + NameError B 类扩展（选定，一次设计覆盖 BDD-30/31/35/36/37）**
- 无 formatter 路径（RM-AG0002）：`gate-result.sh` `run_test_with_formatter` 无 fmt 分支（L93-94）或 `judge_result` 无 formatter 时，把**测试原始输出**纳入判定——exit 1 且输出含 compile/error 关键词（`SyntaxError|IndentationError|ImportError|ModuleNotFoundError|error:`）→ 判 A 类（exit 1）；普通失败（无关键词）→ 仍判正确红灯（exit 0）
- 实现方式：formatter 为空的 JSON 结果里增加 `raw_output` 字段（或让 judge_result 在无 formatter 时额外读原始输出），在 judge_result 内做关键词判断
- formatter 路径（TPV0090-M4）：B 类检测在 `import_errors` 之外增加 NameError 识别——从 formatter JSON 的 `errors` 无法细分，方案是给 pytest.sh 等 formatter 增加 `name_errors` 数组字段（解析输出中 `NameError: name 'X' is not defined`，X 为项目内未定义符号时归 B 类；PROJECT_MODULE 前缀匹配复用 import_errors 的 `count_prefix` 机制），judge_result 在 `errors > 0` 分支前先查 `name_errors`：项目模块内的 NameError → B 类（return 0）；其余 errors → 仍 A 类
- 保持向后兼容（BDD-36）：`globals().get()` 规避模式 → 失败是断言失败非 NameError → 走 `failed > 0` 分支，不受影响
- 优点：一次改动覆盖 RM-AG0002 + TPV0090-M4 两条 roadmap；A/B 判定矩阵完整（formatter 有无 × 错误类型）
- 风险：name_errors 解析要准确（误把真实测试 bug 的 NameError 判 B 类 → BDD-37 兜底：仅"项目模块内"的 NameError 归 B 类，且 NameError 之外的 TypeError 等仍 A 类）；无 formatter 关键词判定要防误判（`error:` 关键词可能出现在断言失败文本中——用更精确的 `Traceback|SyntaxError|ImportError|ModuleNotFoundError` 组合）
- 工作量：中

**候选 11B：只修 RM-AG0002（无 formatter 保守判定），不动 NameError**
- 优点：改动面小
- 风险：TPV0090-M4（BDD-35/37）未覆盖——测试引用未实现符号抛 NameError 仍被 `errors>0` 误判 A 类拦截，TDD 正常红灯被阻断
- 工作量：小

**选择理由**：选 11A。dispatch-context 明确"同文件同修，一次设计覆盖完整判定矩阵，不能只修一半"；11B 与约束冲突。

### 1.12 CI — windows-latest matrix（候选 22）

**候选 12A：protocol-tests.yml 新增 windows-latest 双平台 job（选定）**
- 做法：bats/shellcheck/consistency/gate-backstop 四个 job 各加 `strategy.matrix.os: [ubuntu-latest, windows-latest]`（或新建一个 windows-only job 跑同一组命令）；Windows 上 bats 需 `choco install bats` 或下载 bats-core，shellcheck 需下载 release 二进制
- 优点：Windows 兼容的唯一兜底验证（P0-brief 明确"不得声明已实测 Windows"）
- 风险：Windows 上 bats 安装方式与 Linux 不同（CI yaml 需分支处理）；shellcheck Windows 二进制下载路径
- 工作量：中

**候选 12B：保持 ubuntu-only**
- 优点：无改动
- 风险：无 Windows 兜底；Windows 修复无法验证（P1 capability need windows-runtime 状态 supplementable 的唯一支撑就是 CI）
- 工作量：0

**选择理由**：选 12A。BDD-33 验收对象即 protocol-tests.yml 含 windows matrix；12B 不满足。

### 1.13 其他（候选 23-26）

**候选 13A：`.agate.env` CR 剥离（选定）** — `agate-workspace-resolve.sh:33` 的 `sed 's/^AGATE_WORKSPACE=//'` 前加 `tr -d '\r'`（或 sed 加 `s/\r$//`）。替代方案：不改（风险：Windows 编辑 .agate.env 后 CRLF 残留 → 路径含 `\r` 解析失败，BDD-18 不满足）。

**候选 14A：复制模式 AGATE_ROOT 解析（选定）** — `install-hook.sh` 复制模式下写入一个标记文件 `.agate-root` 存 AGATE_ROOT 绝对路径，`pre-commit-gate.sh:26` 的 readlink 解析失败时读该标记文件兜底。替代方案：不改（风险：Windows 复制模式 hook 的 AGATE_ROOT 落到 `.git/hooks` 上层，gate 加载 scripts 失败静默放行，BDD-19 不满足）。

**候选 15A：render-dispatch-prompt sed 转义（选定）** — `agate-render-dispatch-prompt.sh:112-126` 的 sed 替换用 `awk` 的 `gsub(..., replacement)`（awk 的替换串 `&` 同样特殊，需 `sub(/&/, "\\\\&")` 或改用 envsubst/python）。替代方案：不改（风险：AGATE_ROOT 含 `&`/`|` 时替换错误，BDD-20 不满足）。

**候选 16A：RM-AG0001 与 M4 同文件协同（选定）** — check-gate.sh 的 P1 反引号 + P7 `[:：]` 两处改动同批进行（同一文件避免二次动）。替代方案：分两次改（风险：二次动同一文件增加回归窗口，P0-brief known_risk 明确要求同批）。

## 2. BDD 映射表（P1 37 条 → 设计落点）

| BDD | 设计落点 | 验证维度 |
|-----|---------|---------|
| BDD-1 | §1.1 候选 1A：空格路径 fail-open 修复 | Linux+中文 fixture |
| BDD-2 | §1.1 候选 1A：逐文件处理 | 多 .state.yaml + 空格路径 |
| BDD-3 | §1.1 候选 1A：PROCESSED_DIRS 数组化 | 空格目录不拆段 |
| BDD-4 | §1.1 候选 1A + 全量 bats | Linux 回归 |
| BDD-5 | §1.2 候选 2A：grep 断言审计 | 审计正则（Image.open 除外） |
| BDD-6 | §1.2 候选 2A：py 读中文 | 中文 md/.state.yaml |
| BDD-7 | §1.2 候选 2A：py 写中文 | retreat/card-inject 中文 |
| BDD-8 | §1.2 候选 2A + 全量 bats | Linux ASCII 回归 |
| BDD-9 | §1.3 候选 3A：中文文件名匹配 | 中文证据引用 |
| BDD-10 | §1.3 候选 3A：无扩展名拒绝 | (见截图) 负面用例 |
| BDD-11 | §1.4 候选 4A：check-gate.sh:356 | LC_ALL=C 全角冒号 |
| BDD-12 | §1.4 候选 4A：check-p6-format.sh:69 | LC_ALL=C 小写 fail 全角 |
| BDD-13 | §1.4 候选 4A：半角不变 | LC_ALL=C 半角回归 |
| BDD-14 | §1.5 候选 5A：CRLF frontmatter | CRLF md 提取 |
| BDD-15 | §1.5 候选 5A：LF 不变 | Linux 回归 |
| BDD-16 | §1.5 候选 5A（不动 .gitattributes） | 历史 CRLF 文件未被改写 |
| BDD-17 | §1.6 候选 6A：grep -F 前缀 | 目录含 [ ] * |
| BDD-18 | §1.13 候选 13A：.agate.env CR | CRLF env 文件 |
| BDD-19 | §1.13 候选 14A：复制模式 AGATE_ROOT | 复制 hook |
| BDD-20 | §1.13 候选 15A：sed 转义 | AGATE_ROOT 含 & |
| BDD-21 | §1.7 候选 7A：Q1 归一化 | Windows 盘符/反斜杠 fixture |
| BDD-22 | §1.7 候选 7A：Linux 字节不变 | Linux 输出对比 |
| BDD-23 | §1.8 候选 8A：7 卡补注 | 卡片含规则 2 语义 |
| BDD-24 | §1.8 候选 8A：commit 顺序不变 | 无 gate 逻辑改动 |
| BDD-25 | §1.8 候选 8A + consistency | worktree consistency 0 ERROR |
| BDD-26 | §1.9 候选 9A：SETUP Windows 章节 | 覆盖 5 项 |
| BDD-27 | §1.9 候选 9A：.gitignore 预设 | version.txt/dist |
| BDD-28 | §1.10 候选 10A：反引号 SUGGEST | 反引号包裹计数 |
| BDD-29 | §1.10 候选 10A：反引号 NEED_CONFIRM | exit 1 阻塞 |
| BDD-30 | §1.11 候选 11A：无 formatter A 类 | exit 1 + 关键词 |
| BDD-31 | §1.11 候选 11A：无 formatter B 类 | 普通失败红灯 |
| BDD-32 | §1.1-1.12 全量 | 全量 bats |
| BDD-33 | §1.12 候选 12A：CI windows matrix | protocol-tests.yml |
| BDD-34 | 所有 .sh 改动 + shellcheck | shellcheck -S warning |
| BDD-35 | §1.11 候选 11A：NameError B 类 | formatter name_errors |
| BDD-36 | §1.11 候选 11A：globals().get() 兼容 | 既有测试回归 |
| BDD-37 | §1.11 候选 11A：非 NameError 仍 A 类 | TypeError 等 |

## 3. 验证场景清单（S1 高风险 + 全局）

**S1 数组化后必须验证的 Linux commit 场景**（pre-commit-gate.sh 全路径）：
1. 无 .state.yaml 变更 → 不触发（现状回归）
2. 根级 .state.yaml phase 变更 + P1 产出 → 正常
3. 任务级 .state.yaml phase 变更 + P{n} 产出（T001 常规）→ 正常
4. 多任务并发：两个任务同 commit 各带 .state.yaml → 各自 gate 独立跑
5. 任务目录路径含空格（新建 fixture）→ 不再 fail-open（BDD-1/2/3）
6. PROCESSED_DIRS 场景：空格目录 + P 产出同 commit → 不误报"未处理"（BDD-3）
7. 裁剪跳阶（P2→P5 low 风险）→ 不拦截（回归）
8. PAUSED/READY/DONE phase → 跳过 gate（回归）
9. P6 阶段 + P6-evidence 证据 → P6 gate 正常（回归）

**全局 Linux 回归**：全量 bats（676 基线 + 新增用例）+ consistency 0 ERROR（--strict）+ shellcheck -S warning。

## 4. gate_commands / files_to_read / env_constraints / minimal_validation

### gate_commands（P2 固化，P3/P5 按此执行）

```yaml
gate_commands:
  P3: "bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/"
  P5: "bats agate/tests/sanity.bats agate/tests/unit/ agate/tests/regression/ agate/tests/integration/ && python3 agate/scripts/check-protocol-consistency.py --strict && shellcheck -S warning agate/scripts/*.sh"
```

> 说明：测试运行器是 bats（非 pytest），无 JSON formatter → check-tdd-red.sh 走 exit-code-only 降级路径。本任务 P3 的 A/B 判定增强测试（BDD-30/31/35/36/37）在 check-tdd-red.bats / check-tdd-red-formatter.bats 内用 TEST_RUNNER 指向 fake 脚本的方式写（AGENTS.md「mock pytest」约定），不依赖 gate_commands formatter。
> P5 是紧凑输出模式（bats 汇总 + consistency + shellcheck 单行）。

### files_to_read（P4 implementer 上下文地图）

```yaml
files_to_read:
  - path: agate/scripts/pre-commit-gate.sh
    why: S1 数组化（L45-54/56-58/337-350）+ M9 grep -F 前缀（L102/133/228）+ 复制模式 AGATE_ROOT（L26）
  - path: agate/scripts/check-gate.sh:40-133
    why: RM-AG0001 P1 标记正则（L69/71/89/109/121/125/129）+ M4 P7 BLOCKER 计数（L356/357）
  - path: agate/scripts/check-p6-format.sh:69
    why: M5 全角冒号 sed bracket → alternation（4 处）
  - path: agate/scripts/check-p6-evidence.sh:37
    why: S2 证据引用正则加宽
  - path: agate/scripts/check-tdd-red.sh
    why: RM-AG0002 无 formatter 路径 + TPV0090-M4 NameError B 类（L70/87-107/128-131）
  - path: agate/scripts/gate-result.sh:78-102
    why: run_test_with_formatter 无 formatter 分支需传递原始输出供关键词判定
  - path: agate/scripts/agate-next-card.sh:56
    why: Q1 前缀剥离归一化（L37-57）
  - path: agate/scripts/agate-workspace-resolve.sh:33
    why: 其他-a .agate.env CR 剥离
  - path: agate/scripts/install-hook.sh:25-40
    why: 其他-b 复制模式写 .agate-root 标记
  - path: agate/scripts/agate-render-dispatch-prompt.sh:108-126
    why: 其他-c sed 替换串转义
  - path: agate/scripts/agate-md-field-get.py:111-127
    why: S3 encoding + M6 CRLF 归一（_read/_read_frontmatter）
  - path: agate/scripts/agate-frontmatter-check.py:122-129
    why: M6 CRLF 归一（_extract_frontmatter_block）
  - path: agate/scripts/agate-card-inject.py / agate-retreat-state.py / agate-state-get.py / agate-changelog-unreleased.py / agate-state-yaml-check.py / agate-evidence-consistency.py / agate-vision-blocker.py / agate-gate-missing-cmds.py / agate-gate-p5-count.py / agate-read-gate-commands.py / agate-read-p5-commands.py / ci-gate-backstop.py
    why: S3 批量加 encoding（P1 §6 清单，13 个 py）
  - path: agate/assets/formatters/pytest.sh
    why: TPV0090-M4 增 name_errors 数组解析
  - path: agate/phase-cards/P5-verification.md
    why: Q2 参照样例（已对齐规则 2）
  - path: agate/phase-cards/P{1,2,3,4,6,7,8}-*.md
    why: Q2 补注目标（P1:17 / P2:13 / P3:13 / P4:16 / P6:16 / P7:14 / P8:14）
  - path: agate/git-integration.md:27-33
    why: Q2 规则 2 对齐依据
  - path: agate/SETUP.md + .gitignore
    why: Q5 Windows 章节 + version.txt/dist 预设
  - path: .github/workflows/protocol-tests.yml
    why: CI windows matrix（BDD-33）
  - path: agate/tests/unit/check-p6-format.bats:113-125
    why: F13 已覆盖 LC_ALL=POSIX 全角冒号，M5 新测试参照
  - path: agate/tests/unit/check-tdd-red-formatter.bats
    why: A/B 判定测试写法参照（FMT.4-9）
```

### env_constraints（确认/细化 P0-brief）

```yaml
env_constraints:
  debug_env: "本环境为 Linux（UTF-8 locale），Windows 需通过 CI windows-latest 验证"
  isolation_check: "所有修复在 worktree（/home/kity/oclab/agate/.worktrees/agate-TAG0004）内验证；跑 gate 用 ~/.agate（稳定版 v0.43.0），改代码/跑测试在 worktree；consistency 用 worktree 自己的 python3 agate/scripts/check-protocol-consistency.py"
```

### minimal_validation（P2 关键假设实测）

```yaml
minimal_validation:
  - assumption: "M4/M5 [:：] bracket 在 POSIX locale 下不匹配全角冒号"
    method: "LC_ALL=C 下 grep/sed 实测 [:：] vs (:|：)"
    result: "confirmed"
    note: "grep -E '\\[BLOCKER\\][:：]?...' 在 LC_ALL=C 下不匹配全角冒号（NOMATCH1），(:|：)? 匹配（MATCH2）→ 确认 M4 根因；GNU sed 的 bracket 在 LC_ALL=C 下只匹配全角冒号首字节（EF），靠 \\3 回写'碰巧'输出正确，BSD/busybox sed 不可移植 → M5 需 alternation 统一"
  - assumption: "S2 正则字符类加宽在 LC_ALL=C 下支持中文证据文件名"
    method: "LC_ALL=C 下候选正则可 grep 实测中文文件名 + 负面用例"
    result: "confirmed"
    note: "候选 3A（负类加宽）匹配 '（evidence/截图 验证通过.png）' 与 ASCII 全部现状用例；拒绝 '（见截图）' 无扩展名（BDD-10）；嵌套括号用例（report.pdf, nth(1)）保持现状"
  - assumption: "Q1 ${CARD_FILE#$AGATE_ROOT/} 前缀匹配在 Windows 盘符/斜杠下失效"
    method: "bash 实测 5 种路径形态（正斜杠/反斜杠/大小写盘符）"
    result: "confirmed"
    note: "Linux 直接剥离成功且字节不变（C4）；Windows 混合斜杠（C2/C5）或盘符大小写（C3）下剥离失败 → 需归一化后剥离（候选 7A），Linux 用'先试直接剥离'保持字节不变"
  - assumption: "RM-AG0001 反引号包裹标记不被行首正则识别"
    method: "grep -cE 实测反引号包裹的 [SUGGEST:/[NEED_CONFIRM]"
    result: "confirmed"
    note: "`` `[SUGGEST: ...]` `` 计数少 1，`` `[NEED_CONFIRM]` `` 计数为 0 → 候选 10A 正则加 `* 容错"
  - assumption: "M9 grep -E 拼路径在目录含正则元字符时失效，grep -F 可修"
    method: "真实目录名含 [ ] 时 git diff --cached 管道实测"
    result: "confirmed"
    note: "TASK_REL 含 [ 时 grep -E 前缀匹配失效；grep -F 字面匹配 + awk index($0,p)==1 行首锚定正确；sed re_escape 对 [ charclass 转义实测 3 次失败 → 弃用 6B 倾向"
  - assumption: "M6 CRLF 下 frontmatter 提取失效，tr -d '\\r' 可修"
    method: "CRLF 文件实测 sed -n '/^---$/...' 与 tr -d '\\r' 对比"
    result: "confirmed"
    note: "CRLF 下 sed frontmatter 提取输出空；tr -d '\\r'（或 sed 's/\\r$//'）后正确提取；py 侧 _extract_frontmatter_block startswith('---\\n') 对 CRLF 返回 None → 读取时剥 \\r"
```

## 5. 实现完成标志（P3/P4/P5 判定依据）

1. **S1**：pre-commit-gate.sh 数组化后，§3 场景清单 1-9 全部通过（含新增空格路径 fixture）；全量 bats 绿
2. **S3**：grep 断言审计测试绿（0 个文本 open() 缺 encoding，Image.open 除外）；13 个 py 全部加 encoding；BDD-6/7 中文读写通过
3. **S2**：中文文件名 PASS 引用 exit 0；无扩展名 PASS exit 1；现有 28 个 check-p6-evidence 用例回归绿
4. **M4/M5**：LC_ALL=C 下全角冒号总结行被正确排除/归一化；半角行为不变；check-gate P7 / check-p6-format 相关用例绿
5. **M6**：CRLF md frontmatter 提取正确；LF 行为不变；历史 CRLF 文件未被改写
6. **M9**：目录含 [ ] * 时 gate 判定正确
7. **Q1**：Linux 相对路径输出与修复前逐字节一致；Windows 路径 fixture 前缀剥离成功
8. **Q2**：7 张卡补注规则 2 语义；consistency 0 ERROR
9. **Q5**：SETUP Windows 章节覆盖 5 项；.gitignore 含 version.txt/dist 预设
10. **RM-AG0001**：反引号包裹 SUGGEST 计 WARNING、NEED_CONFIRM 阻塞
11. **RM-AG0002 + TPV0090-M4**：无 formatter A/B 判定、formatter NameError B 类、globals().get() 兼容
12. **其他**：.agate.env CR 剥离、复制模式 AGATE_ROOT 兜底、sed 转义
13. **CI**：protocol-tests.yml 含 windows-latest matrix
14. **全局**：全量 bats 绿 + consistency 0 ERROR + shellcheck 0 error

`[PROD_NOT_TOUCHED]` 本阶段仅读 worktree 内文件与 /tmp/opencode 验证用例，未接触任何生产环境。
