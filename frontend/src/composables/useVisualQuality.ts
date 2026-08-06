import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { useReducedMotion } from './useReducedMotion'

export type VisualQuality = 'high' | 'balanced' | 'reduced'

const STORAGE_KEY = 'scenemind-visual-quality'
const readStoredChoice = (): VisualQuality | 'auto' => {
  if (typeof window === 'undefined') return 'auto'
  const stored = window.localStorage.getItem(STORAGE_KEY)
  return stored === 'high' || stored === 'balanced' || stored === 'reduced' || stored === 'auto' ? stored : 'auto'
}
const sharedUserChoice = ref<VisualQuality | 'auto'>(readStoredChoice())
let storedChoiceLoaded = typeof window !== 'undefined'

export function useVisualQuality() {
  const userChoice = sharedUserChoice
  const reducedMotion = useReducedMotion()
  const isMobile = ref(typeof window !== 'undefined' && window.matchMedia('(max-width: 767px)').matches)
  const initialMemory = typeof navigator === 'undefined' ? undefined : (navigator as Navigator & { deviceMemory?: number }).deviceMemory
  const lowMemory = ref(typeof initialMemory === 'number' && initialMemory <= 4)
  let mobileMedia: MediaQueryList | null = null
  const updateMobile = () => { isMobile.value = Boolean(mobileMedia?.matches) }

  onMounted(() => {
    if (!storedChoiceLoaded) {
      const stored = window.localStorage.getItem(STORAGE_KEY)
      if (stored === 'high' || stored === 'balanced' || stored === 'reduced' || stored === 'auto') userChoice.value = stored
      storedChoiceLoaded = true
    }
    mobileMedia = window.matchMedia('(max-width: 767px)')
    updateMobile()
    mobileMedia.addEventListener('change', updateMobile)
    const memory = (navigator as Navigator & { deviceMemory?: number }).deviceMemory
    lowMemory.value = typeof memory === 'number' && memory <= 4
  })
  onBeforeUnmount(() => mobileMedia?.removeEventListener('change', updateMobile))

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
