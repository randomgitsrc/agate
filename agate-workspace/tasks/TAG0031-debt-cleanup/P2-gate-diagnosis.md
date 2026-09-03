---
phase: P2
date: 2026-09-04
trigger: review_rejected
---
# P2 Gate 诊断（第 1 轮 review 后）

- review 结果：status rejected（plan-eng-review，agent≠main，P2-review.md）
- 失败项：R1 pyyaml checksum 校验顺序缺口, `[SCOPE+]` 行首格式未闭环

## 诊断

主 Agent 已亲自复核两处阻塞，均确认成立：

1. **R1 pyyaml checksum 顺序缺口**：`_ensure_agate_common(bundle_dir)` 缓解设计会在 `pip install`
   + `import yaml` 之后才第一次有能力调用 `verify_checksums()`，导致 pyyaml 这一个组件是 manifest
   里唯一"先执行、后校验"的组件（其余组件均在全部 checksum 通过后才被使用）。已核实
   `agate-pack-offline.py:129` 确认 pyyaml 在 manifest 中是独立受 checksum 保护的文件级组件
   （`components["pyyaml"] = pyyaml_wheels[0]`，非目录哈希）。这打破了 BDD-26 的字面不变量
   （"checksum 不匹配 → 该组件的任何内容都不会被落地/执行"）。
   **修复方向**：`install-offline.py` 在 `pip install` 之前，用一行内联
   `hashlib.sha256(Path(wheel_path).read_bytes()).hexdigest()` 单独校验 manifest 里
   `components["pyyaml"]["sha256"]` 这一个文件级 hash（不构成 BDD-1「全仓仅 1 处 compute_sha256
   定义」的重复实现——一次性、单文件、不对外暴露为函数的内联校验，属于 `_ensure_agate_common`
   自身的引导前置检查）。校验通过再 `pip install`，不通过则 stderr 报错 + exit 非 0，不执行
   `pip install`。约 5-8 行改动量。**或**（弱化方案）：在 R1「代价确认」段明确写清这一具体
   残留风险及可接受理由，不能只停留在"不引入外部信任源"这一层论证。
2. **`[SCOPE+]` 行首格式未闭环**：`check-scope-resolved.py:17` 的
   `SCOPE_PLUS_RE = re.compile(r"^\s*-?\s*\[SCOPE\+\]", re.MULTILINE)` 要求 `[SCOPE+]` 出现在
   行首（允许前导空白/`-`）。P2-design.md 第 75 行 `**R1（新发现，[SCOPE+]）：...**` 把标记嵌在
   加粗标题句中段，不在行首，正则不会匹配，导致这一新发现的隐含需求脱离"主 Agent 增补 P1 基线 +
   `[SCOPE_RESOLVED]` 闭环"的既定机械追踪流程。
   **修复方向**：改写为行首独立格式（参照 architect.md 样例结构：`[SCOPE+] 发现：...` /
   `必须做的理由：...` / `影响：...` 另起一段放在 R1 小节开头），使
   `check-scope-resolved.py` 能正确检出。纯格式修正，不涉及方案本体重新设计。

## 路由

两处均是 P2-design.md 本身的缺口，不涉及 P1 需求基线问题，退回 architect 修改：

- R1「缓解设计」+「代价确认」段：补 pyyaml wheel 前置 checksum 校验（推荐路径），或明确写清残留风险
- R1「回归覆盖」段：若采纳前置校验方案，需补一条 checksum 不匹配场景的用例（review 已给出用例设计建议：mock subprocess.run 断言 pip install 未被调用）
- 第 75 行 `[SCOPE+]` 标记改为行首独立格式

## 不需要修改的部分（避免 architect 无谓返工）

review 已确认通过、无需改动：候选方案 2 否决理由（非稻草人）、gate_commands 声明（格式合规+取值有依据）、BDD 覆盖度（15 条逐条核对无遗漏）、锁定决策（三簇拆批方案本体、debt 登记收尾时机、gate_commands 固化）。

review 的两条「非阻塞建议」（可顺手采纳，不强制）：
- `agate_common.py` L30-34 `import yaml`/`sys.exit(1)` 分支旁补一行代码注释留痕（预防未来消费方重蹈覆辙）
- R5 标题句"agate_common.py 被簇 A 与簇 C 同时触达"措辞澄清（易被误读为两簇同改一文件，正文已自我澄清但标题有歧义）
