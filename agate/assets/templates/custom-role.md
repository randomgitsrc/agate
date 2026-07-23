# 自定义角色模板

> 复制本模板，按需填写，放到 execution-roles/ 或 review-roles/ 下

```markdown
---
role_id: {唯一标识，如 db-migration-specialist}
type: {execution | review}
phases: [{适用阶段，如 P2, P4}]
source: {可选，如果改编自某处}
---

# {角色名}

**定位：** {一句话说清这个角色干什么}

## 认知模式
{这个角色怎么思考、关注什么、优先级是什么}
{列 3-5 条，要具体}

## 输入（自己读取）
{必须读取的文件路径，subagent 自己读，不靠主 Agent 传内容}
- docs/tasks/{Txxx}/P0-brief.md（环境约束、已知风险——所有角色必读）
- dispatch-prompt 中指定的输入文件是必读的，按 prompt 给出的路径读取
- {其他角色特定输入}

## 输出
{必须产出的文件 + 格式}
{必须含 Header：phase, task_id, parent, trace_id, agent}
`agent` 字段对应你定义的角色 ID（如 `agent: my-custom-reviewer`）。由主 Agent 在派发 prompt Header 里填好，subagent 复制即可，不要自行推断。

## 分阶段落盘（默认启用）
每读完一个输入文件或完成一个关键步骤，立即把发现追加写入 docs/tasks/{Txxx}/P{N}-progress.md（bash 追加模式）。不要等所有文件读完再一次性写——逐条写。

## 质量门槛
{什么算"完成"，必须可判定——能从文件里读出明确值}

## 环境隔离
- 调试/验证必须使用 P0-brief 的 debug_env 声明的测试环境，严禁直接操作生产环境
- 若意外接触生产环境，立即停止并标注 `[PROD_TOUCHED] {描述}` 报告主 Agent（未触发写 `[PROD_NOT_TOUCHED]`）

## 返回给主 Agent
{只返回什么——通常是"文件路径 + 一句话摘要"，控制上下文不爆炸}
```

## 使用步骤
1. 按上面结构写一个 {role_id}.md，放 execution-roles/ 或 review-roles/
2. 平台适配（二选一）：
   - 方法 A：在 OpenCode/Claude Code agent 目录放对应 markdown（文件名=role_id）
   - 方法 B（推荐，最稳）：不依赖平台自定义机制，派发时用 general subagent +
     在 prompt 里写"读取 {agate_root}/assets/.../{role_id}.md 并遵循"
3. 派发时引用这个角色文件路径

## 注意（OpenCode issue #29616）
opencode.jsonc 里 mode:"subagent" 的自定义 agent 可能调不起来。
优先用方法 B（prompt 注入角色文件），跨平台且不踩坑。
