// VitePress data loader —— 构建时扫描博客目录，导出最新的几篇文章。
// 主页用它在每次 build 时自动拉最新文章，发博客无需再手工改主页。
// 用法见 site/index.md（`import { data } from './.vitepress/blog.data.js'`）。
import { createContentLoader } from 'vitepress'

export default createContentLoader('blog/**/*.md', {
  // 只要 frontmatter，不需要正文内容，构建产物更小
  includeSrc: false,
  render: false,
  transform(raw) {
    // frontmatter 的 date 会被 js-yaml 解析成 Date 对象，String(date) 得到本地化
    // 字符串（带星期名），字典序不按时间序——必须统一格式化成 YYYY-MM-DD 再排序
    const fmtDate = (v: unknown): string =>
      v instanceof Date ? v.toISOString().slice(0, 10) : String(v ?? '').slice(0, 10)
    // 只留真正的文章页（有 date 的；blog/index.md 没有 date 会被过滤掉）
    const posts = raw
      .filter((page) => page.frontmatter && page.frontmatter.date)
      .map((page) => ({
        title: String(page.frontmatter.title || page.url),
        url: page.url,
        date: fmtDate(page.frontmatter.date),
      }))
    // YYYY-MM-DD 字典序即时间序；倒序 = 最新在前，取最新 3 篇
    return posts.sort((a, b) => (a.date < b.date ? 1 : -1)).slice(0, 3)
  },
})
