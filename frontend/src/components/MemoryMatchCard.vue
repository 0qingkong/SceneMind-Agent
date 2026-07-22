<script setup lang="ts">
import { apiAssetUrl } from '../api/client'
import type { MemoryMatch } from '../types/api'
import { predicateLabels } from '../utils/relationDisplay'

defineProps<{
  match: MemoryMatch
  prominent?: boolean
}>()
</script>

<template>
  <article class="memory-match-card" :class="{ prominent }">
    <img :src="apiAssetUrl(match.observation.image_url)" alt="匹配场景缩略图" />
    <div>
      <p v-if="prominent" class="eyebrow">LAST SEEN</p>
      <h3>{{ match.observation.title || '未命名场景' }}</h3>
      <small>{{ new Date(match.observation.created_at).toLocaleString('zh-CN') }}</small>
      <span v-if="match.observation.location" class="observation-location">{{ match.observation.location }}</span>
      <div class="matched-names">
        <span v-for="name in match.matched_names" :key="name">{{ name }}</span>
      </div>
      <div v-if="match.relations.length" class="relation-context">
        <p v-for="relation in match.relations" :key="relation.relation_id">
          {{ relation.subject_name }} {{ predicateLabels[relation.predicate] }} {{ relation.object_name }}
          <small>几何强度 {{ Math.round(relation.score * 100) }}%</small>
        </p>
      </div>
      <RouterLink class="secondary-link compact-link" :to="match.observation.detail_url">打开场景详情</RouterLink>
    </div>
  </article>
</template>
