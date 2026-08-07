<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { useMemoryCoreState, type MemoryCoreState } from '../../composables/useMemoryCoreState'
import { usePageVisibility } from '../../composables/usePageVisibility'
import { useVisualQuality } from '../../composables/useVisualQuality'
import CoreStatusLabel from './CoreStatusLabel.vue'
import { createMemoryCoreCanvas } from './MemoryCoreCanvas'

const props = withDefaults(defineProps<{ state?: MemoryCoreState; interactive?: boolean; compact?: boolean }>(), { state: 'idle', interactive: false, compact: false })
const emit = defineEmits<{ activate: [] }>()
const canvas = ref<HTMLCanvasElement | null>(null)
const fallbackCanvas = ref<HTMLCanvasElement | null>(null)
const { quality, userChoice } = useVisualQuality()
const pageVisible = usePageVisibility()
const { copy } = useMemoryCoreState(() => props.state)
let dispose: (() => void) | null = null
let mountRevision = 0
let mountQueue = Promise.resolve()

const mountCanvas = async (revision: number) => {
  if (revision !== mountRevision) return
  dispose?.()
  dispose = null
  await nextTick()
  if (canvas.value && fallbackCanvas.value) {
    const nextDispose = await createMemoryCoreCanvas(canvas.value, fallbackCanvas.value, {
      state: () => props.state,
      quality: () => quality.value,
      visible: () => pageVisible.value,
    })
    if (revision !== mountRevision) nextDispose()
    else dispose = nextDispose
  }
}

const scheduleMount = () => {
  const revision = ++mountRevision
  mountQueue = mountQueue.then(() => mountCanvas(revision))
}

watch(quality, scheduleMount)
onMounted(scheduleMount)
onBeforeUnmount(() => {
  mountRevision += 1
  dispose?.()
})
</script>

<template>
  <section class="memory-core" :class="[`state-${state}`, `quality-${quality}`, { compact, interactive }]" :aria-label="copy.label">
    <button v-if="interactive" class="memory-core-hit" type="button" :aria-label="`${copy.label}，执行主要操作`" @click="emit('activate')"></button>
    <canvas ref="fallbackCanvas" class="memory-core-fallback-canvas" aria-hidden="true"></canvas>
    <canvas ref="canvas" class="memory-core-canvas" aria-hidden="true"></canvas>
    <CoreStatusLabel :state="state" :label="copy.label" :detail="copy.detail" />
    <label class="core-quality-control">
      <span>动态效果</span>
      <select v-model="userChoice" aria-label="动态效果质量">
        <option value="auto">自动</option><option value="high">完整</option><option value="balanced">平衡</option><option value="reduced">精简</option>
      </select>
    </label>
  </section>
</template>
