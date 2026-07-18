export type Verdict = 'ENABLE' | 'DISABLE' | 'MEASURE'
export type Objective = 'total_latency' | 'decode_throughput'

export interface WorkloadIntent {
  description: string
  prompt_tokens: number
  output_tokens: number
  objective: Objective
}

export interface HardwareProfile {
  name: string
  vram_total_gb: number
  vram_baseline_gb: number
  vram_reserve_gb: number
  ram_budget_gb: number
  ram_bandwidth_gbps: number
  vram_bandwidth_gbps: number
  model_vram_budget_gb?: number
}

export interface FixtureSummary {
  id: string
  name: string
  summary: string
  model: {
    id: string
    name: string
    architecture: string
    layers: number
    expert_count: number
    experts_used: number
    activation_family: string
    notes: string[]
  }
  hardware: HardwareProfile
  default_workload: WorkloadIntent
  limitations: string[]
  run_count: number
  has_activation_profile: boolean
  provenance: Record<string, unknown>
}

export interface CandidateReport {
  run_id: string
  label: string
  evidence: 'measured' | 'derived' | 'estimated'
  verdict: Verdict
  reason: string
  compatible: boolean
  budget_ok: boolean
  decode_tps: number | null
  prefill_tps: number | null
  coverage: number | null
  baseline_latency_s: number | null
  candidate_latency_s: number | null
  delta_percent: number | null
  break_even_prompt_output_ratio: number | null
  vram_required_gb: number
  ram_required_gb: number
  protocol_signature: string
  risk_flags: string[]
}

export interface AnalysisReport {
  fixture_id: string
  fixture_name: string
  generated_at: string
  workload: WorkloadIntent
  hardware: HardwareProfile
  baseline_run_id: string
  verdict: Verdict
  recommendation_id: string | null
  summary: string
  canonical_coverage: number | null
  candidates: CandidateReport[]
  assumptions: string[]
}

export interface CodexAccount {
  available: boolean
  authenticated: boolean
  auth_mode?: string | null
  plan_type?: string | null
  backend: 'app-server' | 'exec' | 'offline'
  error?: string | null
}

export interface AdvisorProviderStatus {
  id: string
  label: string
  configured: boolean
  available: boolean
  model: string
  auth: 'oauth' | 'environment' | 'none'
  latency_ms: number | null
  error?: string | null
}

export interface AdvisorCouncilStatus {
  mode: 'single' | 'moa'
  strategy: string
  providers: AdvisorProviderStatus[]
}

export interface AdvisorMemberResult {
  provider: string
  label: string
  model: string
  status: 'accepted' | 'rejected' | 'unavailable'
  latency_ms: number
  recommendation_id?: string | null
  rationale?: string | null
  error?: string | null
}

export interface AdvisorDecision {
  recommendation_id: string | null
  rationale: string
  risk_flags: string[]
  assumptions: string[]
  backend: 'app-server' | 'exec' | 'offline' | 'xiaomi' | 'deepseek' | 'moa'
  model: string
  members: AdvisorMemberResult[]
  quorum: number
}

export interface FixtureRunData {
  id: string
  name: string
  runs: Array<{
    id: string
    label: string
    role: string
    evidence: string
    decode_tps: number | null
    prefill_tps: number | null
    coverage: number | null
    hot_n: number | null
    n_cpu_moe: number
    model_vram_gb: number
    ram_required_gb: number
    source_hashes: string[]
    protocol: { instrument: string; model_id: string; build_id: string; flags: Record<string, unknown>; signature: string }
    notes: string[]
  }>
  limitations: string[]
  provenance: { source_artifacts?: Array<{ name: string; sha256: string }>; [key: string]: unknown }
}

export interface RunRecord {
  id: string
  label: string
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
  created_at: string
  updated_at: string
  current_command: number
  return_codes: number[]
  stdout_tail: string
  stderr_tail: string
  vram_baseline_mb: number | null
  error: string | null
}
