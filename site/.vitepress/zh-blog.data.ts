// VitePress data loader（zh）—— 把 posts.ts 的中文文章清单暴露给中文 markdown 页面。
// 中文文章由 i18n-translate.mjs 自动生成；索引/主页自动取数，无需手工登记。
import { getAllPosts, type Post } from './posts'

export default {
  load: (): Post[] => getAllPosts('zh'),
}
