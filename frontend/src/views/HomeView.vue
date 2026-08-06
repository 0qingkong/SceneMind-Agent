<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  PhArrowRight,
  PhBoundingBox,
  PhBrain,
  PhCamera,
  PhEye,
  PhMagnifyingGlass,
  PhSparkle,
  PhUploadSimple,
} from '@phosphor-icons/vue'

import { apiAssetUrl, getReadiness, listCaptureSessions, listObservations } from '../api/client'
import MemoryCore from '../components/spatial/MemoryCore.vue'
import MetricTile from '../components/ui/MetricTile.vue'
import SafeImage from '../components/SafeImage.vue'
import StatusOrb from '../components/ui/StatusOrb.vue'
import type { CaptureSessionSummary, ObservationSummary, ReadinessResponse } from '../types/api'

const router = useRouter()
const recentMemories = ref<ObservationSummary[]>([])
const recentSessions = ref<CaptureSessionSummary[]>([])
const readiness = ref<ReadinessResponse | null>(null)
const memoryTotal = ref(0)
const sessionTotal = ref(0)
const loading = ref(true)
const dataUnavailable = ref(false)

const latestObservation = computed(() => recentMemories.value[0]?.created_at)
const activeSessions = computed(() => recentSessions.value.filter((item) => item.status === 'active').length || readiness.value?.active_session_count || 0)
const coreState = computed(() => dataUnavailable.value ? 'offline' : loading.value ? 'analyzing' : 'idle')

function formatRelative(value?: string) {
  if (!value) return '暂无记录'
  const delta = Date.now() - new Date(value).getTime()
  if (delta < 60_000) return '刚刚'
  if (delta < 3_600_000) return `${Math.max(1, Math.floor(delta / 60_000))} 分钟前`
  if (delta < 86_400_000) return `${Math.floor(delta / 3_600_000)} 小时前`
  return new Intl.DateTimeFormat('zh-CN', { month: 'short', day: 'numeric' }).format(new Date(value))
}

onMounted(async () => {
  try {
    const [memory, sessions, system] = await Promise.all([
      listObservations({ limit: 3 }),
      listCaptureSessions(),
      getReadiness(),
    ])
    recentMemories.value = memory.items
    memoryTotal.value = memory.total
    recentSessions.value = sessions.items.slice(0, 3)
    sessionTotal.value = sessions.total
    readiness.value = system
  } catch {
    dataUnavailable.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="home-view spatial-home">
    <section class="spatial-hero">
      <div class="hero-narrative">
        <p class="eyebrow">SCENEMIND SPATIAL OS</p>
        <h1>让视觉成为<br /><span>可查询的空间记忆</span></h1>
        <p class="hero-description">观察场景、理解二维关系、形成带时间与图片的记忆，再用真实证据回答“物体最后出现在哪里”。</p>
        <div class="hero-actions">
          <RouterLink class="primary-link" to="/live"><PhCamera :size="18" weight="duotone" />开始实时观察</RouterLink>
          <RouterLink class="secondary-link" to="/agent"><PhSparkle :size="18" weight="duotone" />询问空间记忆</RouterLink>
        </div>
        <div class="hero-secondary-actions">
          <RouterLink to="/analyze"><PhUploadSimple :size="16" />上传场景</RouterLink>
          <RouterLink to="/memory"><PhBrain :size="16" />查看记忆</RouterLink>
        </div>
      </div>

      <div class="hero-core-stage">
        <MemoryCore :state="coreState" interactive @activate="router.push('/live')" />
      </div>

      <aside class="hero-instrument" aria-label="真实系统指标">
        <div class="instrument-header"><span>LIVE INSTRUMENTS</span><StatusOrb :status="dataUnavailable ? 'offline' : 'active'" :label="dataUnavailable ? 'offline' : 'ready'" /></div>
        <MetricTile :value="memoryTotal" label="已保存记忆" detail="来自持久化观察" />
        <MetricTile :value="activeSessions" label="活动会话" :detail="`共 ${sessionTotal} 个会话`" />
        <MetricTile :value="readiness?.analyzer_mode === 'mock' ? 'Mock' : readiness?.analyzer_mode === 'yolo' ? 'YOLO' : '—'" label="当前分析器" :detail="readiness?.model_loaded ? '模型已加载' : '按需加载 / 未连接'" />
        <MetricTile :value="formatRelative(latestObservation)" label="最近观察" detail="真实保存时间" />
      </aside>
    </section>

    <section class="home-section process-board">
      <div class="section-header"><div><p class="eyebrow">SPATIAL MEMORY LOOP</p><h2>从视觉到证据，只需四步</h2></div><RouterLink class="text-link" to="/analyze">进入分析工作台 <PhArrowRight :size="15" /></RouterLink></div>
      <div class="capability-grid">
        <article><span>01</span><PhEye :size="25" weight="duotone" /><h3>看见场景</h3><p>从上传图片或明确授权的浏览器镜头获取静态帧。</p></article>
        <article><span>02</span><PhBoundingBox :size="25" weight="duotone" /><h3>理解关系</h3><p>检测物体，并以二维边界框规则推导可解释关系。</p></article>
        <article><span>03</span><PhBrain :size="25" weight="duotone" /><h3>形成记忆</h3><p>保存图片、物体、地点、来源、关系和时间证据。</p></article>
        <article><span>04</span><PhMagnifyingGlass :size="25" weight="duotone" /><h3>证据检索</h3><p>Agent 调用只读工具，回答并引用原始观察记录。</p></article>
      </div>
    </section>

    <section class="home-section home-data-section">
      <div class="section-header"><div><p class="eyebrow">RECENT EVIDENCE</p><h2>最近空间记忆</h2></div><RouterLink class="text-link" to="/memory">查看全部 <PhArrowRight :size="15" /></RouterLink></div>
      <p v-if="loading" class="memory-status">正在读取最近记忆…</p>
      <div v-else-if="recentMemories.length" class="home-memory-grid">
        <RouterLink v-for="item in recentMemories" :key="item.id" class="home-memory-card surface-card" :to="item.detail_url">
          <SafeImage :src="apiAssetUrl(item.image_url)" :alt="`${item.title || '场景记忆'}缩略图`" />
          <div><span v-if="item.is_demo" class="demo-inline">演示数据</span><strong>{{ item.title || '未命名场景' }}</strong><small>{{ item.location || '未记录地点' }} · {{ item.object_count }} 个物体</small></div>
        </RouterLink>
      </div>
      <div v-else class="home-empty surface-card"><strong>{{ dataUnavailable ? '后端暂不可用' : '还没有保存的记忆' }}</strong><p>{{ dataUnavailable ? '启动后端后可查看真实持久化数据。' : '从实时镜头或场景分析保存第一条证据。' }}</p><RouterLink class="text-link" to="/analyze">开始场景分析</RouterLink></div>
    </section>

    <section class="home-section source-and-proof">
      <div class="source-ports">
        <div class="section-header"><div><p class="eyebrow">CAPTURE PORTS</p><h2>视觉入口</h2></div></div>
        <RouterLink class="source-card surface-card" to="/analyze"><PhUploadSimple :size="22" weight="duotone" /><span>UPLOAD</span><strong>许可图片</strong><p>JPG、PNG、WebP 本地分析。</p></RouterLink>
        <RouterLink class="source-card surface-card" to="/live"><PhCamera :size="22" weight="duotone" /><span>CAMERA</span><strong>浏览器镜头</strong><p>点击后请求权限，不采集音频。</p></RouterLink>
      </div>
      <div class="evaluation-summary surface-card">
        <div class="section-header"><div><p class="eyebrow">DAY 15 EVIDENCE</p><h2>小规模真实评测</h2></div><RouterLink class="text-link" to="/system">系统状态</RouterLink></div>
        <div class="evaluation-metrics">
          <article><strong>10 / 10</strong><span>Memory 精确匹配</span><small>确定性查询集</small></article>
          <article><strong>17 / 18</strong><span>Agent 意图与证据</span><small>94.44%</small></article>
          <article><strong>11 / 12</strong><span>关系人工评审</span><small>91.67% overall precision</small></article>
          <article><strong>6 / 6</strong><span>会话保存决策</span><small>确定性帧序列</small></article>
        </div>
        <p class="boundary-note">以上为小规模 Mock/确定性评测，不代表真实 YOLO 模型准确率。真实 YOLO、手机和眼镜硬件评测仍为未运行。</p>
      </div>
    </section>

    <section class="home-section privacy-boundary surface-card">
      <div><p class="eyebrow">TRUST BOUNDARIES</p><h2>能力边界始终可见</h2></div>
      <ul><li>二维空间关系不代表真实深度或厘米距离。</li><li>同类别历史不保证是同一个现实物体。</li><li>AI Glasses Simulator 是交互预览，不是真实硬件。</li><li>Mock / Profile C 始终明确标记。</li></ul>
      <RouterLink class="secondary-link" to="/privacy">隐私与可信边界</RouterLink>
    </section>
  </section>
</template>
