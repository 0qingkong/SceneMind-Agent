import { onBeforeUnmount, onMounted, watch, type Ref } from 'vue'

import { useVisualQuality } from './useVisualQuality'

const REVEAL_SELECTOR = [
  '.page-heading',
  '.hero-narrative',
  '.hero-core-stage',
  '.hero-instrument',
  '.section-header',
  '.perception-context',
  '.surface-card',
  '.metric-tile',
  '.observation-card',
  '.memory-match-card',
  '.agent-evidence-card',
  '.simulator-disclaimer',
  '.device-card',
  '.insight-card',
  '.system-card',
  '.session-card',
  '.privacy-card',
].join(',')

const EXCLUDED_SELECTOR = [
  '.spatial-rail',
  '.mobile-dock',
  '.global-system-strip',
  '[data-motion="off"]',
  '[aria-hidden="true"]',
].join(',')

export function useRevealMotion(root: Ref<HTMLElement | null>) {
  const { quality } = useVisualQuality()
  let mounted = false
  let activeRoot: HTMLElement | null = null
  let intersectionObserver: IntersectionObserver | null = null
  let mutationObserver: MutationObserver | null = null
  let revealOrder = 0
  const targets = new Set<HTMLElement>()

  const reveal = (target: HTMLElement) => target.classList.add('sm-reveal-visible')

  const observeTarget = (target: HTMLElement) => {
    if (targets.has(target) || target.closest(EXCLUDED_SELECTOR)) return
    const revealParent = target.parentElement?.closest('.sm-reveal-target')
    if (revealParent && activeRoot?.contains(revealParent)) return

    targets.add(target)
    target.classList.add('motion-ready', 'sm-reveal-target')
    target.style.setProperty('--sm-reveal-order', String(revealOrder % 8))
    revealOrder += 1

    if (quality.value === 'reduced' || !intersectionObserver) reveal(target)
    else intersectionObserver.observe(target)
  }

  const collect = (node: ParentNode | Element) => {
    if (node instanceof Element && node.matches(REVEAL_SELECTOR)) observeTarget(node as HTMLElement)
    node.querySelectorAll<HTMLElement>(REVEAL_SELECTOR).forEach(observeTarget)
  }

  const release = (node: Node) => {
    targets.forEach((target) => {
      if (target !== node && (!(node instanceof Element) || !node.contains(target))) return
      intersectionObserver?.unobserve(target)
      target.classList.remove('motion-ready', 'sm-reveal-target', 'sm-reveal-visible')
      target.style.removeProperty('--sm-reveal-order')
      targets.delete(target)
    })
  }

  const createIntersectionObserver = () => {
    intersectionObserver?.disconnect()
    intersectionObserver = null
    if (quality.value === 'reduced' || typeof IntersectionObserver === 'undefined') {
      targets.forEach(reveal)
      return
    }
    intersectionObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return
          const target = entry.target as HTMLElement
          reveal(target)
          intersectionObserver?.unobserve(target)
        })
      },
      { rootMargin: '0px 0px -7% 0px', threshold: 0.12 },
    )
    targets.forEach((target) => {
      if (!target.classList.contains('sm-reveal-visible')) intersectionObserver?.observe(target)
    })
  }

  const cleanupRoot = () => {
    intersectionObserver?.disconnect()
    mutationObserver?.disconnect()
    intersectionObserver = null
    mutationObserver = null
    targets.forEach((target) => {
      target.classList.remove('motion-ready', 'sm-reveal-target', 'sm-reveal-visible')
      target.style.removeProperty('--sm-reveal-order')
    })
    targets.clear()
    revealOrder = 0
    activeRoot = null
  }

  const bindRoot = (nextRoot: HTMLElement | null) => {
    cleanupRoot()
    activeRoot = nextRoot
    if (!nextRoot) return
    createIntersectionObserver()
    collect(nextRoot)
    mutationObserver = new MutationObserver((records) => {
      records.forEach((record) => {
        record.removedNodes.forEach(release)
        record.addedNodes.forEach((node) => {
          if (node instanceof Element) collect(node)
        })
      })
    })
    mutationObserver.observe(nextRoot, { childList: true, subtree: true })
  }

  const onQualityChange = () => {
    if (quality.value === 'reduced') {
      intersectionObserver?.disconnect()
      intersectionObserver = null
      targets.forEach(reveal)
    } else createIntersectionObserver()
  }

  const refresh = () => {
    if (activeRoot) collect(activeRoot)
  }

  watch(root, (nextRoot) => {
    if (mounted) bindRoot(nextRoot)
  }, { flush: 'post' })
  watch(quality, () => {
    if (mounted) onQualityChange()
  })

  onMounted(() => {
    mounted = true
    bindRoot(root.value)
  })

  onBeforeUnmount(() => {
    mounted = false
    cleanupRoot()
  })

  return { refresh }
}
