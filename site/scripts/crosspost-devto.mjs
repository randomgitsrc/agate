// site/scripts/crosspost-devto.mjs
// dev.to 自动化发布脚本 —— 把 site/blog/ 的一篇文章同步发布/更新到 dev.to。
// 用法：
//   DEV_TO_API_KEY=xxx node crosspost-devto.mjs 20260827/post-02-agateon-intro          # 发布
//   node crosspost-devto.mjs post-02-agateon-intro --dry-run                            # 只生成 body 不发布
//   node crosspost-devto.mjs 20260827/post-02-agateon-intro --update 4498883            # 更新已有文章
//   node crosspost-devto.mjs post-02 --no-push                                          # 渲染 PNG 但不同步提交
// 自动处理：frontmatter 替换、SVG→raw PNG URL、缺失 PNG 自动从 SVG 渲染（Chrome）+ 提交推送、
// 站内链接→dev.to 链接、浏览器 UA（防 403）、发布后验证。
// 详细机理见 site/guides/devto-crosspost-playbook.md。
import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { execSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { http } from './http.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const SITE_ROOT = path.resolve(HERE, '..')
const REPO_ROOT = path.resolve(SITE_ROOT, '..') // git 仓库根（site/ 上一级）
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
const siteBase = process.env.SITE_BASE_URL || `https://agateon.com`

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
const dateDir = rel.split('/').slice(0, -1).join('/') // 如 20260827（图片在日期级目录共享）
const imagesDir = path.join(SITE_ROOT, 'blog', dateDir, 'images')
const postUrl = `${siteBase}/blog/${rel}`
log('文章:', postFile)
log('站点 URL:', postUrl)

// ---- 读文章 + 拆 frontmatter ----
// 注意：按"独立 --- 行"切，不用 split('---',3)——markdown 表格分隔行 `|---|` 也含 --- 子串，
// 字面 split 会把正文从表格处截断（2026-08-28 post-03 踩坑，与 i18n-translate.mjs 同源）。
const src = readFileSync(postFile, 'utf8')
const fmMatch = src.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/)
if (!fmMatch) { log('frontmatter 格式不对'); process.exit(1) }
const fm = Object.fromEntries(
  fmMatch[1].split('\n').map((l) => l.match(/^([A-Za-z_][\w-]*):\s*(.*)$/)).filter(Boolean).map((kv) => [kv[1], kv[2].trim().replace(/^["']|["']$/g, '')]),
)
let body = src.slice(fmMatch[0].length).replace(/^\n/, '')

// ---- 转换：SVG 图 → raw PNG URL（dev.to 用 PNG，SVG 只在站点内联）；站内链接 → dev.to 链接 ----
const svgNames = []
body = body.replace(/\.\/images\/([\w.-]+)\.svg/g, (_, n) => {
  svgNames.push(n)
  return `https://raw.githubusercontent.com/${owner}/${repo}/main/site/blog/${dateDir}/images/${n}.png`
})

// 缺失的英文 PNG 用 Chrome 从 SVG 渲染（站点用 SVG 内联，PNG 仅为 dev.to raw URL 准备）
function renderMissingPngs(names) {
  const rendered = []
  for (const n of names) {
    const svg = path.join(imagesDir, `${n}.svg`)
    const png = path.join(imagesDir, `${n}.png`)
    if (existsSync(png)) continue
    if (!existsSync(svg)) { log(`警告: 找不到 ${n}.svg，无法渲染 PNG`); continue }
    const dim = readFileSync(svg, 'utf8').match(/width="(\d+)" height="(\d+)"/)
    const w = dim ? dim[1] : 900
    const h = dim ? dim[2] : 520
    try {
      execSync(
        `google-chrome --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --screenshot="${png}" --window-size=${w},${h} "file://${svg}"`,
        { stdio: 'ignore' },
      )
      log(`已渲染缺失 PNG: ${dateDir}/images/${n}.png`)
      rendered.push(png)
    } catch (e) {
      log(`渲染 PNG 失败（${n}.svg）: ${e.message.slice(0, 120)}`)
    }
  }
  return rendered
}

// 把新渲染的 PNG 提交并推送（否则 raw.githubusercontent 的 main 分支 URL 会 404）
function commitPngs(pngs) {
  if (!pngs.length) return
  if (args.includes('--no-push')) { log('--no-push：已渲染但未提交（raw URL 可能 404）'); return }
  const relPngs = pngs.map((p) => path.relative(REPO_ROOT, p).replace(/\\/g, '/'))
  try {
    execSync(`git -C ${REPO_ROOT} add ${relPngs.map((p) => `"${p}"`).join(' ')}`, { stdio: 'inherit' })
    execSync(`git -C ${REPO_ROOT} commit -m "docs(site): 自动渲染 ${dateDir} 英文配图 PNG（dev.to 用）"`, { stdio: 'inherit' })
    execSync(`git -C ${REPO_ROOT} push origin HEAD`, { stdio: 'inherit' })
    log(`已提交并推送 ${pngs.length} 个 PNG → raw URL 现已可达`)
  } catch (e) {
    log('提交/推送 PNG 失败（dev.to 可能抓不到图）:', e.message.slice(0, 300))
  }
}

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
    const missing = svgNames.filter((n) => !existsSync(path.join(imagesDir, `${n}.png`)))
    if (missing.length) log('注意: 以下 PNG 缺失，发布时会自动从 SVG 渲染并提交推送:', missing.join(', '))
    log('---- DRY RUN，body_markdown 如下 ----')
    console.log(devtoFm + body)
    return
  }
  // 发布前确保 PNG 存在且已入库（dev.to 引 raw URL）
  commitPngs(renderMissingPngs(svgNames))
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
