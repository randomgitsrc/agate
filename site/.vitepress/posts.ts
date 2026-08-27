// site/.vitepress/posts.ts
// 博客文章清单的单一权威源：扫描 site/blog/ 下的文章，提取 frontmatter。
// 供 config.mts（sidebar）与 blog.data.ts（主页/索引页）共用。
// 从此发博客只需新增文章文件，索引/侧边栏/主页全部自动生成，无需手工登记。
import { readdirSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import path from 'node:path'

export interface Post {
  title: string
  url: string
  date: string // YYYY-MM-DD
}

// 构建永远从 site/ 目录发起（本地与 CI 均如此，见 deploy-pages.yml 的 working-directory: site）。
// 用 import.meta.url 定位本文件所在目录更稳（不依赖 cwd），失败再回退 cwd。
let blogRoot: string
try {
  blogRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../blog')
} catch {
  blogRoot = path.resolve(process.cwd(), 'blog')
}

// 极简 frontmatter 解析（够用即可：title/date/description 均为单行标量）
function parseFrontmatter(src: string): Record<string, string> {
  const m = src.match(/^---\r?\n([\s\S]*?)\r?\n---/)
  if (!m) return {}
  const out: Record<string, string> = {}
  for (const line of m[1].split(/\r?\n/)) {
    const kv = line.match(/^([A-Za-z_][\w-]*):\s*(.*)$/)
    if (kv) out[kv[1]] = kv[2].trim().replace(/^["']|["']$/g, '')
  }
  return out
}

function walkPosts(dir: string, acc: Post[]): void {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      walkPosts(full, acc)
    } else if (entry.isFile() && entry.name.endsWith('.md') && !entry.name.startsWith('index')) {
      const fm = parseFrontmatter(readFileSync(full, 'utf8'))
      if (!fm.date) continue // 无 date 的不是文章页
      const rel = path.relative(blogRoot, full).replace(/\\/g, '/').replace(/\.md$/, '')
      acc.push({ title: fm.title || rel, url: `/blog/${rel}`, date: fm.date })
    }
  }
}

// 全部文章，最新在前（date 字典序即时间序；同日期内 post-XX 号大的在前）
export function getAllPosts(): Post[] {
  const posts: Post[] = []
  walkPosts(blogRoot, posts)
  return posts.sort((a, b) =>
    a.date === b.date ? (a.url < b.url ? 1 : -1) : a.date < b.date ? 1 : -1,
  )
}
