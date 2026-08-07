<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { useVisualQuality } from '../../composables/useVisualQuality'

const props = withDefaults(defineProps<{ intensity?: number }>(), { intensity: 0.72 })
const { quality } = useVisualQuality()

type Particle = {
  x: number
  y: number
  radius: number
  alpha: number
  phase: number
  speed: number
  depth: number
}

const canvas = ref<HTMLCanvasElement | null>(null)
let context: CanvasRenderingContext2D | null = null
let resizeObserver: ResizeObserver | null = null
let finePointerQuery: MediaQueryList | null = null
let frame = 0
let width = 1
let height = 1
let dpr = 1
let previousFrame = 0
let elapsed = 0
let particles: Particle[] = []
let pointerListening = false
let scrollListening = false
let disposed = false
let lowPower = false
let targetFrameDuration = 1000 / 36

const pointer = { x: 0, y: 0, targetX: 0, targetY: 0 }
const scroll = { y: 0, targetY: 0 }
const palette = [
  { x: 0.12, y: 0.18, radius: 0.54, stretch: 1.48, hue: '102, 204, 255', phase: 0.4 },
  { x: 0.78, y: 0.1, radius: 0.46, stretch: 1.25, hue: '129, 119, 242', phase: 2.1 },
  { x: 0.72, y: 0.74, radius: 0.48, stretch: 1.62, hue: '110, 226, 210', phase: 4.4 },
] as const

const seededRandom = (() => {
  let seed = 0x5c3e7a11
  return () => {
    seed = (seed * 1664525 + 1013904223) >>> 0
    return seed / 0xffffffff
  }
})()

function buildParticles() {
  const count = lowPower
    ? Math.min(22, Math.max(12, Math.round((width * height) / 76000)))
    : Math.min(54, Math.max(22, Math.round((width * height) / 42000)))
  particles = Array.from({ length: count }, () => ({
    x: seededRandom(),
    y: seededRandom(),
    radius: 0.45 + seededRandom() * 1.35,
    alpha: 0.12 + seededRandom() * 0.3,
    phase: seededRandom() * Math.PI * 2,
    speed: 0.15 + seededRandom() * 0.32,
    depth: 0.25 + seededRandom() * 0.75,
  }))
}

function drawAurora(time: number, staticFrame = false) {
  if (!context) return
  const safeIntensity = Math.min(1, Math.max(0, props.intensity))
  context.clearRect(0, 0, width, height)
  context.save()
  context.globalCompositeOperation = 'screen'

  palette.forEach((blob, index) => {
    const drift = staticFrame ? 0 : time * (0.055 + index * 0.012)
    const baseRadius = Math.max(width, height) * blob.radius
    const x = width * blob.x + Math.sin(drift + blob.phase) * width * 0.075 + pointer.x * width * (0.025 + index * 0.009)
    const scrollDrift = (index - 1) * scroll.y * Math.min(82, height * 0.08)
    const y = height * blob.y + Math.cos(drift * 0.82 + blob.phase) * height * 0.065 + pointer.y * height * (0.018 + index * 0.006) + scrollDrift
    const gradient = context!.createRadialGradient(0, 0, baseRadius * 0.04, 0, 0, baseRadius)
    gradient.addColorStop(0, `rgba(${blob.hue}, ${0.14 * safeIntensity})`)
    gradient.addColorStop(0.34, `rgba(${blob.hue}, ${0.075 * safeIntensity})`)
    gradient.addColorStop(0.72, `rgba(${blob.hue}, ${0.022 * safeIntensity})`)
    gradient.addColorStop(1, `rgba(${blob.hue}, 0)`)
    context!.save()
    context!.translate(x, y)
    context!.rotate(Math.sin(drift * 0.7 + blob.phase) * 0.16)
    context!.scale(blob.stretch, 0.68)
    context!.fillStyle = gradient
    context!.beginPath()
    context!.arc(0, 0, baseRadius, 0, Math.PI * 2)
    context!.fill()
    context!.restore()
  })

  const ribbon = context.createLinearGradient(0, height * 0.2, width, height * 0.76)
  ribbon.addColorStop(0, 'rgba(92, 191, 255, 0)')
  ribbon.addColorStop(0.46, `rgba(117, 170, 255, ${0.055 * safeIntensity})`)
  ribbon.addColorStop(0.7, `rgba(133, 116, 242, ${0.04 * safeIntensity})`)
  ribbon.addColorStop(1, 'rgba(133, 116, 242, 0)')
  context.strokeStyle = ribbon
  context.lineWidth = Math.max(70, Math.min(width, height) * 0.12)
  context.lineCap = 'round'
  context.filter = lowPower ? 'none' : `blur(${Math.max(24, Math.min(width, height) * 0.035)}px)`
  context.beginPath()
  context.moveTo(-width * 0.08, height * 0.4)
  context.bezierCurveTo(
    width * 0.28,
    height * (0.2 + Math.sin(time * 0.07) * 0.025) - scroll.y * 28,
    width * 0.64,
    height * (0.7 + Math.cos(time * 0.06) * 0.03) + scroll.y * 18,
    width * 1.08,
    height * 0.53,
  )
  context.stroke()
  context.filter = 'none'

  particles.forEach((particle) => {
    const travel = staticFrame ? 0 : time * 0.0025 * particle.speed
    const x = ((particle.x + travel) % 1.08) * width - width * 0.04 + pointer.x * particle.depth * 14
    const y = particle.y * height + Math.sin(time * 0.23 * particle.speed + particle.phase) * 10 + pointer.y * particle.depth * 9
    const pulse = staticFrame ? 0.72 : 0.62 + Math.sin(time * 0.66 + particle.phase) * 0.22
    context!.fillStyle = `rgba(219, 244, 255, ${particle.alpha * pulse * safeIntensity})`
    context!.shadowColor = 'rgba(113, 200, 255, 0.42)'
    context!.shadowBlur = particle.radius * 5
    context!.beginPath()
    context!.arc(x, y, particle.radius, 0, Math.PI * 2)
    context!.fill()
  })

  context.restore()
  context.shadowBlur = 0
}

function resize() {
  const element = canvas.value
  if (!element || !context) return
  const bounds = element.getBoundingClientRect()
  width = Math.max(1, bounds.width)
  height = Math.max(1, bounds.height)
  const memory = (navigator as Navigator & { deviceMemory?: number }).deviceMemory
  lowPower = quality.value !== 'high' || width < 768 || (typeof memory === 'number' && memory <= 4)
  targetFrameDuration = lowPower ? 1000 / 24 : 1000 / 36
  dpr = Math.min(window.devicePixelRatio || 1, lowPower ? 1 : 1.5)
  element.width = Math.round(width * dpr)
  element.height = Math.round(height * dpr)
  context.setTransform(dpr, 0, 0, dpr, 0, 0)
  buildParticles()
  drawAurora(elapsed, quality.value === 'reduced')
}

function render(time: number) {
  frame = 0
  if (disposed || document.hidden || quality.value === 'reduced') return
  if (time - previousFrame < targetFrameDuration) {
    frame = requestAnimationFrame(render)
    return
  }
  const delta = Math.min(0.05, Math.max(0, (time - previousFrame) / 1000))
  previousFrame = time
  elapsed += delta
  const ease = 1 - Math.exp(-delta * 3.4)
  pointer.x += (pointer.targetX - pointer.x) * ease
  pointer.y += (pointer.targetY - pointer.y) * ease
  scroll.y += (scroll.targetY - scroll.y) * ease * 0.68
  drawAurora(elapsed)
  frame = requestAnimationFrame(render)
}

function start() {
  if (disposed || frame || document.hidden || quality.value === 'reduced') return
  previousFrame = performance.now() - targetFrameDuration
  frame = requestAnimationFrame(render)
}

function stop() {
  cancelAnimationFrame(frame)
  frame = 0
}

function onPointerMove(event: PointerEvent) {
  pointer.targetX = (event.clientX / Math.max(1, window.innerWidth)) * 2 - 1
  pointer.targetY = (event.clientY / Math.max(1, window.innerHeight)) * 2 - 1
}

function onScroll() {
  scroll.targetY = Math.min(1, Math.max(0, window.scrollY / Math.max(1, window.innerHeight * 1.5)))
}

function updatePointerListener() {
  const shouldListen = Boolean(finePointerQuery?.matches) && quality.value !== 'reduced'
  if (shouldListen === pointerListening) return
  pointerListening = shouldListen
  if (shouldListen) window.addEventListener('pointermove', onPointerMove, { passive: true })
  else {
    window.removeEventListener('pointermove', onPointerMove)
    pointer.targetX = 0
    pointer.targetY = 0
  }
}

function updateScrollListener() {
  const shouldListen = quality.value !== 'reduced'
  if (shouldListen === scrollListening) return
  scrollListening = shouldListen
  if (shouldListen) {
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
  } else {
    window.removeEventListener('scroll', onScroll)
    scroll.y = 0
    scroll.targetY = 0
  }
}

function onQualityChange() {
  updatePointerListener()
  updateScrollListener()
  resize()
  if (quality.value === 'reduced') {
    stop()
    pointer.x = 0
    pointer.y = 0
    pointer.targetX = 0
    pointer.targetY = 0
    drawAurora(elapsed, true)
  } else start()
}

function onVisibilityChange() {
  if (document.hidden) stop()
  else if (quality.value === 'reduced') drawAurora(elapsed, true)
  else start()
}

watch(quality, onQualityChange)

onMounted(() => {
  const element = canvas.value
  if (!element) return
  context = element.getContext('2d', { alpha: true })
  if (!context) return

  finePointerQuery = window.matchMedia('(hover: hover) and (pointer: fine)')
  finePointerQuery.addEventListener('change', updatePointerListener)
  document.addEventListener('visibilitychange', onVisibilityChange)
  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(element)
  updatePointerListener()
  updateScrollListener()
  resize()
  start()
})

onBeforeUnmount(() => {
  disposed = true
  stop()
  resizeObserver?.disconnect()
  finePointerQuery?.removeEventListener('change', updatePointerListener)
  document.removeEventListener('visibilitychange', onVisibilityChange)
  window.removeEventListener('pointermove', onPointerMove)
  window.removeEventListener('scroll', onScroll)
  pointerListening = false
  scrollListening = false
  context?.clearRect(0, 0, width, height)
  context = null
})
</script>

<template>
  <canvas ref="canvas" class="spatial-ambient-field" aria-hidden="true"></canvas>
</template>

<style scoped>
.spatial-ambient-field {
  position: fixed;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.96;
  contain: strict;
}

@media (prefers-reduced-motion: reduce) {
  .spatial-ambient-field {
    opacity: 0.74;
  }
}
</style>
