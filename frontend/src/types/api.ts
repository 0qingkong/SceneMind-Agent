export interface DetectedObject {
  id: string
  label: string
  display_name: string
  confidence: number
  bbox: [number, number, number, number]
}

export interface AnalyzeResponse {
  trace_id: string
  engine: string
  filename: string
  scene_summary: string
  objects: DetectedObject[]
  latency_ms: number
}
