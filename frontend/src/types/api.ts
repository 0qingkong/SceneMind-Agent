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
