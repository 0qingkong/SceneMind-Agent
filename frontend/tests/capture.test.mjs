import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { File } from 'node:buffer'
import test from 'node:test'

import { BrowserCameraSource } from '../.test-dist/capture/browserCamera.js'
import { captureVideoFrame, frameDimensions } from '../.test-dist/capture/frameCapture.js'
import { defaultPreferences, loadPreferences, savePreferences } from '../.test-dist/privacy/settings.js'

globalThis.File ??= File
globalThis.isSecureContext = true

test('frame dimensions preserve aspect ratio and compression returns a file', async () => {
  assert.deepEqual(frameDimensions(3200, 1800, 1600), { width: 1600, height: 900 })
  let canvas
  globalThis.document = {
    createElement() {
      canvas = {
        width: 0,
        height: 0,
        getContext: () => ({ drawImage() {} }),
        toBlob: (resolve, type) => resolve(new Blob(['frame'], { type })),
      }
      return canvas
    },
  }
  const file = await captureVideoFrame(
    { videoWidth: 3200, videoHeight: 1800 },
    { imageType: 'image/jpeg', quality: 0.88, maxWidth: 1600 },
  )
  assert.equal(canvas.width, 1600)
  assert.equal(canvas.height, 900)
  assert.equal(file.type, 'image/jpeg')
})

test('browser source prevents duplicate streams, switches facing mode, and stops every track', async () => {
  let requests = 0
  let stops = 0
  const track = {
    label: 'Mock Camera',
    stop: () => { stops += 1 },
    getSettings: () => ({ deviceId: 'camera-1' }),
    addEventListener() {},
  }
  const stream = {
    active: true,
    getTracks: () => [track],
    getVideoTracks: () => [track],
  }
  const mediaDevices = {
    getUserMedia: async (constraints) => {
      requests += 1
      assert.equal(constraints.audio, false)
      return stream
    },
    enumerateDevices: async () => [{ kind: 'videoinput', deviceId: 'camera-1', label: 'Mock Camera' }],
  }
  const video = { srcObject: null, play: async () => {}, pause() {} }
  const source = new BrowserCameraSource(mediaDevices)
  await source.connect({ videoElement: video })
  await source.connect({ videoElement: video })
  assert.equal(requests, 1)
  assert.equal(source.state, 'connected')
  await source.connect({ videoElement: video, facingMode: 'user' })
  assert.equal(requests, 2)
  assert.equal(stops, 1)
  await source.disconnect()
  assert.equal(stops, 2)
  assert.equal(video.srcObject, null)
})

test('privacy preferences persist and invalid values fall back safely', () => {
  const values = new Map()
  const storage = {
    getItem: (key) => values.get(key) ?? null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key),
  }
  const saved = savePreferences({ ...defaultPreferences, defaultCaptureInterval: 12 }, storage)
  assert.equal(saved.defaultCaptureInterval, 12)
  assert.equal(loadPreferences(storage).defaultCaptureInterval, 12)
  values.set('scenemind.privacy.v1', JSON.stringify({
    defaultCaptureInterval: 1,
    pauseAllContinuousCapture: 'false',
  }))
  const invalid = loadPreferences(storage)
  assert.equal(invalid.defaultCaptureInterval, 5)
  assert.equal(invalid.pauseAllContinuousCapture, false)
})

test('glasses page is explicit about simulation and supports all input modes', async () => {
  const source = await readFile(new URL('../src/views/GlassesView.vue', import.meta.url), 'utf8')
  assert.match(source, /AI GLASSES SIMULATOR/i)
  assert.match(source, /当前为浏览器端模拟，不代表已连接真实 AI 眼镜/)
  for (const mode of ['live', 'observation', 'session']) assert.match(source, new RegExp(`value="${mode}"`))
})
