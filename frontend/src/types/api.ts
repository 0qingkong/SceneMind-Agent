export interface DetectedObject {
  id: string
  label: string
  display_name: string
  confidence: number
  bbox: [number, number, number, number]
}

export type RelationPredicate =
  | 'left_of'
  | 'right_of'
  | 'above'
  | 'below'
  | 'near'
  | 'overlaps'
  | 'inside'
  | 'contains'

export interface RelationEvidence {
  method: 'geometry'
  center_distance: number | null
  iou: number | null
  containment_ratio: number | null
}

export interface DetectedRelation {
  id: string
  subject_id: string
  predicate: RelationPredicate
  object_id: string
  score: number
  evidence: RelationEvidence
}

export interface AnalyzeResponse {
  trace_id: string
  engine: string
  filename: string
  image_width: number
  image_height: number
  scene_summary: string
  objects: DetectedObject[]
  relations: DetectedRelation[]
  latency_ms: number
}

export interface ObservedObject extends DetectedObject {
  sort_order: number
}

export interface ObservationSummary {
  id: string
  title: string | null
  location: string | null
  created_at: string
  image_url: string
  detail_url: string
  engine: string
  summary: string
  object_count: number
  relation_count: number
  labels: string[]
}

export interface ObservationDetail extends ObservationSummary {
  original_filename: string
  mime_type: string
  image_width: number
  image_height: number
  objects: ObservedObject[]
  relations: DetectedRelation[]
}

export interface ObservationListResponse {
  items: ObservationSummary[]
  total: number
  limit: number
  offset: number
}
