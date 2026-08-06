import { computed, onMounted, ref, watch } from 'vue'

import { useReducedMotion } from './useReducedMotion'

export type VisualQuality = 'high' | 'balanced' | 'reduced'

const STORAGE_KEY = 'scenemind-visual-quality'

export function useVisualQuality() {
  const userChoice = ref<VisualQuality | 'auto'>('auto')
  const reducedMotion = useReducedMotion()
  const isMobile = ref(false)
  const lowMemory = ref(false)

  onMounted(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY)
    if (stored === 'high' || stored === 'balanced' || stored === 'reduced' || stored === 'auto') userChoice.value = stored
    isMobile.value = window.matchMedia('(max-width: 767px)').matches
    const memory = (navigator as Navigator & { deviceMemory?: number }).deviceMemory
    lowMemory.value = typeof memory === 'number' && memory <= 4
  })

  watch(userChoice, (value) => {
    if (typeof window !== 'undefined') window.localStorage.setItem(STORAGE_KEY, value)
  })

  const quality = computed<VisualQuality>(() => {
    if (reducedMotion.value || userChoice.value === 'reduced') return 'reduced'
    if (userChoice.value !== 'auto') return userChoice.value
    if (isMobile.value || lowMemory.value) return 'balanced'
    return 'high'
  })

  return { quality, userChoice, reducedMotion }
}
