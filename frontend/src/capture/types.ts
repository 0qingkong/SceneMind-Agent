export type CaptureSourceType = 'upload' | 'browser_camera' | 'glasses_simulator'
export type CaptureSourceState = 'disconnected' | 'connecting' | 'connected' | 'error'

export interface CaptureDevice {
  id: string
  label: string
  kind: 'videoinput'
}

export interface CaptureConnectOptions {
  videoElement?: HTMLVideoElement
  deviceId?: string
  facingMode?: 'user' | 'environment'
}

export interface CaptureSource {
  readonly type: CaptureSourceType
  readonly state: CaptureSourceState
  readonly stream: MediaStream | null
  readonly device: CaptureDevice | null
  connect(options?: CaptureConnectOptions): Promise<MediaStream | null>
  disconnect(): Promise<void>
  captureFrame(): Promise<File>
  listDevices(): Promise<CaptureDevice[]>
  switchDevice(deviceId: string, videoElement?: HTMLVideoElement): Promise<MediaStream | null>
}

export class CaptureSourceError extends Error {
  constructor(
    public readonly code:
      | 'unsupported'
      | 'insecure_context'
      | 'permission_denied'
      | 'unavailable'
      | 'not_connected'
      | 'capture_failed',
    message: string,
  ) {
    super(message)
    this.name = 'CaptureSourceError'
  }
}
