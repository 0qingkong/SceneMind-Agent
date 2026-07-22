<script setup lang="ts">
import { computed } from 'vue'

import type { DetectedObject } from '../types/api'
import { buildObjectDisplayNameMap, objectDisplayName } from '../utils/objectDisplayNames'

const props = defineProps<{ objects: DetectedObject[] }>()
const objectNames = computed(() => buildObjectDisplayNameMap(props.objects))
</script>

<template>
  <div class="object-grid">
    <article v-for="item in objects" :key="item.id" class="object-card">
      <div>
        <strong>{{ objectDisplayName(objectNames, item.id) }}</strong>
        <small>{{ item.label }}</small>
      </div>
      <span>{{ Math.round(item.confidence * 100) }}%</span>
    </article>
  </div>
</template>
