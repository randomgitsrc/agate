task: "agate 项目结构管理机制：RM-AG0008（0→1 项目目录结构脚手架）+ RM-AG0009（code-map + 架构演进纪律）。新增机制——骨架是'初始结构'、code-map 是'演进维护'，同一主题'项目结构管理'"

issues:
  - "RM-AG0008 0→1 项目无骨架设计：P0-brief 只写任务描述/风险/环境，无'项目骨架设计'环节；P1 analyst 分析需求、P2 architect 设计本次任务方案，都不要求设计整个项目目录布局。后果：CMakeLists/源码/测试/文档/构建产物散落、阶段文件与工程文件不同步（qtcalc-basic 复盘问题 C：CMake 引用尚未存在文件）。修复=①P1（或 P0）增'项目骨架'产出：按技术栈最佳实践输出目录树（C++/CMake：src/include/tests/docs/build/deploy；Web：src/components/hooks/pages/api）②骨架作为首个可验收产物，后续阶段产出落在骨架布局内 ③配 skeleton 模板"
  - "RM-AG0009 code-map + 架构演进纪律缺失：agate 每阶段（P2/P4）只对本次任务设计/实现，无全局架构视角；P7 一致性只查本次任务范围。缺'当前架构全貌'维护物（模块/层/依赖方向/关键文件）——subagent 每次独立上下文启动不知道项目有什么；缺'新增代码必须符合架构'约束——新增文件放哪层/依赖方向/是否复用抽象 vs 胶水堆叠；架构随版本漂移无防漂移机制。修复=①工作区维护 CODE-MAP.md（模块/层/依赖/关键文件/约定），P4 新增文件时更新，P7 核对漂移 ②P2 架构演进检查（新文件属哪层/依赖合规/复用抽象）③gate 或 WARNING 检测依赖方向偏离 ④P2 评审增设计模式合理性维度"

known_risks:
  - "RM-AG0008 新增'项目骨架'产出环节——需设计放哪个阶段（P0/P1）、怎么验证（目录树可验收）、配模板（按技术栈）——P2 设计关键决策"
  - "RM-AG0009 新增 CODE-MAP 维护物 + 架构演进纪律——CODE-MAP 放哪（工作区）、P2 怎么查架构合规、gate 怎么检测依赖偏离——设计决策多，P1/P2 需充分"
  - "两个都是'建'（新增机制），不是'修'——需完整 P0-P8，不能 plan 硬做（2026-08-13 用户确认：不为了 hotfix 故意不做 task）"
  - "涉及协议文档 + 模板 + 可能新增脚本（gate 检测依赖偏离）→ 触发 SELF-GATE"
  - "与 TAG0002（重构一等任务）关联：code-map 的架构演进纪律要兼容 refactor 类任务的变更记录"
  - "【强制要求】同类扫描 + 机制一致性：骨架/code-map 是全新机制，但落地时会触碰既有机制——P7 一致性检查、P2 架构评审、TAG0002 的 change_type 分流。P2 设计必须梳理'新增机制如何接入既有 gate/角色/卡片'，避免新机制与旧机制并存时的口径冲突。用户明确：不愿意一轮一轮来回改"

executor_env:
  platform: "opencode"
  has_task_tool: true
  has_local_runtime: true
  network: "full"
  git: true

env_constraints:
  debug_env: "本环境为 Linux；可在本仓库自举验证（agate 自己就是 0→1 项目的骨架案例）"
  test_cmd: "python3 -m pytest agate/tests/；python3 agate/scripts/check-protocol-consistency.py --strict；bash agate/tests/scripts/count-tests.sh"
  workspace_path: "{AGATE_WORKSPACE}/tasks/TAG0007-project-structure/"
  # 建机制类任务：骨架 + code-map 是协议新增能力，P2 设计核心（放哪阶段/格式/验证口径）
  # 时效性更新（2026-08-18）：bats 已退役（TAG0011 v0.47.0 迁 pytest），test_cmd 同步现行约定；network 改为 full（本环境演化）
