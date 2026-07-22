<script setup lang="ts">
import { onMounted, ref } from 'vue'
import axios from 'axios'

import { getHistory, getLastSeen, listObservations } from '../api/client'
import MemoryMatchCard from '../components/MemoryMatchCard.vue'
import ObservationCard from '../components/ObservationCard.vue'
import type { MemoryMatch, ObservationSummary } from '../types/api'

const observations = ref<ObservationSummary[]>([])
const observationTotal = ref(0)
const searchInput = ref('')
const activeQuery = ref('')
const lastSeen = ref<MemoryMatch | null>(null)
const history = ref<MemoryMatch[]>([])
const historyTotal = ref(0)
const loading = ref(false)
const errorMessage = ref('')
const pageSize = 20

async function loadObservations(reset = false) {
  loading.value = true
  errorMessage.value = ''
  try {
    const offset = reset ? 0 : observations.value.length
    const response = await listObservations({ limit: pageSize, offset })
    observations.value = reset ? response.items : [...observations.value, ...response.items]
    observationTotal.value = response.total
  } catch {
    errorMessage.value = '无法读取场景记忆，请检查后端。'
  } finally {
    loading.value = false
  }
}

async function searchMemory(reset = true) {
  const query = searchInput.value.trim()
  if (!query) {
    activeQuery.value = ''
    lastSeen.value = null
    history.value = []
    await loadObservations(true)
    return
  }
  activeQuery.value = query
  loading.value = true
  errorMessage.value = ''
  try {
    const offset = reset ? 0 : history.value.length
    const [latest, timeline] = await Promise.all([
      reset
        ? getLastSeen(query).then((response) => response.result).catch((error) => {
            if (axios.isAxiosError(error) && error.response?.status === 404) return null
            throw error
          })
        : Promise.resolve(lastSeen.value),
      getHistory(query, { limit: pageSize, offset }),
    ])
    lastSeen.value = latest
    history.value = reset ? timeline.items : [...history.value, ...timeline.items]
    historyTotal.value = timeline.total
  } catch {
    errorMessage.value = '记忆检索失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

onMounted(() => loadObservations(true))
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">SPATIAL MEMORY</p><h1>空间记忆</h1></div>
      <span>{{ activeQuery ? historyTotal : observationTotal }} Memories</span>
    </div>

    <form class="memory-search" @submit.prevent="searchMemory(true)">
      <input v-model="searchInput" placeholder="搜索杯子、电脑、背包……" />
      <button class="primary-button" :disabled="loading">搜索记忆</button>
    </form>

    <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <template v-if="activeQuery">
      <p class="retrieval-disclaimer">按检测标签检索历史观测，不代表跨图片确认是同一个物体。</p>
      <p v-if="loading && !history.length" class="memory-status">正在检索“{{ activeQuery }}”…</p>
      <div v-else-if="!lastSeen" class="memory-empty compact-empty">
        <h2>没有找到“{{ activeQuery }}”</h2>
        <p>可以尝试英文标签、中文名称或更短的关键词。</p>
      </div>
      <template v-else>
        <section class="last-seen-section">
          <h2>最近一次检测到：{{ activeQuery }}</h2>
          <MemoryMatchCard :match="lastSeen" prominent />
        </section>
        <section class="history-section">
          <h2>历史观测</h2>
          <div class="history-timeline">
            <MemoryMatchCard v-for="item in history" :key="item.observation.id" :match="item" />
          </div>
          <button
            v-if="history.length < historyTotal"
            class="secondary-button load-more-button"
            :disabled="loading"
            @click="searchMemory(false)"
          >{{ loading ? '加载中…' : '加载更多历史' }}</button>
        </section>
      </template>
    </template>

    <template v-else>
      <p v-if="loading && !observations.length" class="memory-status">正在读取场景记忆…</p>
      <div v-else-if="!observations.length" class="memory-empty">
        <strong class="memory-logo">S</strong>
        <h2>让每一次观测成为可检索的记忆</h2>
        <p>还没有保存的场景。完成一次“分析并记忆”后，物体、关系、时间和图片会出现在这里。</p>
        <RouterLink class="primary-link" to="/analyze">返回场景分析</RouterLink>
      </div>
      <div v-else class="observation-timeline">
        <ObservationCard v-for="item in observations" :key="item.id" :observation="item" />
        <button
          v-if="observations.length < observationTotal"
          class="secondary-button load-more-button"
          :disabled="loading"
          @click="loadObservations(false)"
        >{{ loading ? '加载中…' : '加载更多' }}</button>
      </div>
    </template>
  </section>
</template>
