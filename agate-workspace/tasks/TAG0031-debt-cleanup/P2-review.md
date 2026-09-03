---
status: approved
phase: P2
task_id: TAG0031
parent: P2-design.md
trace_id: TAG0031-P2-review-20260904-r2
created: '2026-09-04'
agent: plan-eng-review
---

# P2-review.md — TAG0031 DEBT 存量修复批 · plan-eng-review（第 2 轮复评）

角色：plan-eng-review（工程经理，架构和执行锁定）。评审对象：修订后的 P2-design.md
（`trace_id: TAG0031-P2-20260904`）。本轮范围：仅复核第 1 轮判定的两处阻塞是否修正到位，
其余已通过部分（候选方案 1/2、gate_commands、影响面梳理其余部分、BDD 覆盖）沿用第 1 轮结论，
不重新展开。

## 阻塞项 1 复核：R1 pyyaml checksum 顺序缺口——判定：已闭环

独立读取修订后 §1.3 R1「缓解设计」段（P2-design.md 第 87 行）原文核实时序关系（不只是看有没有
提到"校验"两个字）：

`_ensure_agate_common(bundle_dir, manifest)` 在 `import yaml` 探测不可用时分三步执行：

1. 先用一行内联 `hashlib.sha256(Path(wheel_path).read_bytes()).hexdigest()` 单独校验
   `manifest["components"]["pyyaml"]["sha256"]` 这一个文件级 hash；不匹配 → stderr 报错 +
   `return None` / 调用方 exit 非 0，**不执行 `pip install`**；
2. 内联校验通过后才执行 `pip install --no-index --find-links <bundle_dir>/wheels pyyaml`；
3. 成功后 `import agate_common` 并返回模块引用。

这一顺序把"读取 wheel 文件字节计算 hash"（纯文件系统读操作，不触发 pyyaml 代码执行）放在
`pip install`（会触发包安装 + 后续 `import` 时的 `__init__.py`/C 扩展初始化执行）之前，
第 1 轮判定的"pyyaml 是 manifest 里唯一先执行、后校验的组件"这一顺序缺口已消除——pyyaml 现在
与其余组件一样遵循"先校验、后使用"的不变量，BDD-26 字面意图对 pyyaml 同样成立。

「代价确认」段（第 88 行）进一步确认：`verify_checksums()` 阶段会对 pyyaml 再校验一次（同一
文件同一 hash，幂等，非重复实现），且承认唯一残留差异只是引导阶段用原生 `hashlib` 调用而非
`agate_common.compute_sha256`（物理限制——此刻 `agate_common` 尚不可导入），但两者逻辑等价，
不构成校验强度弱化。这一表述比第 1 轮"不引入外部信任源"的论证更进一步，直接回应了第 1 轮判定
指出的缺口（"是否引入新信任源"≠"是否执行先于校验"），且给出了具体、可核实的时序描述。

「回归覆盖」段（第 89 行）补齐了第 1 轮要求的用例：构造 checksum 不匹配的 pyyaml wheel
（篡改内容或篡改 manifest 里的 `sha256` 值），mock `subprocess.run`，断言
`_ensure_agate_common` 在 `pip install` 之前就 stderr 报错并返回非成功结果，**且全程 mock 的
`subprocess.run` 未被调用**——用"未被调用"断言校验"校验先于安装"这一顺序本身，而不只是校验
最终结果，与第 1 轮 review 给出的用例设计建议（mock subprocess.run 断言 pip install 未被调用）
逐字对应。

**判定**：阻塞项 1 已闭环。缓解设计的技术路线未变（探测 yaml 缺失 → 本地安装 bundle 自带 wheel
→ import agate_common，第 1 轮已锁定该路线方向正确），本轮新增的内联前置校验步骤精确堵上了
"pyyaml 先执行后校验"的顺序缺口，无遗留问题。

## 阻塞项 2 复核：`[SCOPE+]` 行首格式——判定：已闭环

独立执行正则核实（工作目录为 task 目录）：

```
$ python3 -c "import re; text=open('P2-design.md').read(); print(bool(re.search(r'^\s*-?\s*\[SCOPE\+\]', text, re.MULTILINE)))"
True
```

对照 `check-scope-resolved.py:17` 的 `SCOPE_PLUS_RE = re.compile(r"^\s*-?\s*\[SCOPE\+\]", re.MULTILINE)`
逐字节一致，正则确实能匹配修订后的文本。进一步核实匹配位置：P2-design.md 第 77 行
`[SCOPE+] 发现：\`compute_sha256\` 迁移到 \`agate_common.py\` 后……` 前面无任何字符（行首即
`[SCOPE+]`），且该行前有空行（第 76 行）与 R1 小节标题（第 75 行）分隔，构成独立段落，非嵌在
加粗标题句中段——不是"只看有没有出现 `[SCOPE+]` 四个字符"这种表面核实，而是确认了字面位置。

段落结构也对齐了第 1 轮 review 引用的 architect.md 样例（`[SCOPE+] 发现：...` /
`必须做的理由：...` / `影响：...`）：第 77-79 行「发现」描述顺序缺口本身，第 80-81 行「必须做的
理由」引用 BDD-26 字面不变量，第 82-83 行「影响」给出修复范围（`_ensure_agate_common` 内补前置
校验）+ `packages: [agate-scripts]` + 不新增 BDD 编号的说明。三要素齐全。

另核实 `check-scope-resolved.py` 的 `_strip_agate_card()` 不会误伤本次匹配——P2-design.md
全文无 `<!-- AGATE_CARD_START -->` 嵌入块，`_strip_agate_card` 对本文件是 no-op，匹配结果不受
影响。

**判定**：阻塞项 2 已闭环。`[SCOPE+]` 现为行首独立格式，`check-scope-resolved.py` 能正确检出，
可触发主 Agent 增补 P1 基线 + `[SCOPE_RESOLVED]` 闭环的既定机械追踪流程。

## 未意外改动的部分——已核对

逐项对照第 1 轮 P2-review.md 引用的原文与本轮 P2-design.md 对应内容，确认以下部分数值/表述
未被本轮修订意外触碰：

- **候选方案 1/2**：三簇静态拆批 vs 单批顺序实现的优缺点表述、选择理由文字与第 1 轮引用逐字一致。
- **gate_commands（§3）**：四个 P5 系列 key（`P5`/`P5_consistency`/`P5_shellcheck`/
  `P5_offline_bundle`）、`timeout_seconds` 取值（120/60/60/90）、实测数据（34.63s/1.057s/
  0.043s）均与第 1 轮核实值一致，无变动。
- **files_to_read（§4）/env_constraints（§5）/minimal_validation（§6）**：结构与内容读取无
  异常，与第 1 轮"无阻塞问题"结论覆盖范围一致，未见被本轮修订波及的痕迹。
- **实现完成的标志（§7）**：四条验收标准（簇 A/B/C + 收尾）文字未变。
- **R5 表述**：第 1 轮标记为"非阻塞、建议措辞澄清"的标题句歧义（"`agate_common.py` 被簇 A
  与簇 C 同时触达"）本轮仍保留原表述——这是预期内的，因为该项是非阻塞建议，architect 未被
  要求必须修改，不构成回归。
- **非阻塞建议 1**（`agate_common.py` L30-34 补代码注释留痕）：属于建议 P4 阶段顺手采纳的项，
  不要求写入 P2-design.md 本身，本轮未见亦符合预期。

未发现任何已通过部分被本轮修订意外破坏。

## 架构问题（阻塞级）

（无）

## 架构问题（非阻塞）

- 沿用第 1 轮遗留的两条非阻塞建议，供 P4 阶段顺手采纳（不强制、不影响本轮 approved 结论）：
  ① `agate_common.py` L30-34 `import yaml`/`sys.exit(1)` 分支旁补一行代码注释留痕；
  ② R5 标题句"`agate_common.py` 被簇 A 与簇 C 同时触达"措辞可进一步澄清为"簇 A 编辑
  `agate_common.py` 本体，簇 C 仅在 `check-gate.py` 内引用其既有导出符号"。

## 测试缺口

（无新增）第 1 轮指出的测试缺口（checksum 不匹配场景用例）已在本轮「回归覆盖」段补齐，见上文
阻塞项 1 复核。

## 锁定决策

- R1 pyyaml 引导方案的技术路线 + 验证顺序细节（内联前置 checksum 校验先于 `pip install`）均已
  确认，按 P2-design.md §1.3 R1 全段固化，P4 实现须遵循该顺序（先校验、不匹配则不执行
  `pip install`）。
- `[SCOPE+]` 声明已采用行首独立格式，主 Agent 需按既定流程在 P1-requirements.md 增补对应
  `[SCOPE+ from P2]` 条目并推进 `[SCOPE_RESOLVED]` 闭环（协议机械追踪层面的后续动作，不属于
  本次 review 判定范围，但复核确认格式已具备被追踪工具正确检出的前提）。
- 三簇静态拆批并行实现、候选方案 2 否决理由、gate_commands 四个 P5 系列 key 及取值、BDD 覆盖度
  （15 条）——延续第 1 轮 approved 结论，本轮未重新展开，不重新论证。

## 结论

两处第 1 轮阻塞问题（R1 checksum 顺序缺口、`[SCOPE+]` 行首格式）均已修正到位，且核实修订未
波及其余已通过部分。P2-design.md 具备进入 P3 的方案就绪度。
