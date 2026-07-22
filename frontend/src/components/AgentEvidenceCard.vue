<script setup lang="ts">
import { apiAssetUrl } from '../api/client'
import type { AgentEvidence } from '../types/api'
import { predicateLabels } from '../utils/relationDisplay'

defineProps<{ evidence: AgentEvidence }>()
</script>

<template>
  <article class="agent-evidence-card">
    <div class="agent-evidence-image">
      <img :src="apiAssetUrl(evidence.image_url)" alt="Agent 回答所依据的场景图片" />
      <span v-if="evidence.is_demo" class="demo-badge">演示数据</span>
    </div>
    <div class="agent-evidence-body">
      <p class="eyebrow">GROUNDED EVIDENCE</p>
      <h3>{{ evidence.title || '未命名场景' }}</h3>
      <small>{{ new Date(evidence.timestamp).toLocaleString('zh-CN') }}</small>
      <span v-if="evidence.location" class="observation-location">{{ evidence.location }}</span>
      <div v-if="evidence.matched_objects.length" class="matched-names">
        <span v-for="name in evidence.matched_objects" :key="name">{{ name }}</span>
      </div>
      <div v-if="evidence.relation_context.length" class="relation-context">
        <p v-for="relation in evidence.relation_context" :key="relation.relation_id">
          {{ relation.subject_name }} {{ predicateLabels[relation.predicate] }} {{ relation.object_name }}
        </p>
      </div>
      <RouterLink class="secondary-link compact-link" :to="evidence.detail_url">打开原始证据</RouterLink>
    </div>
  </article>
</template>
