<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { getInsights } from '../api/client'
import type { InsightsResponse, RankedCount } from '../types/api'

const insights = ref<InsightsResponse | null>(null)
const loading = ref(true)
const errorMessage = ref('')

function width(item: RankedCount, items: RankedCount[]) {
  const maximum = Math.max(1, ...items.map((entry) => entry.count))
  return `${Math.max(5, item.count / maximum * 100)}%`
}

const activityMax = computed(() => Math.max(1, ...(insights.value?.daily_activity.map((item) => item.count) ?? [1])))

onMounted(async () => {
  try {
    insights.value = await getInsights()
  } catch {
    errorMessage.value = '无法读取真实记忆统计。'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section>
    <div class="page-heading">
      <div><p class="eyebrow">MEMORY INSIGHTS</p><h1>空间记忆洞察</h1></div>
      <span>Persisted data</span>
    </div>
    <p v-if="loading" class="memory-status">正在聚合数据…</p>
    <p v-else-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    <div v-else-if="insights && insights.total_observations" class="insights-layout">
      <div class="insight-metrics">
        <article><strong>{{ insights.total_observations }}</strong><span>全部观察</span><small>7 天 {{ insights.observations_7_days }} · 30 天 {{ insights.observations_30_days }}</small></article>
        <article><strong>{{ insights.total_sessions }}</strong><span>采集会话</span><small>{{ insights.active_sessions }} 个仍标记为 active</small></article>
        <article><strong>{{ insights.analyzed_frames }}</strong><span>已分析帧</span><small>{{ insights.sampled_frames }} 采样 · {{ insights.saved_frames }} 保存</small></article>
        <article><strong>{{ Math.round(insights.session_save_efficiency * 100) }}%</strong><span>会话保存效率</span><small>保存帧 / 已分析帧</small></article>
        <article><strong>{{ insights.average_objects }}</strong><span>平均物体</span><small>每条观察</small></article>
        <article><strong>{{ insights.average_relations }}</strong><span>平均关系</span><small>每条观察</small></article>
      </div>
      <section class="insight-card daily-card">
        <h2>最近 30 天活动</h2>
        <div class="daily-chart">
          <span v-for="item in insights.daily_activity" :key="item.date" :title="`${item.date}: ${item.count}`" :style="{ height: `${Math.max(4, item.count / activityMax * 100)}%` }"></span>
        </div>
      </section>
      <div class="insight-grid">
        <section class="insight-card"><h2>常见物体</h2><p v-if="!insights.top_objects.length">暂无</p><div v-for="item in insights.top_objects" :key="item.label" class="rank-row"><span>{{ item.label }}</span><i><b :style="{ width: width(item, insights.top_objects) }"></b></i><strong>{{ item.count }}</strong></div></section>
        <section class="insight-card"><h2>常用位置</h2><p v-if="!insights.top_locations.length">暂无</p><div v-for="item in insights.top_locations" :key="item.label" class="rank-row"><span>{{ item.label }}</span><i><b :style="{ width: width(item, insights.top_locations) }"></b></i><strong>{{ item.count }}</strong></div></section>
        <section class="insight-card"><h2>采集来源</h2><p v-if="!insights.top_sources.length">暂无</p><div v-for="item in insights.top_sources" :key="item.label" class="rank-row"><span>{{ item.label }}</span><i><b :style="{ width: width(item, insights.top_sources) }"></b></i><strong>{{ item.count }}</strong></div></section>
        <section class="insight-card"><h2>来源设备</h2><p v-if="!insights.top_devices.length">暂无设备名称</p><div v-for="item in insights.top_devices" :key="item.label" class="rank-row"><span>{{ item.label }}</span><i><b :style="{ width: width(item, insights.top_devices) }"></b></i><strong>{{ item.count }}</strong></div></section>
      </div>
      <section v-if="insights.recent_sessions.length" class="insight-card"><h2>最近会话</h2><div class="recent-session-links"><RouterLink v-for="item in insights.recent_sessions" :key="item.id" :to="`/sessions/${item.id}`"><strong>{{ item.title || '未命名会话' }}</strong><span>{{ item.saved_observations }} 保存 / {{ item.analyzed_frames }} 分析</span></RouterLink></div></section>
    </div>
    <div v-else class="memory-empty compact-empty"><h2>还没有可聚合的记忆</h2><p>保存场景或运行观察会话后，这里会使用真实持久化数据生成统计。</p><RouterLink class="primary-link" to="/live">打开实时镜头</RouterLink></div>
  </section>
</template>
