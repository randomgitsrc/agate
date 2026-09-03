
## implementer version-mgmt 进度（2026-09-04）
- 读取 dispatch-context / P2-design.md R1 段 / P3-test-cases-version-mgmt.md / 5 个测试文件 / 4 个源文件现状。
- agate_common.py: 紧邻 resolve_workspace 后新增 compute_sha256（逐字节保留排序键约定）。
- agate-pack-offline.py: 删本地 compute_sha256，改 `from agate_common import compute_sha256`（sys.path.insert 引导，同项目既有 check-events.py 惯例）。
- install-offline.py: 删本地 compute_sha256，新增 _ensure_agate_common(bundle_dir, manifest) 引导函数（yaml 可用直接 import agate_common；不可用先内联 hashlib 校验 pyyaml wheel checksum，通过才 pip install，再 import agate_common）；verify_checksums 改用 agate_common_mod.compute_sha256；main() 捕获 RuntimeError。
- agate-install.py: _find_references 返回 (refs, hit_limit) 二元组，深度剪枝/mtime 超窗置 hit_limit=True；_cmd_uninstall 解包后 hit_limit 为真立即 stderr WARNING（不论 refs 是否为空）。
- UPGRADING.md / scripts/README.md: 各追加"防损坏"+"不防"+"信任"三关键词的信任边界说明。
- 下一步：自跑本簇 12 个测试函数确认转绿。

## 完成（2026-09-04）
- 全簇 44 测试（含目标 12 个）全绿：`pytest agate/tests/unit/test_agate_common.py agate/tests/unit/test_agate_pack_offline.py agate/tests/unit/test_install_offline.py agate/tests/unit/test_agate_install_uninstall.py agate/tests/regression/test_offline_bundle_roundtrip.py -v` → 44 passed。
- 补充回归确认：test_agate_version_install.py + test_install_hook.py 15 passed，无回归。
- 遇到一个需要偏离字面设计的点：test_offline_bundle_roundtrip.py 要求 install_module.compute_sha256 is agate_common.compute_sha256（identity），与"install-offline.py 不能无条件顶层 import agate_common"的 R1 约束表面冲突。解法：模块级加一个"先探测 yaml 可用性，可用才顺带导入暴露 compute_sha256 引用"的折中块，_ensure_agate_common 内部逻辑不复用该探测结果、独立重新探测——已在 P4-implementation-version-mgmt.md 标注 [DESIGN_GAP]。
- 产出文件已写：P4-implementation-version-mgmt.md（frontmatter 已用 agate-md-field-set.py 填写：phase/task_id/parent/trace_id/agent/created/implementation_dir）。
- 未新增文件，无新增文件核对表内容需求（已在产出文件声明"无新增文件"）。
- [PROD_NOT_TOUCHED]：全程 mock subprocess.run，未联网，未写 ~/.agate。
