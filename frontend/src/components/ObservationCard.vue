<script setup lang="ts">
import { apiAssetUrl } from '../api/client'
import type { ObservationSummary } from '../types/api'

defineProps<{ observation: ObservationSummary }>()

function formattedTime(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}
</script>

<template>
  <RouterLink class="observation-card" :to="observation.detail_url">
    <img :src="apiAssetUrl(observation.image_url)" alt="场景记忆缩略图" />
    <div class="observation-card-body">
      <div class="observation-card-heading">
        <strong>{{ observation.title || '未命名场景' }}</strong>
        <div><span v-if="observation.is_demo" class="demo-inline">演示</span><small>{{ formattedTime(observation.created_at) }}</small></div>
      </div>
      <span v-if="observation.location" class="observation-location">{{ observation.location }}</span>
      <p>{{ observation.summary }}</p>
      <div class="observation-labels">
        <span v-for="label in observation.labels.slice(0, 5)" :key="label">{{ label }}</span>
      </div>
      <small>{{ observation.object_count }} 个物体 · {{ observation.relation_count }} 条关系 · {{ observation.source_device_name || observation.source_type || 'upload' }}</small>
    </div>
  </RouterLink>
</template>
