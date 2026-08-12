# BDD-24: 角色卡/模板贴可复制 frontmatter 模板

## 验证方式
P3-test-cases.md 已注明 BDD-24 在 P3 阶段无独立可执行断言（模板文档是产出物本身而非程序行为），
验证载体是"P6 验收阶段人工核对 task-files.md/analyst.md/architect.md/verifier.md 是否含可复制
样例，样例本身用 yaml.safe_load 验证可解析"。本次验收即按此执行：逐文件检索"可直接复制的完整
frontmatter 样例"段落 + 用与 `agate-md-field-get.py` 的 `_read_frontmatter` 完全相同的提取方式
（找首个 `---\n` 到下一个 `\n---` 之间的内容）做 `yaml.safe_load` 验证。

## 本次验收独立复现（完整脚本输出见 bdd24-yaml-validation-output.txt）
```
agate/assets/templates/task-files.md : 5 frontmatter 样例块, 4 解析为 dict 成功
  （唯一解析失败的是文件顶部"通用 Header"模板块，其内容是 {P1-P8}/{Txxx} 占位符字面量，
   本就不是"可直接复制粘贴"的具体样例而是结构说明；真正的 4 个 v2.0 迁移字段样例——P1/P2/P6/P7
   各一个——全部解析成功）
agate/assets/execution-roles/analyst.md : 1 frontmatter 样例块, 1 解析为 dict 成功（P1 样例）
agate/assets/execution-roles/architect.md : 1 frontmatter 样例块（缩进在 bullet 列表下）, 1 解析为 dict 成功（P2 样例）
agate/assets/execution-roles/verifier.md : 1 frontmatter 样例块, 1 解析为 dict 成功（P6 样例）
agate/phase-cards/P1-requirements.md : 1 frontmatter 样例块, 1 解析为 dict 成功
agate/phase-cards/P2-design.md : 1 frontmatter 样例块, 1 解析为 dict 成功
agate/phase-cards/P6-acceptance.md : 1 frontmatter 样例块, 1 解析为 dict 成功
agate/phase-cards/P7-consistency.md : 1 frontmatter 样例块, 1 解析为 dict 成功
```
逐角色核对结果与角色实际产出物对应：analyst 只写 P1（1 个 P1 样例）、architect 只写 P2
（1 个 P2 样例）、verifier P6 模式只写 P6（1 个 P6 样例）——均含可直接复制的完整样例
（迁移字段占位齐全，含注释说明），且全部通过 pyyaml 解析为 dict。task-files.md 和 4 个
phase-cards 各自的 P1/P2/P6/P7 样例同样全部解析成功。

## 判定
PASS（证据文件：bdd24-yaml-validation-output.txt）
