import type { MemoryCoreState } from '../../composables/useMemoryCoreState'
import type { VisualQuality } from '../../composables/useVisualQuality'

type CanvasOptions = {
  state: () => MemoryCoreState
  quality: () => VisualQuality
  visible: () => boolean
}

type CoreProfile = {
  energy: number
  speed: number
  colorA: number
  colorB: number
  accent: number
}

type Dispose = () => void

const profiles: Record<MemoryCoreState, CoreProfile> = {
  idle: { energy: 0.34, speed: 0.72, colorA: 0x8ddcff, colorB: 0x6f78ff, accent: 0xb4f4ff },
  observing: { energy: 0.54, speed: 0.96, colorA: 0x72e4ff, colorB: 0x4d8eff, accent: 0x9ffff0 },
  analyzing: { energy: 0.9, speed: 1.62, colorA: 0x65e6ff, colorB: 0x806cff, accent: 0xffffff },
  remembering: { energy: 0.72, speed: 1.16, colorA: 0x72ddba, colorB: 0x637dff, accent: 0xc8fff2 },
  retrieving: { energy: 0.8, speed: 1.38, colorA: 0x8ddcff, colorB: 0x9c73ff, accent: 0xe2d9ff },
  'target-found': { energy: 0.62, speed: 0.88, colorA: 0x72ddba, colorB: 0x4d9eff, accent: 0xffffff },
  warning: { energy: 0.4, speed: 0.58, colorA: 0xffd78f, colorB: 0xcb7c6d, accent: 0xfff1ca },
  offline: { energy: 0.12, speed: 0.22, colorA: 0xaeb8c8, colorB: 0x77849a, accent: 0xdde4ef },
}

function drawStaticCore(canvas: HTMLCanvasElement, options: CanvasOptions): Dispose {
  const context = canvas.getContext('2d', { alpha: true })
  if (!context) return () => undefined

  let disposed = false
  let dpr = 1

  const draw = () => {
    if (disposed) return
    const bounds = canvas.getBoundingClientRect()
    const width = Math.max(1, bounds.width)
    const height = Math.max(1, bounds.height)
    dpr = Math.min(window.devicePixelRatio || 1, 1.25)
    canvas.width = Math.round(width * dpr)
    canvas.height = Math.round(height * dpr)
    context.setTransform(dpr, 0, 0, dpr, 0, 0)
    context.clearRect(0, 0, width, height)

    const profile = profiles[options.state()]
    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) * 0.245
    const glow = context.createRadialGradient(centerX, centerY, radius * 0.3, centerX, centerY, radius * 1.85)
    glow.addColorStop(0, 'rgba(100,199,255,.18)')
    glow.addColorStop(0.48, 'rgba(129,119,242,.08)')
    glow.addColorStop(1, 'rgba(129,119,242,0)')
    context.fillStyle = glow
    context.fillRect(0, 0, width, height)

    context.save()
    context.translate(centerX, centerY)
    context.scale(1, 0.62)
    context.strokeStyle = 'rgba(62,139,255,.18)'
    context.lineWidth = 1
    context.beginPath()
    context.arc(0, 0, radius * 1.55, 0, Math.PI * 2)
    context.stroke()
    context.restore()

    const gradient = context.createRadialGradient(
      centerX - radius * 0.32,
      centerY - radius * 0.38,
      radius * 0.04,
      centerX,
      centerY,
      radius * 1.08,
    )
    const a = `#${profile.colorA.toString(16).padStart(6, '0')}`
    const b = `#${profile.colorB.toString(16).padStart(6, '0')}`
    gradient.addColorStop(0, '#ffffff')
    gradient.addColorStop(0.2, a)
    gradient.addColorStop(0.7, b)
    gradient.addColorStop(1, 'rgba(129,119,242,.18)')
    context.shadowColor = 'rgba(62,139,255,.24)'
    context.shadowBlur = radius * 0.28
    context.fillStyle = gradient
    context.beginPath()
    context.arc(centerX, centerY, radius, 0, Math.PI * 2)
    context.fill()
    context.shadowBlur = 0
  }

  draw()
  const observer = new ResizeObserver(draw)
  observer.observe(canvas)
  return () => {
    disposed = true
    observer.disconnect()
    context.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr)
  }
}

export async function createMemoryCoreCanvas(
  canvas: HTMLCanvasElement,
  fallbackCanvas: HTMLCanvasElement,
  options: CanvasOptions,
): Promise<Dispose> {
  let disposed = false
  let runtimeDispose: Dispose = () => undefined
  const fallbackDispose = drawStaticCore(fallbackCanvas, options)
  const showStaticFallback = () => {
    fallbackCanvas.classList.remove('is-suppressed')
    canvas.style.opacity = '0'
    canvas.dataset.renderer = 'static'
  }
  canvas.dataset.renderer = 'loading'
  canvas.style.opacity = '0'
  const dispose = () => {
    if (disposed) return
    disposed = true
    runtimeDispose()
    fallbackDispose()
    fallbackCanvas.classList.remove('is-suppressed')
    canvas.style.removeProperty('opacity')
    delete canvas.dataset.renderer
  }

  if (options.quality() === 'reduced') {
    showStaticFallback()
    return dispose
  }

  try {
    const THREE = await import('three')
    if (disposed) return dispose

    const quality = options.quality()
    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: quality === 'high',
      powerPreference: 'high-performance',
      premultipliedAlpha: true,
    })
    renderer.setClearColor(0x000000, 0)
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = 1.12

    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(36, 1, 0.1, 20)
    camera.position.set(0, 0, 4.35)

    const root = new THREE.Group()
    const coreGroup = new THREE.Group()
    const orbitGroup = new THREE.Group()
    const particleGroup = new THREE.Group()
    root.add(coreGroup, orbitGroup, particleGroup)
    scene.add(root)

    const initialProfile = profiles[options.state()]
    const uniforms = {
      uTime: { value: 0 },
      uEnergy: { value: initialProfile.energy },
      uPulse: { value: 0 },
      uPointer: { value: new THREE.Vector2() },
      uColorA: { value: new THREE.Color(initialProfile.colorA) },
      uColorB: { value: new THREE.Color(initialProfile.colorB) },
      uAccent: { value: new THREE.Color(initialProfile.accent) },
    }

    const vertexShader = /* glsl */ `
      precision highp float;
      uniform float uTime;
      uniform float uEnergy;
      uniform float uPulse;
      uniform vec2 uPointer;
      varying vec3 vNormalView;
      varying vec3 vViewPosition;
      varying float vWave;

      float coreWave(vec3 p) {
        float a = sin(p.y * 4.2 + uTime * 1.16);
        float b = sin((p.x + p.z) * 5.35 - uTime * 0.78);
        float c = cos(p.x * 6.4 - p.y * 2.25 + uTime * 0.52);
        float d = sin(length(p.xy) * 8.0 - uTime * 0.68);
        return a * 0.38 + b * 0.28 + c * 0.2 + d * 0.14;
      }

      void main() {
        vec3 unitPosition = normalize(position);
        float wave = coreWave(position);
        float pointerField = dot(unitPosition, normalize(vec3(uPointer * 1.15, 1.0))) * 0.025;
        float displacement = wave * (0.045 + uEnergy * 0.045) + pointerField * uEnergy;
        displacement += sin(uTime * 3.0 + position.y * 3.0) * uPulse * 0.035;
        vec3 displaced = position + normal * displacement;
        vec4 viewPosition = modelViewMatrix * vec4(displaced, 1.0);
        vNormalView = normalize(normalMatrix * normal);
        vViewPosition = -viewPosition.xyz;
        vWave = wave;
        gl_Position = projectionMatrix * viewPosition;
      }
    `

    const fragmentShader = /* glsl */ `
      precision highp float;
      uniform float uTime;
      uniform float uEnergy;
      uniform float uPulse;
      uniform vec3 uColorA;
      uniform vec3 uColorB;
      uniform vec3 uAccent;
      varying vec3 vNormalView;
      varying vec3 vViewPosition;
      varying float vWave;

      void main() {
        vec3 normal = normalize(vNormalView);
        vec3 viewDirection = normalize(vViewPosition);
        float facing = max(dot(normal, viewDirection), 0.0);
        float fresnel = pow(1.0 - facing, 2.25);
        float vertical = normal.y * 0.5 + 0.5;
        float caustic = 0.5 + 0.5 * sin(vWave * 8.0 + uTime * 0.9 + normal.x * 4.0);
        vec3 base = mix(uColorB, uColorA, clamp(vertical * 0.62 + caustic * 0.38, 0.0, 1.0));
        vec3 lightDirection = normalize(vec3(-0.46, 0.72, 0.62));
        float diffuse = max(dot(normal, lightDirection), 0.0);
        float specular = pow(max(dot(reflect(-lightDirection, normal), viewDirection), 0.0), 34.0);
        vec3 color = base * (0.58 + diffuse * 0.64);
        color += uAccent * fresnel * (0.46 + uEnergy * 0.42);
        color += vec3(1.0) * specular * (0.86 + uPulse * 0.7);
        color += uAccent * caustic * 0.08;
        float alpha = 0.9 + fresnel * 0.08;
        gl_FragColor = vec4(color, alpha);
      }
    `

    const coreGeometry = new THREE.IcosahedronGeometry(1.02, quality === 'high' ? 5 : 4)
    const coreMaterial = new THREE.ShaderMaterial({
      uniforms,
      vertexShader,
      fragmentShader,
      transparent: true,
      depthWrite: false,
    })
    const core = new THREE.Mesh(coreGeometry, coreMaterial)
    coreGroup.add(core)

    const auraMaterial = new THREE.ShaderMaterial({
      uniforms: {
        uAccent: uniforms.uAccent,
        uEnergy: uniforms.uEnergy,
      },
      vertexShader: /* glsl */ `
        varying vec3 vNormalView;
        varying vec3 vViewPosition;
        void main() {
          vec4 viewPosition = modelViewMatrix * vec4(position, 1.0);
          vNormalView = normalize(normalMatrix * normal);
          vViewPosition = -viewPosition.xyz;
          gl_Position = projectionMatrix * viewPosition;
        }
      `,
      fragmentShader: /* glsl */ `
        uniform vec3 uAccent;
        uniform float uEnergy;
        varying vec3 vNormalView;
        varying vec3 vViewPosition;
        void main() {
          float fresnel = pow(1.0 - max(dot(normalize(vNormalView), normalize(vViewPosition)), 0.0), 2.8);
          gl_FragColor = vec4(uAccent, fresnel * (0.12 + uEnergy * 0.12));
        }
      `,
      side: THREE.BackSide,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
    })
    const aura = new THREE.Mesh(coreGeometry, auraMaterial)
    aura.scale.setScalar(1.18)
    coreGroup.add(aura)

    const lattice = new THREE.Mesh(
      coreGeometry,
      new THREE.MeshBasicMaterial({
        color: initialProfile.accent,
        wireframe: true,
        transparent: true,
        opacity: quality === 'high' ? 0.055 : 0.035,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      }),
    )
    lattice.scale.setScalar(1.035)
    coreGroup.add(lattice)

    const ringGeometry = new THREE.TorusGeometry(1.48, 0.006, 5, quality === 'high' ? 220 : 128)
    const ringMaterials: InstanceType<typeof THREE.MeshBasicMaterial>[] = []
    const ringSpecs = [
      { rotation: [-0.08, 0.5, 0.16], scaleY: 0.53, opacity: 0.28 },
      { rotation: [0.62, -0.22, -0.28], scaleY: 0.66, opacity: 0.2 },
      { rotation: [-0.74, -0.35, 0.4], scaleY: 0.78, opacity: 0.13 },
    ]
    ringSpecs.forEach((spec, index) => {
      const material = new THREE.MeshBasicMaterial({
        color: index === 1 ? initialProfile.colorB : initialProfile.accent,
        transparent: true,
        opacity: spec.opacity,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
      })
      const ring = new THREE.Mesh(ringGeometry, material)
      ring.rotation.set(spec.rotation[0], spec.rotation[1], spec.rotation[2])
      ring.scale.y = spec.scaleY
      ring.userData.baseOpacity = spec.opacity
      ring.userData.speed = index % 2 ? -1 : 1
      ringMaterials.push(material)
      orbitGroup.add(ring)
    })

    let seed = 0x5c3e7a11
    const random = () => {
      seed = (seed * 1664525 + 1013904223) >>> 0
      return seed / 0xffffffff
    }
    const particleCount = quality === 'high' ? 210 : 92
    const positions = new Float32Array(particleCount * 3)
    const sizes = new Float32Array(particleCount)
    const colors = new Float32Array(particleCount * 3)
    const particleColorA = new THREE.Color(initialProfile.colorA)
    const particleColorB = new THREE.Color(initialProfile.accent)
    for (let index = 0; index < particleCount; index += 1) {
      const theta = random() * Math.PI * 2
      const phi = Math.acos(2 * random() - 1)
      const radius = 1.25 + random() * 0.95
      positions[index * 3] = Math.sin(phi) * Math.cos(theta) * radius
      positions[index * 3 + 1] = Math.cos(phi) * radius * 0.72
      positions[index * 3 + 2] = Math.sin(phi) * Math.sin(theta) * radius
      sizes[index] = 0.8 + random() * 1.9
      const color = particleColorA.clone().lerp(particleColorB, random())
      colors[index * 3] = color.r
      colors[index * 3 + 1] = color.g
      colors[index * 3 + 2] = color.b
    }
    const particleGeometry = new THREE.BufferGeometry()
    particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
    particleGeometry.setAttribute('aSize', new THREE.BufferAttribute(sizes, 1))
    particleGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
    const particleMaterial = new THREE.ShaderMaterial({
      vertexColors: true,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      vertexShader: /* glsl */ `
        attribute float aSize;
        varying vec3 vColor;
        void main() {
          vColor = color;
          vec4 viewPosition = modelViewMatrix * vec4(position, 1.0);
          gl_PointSize = aSize * (18.0 / max(1.0, -viewPosition.z));
          gl_Position = projectionMatrix * viewPosition;
        }
      `,
      fragmentShader: /* glsl */ `
        varying vec3 vColor;
        void main() {
          float distanceToCenter = length(gl_PointCoord - vec2(0.5));
          float alpha = 1.0 - smoothstep(0.12, 0.5, distanceToCenter);
          gl_FragColor = vec4(vColor, alpha * 0.72);
        }
      `,
    })
    particleGroup.add(new THREE.Points(particleGeometry, particleMaterial))

    const pointerTarget = new THREE.Vector2()
    const pointerCurrent = new THREE.Vector2()
    const host = canvas.parentElement ?? canvas
    const onPointerMove = (event: PointerEvent) => {
      if (!window.matchMedia('(pointer: fine)').matches) return
      const bounds = host.getBoundingClientRect()
      pointerTarget.set(
        ((event.clientX - bounds.left) / Math.max(1, bounds.width)) * 2 - 1,
        -(((event.clientY - bounds.top) / Math.max(1, bounds.height)) * 2 - 1),
      )
    }
    const onPointerLeave = () => pointerTarget.set(0, 0)
    host.addEventListener('pointermove', onPointerMove)
    host.addEventListener('pointerleave', onPointerLeave)

    let width = 0
    let height = 0
    const resize = () => {
      const bounds = canvas.getBoundingClientRect()
      width = Math.max(1, bounds.width)
      height = Math.max(1, bounds.height)
      const pixelRatio = Math.min(window.devicePixelRatio || 1, quality === 'high' ? 1.8 : 1.25)
      renderer.setPixelRatio(pixelRatio)
      renderer.setSize(width, height, false)
      camera.aspect = width / height
      camera.updateProjectionMatrix()
    }
    resize()
    const resizeObserver = new ResizeObserver(resize)
    resizeObserver.observe(canvas)

    let frame = 0
    let previousTime = performance.now()
    let elapsed = 0
    let pulse = 0
    let lastState = options.state()
    let currentEnergy = initialProfile.energy
    let currentSpeed = initialProfile.speed
    const targetA = new THREE.Color(initialProfile.colorA)
    const targetB = new THREE.Color(initialProfile.colorB)
    const targetAccent = new THREE.Color(initialProfile.accent)
    const latticeMaterial = lattice.material as InstanceType<typeof THREE.MeshBasicMaterial>
    const minFrameTime = quality === 'high' ? 1000 / 60 : 1000 / 42

    const render = (time: number) => {
      frame = 0
      if (disposed || !options.visible()) return
      const rawDelta = time - previousTime
      if (rawDelta < minFrameTime) {
        frame = requestAnimationFrame(render)
        return
      }
      previousTime = time
      const delta = Math.min(rawDelta / 1000, 0.05)
      const state = options.state()
      const target = profiles[state]
      if (state !== lastState) {
        pulse = state === 'target-found' ? 1 : 0.56
        lastState = state
      }
      const stateEase = 1 - Math.exp(-delta * 3.2)
      currentEnergy += (target.energy - currentEnergy) * stateEase
      currentSpeed += (target.speed - currentSpeed) * stateEase
      targetA.setHex(target.colorA)
      targetB.setHex(target.colorB)
      targetAccent.setHex(target.accent)
      uniforms.uColorA.value.lerp(targetA, stateEase)
      uniforms.uColorB.value.lerp(targetB, stateEase)
      uniforms.uAccent.value.lerp(targetAccent, stateEase)
      uniforms.uEnergy.value = currentEnergy
      uniforms.uPulse.value = pulse
      pulse *= Math.exp(-delta * 3.8)
      elapsed += delta * currentSpeed
      uniforms.uTime.value = elapsed

      pointerCurrent.lerp(pointerTarget, 1 - Math.exp(-delta * 4.8))
      uniforms.uPointer.value.copy(pointerCurrent)
      root.rotation.x += ((-pointerCurrent.y * 0.13) - root.rotation.x) * (1 - Math.exp(-delta * 3.8))
      root.rotation.y += ((pointerCurrent.x * 0.18) - root.rotation.y) * (1 - Math.exp(-delta * 3.8))
      root.rotation.z = Math.sin(elapsed * 0.12) * 0.025
      core.rotation.y = elapsed * 0.08
      core.rotation.x = Math.sin(elapsed * 0.23) * 0.08
      aura.rotation.copy(core.rotation)
      lattice.rotation.copy(core.rotation)
      latticeMaterial.color.lerp(targetAccent, stateEase)
      orbitGroup.children.forEach((ring, index) => {
        ring.rotation.z += delta * (0.055 + index * 0.018) * ring.userData.speed * currentSpeed
        const material = ringMaterials[index]
        material.color.lerp(index === 1 ? targetB : targetAccent, stateEase)
        material.opacity = ring.userData.baseOpacity * (0.76 + currentEnergy * 0.44)
      })
      particleGroup.rotation.y = -elapsed * 0.11
      particleGroup.rotation.z = Math.sin(elapsed * 0.19) * 0.12
      particleGroup.scale.setScalar(1 + pulse * 0.055)
      renderer.render(scene, camera)
      if (canvas.dataset.renderer !== 'webgl') {
        canvas.dataset.renderer = 'webgl'
        canvas.style.opacity = '1'
        fallbackCanvas.classList.add('is-suppressed')
      }
      frame = requestAnimationFrame(render)
    }

    const start = () => {
      if (disposed || frame || !options.visible()) return
      previousTime = performance.now() - minFrameTime
      frame = requestAnimationFrame(render)
    }
    const onVisibilityChange = () => {
      if (document.hidden) {
        cancelAnimationFrame(frame)
        frame = 0
      } else start()
    }
    const onContextLost = (event: Event) => {
      event.preventDefault()
      cancelAnimationFrame(frame)
      frame = 0
      showStaticFallback()
    }
    const onContextRestored = () => {
      canvas.dataset.renderer = 'loading'
      start()
    }
    document.addEventListener('visibilitychange', onVisibilityChange)
    canvas.addEventListener('webglcontextlost', onContextLost)
    canvas.addEventListener('webglcontextrestored', onContextRestored)
    start()

    runtimeDispose = () => {
      cancelAnimationFrame(frame)
      resizeObserver.disconnect()
      document.removeEventListener('visibilitychange', onVisibilityChange)
      canvas.removeEventListener('webglcontextlost', onContextLost)
      canvas.removeEventListener('webglcontextrestored', onContextRestored)
      host.removeEventListener('pointermove', onPointerMove)
      host.removeEventListener('pointerleave', onPointerLeave)
      coreGeometry.dispose()
      ringGeometry.dispose()
      particleGeometry.dispose()
      coreMaterial.dispose()
      auraMaterial.dispose()
      latticeMaterial.dispose()
      particleMaterial.dispose()
      ringMaterials.forEach((material) => material.dispose())
      renderer.dispose()
      renderer.forceContextLoss()
    }
  } catch {
    if (!disposed) showStaticFallback()
  }

  return dispose
}
