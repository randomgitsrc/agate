# 命令流日志数据源实机验证记录

> 对应验证任务的执行交接单（验证过程临时产物，未入库；本记录为最终留档）。
> 验证目的：确认 `design-subagent-liveness-and-self-dispatch-v5-with-cmdstream-validation.md` §3.4.2 的**数据源假设**在真实会话记录里成立。
> 检测逻辑已由 `verify_cmdstream_detection.py` 虚拟时钟模拟验证，本次只验证数据源，不重新验证检测逻辑。

## Claude Code 验证结果（2026-09-03，版本 2.1.246）

- 路径规则：`~/.claude/projects/<sanitized-cwd>/<sessionId>.jsonl`，目录名 = 绝对 cwd 去掉开头的 `/`、`/` 换成 `-`；每个会话一个 `.jsonl`，另有同名 sidecar 目录存 `tool-results/` 和 `subagents/agent-<uuid>.jsonl`（子 agent 独立转录文件）
- 格式：JSONL，每行一个完整 JSON 对象，0 行解析失败；事件类型含 `assistant` / `user` / `attachment` / `system` 等；工具调用嵌套在 `assistant` 行的 `content[]`（`tool_use` part），结果在下一行 `user` 行（`tool_result` part），通过 `sourceToolAssistantUUID` ↔ `uuid` 配对
- Q3 时间戳：字段 `timestamp`，ISO-8601 UTC，**毫秒精度**；`tool_use` 行（命令开始）和 `tool_result` 行（命令结束）都有，实测配对间隔 87–384 ms；`system` 行的 `turn_duration` 还带 `durationMs`
- Q4 命令内容：完整命令文本在 `tool_use` part 的 `input.command`（工具名在 `name`），多行复合命令原样保留
- Q5 exit code：**没有数字 exit code 字段**，两个替代信号：`tool_result.is_error` 布尔（实测 250 False / 10 True）+ 失败输出文本前缀 `"Exit code N\n"`（实测到 1/2/8/123）；`toolUseResult` 另有 `interrupted` / `isImage` / `noOutputExpected`
- Q6 输出内容：完整 stdout/stderr，两处存：结构化 `toolUseResult.stdout/stderr` + 合并 `message.content[].content`；实测 stdout+stderr 最大 6,516 字符、tool_result content 最大 19,296 字符，本次文件中未出现截断标记（Bash 工具 ~30k 字符上限的截断标记在其他会话出现过，本批未命中）
- Q7 实时/延迟写入：**实时写入**。最强证据是 17 个子 agent 转录文件 mtime 比最后一条内容时间戳只晚 95–140 ms，且每行结尾都是完整 JSON 对象；主文件关闭时追加无时间戳的收尾行（`last-prompt` / `file-history-snapshot`）
- 结论：**通过**（4 项关键字段——时间戳/命令内容/exit 信号/实时写入——全部正向）。备注：exit code 需解析 `is_error` + 文本前缀，无数字字段；子 agent 是独立转录文件需注意
- 附样例（脱敏）：

  ```json
  {"type":"tool_use","id":"toolu_01...","name":"Bash",
   "input":{"command":"find /home/kity/oclab/agate -maxdepth 4 -iname \"HANDOFF-TAG0025.md\" 2>/dev/null"}}
  {"tool_use_id":"toolu_01...","type":"tool_result",
   "content":"Exit code 1\nAGATE_CARD 注入失败: ...","is_error":true}
  ```

## OpenCode 验证结果（2026-09-03，版本 1.18.11）

- 路径规则：**单一 SQLite 库** `~/.local/share/opencode/opencode.db`（WAL 模式，当前约 8.4 GB）+ `opencode.db-wal`；会话表 16 张，关键表 `session`（1,259 行）/ `message`（51,663 行）/ `part`（214,122 行）/ `event`（816,217 行）；ID 命名 `ses_`/`msg_`/`prt_`/`call_` + 26 位 hex
- 格式：SQLite，结构化字段 + `data` 列存 JSON blob（`message.data` / `part.data` / `event.data`）；工具记录在 `part.data` 的 `state` 嵌套对象里
- Q3 时间戳：毫秒精度 epoch ms，多级都有。工具级 `state.time.start` / `state.time.end` = **命令开始和结束时间**（实测 ping 复合命令 14 ms 间隔）；另有 `part.time_created/updated`、`message.data.time.created/completed`、`session.time_created/updated`
- Q4 命令内容：完整命令在 `part.data.state.input.command`（工具名在 `state.tool` 或 `tool` 字段，实测 `"tool":"bash"`），多行/`&&`/heredoc 原样保留；`state.title` 是截断预览
- Q5 exit code：`state.metadata.exit` 整数，全部 bash 工具 part 分布 `0`×25,381 / `1`×1,041 / `2`×154 / `128`×32 / `127`×29 等；等价标志 `state.status`：`completed`×56,665 / `error`×386 / `running`×27 / `pending`×6（非 bash 工具可能 exit 为空但 status=error）
- Q6 输出内容：`state.output` + `state.metadata.output`，max 实测 109,474 字符（未截断 max 57,007）；截断是**显式标记** `state.metadata.truncated`（true×5,862 / false×50,803），超大输出 spill 到 `~/.local/share/opencode/tool-output/tool_<id>` 并在 inline 里留指引
- Q7 实时/延迟写入：**实时写入**。证据：WAL mtime = 当前时刻（正在写）；最近几分钟有活跃会话且有 in-flight part；`event` 表是实时写前事件流，一次工具调用以 `pending → running → completed` 多行 event 呈现
- 结论：**通过**（4 项关键字段全正向，且 exit code 是干净的整数字段）。备注：spill 文件名与 part/call ID 无法直接 join（只能从 inline 输出文本里引用）；部分 error 工具 part 缺 `metadata.exit`
- 附样例（脱敏）：

  ```json
  {"type":"tool","tool":"bash","callID":"call_qqosxv...",
   "state":{"status":"completed",
     "input":{"command":"ip -brief addr; echo '---'; ip route; ..."},
     "output":"lo  UNKNOWN  127.0.0.1/8 ...",
     "metadata":{"output":"...","exit":0,"truncated":false},
     "time":{"start":1788245301014,"end":1788245301028}}}
  ```

## 汇总判定

| 判定项 | Claude Code | OpenCode |
|---|---|---|
| Q1 路径规则 | 明确：projects 目录 + sessionId.jsonl | 明确：SQLite 库 + 表 |
| Q2 格式 | JSONL（好解析） | SQLite + JSON blob（可用 sqlite3 只读查询） |
| Q3 开始时间戳 | 有，ms | 有，ms（start/end 分离） |
| Q4 完整命令 | 有（input.command） | 有（state.input.command） |
| Q5 exit code | 替代信号（is_error + 文本前缀），无数字字段 | 整数 exit 字段，干净 |
| Q6 输出内容 | 完整记录，未截断 | 完整 + 显式 truncated 标记 |
| Q7 实时写入 | 是（~100 ms 写延迟） | 是（WAL + event 流，正在写） |

**结论：通过**。两个平台都能找到会话记录、格式可解析、Q3/4/5/7 四项关键字段全部正向且实时写入。§3.4.2 可以按当前设计继续推进，无需降级。

接回主线的差异点（设计文档需要落地时注意）：

- 两个平台的字段命名完全不同，解析器需要各写一套（或做适配层），不能共用
- Claude Code 无数字 exit code，需靠 `is_error` + `"Exit code N"` 文本前缀解析
- Claude Code 的子 agent 会话是**独立转录文件**（sidecar `subagents/agent-<uuid>.jsonl`），不是主文件内联，解析时注意路径
- OpenCode 超大输出会 spill 到外部文件且文件名与 part ID 无法 join，哈希输出时需处理"truncated=true 的 part"（两个不同的失败被截断成同前缀 → 可能误判无效重复，建议 truncated 的 part 直接视为"输出变化不可判定"或走保守策略）
