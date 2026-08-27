# site/ 文档索引（接站点/博客任务先看这里）

> `site/` 的全部开发者文档都在这一个目录 `guides/` 里，**站点源码只放运行时内容**。
> 全部文件都被 `site/.vitepress/config.mts` 的 `srcExclude: ['guides/**']` 排除，**不发布到站点**，仅供开发者。

## 必读（接任何博客/站点任务先读这两份）

| 文档 | 管什么 |
|------|--------|
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | 机械流程：发文章/改文章/删文章/cross-post 的每一步命令（含 i18n 中文版生成） |
| [`BLOG-STANDARDS.md`](BLOG-STANDARDS.md) | 质量标准：配图规范、事实硬项、**独立评审 gate（发布前必须过，pass 才上线）** |

## 操作手册（按需）

| 文档 | 什么时候读 |
|------|-----------|
| [`devto-crosspost-playbook.md`](devto-crosspost-playbook.md) | 要把某篇文章发布/更新到 dev.to 时 |
| `i18n-translate-playbook.md`（暂未单列） | 生成中文版文章/配图时——当前流程已并入 `CONTRIBUTING.md` 第 4 步，细节在 `../scripts/i18n-translate.mjs` 头部注释 |

## 新文档该放哪（规则）

- **站点开发者文档一律放 `guides/`**：操作手册命名 `xxx-playbook.md`；章程就放这里并在此表登记。
- 仓库根的 `AGENTS.md` 是**全仓库**指引（协议/脚本/CI/发版），与 site 无关，别往 site 里塞。
- 站点运行时**读者可见**的内容（新文章/新页面）→ `site/blog/` 与 `site/index.md`，不属于本目录。
