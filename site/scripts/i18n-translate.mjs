// site/scripts/i18n-translate.mjs
// 中文化自动化管道 —— 配图翻译 + 索引生成 + 首页字段翻译。
// **正文不机翻**（2026-09-05 起）：zh 文章正文一律人工重写（活人感，见 BLOG-STANDARDS §9）——
// 脚本对正文只做存在性检查与告警，绝不生成、绝不覆盖人工稿。
// 引擎：Google Gemini 免费档（GOOGLE_API_KEY_FREE / GOOGLE_API_KEY_TIRE，须 bash -lc 取用）。
// 限额保护：限速 15 RPM（调用间隔 4s）、硬上限 I18N_MAX_CALLS（默认 40，远低于免费档 500 RPD）、
// 429 退避重试、403 报错停下。翻译只处理纯文本，代码块/URL/图片路径/mermaid 全部用占位符保护。
//
// 用法：
//   bash -lc 'node site/scripts/i18n-translate.mjs'               # 只处理过期/缺失的中文版
//   bash -lc 'node site/scripts/i18n-translate.mjs --all'         # 强制全部重新翻译
//   bash -lc 'node site/scripts/i18n-translate.mjs --dry-run'     # 只列计划，不调 API
//   bash -lc 'I18N_MAX_CALLS=20 node site/scripts/i18n-translate.mjs post-02'  # 只翻某篇 + 限 20 次
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync, readdirSync, copyFileSync } from 'node:fs'
import { execSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { http } from './http.mjs'

const HERE = path.dirname(fileURLToPath(import.meta.url))
const SITE_ROOT = path.resolve(HERE, '..')
const BLOG_EN = path.join(SITE_ROOT, 'blog')
const ZH_ROOT = path.join(SITE_ROOT, 'zh')

const MODEL = process.env.I18N_MODEL || 'gemini-3.1-flash-lite'
const KEY = process.env.GOOGLE_API_KEY_FREE || process.env.GOOGLE_API_KEY_TIRE || ''
const MAX_CALLS = parseInt(process.env.I18N_MAX_CALLS || '40', 10)
const MIN_INTERVAL_MS = parseInt(process.env.I18N_INTERVAL_MS || '4000', 10) // 15 RPM 安全值
const args = process.argv.slice(2)
const forceAll = args.includes('--all')
const dryRun = args.includes('--dry-run')
const onlyPost = args.find((a) => !a.startsWith('--')) || null

let calls = 0
let lastCallAt = 0

function log(...a) { console.log('[i18n]', ...a) }

// ---- Gemini 翻译（限速 + 配额护栏）----
async function throttle() {
  if (calls >= MAX_CALLS) throw new Error(`已达调用上限 I18N_MAX_CALLS=${MAX_CALLS}（保护免费档配额），请提高限制或分批跑`)
  const wait = lastCallAt + MIN_INTERVAL_MS - Date.now()
  if (wait > 0) await new Promise((r) => setTimeout(r, wait))
  calls += 1
  lastCallAt = Date.now()
  if (calls % 5 === 0) log(`已调用 ${calls} 次（免费档 500 RPD，剩余约 ${500 - calls}）`)
}

async function gemini(prompt, maxTokens = 8192) {
  if (!KEY) throw new Error('缺少 GOOGLE_API_KEY_FREE / GOOGLE_API_KEY_TIRE（取用须 bash -lc）')
  await throttle()
  if (dryRun) return '__DRYRUN__'
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${KEY}`
  const body = { contents: [{ parts: [{ text: prompt }] }], generationConfig: { maxOutputTokens: maxTokens, temperature: 0.3 } }
  for (let attempt = 0; ; attempt++) {
    let res
    try {
      res = http('POST', url, { body: JSON.stringify(body) })
    } catch (e) {
      throw new Error(`Gemini 请求失败: ${e.message}`)
    }
    if (res.status === 429 && attempt < 2) {
      log('429 限流，退避 20s 重试...')
      await new Promise((r) => setTimeout(r, 20000))
      continue
    }
    if (res.status !== 200) {
      if (res.status === 403 || res.status === 429) throw new Error(`Gemini 配额/限流(HTTP ${res.status})：${res.text.slice(0, 300)}`)
      throw new Error(`Gemini HTTP ${res.status}: ${res.text.slice(0, 300)}`)
    }
    const d = JSON.parse(res.text)
    const txt = d?.candidates?.[0]?.content?.parts?.[0]?.text?.trim()
    if (!txt) throw new Error('Gemini 返回为空')
    return txt
  }
}

const TRANS_PROMPT = `你是专业的技术文档翻译。把下面英文翻译成简体中文。
规则：
- 所有 @@CODE数字@@ 占位符必须原样保留，一个都不能丢。
- 保留全部 Markdown 语法（# 标题、**加粗**、- 列表、| 表格、> 引用、\`\`\` 代码块）。
- 专业术语/产品名/命令/标识符保留英文更自然就不用翻（gate、phase、orchestrator、subagent、Agateon、test suite 等）。
- 工程师对工程师的语气，简洁准确，用中文全角标点。
- 只输出译文，不要任何解释。`

// ---- 占位符保护：代码块 / 内联代码 / 链接URL / 图片路径 / 裸URL ----
function protect(text) {
  const map = []
  // 链接/图片 URL：只把括号内的 URL 换成占位符，保留 ]( @@ ) 骨架，防止 LLM 因括号失衡补出多余的 "]"
  const re = /```[\s\S]*?```|`[^`\n]+`|\]\(([^)]+)\)|https?:\/\/[^\s)]+/g
  return {
    text: text.replace(re, (m, url) => {
      const i = map.length
      if (url !== undefined) { map.push(url); return `](@@CODE${i}@@)` }
      map.push(m); return `@@CODE${i}@@`
    }),
    map,
  }
}
function restore(text, map) {
  return text.replace(/@@CODE(\d+)@@/g, (_, i) => map[+i])
}

// ---- frontmatter 解析/重组 ----
// 注意：按"独立 --- 行"切，不用 split('---',3)——markdown 表格分隔行 `|---|` 也含 --- 子串，
// 字面 split 会把正文从表格处截断（2026-08-28 post-03 踩坑：两张表触发）。
function splitFrontmatter(src) {
  const m = src.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/)
  if (!m) throw new Error('frontmatter 缺失')
  return { fm: m[1], body: src.slice(m[0].length).replace(/^\n/, '') }
}
// ---- 判断是否需要更新 ----
function newerThan(target, source) {
  if (!existsSync(target)) return false
  if (forceAll) return false
  return statSync(target).mtimeMs >= statSync(source).mtimeMs
}

// ---- 单篇文章：只检查人工重写稿，不机翻正文 ----
// 2026-09-05 起：zh 正文由作者人工重写（活人感管线，BLOG-STANDARDS §9）。
// 脚本对正文的三种情形：缺失 → 告警跳过；比 EN 旧 → 告警不覆盖；最新 → 跳过。
// 配图翻译不受影响（按 EN images/ 目录发现，与 zh 正文解耦）。
async function translatePost(enFile, rel) {
  const zhFile = path.join(ZH_ROOT, 'blog', rel)
  if (!existsSync(zhFile)) {
    log(`警告: zh/blog/${rel} 缺失——正文需人工重写（BLOG-STANDARDS §9），本次跳过（配图照常处理）`)
    return
  }
  if (newerThan(zhFile, enFile)) { log(`跳过（zh 已最新）: zh/${rel}`); return }
  log(`警告: EN 比 zh 新——zh/blog/${rel} 需人工核对重写稿，本次不覆盖（配图照常处理）`)
}

// ---- 配图中文化：SVG <text> 翻译 + 渲染中文 PNG ----
// 注意：en 图片在日期级目录共享（blog/YYYYMMDD/images/），中文版同样输出到 zh/blog/YYYYMMDD/images/。
async function translateImages(enDir, zhImgDir, label) {
  const svgs = existsSync(enDir) ? readdirSync(enDir).filter((f) => f.endsWith('.svg')) : []
  for (const f of svgs) {
    const srcSvg = path.join(enDir, f)
    const zhSvg = path.join(zhImgDir, f)
    if (newerThan(zhSvg, srcSvg)) { log(`跳过（已最新）: 图片 ${label}/${f}`); continue }
    log(`翻译配图: ${label}/${f}`)
    if (dryRun) { log(`  [dry-run] 将生成中文 SVG + PNG ${label}/${f}`); continue }
    const svg = readFileSync(srcSvg, 'utf8')
    const decode = (s) => s.replace(/&#8212;/g, '—').replace(/&#39;/g, "'").replace(/&amp;/g, '&').replace(/&quot;/g, '"').trim()
    // 收集所有 <text> 内容（按出现顺序）
    const rawTexts = []
    svg.replace(/<text\b[^>]*>([\s\S]*?)<\/text>/g, (m, content) => { rawTexts.push(content); return m })
    const cleanTexts = rawTexts.map(decode)
    const uniq = [...new Set(cleanTexts)].filter(Boolean)
    // 一次性批量翻译去重后的标签，建 原文→译文 字典
    const dict = {}
    if (uniq.length) {
      const r = await gemini(`${TRANS_PROMPT}\n\n把下面这些 UI 短标签翻译成简体中文，每行一个，直接输出对应译文（行数严格一致，纯符号如「?」原样保留）：\n${uniq.map((s, i) => `${i}: ${s}`).join('\n')}`)
      if (dryRun) return
      const lines = r.split('\n').filter((l) => l.trim()).map((l) => l.replace(/^\d+\s*[:：]?\s*/, '').trim())
      uniq.forEach((u, i) => { dict[u] = lines[i] ?? u })
    }
    // 重建 SVG：按原文查字典替换内容 + 切中文字体
    let idx = -1
    const zhSvgContent = svg.replace(/<text\b[^>]*>([\s\S]*?)<\/text>/g, (m, content) => {
      idx += 1
      const zh = dict[cleanTexts[idx]]
      if (!zh) return m
      const entitySafe = zh.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      return m.replace(content, entitySafe).replace(/font-family="[^"]*"/, 'font-family="Noto Sans SC, serif"')
    })
    mkdirSync(zhImgDir, { recursive: true })
    writeFileSync(zhSvg, zhSvgContent)
    // 渲染中文 PNG（同尺寸）
    const dim = zhSvgContent.match(/width="(\d+)" height="(\d+)"/)
    const w = dim ? dim[1] : 900
    const h = dim ? dim[2] : 520
    const png = zhSvg.replace(/\.svg$/, '.png')
    try {
      execSync(
        `google-chrome --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 --screenshot="${png}" --window-size=${w},${h} "file://${zhSvg}"`,
        { stdio: 'ignore' },
      )
      log(`  已生成 zh 图: ${label}/${f} + .png`)
    } catch (e) {
      log(`  Chrome 渲染失败: ${e.message}`)
    }
  }
}

// ---- 首页 ----
async function translateHome() {
  const en = path.join(SITE_ROOT, 'index.md')
  const zh = path.join(ZH_ROOT, 'index.md')
  if (newerThan(zh, en)) { log('跳过（已最新）: zh/index.md'); return }
  log('翻译首页 → zh/index.md')
  if (dryRun) { log('  [dry-run] 将调用 API 生成 zh/index.md'); return }
  const src = readFileSync(en, 'utf8')
  const { fm, body } = splitFrontmatter(src)

  // 1) frontmatter：逐行翻译显示字段（text/tagline/title/details）的值；其余字段原样保留
  const tasks = []
  const fmLines = fm.split('\n').map((line) => {
    const m = line.match(/^(\s*)(text|tagline|title|details):\s+(.+)$/)
    if (m && m[3].trim() && !/^https?:/.test(m[3].trim())) {
      tasks.push({ val: m[3].trim() })
      return `${m[1]}${m[2]}: @@FIELD${tasks.length - 1}@@`
    }
    return line
  })
  let fmZh = fmLines.join('\n')
  if (tasks.length) {
    const r = await gemini(`${TRANS_PROMPT}\n\n把下面这些首页文案（hero/特性）翻译成简体中文，每行一个直接给译文（行数严格一致）：\n${tasks.map((t, i) => `${i}: ${t.val}`).join('\n')}`)
    const lines = r.split('\n').filter((l) => l.trim()).map((l) => l.replace(/^\d+\s*[:：]?\s*/, '').trim())
    fmZh = fmZh.replace(/@@FIELD(\d+)@@/g, (m, idx) => lines[+idx] ?? tasks[+idx].val)
  }
  fmZh = fmZh.replace(/link: \/blog\//g, 'link: /zh/blog/') // 中文首页「读博客」按钮指到中文博客

  // 2) body：确定性装配。script 前的正文翻译；script/ul/末尾链接用固定中文结构
  const scriptZh = `<script setup>\nimport { data as posts } from '../.vitepress/zh-blog.data.ts'\nimport { withBase } from 'vitepress'\n\n// 最新 3 篇（中文文章清单自动生成，见 .vitepress/posts.ts）\nconst latestPosts = posts.slice(0, 3)\n</script>`
  const ulBlock = (body.match(/<ul class="latest-posts">[\s\S]*?<\/ul>/) || [''])[0]
  const preScript = body.slice(0, body.indexOf('<script setup>')).trim()
  const p = protect(preScript)
  const headZh = restore((await gemini(`${TRANS_PROMPT}\n\n${p.text}`)).trim(), p.map)
  const bodyZh = `${headZh}\n\n${scriptZh}\n\n${ulBlock}\n\n[阅读全部文章 →](/zh/blog/)\n`
  mkdirSync(ZH_ROOT, { recursive: true })
  writeFileSync(zh, `---\n${fmZh}\n---\n\n${bodyZh}\n`)
  log('  已写 zh/index.md')
}

// ---- 博客索引页（模板，非翻译）----
async function writeZhBlogIndex() {
  const zh = path.join(ZH_ROOT, 'blog', 'index.md')
  const intro = '构建 Agateon 的工程笔记与复盘。'
  const content = `---
title: 博客
description: ${intro}
---

# 博客

${intro}

<script setup>
import { data as posts } from '../../.vitepress/zh-blog.data.ts'
import { withBase } from 'vitepress'
</script>

<ul class="post-list">
  <li v-for="post in posts" :key="post.url">
    <a :href="withBase(post.url)">{{ post.title }}</a>
    <span class="post-date">— {{ post.date }}</span>
  </li>
</ul>
`
  mkdirSync(path.dirname(zh), { recursive: true })
  writeFileSync(zh, content)
  log('已写 zh/blog/index.md（自动索引）')
}

// ---- 主流程 ----
async function main() {
  log(`翻译引擎: ${MODEL} | 调用上限 ${MAX_CALLS} | 间隔 ${MIN_INTERVAL_MS}ms | dry-run=${dryRun} force=${forceAll}`)
  if (!KEY) { log('警告: 未找到 GOOGLE_API_KEY（须 bash -lc 运行）'); if (!dryRun) process.exit(1) }
  // 收集 en 文章
  const posts = []
  ;(function walk(dir, rel = '') {
    for (const e of readdirSync(dir, { withFileTypes: true })) {
      const f = path.join(dir, e.name)
      if (e.isDirectory()) walk(f, rel ? `${rel}/${e.name}` : e.name)
      else if (e.isFile() && e.name.endsWith('.md') && !e.name.startsWith('index')) posts.push({ file: f, rel: rel ? `${rel}/${e.name}` : e.name })
    }
  })(BLOG_EN, '')
  const targets = onlyPost ? posts.filter((p) => p.rel.includes(onlyPost)) : posts
  if (!targets.length) { log('没有要处理的文章（onlyPost 未命中）'); return }
  log(`文章 ${targets.length} 篇`)
  const seenDates = new Set()
  for (const p of targets) {
    await translatePost(p.file, p.rel)
    const dateRel = path.dirname(p.rel) // 如 20260826
    if (seenDates.has(dateRel)) continue
    seenDates.add(dateRel)
    await translateImages(path.join(path.dirname(p.file), 'images'), path.join(ZH_ROOT, 'blog', dateRel, 'images'), dateRel)
  }
  await translateHome()
  await writeZhBlogIndex()
  log(`完成。共调用 API ${calls} 次（剩余约 ${500 - calls} / 500 RPD）`)
}
main().catch((e) => { console.error('[i18n] 出错:', e.message); process.exit(1) })
