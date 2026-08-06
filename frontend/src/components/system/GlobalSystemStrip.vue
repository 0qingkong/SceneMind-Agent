<script setup lang="ts">
import { PhCloudCheck, PhCloudSlash, PhDatabase, PhPulse } from '@phosphor-icons/vue'

import type { ReadinessResponse } from '../../types/api'
import ProfileBadge from './ProfileBadge.vue'

defineProps<{ readiness: ReadinessResponse | null }>()
</script>

<template>
  <header class="global-system-strip">
    <div class="system-strip-context">
      <PhPulse :size="16" weight="duotone" aria-hidden="true" />
      <span>SceneMind Spatial OS</span>
      <small>AURORA MEMORY SYSTEM</small>
    </div>
    <div class="system-strip-signals" role="status" aria-live="polite">
      <span :class="{ online: readiness?.status === 'ready' }">
        <PhCloudCheck v-if="readiness?.status === 'ready'" :size="15" aria-hidden="true" />
        <PhCloudSlash v-else :size="15" aria-hidden="true" />
        {{ readiness?.status === 'ready' ? 'Backend ready' : 'Backend offline' }}
      </span>
      <span><PhDatabase :size="15" aria-hidden="true" />{{ readiness?.analyzer_mode === 'mock' ? 'Mock analyzer' : readiness?.analyzer_mode === 'yolo' ? 'YOLO analyzer' : 'Analyzer —' }}</span>
      <ProfileBadge :profile="readiness?.demo_profile" :demo="Boolean(readiness?.demo_mode || readiness?.demo_data_present)" />
      <RouterLink to="/system">v0.9.0-rc1</RouterLink>
    </div>
  </header>
</template>
