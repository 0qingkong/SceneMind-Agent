<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'
import { analyzeScene } from './api/client'
import type { AnalyzeResponse } from './types/api'

const selectedFile = ref<File | null>(null)
const previewUrl = ref('')
const result = ref<AnalyzeResponse | null>(null)
const isAnalyzing = ref(false)
const errorMessage = ref('')

const canAnalyze = computed(() => selectedFile.value !== null && !isAnalyzing.value)

function clearPreview(): void {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
    previewUrl.value = ''
  }
}

function handleFileChange(event: Event): void {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] ?? null

  clearPreview()
  result.value = null
  errorMessage.value = ''
  selectedFile.value = file

  if (file) {
    previewUrl.value = URL.createObjectURL(file)
  }
}

async function handleAnalyze(): Promise<void> {
  if (!selectedFile.value) return

  isAnalyzing.value = true
  errorMessage.value = ''
  result.value = null

  try {
    result.value = await analyzeScene(selectedFile.value)
  } catch (error) {
    console.error(error)
    errorMessage.value = '分析失败。请确认 FastAPI 后端已在 8000 端口启动。'
  } finally {
    isAnalyzing.value = false
  }
}

onBeforeUnmount(clearPreview)
</script>

<template>
  <main class="app-shell">
    <section class="hero">
      <div class="brand-row">
        <div class="brand-mark">S</div>
        <span>SceneMind Agent</span>
      </div>

      <p class="eyebrow">MULTIMODAL SPATIAL MEMORY</p>
      <h1>让 AI 记住<br />物品最后出现的位置</h1>
      <p class="hero-copy">
        上传一张场景图片，系统将识别物体、理解空间关系，并逐步构建可检索的场景记忆。
      </p>
    </section>

    <section class="panel">
      <div class="step-heading">
        <span>01</span>
        <div>
          <h2>上传场景图片</h2>
          <p>支持 JPG、PNG、WebP，单张不超过 10 MB。</p>
        </div>
      </div>

      <label class="upload-area">
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          @change="handleFileChange"
        />
        <img v-if="previewUrl" :src="previewUrl" alt="待分析场景预览" />
        <div v-else class="upload-placeholder">
          <strong>点击选择图片</strong>
          <span>建议先使用书桌、宿舍或办公室场景</span>
        </div>
      </label>

      <button class="primary-button" :disabled="!canAnalyze" @click="handleAnalyze">
        {{ isAnalyzing ? '正在分析…' : '开始分析' }}
      </button>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </section>

    <section v-if="result" class="panel result-panel">
      <div class="step-heading">
        <span>02</span>
        <div>
          <h2>场景分析结果</h2>
          <p>{{ result.engine }} · {{ result.latency_ms }} ms</p>
        </div>
      </div>

      <div class="summary-card">
        <span>场景总结</span>
        <p>{{ result.scene_summary }}</p>
      </div>

      <div class="object-list">
        <article v-for="item in result.objects" :key="item.id" class="object-card">
          <div>
            <strong>{{ item.display_name }}</strong>
            <small>{{ item.label }}</small>
          </div>
          <span>{{ Math.round(item.confidence * 100) }}%</span>
        </article>
      </div>

      <p class="trace">Trace ID：{{ result.trace_id }}</p>
    </section>

    <footer>
      Day 1：先打通可靠闭环，再替换为真实视觉模型。
    </footer>
  </main>
</template>
