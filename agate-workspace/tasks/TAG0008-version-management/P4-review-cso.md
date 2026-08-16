---
phase: P4
task_id: TAG0008
type: review
parent: P2-design.md
trace_id: TAG0008-P4CSO2-20260816
status: approved
created: 2026-08-16
agent: cso
---

# P4 实现安全评审 — 复核轮（cso / STRIDE）

> 复核对象：上轮（TAG0008-P4CSO-20260816）MEDIUM 项 + 组长 P4-review.md 的 CRITICAL-1/2/3 修复闭环。
> 方法：rev2 修复代码静态核对 + 关键攻击面**实测复现**（version 穿越 / 组件 path 穿越 / 正常流）+ 相关测试套件跑通。
> 结论：**CRITICAL-1/2/3 全部闭环，MEDIUM-1 闭环**；MEDIUM-2/3 为接受项维持。**无 CRITICAL / 无 HIGH**，status=approved。

## 1. 修复闭环核对（review CRITICAL + 上轮 MEDIUM）

### 1.1 CRITICAL-1 / 指针 isdir 短路（agate_common._resolve_pointer_chain + agate-install._resolve_pointer）—— ✅ 闭环，无新注入面

- 两处均改为**先判 `os.path.islink` 再判 `os.path.isdir`**，软链指针（latest→v0.48.0、current→latest）最终落点 = 实际版本目录名，`_pointer_targets`/`_repair_pointers` 的版本匹配恢复（BDD-5/BDD-16 修复）。
- 安全复核：
  - 软链 target 经 `os.readlink`（非用户可控写入需 ~/.agate 写权限，属信任模型内）；绝对 target 走 `normpath`，无 shell、无命令构造。
  - 循环防护：文本指针用 `seen` 集合，软链环受 `range(8)`（agate-install）与 `seen`（agate_common，绝对 target 以绝对路径名入 seen）双重约束，不会死循环。
  - 解析结果仅用于 root/版本名，不经 exec 拼接注入（exec 目标仍由 `_GATE_MAP` 固定 + `os.path.isfile` 校验）。
- 补测（`test_bdd_5b` / `test_bdd_11b` / `test_bdd_21b`）存在且平台无关（Linux 全量、Windows skip）。resolve/summary/hook 相关 19 用例本地跑通。

### 1.2 CRITICAL-2 / install 清单忽略 manifest（install_wheels）—— ✅ 闭环

- `install_wheels` 改为从 manifest `components` 推导安装清单：含 "pillow" 才装 Pillow，"pyyaml" 必有 → 默认装 pyyaml；`--skip-pillow` 只过滤已包含项（BDD-29 语义正确）。
- 安全复核：该函数只读 components **键名**（"pyyaml"/"pillow"），不消费任何 path/版本字段 → 无路径/注入面。无 Pillow bundle 默认流不再断裂（原 LOW 功能项同步消除）。

### 1.3 CRITICAL-3 / MEDIUM-1 / manifest 字段未校验→写路径穿越 —— ✅ 闭环（实测确认）

- 新增 `_validate_manifest(manifest, bundle_dir)`：
  - `version` 强制 `^v[0-9]+\.[0-9]+\.[0-9]+$`（与 agate-install `_VERSION_RE` 同款）→ 阻断 `dest / version` 写路径穿越与 `current` 指针毒化。
  - 组件 `path` 拒绝绝对路径、`..` 部件，并 `os.path.commonpath([bundle, resolved]) == bundle` 断言（`Path.resolve()` 处理内含 symlink 逃逸）→ 阻断越界读（哈希 oracle）。
  - 接线为 fail-closed 纵深：`main`（读 manifest 后立即）→ `verify_checksums` → `install_bundle` 三处均校验；`main` 异常捕获补 `ValueError`。
- **实测复现（/tmp/opencode 独立目录，已清理）**：
  - A) `version="../../../../../tmp/.../PWNED"` → rc=1，stderr 指明非法 version，**未写出** PWNED 目录 ✓
  - B) 组件 `path="../secret.txt"` → rc=1，stderr 指明 `..`，**未安装** ✓
  - C) 正常 manifest → `_validate_manifest`/`verify_checksums` 通过，`install_bundle` 正确产出 `dest/v0.48.0/` + current 指针 ✓
- 新增 4 个回归测试（traversal/absolute/no-pillow-bundle）存在；`test_install_offline.py` + `test_agate_version_install.py` 本地 19 passed。

### 1.4 MEDIUM-2 / manifest 未签名（整包替换可重算）—— 维持接受，文档建议

- 未要求本轮修，代码未改。**复核确认代码注释与文档均未明示"checksum 只防损坏、不防整包替换"的边界** → 建议发布前在 `agate/UPGRADING.md` / README 离线包章节补一句信任边界说明（bundle 提供者可信 + checksum 防损坏；防整包替换需引入签名）。不阻塞。

### 1.5 MEDIUM-3 / uninstall 引用保护限流弱化（mtime 365 天 / 深度 ≤4 / 跳隐藏目录）—— 维持建议项

- 复核确认：`_find_references` 无 WARNING 提示、文档未说明"限流可能漏扫"。被引用的旧/深/隐藏目录项目在版本删除后 `.agate-version` 静默回退 current。建议低成本加固：**限流边界命中（深度>4 / mtime>窗口 / 跳过目录存在 .agate-version）时向 stderr 输出 WARNING 提示可能漏扫**。不阻塞。

## 2. STRIDE 矩阵（复核后）

| 威胁 | 面 | 处置（复核后） | 严重性 |
|------|-----|------|--------|
| Spoofing（伪装） | `.agate-version`/pointer/exec | version 正则白名单、gate 映射固定、argv exec → 不可注入；`_resolve_pointer*` islink 修复无新增面；manifest 未签名 → 整包替换仍可伪装（MEDIUM-2 接受项） | 中（接受） |
| Tampering（篡改） | 离线 bundle / manifest | 组件全 checksum 覆盖 + version/组件 path 现在**全部纳入字段校验**（防穿越）；manifest 无签名（整包替换可重算）→ 接受项 | 中（接受） |
| Repudiation（抵赖） | 版本变更审计 | 无安装/卸载/切版本审计日志 | LOW |
| Information Disclosure（信息泄露） | 错误输出 / 组件 path | 组件 path 穿越读已阻断（commonpath）；错误输出含本地路径可接受；AGATE_REPO_URL 嵌凭据时进 stderr | LOW |
| Denial of Service（拒绝服务） | 扫描限流 / 目录 hash | `_find_references` 限流 ✓；目录组件内**嵌套 symlink** 仍可被 `rglob`/`compute_sha256` 跟随（指向大文件/特殊文件 → 耗时/读敏感文件 hash，不输出内容） | LOW |
| Elevation of Privilege（提权） | exec gate / pip / 写路径 | exec 无注入、wheel 已校验、写路径穿越已阻断；bundle 整包替换仍可执行任意 wheel（信任边界） | 中（接受） |

## 3. 严重性分级（复核后）

- **CRITICAL：0**（原 3 项全部闭环）
- **HIGH：0**
- **MEDIUM：0（新发现）**；遗留接受项 2：MEDIUM-2（manifest 未签名，建议文档明示）、MEDIUM-3（uninstall 限流漏扫，建议 WARNING 提示）——均不阻塞。
- **LOW：5**（mac 等范围外 OS 平台误标；目录组件嵌套 symlink 被 hash 跟随；AGATE_REPO_URL 凭据进 stderr；无版本变更审计日志；`.agate-root` 内容未校验属信任模型内）

## 4. 总体评估

- 上轮全部 CRITICAL 与 MEDIUM-1（写路径穿越）经修复与实测闭环，未引入新的安全回归；`_validate_manifest` 的 fail-closed 纵深接线（main/verify/install_bundle 三处）符合安全最佳实践。
- 剩余 MEDIUM 均为**已接受的设计局限/建议项**（签名、限流漏扫提示），不构成独立攻击链，建议发布前按 §1.4/§1.5 低成本补充文档与 WARNING 即可。

## 5. 环境隔离

[PROD_NOT_TOUCHED] — 只读评审；实测复现在 /tmp/opencode 独立目录完成并已清理，未触碰真实 ~/.agate / 主 checkout / worktree 内任何文件（除本评审产出）。

## 6. 返回摘要

- Status: approved（复核轮；CRITICAL 3 项 + MEDIUM-1 全部闭环，无新 CRITICAL/HIGH）
- 最高严重级别: MEDIUM（遗留接受项 2，均为建议性）
- 不阻塞发布；建议发布前补 MEDIUM-2 文档明示 + MEDIUM-3 WARNING 提示
