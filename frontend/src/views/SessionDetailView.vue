<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import axios from 'axios'
import { useRoute, useRouter } from 'vue-router'

import {
  deleteCaptureSession,
  getCaptureSession,
  sampleCaptureSession,
  stopCaptureSession,
} from '../api/client'
import { BrowserCameraSource } from '../capture/browserCamera'
import ImageStage from '../components/ImageStage.vue'
import ObservationCard from '../components/ObservationCard.vue'
import { loadPreferences, SETTINGS_EVENT } from '../privacy/settings'
import type { CaptureSampleResponse, CaptureSessionDetail } from '../types/api'

interface WakeLockSentinelLike { release(): Promise<void>; addEventListener(type: 'release', listener: () => void): void }

const route = useRoute()
const router = useRouter()
const camera = new BrowserCameraSource()
const video = ref<HTMLVideoElement | null>(null)
const session = ref<CaptureSessionDetail | null>(null)
const lastSample = ref<CaptureSampleResponse | null>(null)
const frameUrl = ref('')
const cameraConnected = ref(false)
const running = ref(false)
const sampling = ref(false)
const hiddenPaused = ref(false)
const allowWhenHidden = ref(false)
const forceNext = ref(false)
const showCameraIndicator = ref(loadPreferences().alwaysShowCameraIndicator)
const errorMessage = ref('')
const eventMessage = ref('')
let wakeLock: WakeLockSentinelLike | null = null
let loopPromise: Promise<void> | null = null
let wakeLoop: (() => void) | null = null

const active = computed(() => session.value?.status === 'active')

function wait(milliseconds: number) {
  return new Promise<void>((resolve) => {
    const timer = globalThis.setTimeout(() => {
      wakeLoop = null
      resolve()
    }, milliseconds)
    wakeLoop = () => {
      globalThis.clearTimeout(timer)
      wakeLoop = null
      resolve()
    }
  })
}

function revokeFrame() {
  if (frameUrl.value) URL.revokeObjectURL(frameUrl.value)
  frameUrl.value = ''
}

async function load() {
  try {
    session.value = await getCaptureSession(String(route.params.id))
  } catch {
    errorMessage.value = '观察会话不存在或后端不可用。'
  }
}

async function connectCamera() {
  if (!video.value) return
  errorMessage.value = ''
  try {
    await camera.connect({ videoElement: video.value, facingMode: 'environment' })
    cameraConnected.value = true
  } catch (error) {
    cameraConnected.value = false
    errorMessage.value = error instanceof Error ? error.message : '摄像头连接失败。'
  }
}

async function requestWakeLock() {
  const wakeLockApi = (navigator as Navigator & { wakeLock?: { request(type: 'screen'): Promise<WakeLockSentinelLike> } }).wakeLock
  if (!wakeLockApi || wakeLock) return
  try {
    wakeLock = await wakeLockApi.request('screen')
    wakeLock.addEventListener('release', () => { wakeLock = null })
  } catch {
    eventMessage.value = '屏幕唤醒锁不可用；保持页面前台以继续采集。'
  }
}

async function releaseResources() {
  running.value = false
  wakeLoop?.()
  if (wakeLock) await wakeLock.release().catch(() => undefined)
  wakeLock = null
  await camera.disconnect()
  cameraConnected.value = false
}

async function takeSample(force = false) {
  if (!session.value || sampling.value || !cameraConnected.value) return
  sampling.value = true
  errorMessage.value = ''
  try {
    const frame = await camera.captureFrame()
    revokeFrame()
    frameUrl.value = URL.createObjectURL(frame)
    const response = await sampleCaptureSession(session.value.id, frame, {
      forceSave: force || forceNext.value,
      capturedAt: new Date().toISOString(),
      sourceDeviceId: camera.device?.id,
      sourceDeviceName: camera.device?.label,
    })
    forceNext.value = false
    lastSample.value = response
    session.value = { ...session.value, ...response.session }
    eventMessage.value = response.target_found
      ? `目标“${session.value.target_query}”已找到${response.saved ? '并保存' : ''}`
      : response.saved ? `已保存：${response.reason}` : `本帧未保存：${response.reason}`
    if (response.observation_id) await load()
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 409) running.value = false
    errorMessage.value = axios.isAxiosError(error) && typeof error.response?.data?.detail === 'string'
      ? error.response.data.detail
      : '采样分析失败。'
  } finally {
    sampling.value = false
  }
}

async function captureLoop() {
  while (running.value && session.value?.status === 'active') {
    const preferences = loadPreferences()
    if (preferences.pauseAllContinuousCapture) {
      eventMessage.value = '隐私设置已暂停所有连续采集。'
      running.value = false
      break
    }
    hiddenPaused.value = document.hidden && !allowWhenHidden.value
    if (!hiddenPaused.value) await takeSample(false)
    await wait((session.value?.sample_interval_seconds ?? 5) * 1000)
  }
}

async function startLoop() {
  if (running.value || !active.value) return
  if (loadPreferences().pauseAllContinuousCapture) {
    errorMessage.value = '隐私设置已暂停所有连续采集。'
    return
  }
  if (!cameraConnected.value) await connectCamera()
  if (!cameraConnected.value) return
  await requestWakeLock()
  running.value = true
  loopPromise = captureLoop().finally(() => { loopPromise = null })
}

async function stop() {
  running.value = false
  wakeLoop?.()
  if (loopPromise) await loopPromise
  await releaseResources()
  if (session.value?.status === 'active') session.value = await stopCaptureSession(session.value.id)
}

async function remove() {
  if (!session.value || session.value.status === 'active') return
  if (loadPreferences().confirmBeforeDelete && !window.confirm('删除这条会话？已保存的场景记忆会保留。')) return
  await deleteCaptureSession(session.value.id)
  await router.push('/sessions')
}

function visibilityChanged() {
  hiddenPaused.value = document.hidden && !allowWhenHidden.value && running.value
}

function privacyChanged() {
  if (loadPreferences().pauseAllContinuousCapture) void releaseResources()
}

onMounted(() => {
  void load()
  document.addEventListener('visibilitychange', visibilityChanged)
  globalThis.addEventListener(SETTINGS_EVENT, privacyChanged)
  globalThis.addEventListener('storage', privacyChanged)
})
onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', visibilityChanged)
  globalThis.removeEventListener(SETTINGS_EVENT, privacyChanged)
  globalThis.removeEventListener('storage', privacyChanged)
  running.value = false
  wakeLoop?.()
  revokeFrame()
  void releaseResources()
})
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">CAPTURE SESSION</p><h1>{{ session?.title || '观察会话详情' }}</h1></div>
      <span>{{ session?.status || 'loading' }}</span>
    </div>
    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <template v-if="session">
      <div class="session-dashboard">
        <section class="workspace-panel">
          <div class="live-stage session-live-stage">
            <video v-show="!frameUrl" ref="video" autoplay muted playsinline></video>
            <ImageStage v-if="frameUrl" :image-url="frameUrl" :objects="lastSample?.analysis.objects ?? []" :loading="sampling" />
            <span v-if="cameraConnected && showCameraIndicator" class="camera-indicator">● 摄像头使用中</span>
          </div>
          <div class="session-counters large">
            <span><strong>{{ session.sampled_frames }}</strong>采样</span>
            <span><strong>{{ session.analyzed_frames }}</strong>分析</span>
            <span><strong>{{ session.saved_observations }}</strong>保存</span>
          </div>
          <div class="session-actions">
            <button class="secondary-button" :disabled="cameraConnected" @click="connectCamera">连接摄像头</button>
            <button class="primary-button" :disabled="running || !active" @click="startLoop">开始顺序采样</button>
            <button class="secondary-button" :disabled="sampling || !cameraConnected || !active" @click="takeSample(true)">立即强制保存</button>
            <button class="danger-button" :disabled="!active" @click="stop">停止会话</button>
          </div>
          <label class="privacy-check"><input v-model="allowWhenHidden" type="checkbox" /> 页面隐藏时仍尝试采集（浏览器可能暂停，不保证后台运行）</label>
          <p v-if="hiddenPaused" class="warning-message">页面当前不可见，顺序采样已暂停。</p>
          <p v-if="eventMessage" class="success-message">{{ eventMessage }}</p>
          <button v-if="session.status !== 'active'" class="text-button danger-text" @click="remove">删除会话记录</button>
        </section>
        <section class="workspace-panel">
          <h2>会话信息</h2>
          <div class="session-meta">
            <p><span>间隔</span>{{ session.sample_interval_seconds }} 秒</p>
            <p><span>保存策略</span>{{ session.auto_save_mode }}</p>
            <p><span>目标</span>{{ session.target_query || '未设置' }}</p>
            <p><span>目标状态</span>{{ session.target_seen ? '已出现' : '尚未出现' }}</p>
            <p><span>来源</span>{{ session.source_type }}</p>
            <p><span>位置</span>{{ session.location || '未记录' }}</p>
          </div>
          <p class="retrieval-disclaimer">这是低频前台采样，不是连续视频、30 FPS 推理或后台服务。</p>
        </section>
      </div>
      <section v-if="session.recent_observations.length" class="history-section">
        <h2>本会话保存的记忆</h2>
        <div class="observation-timeline">
          <ObservationCard v-for="item in session.recent_observations" :key="item.id" :observation="item" />
        </div>
      </section>
    </template>
  </section>
</template>
