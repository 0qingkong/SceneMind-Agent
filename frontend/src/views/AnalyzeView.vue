<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import axios from 'axios'

import { analyzeScene, createObservation } from '../api/client'
import ImageStage from '../components/ImageStage.vue'
import ObjectList from '../components/ObjectList.vue'
import RelationList from '../components/RelationList.vue'
import type { AnalyzeResponse, ObservationDetail } from '../types/api'

const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const result = ref<AnalyzeResponse | null>(null)
const isAnalyzing = ref(false)
const errorMessage = ref('')
const sceneTitle = ref('')
const sceneLocation = ref('')
const savedObservation = ref<ObservationDetail | null>(null)

const canAnalyze = computed(() => selectedFile.value !== null && !isAnalyzing.value)

function clearPreview() {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] ?? null
  clearPreview()
  result.value = null
  errorMessage.value = ''
  savedObservation.value = null
  selectedFile.value = file
  if (file) previewUrl.value = URL.createObjectURL(file)
}

function observationAsAnalysis(observation: ObservationDetail): AnalyzeResponse {
  return {
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
}

async function handleAnalyze(remember: boolean) {
  if (!selectedFile.value) return
  isAnalyzing.value = true
  errorMessage.value = ''
  result.value = null
  savedObservation.value = null

  try {
    if (remember) {
      const observation = await createObservation(
        selectedFile.value,
        sceneTitle.value,
        sceneLocation.value,
      )
      savedObservation.value = observation
      result.value = observationAsAnalysis(observation)
    } else {
      result.value = await analyzeScene(selectedFile.value)
    }
  } catch (error) {
    if (axios.isAxiosError(error)) {
      errorMessage.value =
        typeof error.response?.data?.detail === 'string'
          ? error.response.data.detail
          : '分析接口不可用，请检查后端。'
    } else {
      errorMessage.value = '发生未知错误。'
    }
  } finally {
    isAnalyzing.value = false
  }
}

onBeforeUnmount(clearPreview)
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">SCENE ANALYSIS</p><h1>场景分析工作台</h1></div>
      <span>检测 · 推理 · 记忆</span>
    </div>

    <div class="workspace-grid">
      <section class="workspace-panel">
        <h2>上传并建立场景记忆</h2>
        <p class="panel-description">图片只会在你点击分析后发送至后端。请使用拥有许可的场景图片。</p>
        <label v-if="!previewUrl" class="upload-dropzone">
          <input type="file" accept="image/jpeg,image/png,image/webp" @change="handleFileChange" />
          <strong>点击选择图片</strong>
          <small>JPG / PNG / WebP · 最大 10 MB</small>
        </label>

        <ImageStage
          v-else
          :image-url="previewUrl"
          :objects="result?.objects ?? []"
          :loading="isAnalyzing"
        />

        <div class="scene-fields">
          <label>场景标题<input v-model="sceneTitle" maxlength="200" placeholder="例如：实验室桌面（可选）" /></label>
          <label>地点<input v-model="sceneLocation" maxlength="200" placeholder="例如：图书馆二层（可选）" /></label>
        </div>
        <div class="analysis-actions">
          <button class="secondary-button" :disabled="!canAnalyze" @click="handleAnalyze(false)">仅查看检测结果</button>
          <button class="primary-button" :disabled="!canAnalyze" @click="handleAnalyze(true)">
            {{ isAnalyzing ? '正在检测与推理…' : '分析并保存到记忆' }}
          </button>
        </div>
        <div v-if="errorMessage" class="state-message state-error" role="alert"><p>{{ errorMessage }}</p><button class="secondary-button" :disabled="!canAnalyze" @click="handleAnalyze(false)">重试分析</button></div>
        <p v-if="savedObservation" class="success-message">
          已保存到场景记忆 · <RouterLink :to="savedObservation.detail_url">查看详情</RouterLink>
        </p>
      </section>

      <section class="workspace-panel result-panel">
        <h2>结构化分析结果</h2>

        <template v-if="result">
          <div class="summary-card">{{ result.scene_summary }}</div>
          <div class="metrics-row">
            <div><strong>{{ result.objects.length }}</strong><small>检测物体</small></div>
            <div><strong>{{ result.image_width }}×{{ result.image_height }}</strong><small>图像分辨率</small></div>
            <div v-if="savedObservation"><strong>已保存</strong><small>记忆状态</small></div>
            <div v-else><strong>{{ result.latency_ms }}ms</strong><small>端到端耗时</small></div>
          </div>
          <div class="analysis-meta"><span>分析器：{{ result.engine }}</span><span>最高置信度：{{ result.objects.length ? Math.round(Math.max(...result.objects.map((item) => item.confidence)) * 100) : 0 }}%</span><span>关系：{{ result.relations.length }} 条</span></div>
          <ObjectList :objects="result.objects" />
          <RelationList :objects="result.objects" :relations="result.relations" />
          <p class="trace">分析追踪 ID：{{ result.trace_id }}</p>
          <p class="boundary-note">二维关系仅来自边界框几何；类别检测不确认现实中的物体身份。</p>
        </template>

        <div v-else class="empty-result">
          <strong>等待场景分析</strong>
          <p>上传图片后，边界框和结构化结果会出现在这里。</p>
        </div>
      </section>
    </div>
  </section>
</template>
