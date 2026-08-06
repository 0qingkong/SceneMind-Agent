<script setup lang="ts">
import type { MemoryCoreState } from '../../composables/useMemoryCoreState'

defineProps<{ state: MemoryCoreState; label: string; detail: string }>()
</script>

<template>
  <div class="core-status-label" :class="`state-${state}`" role="status" aria-live="polite">
    <span><i aria-hidden="true"></i>{{ label }}</span>
    <small>{{ detail }}</small>
  </div>
</template>
