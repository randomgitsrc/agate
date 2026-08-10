# BDD-15 — gate_commands 保持正文读取，四工具无回归

四工具：agate-gate-missing-cmds.py / agate-read-gate-commands.py / agate-read-p5-commands.py / agate-gate-p5-count.py
独立重跑对应测试（非引用旧记录）：
```
1..8
ok 1 GMC.1 提取命令 token 输出 key:token
ok 2 GMC.2 命令含 / 或 = 的 token 跳过
ok 3 P5C.1 P2 含 P5 + P5_formatter + P5_js → 输出对象含 commands
ok 4 P5C.2 P2 无 gate_commands.P5 → 输出空（供 bash -z 判定）
ok 5 P5C.3 P2 无 gate_commands 块 → 输出空
ok 6 P5C.4 P5 键双引号值被去除 + suffix/formatter 关联
ok 7 GPC.1 统计 P5 命令数
ok 8 GPC.2 无 gate_commands 块 → 0
```

agate-read-gate-commands.py（PYX 系列，属 check-tdd-red.bats）：
```
1..38
ok 33 PYX.1 agate-read-gate-commands.py P2 含 P3 + P3_html_formatter + project_module
ok 34 PYX.2 agate-read-gate-commands.py P2 无 gate_commands → 空 JSON
ok 35 PYX.3 agate-read-gate-commands.py P2 双引号值被去除
ok 36 PYX.4 agate-read-gate-commands.py P2 单引号值被去除
ok 37 PYX.5 agate-read-gate-commands.py P2 末行无换行也能解析
ok 38 PYX.6 agate-read-gate-commands.py GATE_FILE 不存在 → 非零退出
```

结论：四个工具对应测试全部实测通过（GMC=agate-gate-missing-cmds 2/2、P5C=agate-read-p5-commands 4/4、GPC=agate-gate-p5-count 2/2、PYX=agate-read-gate-commands 6/6），且 gate_commands 仍在正文读取，未迁移 frontmatter，符合 P2-design.md §2 不改范围声明。
