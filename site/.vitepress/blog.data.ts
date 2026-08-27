// VitePress data loader —— 把 posts.ts 的文章清单暴露给 markdown 页面（主页/索引页）。
// 构建时运行一次，发博客无需手工改主页/索引。
// 用法：`import { data } from './.vitepress/blog.data.ts'`
import { getAllPosts, type Post } from './posts'

export default {
  load: (): Post[] => getAllPosts(),
}
