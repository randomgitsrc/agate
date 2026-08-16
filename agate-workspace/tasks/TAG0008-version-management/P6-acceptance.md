---
phase: P6
task_id: TAG0008
type: acceptance
parent: P5-verification.md
trace_id: TAG0008-P6-20260816
status: draft
created: 2026-08-16
agent: verifier
# ── v2.0 机器汇总 ──
pass: 31
fail: 0
ui_affected: false
---

# P6 — BDD 验收（agate 版本管理机制 v1）

> trace：TAG0008-P6-20260816（verifier，模式二）。验收依据 P1-requirements.md BDD-1~31
> （31 条，逐条实跑，无调整/跳过/覆盖）。本任务为 CLI/文件系统/git 行为（ui_affected=false），
> 验收动作 = tmp_path / 假 HOME 构造 Given 场景 → 真实运行 worktree 内脚本（agate-install /
> agate-resolve / agate-summary / resolve-entry / install-hook / agate-pack-offline /
> install-offline）→ 检查 exit code + 输出字段 + 文件/软链/git worktree list 状态。
> 全部在假 HOME + 临时 repo 内完成，未触碰真实 ~/.agate / 主 checkout `[PROD_NOT_TOUCHED]`。

## 门槛对照

- P6-acceptance.md 存在且非空，pass+fail = 31（BDD-1~31 全覆盖）✓
- 失败计数（fail）= 0 ✓
- 每条 PASS 有证据引用（括号内路径均存在）✓
- P6-evidence/ 非空 ✓
- gate 预检（format/evidence/provenance）通过 ✓

## 验收方法说明

1. **独立实跑为主**：每条 BDD 用真实 CLI 在假 HOME / 临时 git repo 内构造场景并运行，命令输出落盘 P6-evidence/。
2. **pytest 佐证**：dispatch-context 允许复用 P3 测试作为佐证。本任务对 offline 批（pack-offline /
   install-offline，pip download 网络依赖）跑 pytest 15 用例作技术佐证，同时补真实 CLI 打包/安装实跑
   （BDD-22/23/24/27/28 有真实 bundle 实跑证据，BDD-25/26 有真实 manifest 篡改实跑证据）。
3. **BDD-31**：gate 判定脚本 diff 对比（git diff 640607c HEAD 对 check-gate.py / pre-commit-gate.py /
   commit-msg-self-gate.py / pre-push-gate.py / ci-gate-backstop.py / check-p6-* 零改动）。

## 逐条结果

- PASS BDD-1: 无参安装建立 latest 指针指向版本目录，纯指针非 checkout 本体 (P6-evidence/bdd1-install.log)
- PASS BDD-2: 指定版本安装建立版本目录，git worktree list 可查该路径对应 tag v0.48.0，HEAD 与 tag 提交一致 (P6-evidence/bdd2-install.log, P6-evidence/bdd2-worktree.txt)
- PASS BDD-3: 重复安装幂等不报错，第二次输出"已安装，跳过（幂等）"，worktree list 中该版本路径不重复 (P6-evidence/bdd3-again.log)
- PASS BDD-4: 无参安装后 current 默认指向 latest，latest 指向最新发布版本目录 v0.48.0 (P6-evidence/bdd4-pointers.txt)
- PASS BDD-5: 卸载已安装版本删除目录并清理指针，worktree list 不再含该路径，latest/current 重指到剩余有效版本 v0.48.0 (P6-evidence/bdd5-uninstall.log, P6-evidence/bdd5-after.txt)
- PASS BDD-6: 项目仍引用该版本时卸载被拒绝并警告，stderr 指出被引用版本号与引用来源项目路径，v0.43.0 目录仍存在，worktree 仍含该版本 (P6-evidence/bdd6-uninstall.log)
- PASS BDD-7: 环境探测全齐时退出码 0，输出含 python3/pyyaml/git/bash 逐项 (P6-evidence/bdd7-check.log)
- PASS BDD-8: 环境探测缺 pyyaml（venv mock）时退出码非 0，输出列出缺失项并含 Linux 修复指引 pip install pyyaml（Windows 分支由 pytest windows_smoke 覆盖） (P6-evidence/bdd8-check.log)
- PASS BDD-9: 项目锁定版本命中，解析出 AGATE_ROOT=~/.agate/v0.43.0 与版本号 v0.43.0，原因引用 .agate-version (P6-evidence/bdd9-resolve.log, P6-evidence/pytest-bdd1to19.log)
- PASS BDD-10: 从 cwd 向上查找 .agate-version，子目录 a/b 运行仍解析到 v0.43.0 (P6-evidence/bdd10-resolve.log)
- PASS BDD-11: 无声明回退 current → latest → v0.44.0，原因标注"全局 current" (P6-evidence/bdd11-resolve.log)
- PASS BDD-12: AGATE_ROOT env 覆盖优先级最高，覆盖项目声明与全局 current，解析为 env 指定路径 (P6-evidence/bdd12-resolve.log)
- PASS BDD-13: 声明版本未安装（v0.99.0）时 stderr 输出警告，仍回退解析出 current 可用根，exit 0 不静默 (P6-evidence/bdd13-resolve.log, P6-evidence/bdd13-stderr.log)
- PASS BDD-14: 格式非法（random text / foo: bar / 空文件三种）均回退 current 并 stderr 格式警告，exit 0 不 crash (P6-evidence/bdd14a-invalid.log, P6-evidence/bdd14b-invalid.log, P6-evidence/bdd14c-empty.log)
- PASS BDD-15: install-hook 安装的 hook 指向固定解析入口 resolve-entry，hook 内容 exec resolve-entry.py 而非直接 exec 具体版本 gate py (P6-evidence/bdd15-hook-content.txt)
- PASS BDD-16: 项目 A 锁 v0.43.0 跑 GATE-V043、项目 B 无声明走 current 跑 GATE-V044，两项目互不干扰 (P6-evidence/bdd16-proj-a.log, P6-evidence/bdd16-proj-b.log, P6-evidence/pytest-hooks-integration.log)
- PASS BDD-17: 声明未安装版本时 hook 回退 current 跑 gate（GATE-V044 照常执行），stderr 警告非静默，不跳过 gate (P6-evidence/bdd17-resolve.log)
- PASS BDD-18: 改 .agate-version 声明（v0.43.0→v0.44.0）后直接 commit 即生效，无需重装 hook (P6-evidence/bdd18-v43.log, P6-evidence/bdd18-v44.log)
- PASS BDD-19: 复制模式（AGATE_HOOK_COPY_MODE=1）hook 经 .agate-root 标记恢复后仍按项目版本解析并跑 gate GATE-V043 (P6-evidence/bdd19-hook-run.log)
- PASS BDD-20: summary 显示项目解析到的版本 v0.43.0 与原因"引用 .agate-version" (P6-evidence/bdd20-summary.log)
- PASS BDD-21: summary 显示全局 current 回退版本 v0.44.0 与原因"全局 current" (P6-evidence/bdd21-summary.log)
- PASS BDD-22: pack-offline 真实打包产出 bundle（agate tag 代码 + pyyaml wheel + manifest.json），manifest 含 platform: linux-x86_64 与各组件 sha256 (P6-evidence/bdd22-pack-reallog.log, P6-evidence/bdd23-manifest-real.txt, P6-evidence/pytest-bdd22to29.log)
- PASS BDD-23: manifest.json 可解析出 platform 字段与每个组件 64 位 hex sha256 值（非空） (P6-evidence/bdd23-manifest-real.txt)
- PASS BDD-24: 失败路径 tag 不存在（v0.99.0）真实运行 exit 1、stderr 指明版本 tag 检出失败、不产出 manifest（坏包） (P6-evidence/bdd24-fail-tag.log)
- PASS BDD-25: install-offline 平台不匹配（bundle=windows-x86_64 vs 本机 linux-x86_64）时 stderr 警告含两平台字段值、exit 1 拒绝安装、不写 dest (P6-evidence/bdd25-platform-mismatch.log)
- PASS BDD-26: bundle 内 wheel 被篡改后 checksum 校验失败、exit 1 拒绝安装、输出指明被篡改组件（wheels, pyyaml）、不写 dest (P6-evidence/bdd26-checksum-mismatch.log, P6-evidence/pytest-bdd22to29.log)
- PASS BDD-27: wheels 以离线方式安装成功（pip install --no-index --find-links wheels/，venv 内 pyyaml 6.0.3 装上） (P6-evidence/bdd27-real-install.log)
- PASS BDD-28: 安装完成建立版本目录 dest/v0.48.0 + .installed-version=v0.48.0 + current 软链指向，agate-resolve（agate-summary 等价验证）显示 v0.48.0 (P6-evidence/bdd28-install-verify.log, P6-evidence/bdd28-resolve-verify.log)
- PASS BDD-29: --skip-python --skip-pillow 跳过对应安装步骤不报错，pyyaml 装上而 Pillow 未装，其余步骤（版本目录）照常完成 (P6-evidence/bdd29-skip-flags.log, P6-evidence/bdd29-skip-verify.log)
- PASS BDD-30: legacy 单软链布局（~/.agate 软链 → 旧 checkout 的 agate/ 子目录，无版本目录/无指针）不跑新工具，agate-resolve 将软链目标直接解析为 AGATE_ROOT，exit 0 无 breakage (P6-evidence/bdd30-legacy.log)
- PASS BDD-31: gate 判定脚本（check-gate.py / pre-commit-gate.py / commit-msg-self-gate.py / pre-push-gate.py / ci-gate-backstop.py / check-p6-*）在 v1 前后 diff 零改动，仅 hook 薄壳 exec 目标改为 resolve-entry（解析层改动） (P6-evidence/bdd31-gate-diff.txt)

## 补充佐证

- 版本管理单测（install/resolve/summary/install_hook/resolve-entry）34 用例全绿 (P6-evidence/pytest-bdd1to19.log)
- 离线 pack/install 单测 15 用例全绿 (P6-evidence/pytest-bdd22to29.log)
- hook 集成测试（pre-commit / commit-msg / pre-push）58 用例全绿 (P6-evidence/pytest-hooks-integration.log)

**Summary**: 31/31 PASS, 0 FAIL（BDD-1~31 全覆盖，真实 CLI 实跑 + pytest 佐证）