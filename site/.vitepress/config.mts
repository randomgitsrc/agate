import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import { getAllPosts } from './posts'

// site/ 是产品 Web 层，在协议 gate 治理之外（见根 AGENTS.md「仓库四块」）。
// 唯一硬校验 = `npm run build` 通过（site-check.yml + deploy-pages.yml）。
//
// base：项目站 = '/agateon/'；上自定义域名（agateon.com）时改成 '/'，并同步改
// head 里的 og:image 路径。
export default withMermaid(
  defineConfig({
    base: '/agateon/',
    lang: 'en-US',
    title: 'Agateon',
    description: 'Verify AI agents the way a build system verifies a compiler.',
    cleanUrls: true,
    // 内部维护文档（CONTRIBUTING / BLOG-STANDARDS / guides），不发布为公开页面
    srcExclude: ['CONTRIBUTING.md', 'BLOG-STANDARDS.md', 'guides/**'],
    head: [
      ['meta', { property: 'og:title', content: 'Agateon' }],
      [
        'meta',
        {
          property: 'og:description',
          content:
            'An open-source orchestration protocol that gates every phase of an agent\'s work with objective, machine-checkable signals.',
        },
      ],
      ['meta', { property: 'og:image', content: '/agateon/social-preview.png' }],
    ],
    themeConfig: {
      logo: { light: '/logo-mark.svg', dark: '/logo-mark-dark-bg.svg' },
      nav: [
        { text: 'Home', link: '/' },
        { text: 'Blog', link: '/blog/' },
        { text: 'GitHub', link: 'https://github.com/randomgitsrc/agateon' },
      ],
      sidebar: {
        '/blog/': [
          {
            text: 'Blog',
            // 文章清单自动生成（见 .vitepress/posts.ts），发博客无需手工登记 sidebar
            items: getAllPosts().map((p) => ({ text: p.title, link: p.url })),
          },
        ],
      },
      socialLinks: [
        { icon: 'github', link: 'https://github.com/randomgitsrc/agateon' },
      ],
      footer: {
        message: 'Verify AI agents the way a build system verifies a compiler.',
        copyright: 'Agateon',
      },
      search: { provider: 'local' },
    },
  }),
)
