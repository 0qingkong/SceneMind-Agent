<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

import { queryAgent } from '../api/client'
import AgentEvidenceCard from '../components/AgentEvidenceCard.vue'
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
  <section>
    <div class="page-heading agent-heading">
      <div><p class="eyebrow">GROUNDED MEMORY AGENT</p><h1>询问你的场景记忆</h1></div>
      <span>Evidence first</span>
    </div>

    <form class="agent-query" @submit.prevent="ask()">
      <label for="agent-question">只回答已保存场景中的物体、时间、位置和二维关系</label>
      <div>
        <input id="agent-question" v-model="query" maxlength="500" placeholder="例如：我的杯子最后出现在哪里？" />
        <button class="primary-button" :disabled="loading || !query.trim()">
          {{ loading ? '正在查找证据…' : '询问 Agent' }}
        </button>
      </div>
    </form>

    <div class="example-chips" aria-label="示例问题">
      <button v-for="example in examples" :key="example" :disabled="loading" @click="ask(example)">{{ example }}</button>
    </div>

    <p v-if="errorMessage" class="error-message agent-error">{{ errorMessage }}</p>
    <div v-if="loading" class="agent-loading"><span></span><p>正在规划检索并核对观察证据…</p></div>

    <template v-else-if="result">
      <section class="agent-answer-card">
        <div><span>{{ result.intent }}</span><strong>基于 {{ result.evidence.length }} 条观察证据</strong></div>
        <p>{{ result.answer }}</p>
        <ul v-if="result.limitations.length">
          <li v-for="item in result.limitations" :key="item">{{ item }}</li>
        </ul>
      </section>

      <section v-if="result.evidence.length" class="agent-evidence-section">
        <div class="section-heading"><h2>回答证据</h2><span>{{ result.evidence.length }}</span></div>
        <div class="agent-evidence-grid">
          <AgentEvidenceCard v-for="item in result.evidence" :key="item.observation_id" :evidence="item" />
        </div>
      </section>
      <div v-else class="memory-empty compact-empty agent-empty">
        <h2>没有可展示的场景证据</h2>
        <p>Agent 不会在记忆为空或问题超出范围时猜测答案。请先保存场景，或尝试上方示例。</p>
      </div>

      <details class="tool-trace">
        <summary>查看工具执行轨迹</summary>
        <article v-for="(step, index) in result.tool_steps" :key="`${step.tool}-${index}`">
          <strong>{{ step.tool }}</strong><span>{{ step.status }} · {{ step.result_count }}</span>
          <code>{{ JSON.stringify(step.arguments) }}</code>
        </article>
      </details>
    </template>

    <div v-else class="agent-welcome">
      <strong>答案必须有据可查</strong>
      <p>每个回答都会显示对应场景图片、时间、位置和详情入口；不支持开放领域聊天。</p>
    </div>
  </section>
</template>
