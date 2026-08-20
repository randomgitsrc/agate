# P2-progress.md (architect)

- 读完 architect.md 角色定义、P2-dispatch-context-architect.md、P0-brief.md、P1-requirements.md
- 读完 4 个 DEBT0010 解析脚本：
  - agate-read-gate-commands.py L31: elif key.startswith("P3") and not key.endswith("_formatter"): 未排除 _timeout_seconds -> P3_timeout_seconds 会被当作 P3 命令加入 commands 列表（BDD-2 相关）
  - agate-gate-missing-cmds.py: 跳过条件 k.endswith("_formatter") or k=="project_module"，未排除 _timeout_seconds -> P5_timeout_seconds:120 的 token "120" 无 / 或 = 会被当作待核实命令输出（BDD-1）
  - agate-gate-p5-count.py: aux = [k for k in ... if not k.endswith("_formatter")]，未排除 _timeout_seconds -> P5_timeout_seconds 被计入 aux 辅助命令数（BDD-3）
  - agate-read-p5-commands.py: if key.endswith("_formatter"): continue，未排除 _timeout_seconds -> P5_timeout_seconds 会被当作 P5 命令纳入 entries（会被当命令执行）
  - 4 处判据形态不同（field startswith+endswith / 独立跳过条件 / 列表推导 / continue），抽共享函数需要设计统一签名，如 is_aux_or_meta_key(key) 或 should_skip_key(key)
- 读完 agate_common.py 头部：无既有 key 后缀判据函数，probe_python() 只是 shutil.which(python3/python) 顺序探测，供 Python 侧调用（非 hook shell 用）。DEBT0010 共享判据函数需新增，建议函数名 is_meta_gate_key(key) 落 agate_common.py
- 读完 3 个 hook 薄壳（pre-commit-gate.sh/commit-msg-self-gate.sh/pre-push-gate.sh），逐字确认探测循环结构完全一致（约 L15-16）：
  PY=""; for c in python3 python; do command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }; done
  无 AGATE_PYTHON 显式指定机制，无候选可执行性验证。设计方向：AGATE_PYTHON 优先直接使用（跳过探测循环，满足 BDD-11）+ 探测循环增加候选可执行性小测试（通用 exit code 判据：候选执行 "$CAND" -c "" 非零则跳过，覆盖 Store 占位符 exit 49 场景，不依赖 locale 相关字符串匹配）
- 读完 check-protocol-consistency.py main() 尾部（L1076-1134）：--strict 时 if rep.warnings and args.strict: return 2；无 --strict 时 WARNING-only 返回 0。确认 DEBT0012 根因：exit 2（非 0）在 && 链路中会短路后续命令。设计方向：(a) P2 卡片 gate_commands 声明指引改为独立 key 不用 && 拼接 +（b）新增 --strict-errors-only 互斥模式（仅 ERROR 非零，WARNING-only 打印提示 exit 0），两者都做（P1 known_risks 已提示 (b) 影响 AI4 接口需要区分覆盖）
- 读完 SELF-GATE.md 命名模板出现点：L53/54（文件类型表）、L133/143（全量审查模式派发模板）、L183/193（另一派发模板，可能增量/复核模式）——共 6 处两种文件名模式（留痕 agate-alignment-{date}-{NN}.progress.md / 成果 agate-alignment-review-{date}.md）均缺任务标识
- 读完 protocol-alignment-review.md L118 人工验收清单项引用旧命名，且全文无写入前检查目标路径存在性逻辑，需新增
- 读完 agate-extract-context.py L107-109（P1 分支）：env_constraints 只做 _grep_after 抽取拼接注入 output 字符串，无执行判断，确认声明性字段结论
- 读完 platform-notes.md L152 已知限制表（Windows 原生）插入点确认，及 L85 起Windows
 原生」章节结构；AGENTS.md L42「Gate 脚本分层」段是本任务对"升级 agate"相关表述的实际锚点（无独立"升级 agate"标题，按语义就近选址）
- 读完 P4-implementation.md L50-54「自查≠gate」节：内容短，需追加 deploy/构建类 P4 后检查提醒（BDD-6）
- grep 确认已有测试文件锚点：agate/tests/unit/test_agate_gate_p5_count.py（p5-count 判据回归落点）、agate/tests/unit/test_check_protocol_consistency.py、agate/tests/integration/test_pre_commit_hook.py（hook 集成测试模式，用 run_cli + tmp PATH 可验证探测循环）
- 最小验证 1（DEBT0012 && 链路短路假设）：python3 subprocess 跑 `true && (exit 2) && echo STEP3_RAN`，结果 chain exit code=2，STEP3_RAN 未打印（STEP3 ran: False）——confirmed，&& 链路在中间步骤 exit 2 时确实短路后续步骤，与 P1 BDD-9 描述的现象一致
- 最小验证 2（DEBT0014 Store 占位符识别判据，构造模拟 stub）：在 scratchpad 下建 fake-bin/python3（脚本体 `exit 49`，模拟 Store 占位符非交互 exec 直接 49）+ fake-bin2/python（脚本体 `exit 0`，模拟真实可用候选）。用候选设计逻辑 `CAND=$(command -v "$c") || continue; "$CAND" -c "" >/dev/null 2>&1 || continue; PY="$CAND"; break` 在 PATH=fake-bin:fake-bin2:$PATH 下测试：resolved PY=.../fake-bin2/python——confirmed，探测循环正确跳过不可执行的 python3 候选，继续探测并解析到 python。另测 AGATE_PYTHON=/usr/bin/python3 显式指定场景：resolved PY=/usr/bin/python3，循环体未执行——confirmed，显式指定优先跳过探测循环。判据选定：通用 exit code 判据（候选执行 `-c ""` 非零即跳过），不用 stderr 字符串特征匹配（避免 locale 依赖）。声明：本验证在 Linux 用模拟 stub 完成，不代表真实 Windows Store 占位符实测，Windows 真实场景由 CI matrix（pytest -m windows_smoke）冒烟兜底，不得声称已在 Windows 实测通过
- 确认 gate_commands 相关命令均可用：agate/tests/scripts/count-tests.sh 存在；shellcheck 已安装（/usr/bin/shellcheck）
- 所有输入文件读取完毕，开始撰写 P2-design.md 正文
- P2-design.md 已写入并自检：frontmatter YAML 合法（python3 yaml.safe_load 验证）、3 个正文 yaml 代码块（gate_commands/env_constraints/minimal_validation）均合法解析、gate_commands 无 && 拼接、candidate_count=8 与正文 4 组 x 2 候选一致、dispatch_plan 已声明（5 批 static-batch, parallel_limit=5）。任务完成。

## P2 修复轮（retry_round: 1）— architect

- 依据 P2-review.md BLOCKER-1（`SELF-GATE.md` 路径前缀在文档内自相矛盾），修正 P2-design.md 内 2 处遗留的 `agate/SELF-GATE.md` 错误路径前缀：
  - §1.1「改什么」表格（原 L40）：`agate/SELF-GATE.md L53/54...` → `SELF-GATE.md L53/54...`
  - §7 files_to_read 的 `fg2-self-gate-naming` 批次（原 L216）：`agate/SELF-GATE.md:48-60,125-145,175-195` → `SELF-GATE.md:48-60,125-145,175-195`
- 修复后自检：`/usr/bin/grep -n "agate/SELF-GATE" P2-design.md` 无命中（exit 1），确认残留清零。
- 未改动方案主体其余内容（候选方案/影响面梳理其余部分/gate_commands/dispatch_plan/minimal_validation/frontmatter），符合 dispatch-context「不要做的事」约束。
