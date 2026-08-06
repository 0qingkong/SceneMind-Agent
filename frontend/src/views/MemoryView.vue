<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import axios from 'axios'
import { PhGridFour, PhRows } from '@phosphor-icons/vue'

import { getHistory, getLastSeen, listObservations } from '../api/client'
import MemoryMatchCard from '../components/MemoryMatchCard.vue'
import ObservationCard from '../components/ObservationCard.vue'
import MemoryCore from '../components/spatial/MemoryCore.vue'
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
const locationFilter = ref('')
const sourceFilter = ref('')
const sessionFilter = ref('')
const timeFilter = ref<'all' | '7' | '30'>('all')
const pageSize = 100
const viewMode = ref<'grid' | 'timeline'>('grid')

const locations = computed(() => [...new Set(observations.value.map((item) => item.location).filter(Boolean) as string[])].sort())
const sources = computed(() => [...new Set(observations.value.map((item) => item.source_type).filter(Boolean) as string[])].sort())
const sessions = computed(() => [...new Set(observations.value.map((item) => item.session_id).filter(Boolean) as string[])])
const filtersActive = computed(() => Boolean(locationFilter.value || sourceFilter.value || sessionFilter.value || timeFilter.value !== 'all'))
const visibleObservations = computed(() => observations.value.filter((item) => {
  const days = timeFilter.value === 'all' ? null : Number(timeFilter.value)
  const after = days ? Date.now() - days * 86400000 : null
  return (!locationFilter.value || item.location === locationFilter.value)
    && (!sourceFilter.value || item.source_type === sourceFilter.value)
    && (!sessionFilter.value || item.session_id === sessionFilter.value)
    && (!after || new Date(item.created_at).getTime() >= after)
}))

function sourceName(value: string) {
  return ({ upload: '图片上传', browser_camera: '浏览器摄像头', demo_seed: '演示数据', glasses_simulator: '眼镜模拟器' } as Record<string, string>)[value] ?? value
}

function clearFilters() {
  locationFilter.value = ''
  sourceFilter.value = ''
  sessionFilter.value = ''
  timeFilter.value = 'all'
}

async function loadObservations() {
  loading.value = true
  errorMessage.value = ''
  try {
    const response = await listObservations({ limit: pageSize, offset: 0 })
    observations.value = response.items
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
    await loadObservations()
    return
  }
  activeQuery.value = query
  loading.value = true
  errorMessage.value = ''
  try {
    const offset = reset ? 0 : history.value.length
    const [latest, timeline] = await Promise.all([
      reset ? getLastSeen(query).then((response) => response.result).catch((error) => {
        if (axios.isAxiosError(error) && error.response?.status === 404) return null
        throw error
      }) : Promise.resolve(lastSeen.value),
      getHistory(query, { limit: 20, offset }),
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

async function clearSearch() {
  searchInput.value = ''
  activeQuery.value = ''
  lastSeen.value = null
  history.value = []
  await loadObservations()
}

onMounted(loadObservations)
</script>

<template>
  <section class="memory-view">
    <div class="page-heading"><div><p class="eyebrow">SPATIAL MEMORY</p><h1>空间记忆</h1></div><div class="memory-heading-tools"><span>{{ activeQuery ? historyTotal : observationTotal }} 条记忆</span><div class="view-toggle" aria-label="记忆视图"><button :class="{ active: viewMode === 'grid' }" aria-label="网格视图" @click="viewMode = 'grid'"><PhGridFour :size="17" /></button><button :class="{ active: viewMode === 'timeline' }" aria-label="时间线视图" @click="viewMode = 'timeline'"><PhRows :size="17" /></button></div></div></div>
    <form class="memory-search" role="search" @submit.prevent="searchMemory(true)">
      <label class="sr-only" for="memory-query">按物体类别搜索记忆</label>
      <input id="memory-query" v-model="searchInput" placeholder="搜索杯子、电脑、背包……" />
      <button class="primary-button" :disabled="loading">搜索记忆</button>
      <button v-if="activeQuery || searchInput" class="secondary-button" type="button" :disabled="loading" @click="clearSearch">清空搜索</button>
    </form>
    <p class="search-guidance">按检测类别搜索；类别匹配不代表跨图片确认是同一个现实物体。</p>

    <section v-if="!activeQuery && observations.length" class="memory-filter-panel surface-card" aria-label="记忆筛选">
      <label>地点<select v-model="locationFilter"><option value="">全部地点</option><option v-for="item in locations" :key="item" :value="item">{{ item }}</option></select></label>
      <label>来源<select v-model="sourceFilter"><option value="">全部来源</option><option v-for="item in sources" :key="item" :value="item">{{ sourceName(item) }}</option></select></label>
      <label>会话<select v-model="sessionFilter"><option value="">全部会话</option><option v-for="item in sessions" :key="item" :value="item">{{ item.slice(0, 8) }}…</option></select></label>
      <label>时间<select v-model="timeFilter"><option value="all">全部时间</option><option value="7">最近 7 天</option><option value="30">最近 30 天</option></select></label>
      <button class="text-button" :disabled="!filtersActive" @click="clearFilters">清空筛选</button>
    </section>

    <div v-if="errorMessage" class="state-message state-error" role="alert"><p>{{ errorMessage }}</p><button class="secondary-button" @click="activeQuery ? searchMemory(true) : loadObservations()">重试</button></div>
    <template v-if="activeQuery">
      <p class="retrieval-disclaimer">按检测标签检索历史观测，不代表跨图片确认是同一个物体。</p>
      <p v-if="loading && !history.length" class="memory-status">正在检索“{{ activeQuery }}”…</p>
      <div v-else-if="!lastSeen" class="memory-empty compact-empty"><h2>没有找到“{{ activeQuery }}”</h2><p>可以尝试英文标签、中文名称或更短的关键词。</p></div>
      <template v-else>
        <section class="last-seen-section"><h2>最近一次检测到：{{ activeQuery }}</h2><MemoryMatchCard :match="lastSeen" prominent /></section>
        <section class="history-section"><h2>历史观测</h2><div class="history-timeline"><MemoryMatchCard v-for="item in history" :key="item.observation.id" :match="item" /></div><button v-if="history.length < historyTotal" class="secondary-button load-more-button" :disabled="loading" @click="searchMemory(false)">{{ loading ? '加载中…' : '加载更多历史' }}</button></section>
      </template>
    </template>

    <template v-else>
      <p v-if="loading && !observations.length" class="memory-status">正在读取场景记忆…</p>
      <div v-else-if="!observations.length && !errorMessage" class="memory-empty memory-core-empty"><MemoryCore state="idle" compact /><h2>让每一次观测成为可检索的记忆</h2><p>还没有保存的场景。完成一次“分析并记忆”后，物体、关系、时间和图片会出现在这里。</p><RouterLink class="primary-link" to="/analyze">开始场景分析</RouterLink></div>
      <div v-else-if="!visibleObservations.length" class="memory-empty compact-empty"><h2>没有符合筛选条件的记忆</h2><p>清空筛选后可以查看已加载的最近 {{ observations.length }} 条记录。</p><button class="secondary-button" @click="clearFilters">清空筛选</button></div>
      <div v-else class="observation-collection" :class="`view-${viewMode}`"><ObservationCard v-for="item in visibleObservations" :key="item.id" :observation="item" /><p v-if="observationTotal > observations.length" class="search-guidance">当前筛选覆盖最近 {{ observations.length }} 条记录，共 {{ observationTotal }} 条。</p></div>
    </template>
  </section>
</template>
