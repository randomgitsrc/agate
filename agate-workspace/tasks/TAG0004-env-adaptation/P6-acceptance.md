---
phase: P6
task_id: TAG0004-env-adaptation
type: acceptance
parent: P5-verification.md
trace_id: TAG0004-P6-20260813
status: draft
created: 2026-08-13
agent: verifier
# ── v2.0 机器汇总 ──
pass: 37
fail: 0
ui_affected: false
---

# P6 验收报告 — TAG0004（agate 脚本健壮性 + 环境适配）

- **验收范围**：P1-requirements.md 全部 37 条 BDD（BDD-1..37）
- **验收环境**：worktree `/home/kity/oclab/agate/.worktrees/agate-TAG0004`（Linux UTF-8 locale），bats 1.10
- **验收方式**：逐条 BDD 实跑对应 bats 单测 + 全局回归（全量 bats / consistency / shellcheck / CI 静态断言），证据为实际命令执行输出
- **Windows 类 BDD**（BDD-9/11/12/14/21/26 等）用 Linux fixture 模拟 + CI windows-latest matrix 兜底，**未声明已实测 Windows**
- `[PROD_NOT_TOUCHED]` 全程仅操作 worktree 与 /tmp/opencode，未触达主 checkout / ~/.agate / 生产环境

## BDD 逐条验收结果

### S1 — pre-commit-gate.sh 空格路径 fail-open 静默绕过

- PASS BDD-1: 路径含空格时 gate 不静默绕过——空格路径任务 P1 gate 实际不通过时 pre-commit-gate 返回 exit 1 拦截 (p6-bdd-1.log)
- PASS BDD-2: 路径含空格时所有暂存 state 文件都被逐个处理——多个 .state.yaml 含空格路径逐个执行格式校验，不因切词丢失 (p6-bdd-2.log)
- PASS BDD-3: PROCESSED_DIRS 含空格路径时一致性检查正确——空格目录不拆段、gate 正常执行（输出含 GATE P1） (p6-bdd-3.log)
- PASS BDD-4: Linux 路径不含空格时行为与现状完全一致——无空格路径单任务 gate 行为不变（Linux 回归守卫） (p6-bdd-4.log)

### S3 — 13 个 py 缺 encoding

- PASS BDD-5: 所有文本 open() 调用带 encoding="utf-8"——grep 断言审计扫描全部 agate/scripts/*.py，0 个文本 open()/read_text() 缺 encoding（Image.open 除外） (p6-bdd-5.log)
- PASS BDD-6: 含中文的协议文件被 py 工具正确读取——agate-md-field-get.py 读取中文内容文件正确返回字段，无 UnicodeDecodeError (p6-bdd-6.log)
- PASS BDD-7: 含中文的协议文件被 py 工具正确写回——agate-retreat-state.py write_retreat 写回中文 reason 完整（allow_unicode 语义保持） (p6-bdd-7.log)
- PASS BDD-8: Linux 下纯 ASCII 文件读取行为不变——agate-state-get.py 读纯 ASCII .state.yaml 返回正确 (p6-bdd-8.log)

### S2 — check-p6-evidence.sh 中文证据文件名

- PASS BDD-9: 中文文件名证据被识别为合法引用——PASS 行引用 `(截图 验证通过.png)` + 同名证据文件，check-p6-evidence.sh 判定 exit 0 (p6-bdd-9.log)
- PASS BDD-10: 无证据引用的 PASS 仍被拦截——`(见截图)` 无文件名+扩展名仍 exit 1，字符类加宽不放宽结构 (p6-bdd-10.log)

### M4/M5 — 全角冒号 POSIX locale 残留

- PASS BDD-11: check-gate.sh P7 全角冒号计数行正确排除——LC_ALL=C 下 `[BLOCKER]：3 条` 总结行不误计为阻塞，exit 0 (p6-bdd-11.log)
- PASS BDD-12: check-p6-format.sh --fix 全角冒号总结行归一化成功——LC_ALL=C 下 `- fail：3` 经 line 69 bracket 路径归一化为 `**Summary**: FAIL: 3` (p6-bdd-12.log)
- PASS BDD-13: 半角冒号与已有修复行为不变——LC_ALL=C 下 `- FAIL: 3` 半角路径 --fix+--check 与 v0.40.3 一致 (p6-bdd-13.log)

### M6 — md CRLF 污染 frontmatter 提取

- PASS BDD-14: CRLF 行尾的 md 产出文件 frontmatter 提取不失效——CRLF 行尾 P1-review.md 经 check-gate.sh P1 提取 status 不失效 (p6-bdd-14.log)
- PASS BDD-15: Linux LF 行尾 md 文件行为完全不变——LF 行尾 ASCII 文件行为与基线一致 (p6-bdd-15.log)
- PASS BDD-16: 历史 CRLF review 文件不受影响——.gitattributes 不含强制 *.md eol 规则，历史文件不被改写 (p6-bdd-16.log)

### M9 — 路径正则元字符

- PASS BDD-17: 目录含 `[` 或 `*` 时 gate 正则不报错被吞——任务目录含 `[` 元字符时 PROD_TOUCHED 检测不静默绕过，grep -F 前缀修正生效 (p6-bdd-17.log)

### 其他 — .agate.env CR / 复制模式 AGATE_ROOT / sed 转义

- PASS BDD-18: .agate.env 尾部 \r 不污染工作区解析——CRLF 行尾 `AGATE_WORKSPACE=ws-crlf\r` 解析结果无 \r (p6-bdd-18.log)
- PASS BDD-19: 复制模式安装的 hook 能正确解析 AGATE_ROOT——复制 hook + .agate-root 标记，env -u AGATE_ROOT 下 pre-commit-gate 正常执行 (p6-bdd-19.log)
- PASS BDD-20: render-dispatch-prompt sed 替换串转义正确——AGATE_ROOT 含 `&` 时按字面值插入，无占位符残留 (p6-bdd-20.log)

### Q1 — 路径归一化（agate-next-card.sh）

- PASS BDD-21: Windows 盘符/反斜杠路径下前缀匹配稳定——`C:\proj\agate` 风格 AGATE_ROOT 前缀剥离正确输出相对路径 (p6-bdd-21.log)
- PASS BDD-22: Linux 前缀匹配行为不变——常规路径前缀剥离字节输出与修复前一致 (p6-bdd-22.log)

### Q2 — 阶段卡片 phase 推进语义对齐

- PASS BDD-23: 7 张阶段卡片与 git-integration.md 规则 2 对齐——P1/P2/P3/P4/P6/P7/P8 卡无"先更新 phase=N→N+1 再 commit"旧 mode B 写法 (p6-bdd-23.log)
- PASS BDD-24: 修复不改变 commit 顺序与 gate 判定逻辑——git-integration.md 规则 2 语义不变 (p6-bdd-24.log)
- PASS BDD-25: 修复后协议一致性检查 0 ERROR——worktree 自己脚本 `check-protocol-consistency.py --strict` 全部检查 PASS，exit 0 (p6-bdd-25.log, p6-bdd-25-consistency.log)

### Q5 — SETUP.md Windows 章节 + .gitignore 模板预设

- PASS BDD-26: SETUP.md 含 Windows 章节——覆盖 PYTHONUTF8 编码（含 AGATE_ROOT/PATH/CRLF 同章节） (p6-bdd-26.log)
- PASS BDD-27: .gitignore 模板预设 version.txt / dist 白名单——含 version.txt/dist 条目 (p6-bdd-27.log)

### RM-AG0001 — check-gate.sh P1 反引号包裹盲区

- PASS BDD-28: 反引号包裹的 [SUGGEST: ...] 被识别为 SUGGEST——`` `[SUGGEST: 推荐 X]` `` 计入 SUGGEST WARNING，不因反引号前缀漏计 (p6-bdd-28.log)
- PASS BDD-29: 反引号包裹的 NEED_CONFIRM 阻塞标记被正确识别——`` `[NEED_CONFIRM]` `` 判为未解决 NEED_CONFIRM，exit 1 阻塞 (p6-bdd-29.log)

### RM-AG0002 — check-tdd-red.sh 无 formatter 退化

- PASS BDD-30: 无 formatter + 编译失败（A 类）判 A 类红灯——TEST_RUNNER exit 1 + Traceback/SyntaxError 关键词判 A 类，exit 1 不再误判红灯 (p6-bdd-30.log)
- PASS BDD-31: 无 formatter + 断言失败（B 类）判正确红灯——exit 1 无 compile/error 关键词保持红灯光 exit 0，与现状一致 (p6-bdd-31.log)

### 全局回归（Linux 基线 + CI）

- PASS BDD-32: 全量 bats 测试全绿——worktree 实跑 sanity+unit+regression+integration，714 ok / 0 not ok，exit 0 (p6-bdd-32.log, p6-bdd-32-full.log)
- PASS BDD-33: CI 含 windows-latest matrix——protocol-tests.yml 4 个 job 均配置 `os: [ubuntu-latest, windows-latest]` (p6-bdd-33.log, p6-bdd-33-ci.log)
- PASS BDD-34: shellcheck 无 error——`shellcheck -S warning agate/scripts/*.sh` 逐脚本运行 0 error / 0 warning，exit 0 (p6-bdd-34.log, p6-bdd-34-shellcheck.log)

### TPV0090-M4 — check-tdd-red.sh B 类 NameError 盲区

- PASS BDD-35: 测试引用未实现符号（NameError）判 B 类红灯——formatter 输出 errors>0 含项目模块内 NameError 判 B 类红灯光，exit 0 (p6-bdd-35.log)
- PASS BDD-36: 使用 globals().get() 规避的既有测试不受破坏——规避模式断言失败仍判正确红灯 exit 0，向后兼容不回退 (p6-bdd-36.log)
- PASS BDD-37: 非未定义符号的真实测试 bug 仍判 A 类——TypeError 等真实 bug 判 A 类 exit 1，B 类 NameError 扩展不扩大到所有 errors (p6-bdd-37.log)

**Summary**: 37/37 PASS，0 FAIL

## 验收说明

1. **覆盖完整性**：37 条 BDD 全部实跑验证，无跳验/无中间态；每条 PASS 均有 P6-evidence/ 下证据文件引用，证据文件为 bats 单测输出、命令执行日志或静态断言输出，末行均为 `EXIT_CODE: <n>`（n=0）。
2. **Windows 类 BDD 验证方式**：BDD-9/11/12/14/21/26 等在 Linux 用中文 fixture / 参数模拟执行（bats 单测内构造对应场景），BDD-33 CI windows-latest matrix 以配置文件静态断言为证据。按 P1 capability_requirements（windows-runtime=supplementable），本环境未实测 Windows，实际双平台结果待 P8/PR 阶段回看 CI。
3. **全局回归佐证**：BDD-32 全量 714 bats 全绿为 Linux 基线不回的客观证据；consistency 0 ERROR + shellcheck 0 佐证文档与脚本改动未引入结构问题。
4. **环境隔离**：`[PROD_NOT_TOUCHED]` 全程仅在 worktree 与 /tmp/opencode 操作，未触达生产环境 / 主 checkout / ~/.agate。
