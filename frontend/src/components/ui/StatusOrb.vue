<script setup lang="ts">
withDefaults(defineProps<{ status?: 'idle' | 'active' | 'warning' | 'offline'; label: string }>(), { status: 'idle' })
</script>

<template>
  <span class="status-orb" :class="`status-${status}`"><i aria-hidden="true"></i>{{ label }}</span>
</template>
