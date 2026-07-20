<script setup lang="ts">
import type { DetectedObject } from '../types/api'

defineProps<{ objects: DetectedObject[] }>()
</script>

<template>
  <div class="object-grid">
    <article v-for="item in objects" :key="item.id" class="object-card">
      <div>
        <strong>{{ item.display_name }}</strong>
        <small>{{ item.label }}</small>
      </div>
      <span>{{ Math.round(item.confidence * 100) }}%</span>
    </article>
  </div>
</template>
