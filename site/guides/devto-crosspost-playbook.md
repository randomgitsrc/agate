# dev.to Cross-post 攻略

> 把 `site/blog/` 的文章同步发布到 dev.to 的操作手册。
> 前置：先读 `site/BLOG-STANDARDS.md`（质量）与 `site/CONTRIBUTING.md`（流程）；
> 本文只讲 dev.to API 的**实测细节**，所有坑都是 2026-08-27 发 post-02 时踩过并验证的。

## 1. 前置条件

- dev.to API key：Settings → Extensions → API Keys。
  本机存在 `~/.bashrc` 的 `DEV_TO_API_KEY`（非交互 shell 不读 bashrc，取用时必须 `bash -lc`）。
- 文章已合入 `main`（cross-post 在合并部署之后做）。
- 配图 PNG 已随文章 commit 到仓库（`site/blog/YYYYMMDD/images/*.png`）。

## 2. 关键结论（先记住这三个，都是实测）

| # | 结论 | 说明 |
|---|------|------|
| 1 | **`POST /api/image_uploads` 已从新版 dev.to 移除（404）** | 别再传图片了。改为直接引用 GitHub raw 的 PNG URL，dev.to 会走 `media2.dev.to` 图片代理自动缓存 |
| 2 | **POST 必须带浏览器 User-Agent** | dev.to WAF 拦截非浏览器 UA：urllib（`Python-urllib/3.x`）POST 一律 403 空体；curl 带 `Mozilla/5.0 ...` 即通（HTTP 201）。GET 不受影响 |
| 3 | **`POST /api/articles` 一次建好（published: true）** | payload 为 `{"article": {...}}`，`api-key` 走 header，`Content-Type: application/json` |

## 3. 正文改造（站点母稿 → dev.to body_markdown）

1. 去 VitePress 的 frontmatter，换成 dev.to 自己的 frontmatter（`title` / `published` / `description` / `tags` / `canonical_url`）。
2. `./images/xxx.svg` → 仓库内 PNG 的 raw URL：
   `https://raw.githubusercontent.com/randomgitsrc/agateon/main/site/blog/YYYYMMDD/images/xxx.png`
   （dev.to 不支持 SVG；raw URL 稳定且 dev.to 自动代理，返回的链接形如 `media2.dev.to/dynamic/image/...`）
3. 文内**站内链接**（如 `/blog/...`）→ 换成 dev.to 文章 URL（跨平台读者不用跳走），或站点完整 URL。
4. **mermaid 块保留为 ` ```mermaid ` 代码块**——dev.to 不渲染 mermaid，会显示为代码（post-01 同款处理，已是惯例）。
5. tag 固定用 `ai, llm, opensource, discuss`。
6. `canonical_url` 指向站点文章（`https://randomgitsrc.github.io/agateon/blog/YYYYMMDD/post-XX-slug`）——站点是母稿。

## 4. 发布

```bash
bash -lc '
python3 - <<"PY"
import json, urllib.request, os
body = open("/tmp/post.md").read()   # 改造好的 body_markdown
payload = {"article": {
    "title": "...",
    "published": True,
    "body_markdown": body,
    "tags": ["ai", "llm", "opensource", "discuss"],
    "canonical_url": "https://randomgitsrc.github.io/agateon/blog/YYYYMMDD/post-XX-slug",
}}
req = urllib.request.Request("https://dev.to/api/articles",
    data=json.dumps(payload).encode(),
    headers={"api-key": os.environ["DEV_TO_API_KEY"],
             "Content-Type": "application/json",
             "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"},
    method="POST")
import urllib.error
try:
    d = json.load(urllib.request.urlopen(req))
    print("OK", d.get("id"), d.get("url"))
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:500])
PY
'
```

> 成功响应 `201`，返回 `type_of: article`、`id`、`url`。**不要把 `published` 设 false 再补发**——
> 一次到位，避免中间态。

## 5. 发布后验证（必做）

- [ ] 文章 URL 公开可达（`curl -s -o /dev/null -w "%{http_code}" <url>` → 200）
- [ ] 文中每张图经 dev.to 代理后可达：
  `curl -s -o /dev/null -w "%{http_code}" "https://media2.dev.to/dynamic/image/width=800,fit=scale-down/<raw-url>"` → 200
- [ ] tag / canonical_url / 标题 与站点文章一致

## 6. 修改已发布的文章

`PATCH https://dev.to/api/articles/{id}`（id = 发布时返回的 id），payload 同 `POST`，
改完 body_markdown 即可；图片 URL 变了就换 raw URL。改完重复第 5 节验证。

## 7. 踩坑记录（别重踩）

- **`POST /api/image_uploads` 404**：旧版 API 有，新版 dev.to 路由里已删（Forem 源码 `config/routes/api.rb` 无此路由）。
  别再找替代上传端点，直接 raw URL 最省事。
- **POST 403 空体**：不是 key 没权限（`GET /api/users/me` 200），是 WAF 按 UA 拦。urllib 默认 UA 必挂，curl/浏览器 UA 必过。
- **一天别 cross-post 两条自己的内容**（dev.to/HN 对自我推广有量感，见 CONTRIBUTING C 节）。
