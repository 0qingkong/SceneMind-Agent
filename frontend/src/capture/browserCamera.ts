import { captureVideoFrame } from './frameCapture'
import type {
  CaptureConnectOptions,
  CaptureDevice,
  CaptureSource,
  CaptureSourceState,
  CaptureSourceType,
} from './types'
import { CaptureSourceError } from './types'

function cameraError(error: unknown): CaptureSourceError {
  if (error instanceof CaptureSourceError) return error
  if (error instanceof DOMException) {
    if (error.name === 'NotAllowedError' || error.name === 'SecurityError') {
      return new CaptureSourceError('permission_denied', '摄像头权限被拒绝，请在浏览器设置中允许后重试。')
    }
    if (['NotFoundError', 'NotReadableError', 'AbortError', 'OverconstrainedError'].includes(error.name)) {
      return new CaptureSourceError('unavailable', '摄像头不可用、正被占用或不满足所选设备条件。')
    }
  }
  return new CaptureSourceError('unavailable', '无法启动摄像头。')
}

export class BrowserCameraSource implements CaptureSource {
  readonly type: CaptureSourceType = 'browser_camera'
  state: CaptureSourceState = 'disconnected'
  stream: MediaStream | null = null
  device: CaptureDevice | null = null
  private videoElement: HTMLVideoElement | null = null
  private connecting: Promise<MediaStream> | null = null
  private facingMode: 'user' | 'environment' | null = null

  constructor(private readonly mediaDevices: MediaDevices | undefined = globalThis.navigator?.mediaDevices) {}

  async connect(options: CaptureConnectOptions = {}): Promise<MediaStream> {
    if (!globalThis.isSecureContext && globalThis.location?.hostname !== 'localhost') {
      throw new CaptureSourceError('insecure_context', '摄像头需要 HTTPS 或 localhost 安全环境。')
    }
    if (!this.mediaDevices?.getUserMedia) {
      throw new CaptureSourceError('unsupported', '当前浏览器不支持摄像头采集。')
    }
    if (this.connecting) return this.connecting
    const canReuseStream = this.stream?.active
      && !options.deviceId
      && (!options.facingMode || options.facingMode === this.facingMode)
    if (canReuseStream) {
      if (options.videoElement) this.attach(options.videoElement)
      return this.stream
    }
    this.connecting = this.open(options)
    try {
      return await this.connecting
    } finally {
      this.connecting = null
    }
  }

  private async open(options: CaptureConnectOptions): Promise<MediaStream> {
    await this.disconnect()
    this.state = 'connecting'
    this.videoElement = options.videoElement ?? this.videoElement
    const video: MediaTrackConstraints = options.deviceId
      ? { deviceId: { exact: options.deviceId } }
      : { facingMode: { ideal: options.facingMode ?? 'environment' } }
    try {
      const stream = await this.mediaDevices!.getUserMedia({ video, audio: false })
      this.stream = stream
      this.facingMode = options.deviceId ? null : (options.facingMode ?? 'environment')
      this.state = 'connected'
      const track = stream.getVideoTracks()[0]
      const settings = track?.getSettings()
      const devices = await this.listDevices()
      this.device = devices.find((item) => item.id === settings?.deviceId) ?? {
        id: settings?.deviceId ?? '',
        label: track?.label || '浏览器摄像头',
        kind: 'videoinput',
      }
      for (const item of stream.getTracks()) {
        item.addEventListener('ended', () => {
          if (this.stream === stream) {
            this.stream = null
            this.device = null
            this.facingMode = null
            this.state = 'disconnected'
          }
        }, { once: true })
      }
      if (this.videoElement) this.attach(this.videoElement)
      return stream
    } catch (error) {
      await this.disconnect()
      this.state = 'error'
      throw cameraError(error)
    }
  }

  private attach(video: HTMLVideoElement) {
    this.videoElement = video
    video.srcObject = this.stream
    void video.play()
  }

  async disconnect(): Promise<void> {
    if (this.videoElement) {
      this.videoElement.pause()
      this.videoElement.srcObject = null
    }
    for (const track of this.stream?.getTracks() ?? []) track.stop()
    this.stream = null
    this.device = null
    this.facingMode = null
    this.state = 'disconnected'
  }

  async captureFrame(): Promise<File> {
    if (!this.stream?.active || !this.videoElement) {
      throw new CaptureSourceError('not_connected', '请先连接摄像头。')
    }
    return captureVideoFrame(this.videoElement)
  }

  async listDevices(): Promise<CaptureDevice[]> {
    if (!this.mediaDevices?.enumerateDevices) return []
    const devices = await this.mediaDevices.enumerateDevices()
    return devices
      .filter((item) => item.kind === 'videoinput')
      .map((item, index) => ({
        id: item.deviceId,
        label: item.label || `摄像头 ${index + 1}`,
        kind: 'videoinput' as const,
      }))
  }

  async switchDevice(deviceId: string, videoElement?: HTMLVideoElement): Promise<MediaStream> {
    return this.connect({ deviceId, videoElement: videoElement ?? this.videoElement ?? undefined })
  }
}
