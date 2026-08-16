---
phase: P4
task_id: TAG0008
type: review
parent: P2-design.md
trace_id: TAG0008-P4R2-20260816
status: approved
created: 2026-08-16
agent: review
---

# P4 实现评审汇总 — 复核轮（专家组组长）

> 本文件是 P4 阶段最终门槛文件。组长角色：**只汇总，不新增评审发现**。
> 复核轮：上轮汇总为 rejected（3 CRITICAL），implementer 已修复（rev2），两位专家复核均 approved。
> 组长规则：任何专家 BLOCKER/CRITICAL → rejected；全票无 BLOCKER → approved。
> 评审只读，未修改任何代码 `[PROD_NOT_TOUCHED]`。

## 结论（Status: approved）

**Status: approved** —— 全票无 BLOCKER：两位专家复核后均 approved，无新增 CRITICAL/HIGH。

- review 专家（P4-review-eng.md，rev2，TAG0008-P4RE2）：**approved** — 3 CRITICAL 全部真实修复 + 回归测试覆盖（699 passed / 54 passed / ruff / shellcheck / consistency 全绿），8 条 INFORMATIONAL 仍成立但非阻断。
- cso 专家（P4-review-cso.md，rev2，TAG0008-P4CSO2）：**approved** — CRITICAL-1/2/3 + MEDIUM-1 全闭环（含实测复现确认），最高 MEDIUM 为遗留接受项 2（建议性），无新 CRITICAL/HIGH。
- 汇总：**approved**。分歧（manifest 路径穿越评级）已在修复轮解决（按 CRITICAL 处理并修复），本轮无分歧遗留。

## 3 CRITICAL 修复确认（rev2 逐条闭环）

### CRITICAL-1 指针解析 isdir 短路（软链布局卸载指针悬空 + 版本号显示错误）— 已修复
- `agate_common.py:113-151` `_resolve_pointer_chain` + `agate-install.py:98-126` `_resolve_pointer`：解析顺序改为**先 `os.path.islink` 再 `os.path.isdir`**（软链 readlink 目标继续追，绝对 target normpath，seen 防环）→ 最终落点 = 实际版本目录名；`_repair_pointers` 版本匹配恢复（BDD-5 红线 / BDD-16 隔离）。
- 两位专家均实测复现确认：`current→latest→v0.48.0` 解析到 `v0.48.0`；卸载被指向版本时 REPAIR FIRES。
- 回归测试：`test_bdd_5b_uninstall_pointed_version_repoints_symlink` / `test_bdd_11b` / `test_bdd_21b`（平台无关，Windows skip 声明）。
- 安全复核无新注入面：readlink 无 shell、normpath 无命令构造、软链环双重防死循环、exec 仍走 `_GATE_MAP` 固定 + isfile 校验。

### CRITICAL-2 install-offline 安装清单忽略 manifest（无 Pillow bundle 默认流失败）— 已修复
- `install-offline.py:116-135` `install_wheels`：从 manifest `components` 推导安装清单（含 "pillow" 才装 Pillow；"pyyaml" 必有）；`--skip-pillow` 只过滤已包含项（BDD-29 语义对齐）。只消费组件键名，无路径/注入面。
- 回归测试：`test_bdd_29b_no_pillow_bundle_installs_pyyaml_only`（走 install_wheels 真实路径，pip argv 只含 pyyaml）。

### CRITICAL-3 / MEDIUM-1 manifest 字段未校验（version 路径穿越写 / component path 越界读）— 已修复
- `install-offline.py:40-66` 新增 `_validate_manifest`：version 强制 `^v[0-9]+\.[0-9]+\.[0-9]+$`（同 `_VERSION_RE`）；组件 `path` 拒绝绝对路径与 `..` + `os.path.commonpath([bundle, resolved]) == bundle` 断言（含 symlink 逃逸兜底）。
- 接线 fail-closed 纵深：main（读 manifest 后立即）→ verify_checksums → install_bundle 三处校验；main 补 ValueError 捕获。
- cso 实测复现（/tmp/opencode，已清理）：穿越 version → rc=1 不写出；穿越 path → rc=1 不安装；正常 manifest → 正确产出 `dest/v0.48.0/` + current 指针。
- 回归测试：`test_manifest_version_traversal_rejected` / `test_manifest_component_path_traversal_rejected` / `test_manifest_absolute_path_rejected`。

## 遗留建议项（不阻断，供后续/发布前处理）

1. **MEDIUM-2**（cso）：manifest 未签名，checksum 防损坏不防整包替换。建议发布前在 `UPGRADING.md` / README 离线包章节明示信任边界（bundle 提供者可信 + checksum 防损坏；防整包替换需引入签名）。
2. **MEDIUM-3**（cso）：uninstall 引用保护扫描限流（mtime 365 天 / 深度 ≤4 / 跳隐藏目录）使旧引用漏扫且无提示。建议限流边界命中时向 stderr 输出 WARNING 提示可能漏扫。
3. **review INFORMATIONAL 8 条**（P4-review-eng.md rev2 复核仍成立，非阻断）：
   - resolve_agate_root 归口后 worktree 开发场景解析到 `~/.agate/current`（P2 §4.4 决策，文档待确认）
   - `_find_references` 跳过 dot 目录 + mtime 窗口 → 引用保护假阴性（接受取舍）
   - 版本化布局 `~/.agate/scripts/` 入口根无显式 provision（建议 ensure-scripts）
   - agate-pack-offline 失败路径 worktree/bundle 残留（建议回滚 + 清理指引）
   - 指针文件内容未做版本名校验（用户可控，低风险）
   - install-offline 复制模式 `.agate-root` 标记无消费方（接线或删）
   - agate-summary guards 来源与解析 root 不一致（轻微）
   - pack 固定 `--python-version 311` 无 install 端核对 + compute_sha256 双实现漂移（已 DISCLOSE DESIGN_GAP，跟踪）
4. **cso LOW 5 项**：mac 等范围外 OS 平台误标 / 目录组件嵌套 symlink 被 hash 跟随 / AGATE_REPO_URL 凭据进 stderr / 无版本变更审计日志 / `.agate-root` 内容未校验（信任模型内）。
5. 建议将以上遗留项作为 backlog / DEBT 记录（不入本任务阻塞）。

## 修复要求历史（上轮 rejected 记录，供追溯）

> 上轮（TAG0008-P4R-20260816）rejected 理由：review 专家 3 CRITICAL（指针解析 isdir 短路 / install-offline 无 Pillow 默认流失败 / manifest 路径穿越）+ 专家组分歧（manifest 路径穿越评级：review CRITICAL vs cso MEDIUM）。已按 CRITICAL 处理并在 rev2 全部修复闭环（见上）。分歧已消解。

## 环境隔离

`[PROD_NOT_TOUCHED]` —— 本汇总仅整合两位专家复核意见，未读取/修改任何生产代码。专家实测复现均在 /tmp/opencode 独立模拟目录完成并已清理。
