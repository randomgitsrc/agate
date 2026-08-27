---
layout: home

hero:
  name: Agateon
  text: 像构建系统验证编译器一样验证 AI agents
  tagline: 一个开源的编排协议，通过 AI agents 运行软件工作，并利用客观、可机器检查的信号对每个 phase 进行 gate。
  actions:
    - theme: brand
      text: 快速开始
      link: https://github.com/randomgitsrc/agateon
    - theme: alt
      text: 阅读博客
      link: /zh/blog/

features:
  - icon: 🛡️
    title: 客观的 gates
    details: 八个 phases —— 需求、设计、测试优先、实现、验证、验收、一致性、发布 —— 在状态机推进之前，每一项都必须通过一个可机器检查的 gate（测试退出代码、git log、BDD 计数）。
  - icon: 📝
    title: 可在崩溃后恢复的状态
    details: 所有进度都保存在版本控制的 Markdown 中。终止的会话可以从中断处恢复，并且每一步都可以通过 git 历史进行审计。
  - icon: 🧩
    title: 设计上分离的角色
    details: 一个 orchestrator 负责规划和调度；独立的 subagents 负责执行；gates 负责评估。执行工作的 agent 永远不会对自己完成的工作进行签收。
---

## 快速开始

从全新的 checkout 安装并运行 Agateon：

```bash
curl -sSL https://raw.githubusercontent.com/randomgitsrc/agateon/main/install.sh | bash
```

无需运行时，无需守护进程。该协议由一组 Markdown 卡片和 gate 脚本组成，与你的工作代码一同存储在版本控制系统中。

## 博客最新动态

<script setup>
import { data as posts } from '../.vitepress/zh-blog.data.ts'
import { withBase } from 'vitepress'

// 最新 3 篇（中文文章清单自动生成，见 .vitepress/posts.ts）
const latestPosts = posts.slice(0, 3)
</script>

<ul class="latest-posts">
  <li v-for="post in latestPosts" :key="post.url">
    <a :href="withBase(post.url)">{{ post.title }}</a>
    <span class="post-date">{{ post.date }}</span>
  </li>
</ul>

[阅读全部文章 →](/zh/blog/)

