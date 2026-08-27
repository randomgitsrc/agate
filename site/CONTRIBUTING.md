# site/ 维护流程

`site/` 是 Agateon 的产品 Web 层（VitePress 站点：首页 + 博客），**在协议 gate 治理之外**。
本文档只讲 site 的维护；协议开发见根 `AGENTS.md` 与 `agate/AGENTS.md`。

## 核心原则

- **改它不触发 SELF-GATE**，也**不走 Agateon 的 P0-P8 编排**（除了站点工程的机制交叉大改）。
- **唯一硬校验 = `npm run build` 通过**。构建失败：PR 上 `site-build` 检查变红（informational），合并到 main 后 `deploy-pages.yml` 构建不过就不部署（线上保持上一版）。
- **main 分支受保护，不能直推**——"轻量"≠"绕过 PR"，而是"不跑全量 CI、不被无关测试卡死"。site 改动被 `detect-docs-only` 判定为 docs-only，required 的 pytest/shellcheck 秒级 fast-pass。

## 改动分级

| 层 | 改什么 | 流程 |
|----|--------|------|
| L0 内容小改 | 文案 / typo / 链接 / 日期 / 博客文章 | 直接改 → commit（`docs:` 前缀）→ git-to-pr → git-to-main |
| L1 内容新增 | 新博客文章 / 新页面 | 写稿 → 本地 `npm run dev` 预览 → commit → PR → 轻 review（图片路径 / mermaid / frontmatter / 链接）→ 合并 |
| L2 站点工程 | config.mts / 主题 / 插件 / 依赖 / 构建 | 声明性→同 L0；行为逻辑 / 机制交叉（i18n、构建管线、新插件）→ 按 ADR-005 走 Agateon（至少裁剪版） |

## 品牌资产同步

- `docs/brand/` 是**唯一权威源**；`site/public/` 是构建快照（`.gitignore` 忽略，不入库）。
- `npm run dev` / `npm run build` 都会先跑 `node scripts/sync-brand.mjs` 自动同步，**无需手动拷贝**。
- 改品牌只在 `docs/brand/` 改，提交时 site 会自动带上新品牌（deploy-pages 会因 `docs/brand/**` 改动而重新部署）。

## 本地预览与构建

```bash
cd site
npm ci           # 首次；之后改依赖后也用这个（基于 package-lock.json）
npm run dev      # 本地预览 http://localhost:5173/agateon/
npm run build    # 产物在 site/.vitepress/dist/，CI 与部署都以此为准
```

## 发布路径

1. 改内容 / 站点工程，本地 `npm run build` 确认绿。
2. commit（`docs:` 前缀；L2 工程改动用 `feat(site):` / `fix(site):`）。
3. `/home/kity/bin/git-to-pr` 建分支 + PR；`/home/kity/bin/git-to-main` 等 CI + 合并。
4. 合并后 `deploy-pages.yml` 自动构建部署到 GitHub Pages。
5. 博客文章合并后再手动 cross-post：dev.to（上传 PNG 换链接）+ HN（普通链接，不加 Show HN）+ 微信群。

## 博客工作流（agent 照此执行）

> 用户不自己动手，博客的加/改/发布由 agent 代做。以下每一步都要做全。
> **质量标准与配图规范见 `site/BLOG-STANDARDS.md`；发布前必须过独立评审（第 7 节 gate），pass 才上线。**

### A. 新增博客文章

1. **写稿**：创建 `site/blog/YYYYMMDD/post-XX-slug.md`（`YYYYMMDD` = 发布日期，`XX` = 当日序号）。
   图片放同目录 `images/`：SVG 源 + PNG 版（PNG 供 dev.to 用，尺寸≥1200px 宽更稳）。
   正文图片用相对路径 `./images/xxx.svg`；mermaid 图直接用 ` ```mermaid ` 代码块。
2. **frontmatter**（文件顶部，必须齐全，否则博客列表和 sidebar 缺标题/日期）：

   ```yaml
   ---
   title: "文章标题"
   date: YYYY-MM-DD
   description: 一句话摘要（供搜索/og）
   tags:
     - 标签1
   ---
   ```

3. **登记两处**（漏了就不显示在站点上）：
   - `site/blog/index.md`：列表里加一条 `- [标题](/blog/YYYYMMDD/post-XX-slug) — YYYY-MM-DD`
   - `site/.vitepress/config.mts`：`sidebar` 的 Blog 段 `items` 加一条 `{ text: 标题, link: '/blog/YYYYMMDD/post-XX-slug' }`
4. **本地验证（必做）**：`cd site && npm run build`。重点检查：
   - 新页面出现在 `site/.vitepress/dist/blog/YYYYMMDD/post-XX-slug.html`
   - mermaid 块没报语法错（build 有 warning 也要看）
   - 图片路径解析（dist 里能找到图片：>4KB 的是独立文件，<4KB 内联成 data URI，都正常）
5. **提交**：commit（`docs:` 前缀）→ `/home/kity/bin/git-to-pr` → `/home/kity/bin/git-to-main` → 合并后自动部署。
6. **cross-post（合并后）**：
   - dev.to：用 API 发布（`POST /api/articles`）。**详细实测步骤、已失效的端点、UA 坑、验证清单见 [`guides/devto-crosspost-playbook.md`](guides/devto-crosspost-playbook.md)**——一句话版：图用 GitHub raw PNG URL（新版 dev.to 已移除 `POST /api/image_uploads`）、POST 必须带浏览器 User-Agent（否则 403）、tag 用 `ai, llm, opensource, discuss`。需要 dev.to API key（Settings → Extensions → API Keys；本机存在 `~/.bashrc` 的 `DEV_TO_API_KEY`，取用须 `bash -lc`）。
   - HN：普通链接提交（不加 Show HN），title 用文章标题，url 用 dev.to 链接。
   - 微信群：短文案（见 2026-08 的版本 A/B/C 模板思路，痛点开场 + 求讨论）。

### B. 修改博客文章

1. 改 `site/blog/YYYYMMDD/post-XX-slug.md`（改图则更新 `images/`，改标题则同步 frontmatter `title`）。
2. `cd site && npm run build` 验证。
3. commit（`docs:` 前缀）→ git-to-pr → git-to-main → 自动部署。
4. 若该篇已发 dev.to：同步更新 dev.to 文章（`PATCH /api/articles/{id}`，图片用新 PNG URL）。

### C. 注意事项

- **改标题/日期**必须同步 frontmatter + `site/blog/index.md` + `config.mts` sidebar 三处，三处不一致会出怪问题。
- **删文章** = 删 md + 从 index 和 sidebar 移除 + 删 images 里无引用的图（dev.to 上如已发布需手动删/撤）。
- **发布节奏**：一天别 cross-post 两条自己的内容（dev.to/HN 对自我推广有量感），间隔开。

## base 路径与自定义域名

- 当前 `base: '/agateon/'`（项目站 `https://randomgitsrc.github.io/agateon/`）。
- 上自定义域名（agateon.com）时：把 `site/.vitepress/config.mts` 的 `base` 改成 `'/'`，并同步改 `head` 里的 `og:image` 路径；DNS 配 4 条 A 记录 + CNAME；Repo → Settings → Pages → Custom domain。
