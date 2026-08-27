// site/scripts/crosspost-devto.mjs
// dev.to 自动化发布脚本 —— 把 site/blog/ 的一篇文章同步发布/更新到 dev.to。
// 用法：
//   DEV_TO_API_KEY=xxx node crosspost-devto.mjs 20260827/post-02-agateon-intro          # 发布
//   node crosspost-devto.mjs post-02-agateon-intro --dry-run                            # 只生成 body 不发布
//   node crosspost-devto.mjs 20260827/post-02-agateon-intro --update 4498883            # 更新已有文章
// 自动处理：frontmatter 替换、SVG→raw PNG URL、站内链接→dev.to 链接、浏览器 UA（防 403）、
// 发布后验证。详细机理见 site/guides/devto-crosspost-playbook.md。
import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { execSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { http } from './http.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const SITE_ROOT = path.resolve(HERE, '..')
const TAGS = ['ai', 'llm', 'opensource', 'discuss']
const UA =
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'

function log(...a) { console.log('[crosspost]', ...a) }

// ---- 参数 ----
const args = process.argv.slice(2)
const dryRun = args.includes('--dry-run')
const updateIdx = args.indexOf('--update')
const updateId = updateIdx >= 0 ? args[updateIdx + 1] : null
const postArg = args.find((a) => !a.startsWith('--'))

if (!postArg) {
  log('用法: node crosspost-devto.mjs <post路径> [--dry-run] [--update <dev.to id>]')
  log('  例: node crosspost-devto.mjs 20260827/post-02-agateon-intro')
  process.exit(1)
}

// ---- 仓库信息 ----
const remote = execSync('git -C ' + SITE_ROOT + ' remote get-url origin', { encoding: 'utf8' }).trim()
const m = remote.match(/github\.com[:/]([^/]+)\/([^/]+?)(\.git)?$/)
if (!m) { log('无法从 git remote 推断 owner/repo:', remote); process.exit(1) }
const [owner, repo] = [m[1], m[2]]
const siteBase = process.env.SITE_BASE_URL || `https://${owner}.github.io/${repo}`

// ---- 定位文章文件 ----
function findPost(arg) {
  const candidates = [
    path.join(SITE_ROOT, 'blog', arg + '.md'),
    path.join(SITE_ROOT, 'blog', arg, 'index.md'),
  ]
  for (const c of candidates) if (existsSync(c)) return c
  // 按 slug 名全库找（如 post-02-agateon-intro）
  function walk(dir, out = []) {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      const f = path.join(dir, e.name)
      if (e.isDirectory()) walk(f, out)
      else if (e.isFile() && e.name.endsWith('.md') && e.name === arg + '.md') out.push(f)
    }
    return out
  }
  const hits = walk(path.join(SITE_ROOT, 'blog'))
  if (hits.length === 1) return hits[0]
  if (hits.length === 0) { log('找不到文章:', arg); process.exit(1) }
  log('多个匹配，取最新的:', hits[hits.length - 1])
  return hits[hits.length - 1]
}

const postFile = findPost(postArg)
const rel = path.relative(path.join(SITE_ROOT, 'blog'), postFile).replace(/\.md$/, '').replace(/\\/g, '/')
const postUrl = `${siteBase}/blog/${rel}`
log('文章:', postFile)
log('站点 URL:', postUrl)

// ---- 读文章 + 拆 frontmatter ----
const src = readFileSync(postFile, 'utf8')
const parts = src.split('---', 3)
if (parts.length !== 3) { log('frontmatter 格式不对'); process.exit(1) }
const fm = Object.fromEntries(
  parts[1].split('\n').map((l) => l.match(/^([A-Za-z_][\w-]*):\s*(.*)$/)).filter(Boolean).map((kv) => [kv[1], kv[2].trim().replace(/^["']|["']$/g, '')]),
)
let body = parts[2].replace(/^\n/, '')

// ---- 转换：SVG 图 → raw PNG URL；站内链接 → dev.to 链接 ----
body = body.replace(/\.\/images\/([\w.-]+)\.svg/g, (_, n) =>
  `https://raw.githubusercontent.com/${owner}/${repo}/main/site/blog/${rel.split('/').slice(0, -1).join('/')}/images/${n}.png`,
)

// 拿本账号已发布的 dev.to 文章，建 canonical_url -> dev.to url 映射
let devtoMap = {}
if (!dryRun || updateId) {
  try {
    const r = http('GET', `https://dev.to/api/articles?username=${owner}&per_page=50`, { headers: { 'api-key': process.env.DEV_TO_API_KEY || '' } })
    if (r.status === 200) {
      const arts = JSON.parse(r.text)
      for (const a of arts) if (a.canonical_url) devtoMap[a.canonical_url] = a.url
    }
  } catch (e) { log('获取已发布文章失败（忽略，站内链接回退站点 URL）:', e.message) }
}
body = body.replace(/\]\(\/blog\/([^)]+)\)/g, (whole, p) => {
  const siteLink = `${siteBase}/blog/${p.replace(/\.md$/, '')}`
  return `](${devtoMap[siteLink] || siteLink})`
})

// ---- dev.to frontmatter ----
const devtoFm = [
  '---',
  `title: "${fm.title.replace(/"/g, '\\"')}"`,
  'published: true',
  `description: "${(fm.description || '').replace(/"/g, '\\"')}"`,
  `tags: [${TAGS.join(', ')}]`,
  `canonical_url: ${postUrl}`,
  '---',
  '',
].join('\n')

// ---- 发布/更新 ----
async function main() {
  if (dryRun) {
    log('---- DRY RUN，body_markdown 如下 ----')
    console.log(devtoFm + body)
    return
  }
  const key = process.env.DEV_TO_API_KEY
  if (!key) { log('缺少 DEV_TO_API_KEY（取用须 bash -lc）'); process.exit(1) }
  const payload = JSON.stringify({ article: {
    title: fm.title, published: true, body_markdown: devtoFm + body,
    tags: TAGS, description: fm.description || '', canonical_url: postUrl,
  } })
  const url = updateId ? `https://dev.to/api/articles/${updateId}` : 'https://dev.to/api/articles'
  const res = http(updateId ? 'PATCH' : 'POST', url, {
    headers: { 'api-key': key, 'User-Agent': UA },
    body: payload,
  })
  if (res.status < 200 || res.status >= 300) { log(`HTTP ${res.status}:`, res.text.slice(0, 500)); process.exit(1) }
  const d = JSON.parse(res.text)
  log(updateId ? `已更新文章 ${d.id}` : `已发布文章 ${d.id}`)
  log('URL:', d.url)
  // 验证
  const u = http('HEAD', d.url)
  log('文章公开可达:', u.status === 200 ? '✓' : `✗ HTTP ${u.status}`)
  const imgUrls = [...body.matchAll(/https:\/\/raw\.githubusercontent\.com\/[^)]+\.png/g)].map((x) => x[0])
  for (const img of imgUrls) {
    const proxied = `https://media2.dev.to/dynamic/image/width=800,fit=scale-down/${encodeURIComponent(img)}`
    const ir = http('HEAD', proxied)
    log(`图片代理 ${path.basename(new URL(img).pathname)}:`, ir.status === 200 ? '✓' : `✗ HTTP ${ir.status}`)
  }
  // 记住 id，方便后续 --update
  log(`下次更新: node ${path.basename(process.argv[1])} ${postArg} --update ${d.id}`)
}
main().catch((e) => { log('出错:', e.message); process.exit(1) })
