<script setup lang="ts">
defineProps<{ value: string | number; label: string; detail?: string }>()
</script>

<template>
  <article class="metric-tile"><strong>{{ value }}</strong><span>{{ label }}</span><small v-if="detail">{{ detail }}</small></article>
</template>
