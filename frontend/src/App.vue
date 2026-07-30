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
    <RouterLink v-if="readiness?.demo_mode || readiness?.demo_data_present" class="global-demo-banner" to="/system">
      演示环境 · Profile {{ readiness.demo_profile }} · 当前内容包含明确标记的预置演示数据
    </RouterLink>
    <header class="topbar">
      <RouterLink class="brand" to="/">
        <span class="brand-mark">S</span>
        <span><strong>SceneMind</strong><small>Spatial Memory Agent</small></span>
      </RouterLink>
      <nav class="desktop-nav">
        <RouterLink to="/">首页</RouterLink><RouterLink to="/live">实时镜头</RouterLink>
        <RouterLink to="/analyze">分析</RouterLink><RouterLink to="/memory">记忆</RouterLink>
        <RouterLink to="/agent">Agent</RouterLink><RouterLink to="/sessions">观察会话</RouterLink>
        <RouterLink to="/devices">设备</RouterLink><RouterLink to="/insights">洞察</RouterLink>
      </nav>
      <span class="version-chip">v0.13</span>
    </header>

    <main class="page-container">
      <RouterView />
    </main>

    <nav class="bottom-nav">
      <RouterLink to="/">首页</RouterLink>
      <RouterLink to="/live">镜头</RouterLink>
      <RouterLink to="/memory">记忆</RouterLink>
      <RouterLink to="/agent">Agent</RouterLink>
      <RouterLink to="/me">我的</RouterLink>
    </nav>
  </div>
</template>
