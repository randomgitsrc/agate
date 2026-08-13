---
phase: P4
task_id: TAG0004-env-adaptation
type: review
parent: P4-implementation.md
trace_id: TAG0004-P4-20260813
status: approved
created: 2026-08-13
agent: cso
---

# P4 安全评审（cso）— TAG0004-env-adaptation

**评审对象**：五份 P4-implementation（group1/2/3a/3b/m6-shell）+ `agate/scripts/` 实际 diff + `.github/workflows/protocol-tests.yml` + `agate/SETUP.md` + `.gitignore`。
**方法论**：OWASP Top 10 + STRIDE 视角，聚焦本任务特殊性——改的是 agate 协议自身脚本（gate/hook/py 工具/CI），重点看改动是否引入**新的**安全脆弱点，而非业务应用漏洞。
**结论**：`status: approved`（无 CRITICAL / 无 HIGH；MEDIUM 2 项均为已声明的设计偏差或 CI 硬化缺口，不阻断发布；LOW 4 项为文档性观察）。

---

## 1. STRIDE 矩阵

| STRIDE 类别 | 相关改动 | 评估 | 风险 |
|-------------|---------|------|------|
| **Spoofing**（伪造） | group2 pytest.sh `name_errors` 文本解析 + judge_result 无前缀门禁的 B 类判定（`agate/assets/formatters/pytest.sh` + `agate/scripts/check-tdd-red.sh:118-129`） | 测试输出含 `NameError: name 'X' is not defined` 字面量即被计为 name_error → 判 B 类红灯（exit 0）。可伪造 A/B 判定结果。缓解：① 精确形态正则（见 §3.1）；② 无代码执行；③ P5 gate 独立跑真实测试兜底，最坏影响是浪费一个 P4 实现轮次。 | **MEDIUM** |
| **Tampering**（篡改） | 其他-b `.agate-root` 标记文件（`install-hook.sh` 写 / `pre-commit-gate.sh:30-33` 读） | 标记内容直接作为 AGATE_ROOT 参与 `source`（`pre-commit-gate.sh:37-47`）。篡改标记可指向攻击者目录执行其 `gate-result.sh`。缓解：`.git/hooks/` 可写者本可替换 pre-commit hook 本身，信任边界未扩大；脚本目录缺失时 fail-closed（`source || exit 1`）。 | **LOW** |
| **Repudiation**（抵赖） | `raw_output` 字段（`gate-result.sh:93-100`）经 `agate-json-get.py escape`（`json.dumps`）转义写入 JSON；`.gate-result.json` 仍由 `write_gate_result` 原样记录 | JSON 转义正确，无注入/伪造审计记录面；无新抵赖路径。 | LOW |
| **Information Disclosure** | gate 输出/log、`.agate-root` 读取、SETUP.md Windows 章节 | 新增输出不含敏感信息；`raw_output` 只进内存（`check-tdd-red.sh:77`）不落盘；gate 报错回显路径为既有行为。Windows 中文路径处理（13 py encoding）无泄露。 | LOW |
| **Denial of Service** | S2 负类加宽正则（`check-p6-evidence.sh:37`）、RM-AG0001 反引号正则（`check-gate.sh`）、M4 alternation、pytest.sh name_errors 正则 | 无嵌套量词/灾难性回溯（见 §3.3）；grep 走 DFA；输入为单行文本，长度受控。 | LOW |
| **Elevation of Privilege** | Q1 `rel_card`/`lower_drive`（`agate-next-card.sh`）、M9 awk（`pre-commit-gate.sh:109/112/...`）、其他-c `esc_repl`（`agate-render-dispatch-prompt.sh`）、S1 数组化 | 无 eval/无注入；awk `-v` 字面传参 + `index()` 前缀匹配免疫正则元字符（见 §3.2）；S1 数组化消除切词注入（见 §3.4）。 | LOW |

## 2. 严重性分级

| 级别 | 数量 | 条目 |
|------|------|------|
| CRITICAL | 0 | — |
| HIGH | 0 | — |
| MEDIUM | 2 | M-1 无前缀 NameError 判 B 类（group2 DESIGN_GAP）；M-2 CI shellcheck/bats 下载无 checksum 校验 |
| LOW | 4 | L-1 awk `-v` 反斜杠转义（M9 降级分支）；L-2 `.agate-root` 标记内容未校验；L-3 raw_output 关键词判定误报方向 fail-closed（可用性）；L-4 `sed '\r'` 非 GNU sed 移植性（超出 CI 矩阵） |

---

## 3. 逐项评估（含实质锚点）

### 3.1 M-1 [MEDIUM] — group2 无前缀 NameError 判 B 类 + pytest.sh 文本解析欺骗面

- **锚点**：`agate/scripts/check-tdd-red.sh:118-129`（`name_errors_count > 0` 分支：前缀匹配仅影响措辞，未匹配/裸符号一律 `return 0` 判 B 类）；`agate/assets/formatters/pytest.sh`（`re.finditer(r".*NameError: name '([^']+)' is not defined.*", output)`）；`agate-workspace/tasks/TAG0004-env-adaptation/P4-implementation-group2.md:36-38`（DESIGN_GAP 声明）。
- **评估**：P2-design 候选 11A（`P2-design.md:235`）明确"**仅项目模块内**的 NameError 归 B 类"，但实现选择了"检测到 NameError 即 B 类"。这是对设计意图的放宽，group2 已用 [DESIGN_GAP] 显式声明并经 dispatch-context 获知（上游关联节明确"不涉及安全面"）。安全面确认：① 无任意代码执行——正则只解析文本；② 欺骗面 = 测试输出含精确 `NameError: name 'X' is not defined` 字面量（格式非常特定，普通断言输出不含此形态）才会触发；③ 即便误判，P5 verifier 跑真实测试独立验证，最坏影响是 A 类测试 bug 被当红绿灯放行一个 P4 轮次后于 P5 暴露。**判定：不阻断，但建议后续硬化**（如要求 `name_errors` 仅来自 pytest 真实 traceback 行的 `\s*NameError:` 前缀、或恢复 P2 的 module 前缀门禁同时放宽 fixture）。BDD-37（TypeError 仍 A 类）已由精确正则 + `errors>0` 兜底满足，非过宽到所有 errors。
- **结论**：接受（已声明的设计偏差），不阻塞。

### 3.2 命令/路径注入（M9 / Q1 / 其他-c）— 通过

- **M9**：`pre-commit-gate.sh:109/112/141/239/301` 改为 `awk -v p="${TASK_REL}/" 'index($0, p) == 1'`。`awk index()` 是字面子串匹配，非正则——目录含 `[`/`*` 免疫（P2 §4 minimal_validation 实测确认）。行首锚定 `index(...)==1` 保留 `^` 语义防中段误匹配。**无注入**。
- **L-1 [LOW]**：awk `-v` 赋值会处理反斜杠转义（gawk 行为，如 `\t`）。正常路径下 `TASK_REL` 来自 `realpath`（Linux/Git Bash 均输出正斜杠），仅 `realpath` 失败回退 `echo "$TASK_DIR"` 且 TASK_DIR 含反斜杠时才可能被转义。实际影响：前缀匹配失败 → STAGED_OUTPUTS 为空 → 对应一致性 WARNING 静默跳过（fail-open 仅限 WARNING 级检查，非 gate 拦截）。观察项，不阻断。
- **Q1**：`agate-next-card.sh` `lower_drive`/`rel_card` 只用 bash 参数替换 + `tr`，无 eval/无 sed 注入面；归一化仅在直接剥离失败时触发，Linux 字节输出不变（BDD-22）。**通过**。
- **其他-c**：`agate-render-dispatch-prompt.sh` `esc_repl()`（`sed 's/[&|/\\]/\\&/g'`）对 `&`/`|`/`/`/`\` 双重转义，GNU sed 语义下替换串字面插入正确（`\&`→`&`、`\\`→`\`、`\/`→`/`、`\|`→字面 `|` 且不充当 `s|..|..|g` 定界符）。**通过**（BSD/macOS sed 未纳入本任务 CI 矩阵，L-4 观察）。

### 3.3 正则 DoS — 通过

- **S2** `\([^()]*[^()[:space:]]\.[a-zA-Z0-9]+[^)]*\)`（`check-p6-evidence.sh:37`）：`[^()]*` 与 `[^()[:space:]]` 字符集重叠产生回溯歧义，但 ① GNU grep 用 DFA 匹配（线性）；② 无嵌套量词（`[^)]*` 为单层）；③ 输入为单行 review 文本长度受控。非灾难性回溯。
- **RM-AG0001** `^\s*`*-?\s*`*\[NEED_CONFIRM\]`（`check-gate.sh:70/72/92`）：`\s*` 后跟字面反引号 + `*` 量词、`-?`、`\s*`、反引号 `*`、字面 `\[`——无嵌套量词，锚定 `^` 下线性。**通过**。
- **M4** alternation `(:|：)?`、**M5** `([[:space:]]|:|：|$)`：固定分支，无回溯风险。**通过**。
- **pytest.sh name_errors** `.*NameError: name '([^']+)' is not defined.*`：`.*`+字面前缀，Python re 回溯最坏 O(n)（单行内找字面），非灾难性。**通过**。

### 3.4 编码/字符处理（S3 / M6 / 其他-a）— 通过

- **S3**：14 个 py 文本 `open()` 全部加 `encoding="utf-8"`（group3a 清单 20 处 + `agate-frontmatter-check.py`），写回类（`agate-retreat-state.py:42/49`）保留 `allow_unicode=True`。grep 断言审计 `agate-scripts-encoding.bats:19-23` 用 `(?<!Image\.)\bopen\(` 排除二进制，逐行查 `encoding=`。**通过**。
- **M6**：shell 侧 `sed -n 's/\r$//; /^---$/,/^---$/p'`（`check-gate.sh` 8 处）只剥**行尾** `\r`，不破坏行中内容；LF 文件 `s/\r$//` 无匹配行为不变（BDD-15）。py 侧 `.replace("\r\n", "\n")` 同理。`\r` 在文件名/内容行中（非行尾）不受影响。**通过**。
- **其他-a**：`.agate.env` 值 `tr -d '\r'`（`agate-workspace-resolve.sh:33`）——`tr -d` 移除值内所有 `\r`，路径含行中 `\r` 场景理论存在但实践中不存在，可接受。

### 3.5 hook 信任链（其他-b）— LOW，信任边界未扩大

- **锚点**：`install-hook.sh:37-40`（复制模式写 `$HOOK_DIR/.agate-root`）；`pre-commit-gate.sh:30-33`（`[ ! -d "$AGATE_ROOT/scripts" ]` 且标记存在时读入 AGATE_ROOT）；随后 `pre-commit-gate.sh:37/46` 以该值 `source`。
- **评估**：标记内容未做绝对路径/存在性校验，篡改可重定向 `source` 的 gate-result.sh → 提交时 RCE。但**信任边界未扩大**：`.agate-root` 位于 `.git/hooks/`，能写该目录的攻击者本可直接替换 `pre-commit` hook 实现 RCE；安装流程由 `install-hook.sh` 写入正确值。且 `scripts/` 缺失时 `source` 失败走 `exit 1`（fail-closed，不静默放行——原复制模式行为是"加载不完整退出"，行为不退化）。**观察项**：建议读取时校验标记为绝对路径且 `-d $AGATE_ROOT/scripts`（当前已有等价隐式校验，硬化为显式更稳）。

### 3.6 敏感数据 — 通过

- `raw_output` 仅在本进程内用于关键词判定（`check-tdd-red.sh:77`），不写入 `.gate-result.json`/`.gate-history.jsonl`（`write_gate_result` 记录的是 gate 输出原文，为既有行为）；JSON 注入经 `json.dumps` 转义（`agate-json-get.py:25-26`）免疫。**通过**。
- 新增输出（`TDD_CHECK:` 行、GATE 报错）不含 AGATE_ROOT 绝对值之外的新敏感信息；Windows 路径/中文路径不回显到日志。**通过**。

### 3.7 CI 安全（windows-latest matrix）— 通过，含硬化建议

- **锚点**：`.github/workflows/protocol-tests.yml`。
- **评估**：① bats 从官方 `github.com/bats-core/bats-core` 固定 tag `v1.10.0` clone（`--depth 1 --branch`），非 master 漂移，来源可信；② shellcheck 从官方 release `v0.10.0` zip 下载（HTTPS）；③ 无密钥/令牌处理（默认 GITHUB_TOKEN 仅 checkout）；④ 无 `eval`、无不可信脚本注入（全部官方源）。
- **M-2 [MEDIUM]**：shellcheck zip 未做 SHA256 校验（供应链硬化缺口）。github.com 官方 release 经 HTTPS + 版本 pin 属行业常规做法，风险较低；但加 checksum 校验成本极低，建议后续补上（不阻塞本次发布）。bats clone 同理可加 `verify-commit`/checksum，但固定 tag 已可接受。
- **可用性观察**（非安全）：windows-latest 上 `unzip` 可用性、`python` vs `python3` 命令适配已处理；`defaults.run.shell: bash` 保证跨平台一致。若 Windows job 首跑失败，属 CI 可靠性问题，不构成安全缺陷。

### 3.8 RM-AG0002 raw_output 关键词判定 — fail-closed，通过

- **锚点**：`check-tdd-red.sh:89-94`（`exit_code == 1` 且 raw_output 含 `Traceback|SyntaxError|ImportError|ModuleNotFoundError` → A 类 exit 1）。
- **评估**：关键词为精确组合（不含裸 `error:`，P2 风险节已要求），误判方向是**过度拦截**（真实 B 类红灯被拦为 A 类 → 重试），属 fail-closed，可用性影响可接受。`exit==1` 限定避免破坏 TD.4-8（exit 2 + 文本期望 exit 0）既有语义。**通过**。

## 4. 其余 BDD 相关安全面抽样确认

- **S1 数组化**（`pre-commit-gate.sh:52/58/65/349/357-363`）：`+=("$REPO_ROOT/$f")` 与 `"${STAGED_STATE_FILES[@]}"` 全部引号保护，`is_processed_dir` 数组遍历精确 `=` 比对——消除空格切词 fail-open（BDD-1/2/3），无注入面。**通过**。
- **M4/M5 全角冒号**：alternation 与 v0.40.3 L84 修法同构，POSIX locale 下行为正确（P2 §4 minimal_validation 实测 MATCH2）。**通过**。
- **编码审计测试**（`agate-scripts-encoding.bats`）：`errors='replace'` 读自身文件、lookbehind 排除 `Image.open`、`encoding=` 同行检查——作为回归拦截充分（多行 open() 漏检在 14 个 py 单行风格下不成立）。**通过**。

## 5. 结论

STRIDE 全维度无 CRITICAL/HIGH。MEDIUM 2 项：M-1（NameError 无前缀 B 类判定）为已声明的设计偏差、无代码执行、P5 兜底，**接受**；M-2（CI 下载无 checksum）为供应链硬化建议，不阻断。LOW 4 项均为观察/硬化建议。改动整体保持"Linux 基线不变 + Windows 增量"约束，未引入新的命令注入、路径注入、正则 DoS、敏感数据泄露或信任边界扩大。**评审通过（approved）。**

`[PROD_NOT_TOUCHED]` 本评审仅读 worktree 内文件与 git diff，未修改任何代码/文档，未接触生产环境。
