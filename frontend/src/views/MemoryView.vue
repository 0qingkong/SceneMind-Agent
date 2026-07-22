<script setup lang="ts">
import { onMounted, ref } from 'vue'
import axios from 'axios'

import { listObservations } from '../api/client'
import ObservationCard from '../components/ObservationCard.vue'
import type { ObservationSummary } from '../types/api'

const observations = ref<ObservationSummary[]>([])
const total = ref(0)
const loading = ref(false)
const errorMessage = ref('')
const pageSize = 20

async function loadMore(reset = false) {
  loading.value = true
  errorMessage.value = ''
  try {
    const offset = reset ? 0 : observations.value.length
    const response = await listObservations({ limit: pageSize, offset })
    observations.value = reset ? response.items : [...observations.value, ...response.items]
    total.value = response.total
  } catch (error) {
    errorMessage.value = axios.isAxiosError(error)
      ? '无法读取场景记忆，请检查后端。'
      : '发生未知错误。'
  } finally {
    loading.value = false
  }
}

onMounted(() => loadMore(true))
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">SPATIAL MEMORY</p><h1>空间记忆</h1></div>
      <span>{{ total }} Memories</span>
    </div>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <p v-else-if="loading && !observations.length" class="memory-status">正在读取场景记忆…</p>
    <div v-else-if="!observations.length" class="memory-empty">
      <strong class="memory-logo">S</strong>
      <h2>让每一次观测成为可检索的记忆</h2>
      <p>还没有保存的场景。完成一次“分析并记忆”后，物体、关系、时间和图片会出现在这里。</p>
      <RouterLink class="primary-link" to="/analyze">返回场景分析</RouterLink>
    </div>
    <div v-else class="observation-timeline">
      <ObservationCard v-for="item in observations" :key="item.id" :observation="item" />
      <button
        v-if="observations.length < total"
        class="secondary-button load-more-button"
        :disabled="loading"
        @click="loadMore(false)"
      >{{ loading ? '加载中…' : '加载更多' }}</button>
    </div>
  </section>
</template>
