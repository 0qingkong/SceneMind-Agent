<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'

import { getHealth, getReadiness } from '../api/client'
import type { HealthResponse, ReadinessResponse } from '../types/api'

type StatusLevel = '正常' | '注意' | '不可用'

const health = ref<HealthResponse | null>(null)
const readiness = ref<ReadinessResponse | null>(null)
const loading = ref(true)
const backendUnavailable = ref(false)
const cameraSupported = computed(() => Boolean(navigator.mediaDevices?.getUserMedia))
const secureContext = computed(() => globalThis.isSecureContext || globalThis.location.hostname === 'localhost')
const copiedCommand = ref('')
const recoveryCommands = [
  ['重新检查', '.\\scripts\\check-system.ps1'],
  ['应急演示', '.\\scripts\\start-demo.ps1 -Profile C'],
  ['安全停止', '.\\scripts\\stop-demo.ps1'],
]

async function copyCommand(command: string) {
  try {
    await navigator.clipboard.writeText(command)
    copiedCommand.value = command
    setTimeout(() => { if (copiedCommand.value === command) copiedCommand.value = '' }, 1800)
  } catch {
    copiedCommand.value = ''
  }
}

function level(value: boolean, warning = false): StatusLevel {
  if (value) return warning ? '注意' : '正常'
  return '不可用'
}

function statusClass(value: StatusLevel) {
  return value === '正常' ? 'ok' : value === '注意' ? 'warn' : 'bad'
}

onMounted(async () => {
  try {
    const [healthResult, readyResult] = await Promise.all([getHealth(), getReadiness()])
    health.value = healthResult
    readiness.value = readyResult
  } catch (error) {
    if (axios.isAxiosError<ReadinessResponse>(error) && error.response?.data) {
      readiness.value = error.response.data
      try { health.value = await getHealth() } catch { backendUnavailable.value = true }
    } else {
      backendUnavailable.value = true
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section>
    <div class="page-heading"><div><p class="eyebrow">COMPETITION READINESS</p><h1>系统状态</h1></div><span>{{ readiness ? (readiness.status === 'ready' ? '就绪' : '需要注意') : (loading ? '检查中' : '离线') }}</span></div>
    <p v-if="backendUnavailable" class="error-message">后端不可用。请运行 <code>.\scripts\start-demo.ps1</code>，并查看 <code>.runtime\logs</code>。</p>
    <div class="system-status-grid">
      <article><span :class="statusClass(level(Boolean(health)))">{{ level(Boolean(health)) }}</span><strong>后端</strong><small>{{ health ? `API v${health.version} · ${health.build}` : '无法连接健康检查' }}</small></article>
      <article><span :class="statusClass(level(Boolean(readiness?.database_reachable)))">{{ level(Boolean(readiness?.database_reachable)) }}</span><strong>数据库</strong><small>{{ readiness?.database_reachable ? '查询正常' : '数据库不可达' }}</small></article>
      <article><span :class="statusClass(level(Boolean(readiness?.storage_writable)))">{{ level(Boolean(readiness?.storage_writable)) }}</span><strong>图片存储</strong><small>{{ readiness?.storage_writable ? '可写' : '不可写' }}</small></article>
      <article><span :class="statusClass(level(Boolean(readiness?.model_configured), Boolean(readiness && !readiness.model_loaded)))">{{ level(Boolean(readiness?.model_configured), Boolean(readiness && !readiness.model_loaded)) }}</span><strong>检测器</strong><small>{{ readiness ? `${readiness.analyzer_mode} · ${readiness.model_loaded ? '模型已加载' : '模型按需加载'}` : '未知' }}</small></article>
      <article><span :class="statusClass(level(cameraSupported))">{{ level(cameraSupported) }}</span><strong>浏览器摄像头</strong><small>{{ cameraSupported ? 'API 可用，仍需用户授权' : '浏览器不支持' }}</small></article>
      <article><span :class="statusClass(level(secureContext))">{{ level(secureContext) }}</span><strong>安全上下文</strong><small>{{ secureContext ? '允许请求摄像头' : '手机/LAN 通常需要 HTTPS' }}</small></article>
    </div>
    <section v-if="readiness" class="system-card system-details">
      <h2>当前演示环境</h2>
      <p><span>Profile</span>{{ readiness.demo_profile }}</p><p><span>Demo 数据</span>{{ readiness.demo_data_present ? '存在' : '不存在' }}</p>
      <p><span>运行设备</span>{{ readiness.device || '尚未选择 CPU/CUDA' }}</p><p><span>空间推理</span>{{ readiness.spatial_reasoner_enabled ? '启用' : '关闭' }}</p>
      <p><span>活动会话</span>{{ readiness.active_session_count }}</p><p><span>更新时间</span>{{ new Date(readiness.timestamp).toLocaleString('zh-CN') }}</p>
    </section>
    <section class="system-card recovery-card">
      <h2>恢复入口</h2>
      <p v-for="item in recoveryCommands" :key="item[0]"><span>{{ item[0] }}</span><code>{{ item[1] }}</code><button class="copy-button" :aria-label="`复制${item[0]}命令`" @click="copyCommand(item[1])">{{ copiedCommand === item[1] ? '已复制' : '复制' }}</button></p>
      <p><span>详细手册</span><code>docs\RECOVERY.md</code></p>
    </section>
  </section>
</template>
