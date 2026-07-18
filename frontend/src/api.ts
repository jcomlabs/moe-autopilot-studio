import type { AdvisorCouncilStatus, AdvisorDecision, AnalysisReport, CodexAccount, FixtureRunData, FixtureSummary, RunRecord, WorkloadIntent, HardwareProfile } from './types'

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }))
    throw new Error(body.detail ?? `Request failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

export const api = {
  fixtures: () => request<{ fixtures: FixtureSummary[]; manifest: Record<string, unknown> }>('/api/fixtures'),
  fixtureRuns: (id: string) => request<FixtureRunData>(`/api/fixtures/${encodeURIComponent(id)}/runs`),
  analyze: (fixtureId: string, workload: WorkloadIntent, hardware: HardwareProfile) =>
    request<AnalysisReport>('/api/analyze', { method: 'POST', body: JSON.stringify({ fixture_id: fixtureId, workload, hardware }) }),
  account: () => request<CodexAccount>('/api/codex/account'),
  advisorStatus: (probe = false) => request<AdvisorCouncilStatus>(`/api/advisors/status?probe=${probe ? 'true' : 'false'}`),
  login: () => request<{ auth_url?: string; status: string }>('/api/codex/login', { method: 'POST' }),
  advisor: (userIntent: string, report: AnalysisReport) =>
    request<AdvisorDecision>('/api/advisor', { method: 'POST', body: JSON.stringify({ user_intent: userIntent, report }) }),
  runs: () => request<{ runs: RunRecord[] }>('/api/runs'),
  createRun: (spec: unknown) => request<RunRecord>('/api/runs', { method: 'POST', body: JSON.stringify(spec) }),
  cancelRun: (id: string) => request<RunRecord>(`/api/runs/${id}/cancel`, { method: 'POST' }),
  import: (kind: string, content: string, filename: string) =>
    request<{ kind: string; summary: Record<string, unknown> }>('/api/import', { method: 'POST', body: JSON.stringify({ kind, content, filename }) }),
}

export async function downloadReport(format: string, report: AnalysisReport) {
  const response = await fetch('/api/export', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ format, report, run_spec: null }),
  })
  if (!response.ok) throw new Error('Export failed')
  const blob = await response.blob()
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `moe-autopilot-report.${format === 'markdown' ? 'md' : format}`
  anchor.click()
  URL.revokeObjectURL(url)
}
