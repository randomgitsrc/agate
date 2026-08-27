// VitePress data loader（en）—— 把 posts.ts 的文章清单暴露给英文 markdown 页面。
// 构建时运行一次，发博客无需手工改主页/索引。
import { getAllPosts, type Post } from './posts'

export default {
  load: (): Post[] => getAllPosts('en'),
}
