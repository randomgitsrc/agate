# P1 gate 诊断 — TAG0023

## 现象

`check-gate.py P1` exit 1：`GATE P1: P1-review.md frontmatter status 非 approved（当前: 缺失）`

## 根因

`P1-review.md` 的 Header 用了 markdown 代码围栏 ` ``` `（三个反引号）包裹 YAML 字段，而不是协议要求的 `---` YAML frontmatter 分隔符。gate 脚本按 `---...---` 块解析 frontmatter，围栏内容不被识别为 frontmatter，故读到 `status` 缺失。

对照：`P1-requirements.md`（同任务、同一批产出）Header 正确使用 `---` 分隔符，能被 gate 正常解析（P1-requirements.md 本身不是本次 gate 报错对象）。

**根因定位**：主 Agent（我）在派发 requirements-review 复评 subagent 时，prompt 里用 markdown 代码块（```）展示"输出文件 Header"示例，subagent 把示例里的 ``` 围栏也字面复制进了实际产出文件，而不是替换成 `---`。这是派发 prompt 格式易混淆导致的机械性错误，不是评审内容本身的问题——已核实 `status: approved` 字段值、BDD 锚点引用、覆盖维度标注等实质内容全部正确落盘，只是分隔符用错。

## 处理方式

不构成内容级 needs-revision（评审实质结论未受影响），按机械格式修复处理：追加一次极小范围的修补派发（只改 Header 分隔符，不碰正文），不计入 retries 对应性事件（不是评审被拒/门槛失败，是主 Agent 派发失误的直接后果）。修复后重跑 `check-gate.py P1` 确认 exit 2。
