import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useReducedMotion() {
  const reducedMotion = ref(false)
  let media: MediaQueryList | null = null

  const update = () => { reducedMotion.value = Boolean(media?.matches) }

  onMounted(() => {
    media = window.matchMedia('(prefers-reduced-motion: reduce)')
    update()
    media.addEventListener('change', update)
  })
  onBeforeUnmount(() => media?.removeEventListener('change', update))

  return reducedMotion
}
