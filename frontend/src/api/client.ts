import axios from 'axios'
import type { AnalyzeResponse } from '../types/api'

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
