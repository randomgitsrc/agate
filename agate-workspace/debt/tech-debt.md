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
