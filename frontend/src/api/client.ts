import axios from 'axios'
import type {
  AnalyzeResponse,
  ObservationDetail,
  ObservationListResponse,
  HistoryResponse,
  LastSeenResponse,
  AgentQueryResponse,
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
): Promise<ObservationDetail> {
  const formData = new FormData()
  formData.append('file', file)
  if (title?.trim()) formData.append('title', title.trim())
  if (location?.trim()) formData.append('location', location.trim())
  const response = await api.post<ObservationDetail>('/observations', formData)
  return response.data
}

export async function listObservations(params?: {
  limit?: number
  offset?: number
  label?: string
  q?: string
}): Promise<ObservationListResponse> {
  const response = await api.get<ObservationListResponse>('/observations', { params })
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
