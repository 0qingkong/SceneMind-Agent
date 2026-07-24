<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getDeviceStats } from '../api/client'
import { BrowserCameraSource } from '../capture/browserCamera'
import type { CaptureDevice } from '../capture/types'
import type { DeviceStatsResponse } from '../types/api'

const camera = new BrowserCameraSource()
const cameras = ref<CaptureDevice[]>([])
const stats = ref<DeviceStatsResponse | null>(null)
const loading = ref(true)
const errorMessage = ref('')

async function load() {
  loading.value = true
  try {
    const [browserDevices, persisted] = await Promise.all([
      camera.listDevices().catch(() => []),
      getDeviceStats(),
    ])
    cameras.value = browserDevices
    stats.value = persisted
  } catch {
    errorMessage.value = '无法读取设备统计。'
  } finally {
    loading.value = false
  }
}

function latest(sourceType: string) {
  const candidates = stats.value?.sources.filter((item) => item.source_type === sourceType) ?? []
  return candidates.map((item) => item.latest_activity).filter(Boolean).sort().at(-1) ?? null
}

onMounted(load)
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">DEVICE CENTER</p><h1>采集设备中心</h1></div>
      <span>{{ cameras.length }} Cameras</span>
    </div>
    <p class="retrieval-disclaimer">浏览器设备连接状态不会跨刷新保留；下方活动数据来自已保存记录。</p>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="loading" class="memory-status">正在读取设备…</p>
    <div v-else class="device-grid">
      <article class="device-card">
        <span class="device-icon">UP</span><div><h2>图片上传</h2><p>文件选择来源</p></div>
        <strong class="source-state available">可用</strong>
        <small>最近活动：{{ latest('upload') ? new Date(String(latest('upload'))).toLocaleString('zh-CN') : '暂无' }}</small>
        <RouterLink class="secondary-link compact-link" to="/analyze">打开分析</RouterLink>
      </article>
      <article class="device-card">
        <span class="device-icon">CAM</span><div><h2>浏览器摄像头</h2><p>{{ cameras.length ? `发现 ${cameras.length} 个视频输入` : '需要权限后显示设备名称' }}</p></div>
        <strong class="source-state">当前未连接</strong>
        <small>刷新页面后必须重新明确连接。</small>
        <RouterLink class="secondary-link compact-link" to="/live">打开实时镜头</RouterLink>
      </article>
      <article v-for="item in cameras" :key="item.id" class="device-card camera-device-card">
        <span class="device-icon">{{ cameras.indexOf(item) + 1 }}</span><div><h2>{{ item.label }}</h2><p>videoinput</p></div>
        <strong class="source-state">已枚举，未连接</strong>
        <small>设备 ID 仅保留在当前浏览器上下文。</small>
        <RouterLink class="secondary-link compact-link" to="/live">选择使用</RouterLink>
      </article>
      <article class="device-card simulator-device-card">
        <span class="device-icon">HUD</span><div><h2>AI Glasses Simulator</h2><p>未来设备交互预览</p></div>
        <strong class="source-state simulator">浏览器模拟</strong>
        <small>不代表已连接真实 AI 眼镜。</small>
        <RouterLink class="secondary-link compact-link" to="/glasses">打开模拟器</RouterLink>
      </article>
    </div>
    <div v-if="stats" class="metrics-row device-metrics">
      <div><strong>{{ stats.memory_count }}</strong><small>Memories</small></div>
      <div><strong>{{ stats.session_count }}</strong><small>Sessions</small></div>
      <div><strong>{{ stats.active_session_count }}</strong><small>Active</small></div>
    </div>
    <section v-if="stats?.sources.length" class="insight-card source-activity">
      <h2>持久化来源活动</h2>
      <div v-for="item in stats.sources" :key="`${item.source_type}-${item.device_name}`">
        <strong>{{ item.device_name || item.source_type }}</strong>
        <span>{{ item.source_type }} · {{ item.observation_count }} 条记忆 · {{ item.session_count }} 个会话</span>
        <small>{{ item.latest_activity ? new Date(item.latest_activity).toLocaleString('zh-CN') : '暂无活动时间' }}</small>
      </div>
    </section>
  </section>
</template>
