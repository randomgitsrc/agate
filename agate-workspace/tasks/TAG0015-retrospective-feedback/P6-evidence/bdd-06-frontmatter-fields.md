# BDD-6 证据：frontmatter 机器字段（AG0021 依赖）

文件：`agate/assets/templates/retrospective-template.md`

## Then 子句逐项核对

Then 要求：一份基于该模板的复盘文档定稿时，frontmatter 含 `mechanism_issues`（list）/
`execution_issues`（list）/`feedback_ready`（bool）三个字段，字段存在性可用 YAML 解析校验；
模板文件本身声明这三个字段的样例与填写说明。

| 要求 | 实际（行号） |
|------|-------------|
| 模板声明样例块 | L19-31「frontmatter 样例」小节，含完整 `---\n...\n---` YAML 块 |
| `mechanism_issues`（list） | L27 `mechanism_issues: []      # list：本次复盘归因为"机制缺口"的问题条目（简述）` |
| `execution_issues`（list） | L28 `execution_issues: []      # list：本次复盘归因为"执行错误"的问题条目（简述）` |
| `feedback_ready`（bool） | L29 `feedback_ready: false     # bool：为 true 时下方「## agate 反馈」节内容视为已就绪，可供 agate-feedback.py 提取` |

## YAML 可解析性独立验证（本轮实跑，非转抄）

用模板样例块本身构造一份最小复盘文档并跑 Python `yaml.safe_load`（提取代码块后剥离首尾
`---` frontmatter 分隔符再解析 YAML 正文）：

```
$ python3 -c "
import yaml
text = open('agate/assets/templates/retrospective-template.md', encoding='utf-8').read()
start = text.find('\`\`\`yaml') + 7
end = text.find('\`\`\`', start)
block = text[start:end].strip()
lines = block.split(chr(10))
assert lines[0] == '---'
assert lines[-1] == '---'
body = chr(10).join(lines[1:-1])
data = yaml.safe_load(body)
print(type(data['mechanism_issues']), type(data['execution_issues']), type(data['feedback_ready']))
print(data)
"

实际输出：
<class 'list'> <class 'list'> <class 'bool'>
{'task_id': 'TAG0001', 'mechanism_issues': [], 'execution_issues': [], 'feedback_ready': False}
```

三字段类型与 Then 要求 list/list/bool 完全一致，YAML 解析无错误（本轮实跑第一次直接对代码块
整体解析时报 `ComposerError: expected a single document`——因为原始代码块含头尾两个 `---`
被识别为多文档流，剥离分隔符后解析成功；这一实测过程本身也验证了"该 YAML 块严格遵守单个
frontmatter 文档的书写规范"）。

## 判定

**满足**——模板文件本身声明了三字段样例（含类型注释、填写说明），且本轮独立跑 `yaml.safe_load`
验证该样例块本身是合法 YAML、三字段类型正确，符合"字段存在性可用 YAML 解析校验"的可验证性
要求；agate-feedback.py 侧的实际提取行为见 `P6-evidence/bdd-17-extraction.md`。
