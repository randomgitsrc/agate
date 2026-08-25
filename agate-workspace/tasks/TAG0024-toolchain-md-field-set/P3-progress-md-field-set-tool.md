# P3 progress — md-field-set-tool 批次（test-designer）

- 读完 dispatch-context / test-designer 角色定义 / P0-brief / P1-requirements（BDD-1~19）/
  P2-design.md §1.1/§2/§3.1~3.4，以及 agate-md-field-get.py / agate-frontmatter-check.py /
  check-judge-verdict.py / agate_common.py / check-routing.py（_load_script 先例）/
  phases.yaml / role-system.md review-roles 目录 / docs/design-notes/design-md-field-set.md
  §5.1~5.6，确认 CLI 契约：agate-md-field-set.py 用 FILE env（同 get 工具），
  agate-md-field-set-gate-commands.py 用 FILE 位置参数（P2-design.md §3.3 用法行原样）。
- 关键设计决策记录：
  1. agate-frontmatter-check._check() 对"部分字段仍缺失"按 f"{basename}:{field}:" 前缀过滤
     （P2 §1.3 风险6），已用真实 python3 -c 验证 candidate_count=0/2 两种真实返回值，据此
     确认 BDD-6/BDD-1/BDD-16 的"逐字段增量写入不会被其余未填必填字段挡住"这一假设成立。
  2. BDD-10（原子写中断）采用白盒 importlib 加载 + monkeypatch mod.os.replace + 调用
     mod.main() 的方式（不假设具体内部函数名，只假设 main() 入口，风险最低）。
  3. BDD-15（同源铁律）不分别断言两次硬编码期望值，而是直接调用真实 _check() 取得错误串，
     用该返回值驱动对 CLI 输出的断言（含 accept/reject 两分支参数化，双向验证不产生分叉）。
  4. BDD-17 白名单并集测试：expected task_fields 从真实 phases.yaml 动态读取计算（非抄
     子集），GENERIC_HEADER_KEYS 复用实现自身声明的常量，只验证"并集计算逻辑"本身。
  5. 发现并修复一处假红灯风险：BDD-8/BDD-16 最初的断言过弱（"exit非0 + 非空输出"/
     "list 输出不含'剩余缺失'"），在脚本不存在时也会因"can't open file" 错误恰好满足弱断言
     而被误判为通过（BDD-8 曾实测 2/2 参数化用例"意外 PASS"）。已改为断言输出含具体非法
     key 字面值 / 断言 returncode==0 兜底，重跑确认全部转为真红灯。
- 新建 agate/tests/unit/test_agate_md_field_set.py，覆盖 BDD-1~19（19 个测试函数，
  BDD-8/9/15/18 参数化展开共 35 个测试项），风格对齐 test_agate_md_field_get.py。
- 自跑：`python3 -m pytest agate/tests/unit/test_agate_md_field_set.py --basetemp=.pytest-tmp
  -p no:cacheprovider -v` → 35/35 全部失败，均为 B 类真红灯（CLI 用例因两脚本文件不存在
  subprocess "can't open file" 非0退出；白盒用例因 importlib exec_module 阶段
  FileNotFoundError），无 SyntaxError。`python3 -m py_compile` 确认测试代码本身语法正确。
- 写 P3-test-cases-md-field-set-tool.md（本批次说明，含 header + 19 条 BDD→测试函数→断言点
  清单 + 覆盖率自检），未声明 test_code_dir（按派发指引留给主 Agent 合并声明）。
- 完成，返回路径 + 摘要。
