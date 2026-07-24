<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import {
  analyzeScene,
  apiAssetUrl,
  createObservation,
  getCaptureSession,
  getObservation,
  listCaptureSessions,
  listObservations,
  queryAgent,
} from '../api/client'
import { GlassesSimulatorSource } from '../capture/glassesSimulator'
import ImageStage from '../components/ImageStage.vue'
import RelationList from '../components/RelationList.vue'
import { loadPreferences } from '../privacy/settings'
import type {
  AgentQueryResponse,
  AnalyzeResponse,
  CaptureSessionSummary,
  ObservationDetail,
  ObservationSummary,
} from '../types/api'

type SimulatorInput = 'live' | 'observation' | 'session'

const source = new GlassesSimulatorSource()
const video = ref<HTMLVideoElement | null>(null)
const input = ref<SimulatorInput>('live')
const observations = ref<ObservationSummary[]>([])
const sessions = ref<CaptureSessionSummary[]>([])
const selectedObservation = ref('')
const selectedSession = ref('')
const currentObservation = ref<ObservationDetail | null>(null)
const result = ref<AnalyzeResponse | null>(null)
const imageUrl = ref('')
const recording = ref(false)
const busy = ref(false)
const eventMessage = ref('')
const targetQuery = ref('')
const agentQuery = ref('')
const agentAnswer = ref<AgentQueryResponse | null>(null)
const showLabels = ref(loadPreferences().showSimulatorLabels)

const targetFound = computed(() => {
  const target = targetQuery.value.trim().toLocaleLowerCase()
  if (!target || !result.value) return false
  return result.value.objects.some((item) => item.label.toLocaleLowerCase().includes(target) || item.display_name.toLocaleLowerCase().includes(target))
})

function releaseImage() {
  if (imageUrl.value.startsWith('blob:')) URL.revokeObjectURL(imageUrl.value)
  imageUrl.value = ''
}

async function switchInput() {
  eventMessage.value = ''
  result.value = null
  currentObservation.value = null
  releaseImage()
  if (input.value !== 'live') {
    recording.value = false
    await source.disconnect()
  }
}

async function connectLive() {
  if (!video.value) return
  await source.connect({ videoElement: video.value, facingMode: 'environment' })
  recording.value = true
}

async function scanLive(remember = false) {
  if (!recording.value || busy.value) return
  busy.value = true
  try {
    const frame = await source.captureFrame()
    releaseImage()
    imageUrl.value = URL.createObjectURL(frame)
    if (remember) {
      const saved = await createObservation(frame, '眼镜模拟器抓拍', undefined, {
        sourceType: 'glasses_simulator',
        sourceDeviceId: source.device?.id,
        sourceDeviceName: source.device?.label,
        capturedAt: new Date().toISOString(),
      })
      currentObservation.value = saved
      result.value = savedAsAnalysis(saved)
      eventMessage.value = 'MEMORY SAVED'
    } else {
      result.value = await analyzeScene(frame)
      eventMessage.value = 'FRAME ANALYZED'
    }
  } finally {
    busy.value = false
  }
}

function savedAsAnalysis(item: ObservationDetail): AnalyzeResponse {
  return {
    trace_id: item.id, engine: item.engine, filename: item.original_filename,
    image_width: item.image_width, image_height: item.image_height,
    scene_summary: item.summary, objects: item.objects, relations: item.relations, latency_ms: 0,
  }
}

async function loadObservationInput() {
  if (!selectedObservation.value) return
  const detail = await getObservation(selectedObservation.value)
  currentObservation.value = detail
  result.value = savedAsAnalysis(detail)
  imageUrl.value = apiAssetUrl(detail.image_url)
  eventMessage.value = 'SAVED MEMORY LOADED'
}

async function loadSessionInput() {
  if (!selectedSession.value) return
  const detail = await getCaptureSession(selectedSession.value)
  const latest = detail.recent_observations[0]
  if (!latest) {
    eventMessage.value = '此会话还没有保存的观察'
    return
  }
  selectedObservation.value = latest.id
  await loadObservationInput()
  eventMessage.value = 'SESSION MEMORY LOADED'
}

async function askAgent() {
  if (!agentQuery.value.trim()) return
  agentAnswer.value = await queryAgent(agentQuery.value.trim())
}

onMounted(async () => {
  const [memory, captureSessions] = await Promise.all([listObservations({ limit: 100 }), listCaptureSessions()])
  observations.value = memory.items
  sessions.value = captureSessions.items
})
onBeforeUnmount(() => {
  releaseImage()
  void source.disconnect()
})
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">AI GLASSES SIMULATOR</p><h1>未来设备交互预览</h1></div>
      <span>Simulator</span>
    </div>
    <div class="simulator-disclaimer">当前为浏览器端模拟，不代表已连接真实 AI 眼镜。</div>
    <div class="simulator-toolbar">
      <label>输入来源
        <select v-model="input" @change="switchInput">
          <option value="live">实时浏览器摄像头</option>
          <option value="observation">已保存观察</option>
          <option value="session">已保存会话</option>
        </select>
      </label>
      <label v-if="input === 'observation'">观察
        <select v-model="selectedObservation" @change="loadObservationInput">
          <option value="">选择记忆</option>
          <option v-for="item in observations" :key="item.id" :value="item.id">{{ item.title || item.id }}</option>
        </select>
      </label>
      <label v-if="input === 'session'">会话
        <select v-model="selectedSession" @change="loadSessionInput">
          <option value="">选择会话</option>
          <option v-for="item in sessions" :key="item.id" :value="item.id">{{ item.title || item.id }}</option>
        </select>
      </label>
    </div>
    <div class="glasses-shell">
      <div class="hud-stage">
        <video v-show="input === 'live' && !imageUrl" ref="video" autoplay muted playsinline></video>
        <ImageStage v-if="imageUrl" :image-url="imageUrl" :objects="showLabels ? result?.objects ?? [] : []" :loading="busy" />
        <div v-if="input === 'live' && !recording" class="live-placeholder"><p>连接摄像头开始模拟</p></div>
        <span class="hud-rec" :class="{ active: recording }">{{ recording ? '● REC' : 'PAUSED' }}</span>
        <span class="hud-source">{{ input.toUpperCase() }}</span>
        <div v-if="eventMessage" class="hud-event">{{ targetFound ? 'TARGET FOUND · ' : '' }}{{ eventMessage }}</div>
      </div>
      <aside class="hud-panel">
        <button v-if="input === 'live'" class="primary-button" :disabled="recording" @click="connectLive">连接模拟镜头</button>
        <div v-if="input === 'live'" class="analysis-actions">
          <button class="secondary-button" :disabled="!recording || busy" @click="scanLive(false)">分析帧</button>
          <button class="primary-button" :disabled="!recording || busy" @click="scanLive(true)">保存记忆</button>
        </div>
        <label class="find-helper"><input v-model="targetQuery" placeholder="目标物体" /><span :class="targetFound ? 'found-state' : 'not-found-state'">{{ targetFound ? 'FOUND' : 'WAITING' }}</span></label>
        <RelationList v-if="result" :objects="result.objects" :relations="result.relations.slice(0, 6)" />
        <form class="hud-agent" @submit.prevent="askAgent">
          <input v-model="agentQuery" placeholder="询问记忆 Agent" />
          <button>ASK</button>
        </form>
        <p v-if="agentAnswer" class="hud-answer">{{ agentAnswer.answer }}<small>证据 {{ agentAnswer.evidence.length }} 条</small></p>
      </aside>
    </div>
  </section>
</template>
