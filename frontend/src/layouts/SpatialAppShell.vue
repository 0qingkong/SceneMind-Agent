<script setup lang="ts">
import { ref } from 'vue'

import MobileDock from '../components/navigation/MobileDock.vue'
import SpatialRail from '../components/navigation/SpatialRail.vue'
import SpatialAmbientField from '../components/spatial/SpatialAmbientField.vue'
import GlobalSystemStrip from '../components/system/GlobalSystemStrip.vue'
import { useKineticSurfaces } from '../composables/useKineticSurfaces'
import { useRevealMotion } from '../composables/useRevealMotion'
import { useVisualQuality } from '../composables/useVisualQuality'
import type { ReadinessResponse } from '../types/api'

defineProps<{ readiness: ReadinessResponse | null }>()
const railExpanded = ref(false)
const shell = ref<HTMLElement | null>(null)
const { quality } = useVisualQuality()

useRevealMotion(shell)
useKineticSurfaces(shell)
</script>

<template>
  <div ref="shell" class="spatial-shell" :class="[`visual-quality-${quality}`, { 'rail-expanded': railExpanded }]">
    <a class="skip-link" href="#main-content">跳到主要内容</a>
    <SpatialAmbientField />
    <SpatialRail :expanded="railExpanded" @toggle="railExpanded = !railExpanded" />
    <div class="spatial-workspace">
      <GlobalSystemStrip :readiness="readiness" />
      <RouterLink
        v-if="readiness?.demo_mode || readiness?.demo_data_present"
        class="global-demo-banner"
        to="/system"
        role="status"
      >
        Profile {{ readiness.demo_profile }} · Mock / 演示数据已明确标记 · 不代表真实 YOLO 检测
      </RouterLink>
      <main id="main-content" class="page-container" tabindex="-1">
        <slot />
      </main>
    </div>
    <MobileDock />
  </div>
</template>
