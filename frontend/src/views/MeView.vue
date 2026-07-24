<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getHealth } from '../api/client'
import type { HealthResponse } from '../types/api'

const health = ref<HealthResponse | null>(null)
const offline = ref(false)

onMounted(async () => {
  try { health.value = await getHealth() } catch { offline.value = true }
})
</script>

<template>
  <section>
    <div class="page-heading"><div><p class="eyebrow">MY SCENEMIND</p><h1>我的</h1></div><span>{{ offline ? 'Offline' : health?.status || 'Checking' }}</span></div>
    <div class="me-grid">
      <RouterLink to="/sessions"><strong>观察会话</strong><span>低频连续采集与会话记录</span></RouterLink>
      <RouterLink to="/devices"><strong>设备中心</strong><span>来源状态和浏览器摄像头</span></RouterLink>
      <RouterLink to="/glasses"><strong>眼镜模拟器</strong><span>未来设备交互预览</span></RouterLink>
      <RouterLink to="/insights"><strong>记忆洞察</strong><span>真实持久化数据统计</span></RouterLink>
      <RouterLink to="/privacy"><strong>隐私与设置</strong><span>采集偏好和 JSON 导出</span></RouterLink>
    </div>
    <section class="system-card"><h2>系统状态</h2><p v-if="offline">后端不可用</p><template v-else-if="health"><p>API v{{ health.version }} · {{ health.analyzer_mode }}</p><p>模型：{{ health.model_loaded ? '已加载' : '按需加载' }} · {{ health.device || '尚未选择设备' }}</p><p>Demo Mode：{{ health.demo_mode ? '开启' : '关闭' }}</p></template></section>
  </section>
</template>
