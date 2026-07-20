<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import axios from 'axios'

import { analyzeScene } from '../api/client'
import ImageStage from '../components/ImageStage.vue'
import ObjectList from '../components/ObjectList.vue'
import type { AnalyzeResponse } from '../types/api'

const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const result = ref<AnalyzeResponse | null>(null)
const isAnalyzing = ref(false)
const errorMessage = ref('')

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
  selectedFile.value = file
  if (file) previewUrl.value = URL.createObjectURL(file)
}

async function handleAnalyze() {
  if (!selectedFile.value) return
  isAnalyzing.value = true
  errorMessage.value = ''
  result.value = null

  try {
    result.value = await analyzeScene(selectedFile.value)
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
      <span>Day 2</span>
    </div>

    <div class="workspace-grid">
      <section class="workspace-panel">
        <h2>上传场景图片</h2>
        <label v-if="!previewUrl" class="upload-dropzone">
          <input type="file" accept="image/jpeg,image/png,image/webp" @change="handleFileChange" />
          <strong>点击选择图片</strong>
          <small>JPG / PNG / WebP · Max 10 MB</small>
        </label>

        <ImageStage
          v-else
          :image-url="previewUrl"
          :objects="result?.objects ?? []"
          :loading="isAnalyzing"
        />

        <button class="primary-button" :disabled="!canAnalyze" @click="handleAnalyze">
          {{ isAnalyzing ? '分析进行中…' : '开始场景分析' }}
        </button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </section>

      <section class="workspace-panel result-panel">
        <h2>结构化分析结果</h2>

        <template v-if="result">
          <div class="summary-card">{{ result.scene_summary }}</div>
          <div class="metrics-row">
            <div><strong>{{ result.objects.length }}</strong><small>Objects</small></div>
            <div><strong>{{ result.image_width }}×{{ result.image_height }}</strong><small>Resolution</small></div>
            <div><strong>{{ result.latency_ms }}ms</strong><small>Latency</small></div>
          </div>
          <ObjectList :objects="result.objects" />
          <p class="trace">Engine: {{ result.engine }}<br />{{ result.trace_id }}</p>
        </template>

        <div v-else class="empty-result">
          <strong>等待场景分析</strong>
          <p>上传图片后，边界框和结构化结果会出现在这里。</p>
        </div>
      </section>
    </div>
  </section>
</template>
