<script setup lang="ts">
withDefaults(defineProps<{ variant?: 'primary' | 'secondary'; disabled?: boolean; type?: 'button' | 'submit' }>(), { variant: 'primary', type: 'button' })
</script>

<template>
  <button :type="type" class="aurora-button" :class="`variant-${variant}`" :disabled="disabled"><slot /></button>
</template>
