import axios from 'axios'
import type {
  AnalyzeResponse,
  ObservationDetail,
  ObservationListResponse,
  HistoryResponse,
  LastSeenResponse,
  AgentQueryResponse,
  AutoSaveMode,
  CaptureSampleResponse,
  CaptureSessionDetail,
  CaptureSessionListResponse,
  DeviceStatsResponse,
  HealthResponse,
  InsightsResponse,
} from '../types/api'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api/v1',
  timeout: 30_000,
})

export async function analyzeScene(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData()
  formData.append('image', file)

  const response = await api.post<AnalyzeResponse>('/analyze', formData)
  return response.data
}

export async function createObservation(
  file: File,
  title?: string,
  location?: string,
  source?: {
    sourceType?: string
    sourceDeviceId?: string
    sourceDeviceName?: string
    capturedAt?: string
    sessionId?: string
  },
): Promise<ObservationDetail> {
  const formData = new FormData()
  formData.append('file', file)
  if (title?.trim()) formData.append('title', title.trim())
  if (location?.trim()) formData.append('location', location.trim())
  if (source?.sourceType) formData.append('source_type', source.sourceType)
  if (source?.sourceDeviceId) formData.append('source_device_id', source.sourceDeviceId)
  if (source?.sourceDeviceName) formData.append('source_device_name', source.sourceDeviceName)
  if (source?.capturedAt) formData.append('captured_at', source.capturedAt)
  if (source?.sessionId) formData.append('session_id', source.sessionId)
  const response = await api.post<ObservationDetail>('/observations', formData)
  return response.data
}

export async function listObservations(params?: {
  limit?: number
  offset?: number
  label?: string
  q?: string
  sessionId?: string
}): Promise<ObservationListResponse> {
  const { sessionId, ...query } = params ?? {}
  const response = await api.get<ObservationListResponse>('/observations', {
    params: params ? { ...query, session_id: sessionId } : undefined,
  })
  return response.data
}

export async function getObservation(id: string): Promise<ObservationDetail> {
  const response = await api.get<ObservationDetail>(`/observations/${id}`)
  return response.data
}

export async function deleteObservation(id: string): Promise<void> {
  await api.delete(`/observations/${id}`)
}

export function apiAssetUrl(path: string) {
  const base = api.defaults.baseURL ?? window.location.origin
  return new URL(path, base).toString()
}

export async function getLastSeen(query: string): Promise<LastSeenResponse> {
  const response = await api.get<LastSeenResponse>('/memory/last-seen', {
    params: { q: query },
  })
  return response.data
}

export async function getHistory(
  query: string,
  params?: { limit?: number; offset?: number },
): Promise<HistoryResponse> {
  const response = await api.get<HistoryResponse>('/memory/history', {
    params: { q: query, ...params },
  })
  return response.data
}

export async function queryAgent(query: string): Promise<AgentQueryResponse> {
  const response = await api.post<AgentQueryResponse>('/agent/query', { query })
  return response.data
}

export async function createCaptureSession(payload: {
  title?: string
  location?: string
  source_type: string
  device_name?: string
  sample_interval_seconds: number
  target_query?: string
  auto_save_mode: AutoSaveMode
}): Promise<CaptureSessionDetail> {
  const response = await api.post<CaptureSessionDetail>('/capture-sessions', payload)
  return response.data
}

export async function listCaptureSessions(): Promise<CaptureSessionListResponse> {
  return (await api.get<CaptureSessionListResponse>('/capture-sessions')).data
}

export async function getCaptureSession(id: string): Promise<CaptureSessionDetail> {
  return (await api.get<CaptureSessionDetail>(`/capture-sessions/${id}`)).data
}

export async function sampleCaptureSession(
  id: string,
  file: File,
  options?: {
    forceSave?: boolean
    capturedAt?: string
    sourceDeviceId?: string
    sourceDeviceName?: string
  },
): Promise<CaptureSampleResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('force_save', String(Boolean(options?.forceSave)))
  if (options?.capturedAt) formData.append('captured_at', options.capturedAt)
  if (options?.sourceDeviceId) formData.append('source_device_id', options.sourceDeviceId)
  if (options?.sourceDeviceName) formData.append('source_device_name', options.sourceDeviceName)
  return (await api.post<CaptureSampleResponse>(`/capture-sessions/${id}/samples`, formData)).data
}

export async function stopCaptureSession(id: string): Promise<CaptureSessionDetail> {
  return (await api.post<CaptureSessionDetail>(`/capture-sessions/${id}/stop`)).data
}

export async function deleteCaptureSession(id: string): Promise<void> {
  await api.delete(`/capture-sessions/${id}`)
}

export async function getDeviceStats(): Promise<DeviceStatsResponse> {
  return (await api.get<DeviceStatsResponse>('/devices/stats')).data
}

export async function getInsights(): Promise<InsightsResponse> {
  return (await api.get<InsightsResponse>('/insights')).data
}

export async function getHealth(): Promise<HealthResponse> {
  return (await api.get<HealthResponse>('/health')).data
}

export async function exportData(): Promise<Blob> {
  return (await api.get('/privacy/export', { responseType: 'blob' })).data
}
