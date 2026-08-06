<script setup lang="ts">
import { computed, ref } from 'vue'
import axios from 'axios'

import { queryAgent } from '../api/client'
import AgentEvidenceCard from '../components/AgentEvidenceCard.vue'
import MemoryCore from '../components/spatial/MemoryCore.vue'
import type { AgentQueryResponse } from '../types/api'

const examples = [
  '我的杯子最后出现在哪里？',
  '最近在哪些场景里见过人物？',
  '展示最近两条场景记忆',
  '图书馆那条记录里有什么？',
  '一共检测到多少把椅子？',
]

const query = ref('')
const loading = ref(false)
const errorMessage = ref('')
const result = ref<AgentQueryResponse | null>(null)
const intentLabels: Record<string, string> = {
  last_seen: '最近出现', history: '历史记录', recent_observations: '最近观察',
  observation_detail: '观察详情', object_count: '物体计数', help: '使用帮助', unknown: '超出支持范围',
}
const toolLabels: Record<string, string> = {
  memory_last_seen: '查询最近出现', memory_history: '查询历史记录', list_recent_observations: '读取最近观察',
  get_observation_detail: '读取观察详情', count_objects: '统计物体', none: '未调用工具',
}
const unsupported = computed(() => result.value?.intent === 'unknown')

async function ask(value?: string) {
  if (value) query.value = value
  const cleaned = query.value.trim()
  if (!cleaned || loading.value) return
  loading.value = true
  errorMessage.value = ''
  result.value = null
  try {
    result.value = await queryAgent(cleaned)
  } catch (error) {
    errorMessage.value = axios.isAxiosError(error) && typeof error.response?.data?.detail === 'string'
      ? error.response.data.detail
      : 'Agent 暂时无法读取场景记忆，请检查后端。'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="agent-view">
    <div class="page-heading agent-heading">
      <div><p class="eyebrow">GROUNDED MEMORY AGENT</p><h1>询问你的场景记忆</h1></div>
      <span>Evidence first</span>
    </div>

    <div class="agent-spatial-layout">
      <section class="agent-dialogue-panel">
        <form class="agent-query" @submit.prevent="ask()">
          <label for="agent-question">只回答已保存场景中的物体、时间、位置和二维关系</label>
          <div><input id="agent-question" v-model="query" maxlength="500" placeholder="例如：我的杯子最后出现在哪里？" /><button class="primary-button" :disabled="loading || !query.trim()">{{ loading ? '正在查找证据…' : '询问 Agent' }}</button></div>
        </form>

        <aside class="agent-scope-note surface-card"><strong>Agent 只查询已保存证据</strong><span>支持最近出现、历史、观察详情、最近记忆和物体计数；不回答天气、身份识别、真实深度或厘米距离。</span></aside>
        <div class="example-chips" aria-label="示例问题"><button v-for="example in examples" :key="example" :disabled="loading" @click="ask(example)">{{ example }}</button></div>
        <p v-if="errorMessage" class="error-message agent-error">{{ errorMessage }}</p>
        <div v-if="loading" class="agent-loading"><span></span><p>正在请求记忆工具并核对观察证据…</p></div>

        <section v-else-if="result" class="agent-answer-card" :class="{ 'unsupported-answer': unsupported }">
          <div><span>{{ intentLabels[result.intent] }}</span><strong>{{ unsupported ? '未调用记忆工具' : `基于 ${result.evidence.length} 条观察证据` }}</strong></div>
          <p>{{ result.answer }}</p>
        </section>
        <div v-else class="agent-welcome"><strong>答案必须有据可查</strong><p>每个回答都会显示对应场景图片、时间、位置和详情入口；不支持开放领域聊天。</p></div>
      </section>

      <aside class="agent-evidence-workspace">
        <section v-if="result?.evidence.length" class="agent-evidence-section">
          <div class="section-heading"><div><p class="eyebrow">GROUNDED EVIDENCE</p><h2>回答证据</h2></div><span>{{ result.evidence.length }}</span></div>
          <div class="agent-evidence-grid"><AgentEvidenceCard v-for="item in result.evidence" :key="item.observation_id" :evidence="item" /></div>
        </section>
        <div v-else-if="result" class="memory-empty compact-empty agent-empty" :class="{ 'unsupported-empty': unsupported }"><h2>{{ unsupported ? '这个问题超出当前支持范围' : '没有找到匹配的场景证据' }}</h2><p>{{ unsupported ? 'SceneMind 不会把开放领域知识或物理距离伪装成空间记忆答案。' : 'Agent 不会在记忆为空时猜测答案。请先保存场景，或换一个检测类别。' }}</p></div>
        <div v-else class="agent-core-empty"><MemoryCore :state="loading ? 'retrieving' : 'idle'" compact /><p>提出问题后，真实工具调用与场景证据会在这里展开。</p></div>

        <details v-if="result" class="tool-trace">
          <summary>工具执行轨迹 · {{ intentLabels[result.intent] }}</summary>
          <article v-for="(step, index) in result.tool_steps" :key="`${step.tool}-${index}`"><i aria-hidden="true"></i><strong>{{ toolLabels[step.tool] || step.tool }}</strong><span>{{ step.status === 'success' ? '成功' : step.status === 'no_match' ? '无匹配' : '已跳过' }} · {{ step.result_count }} 条</span><code>{{ JSON.stringify(step.arguments) }}</code></article>
        </details>
        <section v-if="result?.limitations.length" class="boundary-card surface-card"><h2>能力边界</h2><ul><li v-for="item in result.limitations" :key="item">{{ item }}</li></ul><p>类别匹配不等于确认是同一个现实物体。</p></section>
      </aside>
    </div>
  </section>
</template>
