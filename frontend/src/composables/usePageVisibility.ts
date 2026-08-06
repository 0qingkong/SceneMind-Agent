import { onBeforeUnmount, onMounted, ref } from 'vue'

export function usePageVisibility() {
  const pageVisible = ref(true)
  const update = () => { pageVisible.value = document.visibilityState === 'visible' }

  onMounted(() => {
    update()
    document.addEventListener('visibilitychange', update)
  })
  onBeforeUnmount(() => document.removeEventListener('visibilitychange', update))

  return pageVisible
}
