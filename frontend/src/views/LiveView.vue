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
const showCameraIndicator = ref(true)

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
  <section class="perception-view live-view">
    <div class="page-heading">
      <div><p class="eyebrow">LIVE LENS</p><h1>实时空间镜头</h1></div>
      <span :class="{ 'camera-live-chip': cameraActive }">{{ cameraActive ? '● 摄像头使用中' : '摄像头未开启' }}</span>
    </div>

    <div class="perception-context" aria-label="镜头状态">
      <span>DEVICE · {{ camera.device?.label || 'Browser camera' }}</span><span>SOURCE · Live Camera</span><span>{{ cameraActive ? 'STATE · Connected' : 'STATE · Permission required' }}</span>
    </div>

    <div class="workspace-grid live-workspace perception-workspace">
      <section class="workspace-panel capture-panel">
        <aside class="permission-note"><strong>启用前说明</strong><p>浏览器会在你点击后请求摄像头权限，仅抓取你主动分析的静态画面，不请求麦克风。</p></aside>
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
          <button class="primary-button" :disabled="cameraState === 'connecting' || busy" @click="connect">
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
          <label>场景标题<input v-model="title" maxlength="200" placeholder="例如：办公桌（可选）" /></label>
          <label>地点<input v-model="location" maxlength="200" placeholder="例如：实验室（可选）" /></label>
        </div>
        <div class="analysis-actions">
          <button class="secondary-button" :disabled="!cameraActive || busy" @click="capture(false)">{{ busy ? '正在分析…' : '抓拍并分析' }}</button>
          <button class="primary-button" :disabled="!cameraActive || busy" @click="capture(true)">{{ busy ? '正在处理…' : '抓拍、分析并记忆' }}</button>
        </div>
        <button v-if="frozenUrl" class="text-button" @click="returnToLive">返回实时画面</button>
        <div v-if="errorMessage" class="state-message state-error" role="alert"><p>{{ errorMessage }}</p><button class="secondary-button" @click="connect">重新连接</button></div>
        <p v-if="saved" class="success-message">已保存 · <RouterLink :to="saved.detail_url">打开记忆证据</RouterLink></p>
      </section>

      <section class="workspace-panel result-panel intelligence-panel" :class="{ 'result-ready': result }">
        <div class="panel-title-row"><div><p class="eyebrow">LIVE INTERPRETATION</p><h2>镜头分析</h2></div><span>{{ result ? '场景理解完成' : busy ? '正在理解' : '等待抓拍' }}</span></div>
        <div class="find-helper">
          <input v-model="findQuery" placeholder="查找物体，例如：杯子 / cup" />
          <span v-if="findState === true" class="found-state">已找到</span>
          <span v-else-if="findState === false" class="not-found-state">未找到</span>
        </div>
        <template v-if="result">
          <div class="summary-card">{{ result.scene_summary }}</div>
          <div class="metrics-row">
            <div><strong>{{ result.objects.length }}</strong><small>检测物体</small></div>
            <div><strong>{{ result.latency_ms }}ms</strong><small>分析耗时</small></div>
            <div><strong>{{ result.engine }}</strong><small>分析器模式</small></div>
          </div>
          <ObjectList :objects="result.objects" />
          <RelationList :objects="result.objects" :relations="result.relations" />
          <p class="boundary-note">二维关系不代表真实深度或物理距离；类别结果不用于身份识别。</p>
        </template>
        <div v-else class="empty-result"><strong>等待抓拍</strong><p>画面只会在你点击分析或会话采样时发送到后端。</p></div>
      </section>
    </div>
  </section>
</template>
