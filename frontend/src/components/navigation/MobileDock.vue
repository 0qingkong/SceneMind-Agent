<script setup lang="ts">
import { PhBrain, PhCamera, PhHouse, PhSparkle, PhUserCircle } from '@phosphor-icons/vue'

const items = [
  { to: '/', label: '首页', icon: PhHouse },
  { to: '/live', label: '镜头', icon: PhCamera },
  { to: '/memory', label: '记忆', icon: PhBrain },
  { to: '/agent', label: 'Agent', icon: PhSparkle },
  { to: '/me', label: '我的', icon: PhUserCircle },
]
</script>

<template>
  <nav class="mobile-dock" aria-label="移动端主导航">
    <RouterLink v-for="item in items" :key="item.to" :to="item.to">
      <component :is="item.icon" :size="22" weight="duotone" aria-hidden="true" />
      <small>{{ item.label }}</small>
    </RouterLink>
  </nav>
</template>
