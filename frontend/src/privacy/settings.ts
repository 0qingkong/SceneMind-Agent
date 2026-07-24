import type { AutoSaveMode } from '../types/api'

export interface PrivacyPreferences {
  defaultCaptureInterval: number
  autoSaveMode: AutoSaveMode
  retentionDays: number
  alwaysShowCameraIndicator: boolean
  pauseAllContinuousCapture: boolean
  confirmBeforeDelete: boolean
  showSimulatorLabels: boolean
}

export const SETTINGS_KEY = 'scenemind.privacy.v1'
export const SETTINGS_EVENT = 'scenemind-preferences-changed'

export const defaultPreferences: PrivacyPreferences = {
  defaultCaptureInterval: 5,
  autoSaveMode: 'meaningful-change',
  retentionDays: 30,
  alwaysShowCameraIndicator: true,
  pauseAllContinuousCapture: false,
  confirmBeforeDelete: true,
  showSimulatorLabels: true,
}

function boundedInteger(value: unknown, fallback: number, minimum: number, maximum: number) {
  const number = Number(value)
  return Number.isInteger(number) && number >= minimum && number <= maximum ? number : fallback
}

function booleanPreference(value: unknown, fallback: boolean) {
  return typeof value === 'boolean' ? value : fallback
}

export function loadPreferences(storage: Storage = localStorage): PrivacyPreferences {
  try {
    const parsed = JSON.parse(storage.getItem(SETTINGS_KEY) ?? '{}') as Partial<PrivacyPreferences>
    const mode: AutoSaveMode = ['manual', 'meaningful-change', 'every-analyzed-sample'].includes(parsed.autoSaveMode ?? '')
      ? parsed.autoSaveMode as AutoSaveMode
      : defaultPreferences.autoSaveMode
    return {
      defaultCaptureInterval: boundedInteger(parsed.defaultCaptureInterval, 5, 3, 60),
      autoSaveMode: mode,
      retentionDays: boundedInteger(parsed.retentionDays, 30, 1, 3650),
      alwaysShowCameraIndicator: booleanPreference(parsed.alwaysShowCameraIndicator, true),
      pauseAllContinuousCapture: booleanPreference(parsed.pauseAllContinuousCapture, false),
      confirmBeforeDelete: booleanPreference(parsed.confirmBeforeDelete, true),
      showSimulatorLabels: booleanPreference(parsed.showSimulatorLabels, true),
    }
  } catch {
    return { ...defaultPreferences }
  }
}

export function savePreferences(
  preferences: PrivacyPreferences,
  storage: Storage = localStorage,
) {
  const normalized = loadPreferences({
    getItem: () => JSON.stringify(preferences),
  } as Storage)
  storage.setItem(SETTINGS_KEY, JSON.stringify(normalized))
  globalThis.dispatchEvent?.(new CustomEvent(SETTINGS_EVENT, { detail: normalized }))
  return normalized
}

export function resetPreferences(storage: Storage = localStorage) {
  storage.removeItem(SETTINGS_KEY)
  globalThis.dispatchEvent?.(new CustomEvent(SETTINGS_EVENT, { detail: defaultPreferences }))
  return { ...defaultPreferences }
}
