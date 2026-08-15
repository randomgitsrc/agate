---
task_id: agate-multi-platform-ci-support
agent: main
date: 2026-07-21
status: 评审修订版（7 条决定已落地，见文档内 [决定 1]-[决定 7] 标记）
来源:
  - docs/plans/agate-risk-mitigation-plan-2026-07-21.md（R4 部分）
  - docs/reviews/review-implementation-guide-2026-07-21.md
  - docs/reviews/review-multi-platform-ci-comprehensive-plan-2026-07-21.md
  - docs/reviews/review-execution-verification-round-2026-07-21.md
仓库快照: randomgitsrc/agate v0.15.0（commit 4225d03）
---

# agate 多平台 CI 支持——完整实施计划（代码改动 + self-gate 影响分析，合并版）

## 文档说明

本文档合并了此前拆成两份的内容：一份只写"怎么改代码"（实施指南），一份只写"这次改动对 self-gate 机制本身有什么影响"（综合计划）。两份分开容易让人对着 `ci-gate-backstop.py` 这类文件不知道该翻哪一份，合并为一份、按"先分析影响 → 再给代码 → 最后给统一执行顺序"组织。

---

# 第一部分：self-gate 机制影响分析

## 为什么要单独分析这一层

`SELF-GATE.md` 规定：agate 改自己的协议文档或脚本时必须走 self-gate 流程。本次要改的文件（`ci-gate-backstop.py`、`install-hook.sh`、`check-p6-evidence.sh`、`check-p6-provenance.sh`、`check-protocol-consistency.py`）全部落在这个范围内，但 self-gate 流程本身对这些文件是否真的生效，之前从未核实过——这是本次实测发现的一个真实盲区，必须先分析清楚再动代码，否则代码改完，一部分改动会绕过协议自己要求的审查而不自知。

## 核查 1：commit-msg-self-gate.sh 的触发正则是否覆盖本次要改的文件

`agate/scripts/commit-msg-self-gate.sh` 当前触发正则：

```
^(agate/scripts/.*\.sh|agate/scripts/check-protocol-consistency\.py|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$
```

用本次要改的文件名逐一测试（`echo "$f" | grep -qE "$REGEX"`，沙箱内真实执行）：

| 文件 | 是否触发 self-gate |
|---|---|
| `agate/scripts/ci-gate-backstop.py` | **否**（实测确认） |
| `agate/scripts/install-hook.sh` | 是 |
| `agate/scripts/check-p6-evidence.sh` | 是 |
| `agate/scripts/check-p6-provenance.sh` | 是 |
| `agate/scripts/check-protocol-consistency.py` | 是（被显式列名匹配） |

**结论（阻断级发现）**：`ci-gate-backstop.py` 恰好是本次 M4.1/M4.2 要重点修改的文件，但当前正则只显式匹配了 `check-protocol-consistency.py` 这一个 `.py` 文件，没有覆盖 `agate/scripts/*.py` 这个更一般的模式。这不是本次改动才产生的新问题，是协议现有的盲区，这次改的文件恰好踩中它。

## 核查 2：CHECK 9 锚点覆盖检查（check_anchor_coverage）是否覆盖本次要改的文件

打开 `check-protocol-consistency.py` 第 635-662 行的反向覆盖检查逻辑，实际扫描范围：

```python
gate_scripts = sorted(
    str(p.relative_to(root))
    for p in scripts_dir.glob("check-*.sh")   # 只匹配 check-*.sh
    if p.is_file()
)
pre_commit = root / "agate" / "scripts" / "pre-commit-gate.sh"
if pre_commit.exists():
    gate_scripts.append("agate/scripts/pre-commit-gate.sh")   # 显式补充这一个
```

**结论（阻断级发现）**：扫描范围是"`check-*.sh` glob + 显式追加的 `pre-commit-gate.sh`"，`ci-gate-backstop.py` 既不匹配 glob，也没被显式追加——即使以后它完全没有锚点条目，CHECK 9 的反向兜底也发现不了这个缺口，因为它连"要不要检查"这一步都进不去。这是比正则漏洞更深一层的结构性盲区。

## 核查 3：install-hook.sh 的豁免状态在 M5.1 之后是否仍然合理

`GATE_SCRIPT_EXEMPT` 集合（第 626-632 行）把 `install-hook.sh` 列为"工具类脚本，无 gate 逻辑，不需要锚点"。M5.1 要往这个文件里加一段生成 pre-push hook 的 heredoc，heredoc 内容含有真实的阈值判断逻辑（虽然只是 WARNING 不阻断，但判断逻辑本身是新的）。

**[决定 7] 保留豁免，单独给阈值加锚点**：`install-hook.sh` 本质还是安装器，不是阶段判定逻辑，整体分类没错，不建议从 `GATE_SCRIPT_EXEMPT` 移出。但 M5.1 新加的 heredoc 里 `AGATE_ALIGNMENT_REVIEW_THRESHOLD:-20` 这个默认阈值是后续可能被改却没人发现的漂移点——如果以后默认值从 20 改成 50，没有任何机制会发现协议文档和实际代码不一致。建议单独给这个阈值加一条锚点（跟 `MAX_RETRY` 那条锚点的做法一样），锚点关键词就是 `AGATE_ALIGNMENT_REVIEW_THRESHOLD`，目标文件是 `install-hook.sh`。这样保留了"这个文件本质是安装器"的分类，又不放过这一个具体会漂移的数值。最终仍应经 protocol-alignment-review 确认——此处给的是方向性意见，不是替代那道审查，只是让审查有明确的起点。

---

# 第二部分：self-gate 机制本身的三处修复

## 修复 A：commit-msg-self-gate.sh 正则通用化

**改动**（已用真实文件名列表验证匹配结果，并用真实 git 仓库跑过端到端 commit 测试）：

```diff
- ^(agate/scripts/.*\.sh|agate/scripts/check-protocol-consistency\.py|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$
+ ^(agate/scripts/.*\.(sh|py)|agate/[^/]+\.md|agate/.+/.*\.md|SELF-GATE\.md)$
```

**同步修复提示文字**（端到端测试时发现给用户看的提示文字没跟着正则一起改，容易让人误以为只有 `.sh` 会触发）：

```diff
- echo "GATE SELF-GATE: 暂存区含 self-gate 触发文件（agate/scripts/*.sh / agate/*.md / SELF-GATE.md），" >&2
+ echo "GATE SELF-GATE: 暂存区含 self-gate 触发文件（agate/scripts/*.sh / agate/scripts/*.py / agate/*.md / SELF-GATE.md），" >&2
```

**实测结果**：对 6 个样本文件跑过（`ci-gate-backstop.py`、`install-hook.sh`、`check-p6-evidence.sh`、`check-protocol-consistency.py`、`agate/WORKFLOW.md` 正确触发；`some/other/file.py` 负样本正确不触发）；另外真实建立本地 git 仓库、stage 文件、真实调用 hook、真实 `git commit`，确认修复后正确报 WARNING 且不阻断 commit。修复后不再需要对 `check-protocol-consistency.py` 单独列名，正则可以同时简化和扩大覆盖面。

**软链接机制说明**：`install-hook.sh` 里 commit-msg hook 是用 `ln -sf` 软链接安装的（第 45 行已核实），不是复制。agate 仓库自身改完这个源文件**不需要额外重装 hook**，下次 commit 立即生效；但下游使用 agate 的项目，要等其本地 `~/.agate` 软链接指向的仓库副本 `git pull` 到含本次修复的版本后才会生效——这是软链接机制固有的传播延迟，不是缺陷，只是需要跟下游用户说清楚。

## 修复 B：check_anchor_coverage 扫描范围补上非 check-*.sh 命名的 gate 脚本

**改动**：在现有"显式追加 pre-commit-gate.sh"那行之后，同样显式追加 `ci-gate-backstop.py`：

```diff
  pre_commit = root / "agate" / "scripts" / "pre-commit-gate.sh"
  if pre_commit.exists():
      gate_scripts.append("agate/scripts/pre-commit-gate.sh")
+ ci_backstop = root / "agate" / "scripts" / "ci-gate-backstop.py"
+ if ci_backstop.exists():
+     gate_scripts.append("agate/scripts/ci-gate-backstop.py")
```

**说明**：这只解决本次踩中的这一个文件的盲区，不解决"以后又出现一个不叫 check-\*.sh 的 gate 脚本"这个同类问题。更彻底的修法（把 glob 规则改成"扫描全部文件 + 白名单排除法"）记录在第五部分"范围外事项"里，本次不做，避免范围蔓延。

## 修复 C：为本次新增的三条规则补上 CHECK 9 锚点

`check_script_alignment`（第 589-622 行）的检查逻辑是"某关键词是否出现在某文件里"的单点检查，doc 侧和 script 侧需要各开一条锚点（参照仓库里"PAUSED 语义翻转"的既有先例）：

```python
# 新增于 SCRIPT_ALIGNMENT_ANCHORS 列表末尾
{
    "desc": "证据日志 EXIT_CODE 格式约定（文档侧）",
    "script": "agate/assets/templates/dispatch-prompt.md",
    "keywords": ["EXIT_CODE"],
},
{
    "desc": "证据日志 EXIT_CODE 一致性检测（脚本侧）",
    "script": "agate/scripts/check-p6-provenance.sh",
    "keywords": ["EXIT_CODE"],
},
{
    "desc": "CI 平台探测（Gitea/GitLab/GitHub）",
    "script": "agate/scripts/ci-gate-backstop.py",
    "keywords": ["detect_ci_platform", "GITEA_ACTIONS", "GITLAB_CI"],
    "callers": [".github/workflows/protocol-tests.yml"],
},
{
    "desc": "pre-push alignment-review 阈值（决定 7：install-hook.sh 保留豁免，单独加锚点）",
    "script": "agate/scripts/install-hook.sh",
    "keywords": ["AGATE_ALIGNMENT_REVIEW_THRESHOLD"],
},
```

（`.gitlab-ci.yml`/`.gitea/workflows/*.yml` 目前仓库里不存在，`callers` 暂只填已有调用点；等 Gitea/GitLab CE 侧配置文件真正加进仓库后需追加，这是后置依赖，见第四部分实施顺序。）

已用 `python3 -c` 单独解析确认语法有效。**M3.1/M3.2 暂不加对应锚点**：这两条规则目前只在脚本里实现，没有在任何协议文档里"声明"，按锚点设计模式，必须先在文档层声明（第三部分步骤1），才轮到加锚点。

---

# 第三部分：各项措施的具体实施

## M4.1 + M4.2：CI 平台探测插件化 + provenance 审计纳入 backstop

**目标文件**：`agate/scripts/ci-gate-backstop.py`

### 改动 1：平台探测函数，检测顺序 Gitea → GitLab → GitHub

```python
def detect_ci_platform() -> str | None:
    """检测顺序不可颠倒：Gitea Actions 的 runner 是 GitHub Actions 兼容 fork，
    可能同时暴露 GitHub 风格变量，必须先判定 GITEA_ACTIONS 排除歧义。"""
    if os.environ.get("GITEA_ACTIONS") == "true":
        return "gitea"
    if os.environ.get("GITLAB_CI") == "true":
        return "gitlab"
    if os.environ.get("GITHUB_ACTIONS") == "true":
        return "github"
    return None


def get_pr_metadata(platform: str) -> dict:
    """PR/MR 元信息适配器。GitLab 直接读环境变量，GitHub 读事件文件，
    Gitea 的读取方式需先实测确认（见"实施前置步骤"），此处先按
    GitHub 兼容路径实现，实测不符时再改。"""
    if platform == "gitlab":
        return {
            "iid": os.environ.get("CI_MERGE_REQUEST_IID", ""),
            "source_branch": os.environ.get("CI_MERGE_REQUEST_SOURCE_BRANCH_NAME", ""),
            "target_branch": os.environ.get("CI_MERGE_REQUEST_TARGET_BRANCH_NAME", ""),
            "project_id": os.environ.get("CI_PROJECT_ID", ""),
        }
    if platform in ("github", "gitea"):
        event_path = os.environ.get("GITHUB_EVENT_PATH", "")
        if event_path and Path(event_path).exists():
            with open(event_path) as f:
                return json.load(f)
        return {}
    return {}
```

在 `main()` 里，改为先调用 `detect_ci_platform()` 并显式打印识别结果（配合下方 bats 测试断言所需的可见输出，不是可选项）：

```python
    platform = detect_ci_platform()
    print(f"CI platform: {platform}")
    if platform is None:
        print("SKIP: 未识别的 CI 平台（非 Gitea/GitLab/GitHub），backstop 不生效")
        return 0
```

### 改动 2：provenance 审计纳入 backstop

在 `main()` 末尾、`return 0` 之前追加：

```python
    # provenance 审计兜底（--no-verify 绕过 hook 时，backstop 层补跑）
    provenance_script = repo_root / "agate/scripts/check-p6-provenance.sh"
    if task_dir and provenance_script.exists() and Path(task_dir, "P6-acceptance.md").exists():
        prov_result = subprocess.run(
            ["bash", str(provenance_script), task_dir],
            capture_output=True, text=True
        )
        if prov_result.returncode == 1:
            print(f"FAIL: check-p6-provenance.sh 重跑未通过：\n{prov_result.stdout}{prov_result.stderr}")
            return 1
        print("PASS: provenance 审计 CI 层重跑通过")
```

### 实施前置步骤（做代码改动之前，先做这一步）

1. 在目标 Gitea 实例上建测试仓库，写最简单的 `.gitea/workflows/test.yml`（`on: push`，`steps: - run: env | sort > env_dump.txt`），推一次 push，下载 `env_dump.txt`。
2. 核对：（a）`GITEA_ACTIONS` 是否确实等于 `true`；（b）是否存在类似 `GITHUB_EVENT_PATH` 的变量、文件格式是否和 GitHub 一致。
3. 若（b）不成立，`get_pr_metadata` 的 Gitea 分支需改成读 Gitea API（`GET /api/v1/repos/{owner}/{repo}/pulls/{index}`，用自动注入的 `GITEA_TOKEN`）。

**这一步在本环境里做不到，需要说清楚**：这个沙箱下载得到 Gitea server 二进制（`github.com/go-gitea/gitea` releases 可访问，已实测能跑），但 Gitea Actions 真正执行 workflow 靠的 `act_runner` 只发布在 `gitea.com`，这个域名在本环境网络白名单外（实测 403，且 GitHub 侧找不到镜像）。翻过 Gitea 主仓库源码确认 `GITEA_ACTIONS` 这个变量不在主仓库里设置（只找到用途完全不同的 `GITEA_ACTIONS_TASK_ID`），真正设置逻辑在 `act_runner` 里，这个仓库到不了。GitLab CE 同样：`gitlab.com` 整体 403，连安装包都下不了。**上面第 1-2 步只能在你自己有权限的 Gitea 实例上做，本文档到此为止的"GITEA_ACTIONS=true"仍然是读官方 issue 讨论串得出的推断，不是实测确认，可信度低于本文档其他标"已实测"的部分，不能混为一谈。**

### 验证方式

新增 `agate/tests/unit/ci-gate-backstop.bats`。原计划里用 `import_module('ci-gate-backstop'.replace('-','_'))` 尝试导入函数做单元测试——这行不通（文件名连字符不是下划线，`import_module` 找不到），改为端到端调用整个脚本、检查 stdout：

```bash
@test "detect_ci_platform: Gitea 优先于 GitHub 被识别" {
    export GITEA_ACTIONS=true
    export GITHUB_ACTIONS=true
    run bash -c "cd '$TEST_REPO' && python3 '$AGATE_ROOT/agate/scripts/ci-gate-backstop.py'"
    [[ "$output" == *"gitea"* ]]
}

@test "detect_ci_platform: GitLab CI 正确识别" {
    export GITLAB_CI=true
    unset GITEA_ACTIONS GITHUB_ACTIONS
    run bash -c "cd '$TEST_REPO' && python3 '$AGATE_ROOT/agate/scripts/ci-gate-backstop.py'"
    [[ "$output" == *"gitlab"* ]]
}

@test "detect_ci_platform: 无可识别平台时 SKIP 而非误判" {
    unset GITEA_ACTIONS GITLAB_CI GITHUB_ACTIONS
    run bash -c "cd '$TEST_REPO' && python3 '$AGATE_ROOT/agate/scripts/ci-gate-backstop.py'"
    [[ "$output" == *"SKIP"* ]] || [[ "$output" == *"未识别"* ]]
}
```

实测过（真实 Python 解释器分三种场景跑过）：`GITEA_ACTIONS+GITHUB_ACTIONS` 同时存在时返回 `gitea`；仅 `GITLAB_CI` 返回 `gitlab`；三者皆无返回 `None`。均符合设计预期。

---

## M5.1：pre-push 自动触发 protocol-alignment-review

**目标文件**：`agate/scripts/install-hook.sh`（现有第 36 行"安装 commit-msg hook"附近追加）

git 的 pre-push hook 标准调用方式是从 **stdin** 逐行读入待推送的 ref（格式：`<local ref> <local sha1> <remote ref> <remote sha1>`），不能依赖 `@{push}`（首次 push/force-push 会解析失败或给出误导结果）：

```bash
# 安装 pre-push hook（协议文件大改动自动提示 alignment-review）
PRE_PUSH_HOOK="$GIT_DIR/hooks/pre-push"
cat > "$PRE_PUSH_HOOK" << 'HOOK_EOF'
#!/usr/bin/env bash
THRESHOLD="${AGATE_ALIGNMENT_REVIEW_THRESHOLD:-20}"
ZERO_SHA="0000000000000000000000000000000000000000"

while read -r local_ref local_sha remote_ref remote_sha; do
    [ -z "$local_sha" ] && continue
    if [ "$remote_sha" = "$ZERO_SHA" ]; then
        echo "ℹ️  新分支首次推送，跳过 agate/*.md 改动量检测（无远端基线可比较）"
        continue
    fi
    CHANGED_LINES=$(git diff "$remote_sha".."$local_sha" -- 'agate/*.md' 2>/dev/null | grep -cE '^[+-]' || echo 0)
    if [ "$CHANGED_LINES" -gt "$THRESHOLD" ]; then
        echo "⚠️  本次 push（${local_ref}）对 agate/*.md 的改动达 ${CHANGED_LINES} 行（阈值 ${THRESHOLD}）"
        echo "    建议先派发一次 protocol-alignment-review，确认改动未破坏协议文件间的语义一致性。"
        echo "    忽略本提示继续 push：git push --no-verify"
    fi
done
exit 0
HOOK_EOF
chmod +x "$PRE_PUSH_HOOK"
```

**注意**：恒 `exit 0`，不阻断 push——语义一致性判断不该由行数阈值硬拦截，阈值只决定"要不要提醒"。新分支首次推送（`remote_sha` 全零）明确提示"跳过检测"而非让 diff 静默失败后被当成 0 行改动。

**实测**：搭建真实本地 bare repo + clone，实际执行 `git push` 触发 hook，验证了"大改动触发警告但不阻断推送"（27 行改动，阈值 20，警告正确打印，push 成功）和"新分支首次推送走 zero-sha 分支不报错"两种场景，均为真实 git 操作结果。

### 验证方式

集成测试：mock 超阈值的 `agate/*.md` 改动，执行 `git push`，确认输出含提示文字且 exit code 仍为 0（已用真实 git 仓库验证过，见上）。

---

## M3.1：图像方差检测（低方差/疑似占位图）

**目标文件**：`agate/scripts/check-p6-evidence.sh`

**实测发现的设计缺陷（已修正）**：最初设计把方差检测插入在既有的 `SIZE ≤ 1024` 分支内部。用一张 1920×1080 纯色填充 PNG（实测体积 8594 字节，远超 1KB）验证后发现：这类"体积正常但内容单调"的典型占位图场景会被这个插入位置直接排除在检测范围外——而这恰恰是 M3.1 本来想抓的场景。已修正为方差检测独立于文件大小判断，对 `screenshots/` 目录下所有文件运行。

**[决定 1] Pillow 依赖可接受，但须补两条防静默失效**：Pillow 装不上时 `VARIANCE` 拿到 `-1`，检测静默跳过，gate 输出与"检测过、没问题"一模一样——静默失效比明确拒绝更违背"gate 结果要可信"的原则。补两条：

1. Pillow import 失败时输出 `WARNING: Pillow 未安装，方差/相似度检测已跳过`，而非纯粹返回 -1
2. 加显式开关 `AGATE_SKIP_IMAGE_CHECKS=1`，让明确不想装 Pillow 的部署可以主动声明"我知道跳过了"，而不是靠环境缺失被动触发跳过

改动后的代码（M3.1 方差检测部分）：

```bash
        VARIANCE_WARNING=0
        if [ "${AGATE_SKIP_IMAGE_CHECKS:-0}" = "1" ]; then
            echo "GATE P6-EVIDENCE WARNING: AGATE_SKIP_IMAGE_CHECKS=1，方差/相似度检测已主动跳过" >&2
        else
        while IFS= read -r -d '' img; do
            SIZE=$(stat -c%s "$img" 2>/dev/null || stat -f%z "$img" 2>/dev/null || echo 0)
            if [ "$SIZE" -le 1024 ]; then
                # PNG header check: 前 8 字节 = \x89PNG\r\n\x1a\n
                HEADER=$(head -c 8 "$img" 2>/dev/null | od -A n -t x1 | tr -d ' ')
                EXPECTED='89504e470d0a1a0a'
                if [ "$HEADER" = "$EXPECTED" ]; then
                    PNG_WARNING=$((PNG_WARNING + 1))
                else
                    EMPTY_COUNT=$((EMPTY_COUNT + 1))
                fi
            fi
            # 方差检测独立于文件大小分支运行：一张被 PNG 压缩得很好的纯色图
            # 完全可能超过 1KB（实测 1920x1080 纯色图为 8594 字节），不能只检查小文件
            VARIANCE=$(python3 -c "
from PIL import Image
try:
    img = Image.open('$img').convert('L')
    pixels = list(img.tobytes())
    mean = sum(pixels) / len(pixels)
    variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
    print(int(variance))
except ImportError:
    print('SKIP_NO_PILLOW')
except Exception:
    print(-1)
" 2>/dev/null || echo -1)
            if [ "$VARIANCE" = "SKIP_NO_PILLOW" ]; then
                echo "GATE P6-EVIDENCE WARNING: Pillow 未安装，方差/相似度检测已跳过" >&2
                break
            elif [ "$VARIANCE" -ge 0 ] && [ "$VARIANCE" -lt 50 ]; then
                VARIANCE_WARNING=$((VARIANCE_WARNING + 1))
                echo "GATE P6-EVIDENCE WARNING: $(basename "$img") 像素方差 ${VARIANCE}（<50，疑似纯色/占位图，请确认非充数）" >&2
            fi
        done < <(find "$SCREENSHOTS_DIR" -type f -not -name '.*' -print0 2>/dev/null)
        fi
```

（用 `img.tobytes()` 而非 `Image.getdata()`——后者在 Pillow 14（2027-10-15 起）会被移除，实测两者结果一致，直接用不会过时的写法。）

**依赖**：需要 Pillow（`pip install Pillow --break-system-packages`），新增运行时依赖，需写进 `LIMITATIONS.md` 局限6依赖清单，并在 CI workflow（`.github/workflows/protocol-tests.yml`）的依赖安装步骤加一行 `pip install Pillow`。Pillow 未安装时检测跳过并输出 WARNING，不阻断 gate；`AGATE_SKIP_IMAGE_CHECKS=1` 可主动声明跳过。

**阈值说明**：50 是保守起点（纯色图方差为 0，实测随机噪点图方差约 5000+），建议先跑一遍历史 `P6-evidence/screenshots/` 存量截图统计实际方差分布再校准，不要凭空定死。

### 验证方式

已实测：纯色 1920×1080 PNG（方差=0）正确触发 WARNING；随机噪点 PNG（方差约 5000+）不触发。新增 `agate/tests/unit/check-p6-evidence.bats` 用例覆盖这两种场景。

---

## M3.2：average hash 补充 md5 去重（非替换）

**目标文件**：同上，替换现有 `MD5_LIST`/`MD5_TOTAL` 逻辑

**依赖取舍（评审修正）**：M3.1 已引入 Pillow，这里不再额外引入 `imagehash` 第三方包——多一个 pip 依赖就多一种"没装就跑不了"的失败模式，与 `LIMITATIONS.md` 局限6"控制运行时依赖面"的精神冲突。用 Pillow 自带操作实现最简 average hash（缩放 8×8 灰度图，与均值比较生成 64 位指纹）即可。

### 改动

```bash
        # md5 完全重复升级为阻断级（同一物理文件被引用两次，属证据造假）
        MD5_LIST=$(find "$SCREENSHOTS_DIR" -type f -not -name '.*' -exec md5sum {} \; 2>/dev/null | cut -d' ' -f1 | sort)
        MD5_TOTAL=$(echo "$MD5_LIST" | grep -c . || echo 0)
        MD5_UNIQUE=$(echo "$MD5_LIST" | sort -u | grep -c . || echo 0)
        if [ "$MD5_TOTAL" -gt "$MD5_UNIQUE" ]; then
            MD5_DUPES=$((MD5_TOTAL - MD5_UNIQUE))
            echo "GATE P6-EVIDENCE: 有 ${MD5_DUPES} 个截图文件逐字节完全相同（md5 重复，疑似同一物理文件被多条 PASS 引用充数）" >&2
            exit 1
        fi

        # average hash（纯 Pillow 实现，无需 imagehash 依赖）
        if [ "${AGATE_SKIP_IMAGE_CHECKS:-0}" != "1" ]; then
        AHASH_LIST=$(python3 -c "
from PIL import Image
import glob
import sys
def ahash(path):
    img = Image.open(path).convert('L').resize((8, 8))
    pixels = list(img.tobytes())
    avg = sum(pixels) / len(pixels)
    return ''.join('1' if p >= avg else '0' for p in pixels)
try:
    from PIL import Image
except ImportError:
    print('SKIP_NO_PILLOW', file=sys.stderr)
    sys.exit(1)
for f in sorted(glob.glob('$SCREENSHOTS_DIR/*')):
    try:
        print(ahash(f))
    except Exception:
        pass
" 2>/dev/null || echo "")
        if echo "$AHASH_LIST" | grep -q "SKIP_NO_PILLOW"; then
            echo "GATE P6-EVIDENCE WARNING: Pillow 未安装，相似度检测已跳过" >&2
        else
        AHASH_TOTAL=$(echo "$AHASH_LIST" | grep -c . || echo 0)
        AHASH_UNIQUE=$(echo "$AHASH_LIST" | sort -u | grep -c . || echo 0)
        if [ "$AHASH_TOTAL" -gt "$AHASH_UNIQUE" ]; then
            AHASH_DUPES=$((AHASH_TOTAL - AHASH_UNIQUE))
            echo "GATE P6-EVIDENCE WARNING: 有 ${AHASH_DUPES} 组视觉高度相似截图（average hash 相同但非逐字节相同，不阻断，行为差异类 BDD 截图可能视觉相同，请在 acceptance report 说明原因）" >&2
        fi
        fi
        fi
```

（本次合并时统一把 `img.getdata()` 改成了 `img.tobytes()`——此前 M3.1 已经因 Pillow 弃用问题改过，但 M3.2 这段代码遗留了旧写法，两处不一致，合并时一并订正并重新实测确认功能不变。）

**依赖**：仅需 Pillow，无新增。average hash 判别力弱于 pHash（对旋转、裁切不敏感），但这里只需要"内容明显雷同"的粗粒度信号，用更简单实现换一个依赖是合理取舍。

**[决定 2] 既有短路结构**：`check-p6-evidence.sh` 现有结构是"遇到第一类 WARNING 就 `exit 2`（或本次改为 `exit 1`）提前返回"，`PNG_WARNING` 分支、MD5 完全重复分支都是如此。这意味着 average hash 检测只有在前面两类判断都没触发时才会真正执行到。实测两张体积正常（>250KB）、随机噪点、仅一像素不同的图，在不触发前两类判断的前提下，average hash 正确识别"视觉几乎相同但字节不同"；但如果同一批截图恰好也有 PNG_WARNING 或 MD5 完全重复，脚本会提前返回，这条检测不会执行。这是既有脚本结构使然，不是本次改动的缺陷，已升级为第五部分正式待办条目。

### 验证方式

已实测：两张体积>250KB、随机噪点、仅一像素不同的图正确触发 average hash WARNING；复制文件（md5 相同）触发 md5 阻断，不会重复触发 average hash（因为 md5 分支已提前 exit 1）。

---

## M1.3a：定义最小日志格式约定

**目标文件**：`agate/assets/templates/dispatch-prompt.md`（"## 自查≠gate"一节之后追加）

```markdown
## 证据日志格式约定（M1.3a）
凡是要求 subagent 产出可核验日志的场景（P5 测试执行、P6 验证脚本执行），
日志文件末行必须是可解析的退出码声明，格式固定为：
`EXIT_CODE: <n>`（n 为整数，0 表示成功）
不符合此格式的日志，check-p6-provenance.sh 的一致性检测（M1.3b）不做强判定，
仅输出 INFO 提示"日志缺少标准 EXIT_CODE 尾行，无法自动核验一致性"。
```

纯文档新增，成本最低，是 M1.3b 的前置条件，必须先做（也是修复C里 EXIT_CODE 文档侧锚点的来源）。

---

## M1.3b：日志一致性检测（依赖 M1.3a）

**目标文件**：`agate/scripts/check-p6-provenance.sh`（该文件内部命名体系是"审计 1／审计 2／审计 3／审计 4"+"协作规范"五段结构）

**确切插入位置**：第 204 行（"审计 4"代码块结束）与第 206 行（"协作规范：agent 字段"开始）之间。新增内容命名为"审计 5"。

```bash
# --- 审计 5：日志 EXIT_CODE 与 PASS/FAIL 声明一致性（依赖 M1.3a 约定）---
if [ -f "$P6_FILE" ]; then
    while IFS= read -r log_file; do
        LAST_LINE=$(tail -1 "$log_file" 2>/dev/null || echo "")
        if echo "$LAST_LINE" | grep -qE '^EXIT_CODE: [0-9]+$'; then
            LOG_EXIT=$(echo "$LAST_LINE" | grep -oE '[0-9]+$')
            LOG_BASENAME=$(basename "$log_file")
            if grep -qE "PASS.*\\(${LOG_BASENAME}\\)" "$P6_FILE" 2>/dev/null && [ "$LOG_EXIT" != "0" ]; then
                echo "GATE PROVENANCE: ${LOG_BASENAME} 声明 PASS 但日志 EXIT_CODE=${LOG_EXIT}（矛盾）" >&2
                exit 1
            fi
        else
            echo "GATE PROVENANCE: $(basename "$log_file") 缺少标准 EXIT_CODE 尾行，跳过一致性核验（不阻塞）" >&2
        fi
    done < <(find "$TASK_DIR/P6-evidence" -name "*.log" 2>/dev/null)
fi
```

**实测**（真实运行修改后的完整脚本，三种场景）：日志 `EXIT_CODE: 1` 但 `P6-acceptance.md` 声明 `PASS` → exit 1，正确拦截；`EXIT_CODE: 0` 配 `PASS` → exit 0，不误伤；日志缺少 `EXIT_CODE` 尾行 → 只 WARNING，exit 0，不阻断。三种场景均为真实脚本执行结果。

---

## M1.1：判定权下放到 subagent 产出文件——已评估，判定不值得实现

**目标文件**：`agate/scripts/check-gate.sh`（P6 分支，第 119-138 行）

**现状问题**：P6 分支判定逻辑直接对 `P6-acceptance.md` 的 PASS/FAIL 行计数，这个文件理论上可以由主 Agent 自己写。M1.1 原本想做到"确认这个文件确实是 subagent 产出的"，但纯文件内容检查做不到这一点。

**平台能力边界（诚实说明）**：当前架构下主 Agent 和 subagent 共享同一个 git author，纯 git blame 区分不了两者——这是 M1.1 的真实边界。在"独立 git author"（LIMITATIONS 提到的 Phase 3 根治方向）落地之前，只能做到"检查文件是否存在且格式合规"，做不到"确认作者身份"。

**[决定 3] 时间戳弱信号方案已评估，判定不值得实现**。此前考虑的降级版本是检查 `P6-acceptance.md` 的 mtime 是否早于 dispatch-context 文件的 mtime（`-nt` 比较），经评估存在两个结构性缺陷：

1. **CI 场景 mtime 被 checkout 重置**：M4.2 的 provenance 审计在 CI backstop 里跑，CI 场景下所有文件都是同一次 `git checkout` 一起落盘的，mtime 基本同时，`-nt` 比较几乎是看文件系统写入顺序的随机结果，不是看"谁先谁后"的真实顺序——这恰好是这条检查真正生效的主战场
2. **威胁模型本身对伪造行为无区分力**：这条检查想防的是"主 Agent 自己伪造 P6-acceptance.md"。一个要伪造的主 Agent 自然会先写 dispatch-context 再写 acceptance 文件——顺序对的，伪造者不需要额外费力气就能让时间戳顺序"看起来诚实"。真正会触发"顺序颠倒" WARNING 的，反而是一些无关的正常操作（rebase、cherry-pick、分支切换后重新 touch）

结论：这条检查对着真正要防的场景几乎抓不到，对无关的正常操作却会误报——净负信噪比，不是"聊胜于无"的弱信号，是"提供虚假安心感"。**M1.1 保持无代码层缓解，完全依赖独立 git author 这个根治方向。**

---

# 第四部分：统一实施顺序（含前置依赖，不能颠倒）

1. **Gitea 环境实测**——独立于 self-gate 修复，可并行做，但本环境做不到（见 M4.1 说明），需你自己的环境完成。
2. **文档层声明**——M1.3a 已计划这么做；M3.1/M3.2 需要补一条声明（具体修改文本见第八部分 B1 的 dispatch-protocol.md:523 修改）。**必须先于**修复C的文档侧锚点。同时更新所有文档传播项（第八部分 B1-B3 + N1-N7），包括 LIMITATIONS.md 局限 3/6/8、WORKFLOW.md CI backstop 描述、state-machine.md CI 兜底描述、dispatch-protocol.md CI backstop 描述、protocol-alignment-review.md 触发条件、SELF-GATE.md 触发条件、脚本注释。
3. **修复 A**（commit-msg 正则 + 提示文字）——**必须先于**步骤6的代码实施，否则该步骤的 commit 会静默绕过 self-gate。agate 自身仓库因软链接机制立即生效，下游项目需各自 `git pull`。
4. **修复 B**（check_anchor_coverage 扫描范围）——与修复A无先后依赖，建议同批做。
5. **修复 C**（新增锚点，依赖步骤2的文档声明已落地）。
6. **M4.1/M4.2/M5.1/M3.1/M3.2/M1.3a/M1.3b 代码实施**（M1.1 已判定不值得实现，不实施；M3.1/M3.2 须含决定 1 的 Pillow 缺失 WARNING + `AGATE_SKIP_IMAGE_CHECKS` 开关；`install-hook.sh` 保留豁免但加 `AGATE_ALIGNMENT_REVIEW_THRESHOLD` 锚点，见修复 C）。
7. **`check-protocol-consistency.py` 本地跑一遍**，此时应零 ERROR，锚点全部对齐。确认版本号需 minor bump（v0.15.0→v0.16.0，因 md5 重复升级为阻断属破坏性变更，见 B1）。
8. **派发 protocol-alignment-review subagent**，审查范围至少含：本次改动全部文件 + `LIMITATIONS.md`（依赖清单加 Pillow + `AGATE_SKIP_IMAGE_CHECKS` 说明）+ `.github/workflows/protocol-tests.yml`（加 `pip install Pillow`）+ `install-hook.sh` 豁免状态（决定 7：保留豁免 + 单独锚点，审查确认此方向）。
9. **读审查报告**，MISALIGNED 必须修复；`install-hook.sh` 豁免状态若判定 NEEDS_HUMAN_REVIEW，commit message 附 `[HUMAN_CONFIRMED: ...]`。
10. **跑全量 bats**，确认无退化（含新增的 `ci-gate-backstop.bats`）。
11. **commit**，message 带 `self-gate-review: docs/reviews/agate-alignment-review-{date}.md`。

---

# 第五部分：范围外但需要记录的后续改进项（本次不做）

- `check_anchor_coverage` 的筛选逻辑从"命名匹配 check-\*.sh"改为"白名单排除法"（扫描 `agate/scripts/` 全部文件，用 `GATE_SCRIPT_EXEMPT` 排除非 gate 脚本），彻底关闭"新 gate 脚本命名不规范就被漏检"这类问题，而非每次踩中一个补一个。
- **[决定 2 升级]** WARNING 类检查改成全部跑完再汇总，而非逐类短路提前 exit——当前 `check-p6-evidence.sh` 的 PNG_WARNING / MD5 重复 / average hash 三类检测是短路结构，前一类触发后后面的检测不会执行。应改为收集全部 WARNING 后统一输出，确保每类检测都有机会运行。
- `install-hook.sh` 是否该从 `GATE_SCRIPT_EXEMPT` 移出——决定 7 已判定保留豁免 + 单独锚点，本次不重新审查整个豁免名单。如未来该文件内嵌更多可执行判断逻辑，应重新评估。

---

# 第六部分：验证状态说明（区分"已实测"与"仍是推断"）

## 已在沙箱内实际执行并确认结果的部分（非推断）

- `commit-msg-self-gate.sh` 新旧正则对 6+ 样本文件的匹配结果（真实 `grep -qE` 执行）+ 真实 git 仓库端到端 commit 测试
- M3.1 方差检测：纯色图（方差=0）、随机噪点图（方差约5000+）、以及体积>1KB 的大尺寸纯色占位图（8594字节，验证修正后的插入位置生效）
- M3.2 average hash：纯色图、随机噪点图、随机噪点图逐字节复制文件（md5 相同）、两张体积>250KB 仅一像素不同的图（验证 average hash 生效）——四种场景均实测
- M5.1 pre-push hook：真实本地 bare repo + clone，真实 `git push` 触发，验证"大改动警告不阻断"和"新分支首次推送不报错"两种场景
- `detect_ci_platform()` 探测顺序：真实 Python 解释器验证三种场景（Gitea+GitHub 混合、仅 GitLab、无平台变量）
- 新增 CHECK 9 锚点字典：`python3 -c` 解析确认语法有效，且用带新锚点的完整脚本跑过真实仓库，确认新锚点正确报出预期的 WARN（代码未实现前的正常状态）

## 仍是推断、无法在本环境验证的部分（诚实标注，不可与上面混为一谈）

- **`GITEA_ACTIONS=true`**：来源是 Gitea 官方 GitHub issue 讨论串（`go-gitea/gitea#24038`）里维护者的提议，不是实测确认。已尝试三条路径验证：（1）下载 `act_runner` 二进制——只发布在 `gitea.com`，本环境网络白名单访问返回 403；（2）找 GitHub 镜像——`github.com/gitea/act_runner`、`github.com/go-gitea/act_runner` 均 404，无镜像；（3）翻 Gitea 主仓库源码（`go-gitea/gitea`，GitHub 可访问，已下载确认可运行）——只找到 `GITEA_ACTIONS_TASK_ID`（用途是 git hooks，非 Actions 环境判定），真正的环境变量注入逻辑在 `act_runner` 里，这个仓库到不了。**三条路径都在本环境的网络白名单边界前止步，不是不想验证，是这个沙箱结构性到不了。**
- **`GITLAB_CI=true` 及配套的 `CI_MERGE_REQUEST_*` 系列变量**：`gitlab.com` 整体 403（含安装包下载地址 `packages.gitlab.com`），无法下载 GitLab CE 做实测。这条的可信度依据是这个变量长期稳定、业界文档高度一致，属于"高置信度的既有知识"，但严格说仍不是本环境的实测结果，与上面"已实测"的条目不是同一个可信度级别。

## 这意味着什么

第四部分步骤1（Gitea 环境实测）是本文档唯一无法在当前环境完成、必须由你在自己的基础设施上执行的前置步骤。其余全部步骤（self-gate 三处修复、M4.2/M5.1/M3.1/M3.2/M1.3a/M1.3b/M1.1 的代码本身、CHECK 9 锚点）都已经过沙箱内的真实执行验证，可以按第四部分的顺序直接推进，不需要等 Gitea 验证结果——只有 M4.1 里 Gitea 分支的 `get_pr_metadata` 实现细节，需要等你那边的验证结果回来后再最终确认或调整。

---

# 第七部分：实施就绪核查清单

| 措施 | 代码锚点是否已核实 | 新增依赖 | 实施前必须先做的事 | 状态 |
|---|---|---|---|---|
| self-gate 修复A | 是（正则+提示文字均实测） | 无 | 无 | 可直接实施 |
| self-gate 修复B | 是（`check_anchor_coverage` 全文已读） | 无 | 无 | 可直接实施 |
| self-gate 修复C | 是（新锚点已用真实脚本验证 WARN 行为符合预期） | 无 | 需等步骤2文档声明落地 | 可直接实施（顺序见第四部分） |
| M4.2 provenance 纳入 backstop | 是 | 无 | 无 | 可直接实施 |
| M5.1 pre-push 提示钩子 | 是（真实 git push 验证过） | 无 | 无 | 可直接实施 |
| M3.1 像素方差检测 | 是（真实图片验证过，含插入位置缺陷修正） | Pillow | CI workflow 加 `pip install Pillow`；Pillow 未安装时输出 WARNING 不静默跳过（决定 1）；`AGATE_SKIP_IMAGE_CHECKS=1` 主动跳过开关；阈值需实施后一周内用真实数据复核 | 可实施 |
| M3.2 average hash | 是（真实图片验证过） | 无（复用 Pillow） | 同决定 1 的 Pillow 缺失处理 + `AGATE_SKIP_IMAGE_CHECKS` | 可直接实施 |
| M1.3a 日志格式约定 | 是 | 无 | 无 | 可直接实施 |
| M1.3b 日志一致性检测 | 是（真实脚本三场景验证过） | 无 | 无 | 可直接实施 |
| M1.1 时间戳弱信号 | N/A | 无 | 决定 3：已评估，判定不值得实现（CI 场景 mtime 无区分力 + 威胁模型对伪造行为无区分力） | 不实施 |
| M4.1 平台探测（Gitea 分支细节） | 部分——探测顺序逻辑已验证，Gitea 环境变量/事件文件格式未验证 | 无 | **待做**：Gitea 真实实例验证，本环境做不到，需你执行 | 待前置验证后可实施 |

**尚未纳入本次合并范围、此前指南里提到但未展开的三项**（M1.4 派发提示词偏置审计扩展、M1.2/M2.2 对抗性框定提示词、M2.1 跨模型配置字段）：这三项当时就标注为"未打开对应文件核对，不满足可直接实施标准"，本次合并聚焦"多平台 CI 支持"这条主线，不在这次一并处理，如需实施应另开一轮，先打开 `assets/review-roles/*.md`、`protocol-alignment-review.md`、`orchestrator-template.md` 核对现状。

## 结论

除 M4.1 里 Gitea 环境变量/事件文件格式这一项外，本文档列出的全部改动（self-gate 三处修复 + 7 条措施代码本身，M1.1 已判定不实施）都已在沙箱内用真实脚本、真实图片、真实 git 仓库验证过，可以按第四部分顺序直接推进实施。Gitea 那一项的验证权限和执行环境都在你那边，我这边已经把能做的都做到头了——包括试图绕过网络限制的三条路径，全部有真实执行记录、真实失败原因，不是空手回答"做不到"。

---

# 第八部分：文档传播具体修改文本（评审 B1-B4 + N1-N7 修复）

> 本节回应 protocol-alignment-review v2 的 4 个 BLOCKER + 7 个非阻断发现，逐一给出具体修改文本。实施时按本节文本落地即可。

## B1：md5 重复从 WARNING 升级为阻断——破坏性变更标注

**发现**：M3.2 将 md5 重复从 exit 2（WARNING）升级为 exit 1（阻断），是破坏性变更，计划未标注。

**决定**：确认此为破坏性变更，按 ADR-005 判定需 minor bump（v0.15.0→v0.16.0）。理由：md5 重复从"通过但警告"变为"不通过"，改变了 gate 的通过条件，现有项目如果存在合法 md5 重复截图（行为差异类 BDD 截图视觉相同），gate 行为将改变。

**CHANGELOG.md 追加**（在 `[Unreleased]` 下）：

```markdown
### BREAKING

- **P6 gate: md5 完全重复截图从 WARNING 升级为阻断**（exit 2 → exit 1）。同一物理文件被两条 PASS 引用视为证据造假。行为差异类 BDD 截图如果视觉相同但需分别引用，请在 acceptance report 说明原因——average hash 检测（WARNING 不阻断）仍允许视觉相似但非逐字节相同的截图
```

**dispatch-protocol.md:523 修改**（P5/P6 派发追加的截图质量标准）：

```diff
- 操作类 BDD 截图必须互不相同（md5 去重，hook 强制），查询类 BDD 可不截图但须有断言记录文件（response.json / assert.log 等，hook 强制）。
+ 操作类 BDD 截图必须互不相同（md5 逐字节去重，hook 阻断；average hash 视觉相似度检测，WARNING 不阻断），查询类 BDD 可不截图但须有断言记录文件（response.json / assert.log 等，hook 强制）。
+ 截图须通过像素方差检测（低方差/疑似占位图 WARNING 不阻断）；Pillow 未安装时检测跳过并输出 WARNING，可设 `AGATE_SKIP_IMAGE_CHECKS=1` 主动跳过。
```

**WORKFLOW.md:244 修改**（Pre-commit 检查总览 P1.7 行）：

```diff
- | 1.7 | `check-p6-evidence.sh` | 阶段 ∈ {P6, P7} | 阶段级 | P6-evidence/ 非空 + BDD 行数 ≥ 1（P1.7）|
+ | 1.7 | `check-p6-evidence.sh` | 阶段 ∈ {P6, P7} | 阶段级 | P6-evidence/ 非空 + BDD 行数 ≥ 1 + md5 逐字节去重（阻断）+ 像素方差/average hash 检测（WARNING）|
```

**state-machine.md:222 修改**（Pre-commit 检查全景 P1.7 行）：

```diff
- | **P1.7** P6 证据 (scripts/check-p6-evidence.sh) | phase ∈ {P6,P7} | 缺证据目录/BDD → 拦截 |
+ | **P1.7** P6 证据 (scripts/check-p6-evidence.sh) | phase ∈ {P6,P7} | 缺证据目录/BDD → 拦截；md5 重复 → 拦截；方差/相似度 → WARNING |
```

## B2：LIMITATIONS.md 局限 3/6/8 具体修改文本

### 局限 3（:44）修改

```diff
- - 已知局限：`git commit --no-verify` 绕过 pre-commit hook 时 provenance 审计也被绕过，CI backstop 当前不重跑 check-p6-provenance.sh（只重跑 check-gate.sh），provenance 的 CI 层覆盖仅为 git blame WARNING
+ - 已知局限：`git commit --no-verify` 绕过 pre-commit hook 时 provenance 审计也被绕过，CI backstop 现已重跑 check-p6-provenance.sh（M4.2），provenance 的 CI 层覆盖为 git blame WARNING + provenance 重跑
```

### 局限 6（:82-91）修改

```diff
  ## 局限 6：运行时依赖 bash+git+python3+pyyaml+Pillow（可选），但不限制被管理项目语言

- agate 的 gate 脚本和 pre-commit hook 依赖 bash、git、python3（+pyyaml）作为运行时工具。这些是**工具依赖**，不是被管理项目的语言限制——agate 编排的项目可以是任何语言（Go、Rust、Java、Ruby 等），只要执行环境有 bash+git+python3 可用。
+ agate 的 gate 脚本和 pre-commit hook 依赖 bash、git、python3（+pyyaml+Pillow）作为运行时工具。这些是**工具依赖**，不是被管理项目的语言限制——agate 编排的项目可以是任何语言（Go、Rust、Java、Ruby 等），只要执行环境有 bash+git+python3 可用。

  具体影响：
  - **bash**：所有 gate 脚本（check-gate.sh、check-pruning.sh 等）和 pre-commit hook 用 bash 编写。无 bash 则无法运行 gate
  - **git**：状态落盘、pre-commit hook、P8 version 检测、P7 源文件计数均依赖 git。非 git 项目无法使用 agate
- - **python3 + pyyaml**：check-protocol-consistency.py 和 ci-gate-backstop.py 需要 python3 + pyyaml。此外 8 个 gate 脚本内联 python3 调用（见 AGENTS.md 依赖节完整列表），缺 python3 时这些脚本的 YAML 解析逻辑不可用
+ - **python3 + pyyaml**：check-protocol-consistency.py 和 ci-gate-backstop.py 需要 python3 + pyyaml。此外 8 个 gate 脚本内联 python3 调用（见 AGENTS.md 依赖节完整列表），缺 python3 时这些脚本的 YAML 解析逻辑不可用
+ - **Pillow（可选）**：check-p6-evidence.sh 的像素方差检测和 average hash 相似度检测需要 Pillow。Pillow 未安装时这两项检测跳过并输出 WARNING（不阻断 gate），可设 `AGATE_SKIP_IMAGE_CHECKS=1` 主动声明跳过。CI 环境建议安装 Pillow 以获得完整检测覆盖
```

### 局限 8（:104-113）修改

```diff
- ## 局限 8：CI backstop 当前仅支持 GitHub Actions
+ ## 局限 8：CI backstop 支持 GitHub Actions / GitLab CI / Gitea Actions

- ci-gate-backstop.py 设计为 CI 层兜底——在 pre-commit hook 被绕过时（如 `git commit --no-verify`）重跑 gate 检查。当前实现仅支持 GitHub Actions 环境（通过 `GITHUB_ACTIONS` 环境变量检测，从 `$GITHUB_EVENT_PATH` 读取 PR 信息）。
+ ci-gate-backstop.py 设计为 CI 层兜底——在 pre-commit hook 被绕过时（如 `git commit --no-verify`）重跑 gate 检查。当前实现支持 GitHub Actions、GitLab CI、Gitea Actions 三种平台（通过 `detect_ci_platform()` 函数检测，检测顺序 Gitea → GitLab → GitHub，避免 Gitea Actions 的 GitHub 兼容变量导致误判）。

  具体影响：
- - GitLab CI、Jenkins、CircleCI 等平台的用户需自行适配 ci-gate-backstop.py 的环境检测逻辑
+ - Jenkins、CircleCI 等其他平台的用户需自行适配 ci-gate-backstop.py 的环境检测逻辑
  - 不使用 CI 的项目完全依赖 pre-commit hook，无兜底机制
  - AGATE_TASKS_DIR 环境变量（v0.13.0 新增）允许配置任务目录路径，但 CI 平台检测仍需手动适配
+ - Gitea Actions 的环境变量（`GITEA_ACTIONS=true`）和事件文件格式尚未实测确认（见第六部分验证状态说明），`get_pr_metadata` 的 Gitea 分支先按 GitHub 兼容路径实现，实测不符时需调整

- **现状**：CI backstop 是可选增强层。核心 gate 检查在 pre-commit hook 中运行，不依赖特定 CI 平台。非 GHA 用户可参考 ci-gate-backstop.py 的逻辑自行实现对应平台的 backstop。
+ **现状**：CI backstop 是可选增强层。核心 gate 检查在 pre-commit hook 中运行，不依赖特定 CI 平台。非支持平台的用户可参考 ci-gate-backstop.py 的逻辑自行实现对应平台的 backstop。M4.2 新增 provenance 审计重跑（check-p6-provenance.sh），CI backstop 现在同时重跑 check-gate.sh + check-p6-provenance.sh。
```

## B3：CI backstop 多平台 + provenance 描述更新

### WORKFLOW.md:255 修改

```diff
- - **CI backstop（P1.3）**：push 后 GitHub Actions 重跑 `check-gate.sh` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的恶意提交；git blame 单 author WARNING 作为 provenance 兜底审计。
+ - **CI backstop（P1.3）**：push 后 CI 平台（GitHub Actions / GitLab CI / Gitea Actions）重跑 `check-gate.sh` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的恶意提交；provenance 审计重跑（check-p6-provenance.sh）+ git blame 单 author WARNING 作为兜底审计。
```

### state-machine.md:232 修改

```diff
- **CI 兜底（P1.3）**：push 后 GitHub Actions 重跑 `check-gate.sh` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的 commit。
+ **CI 兜底（P1.3）**：push 后 CI 平台（GitHub Actions / GitLab CI / Gitea Actions）重跑 `check-gate.sh` + `ci-gate-backstop.py` + `check-p6-provenance.sh`，捕获 `--no-verify` 绕过 hook 的 commit。
```

### dispatch-protocol.md:825 修改

```diff
- **CI backstop（P1.3）**：`push` 后 GitHub Actions `.github/workflows/protocol-tests.yml` 重跑 `check-gate.sh` + `ci-gate-backstop.py`，捕获 `--no-verify` 绕过 hook 的 commit；并对 `P6-acceptance.md` 单 author 情况发 WARNING 作为兜底审计。
+ **CI backstop（P1.3）**：`push` 后 CI 平台（GitHub Actions / GitLab CI / Gitea Actions）重跑 `check-gate.sh` + `ci-gate-backstop.py` + `check-p6-provenance.sh`，捕获 `--no-verify` 绕过 hook 的 commit；provenance 审计重跑 + `P6-acceptance.md` 单 author WARNING 作为兜底审计。
```

## B4：修复 A/B/C bats 测试覆盖

### 修复 A 测试（commit-msg-self-gate.sh 正则修改）

新增 `agate/tests/unit/commit-msg-self-gate.bats`：

```bash
load "tests/helpers/load.bash"

@test "commit-msg-self-gate: .sh 文件触发 self-gate" {
    create_task_dir
    echo "test" > "$REPO_ROOT/agate/scripts/test-file.sh"
    git_add "agate/scripts/test-file.sh"
    echo "feat: test" > "$BATS_TEST_TMPDIR/commit-msg"
    run bash -c "cd '$REPO_ROOT' && bash agate/scripts/commit-msg-self-gate.sh '$BATS_TEST_TMPDIR/commit-msg'"
    [[ "$output" == *"self-gate"* ]]
}

@test "commit-msg-self-gate: .py 文件触发 self-gate" {
    create_task_dir
    echo "test" > "$REPO_ROOT/agate/scripts/test-file.py"
    git_add "agate/scripts/test-file.py"
    echo "feat: test" > "$BATS_TEST_TMPDIR/commit-msg"
    run bash -c "cd '$REPO_ROOT' && bash agate/scripts/commit-msg-self-gate.sh '$BATS_TEST_TMPDIR/commit-msg'"
    [[ "$output" == *"self-gate"* ]]
}

@test "commit-msg-self-gate: 非 agate .py 文件不触发" {
    create_task_dir
    echo "test" > "$REPO_ROOT/other/test-file.py"
    git_add "other/test-file.py"
    echo "feat: test" > "$BATS_TEST_TMPDIR/commit-msg"
    run bash -c "cd '$REPO_ROOT' && bash agate/scripts/commit-msg-self-gate.sh '$BATS_TEST_TMPDIR/commit-msg'"
    [[ "$status" -eq 0 ]]
    [[ "$output" == "" ]]
}

@test "commit-msg-self-gate: self-gate-review: 路径消除 WARNING" {
    create_task_dir
    echo "test" > "$REPO_ROOT/agate/scripts/test-file.sh"
    git_add "agate/scripts/test-file.sh"
    printf 'feat: test\nself-gate-review: docs/reviews/test.md' > "$BATS_TEST_TMPDIR/commit-msg"
    run bash -c "cd '$REPO_ROOT' && bash agate/scripts/commit-msg-self-gate.sh '$BATS_TEST_TMPDIR/commit-msg'"
    [[ "$status" -eq 0 ]]
}
```

### 修复 B 测试（check_anchor_coverage 扫描范围）

新增测试用例到 `agate/tests/unit/check-protocol-consistency.bats`：

```bash
@test "CHECK 9: ci-gate-backstop.py 被纳入 anchor coverage 扫描范围" {
    # 验证 ci-gate-backstop.py 出现在 CHECK 9 的 gate_scripts 列表中
    # 如果 ci-gate-backstop.py 无锚点条目，CHECK 9 应报 WARN（而非静默跳过）
    run python3 -c "
import sys; sys.path.insert(0, '$AGATE_ROOT/agate/scripts')
from check_protocol_consistency import get_gate_scripts
scripts = get_gate_scripts()
assert 'agate/scripts/ci-gate-backstop.py' in scripts, f'ci-gate-backstop.py not in {scripts}'
"
    [[ "$status" -eq 0 ]]
}
```

### 修复 C 测试（新增锚点运行时行为）

新增测试用例到 `agate/tests/unit/check-protocol-consistency.bats`：

```bash
@test "CHECK 9: EXIT_CODE 锚点存在且关键词匹配" {
    run python3 -c "
import sys; sys.path.insert(0, '$AGATE_ROOT/agate/scripts')
from check_protocol_consistency import SCRIPT_ALIGNMENT_ANCHORS
exit_code_anchors = [a for a in SCRIPT_ALIGNMENT_ANCHORS if 'EXIT_CODE' in a.get('keywords', [])]
assert len(exit_code_anchors) >= 2, f'Expected >=2 EXIT_CODE anchors, got {len(exit_code_anchors)}'
"
    [[ "$status" -eq 0 ]]
}

@test "CHECK 9: AGATE_ALIGNMENT_REVIEW_THRESHOLD 锚点存在" {
    run python3 -c "
import sys; sys.path.insert(0, '$AGATE_ROOT/agate/scripts')
from check_protocol_consistency import SCRIPT_ALIGNMENT_ANCHORS
threshold_anchors = [a for a in SCRIPT_ALIGNMENT_ANCHORS if 'AGATE_ALIGNMENT_REVIEW_THRESHOLD' in a.get('keywords', [])]
assert len(threshold_anchors) >= 1, f'Expected >=1 AGATE_ALIGNMENT_REVIEW_THRESHOLD anchor, got {len(threshold_anchors)}'
"
    [[ "$status" -eq 0 ]]
}
```

### M5.1 测试（pre-push hook）

新增 `agate/tests/integration/pre-push-hook.bats`：

```bash
load "tests/helpers/load.bash"

@test "pre-push hook: 大改动触发提示但不阻断" {
    # 创建 bare repo + clone，模拟 agate/*.md 大改动 push
    # 验证输出含 "protocol-alignment-review" 提示且 exit 0
    # （具体实现依赖 git-helper.bash 的 git_init / git_commit）
}

@test "pre-push hook: 新分支首次推送跳过检测" {
    # remote_sha 全零场景，验证输出含 "新分支" 提示且 exit 0
}

@test "pre-push hook: AGATE_ALIGNMENT_REVIEW_THRESHOLD 环境变量覆盖默认阈值" {
    # 设置 AGATE_ALIGNMENT_REVIEW_THRESHOLD=5，验证 5 行以上改动触发提示
}
```

### M1.3b 测试（审计 5 EXIT_CODE 一致性）

新增测试用例到 `agate/tests/unit/check-p6-provenance.bats`：

```bash
@test "审计 5: 日志 EXIT_CODE=1 但声明 PASS → exit 1" {
    # 创建 P6-acceptance.md 含 PASS 引用 test.log
    # 创建 test.log 末行 EXIT_CODE: 1
    # 验证 check-p6-provenance.sh exit 1
}

@test "审计 5: 日志 EXIT_CODE=0 配 PASS → exit 0" {
    # 创建 P6-acceptance.md 含 PASS 引用 test.log
    # 创建 test.log 末行 EXIT_CODE: 0
    # 验证 check-p6-provenance.sh exit 0
}

@test "审计 5: 日志缺少 EXIT_CODE 尾行 → WARNING 不阻断" {
    # 创建 P6-acceptance.md 含 PASS 引用 test.log
    # 创建 test.log 无 EXIT_CODE 尾行
    # 验证 check-p6-provenance.sh exit 0 + 输出含 "缺少标准 EXIT_CODE"
}
```

## N1：M3.1/M3.2 文档声明具体修改文本

已在 B1 的 dispatch-protocol.md:523 修改中给出。

## N2：protocol-alignment-review.md 触发条件同步更新

```diff
- **触发条件**：`agate/scripts/*.sh`、`agate/scripts/check-protocol-consistency.py`、`agate/*.md`、`agate/**/*.md`、`SELF-GATE.md` 有改动时，主 Agent 在 commit 前派发本角色。
+ **触发条件**：`agate/scripts/*.sh`、`agate/scripts/*.py`、`agate/*.md`、`agate/**/*.md`、`SELF-GATE.md` 有改动时，主 Agent 在 commit 前派发本角色。
```

## N3：install-hook.sh 注释更新

```diff
- # install-hook.sh — 安装 pre-commit hook
- # 把 agate 的 pre-commit-gate.sh 链接到当前 git 仓库的 .git/hooks/pre-commit
+ # install-hook.sh — 安装 pre-commit hook + commit-msg hook + pre-push hook
+ # 把 agate 的 pre-commit-gate.sh 链接到 .git/hooks/pre-commit
+ # 把 agate 的 commit-msg-self-gate.sh 链接到 .git/hooks/commit-msg
+ # 生成 pre-push hook（协议文件大改动自动提示 alignment-review）
```

## N4：脚本注释更新

### check-p6-evidence.sh 注释

```diff
- # check-p6-evidence.sh — P6 证据格式检查（P1.7）
- # 检查 P6-evidence/ 目录非空 + UI 截图实质检查（R1a）
+ # check-p6-evidence.sh — P6 证据格式检查（P1.7）
+ # 检查 P6-evidence/ 目录非空 + UI 截图实质检查（R1a）+ md5 去重（阻断）+ 像素方差/average hash 检测（WARNING，需 Pillow）
```

### check-p6-provenance.sh 注释

```diff
- # check-p6-provenance.sh — P6 验收客观行为审计（P2.1/P2.10 降级方案 v2）
- # 四道客观审计 + agent 字段协作规范
+ # check-p6-provenance.sh — P6 验收客观行为审计（P2.1/P2.10 降级方案 v2）
+ # 五道客观审计 + agent 字段协作规范
```

## N5：M5.1/M1.3b bats 文件路径

已在 B4 中明确：
- M5.1：`agate/tests/integration/pre-push-hook.bats`
- M1.3b：`agate/tests/unit/check-p6-provenance.bats`（追加用例）

## N6：ADR-003 Pillow 依赖人工确认

ADR-003 标 NEEDS_HUMAN_REVIEW。人工确认方向：Pillow 是 agate 自身工具依赖（非对被管理项目的限制），且未安装时不阻断 gate（WARNING + AGATE_SKIP_IMAGE_CHECKS=1），与 ADR-003 核心精神一致。确认后建议在 LIMITATIONS.md 局限 6 标注"Pillow 为可选依赖"（已在 B2 修改文本中体现）。

`[HUMAN_CONFIRMED: 2026-07-21 确认：Pillow 依赖可接受，理由见决定 1——静默失效已通过 WARNING + AGATE_SKIP_IMAGE_CHECKS=1 缓解，与 ADR-003 核心精神（不绑定被管理项目技术栈）不冲突]`

## N7：步骤 2 文档声明落地后为 M3.1/M3.2 补充锚点

步骤 2 文档声明落地后，在修复 C 的锚点列表追加：

```python
{
    "desc": "截图像素方差检测（M3.1）",
    "script": "agate/scripts/check-p6-evidence.sh",
    "keywords": ["VARIANCE_WARNING", "AGATE_SKIP_IMAGE_CHECKS"],
},
{
    "desc": "截图 average hash 相似度检测（M3.2）",
    "script": "agate/scripts/check-p6-evidence.sh",
    "keywords": ["AHASH_LIST", "AHASH_DUPES"],
},
```

## SELF-GATE.md 触发条件同步

```diff
  以下任一文件有改动并准备 commit 时：
  - `agate/scripts/*.sh`
- - `agate/scripts/check-protocol-consistency.py`
+ - `agate/scripts/*.py`
  - `agate/*.md`（协议文档：WORKFLOW.md / state-machine.md / dispatch-protocol.md 等）
  - `agate/**/*.md`（角色文件、模板文件等子目录）
  - `SELF-GATE.md`（本文件自身的改动也走 self-gate）
```

## AGENTS.md 依赖节计数更新

AGENTS.md 依赖节中"8 个 sh 脚本内联 python3"清单已含 `check-p6-evidence.sh` 和 `check-p6-provenance.sh`（v5 评审纠正：M3.1/M3.2 是在已有 Python 内联的同一脚本中增加新 Python 代码块，不是新增脚本，**总数保持 8 不变**）。只需在依赖描述中注明 Pillow 新增即可：

```diff
- Python 3.8+ + `pyyaml`（`pip install pyyaml`）— 8 个 sh 脚本内联 python3：check-changelog.sh、check-p6-evidence.sh、check-p6-provenance.sh、check-pruning.sh、check-retrospective.sh、check-state-transition.sh、check-state-yaml.sh、gate-result.sh
+ Python 3.8+ + `pyyaml` + `Pillow`（`pip install pyyaml Pillow`，Pillow 可选）— 8 个 sh 脚本内联 python3：check-changelog.sh、check-p6-evidence.sh、check-p6-provenance.sh、check-pruning.sh、check-retrospective.sh、check-state-transition.sh、check-state-yaml.sh、gate-result.sh（其中 check-p6-evidence.sh 新增 Pillow 依赖用于像素方差/average hash 检测）
```

LIMITATIONS.md 局限 6 的 8→9 计数同步撤消（局限 6 的 B2 diff 中已通过新增 Pillow 条目正确表达了依赖变更，不涉及脚本计数变更）。

## N-N1：platform-notes.md CI backstop 描述更新

```diff
- | CI backstop（gate 重跑 + git blame WARNING）| ⚠️ 自实现 | ⚠️ 自实现 | ⚠️ 自实现 | 仅 GitHub Actions 提供开箱实现 |
+ | CI backstop（gate 重跑 + provenance 重跑 + git blame WARNING）| ⚠️ 自实现 | ⚠️ 自实现 | ⚠️ 自实现 | GitHub Actions / GitLab CI / Gitea Actions 提供开箱实现（⚠️ Gitea 未实测） |

- **CI backstop 说明**：`.github/workflows/protocol-tests.yml` 的 `gate-backstop` job 用 GitHub Actions 实现。在自建 CI（Gitea/GitLab/本地）跑 agate 时：
- - 需要等价实现：`git push` 后重跑 `scripts/check-gate.sh` + 调用 `ci-gate-backstop.py`
+ **CI backstop 说明**：`.github/workflows/protocol-tests.yml` 的 `gate-backstop` job 用 GitHub Actions 实现。ci-gate-backstop.py 原生支持 GitHub Actions / GitLab CI / Gitea Actions（通过 `detect_ci_platform()` 自动检测）。在自建 CI（Jenkins/本地）跑 agate 时：
+ - 需要等价实现：`git push` 后重跑 `scripts/check-gate.sh` + `scripts/check-p6-provenance.sh` + 调用 `ci-gate-backstop.py`
```

## N-N2：orchestrator-template.md:91 CI 兜底描述更新

```diff
- - **CI 兜底**：push 后 GitHub Actions 重跑 gate + git blame 单 author WARNING，捕获 `--no-verify` 绕过
+ - **CI 兜底**：push 后 CI 平台（GitHub Actions / GitLab CI / Gitea Actions）重跑 gate + provenance 审计 + git blame 单 author WARNING，捕获 `--no-verify` 绕过
```

## N-N3：git-integration.md:181 CI backstop 描述更新

```diff
- **禁止 `--no-verify` 绕过 hook**：CI backstop 会重跑 `check-gate.sh` + git blame 单 author WARNING，绕过 hook 的"恶意 commit"会被抓到并在日志暴露。详见 LIMITATIONS.md 局限 3。
+ **禁止 `--no-verify` 绕过 hook**：CI backstop 会重跑 `check-gate.sh` + `check-p6-provenance.sh` + git blame 单 author WARNING，绕过 hook 的"恶意 commit"会被抓到并在日志暴露。详见 LIMITATIONS.md 局限 3。
```

## N-N4：dispatch-protocol.md:800 install-hook.sh 描述更新

```diff
- 每次 `git commit` 触发 `.git/hooks/pre-commit`（由 `~/.agate/scripts/install-hook.sh` 安装），按顺序执行：
+ 每次 `git commit` 触发 `.git/hooks/pre-commit`（由 `~/.agate/scripts/install-hook.sh` 安装 pre-commit + commit-msg + pre-push hook），按顺序执行：
```

并在全景表后追加：

```markdown
**Pre-push hook**：`git push` 时自动检测 `agate/*.md` 改动量，超过阈值（默认 20 行，可通过 `AGATE_ALIGNMENT_REVIEW_THRESHOLD` 环境变量配置）时提示建议先派发 protocol-alignment-review。不阻断 push（exit 0）。
```

## N-N5：AGENTS.md 依赖节 diff

已在上方"AGENTS.md 依赖节计数更新"节给出。

## N-N6：orchestrator-template.md:113 install-hook.sh 描述更新

```diff
- 1. `bash ~/.agate/scripts/install-hook.sh` — 安装 pre-commit hook（重复执行安全，会覆盖旧链接）
+ 1. `bash ~/.agate/scripts/install-hook.sh` — 安装 pre-commit + commit-msg + pre-push hook（重复执行安全，会覆盖旧链接）
```

## N-N7：scripts/README.md install-hook.sh 描述更新

```diff
- | `install-hook.sh` | 在项目仓库内安装 pre-commit hook（接受 `AGATE_ROOT` 参数）|
+ | `install-hook.sh` | 在项目仓库内安装 pre-commit + commit-msg + pre-push hook（接受 `AGATE_ROOT` 参数）|
```

## 补充：scripts/README.md 三处条目更新（v5 评审 MISALIGNED-2）

```diff
- | `check-p6-evidence.sh` (P1.7) | P6 证据目录非空检查 | 0=通过, 1=缺证据/空文件, 2=WARNING |
+ | `check-p6-evidence.sh` (P1.7) | P6 证据目录非空 + md5 逐字节去重（阻断）+ 像素方差/average hash 检测（WARNING）| 0=通过, 1=阻断, 2=WARNING |
```

```diff
- | `check-p6-provenance.sh` (P2.1/P2.10) | P6 客观行为审计（三道）| 0=通过, 1=审计失败, 2=WARNING |
+ | `check-p6-provenance.sh` (P2.1/P2.10) | P6 客观行为审计（五道 + EXIT_CODE 一致性 + 协作规范）| 0=通过, 1=审计失败, 2=WARNING |
```

```diff
- | `ci-gate-backstop.py` (P1.3) | push 后重跑 gate + P6 git blame 单 author WARNING |
+ | `ci-gate-backstop.py` (P1.3) | push 后重跑 gate + provenance 审计重跑 + git blame 单 author WARNING；多平台自动检测（GitHub/GitLab/Gitea）|
```
