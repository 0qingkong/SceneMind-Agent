import { BrowserCameraSource } from './browserCamera.js'

export class GlassesSimulatorSource extends BrowserCameraSource {
  override readonly type = 'glasses_simulator' as const
}
