# tech-debt 登记簿

> 协议/项目技术债登记。每条 DEBT = 一个 ` ```yaml ` fenced block（机器校验）+ 可选正文。
> 机器校验：`python3 {agate_root}/scripts/check-debt.py {AGATE_WORKSPACE}/debt/tech-debt.md`
> 登记判据（三分法）：① 不修它验收声明变假 → 登记；② 不修但未来变更更贵/更危险 → 登记；③ 都不影响 → 不登记（合法出口）。

## DEBT0001

```yaml
id: DEBT0001
category: technical
title: 文档脚本名引用漂移无 gate 兜底（裸脚本名不被 CHECK 2 捕获）
status: closed
priority: high
evidence:
  - ref: agate-workspace/roadmap/roadmap.md
    note: RM-AG0015（backlog，2026-08-15 立案）
  - ref: docs/reviews/retrospective-tag0010-0011-docs-20260815.md
    note: TAG0010/0011 复盘 §3.1——phase-cards 26 处过时 .sh 引用无 gate 兜住
  - ref: agate/scripts/check-protocol-consistency.py
    note: CHECK 2 REF_RE（L238）只匹配 docs/assets/scripts 前缀引用，裸脚本名（phase-cards/rules 全是）完全漏检（实测验证）
  - ref: agate-workspace/tasks/TAG0013-script-consistency/P6-evidence/bdd-1.log
    note: CHECK 10 落地后 0 ERROR（closure_criteria 1 满足）
  - ref: agate-workspace/tasks/TAG0013-script-consistency/P6-evidence/bdd-2.log
    note: 假协议树 check-nonexistent-script.py → ERROR + exit 1（closure_criteria 2 满足）
  - ref: agate-workspace/tasks/TAG0013-script-consistency/P6-evidence/bdd-4.log
    note: PROTOCOL_DIRS 含 phase-cards/rules，CHECK 2/3 0 ERROR（closure_criteria 3 满足）
impact: 脚本删/改名后协议文档漂移，consistency 0 ERROR 照过（v0.46.0 的 26 处过时引用是实锤）；修复后无 gate 防复发，未来破坏性变更再次漂移无拦截
recommendation: 新增 CHECK 10——扫描协议文件脚本名引用（裸名+相对路径）对照 agate/scripts/ 实际文件，漂移报 ERROR；豁免 UPGRADING 对照表/formatters/3 hook 薄壳/count-tests.sh；phase-cards/rules 入 PROTOCOL_DIRS
closure_criteria:
  - check-protocol-consistency.py 新增 CHECK 10 且通过率 0 ERROR
  - 协议文档引用已删脚本名 → 报 ERROR（测试锁定）
  - phase-cards/rules 入 PROTOCOL_DIRS（引用检查升级为严格）
source: retrospective
created_at: 2026-08-15
task_id: TAG0013-script-consistency
closed_at: 2026-08-16
```

## DEBT0002

```yaml
id: DEBT0002
category: technical
title: 离线包 compute_sha256 双实现漂移（pack/install 两侧各自实现，未共享 agate_common）
status: open
priority: medium
evidence:
  - ref: agate-workspace/tasks/TAG0008-version-management/P7-consistency.md
    note: DESIGN_GAP 1.3 双实现漂移——resolve-chain 批交付的 agate_common.py（438 行）未含 sha256/目录 hash 工具，offline 批受"只新建 2 脚本、不改 agate_common"约束，两侧各自实现相同约定的 compute_sha256
  - ref: agate-workspace/tasks/TAG0008-version-management/P4-review-eng.md
    note: INFORMATIONAL 8 显式跟踪（"compute_sha256 双实现漂移"）
impact: 目录 hash 约定（排序逐文件 hash 拼接再整体 hash）靠文档同步，两侧若未来改约定不一致 → 打包/安装校验失配，内网错装/误拒
recommendation: 在 agate_common.py 补一个目录 hash 工具（compute_sha256），pack/install 两侧改 import 共享
closure_criteria:
  - agate_common.py 新增 compute_sha256 且两侧 import
  - 两侧不再各自实现 hash 逻辑（grep 无重复定义）
  - BDD-22/23/26 回归通过
source: review
created_at: 2026-08-16
task_id: TAG0008-version-management
```

## DEBT0003

```yaml
id: DEBT0003
category: technical
title: 离线 manifest 未签名（checksum 防损坏不防整包替换）
status: open
priority: medium
evidence:
  - ref: agate-workspace/tasks/TAG0008-version-management/P4-review-cso.md
    note: MEDIUM-2——manifest 无签名，攻击者可整包替换并重算 checksum，完整性校验被绕过
  - ref: agate-workspace/tasks/TAG0008-version-management/P4-review.md
    note: 遗留建议项 1——建议发布前在 UPGRADING/README 离线包章节明示信任边界（bundle 提供者可信 + checksum 防损坏；防整包替换需引入签名）
impact: 内网安装的信任边界依赖"bundle 提供者可信"的隐含假设；恶意中间人整包替换时 checksum 校验不拦截
recommendation: 文档明示信任边界（bundle 提供者可信）；如需防整包替换引入签名（如 minisign/GPG）校验 manifest
closure_criteria:
  - UPGRADING/scripts README 离线包章节写明"checksum 防损坏不防整包替换"信任边界
  - （可选）manifest 引入签名校验
source: review
created_at: 2026-08-16
task_id: TAG0008-version-management
```

## DEBT0004

```yaml
id: DEBT0004
category: technical
title: 卸载引用保护扫描限流（mtime 365 天/深度 ≤4/跳隐藏目录）漏扫旧引用且无提示
status: open
priority: medium
evidence:
  - ref: agate-workspace/tasks/TAG0008-version-management/P4-review-cso.md
    note: MEDIUM-3——_find_references 限流（深度 ≤4 + 跳隐藏/.agate/.git + mtime 窗口 365 天）使边界外引用漏扫，被引用的旧/深/隐藏项目在版本删除后 .agate-version 静默回退 current
  - ref: agate-workspace/tasks/TAG0008-version-management/P4-review.md
    note: 遗留建议项 2——建议限流边界命中时向 stderr 输出 WARNING 提示可能漏扫
impact: 引用即保护（设计稿 §8.3）保证被限流弱化——边界外项目锁定版本被误删后静默回退，无提示
recommendation: 限流边界命中（深度>4 / mtime 超窗 / 跳过目录含 .agate-version）时 stderr WARNING 提示可能漏扫
closure_criteria:
  - _find_references 限流边界命中时输出 stderr WARNING
  - BDD-6 回归通过
source: review
created_at: 2026-08-16
task_id: TAG0008-version-management
```

## DEBT0005

```yaml
id: DEBT0005
category: technical
title: P6 双证据三态解析逻辑三处重复（check-gate / check-p6-evidence / check-p6-provenance）
status: closed
priority: medium
evidence:
  - ref: agate-workspace/tasks/TAG0006-ui-ux-quality/P2-design.md
    note: §2.1 _gate_p1_vision_capability / §2.8 check-p6-evidence 与 check-p6-provenance 各自读取 P1 视觉条目三态
impact: 三处解析口径若漂移（如 GAP 判据扩展）会各自不一致，P6/P1 gate 判定分叉
recommendation: 抽取公共 helper（agate_common.py 新增 read_vision_tri_state(p1_file)），三处复用
closure_criteria:
  - 公共 helper 就位且三处脚本调用同一函数
  - 全量 pytest 825+ 全绿 + consistency 0 ERROR
source: review
created_at: 2026-08-17
task_id: TAG0006-ui-ux-quality
```

## DEBT0006

```yaml
id: DEBT0006
category: technical
title: check-p6-evidence.py ahash 文件名↔哈希 zip 对齐脆性（非图片/损坏图静默跳过致错位）
status: closed
priority: high
evidence:
  - ref: agate-workspace/tasks/TAG0006-ui-ux-quality/P4-review-backend.md
    note: CRITICAL-1——agate-image-check ahash 对非图片文件 contextlib.suppress 吞错不打印行，check-p6-evidence 用 sorted(glob) 与输出 zip 对齐，行数不匹配 → 哈希错位（误拦/漏放）
impact: avg-hash 雷同分组（BDD-14）与同 BDD 时序豁免（BDD-17）判定失真，静默破坏充数/雷同防伪
recommendation: ahash 计算收敛到单一拥有方（内联到 check-p6-evidence 或 agate-image-check 改输出 文件名\t哈希 成对行），消除 zip 对齐脆性；补含非图片文件的中等复现单测
closure_criteria:
  - check-p6-evidence 与图片哈希文件一一对应，无 zip 错位
  - 含 >1KB 非图片文件的 screenshots 场景，重复对仍正确分组
source: P4-review
created_at: 2026-08-17
task_id: TAG0006-ui-ux-quality
```

## DEBT0007

```yaml
id: DEBT0007
category: technical
title: test_check_pruning.py 部分用例依赖真实 git 暂存区而非隔离 fixture，大体量协议自身任务会误报
status: open
priority: medium
evidence:
  - ref: agate-workspace/tasks/TAG0015-retrospective-feedback/retrospective.md
    note: TAG0015 P4/P5/P6/P8 阶段多次独立验证全量 pytest 时反复出现
      test_p2_6e_prune_p7_coupling_checklist_exit_0 / test_p2_52_yaml_list_phases_exit_0 /
      test_p2_52b_yaml_list_phases_p3_pruned_low_exit_0 三个用例间歇性失败；根因排查（手工构造
      隔离目录复现）确认 agate/scripts/check-pruning.py:56 `_staged_source_count` 用
      `git diff --cached --name-only` 读取**当前仓库真实暂存区**（通过 `git rev-parse
      --show-toplevel` 定位），不是隔离在测试自己的 tmp_path fixture 内——协议自身改造类任务
      （如 TAG0015 本身）在 P4-P8 阶段暂存区常有 20+ 个协议/文档文件（远超判据"源码文件数≤5"），
      导致这三个用例的"应 exit 0"断言被仓库真实暂存区体量污染而失败，commit 后暂存区清空即恢复
  - ref: agate-workspace/tasks/TAG0015-retrospective-feedback/orchestrator-log.md
    note: 2026-08-19 P4/P5 阶段记录了完整的根因排查过程（isolated run / 组合子集 run / git
      stash A-B 对比 / 无并发进程下干净单跑），确认非本任务代码缺陷、非资源竞争假阳性，而是该
      测试固有的隔离缺口
impact: 任何协议自身改造任务（agate 改自己）在 P4-P8 阶段跑全量回归时，都可能被这三个用例的
  误报打断验证节奏，需要每次重新排查"是不是这个已知坑"——排查成本随任务改动文件数增长；更危险的
  是若排查者不知道这个坑，可能误判为真实回归而阻塞流程，或反过来对真实回归掉以轻心（"反正是那三个
  老熟人误报"）
recommendation: 让 `_staged_source_count` 的测试用例改为在隔离的临时 git 仓库内运行（`git init`
  临时目录 + 在其中构造暂存区），不依赖运行 pytest 时外层仓库的真实暂存区状态；或至少在这三个
  用例里显式 monkeypatch `run_git`/`_staged_source_count` 的返回值，不依赖环境
closure_criteria:
  - 三个用例改为不依赖外层仓库真实 git 暂存区状态（隔离或 monkeypatch 任一方式）
  - 在暂存区含 20+ 文件的环境下重跑，三个用例仍稳定 exit 0
  - 全量 pytest 回归通过
source: retrospective
created_at: 2026-08-19
task_id: null
```

## DEBT0008

```yaml
id: DEBT0008
category: technical
title: agate-feedback.py 匿名化正则 ABS_PATH_RE 误伤中文散文里的斜杠分隔词（非路径场景过度脱敏）
status: open
priority: low
evidence:
  - ref: agate-workspace/tasks/TAG0015-retrospective-feedback/retrospective.md
    note: 撰写本复盘后端到端跑
      `AGATE_FEEDBACK=on python3 agate/scripts/agate-feedback.py
      agate-workspace/tasks/TAG0015-retrospective-feedback/retrospective.md`（TAG0015
      自身产出、真实 dogfooding，非单测构造场景）验证机制闭环时发现：
      `agate/scripts/agate-feedback.py` 的 `ABS_PATH_RE = re.compile(r'(?:[A-Za-z]:\\|/)
      [^\s\'"`]+')` 会把中文散文里"机制/执行层面""P1/P2 卡片"这类用 `/` 做分隔符的正常文本
      误判为绝对路径并替换成 `<PATH>`（复现：`ABS_PATH_RE.findall('机制/执行层面')` →
      `['/执行层面']`），产出的脱敏 JSON/Markdown 里出现"归因到 <PROJECT> 机制<PATH> ...
      提取"这类语义被破坏的乱码式替换
impact: 不影响 BDD-18 验收的核心诉求（不泄露项目名/绝对路径，方向正确，偏保守不算安全问题），
  但会让 agate-feedback.py 产出的待提交内容出现明显语义破损的乱码片段，人工复核时体验差、
  可能被误认为脚本 bug 而不敢提交，间接削弱 AG0021 反馈机制的可用性
recommendation: ABS_PATH_RE 增加边界约束，要求路径 token 匹配后紧跟或结尾为常见路径结构特征
  （如至少含一个 `.`/字母数字扩展名，或前一个字符是空白/行首/标点而非中日韩文字），排除
  "中文字/中文字"这类纯分隔符用法；或改用更严格的路径检测（如要求匹配到已知项目内文件后缀/
  目录关键词）
closure_criteria:
  - ABS_PATH_RE（或替代实现）对 "机制/执行层面"、"P1/P2" 等中文散文分隔符用法不再误判
  - 对真实绝对路径（/home/xxx/... 、C:\Users\...）判断能力不退化（既有 test_agate_feedback.py
    BDD-18 用例仍全绿）
  - 新增覆盖本条 evidence 场景的回归用例
source: retrospective
created_at: 2026-08-19
task_id: null
```

## DEBT0009

```yaml
id: DEBT0009
category: protocol
title: BDD-12 P5 provenance 存储位置候选 C（commit message 派生）技术上更优雅但依赖无 gate 强校验的自然语言约定，本次未采纳
status: open
priority: low
evidence:
  - path: agate-workspace/tasks/TAG0016-protocol-hygiene/P2-design.md
    note: "§3.3/§3.4 候选方案权衡——候选 C 从既有 commit message（`wf({task_id}-P5):` 前缀）现查现用派生
      P5 pass commit，零 schema 改动、直接复用已有约定；但该前缀当前没有任何 gate 脚本强制校验格式，
      属于自然语言约定，健壮性弱于候选 A。本任务最终选择候选 A（`.state.yaml` 新增可选字段
      `p5_pass_commit`），信任模型更干净（写入者为主 Agent 本人，非依赖 subagent 自报或文本格式约定）"
impact: 若未来 commit message 格式（wf() 前缀约定）仍未被 gate 强制校验，候选 C 的健壮性风险持续存在，
  不会自然消解；若届时想重新评估切换到候选 C 以省去 `.state.yaml` schema 改动，需要重新翻找本次
  P2-design.md §3.3 已做过的权衡分析，增加决策成本
recommendation: 若未来 commit message 格式（wf() 前缀约定）被新增 gate 脚本强制校验，重新评估是否将
  BDD-12 provenance 存储从候选 A（.state.yaml 字段）切换为候选 C（commit message 派生），届时候选 C
  零 schema 改动的优势才能安全兑现；若无此前提变化，维持候选 A 现状
closure_criteria:
  - commit message 的 wf() 前缀格式已被新增 gate 脚本强制校验，且完成候选 A→C 切换评估（切或不切均可，需记录理由）
  - 或明确评估后决定长期维持候选 A，本条债务关闭并记录理由
source: review
created_at: 2026-08-19
task_id: TAG0016
```

## DEBT0010

```yaml
id: DEBT0010
category: technical
title: 至少 4 个 gate_commands 键解析脚本只排除 _formatter 后缀、未排除 _timeout_seconds 后缀，把超时声明字段误判为待执行命令/待核实字段（同类扫描后发现是系统性模式，不止 P3 一处）
status: open
priority: medium
evidence:
  - ref: agate/scripts/agate-read-gate-commands.py
    note: "L31 `elif key.startswith(\"P3\") and not key.endswith(\"_formatter\"):` 只排除
      `_formatter` 后缀键，未排除 `_timeout_seconds` 后缀键——P2-design.md §6 声明
      `gate_commands.P3_timeout_seconds: 120`（P2 卡片「{key}_timeout_seconds 字段规则」正式
      支持的可选字段）时，该整数值 120 被当成一条待执行 shell 命令解析"
  - path: agate-workspace/tasks/TAG0016-protocol-hygiene/P3-test-cases.md
    note: "§3「已知问题」——TAG0016 自身 P3 阶段实测复现：`python3 agate/scripts/check-tdd-red.py
      {task_dir}` 对真实真红灯（24 个 AssertionError/AttributeError，0 个 A 类）误报
      exit 1（A 类，`bash -c \"120\"` 返回 127）；用 `TEST_RUNNER` 环境变量覆盖绕过后确认
      exit 0（真实 B 类红灯）"
  - ref: agate/scripts/agate-gate-missing-cmds.py
    note: "L20 `if k.endswith(\"_formatter\") or k == \"project_module\":` 同样未排除
      `_timeout_seconds`——TAG0016 P2 阶段实测复现：check-gate.py P2 对
      `gate_commands.P3_timeout_seconds: 120` / `P5_timeout_seconds: 180` 均报
      'GATE P2 WARNING: gate_commands.{key} 命令 {token} 不存在于当前环境'（把整数值当成
      待核实是否可执行的命令 token）"
  - ref: agate/scripts/agate-gate-p5-count.py
    note: "L23 `aux = [k for k in re.findall(r\"^  (P5_\\w+):\", block, re.MULTILINE) if not
      k.endswith(\"_formatter\")]` 同样未排除 `_timeout_seconds`——TAG0016 P5 阶段实测复现：
      check-gate.py P5 把声明的 `P5_timeout_seconds` 计为 1 条'辅助命令'，报
      'GATE P5 WARNING: P2 声明了 1 个主命令 + 1 个辅助命令...请确认已全部执行（非子集）'，
      而实际只有 1 条真实 P5 命令（`P5_timeout_seconds` 不是命令）"
  - ref: agate/scripts/agate-read-p5-commands.py
    note: "L29 `if key.endswith(\"_formatter\"):` 同样未排除 `_timeout_seconds`——TAG0016 系统性
      grep `_formatter` 排除模式命中的第 4 处，未逐一实测复现（该脚本是否会把
      `_timeout_seconds` 键实际当命令执行、还是仅列举，需要修复时一并核实），先登记同一根因，
      避免遗漏"
impact: 任何任务在 P2-design.md 按 P2 卡片「{key}_timeout_seconds 字段规则」正常声明
  `{key}_timeout_seconds` 字段（协议鼓励的正常用法，非误用）后，P2/P3/P5 阶段的 gate 校验/红灯
  判定/命令完整性核对都可能被这同一类"未排除 _timeout_seconds 后缀"的解析缺陷误导——P3 会被
  `check-tdd-red.py` 误报真红灯为假红灯（A 类），P2/P5 会收到虚假的"命令不存在"/"还有命令未执行"
  WARNING，操作者若不知道这是已知的工具解析缺陷，容易误判任务自身有问题而返工，或反过来对真实
  问题的 WARNING 掉以轻心（"反正 timeout_seconds 那个坑我知道，不用管"）
recommendation: 四个脚本的判据统一补充排除 `key.endswith("_timeout_seconds")`（与已有的
  `_formatter` 排除并列，四处修法结构相似，可考虑抽成 agate_common.py 的一个共享判据函数，
  避免未来又出现第五处遗漏——这正是本任务 RM-AG0025 想要的"权威源+复用"模式在脚本代码层面的
  应用）
closure_criteria:
  - agate-read-gate-commands.py / agate-gate-missing-cmds.py / agate-gate-p5-count.py /
    agate-read-p5-commands.py 四处均不再把 `_timeout_seconds` 后缀键当作命令/待执行项解析
  - 新增回归用例覆盖"声明 P3_timeout_seconds/P5_timeout_seconds 时，check-tdd-red.py 仍正确
    判定真红灯 + check-gate.py P2/P5 不再误报命令不存在/命令数不符"场景
  - 全量 pytest 回归通过
source: review
created_at: 2026-08-19
task_id: TAG0016
```

## DEBT0011

```yaml
id: DEBT0011
category: technical
title: SELF-GATE.md protocol-alignment-review 成果文件/留痕文件按纯日期命名，跨任务同日复用会静默覆盖已提交的历史审查记录
status: open
priority: medium
evidence:
  - ref: SELF-GATE.md
    note: "「变更触发模式」派发模板声明成果文件路径为
      `docs/reviews/agate-alignment-review-{date}.md`、留痕文件为
      `docs/reviews/agate-alignment-{date}-{NN}.progress.md`——命名只含日期，不含任务标识"
  - path: docs/reviews/agate-alignment-review-2026-08-19.md
    note: "TAG0016 自身实测复现：2026-08-19 当天 TAG0015（commit 208a1ec，已合并入 main）与
      TAG0016 各自触发了一次 protocol-alignment-review，两次派发都按 SELF-GATE.md 模板生成同名
      文件 `agate-alignment-review-2026-08-19.md`（及同名留痕文件
      `agate-alignment-2026-08-19-01.progress.md`）。TAG0016 的 subagent 用 Write 覆盖写入该
      文件时，TAG0015 已提交的历史审查记录被静默覆盖（`git diff` 显示 TAG0015 全部审查内容被
      TAG0016 内容整体替换）——若主 Agent 未在 commit 前跑 `git status`/`git diff` 逐一核对新增
      文件是否真的是新增（而非覆盖了已跟踪文件），这类覆盖会在 commit 时静默发生且不产生任何
      WARNING（git 无法区分'合法覆盖旧草稿'与'意外破坏历史记录'）。TAG0016 已手工恢复
      TAG0015 原文件内容（`git checkout --`）并将自己的审查另存为
      `agate-alignment-review-2026-08-19-tag0016.md` 规避，但这是本次会话的人工补救，不是机制修复"
impact: 只要两次 self-gate 审查落在同一日历日（对活跃度较高的 agate 自身改造仓库并不罕见——同一天
  推进两个任务、或同一任务当天多轮 P4/P8 均可能触发多次），后触发的一次会静默覆盖前一次已提交的
  审查历史（若前一次尚未 commit 则是工作区覆盖，损失更隐蔽），且没有任何 gate/hook 检测这种覆盖；
  这类历史记录一旦被覆盖再 commit，除非人工翻 git log 逐次核对，否则不会被发现
recommendation: SELF-GATE.md 的成果文件/留痕文件命名模板补充任务标识（如
  `agate-alignment-review-{date}-{task_id}.md`，无关联任务时用序号 `-{NN}` 后缀，与留痕文件已有
  的多批次序号约定对齐）；同时可选加固：`protocol-alignment-review` 角色文件的分阶段落盘指引里
  提示 subagent 用 Write 前先检查目标路径是否已存在且内容非空，若已存在应先读一遍确认是不是同一
  任务的复核轮（可覆盖）还是别的任务遗留（不可覆盖，需改用带任务标识的新文件名）
closure_criteria:
  - SELF-GATE.md 派发模板的成果文件/留痕文件路径模板补充任务标识占位符
  - 新增或更新一条回归检查（哪怕只是文档层面的检查清单项），要求 subagent 覆盖写前先确认目标
    文件不是别的任务的记录
  - 全量 pytest 回归通过（若涉及脚本改动）
source: review
created_at: 2026-08-19
task_id: TAG0016
```

## DEBT0012

```yaml
id: DEBT0012
category: technical
title: check-protocol-consistency.py --strict 在"仅有 WARNING 无 ERROR"时返回 exit 2，与 && 串联的
  gate_commands.P5 链路组合会因长期存量 WARNING 债务而永远短路中断
status: open
priority: medium
evidence:
  - ref: agate/scripts/check-protocol-consistency.py
    note: "main() 末尾（约 L1129-1133）：`if rep.errors: return 1` / `if rep.warnings and
      args.strict: return 2` / `return 0`——--strict 模式下'仅有 WARNING、无 ERROR'与'有
      ERROR'是两种不同的非 0 返回码，但对 `&&` 串联的调用方而言都同样会短路后续命令"
  - path: agate-workspace/tasks/TAG0016-protocol-hygiene/P5-test-results/unit.md
    note: "TAG0016 P5 阶段实测复现：gate_commands.P5（P2-design.md §6 声明）为
      `pytest ... && check-protocol-consistency.py --strict && count-tests.sh` 三命令 &&
      串联；实跑链路整体 exit=2，第 3 步 count-tests.sh 因链路在第 2 步短路而**未在链路内
      执行到**。逐步单独复核确认：pytest 0 failed、consistency 0 ERROR（308 个 WARNING，
      全部为历史遗留的叙事文件死链引用，与本任务无关）、count-tests.sh 独立跑通过——三步
      本身均无问题，问题在于链路层面的 && 短路语义与 --strict 的'WARNING-only 也非 0'设计
      叠加后产生的组合缺陷"
  - ref: git log（历史 P5/P8 commit message）
    note: "e40adac/687e622/eb48440/916d537 等历史任务的 P5/P8 commit message 均只声称
      'consistency 0 ERROR'，从未声称'0 WARNING'——说明本仓库长期以来的实际验收标准是
      0 ERROR 而非 0 WARNING/strict-exit-0；结合当前 308+ 条存量 WARNING 从未被清理，
      推断这一 && 链路组合缺陷可能自 --strict 与该链路命令首次一起使用起就一直存在，只是
      此前的验证流程习惯性用 `command | tail -N; echo $?` 之类的管道模式核对，管道会让 `$?`
      变成 `tail` 的退出码而非目标命令的真实退出码，掩盖了这个问题（TAG0016 本次也曾踩过
      同一个验证方法陷阱，后改用 `timeout ... bash -c '...'; echo $?` 不经管道直接核对才发现）"
impact: 任何后续任务若原样沿用当前 gate_commands.P5 的 && 串联写法（这是 P2-design.md 已固化的
  声明，大概率会被后续任务复制作为范式），只要仓库内存量 WARNING 未清零，P5 阶段的链路级 exit
  code 永远是 2、且链路最后一步命令永远不会真正被链路执行到——若验证者使用管道+tail 模式核对
  exit code（如本任务前几个阶段一度采用的方式），会得到虚假的"exit 0"印象而看不出问题；若验证
  者直接核对链路真实 exit code，则会看到非 0 但需要额外做"逐步拆解复核"才能确认这不是真失败，
  增加了每次 P5 验证的认知负担和排查成本
recommendation: 二选一（或都做）——(a) gate_commands.P5 declaration 层面：不要用 `&&` 串联含
  `--strict` 的 consistency 检查，改为三条独立命令（如 P0-brief.md env_constraints.test_cmd
  已经是用中文分号分隔的三条独立命令，语义上更准确）分别执行并分别判定，不整体链式短路；
  (b) 脚本层面：`check-protocol-consistency.py` 增加一个更细粒度的模式（如
  `--strict-errors-only`），仅在存在 ERROR 时非 0，WARNING-only 时仍返回 0（把"WARNING 需要
  关注"这件事通过打印内容告知人类，而不是通过阻断式退出码），保留现有 `--strict`
  （WARNING-only 也非 0）作为可选的更严格模式供人工主动选用，不作为 && 链路的默认组成部分
closure_criteria:
  - gate_commands.P5 相关文档/模板（P2 卡片 gate_commands 声明示例、或 HANDOFF 类文档）不再
    推荐把 --strict 塞进 && 链路中间位置
  - 或 check-protocol-consistency.py 新增区分 ERROR-only 与 WARNING-only 的退出码模式，
    且有对应回归测试覆盖两种模式的 exit code 差异
  - 全量 pytest 回归通过
source: review
created_at: 2026-08-19
task_id: TAG0016
```
