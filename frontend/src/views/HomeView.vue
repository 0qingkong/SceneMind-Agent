<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { apiAssetUrl, listCaptureSessions, listObservations } from '../api/client'
import SafeImage from '../components/SafeImage.vue'
import type { CaptureSessionSummary, ObservationSummary } from '../types/api'

const recentMemories = ref<ObservationSummary[]>([])
const recentSessions = ref<CaptureSessionSummary[]>([])
const loading = ref(true)
const dataUnavailable = ref(false)

onMounted(async () => {
  try {
    const [memory, sessions] = await Promise.all([
      listObservations({ limit: 3 }),
      listCaptureSessions(),
    ])
    recentMemories.value = memory.items
    recentSessions.value = sessions.items.slice(0, 3)
  } catch {
    dataUnavailable.value = true
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="home-view">
    <div class="hero-layout">
      <div>
        <p class="eyebrow">EVIDENCE-BACKED SPATIAL MEMORY</p>
        <h1>让视觉场景<br />成为可查询的记忆</h1>
        <p class="hero-description">
          SceneMind 是一个面向手机摄像头与未来 AI 眼镜的空间记忆智能体，可从视觉场景中检测物体、推导二维关系、形成长期记忆，并通过自然语言查询返回时间、地点和原始图片证据。
        </p>
        <div class="hero-actions">
          <RouterLink class="primary-link" to="/live">开始实时观察</RouterLink>
          <RouterLink class="secondary-link" to="/agent">询问空间记忆 Agent</RouterLink>
        </div>
      </div>
      <aside class="hero-trust-card surface-card">
        <span class="status-pill status-success">证据优先</span>
        <strong>回答来自已保存观察</strong>
        <p>每条结论都可回到时间、地点、物体框和原始场景图片。</p>
        <div><span>当前能力</span><b>上传 · 浏览器镜头 · 本地记忆</b></div>
        <div><span>可信边界</span><b>二维几何 · 类别检索 · 非身份识别</b></div>
      </aside>
    </div>

    <section class="home-section">
      <div class="section-header"><div><p class="eyebrow">PRODUCT LOOP</p><h2>四步形成空间记忆</h2></div></div>
      <div class="capability-grid">
        <article><span>01</span><h3>看见场景</h3><p>从上传或明确授权的浏览器镜头获得静态图像。</p></article>
        <article><span>02</span><h3>理解关系</h3><p>检测物体，并从二维边界框推导可解释关系。</p></article>
        <article><span>03</span><h3>形成记忆</h3><p>持久化图片、物体、关系、地点、来源和时间。</p></article>
        <article><span>04</span><h3>证据化检索</h3><p>Agent 调用只读工具，返回答案和原始图片证据。</p></article>
      </div>
    </section>

    <section class="home-section">
      <div class="section-header"><div><p class="eyebrow">CAPTURE SOURCES</p><h2>多来源视觉采集</h2></div><RouterLink class="text-link" to="/devices">查看设备中心</RouterLink></div>
      <div class="source-grid">
        <RouterLink class="source-card surface-card" to="/analyze"><span>UPLOAD</span><strong>本地图片</strong><p>使用拥有许可的 JPG、PNG 或 WebP。</p></RouterLink>
        <RouterLink class="source-card surface-card" to="/live"><span>CAMERA</span><strong>手机 / 电脑镜头</strong><p>用户点击后才请求权限，且不采集音频。</p></RouterLink>
        <RouterLink class="source-card simulator-source surface-card" to="/glasses"><span>SIMULATOR</span><strong>AI Glasses Simulator</strong><p>未来设备交互预览，不代表真实硬件已连接。</p></RouterLink>
      </div>
    </section>

    <section class="home-section home-data-section">
      <div class="section-header"><div><p class="eyebrow">RECENT EVIDENCE</p><h2>最近空间记忆</h2></div><RouterLink class="text-link" to="/memory">查看全部</RouterLink></div>
      <p v-if="loading" class="memory-status">正在读取最近记忆…</p>
      <div v-else-if="recentMemories.length" class="home-memory-grid">
        <RouterLink v-for="item in recentMemories" :key="item.id" class="home-memory-card surface-card" :to="item.detail_url">
          <SafeImage :src="apiAssetUrl(item.image_url)" :alt="`${item.title || '场景记忆'}缩略图`" />
          <div><span v-if="item.is_demo" class="demo-inline">演示数据</span><strong>{{ item.title || '未命名场景' }}</strong><small>{{ item.location || '未记录地点' }} · {{ item.object_count }} 个物体</small></div>
        </RouterLink>
      </div>
      <div v-else class="home-empty surface-card"><strong>{{ dataUnavailable ? '后端暂不可用' : '还没有保存的记忆' }}</strong><p>{{ dataUnavailable ? '启动后端后可查看真实持久化数据。' : '从实时镜头或场景分析保存第一条证据。' }}</p><RouterLink class="text-link" to="/analyze">开始场景分析</RouterLink></div>
    </section>

    <section class="home-section home-data-section">
      <div class="section-header"><div><p class="eyebrow">SEQUENTIAL OBSERVATION</p><h2>最近观察会话</h2></div><RouterLink class="text-link" to="/sessions">管理会话</RouterLink></div>
      <div v-if="recentSessions.length" class="home-session-list surface-card">
        <RouterLink v-for="item in recentSessions" :key="item.id" :to="`/sessions/${item.id}`">
          <span class="session-status" :class="item.status">{{ item.status === 'active' ? '运行中' : item.status === 'failed' ? '失败' : '已停止' }}</span>
          <strong>{{ item.title || '未命名观察会话' }}</strong>
          <small>{{ item.analyzed_frames }} 分析 · {{ item.saved_observations }} 保存</small>
        </RouterLink>
      </div>
      <div v-else-if="!loading" class="home-empty surface-card"><strong>还没有观察会话</strong><p>低频顺序采样只保存有意义的变化，不是逐帧视频推理。</p></div>
    </section>

    <section class="home-section evaluation-summary surface-card">
      <div class="section-header"><div><p class="eyebrow">DAY 15 EVIDENCE</p><h2>真实评测摘要</h2></div><RouterLink class="text-link" to="/system">系统状态</RouterLink></div>
      <div class="evaluation-metrics">
        <article><strong>10 / 10</strong><span>Memory 精确匹配</span><small>确定性查询集</small></article>
        <article><strong>17 / 18</strong><span>Agent 意图与证据</span><small>94.44%</small></article>
        <article><strong>11 / 12</strong><span>关系人工评审</span><small>91.67% overall precision</small></article>
        <article><strong>6 / 6</strong><span>会话保存决策</span><small>确定性帧序列</small></article>
      </div>
      <p class="boundary-note">以上为小规模 Mock/确定性评测，不代表真实 YOLO 模型准确率。真实 YOLO、手机和眼镜硬件评测仍为未运行。</p>
    </section>

    <section class="home-section privacy-boundary surface-card">
      <div><p class="eyebrow">PRIVACY & LIMITS</p><h2>只陈述已实现能力</h2></div>
      <ul><li>摄像头仅在用户明确点击后启用，不采集麦克风。</li><li>空间关系来自二维边界框，不代表真实深度或厘米距离。</li><li>类别历史不等于确认是同一个现实物体，也不做人脸识别。</li><li>AI Glasses Simulator 是浏览器模拟，不是商业眼镜硬件接入。</li></ul>
      <RouterLink class="secondary-link" to="/privacy">查看隐私与可信边界</RouterLink>
    </section>
  </section>
</template>
