# site/ 文档索引（接站点/博客任务先看这里）

> `site/` 的开发者文档分两层，规矩：
> - **根级 = 必读章程**：`BLOG-STANDARDS.md` + `CONTRIBUTING.md`——接任何博客/站点任务**先读这两份**。
> - **`guides/` = 按需操作手册**：一类操作一份 playbook，做具体操作时读对应那份。
>
> 根级两份与 `guides/**` 全部被 `site/.vitepress/config.mts` 的 `srcExclude` 排除，
> **不发布到站点**，仅供开发者。命名约定：操作类手册统一放 `guides/`，文件名 `-playbook.md` 后缀。

## 根级（必读，先读）

| 文档 | 管什么 |
|------|--------|
| [`BLOG-STANDARDS.md`](../BLOG-STANDARDS.md) | 质量标准：配图规范、事实硬项、**独立评审 gate（发布前必须过，pass 才上线）** |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) | 机械流程：发文章/改文章/删文章/cross-post 的每一步命令（含 i18n 中文版生成） |

## 操作手册（按需）

| 文档 | 什么时候读 |
|------|-----------|
| [`devto-crosspost-playbook.md`](devto-crosspost-playbook.md) | 要把某篇文章发布/更新到 dev.to 时 |
| `i18n-translate-playbook.md`（暂未单列） | 生成中文版文章/配图时——当前流程已并入 `CONTRIBUTING.md` 第 4 步，细节在 `../scripts/i18n-translate.mjs` 头部注释 |

## 新文档该放哪（规则）

- 新操作类手册（如"换 logo 全流程""发 HN"）→ `site/guides/xxx-playbook.md`，并在此表加一行。
- 新的质量/流程章程 → `site/` 根，紧挨现有两份。
- 站点运行时**读者可见**的内容（新文章/新页面）→ `site/blog/` 与 `site/index.md`，不属于本目录。
