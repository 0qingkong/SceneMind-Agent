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
  is_demo: boolean
  source_type: string | null
  source_device_id: string | null
  source_device_name: string | null
  captured_at: string | null
  session_id: string | null
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

export interface RelationContext {
  relation_id: string
  subject_id: string
  subject_name: string
  predicate: RelationPredicate
  object_id: string
  object_name: string
  score: number
}

export interface MemoryMatch {
  observation: ObservationSummary
  matched_object_ids: string[]
  matched_names: string[]
  relations: RelationContext[]
}

export interface LastSeenResponse {
  query: string
  matched_labels: string[]
  result: MemoryMatch
}

export interface HistoryResponse {
  query: string
  items: MemoryMatch[]
  total: number
  limit: number
  offset: number
}

export type AgentIntent =
  | 'last_seen'
  | 'history'
  | 'recent_observations'
  | 'observation_detail'
  | 'object_count'
  | 'help'
  | 'unknown'

export interface AgentToolStep {
  tool: string
  arguments: Record<string, string | number | null>
  status: 'success' | 'no_match' | 'skipped'
  result_count: number
}

export interface AgentEvidence {
  observation_id: string
  title: string | null
  location: string | null
  timestamp: string
  image_url: string
  detail_url: string
  matched_objects: string[]
  relation_context: RelationContext[]
  is_demo: boolean
}

export interface AgentQueryResponse {
  query: string
  intent: AgentIntent
  answer: string
  tool_steps: AgentToolStep[]
  evidence: AgentEvidence[]
  limitations: string[]
}

export type CaptureStatus = 'active' | 'stopped' | 'failed'
export type AutoSaveMode = 'manual' | 'meaningful-change' | 'every-analyzed-sample'

export interface CaptureSessionSummary {
  id: string
  title: string | null
  location: string | null
  source_type: string
  device_name: string | null
  status: CaptureStatus
  started_at: string
  ended_at: string | null
  sample_interval_seconds: number
  sampled_frames: number
  analyzed_frames: number
  saved_observations: number
  target_query: string | null
  target_seen: boolean
  last_error: string | null
  auto_save_mode: AutoSaveMode
  last_sampled_at: string | null
  last_saved_at: string | null
}

export interface CaptureSessionDetail extends CaptureSessionSummary {
  recent_observations: ObservationSummary[]
}

export interface CaptureSessionListResponse {
  items: CaptureSessionSummary[]
  total: number
}

export interface CaptureSampleResponse {
  session: CaptureSessionSummary
  saved: boolean
  reason: string
  observation_id: string | null
  target_found: boolean
  analysis: AnalyzeResponse
}

export interface DeviceSourceStat {
  source_type: string
  device_name: string | null
  observation_count: number
  session_count: number
  latest_activity: string | null
}

export interface DeviceStatsResponse {
  memory_count: number
  session_count: number
  active_session_count: number
  sources: DeviceSourceStat[]
}

export interface RankedCount { label: string; count: number }
export interface DailyActivity { date: string; count: number }

export interface InsightsResponse {
  total_observations: number
  observations_7_days: number
  observations_30_days: number
  total_sessions: number
  active_sessions: number
  sampled_frames: number
  analyzed_frames: number
  saved_frames: number
  average_objects: number
  average_relations: number
  session_save_efficiency: number
  top_objects: RankedCount[]
  top_locations: RankedCount[]
  top_sources: RankedCount[]
  top_devices: RankedCount[]
  daily_activity: DailyActivity[]
  recent_sessions: CaptureSessionSummary[]
}

export interface HealthResponse {
  status: string
  version: string
  analyzer_mode: string
  model_loaded: boolean
  device: string | null
  demo_mode: boolean
}
