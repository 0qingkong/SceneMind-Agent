<script setup lang="ts">
withDefaults(defineProps<{ as?: string; tone?: 'default' | 'soft' | 'inverse' }>(), { as: 'section', tone: 'default' })
</script>

<template>
  <component :is="as" class="spatial-panel" :class="`tone-${tone}`"><slot /></component>
</template>
