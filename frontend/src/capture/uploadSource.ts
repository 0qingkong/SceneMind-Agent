import type { CaptureDevice, CaptureSource, CaptureSourceState } from './types'
import { CaptureSourceError } from './types'

export class UploadCaptureSource implements CaptureSource {
  readonly type = 'upload' as const
  state: CaptureSourceState = 'disconnected'
  readonly stream = null
  readonly device = null
  private file: File | null = null

  setFile(file: File | null) {
    this.file = file
    this.state = file ? 'connected' : 'disconnected'
  }

  async connect(): Promise<null> {
    this.state = this.file ? 'connected' : 'disconnected'
    return null
  }

  async disconnect(): Promise<void> {
    this.file = null
    this.state = 'disconnected'
  }

  async captureFrame(): Promise<File> {
    if (!this.file) throw new CaptureSourceError('not_connected', '请先选择图片。')
    return this.file
  }

  async listDevices(): Promise<CaptureDevice[]> { return [] }
  async switchDevice(): Promise<null> { return null }
}
