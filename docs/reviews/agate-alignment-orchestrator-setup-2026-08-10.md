---
review_date: 2026-08-10
reviewer: protocol-alignment-review
change_summary: orchestrator-template.md 改为对所有项目内容完全一致的符号链接接入模式（不再拷贝改字段），新增 agate/SETUP.md 首次接入指南 + agate/assets/templates/project.md 项目特定信息模板，README.md/agate/AGENTS.md/install.sh 同步更新入口指引
files_changed: [agate/orchestrator-template.md, agate/SETUP.md (新), agate/assets/templates/project.md (新), agate/AGENTS.md, README.md, install.sh]
---

# 协议-脚本对齐审查：orchestrator 符号链接接入改造

## 审查结论汇总

| # | 审查项 | 结论 |
|---|--------|------|
| A1 | 文档→脚本对齐 | ALIGNED（本次改动不涉及 gate 脚本逻辑，纯 onboarding 文档改造，无新协议规则需要脚本实现） |
| A2 | 脚本→文档对齐 | ALIGNED（install.sh 下一步提示准确指向 agate/SETUP.md） |
| A3 | 一致性连锁 + 反向传播 | **MISALIGNED**（发现 1 处占位符先于说明出现 + 1 处严重的 frontmatter 缺字段问题 + 2 处旧路径残留） |
| A4 | 测试覆盖 | ALIGNED（bats 603/603 全绿，count-tests.sh=597，consistency 0 ERROR；本质是 onboarding 文档，无需新增专门 bats 用例，现有结构性检查已覆盖） |
| A5 | 下游影响 + 文档传播 | **MISALIGNED**（CHANGELOG.md 未记录本次破坏性变更；README.md 卸载节 + 仓库根 AGENTS.md 有残留旧路径描述） |
| A6 | 锚点表覆盖 | NEEDS_HUMAN_REVIEW（`agate/SETUP.md` 未加入 check-protocol-consistency.py 的 PROTOCOL_FILES，CHECK3 硬编码行号检查不覆盖它；当前无实害但是覆盖缺口）→ 已修复，[HUMAN_CONFIRMED: 2026-08-10] |
| A7 | 设计原则一致性 | NEEDS_HUMAN_REVIEW（这是一次真实的架构决策——从"逐项目拷贝改字段"转为"全项目一致 + 符号链接"，adr.md 现有 ADR-001~007 均未覆盖，建议补 ADR-008）→ 已修复，[HUMAN_CONFIRMED: 2026-08-10] |

**未充分验证风险点：1 个**（详见「重点核查点 3」，已用二进制静态分析部分弥补，但仍非官方文档/真实会话确认）。

---

## 逐项审查

### A1: 文档→脚本对齐

本次改动的六个文件（orchestrator-template.md、SETUP.md、project.md 模板、AGENTS.md、README.md、install.sh）均不触及任何 `agate/scripts/check-*.sh`/`.py` 的判定逻辑——这是一次纯 onboarding/文档层面的改造（如何把 orchestrator-template.md 注册成平台 agent），不引入任何新的、需要 gate 脚本机器判定的协议规则。

**结论**：ALIGNED（N/A——无新规则需要脚本实现）

### A2: 脚本→文档对齐

**脚本改动**（install.sh:47-49）：
```
echo "下一步:"
echo "  在项目里按 $LINK_NAME/SETUP.md 的步骤把 orchestrator 注册成"
echo "  OpenCode/Claude Code 能调用的 agent（含装 hook 那一步）"
```

`$LINK_NAME` 默认值为 `${AGATE_SYMLINK:-$HOME/.agate}`（install.sh:10），`~/.agate` 软链接指向 `<repo>/agate/` 子目录（install.sh:9 `LINK_TARGET="$INSTALL_DIR/agate"`），因此 `$LINK_NAME/SETUP.md` 实际解析为 `agate/SETUP.md`——与新建文件的真实路径一致。

**结论**：ALIGNED

### A3: 一致性连锁 + 反向传播

#### A3a 连锁一致性

**重点核查点 1（占位符是否先于说明出现）**：

`agate/orchestrator-template.md` 第 13 行（frontmatter 后的警告 blockquote 内）：
> 项目特定信息全部只从 `{project_root}/docs/agents/project.md`（可选）+ `{project_root}/AGENTS.md`/`CLAUDE.md` 读取

而"这些占位符要靠你自己解析替换，平台不会帮你替换"的说明位于第 21-24 行的独立小节标题："## 会话开始时先解析这两个值（本文件其余部分出现的 `{agate_root}`/`{project_root}` 都指这里解析出的实际路径——你的运行平台不会替你做这个替换，占位符要靠你自己认）"。

**第 13 行的 `{project_root}` 确实出现在第 21-24 行说明之前**。这正是本次审查任务点名要挑刺的风险——不是假设性风险，而是真实存在的顺序问题。风险：模型读到第 13 行时，`{project_root}` 尚未被"这是需要自己解析的占位符"的说明覆盖，可能被当成字面文本理解（虽然大括号本身有一定占位符暗示性，但缺乏第 21-24 行那样的明确指令，读者/模型的第一印象锚点被削弱）。

第 15 行提到 `agate/SETUP.md` 是字面相对路径（非占位符），不受此问题影响。表格（第 71-82 行）、"接入"节（87-91 行）、"项目必读"节（108-114 行）里的 `{agate_root}`/`{project_root}` 均在第 21-24 行说明之后，没有类似问题。

**结论**：MISALIGNED
**差异**：警告 blockquote（第 11-15 行）先于"占位符解析规则"说明（第 21-24 行）出现，且 blockquote 内已经使用了 `{project_root}` 占位符。
**建议**：把"会话开始时先解析这两个值"这一节整体挪到 frontmatter 之后、警告 blockquote 之前（即现在的第 21-26 行提到第 9 行之后），或者至少在警告 blockquote 里把 `{project_root}` 换成一句不依赖占位符的等价描述（如"项目根目录下的 docs/agents/project.md"），把首次出现占位符的位置推迟到说明之后。

---

**重点核查点 2（project.md 路径三处一致性）**：

| 来源 | 内容 |
|------|------|
| `agate/orchestrator-template.md:110` | `` `{project_root}/docs/agents/project.md`（**若存在**——项目侧按需创建，模板见 `{agate_root}/assets/templates/project.md`；不存在则跳过这条，只读下面两条） `` |
| `agate/SETUP.md:13` | `` 项目特定信息……**只写进** `{project_root}/docs/agents/project.md`（可选文件，模板见 `assets/templates/project.md`） `` |
| `agate/SETUP.md:23`（步骤 1 代码块） | `cp {agate_root}/assets/templates/project.md docs/agents/project.md` |
| `agate/assets/templates/project.md:3` | `> 复制此文件到 \`{project_root}/docs/agents/project.md\`，按需填写后删掉本说明块。` |

四处引用的路径字面量完全一致（`{project_root}/docs/agents/project.md` 或其等价相对写法），未发现用户描述的"改到一半、个别地方还停留在旧思路（与 orchestrator.md 同目录）"的残留。

**结论**：ALIGNED

#### A3a 追加发现（非任务原始 4 个重点，审查过程中新定位到的严重问题）

**`agate/orchestrator-template.md` frontmatter 缺少 Claude Code 官方要求的 `name:` 字段**（详见「重点核查点 3」章节的完整证据链）。这不是"未知字段会不会报错"的问题，而是**必填字段缺失**——会导致 Claude Code 完全无法把 `.claude/agents/orchestrator.md` 加载为一个可用 agent，SETUP.md 描述的整个 Claude Code 接入流程（含步骤 3 的默认 agent 设置）在 Claude Code 上实际不生效。

**结论**：MISALIGNED（详见下方重点核查点 3 的完整证据）
**建议**：`orchestrator-template.md` frontmatter 增加 `name: orchestrator` 字段。

#### A3b 反向传播

按 `protocol-alignment-review.md` 常见路径表 + 本次改动的实际内容（orchestrator 接入方式从"拷贝改字段"变为"符号链接 + project.md"），全仓库 `grep -rn "orchestrator-template\|docs/agents/orchestrator"` 排查，发现两处未同步的残留：

1. **仓库根 `AGENTS.md:21`**（不在本次 diff 范围，但应受影响）：
   ```
   ├── orchestrator-template.md # 接入新项目时拷贝为 docs/agents/orchestrator.md
   ```
   这是旧"拷贝到 `docs/agents/orchestrator.md`"约定的原文，与本次改动后的新约定（`.claude/agents/orchestrator.md` / `.opencode/agents/orchestrator.md` 符号链接，`docs/agents/project.md` 才是项目侧可选文件）矛盾。`agate/AGENTS.md`（协议本体的入口指引）已经在本次 diff 里正确更新，但仓库根这份面向"修改 agate 协议的开发者"的 AGENTS.md 没有同步。

2. **`README.md:109`**（"## 卸载"一节，不在本次 diff 范围）：
   ```
   你的项目里的 `docs/agents/orchestrator.md` 等文件**不会**被删（它们独立于 agate）。
   ```
   同样是旧路径残留——新约定下项目里不会有 `docs/agents/orchestrator.md` 这个文件（那是符号链接目标改到 `.claude/agents/` 或 `.opencode/agents/` 之后腾出来给 `project.md` 用的路径）。

`agate/dispatch-protocol.md`、`agate/state-machine.md`、`agate/role-system.md`、`agate/LIMITATIONS.md` 逐一 grep 核实——均无描述 orchestrator.md 拷贝/字段填写方式的旧内容需要同步（它们只是泛引用 orchestrator-template.md 的 mapping 表功能，不涉及接入方式细节），ALIGNED。`agate/platform-notes.md` 未提及 orchestrator 注册细节，与 SETUP.md 不冲突，ALIGNED。

**结论**：MISALIGNED
**差异**：2 处旧路径描述残留（仓库根 AGENTS.md:21、README.md:109）
**建议**：
- AGENTS.md:21 改为类似 `├── orchestrator-template.md # 主 Agent 提示词，符号链接接入（见 agate/SETUP.md），不拷贝`
- README.md:109 改为类似 `你的项目里 .claude/agents/orchestrator.md、.opencode/agents/orchestrator.md（符号链接）与 docs/agents/project.md（如果创建了）等文件**不会**被删（它们独立于 agate）。`

---

### A4: 测试覆盖

实跑结果：
```
count-tests.sh → 总计：597 个测试用例（达标，与任务基线一致）
bats sanity.bats + unit/ + regression/ + integration/ → 603/603 全绿（grep 统计 ok=603, not ok=0）
python3 check-protocol-consistency.py → CHECK 1-9 全部 PASS，0 ERROR（复跑确认未被后续改动破坏）
```

本次改动是纯 onboarding 文档，没有新增可机器判定的协议规则，因此没有配套的新 bats 用例——这与该改动的性质相符（不是"该加测试而没加"，而是"这类内容本身不落在 bats 覆盖范围内"，其正确性由 CHECK1/CHECK2 等结构性检查 + 本次人工审查兜底）。

**结论**：ALIGNED

### A5: 下游影响 + 文档传播

**破坏性变更未标注**：本次改动是一次面向所有已部署项目的破坏性变更——已有项目此前按旧流程把 `orchestrator-template.md` **拷贝**到 `docs/agents/orchestrator.md` 并手改了 `project_root`/`agate_root`/平台专属字段；升级到本次改动后的新版协议，这些项目的旧拷贝不会自动获得新模板的任何改进（`{agate_root}`/`{project_root}` 解析指令、project.md 分离等），需要人工迁移到符号链接方式。检查 `CHANGELOG.md`（`git diff --stat -- CHANGELOG.md` 为空，说明本次改动完全没有触碰这个文件），**当前 [0.40.0] 条目只记录了 T001 结构化数据改造，完全没有提及这次 orchestrator 接入方式的改造**。

**文档传播**：见 A3b——README.md 卸载节 + 仓库根 AGENTS.md 两处残留未同步。

**结论**：MISALIGNED
**差异**：CHANGELOG.md 未记录本次破坏性变更；两处文档传播遗漏（同 A3b）
**建议**：在 CHANGELOG.md `[0.40.0]` 或新增条目下补充说明本次 orchestrator 接入方式变更（旧项目的手动迁移路径：删除拷贝的 `docs/agents/orchestrator.md`，改为按 `agate/SETUP.md` 建立符号链接，如有项目特定信息迁移到新建的 `docs/agents/project.md`）。

### A6: 锚点表覆盖

`agate/scripts/check-protocol-consistency.py` 的 `PROTOCOL_FILES`（第 45-56 行）显式列出 `agate/orchestrator-template.md`，但**新文件 `agate/SETUP.md` 未加入**（既不在 `PROTOCOL_FILES` 集合里，也不匹配 `PROTOCOL_DIRS = ("agate/assets/",)` 前缀）。

影响面核实：
- `is_protocol_file("agate/SETUP.md")` → `False`
- CHECK 2（死链检查，`check_internal_refs`）：不区分 protocol/非-protocol，只区分 narrative/非-narrative；`agate/SETUP.md` 不落在 `NARRATIVE_DIRS` 里，所以仍按"非叙事文件"从严检查（死链 → ERROR）。**不受影响，仍被覆盖**。
- CHECK 3（硬编码行号引用检查，`check_line_refs`）：显式 `if not is_protocol_file(relpath): continue`，只检查 protocol file。`agate/SETUP.md` **不会被 CHECK 3 检查**。当前 SETUP.md 全文没有 `xxx.md L\d+` 这种硬编码行号引用，所以现在没有实际漏报；但这是一个结构性覆盖缺口——未来如果有人在 SETUP.md 里加了类似 `见 orchestrator-template.md L52` 这种引用，不会被拦截。

`agate/assets/templates/project.md` 落在 `agate/assets/` 下，被 `PROTOCOL_DIRS` 覆盖，无此问题。

CHECK 9（gate 脚本-协议锚点表）与本次改动无关——本次不触及任何 `check-*.sh` 判定逻辑，无需新增锚点。

**结论**：NEEDS_HUMAN_REVIEW
**理由**：不是"当前判断有误"的硬缺陷（现状无实际漏报），是否值得为一个纯 onboarding 指南文件升格为 protocol file 级别的严格检查，属于取舍判断而非可机械判定的对错。
**建议**：`PROTOCOL_FILES` 加入 `"agate/SETUP.md"`，成本很低（一行），可以直接采纳而不必等人工确认；但按角色规则，NEEDS_HUMAN_REVIEW 项仍需要人工 `[HUMAN_CONFIRMED: ...]` 才能 commit。
[HUMAN_CONFIRMED: 2026-08-10 用户确认：`PROTOCOL_FILES` 已加入 `agate/SETUP.md`，consistency 检查复跑 0 ERROR，全量 bats 复跑 603/603]

### A7: 设计原则一致性

`agate/adr.md` 现有 ADR-001 至 ADR-007，逐条 grep 核实（关键词：orchestrator / 符号链接 / 软链接 / project.md）均**无命中**——没有任何现有 ADR 覆盖"orchestrator-template.md 从逐项目拷贝改字段，改为对所有项目内容完全一致、标准接入方式为文件级符号链接，项目特定信息分离到可选的 project.md"这一决策。

这是一次实质性的架构决策（改变了核心提示词文件的分发/维护机制，直接影响所有下游项目的接入方式），落在 protocol-alignment-review.md A7 规则"如发现未记录的架构决策，建议补充新 ADR"的适用范围内。

**结论**：NEEDS_HUMAN_REVIEW（A7 规则本身不存在 MISALIGNED）
**建议**：补 `ADR-008`，记录：
- 决策：orchestrator-template.md 单文件符号链接接入，不再逐项目拷贝改字段；项目特定信息分离到可选的 `{project_root}/docs/agents/project.md`
- 动机：旧模式下 (1) agate 升级模板后已部署项目不会自动跟着更新 (2) 缺少"如何注册成平台可调用 agent"的指引
- 权衡：Windows 无符号链接权限场景退化为复制模式，牺牲自动同步能力（SETUP.md 已文档化此权衡）
[HUMAN_CONFIRMED: 2026-08-10 用户确认：`agate/adr.md` 已补 ADR-008，记录决策/理由/权衡/后果]

---

## 重点核查点详情

### 重点核查点 1：占位符是否先于"自行解析"说明出现

见上文 A3a。**结论：存在真实问题**——第 13 行警告 blockquote 里的 `{project_root}` 出现在第 21-24 行的占位符解析说明之前。建议修复方向已给出。

### 重点核查点 2：project.md 路径三处一致性

见上文 A3a。**结论：三处（实为四处引用）完全一致**，均为 `{project_root}/docs/agents/project.md`，未发现"改到一半、个别地方停在旧思路"的残留。审查时特别检查了 `agate/orchestrator-template.md:110`、`agate/SETUP.md:13/23`、`agate/assets/templates/project.md:3` 四处原文，逐字比对确认。

### 重点核查点 3：Claude Code frontmatter 未知字段处理 + 缺失必填字段（本次审查最重要的发现）

**验证方式**：本机已装 Claude Code CLI 2.1.226（`@anthropic-ai/claude-code` npm 包，实际执行体是原生二进制 `bin/claude.exe`，Node wrapper 仅为 fallback）。由于没有等价于 OpenCode `opencode debug agent <name>` 的"空跑校验"命令（`claude agents --json` 实际列的是后台/交互**会话**列表，不是自定义 agent 定义，见下方附带发现），本次审查改用**字符串级反汇编**对二进制做静态分析，定位到自定义 agent 加载的实际代码路径，作为不消耗真实会话/API 调用的验证手段。

**证据链**（原始命令与输出见留痕文件对应条目，此处摘录关键代码片段）：

1. 定位 markdown frontmatter 解析函数 `eCr()`：
   ```js
   let{frontmatter:l,content:c}=qp(a,s,{normalizeKeys:!0});
   return{filePath:s,frontmatter:l,content:c}
   ```
   用 `qp(...)` 解析 YAML frontmatter，**没有任何"用文件名回填 name 字段"的兜底逻辑**——frontmatter 里没写什么字段，解析结果就是没有。

2. 定位 agent 加载函数 `yfd(e,t,r,n,o)`（`r` = frontmatter 对象）：
   ```js
   function yfd(e,t,r,n,o){
     try{
       let{name:i,description:s}=r;
       if(!i||typeof i!=="string")return null;
       ...
   ```
   **`name` 字段直接从 frontmatter 解构，缺失或非字符串直接 `return null`**——文件被完全排除在已加载 agent 列表之外。

3. 定位外层调用处：
   ```js
   let m=yfd(c,u,d,p,f);
   if(!m){
     if(!d.name)return null;   // 无 name：连警告日志都不打印，直接跳过
     let h=Yh_(d);
     return w(`Failed to parse agent from ${c}: ${h}`), O("tengu_agent_parse_error",{error:h,location:ge(f)}), null
   }
   ```
   确认：**没有 `name` 字段是最沉默的失败路径**——不报错、不警告，文件就是"不存在"。只有当 `name` 存在但校验其他字段失败时，才会打印警告 + 发送遥测事件。

4. 同时确认了**未知字段（如 `mode`、`permission`）的处理**：`yfd()` 后续按已知字段名逐个手工读取（`color`、`model`、`background`、`memory`、`isolation`、`effort`、`permissionMode`、`maxTurns`、`tools`、`disallowedTools`、`skills`、`initialPrompt`、`observer`/`observerMessage`/`observeSubagents`、`mcpServers`），构造最终 agent 对象时用条件展开逐个拼装（`...a&&...{color:a}` 这种写法），**全程没有对 frontmatter 做 zod `.strict()` 或"拒绝未知键"的校验**（binary 里确实存在 `unrecognized_keys`/zod 严格模式相关字符串，但出现在别的、与此 agent 加载路径无关的地方）。

**结论**：

| 问题 | 结论 | 依据 |
|------|------|------|
| Claude Code 会不会因为看到 `mode`/`color`/`permission` 这些不认识的字段而**报错** | **不会**——会静默忽略未知字段，这部分原设计的"网络检索 + 类比推断"是对的 | 上述反汇编证据 4 |
| Claude Code 是否会实际**使用** `mode`/`permission` 这两个字段产生效果 | **不会**——它们不在 Claude Code 已知字段集合内，纯粹是死字段，只对 OpenCode 有意义 | 上述反汇编证据 4（已知字段枚举中没有 `mode`/`permission`） |
| 当前 orchestrator-template.md frontmatter（只有 `description`/`mode`/`color`/`permission`）在 Claude Code 上能否被成功加载为 `orchestrator` agent | **不能**——缺少必填的 `name` 字段，会被**静默跳过**，不出现在已加载 agent 列表里 | 上述反汇编证据 1-3 |

第三条是本次审查在"重点核查点 3"框架下意外定位到的、比原始问题更严重的缺陷：**不是"字段会不会导致报错"，而是"整个 agent 根本不会被加载"**。SETUP.md 里 Claude Code 的全部注册步骤（符号链接、`claude agents --json` 验证、步骤 3 设默认 agent 的 `.claude/settings.json {"agent": "orchestrator"}`）建立在"agent 名字是 orchestrator"这个假设上，而这个名字从未在 frontmatter 里出现过。

**附带发现**：SETUP.md:42-45 给出的验证命令
```bash
claude agents --json    # 能跑通说明 CLI 环境正常，具体 agent 解析暂无独立校验命令，直接开会话确认最准
```
本次审查实测（`claude agents --json`）确认该命令返回的是**当前活跃的后台/交互会话列表**（`pid`/`cwd`/`sessionId`/`status` 等字段），**与 `.claude/agents/` 目录下的自定义 agent 定义完全无关**。命令本身能跑通，但跑通与否不能说明任何关于 orchestrator agent 是否注册成功的信息——这一步的验证价值基本为零，容易给读者"我验证过了"的错觉。SETUP.md 注释里虽然已经写了"具体 agent 解析暂无独立校验命令"，但仍然给出了这条命令，措辞上容易被当作有效验证步骤误用。

**验证方式的局限性声明**：以上结论基于对已安装的 Claude Code CLI **2.1.226** 版本二进制做字符串级反汇编得出，是可复核的静态证据（比单纯网络检索/类比推断更可靠），但不是官方文档的正式确认，也不是真实会话的端到端验证；后续版本升级可能改变解析逻辑，建议在正式发布前用真实的 `.claude/agents/` 目录做一次端到端验证（哪怕只是最小化验证：符号链接 + 补上 `name: orchestrator` 之后，用 `claude --agent orchestrator -p "echo test"` 之类的最小 prompt 跑一次，确认能选中且不报错，成本远低于完整任务会话）。

**建议**：`agate/orchestrator-template.md` frontmatter 加一行 `name: orchestrator`（这也是 OpenCode 侧后续步骤 `.opencode/agents/orchestrator.md` 隐式假设的名字——OpenCode 的自定义 agent 命名通常也是从文件名或显式 `name` 字段决定，建议一并确认 OpenCode 侧是否也需要显式 `name` 字段，本次审查未针对这点做同等深度的 OpenCode 二进制验证，仅验证了 Claude Code）。

### 重点核查点 4：README.md / AGENTS.md / SETUP.md 三处接入方式描述一致性

见上文 A3b。**结论**：`README.md`「快速上手」、`agate/AGENTS.md`「你要做什么」表均已正确改为"符号链接"表述，与 `agate/SETUP.md` 一致；**但仓库根 `AGENTS.md:21` 和 `README.md:109`（卸载节）两处残留了旧的"拷贝到 docs/agents/orchestrator.md"表述**，未随本次改动同步。已在 A3b/A5 中给出具体修复建议。

### install.sh 下一步提示

见上文 A2。**结论**：ALIGNED，`$LINK_NAME/SETUP.md` 路径解析正确。

---

## 人工验收清单

- [x] 审查报告含 A1-A7 七项，每项有结论
- [x] MISALIGNED 项（A3、A5）有差异描述 + 建议方向
- [x] NEEDS_HUMAN_REVIEW 项（A6、A7）下面的 `[HUMAN_CONFIRMED: ...]` 标记——2026-08-10 用户已确认，两项建议均已实现（`PROTOCOL_FILES` 加入 `agate/SETUP.md`；`agate/adr.md` 补 ADR-008），可以 commit
- [x] 审查报告落盘到 `docs/reviews/agate-alignment-orchestrator-setup-2026-08-10.md`
