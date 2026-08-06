import type { MemoryCoreState } from '../../composables/useMemoryCoreState'
import type { VisualQuality } from '../../composables/useVisualQuality'

type CanvasOptions = {
  state: () => MemoryCoreState
  quality: () => VisualQuality
  visible: () => boolean
}

let activeDispose: (() => void) | null = null

const stateEnergy: Record<MemoryCoreState, number> = {
  idle: 0.28,
  observing: 0.48,
  analyzing: 0.76,
  remembering: 0.62,
  retrieving: 0.68,
  'target-found': 0.5,
  warning: 0.22,
  offline: 0.08,
}

export function createMemoryCoreCanvas(canvas: HTMLCanvasElement, options: CanvasOptions) {
  activeDispose?.()

  const context = canvas.getContext('2d', { alpha: true })
  if (!context) return () => undefined

  let frame = 0
  let disposed = false
  let width = 0
  let height = 0
  let dpr = 1

  const resize = () => {
    const bounds = canvas.getBoundingClientRect()
    dpr = Math.min(window.devicePixelRatio || 1, options.quality() === 'high' ? 2 : 1.35)
    width = Math.max(1, bounds.width)
    height = Math.max(1, bounds.height)
    canvas.width = Math.round(width * dpr)
    canvas.height = Math.round(height * dpr)
    context.setTransform(dpr, 0, 0, dpr, 0, 0)
  }

  const draw = (time: number) => {
    if (disposed) return
    if (!options.visible()) {
      frame = requestAnimationFrame(draw)
      return
    }

    context.clearRect(0, 0, width, height)
    const state = options.state()
    const energy = stateEnergy[state]
    const speed = options.quality() === 'high' ? 0.00018 : 0.00011
    const t = time * speed
    const centerX = width / 2
    const centerY = height / 2
    const baseRadius = Math.min(width, height) * (state === 'analyzing' ? 0.245 : 0.255)
    const points = options.quality() === 'high' ? 96 : 54

    context.save()
    context.shadowColor = state === 'warning' ? 'rgba(231,162,71,.22)' : 'rgba(62,139,255,.28)'
    context.shadowBlur = 38
    context.beginPath()
    for (let index = 0; index <= points; index += 1) {
      const angle = (index / points) * Math.PI * 2
      const wave = Math.sin(angle * 3 + t * 2.4) * 0.045 + Math.cos(angle * 5 - t * 1.6) * 0.028 + Math.sin(angle * 7 + t) * energy * 0.018
      const radius = baseRadius * (1 + wave)
      const x = centerX + Math.cos(angle) * radius
      const y = centerY + Math.sin(angle) * radius * 0.96
      if (index === 0) context.moveTo(x, y)
      else context.lineTo(x, y)
    }
    context.closePath()
    const gradient = context.createRadialGradient(centerX - baseRadius * 0.34, centerY - baseRadius * 0.38, baseRadius * 0.04, centerX, centerY, baseRadius * 1.18)
    gradient.addColorStop(0, 'rgba(255,255,255,.98)')
    gradient.addColorStop(0.18, state === 'target-found' ? 'rgba(114,221,186,.92)' : 'rgba(141,220,255,.94)')
    gradient.addColorStop(0.56, state === 'offline' ? 'rgba(154,166,186,.58)' : 'rgba(62,139,255,.9)')
    gradient.addColorStop(0.86, state === 'warning' ? 'rgba(231,162,71,.62)' : 'rgba(129,119,242,.78)')
    gradient.addColorStop(1, 'rgba(129,119,242,.08)')
    context.fillStyle = gradient
    context.fill()
    context.restore()

    const nodeCount = options.quality() === 'high' ? 8 : 5
    for (let index = 0; index < nodeCount; index += 1) {
      const angle = t * (0.28 + index * 0.018) + (index / nodeCount) * Math.PI * 2
      const orbit = baseRadius * (1.65 + (index % 2) * 0.33)
      const x = centerX + Math.cos(angle) * orbit
      const y = centerY + Math.sin(angle) * orbit * 0.54
      context.beginPath()
      context.arc(x, y, index % 3 === 0 ? 2.6 : 1.6, 0, Math.PI * 2)
      context.fillStyle = index % 2 === 0 ? 'rgba(62,139,255,.54)' : 'rgba(129,119,242,.42)'
      context.fill()
    }

    frame = requestAnimationFrame(draw)
  }

  resize()
  const observer = new ResizeObserver(resize)
  observer.observe(canvas)
  frame = requestAnimationFrame(draw)

  const dispose = () => {
    if (disposed) return
    disposed = true
    cancelAnimationFrame(frame)
    observer.disconnect()
    context.clearRect(0, 0, canvas.width, canvas.height)
    if (activeDispose === dispose) activeDispose = null
  }
  activeDispose = dispose
  return dispose
}
