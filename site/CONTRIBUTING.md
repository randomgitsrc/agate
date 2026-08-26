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

## base 路径与自定义域名

- 当前 `base: '/agateon/'`（项目站 `https://randomgitsrc.github.io/agateon/`）。
- 上自定义域名（agateon.com）时：把 `site/.vitepress/config.mts` 的 `base` 改成 `'/'`，并同步改 `head` 里的 `og:image` 路径；DNS 配 4 条 A 记录 + CNAME；Repo → Settings → Pages → Custom domain。
