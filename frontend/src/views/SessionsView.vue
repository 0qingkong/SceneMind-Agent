<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createCaptureSession, listCaptureSessions } from '../api/client'
import { loadPreferences } from '../privacy/settings'
import type { CaptureSessionSummary } from '../types/api'

const router = useRouter()
const sessions = ref<CaptureSessionSummary[]>([])
const loading = ref(false)
const creating = ref(false)
const errorMessage = ref('')
const title = ref('')
const location = ref('')
const targetQuery = ref('')
const interval = ref(loadPreferences().defaultCaptureInterval)

async function load() {
  loading.value = true
  try {
    sessions.value = (await listCaptureSessions()).items
  } catch {
    errorMessage.value = '无法读取观察会话。'
  } finally {
    loading.value = false
  }
}

async function create() {
  if (creating.value) return
  creating.value = true
  errorMessage.value = ''
  try {
    const preferences = loadPreferences()
    const session = await createCaptureSession({
      title: title.value.trim() || undefined,
      location: location.value.trim() || undefined,
      source_type: 'browser_camera',
      sample_interval_seconds: interval.value,
      target_query: targetQuery.value.trim() || undefined,
      auto_save_mode: preferences.autoSaveMode,
    })
    await router.push(`/sessions/${session.id}`)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '创建会话失败。'
  } finally {
    creating.value = false
  }
}

onMounted(load)
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">CONTINUOUS CAPTURE</p><h1>观察会话</h1></div>
      <span>{{ sessions.length }} Sessions</span>
    </div>
    <section class="session-create-card">
      <div><h2>新建低频观察</h2><p>按秒级间隔顺序抓拍和分析，不上传连续视频。</p></div>
      <div class="session-form-grid">
        <input v-model="title" maxlength="200" placeholder="会话标题（可选）" />
        <input v-model="location" maxlength="200" placeholder="位置（可选）" />
        <input v-model="targetQuery" maxlength="200" placeholder="目标物体，例如：杯子（可选）" />
        <label>采样间隔 <input v-model.number="interval" type="number" min="3" max="60" /> 秒</label>
      </div>
      <button class="primary-button" :disabled="creating" @click="create">{{ creating ? '正在创建…' : '创建并进入会话' }}</button>
    </section>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-if="loading" class="memory-status">正在读取会话…</p>
    <div v-else-if="sessions.length" class="session-list">
      <RouterLink v-for="item in sessions" :key="item.id" class="session-card" :to="`/sessions/${item.id}`">
        <div><span class="session-status" :class="item.status">{{ item.status }}</span><h3>{{ item.title || '未命名观察会话' }}</h3></div>
        <p>{{ item.location || '未记录位置' }} · 每 {{ item.sample_interval_seconds }} 秒</p>
        <div class="session-counters">
          <span><strong>{{ item.sampled_frames }}</strong>采样</span>
          <span><strong>{{ item.analyzed_frames }}</strong>分析</span>
          <span><strong>{{ item.saved_observations }}</strong>保存</span>
        </div>
        <small>{{ new Date(item.started_at).toLocaleString('zh-CN') }}</small>
      </RouterLink>
    </div>
    <div v-else class="memory-empty compact-empty"><h2>还没有观察会话</h2><p>创建后需要在会话页面明确开启摄像头；不会在后台自动采集。</p></div>
  </section>
</template>
