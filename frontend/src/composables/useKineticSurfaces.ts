import { onBeforeUnmount, onMounted, watch, type Ref } from 'vue'

import { useVisualQuality } from './useVisualQuality'

const KINETIC_SELECTOR = [
  '.hero-instrument',
  '.source-card',
  '.home-memory-card',
  '.observation-card',
  '.memory-match-card.prominent',
  '.agent-evidence-card',
  '.device-card',
  '.insight-card',
  '.system-card',
].join(',')

export function useKineticSurfaces(root: Ref<HTMLElement | null>) {
  const { quality } = useVisualQuality()
  let mounted = false
  let activeRoot: HTMLElement | null = null
  let activeSurface: HTMLElement | null = null
  let pendingSurface: HTMLElement | null = null
  let pendingX = 0
  let pendingY = 0
  let frame = 0
  let finePointerQuery: MediaQueryList | null = null
  let listening = false
  const touched = new Set<HTMLElement>()

  const resetSurface = (surface: HTMLElement | null) => {
    if (!surface) return
    surface.classList.remove('sm-kinetic-active')
    surface.style.removeProperty('--sm-tilt-x')
    surface.style.removeProperty('--sm-tilt-y')
  }

  const applyPointerFrame = () => {
    frame = 0
    if (pendingSurface !== activeSurface) {
      resetSurface(activeSurface)
      activeSurface = pendingSurface
    }
    if (!activeSurface) return

    const bounds = activeSurface.getBoundingClientRect()
    const normalizedX = Math.min(1, Math.max(-1, ((pendingX - bounds.left) / Math.max(1, bounds.width)) * 2 - 1))
    const normalizedY = Math.min(1, Math.max(-1, ((pendingY - bounds.top) / Math.max(1, bounds.height)) * 2 - 1))
    activeSurface.classList.add('sm-kinetic-surface', 'sm-kinetic-active')
    activeSurface.style.setProperty('--sm-tilt-x', `${(-normalizedY * 2.15).toFixed(2)}deg`)
    activeSurface.style.setProperty('--sm-tilt-y', `${(normalizedX * 2.8).toFixed(2)}deg`)
    touched.add(activeSurface)
  }

  const scheduleFrame = () => {
    if (!frame) frame = requestAnimationFrame(applyPointerFrame)
  }

  const onPointerMove = (event: PointerEvent) => {
    if (!event.isPrimary || !(event.target instanceof Element) || !activeRoot) return
    const candidate = event.target.closest<HTMLElement>(KINETIC_SELECTOR)
    pendingSurface = candidate && activeRoot.contains(candidate) ? candidate : null
    pendingX = event.clientX
    pendingY = event.clientY
    scheduleFrame()
  }

  const onPointerLeave = () => {
    pendingSurface = null
    scheduleFrame()
  }

  const shouldListen = () => Boolean(finePointerQuery?.matches) && quality.value !== 'reduced'

  const removeListeners = () => {
    if (!activeRoot || !listening) return
    activeRoot.removeEventListener('pointermove', onPointerMove)
    activeRoot.removeEventListener('pointerleave', onPointerLeave)
    listening = false
  }

  const updateListeners = () => {
    removeListeners()
    if (!activeRoot || !shouldListen()) {
      resetSurface(activeSurface)
      activeSurface = null
      pendingSurface = null
      return
    }
    activeRoot.addEventListener('pointermove', onPointerMove, { passive: true })
    activeRoot.addEventListener('pointerleave', onPointerLeave, { passive: true })
    listening = true
  }

  const bindRoot = (nextRoot: HTMLElement | null) => {
    removeListeners()
    resetSurface(activeSurface)
    activeSurface = null
    pendingSurface = null
    activeRoot = nextRoot
    updateListeners()
  }

  const reset = () => {
    cancelAnimationFrame(frame)
    frame = 0
    resetSurface(activeSurface)
    activeSurface = null
    pendingSurface = null
  }

  watch(root, (nextRoot) => {
    if (mounted) bindRoot(nextRoot)
  }, { flush: 'post' })
  watch(quality, () => {
    if (mounted) updateListeners()
  })

  onMounted(() => {
    mounted = true
    finePointerQuery = window.matchMedia('(hover: hover) and (pointer: fine)')
    finePointerQuery.addEventListener('change', updateListeners)
    bindRoot(root.value)
  })

  onBeforeUnmount(() => {
    mounted = false
    removeListeners()
    reset()
    touched.forEach((surface) => {
      surface.classList.remove('sm-kinetic-surface', 'sm-kinetic-active')
      surface.style.removeProperty('--sm-tilt-x')
      surface.style.removeProperty('--sm-tilt-y')
    })
    touched.clear()
    finePointerQuery?.removeEventListener('change', updateListeners)
    finePointerQuery = null
    activeRoot = null
  })

  return { reset }
}
