# dev.to Cross-post 攻略

> 把 `site/blog/` 的文章同步发布到 dev.to 的操作手册。
> 前置：先读 `site/BLOG-STANDARDS.md`（质量）与 `site/CONTRIBUTING.md`（流程）；
> 本文只讲 dev.to API 的**实测细节**，所有坑都是 2026-08-27 发 post-02 时踩过并验证的。

## 1. 前置条件

- dev.to API key：Settings → Extensions → API Keys。
  本机存在 `~/.bashrc` 的 `DEV_TO_API_KEY`（非交互 shell 不读 bashrc，取用时必须 `bash -lc`）。
- 文章已合入 `main`（cross-post 在合并部署之后做）。
- 配图 PNG **不必提前手工渲染**：脚本会自动检查，缺失就从 SVG 用 Chrome 渲染并 commit+push 到仓库（否则 raw URL 404）。
  站点本身用 SVG（<4KB 内联成 data URI 渲染），PNG 仅为 dev.to 的 raw URL 准备。

## 2. 关键结论（先记住这三个，都是实测）

| # | 结论 | 说明 |
|---|------|------|
| 1 | **`POST /api/image_uploads` 已从新版 dev.to 移除（404）** | 别再传图片了。改为直接引用 GitHub raw 的 PNG URL，dev.to 会走 `media2.dev.to` 图片代理自动缓存 |
| 2 | **POST 必须带浏览器 User-Agent** | dev.to WAF 拦截非浏览器 UA：urllib（`Python-urllib/3.x`）POST 一律 403 空体；curl 带 `Mozilla/5.0 ...` 即通（HTTP 201）。GET 不受影响 |
| 3 | **`POST /api/articles` 一次建好（published: true）** | payload 为 `{"article": {...}}`，`api-key` 走 header，`Content-Type: application/json` |

## 3. 一条命令发布（主流程，全自动）

```bash
bash -lc 'cd ~/oclab/agateon/site && node scripts/crosspost-devto.mjs post-02-agateon-intro'
```

脚本自动完成全部正文改造 + 发布 + 验证：

1. 定位文章（`post-02-agateon-intro` 按 slug 全库找，也可给 `20260827/post-02-agateon-intro`）
2. 去 VitePress frontmatter → 换 dev.to frontmatter（`title`/`published`/`description`/`tags`/`canonical_url`）
3. `./images/xxx.svg` → 仓库内 PNG 的 raw URL（dev.to 不支持 SVG；raw URL 稳定且 dev.to 自动代理，返回 `media2.dev.to/dynamic/image/...`）
4. **PNG 兜底**：缺失的 PNG 自动用 `google-chrome --headless=new --screenshot` 从 SVG 渲染，并 `git add/commit/push` 到当前分支（raw URL 即刻可达）
5. 文内站内链接 `/blog/...` → 已发布文章的 dev.to URL（跨平台读者不用跳走）；没发过的回退站点完整 URL
6. **mermaid 块保留为 ` ```mermaid ` 代码块**——dev.to 不渲染 mermaid，会显示为代码（惯例）
7. tag 固定 `ai, llm, opensource, discuss`；`canonical_url` 指向站点文章（站点是母稿）
8. 发布后验证：文章 URL 200 + 每张图经 dev.to 代理可达

常用变体：

```bash
bash -lc 'cd ~/oclab/agateon/site && node scripts/crosspost-devto.mjs post-02 --dry-run'   # 只预览 body，不发布
bash -lc 'cd ~/oclab/agateon/site && node scripts/crosspost-devto.mjs post-02 --update 4498883'  # 更新已发布文章（PATCH）
bash -lc 'cd ~/oclab/agateon/site && node scripts/crosspost-devto.mjs post-02 --no-push'   # 渲染 PNG 但不同步提交
```

> 成功响应 `201`，返回 `type_of: article`、`id`、`url`。**不要把 `published` 设 false 再补发**——一次到位，避免中间态。

## 4. 手动兜底（脚本不可用时）

- **正文改造**按第 3 节 1-7 步手工做，图用 raw PNG URL：
  `https://raw.githubusercontent.com/randomgitsrc/agateon/main/site/blog/YYYYMMDD/images/xxx.png`
- **发布**用 curl（带浏览器 UA，否则 403）：

```bash
bash -lc '
curl -sS -X POST https://dev.to/api/articles \
  -H "api-key: $DEV_TO_API_KEY" -H "Content-Type: application/json" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36" \
  -d "$(cat /tmp/post.json)"
'
```

- **更新**：`curl -X PATCH https://dev.to/api/articles/{id}`，payload 同 POST。

## 5. 发布后验证（脚本已自动做；手动核对用）

- [ ] 文章 URL 公开可达（`curl -s -o /dev/null -w "%{http_code}" <url>` → 200）
- [ ] 文中每张图经 dev.to 代理后可达：
  `curl -s -o /dev/null -w "%{http_code}" "https://media2.dev.to/dynamic/image/width=800,fit=scale-down/<raw-url>"` → 200
- [ ] tag / canonical_url / 标题 与站点文章一致

## 6. 踩坑记录（别重踩）

- **`POST /api/image_uploads` 404**：旧版 API 有，新版 dev.to 路由里已删（Forem 源码 `config/routes/api.rb` 无此路由）。别再找替代上传端点，直接 raw URL 最省事。
- **POST 403 空体**：不是 key 没权限（`GET /api/users/me` 200），是 WAF 按 UA 拦。urllib 默认 UA 必挂，curl/浏览器 UA 必过。
- **Node fetch 不走代理**：本机有 `HTTPS_PROXY=127.0.0.1:10808`，undici 的全局 fetch 不读代理 env，会 `UND_ERR_CONNECT_TIMEOUT`。所有脚本统一走 `site/scripts/http.mjs`（curl 封装，自动继承代理）——**新脚本别用裸 fetch 打外网**。
- **英文 PNG 别忘**：站点用 SVG 内联不依赖 PNG，但 dev.to 用 raw PNG URL。脚本已自动渲染兜底；手工发帖时若 PNG 缺失，dev.to 图片会 404。
- **一天别 cross-post 两条自己的内容**（dev.to/HN 对自我推广有量感，见 CONTRIBUTING C 节）。
