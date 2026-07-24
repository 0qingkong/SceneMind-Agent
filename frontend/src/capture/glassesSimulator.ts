import { BrowserCameraSource } from './browserCamera'

export class GlassesSimulatorSource extends BrowserCameraSource {
  override readonly type = 'glasses_simulator' as const
}
