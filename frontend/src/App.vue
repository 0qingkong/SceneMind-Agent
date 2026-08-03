<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getReadiness } from './api/client'
import type { ReadinessResponse } from './types/api'

const readiness = ref<ReadinessResponse | null>(null)
onMounted(async () => {
  try { readiness.value = await getReadiness() } catch { readiness.value = null }
})
</script>

<template>
  <div class="application">
    <a class="skip-link" href="#main-content">跳到主要内容</a>
    <RouterLink v-if="readiness?.demo_mode || readiness?.demo_data_present" class="global-demo-banner" to="/system" role="status">
      演示环境 · Profile {{ readiness.demo_profile }} · 当前内容包含明确标记的预置演示数据
    </RouterLink>
    <header class="topbar">
      <RouterLink class="brand" to="/" aria-label="SceneMind 首页">
        <span class="brand-mark">S</span>
        <span><strong>SceneMind</strong><small>Spatial Memory Agent</small></span>
      </RouterLink>
      <nav class="desktop-nav" aria-label="主导航">
        <RouterLink to="/">首页</RouterLink><RouterLink to="/live">实时镜头</RouterLink>
        <RouterLink to="/analyze">场景分析</RouterLink><RouterLink to="/memory">空间记忆</RouterLink>
        <RouterLink to="/agent">Agent</RouterLink><RouterLink to="/sessions">观察会话</RouterLink>
        <RouterLink to="/devices">设备</RouterLink><RouterLink to="/insights">洞察</RouterLink>
      </nav>
      <RouterLink class="version-chip" to="/system" aria-label="查看系统状态">v0.18</RouterLink>
    </header>

    <main id="main-content" class="page-container" tabindex="-1">
      <RouterView />
    </main>

    <nav class="bottom-nav" aria-label="移动端主导航">
      <RouterLink to="/"><span aria-hidden="true">⌂</span><small>首页</small></RouterLink>
      <RouterLink to="/live"><span aria-hidden="true">◎</span><small>镜头</small></RouterLink>
      <RouterLink to="/memory"><span aria-hidden="true">▦</span><small>记忆</small></RouterLink>
      <RouterLink to="/agent"><span aria-hidden="true">✦</span><small>Agent</small></RouterLink>
      <RouterLink to="/me"><span aria-hidden="true">●</span><small>我的</small></RouterLink>
    </nav>
  </div>
</template>
