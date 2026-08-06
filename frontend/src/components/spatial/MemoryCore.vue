<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { useMemoryCoreState, type MemoryCoreState } from '../../composables/useMemoryCoreState'
import { usePageVisibility } from '../../composables/usePageVisibility'
import { useVisualQuality } from '../../composables/useVisualQuality'
import CoreStatusLabel from './CoreStatusLabel.vue'
import { createMemoryCoreCanvas } from './MemoryCoreCanvas'
import OrbitRings from './OrbitRings.vue'

const props = withDefaults(defineProps<{ state?: MemoryCoreState; interactive?: boolean; compact?: boolean }>(), { state: 'idle', interactive: false, compact: false })
const emit = defineEmits<{ activate: [] }>()
const canvas = ref<HTMLCanvasElement | null>(null)
const { quality, userChoice } = useVisualQuality()
const pageVisible = usePageVisibility()
const { copy } = useMemoryCoreState(() => props.state)
const useCanvas = computed(() => quality.value !== 'reduced')
let dispose: (() => void) | null = null

const mountCanvas = async () => {
  dispose?.()
  dispose = null
  if (!useCanvas.value) return
  await nextTick()
  if (canvas.value) {
    dispose = createMemoryCoreCanvas(canvas.value, {
      state: () => props.state,
      quality: () => quality.value,
      visible: () => pageVisible.value,
    })
  }
}

watch(useCanvas, mountCanvas)
onMounted(mountCanvas)
onBeforeUnmount(() => dispose?.())
</script>

<template>
  <section class="memory-core" :class="[`state-${state}`, `quality-${quality}`, { compact, interactive }]" :aria-label="copy.label">
    <button v-if="interactive" class="memory-core-hit" type="button" :aria-label="`${copy.label}，执行主要操作`" @click="emit('activate')"></button>
    <OrbitRings />
    <canvas v-if="useCanvas" ref="canvas" class="memory-core-canvas" aria-hidden="true"></canvas>
    <div v-else class="memory-core-static" aria-hidden="true"></div>
    <CoreStatusLabel :state="state" :label="copy.label" :detail="copy.detail" />
    <label class="core-quality-control">
      <span>动态效果</span>
      <select v-model="userChoice" aria-label="动态效果质量">
        <option value="auto">自动</option><option value="high">完整</option><option value="balanced">平衡</option><option value="reduced">精简</option>
      </select>
    </label>
  </section>
</template>
