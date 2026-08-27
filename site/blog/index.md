---
title: Blog
description: Engineering notes and postmortems from building Agateon.
---

# Blog

Engineering notes and postmortems from building Agateon.

<script setup>
import { data as posts } from '../.vitepress/blog.data.ts'
import { withBase } from 'vitepress'
</script>

<ul class="post-list">
  <li v-for="post in posts" :key="post.url">
    <a :href="withBase(post.url)">{{ post.title }}</a>
    <span class="post-date">— {{ post.date }}</span>
  </li>
</ul>
