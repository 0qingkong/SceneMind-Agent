<script setup lang="ts">
defineProps<{ profile?: string; demo?: boolean }>()
</script>

<template>
  <span class="profile-badge" :class="{ demo }">
    <i aria-hidden="true"></i>
    Profile {{ profile && profile !== 'none' ? profile : '—' }}
    <em v-if="demo">DEMO</em>
  </span>
</template>
