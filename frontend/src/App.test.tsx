import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'

const hardware = {
  name: 'Fixture workstation',
  vram_total_gb: 32,
  vram_baseline_gb: 1,
  vram_reserve_gb: 0.5,
  ram_budget_gb: 48,
  ram_bandwidth_gbps: 42,
  vram_bandwidth_gbps: 1050,
}

const workload = {
  description: 'Generation-heavy coding assistant',
  prompt_tokens: 500,
  output_tokens: 300,
  objective: 'decode_throughput',
}

const fixture = {
  id: 'coder-next-decode',
  name: 'Coder-Next: session transfer',
  summary: 'Protocol-compatible fixture.',
  model: {
    id: 'coder-next', name: 'Coder-Next', architecture: 'qwen3next', layers: 48,
    expert_count: 512, experts_used: 10, activation_family: 'gated-swiglu', notes: [],
  },
  hardware,
  default_workload: workload,
  limitations: ['Decode-only protocol.'],
  run_count: 2,
  has_activation_profile: true,
  provenance: {},
}

const report = {
  fixture_id: fixture.id,
  fixture_name: fixture.name,
  generated_at: '2026-07-18T12:00:00Z',
  workload,
  hardware,
  baseline_run_id: 'baseline',
  verdict: 'ENABLE',
  recommendation_id: 'session',
  summary: 'Measured decode throughput improves by 22.2%.',
  canonical_coverage: 0.685557,
  assumptions: ['Coverage is canonical.'],
  candidates: [{
    run_id: 'session', label: 'Session history', evidence: 'measured', verdict: 'ENABLE',
    reason: 'Measured decode throughput improves by 22.2%.', compatible: true, budget_ok: true,
    decode_tps: 88.35, prefill_tps: null, coverage: 0.686, baseline_latency_s: null,
    candidate_latency_s: null, delta_percent: 22.22, break_even_prompt_output_ratio: null,
    vram_required_gb: 29.2, ram_required_gb: 45, protocol_signature: 'fixture-signature', risk_flags: ['decode-only'],
  }],
}

function response(payload: unknown) {
  return Promise.resolve(new Response(JSON.stringify(payload), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  }))
}

describe('Studio flow', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn((input: RequestInfo | URL) => {
      const url = String(input)
      if (url === '/api/fixtures') return response({ fixtures: [fixture], manifest: {} })
      if (url.includes('/api/fixtures/coder-next-decode/runs')) return response({ id: fixture.id, name: fixture.name, runs: [], limitations: fixture.limitations, provenance: {} })
      if (url === '/api/codex/account') return response({ available: false, authenticated: false, backend: 'offline' })
      if (url.startsWith('/api/advisors/status')) return response({
        mode: 'single', strategy: 'deterministic validation', providers: [],
      })
      if (url === '/api/runs') return response({ runs: [] })
      if (url === '/api/analyze') return response(report)
      return Promise.resolve(new Response('{}', { status: 404 }))
    }))
  })

  afterEach(() => vi.unstubAllGlobals())

  it('renders a deterministic verdict without ChatGPT or a GPU', async () => {
    render(<App />)
    expect(await screen.findByText('Coder-Next: session transfer')).toBeInTheDocument()
    expect(await screen.findByText('Enable this configuration')).toBeInTheDocument()
    expect(screen.getAllByText('+22.2%')).toHaveLength(2)
    expect(screen.getAllByText('68.6%')).toHaveLength(2)
    await waitFor(() => expect(fetch).toHaveBeenCalledWith('/api/analyze', expect.any(Object)))
  })
})
