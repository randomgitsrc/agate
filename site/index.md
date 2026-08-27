---
layout: home

hero:
  name: Agateon
  text: Verify AI agents the way a build system verifies a compiler
  tagline: An open-source orchestration protocol that runs software work through AI agents — and gates every phase with objective, machine-checkable signals.
  actions:
    - theme: brand
      text: Get started
      link: https://github.com/randomgitsrc/agateon
    - theme: alt
      text: Read the blog
      link: /blog/

features:
  - icon: 🛡️
    title: Objective gates
    details: Eight phases — requirements, design, test-first, implementation, verification, acceptance, consistency, release — each must pass a machine-checkable gate (test exit codes, git log, BDD counts) before the state machine advances.
  - icon: 📝
    title: State that survives crashes
    details: All progress lives in version-controlled Markdown. A killed session resumes where it left off, and every step is auditable from git history.
  - icon: 🧩
    title: Roles separated by design
    details: One orchestrator plans and dispatches; independent subagents execute; gates judge. The agent doing the work never signs off on its own work.
---

## Quick start

Install and run Agateon from a fresh checkout:

```bash
curl -sSL https://raw.githubusercontent.com/randomgitsrc/agateon/main/install.sh | bash
```

No runtime, no daemon. The protocol is a set of Markdown cards plus gate scripts, stored in version control alongside your work.

## Latest from the blog

<script setup>
import { data as posts } from './.vitepress/blog.data.ts'
import { withBase } from 'vitepress'

// 最新 3 篇（文章清单自动生成，见 .vitepress/posts.ts）
const latestPosts = posts.slice(0, 3)
</script>

<ul class="latest-posts">
  <li v-for="post in latestPosts" :key="post.url">
    <a :href="withBase(post.url)">{{ post.title }}</a>
    <span class="post-date">{{ post.date }}</span>
  </li>
</ul>

[Read all posts →](/blog/)
