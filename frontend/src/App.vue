<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { getReadiness } from './api/client'
import SpatialAppShell from './layouts/SpatialAppShell.vue'
import type { ReadinessResponse } from './types/api'

const readiness = ref<ReadinessResponse | null>(null)

onMounted(async () => {
  try { readiness.value = await getReadiness() } catch { readiness.value = null }
})
</script>

<template>
  <SpatialAppShell :readiness="readiness">
    <RouterView v-slot="{ Component }">
      <Transition name="route" mode="out-in">
        <component :is="Component" />
      </Transition>
    </RouterView>
  </SpatialAppShell>
</template>
