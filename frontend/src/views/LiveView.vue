<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import axios from 'axios'

import { analyzeScene, createObservation } from '../api/client'
import { BrowserCameraSource } from '../capture/browserCamera'
import type { CaptureDevice, CaptureSourceState } from '../capture/types'
import ImageStage from '../components/ImageStage.vue'
import ObjectList from '../components/ObjectList.vue'
import RelationList from '../components/RelationList.vue'
import type { AnalyzeResponse, ObservationDetail } from '../types/api'
import { loadPreferences } from '../privacy/settings'

const camera = new BrowserCameraSource()
const video = ref<HTMLVideoElement | null>(null)
const devices = ref<CaptureDevice[]>([])
const selectedDeviceId = ref('')
const facingMode = ref<'user' | 'environment'>('environment')
const cameraState = ref<CaptureSourceState>('disconnected')
const busy = ref(false)
const errorMessage = ref('')
const frozenUrl = ref('')
const result = ref<AnalyzeResponse | null>(null)
const saved = ref<ObservationDetail | null>(null)
const title = ref('')
const location = ref('')
const findQuery = ref('')
const showCameraIndicator = ref(loadPreferences().alwaysShowCameraIndicator)

const cameraActive = computed(() => cameraState.value === 'connected')
const findState = computed(() => {
  const query = findQuery.value.trim().toLocaleLowerCase()
  if (!query || !result.value) return null
  return result.value.objects.some((item) =>
    item.label.toLocaleLowerCase().includes(query)
    || item.display_name.toLocaleLowerCase().includes(query),
  )
})

function syncState() {
  cameraState.value = camera.state
  selectedDeviceId.value = camera.device?.id ?? selectedDeviceId.value
}

function releaseFrozen() {
  if (frozenUrl.value) URL.revokeObjectURL(frozenUrl.value)
  frozenUrl.value = ''
}

async function refreshDevices() {
  devices.value = await camera.listDevices()
}

async function connect() {
  if (!video.value || busy.value) return
  errorMessage.value = ''
  cameraState.value = 'connecting'
  try {
    await camera.connect({
      videoElement: video.value,
      deviceId: selectedDeviceId.value || undefined,
      facingMode: facingMode.value,
    })
    syncState()
    await refreshDevices()
  } catch (error) {
    syncState()
    errorMessage.value = error instanceof Error ? error.message : '无法启动摄像头。'
  }
}

async function switchFacing(mode: 'user' | 'environment') {
  facingMode.value = mode
  selectedDeviceId.value = ''
  await connect()
}

async function switchDevice() {
  if (!video.value || !selectedDeviceId.value) return
  errorMessage.value = ''
  cameraState.value = 'connecting'
  try {
    await camera.switchDevice(selectedDeviceId.value, video.value)
    syncState()
  } catch (error) {
    syncState()
    errorMessage.value = error instanceof Error ? error.message : '无法切换摄像头。'
  }
}

async function stopCamera() {
  await camera.disconnect()
  syncState()
}

function apiError(error: unknown) {
  if (!axios.isAxiosError(error)) return '分析失败，请稍后重试。'
  if (!error.response) return '无法连接分析后端，请确认后端已经启动。'
  if (error.response.status === 503) return '真实检测器当前不可用，请检查后端模型状态。'
  return typeof error.response.data?.detail === 'string' ? error.response.data.detail : '分析失败。'
}

async function capture(remember: boolean) {
  if (busy.value || cameraState.value !== 'connected') return
  busy.value = true
  errorMessage.value = ''
  saved.value = null
  result.value = null
  releaseFrozen()
  try {
    const frame = await camera.captureFrame()
    frozenUrl.value = URL.createObjectURL(frame)
    if (remember) {
      const observation = await createObservation(frame, title.value, location.value, {
        sourceType: 'browser_camera',
        sourceDeviceId: camera.device?.id,
        sourceDeviceName: camera.device?.label,
        capturedAt: new Date().toISOString(),
      })
      saved.value = observation
      result.value = {
        trace_id: observation.id,
        engine: observation.engine,
        filename: observation.original_filename,
        image_width: observation.image_width,
        image_height: observation.image_height,
        scene_summary: observation.summary,
        objects: observation.objects,
        relations: observation.relations,
        latency_ms: 0,
      }
    } else {
      result.value = await analyzeScene(frame)
    }
  } catch (error) {
    errorMessage.value = apiError(error)
    if (!result.value) releaseFrozen()
  } finally {
    busy.value = false
  }
}

async function returnToLive() {
  releaseFrozen()
  result.value = null
  saved.value = null
  await nextTick()
  if (video.value && camera.stream) video.value.srcObject = camera.stream
}

onMounted(() => refreshDevices().catch(() => undefined))
onBeforeUnmount(() => {
  releaseFrozen()
  void camera.disconnect()
})
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">LIVE LENS</p><h1>实时空间镜头</h1></div>
      <span :class="{ 'camera-live-chip': cameraActive }">{{ cameraActive ? '● CAMERA ACTIVE' : 'Camera off' }}</span>
    </div>

    <div class="workspace-grid live-workspace">
      <section class="workspace-panel">
        <div class="live-stage">
          <video v-show="!frozenUrl" ref="video" autoplay muted playsinline></video>
          <ImageStage v-if="frozenUrl" :image-url="frozenUrl" :objects="result?.objects ?? []" :loading="busy" />
          <div v-if="cameraState === 'disconnected' && !frozenUrl" class="live-placeholder">
            <strong>摄像头尚未启用</strong>
            <p>点击下方按钮后浏览器才会请求摄像头权限。不会采集音频。</p>
          </div>
          <span v-if="cameraActive && showCameraIndicator" class="camera-indicator">● 摄像头使用中</span>
        </div>

        <div class="camera-controls">
          <button class="primary-button" :disabled="cameraState === 'connecting'" @click="connect">
            {{ cameraState === 'connecting' ? '正在连接…' : cameraState === 'connected' ? '重新连接' : '允许并开启摄像头' }}
          </button>
          <button class="secondary-button" :disabled="cameraState === 'disconnected'" @click="stopCamera">停止摄像头</button>
        </div>
        <div class="camera-options">
          <button :class="{ active: facingMode === 'environment' }" @click="switchFacing('environment')">优先后置</button>
          <button :class="{ active: facingMode === 'user' }" @click="switchFacing('user')">优先前置</button>
          <select v-model="selectedDeviceId" @change="switchDevice">
            <option value="">自动选择摄像头</option>
            <option v-for="device in devices" :key="device.id" :value="device.id">{{ device.label }}</option>
          </select>
        </div>
        <div class="scene-fields">
          <input v-model="title" maxlength="200" placeholder="场景标题（可选）" />
          <input v-model="location" maxlength="200" placeholder="位置（可选）" />
        </div>
        <div class="analysis-actions">
          <button class="secondary-button" :disabled="!cameraActive || busy" @click="capture(false)">抓拍并分析</button>
          <button class="primary-button" :disabled="!cameraActive || busy" @click="capture(true)">抓拍、分析并记忆</button>
        </div>
        <button v-if="frozenUrl" class="text-button" @click="returnToLive">返回实时画面</button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p v-if="saved" class="success-message">已保存 · <RouterLink :to="saved.detail_url">打开记忆证据</RouterLink></p>
      </section>

      <section class="workspace-panel result-panel">
        <h2>镜头分析</h2>
        <div class="find-helper">
          <input v-model="findQuery" placeholder="查找物体，例如：杯子 / cup" />
          <span v-if="findState === true" class="found-state">已找到</span>
          <span v-else-if="findState === false" class="not-found-state">未找到</span>
        </div>
        <template v-if="result">
          <div class="summary-card">{{ result.scene_summary }}</div>
          <div class="metrics-row">
            <div><strong>{{ result.objects.length }}</strong><small>Objects</small></div>
            <div><strong>{{ result.latency_ms }}ms</strong><small>Latency</small></div>
            <div><strong>{{ result.engine }}</strong><small>Engine</small></div>
          </div>
          <ObjectList :objects="result.objects" />
          <RelationList :objects="result.objects" :relations="result.relations" />
        </template>
        <div v-else class="empty-result"><strong>等待抓拍</strong><p>画面只会在你点击分析或会话采样时发送到后端。</p></div>
      </section>
    </div>
  </section>
</template>
