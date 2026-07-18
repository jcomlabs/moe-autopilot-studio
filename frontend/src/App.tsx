import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  Activity,
  BarChart3,
  Bot,
  Check,
  ChevronRight,
  CircleGauge,
  Cpu,
  Database,
  Download,
  FileJson,
  FlaskConical,
  LogIn,
  Play,
  RefreshCw,
  Server,
  ShieldCheck,
  Square,
  TriangleAlert,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { api, downloadReport } from './api'
import type {
  AdvisorDecision,
  AnalysisReport,
  CodexAccount,
  FixtureRunData,
  FixtureSummary,
  HardwareProfile,
  Objective,
  RunRecord,
  Verdict,
  WorkloadIntent,
} from './types'

type View = 'studio' | 'evidence' | 'runs'

const verdictMeta: Record<Verdict, { label: string; icon: typeof Check }> = {
  ENABLE: { label: 'Enable this configuration', icon: Check },
  DISABLE: { label: 'Leave the split disabled', icon: TriangleAlert },
  MEASURE: { label: 'Run the next experiment', icon: FlaskConical },
}

function formatNumber(value: number | null | undefined, digits = 1) {
  return value == null ? '—' : value.toFixed(digits)
}

function verdictClass(verdict: Verdict) {
  return `verdict-${verdict.toLowerCase()}`
}

function StatusBadge({ verdict }: { verdict: Verdict }) {
  return <span className={`status-badge ${verdictClass(verdict)}`}>{verdict}</span>
}

function App() {
  const [view, setView] = useState<View>('studio')
  const [fixtures, setFixtures] = useState<FixtureSummary[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [workload, setWorkload] = useState<WorkloadIntent>({ description: '', prompt_tokens: 500, output_tokens: 300, objective: 'total_latency' })
  const [hardware, setHardware] = useState<HardwareProfile | null>(null)
  const [report, setReport] = useState<AnalysisReport | null>(null)
  const [evidence, setEvidence] = useState<FixtureRunData | null>(null)
  const [account, setAccount] = useState<CodexAccount | null>(null)
  const [advisor, setAdvisor] = useState<AdvisorDecision | null>(null)
  const [runs, setRuns] = useState<RunRecord[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const selected = fixtures.find((fixture) => fixture.id === selectedId)

  const refreshAccount = useCallback(async () => {
    try { setAccount(await api.account()) } catch { setAccount(null) }
  }, [])

  const refreshRuns = useCallback(async () => {
    try { setRuns((await api.runs()).runs) } catch { setRuns([]) }
  }, [])

  useEffect(() => {
    Promise.all([api.fixtures(), api.account(), api.runs()])
      .then(([fixtureData, accountData, runData]) => {
        setFixtures(fixtureData.fixtures)
        setAccount(accountData)
        setRuns(runData.runs)
        const initial = fixtureData.fixtures.find((item) => item.id === 'coder-next-e2e') ?? fixtureData.fixtures[0]
        if (initial) {
          setSelectedId(initial.id)
          setWorkload(initial.default_workload)
          setHardware(initial.hardware)
        }
      })
      .catch((reason) => setError(String(reason)))
  }, [])

  useEffect(() => {
    if (!selectedId) return
    api.fixtureRuns(selectedId).then(setEvidence).catch((reason) => setError(String(reason)))
  }, [selectedId])

  const runAnalysis = useCallback(async () => {
    if (!selectedId || !hardware) return
    setBusy(true)
    setError('')
    setAdvisor(null)
    try { setReport(await api.analyze(selectedId, workload, hardware)) }
    catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)) }
    finally { setBusy(false) }
  }, [selectedId, workload, hardware])

  useEffect(() => {
    if (selectedId && hardware && !report) void runAnalysis()
  }, [selectedId, hardware, report, runAnalysis])

  useEffect(() => {
    if (view !== 'runs') return
    void refreshRuns()
    const timer = window.setInterval(refreshRuns, 3000)
    return () => window.clearInterval(timer)
  }, [view, refreshRuns])

  function chooseFixture(fixture: FixtureSummary) {
    setSelectedId(fixture.id)
    setWorkload(fixture.default_workload)
    setHardware(fixture.hardware)
    setReport(null)
    setAdvisor(null)
  }

  async function connectChatGPT() {
    setBusy(true)
    try {
      const result = await api.login()
      if (result.auth_url) window.open(result.auth_url, '_blank', 'noopener,noreferrer')
      window.setTimeout(refreshAccount, 3000)
    } catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)) }
    finally { setBusy(false) }
  }

  async function askAdvisor() {
    if (!report) return
    setBusy(true)
    try { setAdvisor(await api.advisor(workload.description, report)) }
    catch (reason) { setError(reason instanceof Error ? reason.message : String(reason)) }
    finally { setBusy(false) }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><Cpu size={21} /><span>MoE Autopilot</span><b>Studio</b></div>
        <nav className="topnav" aria-label="Main views">
          <button className={view === 'studio' ? 'active' : ''} onClick={() => setView('studio')}><CircleGauge size={16} />Studio</button>
          <button className={view === 'evidence' ? 'active' : ''} onClick={() => setView('evidence')}><Database size={16} />Evidence</button>
          <button className={view === 'runs' ? 'active' : ''} onClick={() => setView('runs')}><Activity size={16} />Runs</button>
        </nav>
        <button className={`connection ${account?.authenticated ? 'connected' : ''}`} onClick={account?.authenticated ? refreshAccount : connectChatGPT} title="ChatGPT connection">
          {account?.authenticated ? <ShieldCheck size={16} /> : <LogIn size={16} />}
          <span>{account?.authenticated ? `GPT-5.6 · ${account.backend}` : 'Connect ChatGPT'}</span>
        </button>
      </header>

      {error && <div className="error-strip"><TriangleAlert size={16} />{error}<button onClick={() => setError('')}>Dismiss</button></div>}

      {view === 'studio' && (
        <StudioView
          fixtures={fixtures}
          selected={selected}
          workload={workload}
          hardware={hardware}
          report={report}
          evidence={evidence}
          advisor={advisor}
          busy={busy}
          account={account}
          onChoose={chooseFixture}
          onWorkload={setWorkload}
          onHardware={setHardware}
          onAnalyze={runAnalysis}
          onAdvisor={askAdvisor}
          onConnect={connectChatGPT}
        />
      )}
      {view === 'evidence' && <EvidenceView fixture={selected} evidence={evidence} onImportError={setError} />}
      {view === 'runs' && <RunsView fixture={selected} runs={runs} refresh={refreshRuns} onError={setError} />}
    </div>
  )
}

interface StudioProps {
  fixtures: FixtureSummary[]
  selected?: FixtureSummary
  workload: WorkloadIntent
  hardware: HardwareProfile | null
  report: AnalysisReport | null
  evidence: FixtureRunData | null
  advisor: AdvisorDecision | null
  account: CodexAccount | null
  busy: boolean
  onChoose: (fixture: FixtureSummary) => void
  onWorkload: (workload: WorkloadIntent) => void
  onHardware: (hardware: HardwareProfile) => void
  onAnalyze: () => void
  onAdvisor: () => void
  onConnect: () => void
}

function StudioView(props: StudioProps) {
  const { fixtures, selected, workload, hardware, report, evidence, advisor, busy } = props
  const recommendation = report?.candidates.find((candidate) => candidate.run_id === report.recommendation_id)
  const VerdictIcon = report ? verdictMeta[report.verdict].icon : CircleGauge

  return (
    <main className="workspace">
      <aside className="scenario-panel">
        <div className="panel-heading"><span>Measured scenario</span><small>{fixtures.length} fixtures</small></div>
        <div className="fixture-list">
          {fixtures.map((fixture) => (
            <button key={fixture.id} className={fixture.id === selected?.id ? 'selected' : ''} onClick={() => props.onChoose(fixture)}>
              <span>{fixture.name}</span><small>{fixture.model.expert_count} experts · {fixture.run_count} arms</small><ChevronRight size={15} />
            </button>
          ))}
        </div>
        <div className="control-section">
          <label>Workload intent<textarea value={workload.description} rows={3} onChange={(event) => props.onWorkload({ ...workload, description: event.target.value })} /></label>
          <div className="segmented" aria-label="Optimization objective">
            {(['total_latency', 'decode_throughput'] as Objective[]).map((objective) => (
              <button key={objective} className={workload.objective === objective ? 'active' : ''} onClick={() => props.onWorkload({ ...workload, objective })}>
                {objective === 'total_latency' ? 'Total latency' : 'Decode only'}
              </button>
            ))}
          </div>
          <div className="input-grid">
            <label>Prompt<input type="number" min="0" value={workload.prompt_tokens} onChange={(event) => props.onWorkload({ ...workload, prompt_tokens: Number(event.target.value) })} /><span>tokens</span></label>
            <label>Output<input type="number" min="1" value={workload.output_tokens} onChange={(event) => props.onWorkload({ ...workload, output_tokens: Number(event.target.value) })} /><span>tokens</span></label>
          </div>
          {hardware && <div className="input-grid">
            <label>VRAM<input type="number" step="0.5" value={hardware.vram_total_gb} onChange={(event) => props.onHardware({ ...hardware, vram_total_gb: Number(event.target.value) })} /><span>GB</span></label>
            <label>RAM<input type="number" step="1" value={hardware.ram_budget_gb} onChange={(event) => props.onHardware({ ...hardware, ram_budget_gb: Number(event.target.value) })} /><span>GB</span></label>
          </div>}
          <button className="primary-command" onClick={props.onAnalyze} disabled={busy}><RefreshCw size={16} className={busy ? 'spin' : ''} />Analyze workload</button>
        </div>
      </aside>

      <section className="analysis-canvas">
        <div className={`verdict-band ${report ? verdictClass(report.verdict) : ''}`}>
          <div className="verdict-icon"><VerdictIcon size={24} /></div>
          <div><span>Workload verdict</span><h1>{report ? verdictMeta[report.verdict].label : 'Loading evidence'}</h1><p>{report?.summary ?? 'Validating the selected protocol and hardware budget.'}</p></div>
          {report && <StatusBadge verdict={report.verdict} />}
        </div>

        <div className="metric-row">
          <Metric label="Coverage" value={report?.canonical_coverage != null ? `${(report.canonical_coverage * 100).toFixed(1)}%` : 'Protocol only'} sub="canonical mean" />
          <Metric label={workload.objective === 'total_latency' ? 'Latency delta' : 'Decode delta'} value={recommendation?.delta_percent != null ? `${recommendation.delta_percent > 0 ? '+' : ''}${recommendation.delta_percent.toFixed(1)}%` : 'Need measurement'} sub={recommendation?.evidence ?? 'no compatible arm'} />
          <Metric label="Break-even" value={recommendation?.break_even_prompt_output_ratio ? `${recommendation.break_even_prompt_output_ratio.toFixed(1)} : 1` : 'Not bounded'} sub="prompt / output" />
          <Metric label="Model VRAM" value={recommendation ? `${recommendation.vram_required_gb.toFixed(1)} GB` : '—'} sub={recommendation?.budget_ok ? 'inside budget' : 'check budget'} />
        </div>

        <div className="chart-grid">
          <section className="chart-section">
            <div className="section-title"><div><h2>Coverage → decode</h2><p>Protocol-compatible arms</p></div><BarChart3 size={18} /></div>
            <CoverageChart evidence={evidence} />
          </section>
          <section className="chart-section">
            <div className="section-title"><div><h2>{workload.objective === 'total_latency' ? 'End-to-end latency' : 'VRAM placement'}</h2><p>{workload.objective === 'total_latency' ? `${workload.prompt_tokens} in / ${workload.output_tokens} out` : 'Measured working set'}</p></div><Activity size={18} /></div>
            {workload.objective === 'total_latency' ? <LatencyChart report={report} /> : <VramChart evidence={evidence} />}
          </section>
        </div>

        <section className="candidate-section">
          <div className="section-title"><div><h2>Candidate matrix</h2><p>Protocol, budget and evidence gates applied</p></div><ShieldCheck size={18} /></div>
          <div className="table-wrap"><table><thead><tr><th>Configuration</th><th>Verdict</th><th>Coverage</th><th>Decode</th><th>Delta</th><th>VRAM</th><th>Protocol</th></tr></thead>
            <tbody>{report?.candidates.map((candidate) => <tr key={candidate.run_id} className={candidate.run_id === report.recommendation_id ? 'recommended' : ''}>
              <td><b>{candidate.label}</b><small>{candidate.risk_flags.join(' · ') || candidate.evidence}</small></td>
              <td><StatusBadge verdict={candidate.verdict} /></td>
              <td>{candidate.coverage == null ? '—' : `${(candidate.coverage * 100).toFixed(1)}%`}</td>
              <td>{candidate.decode_tps == null ? '—' : `${candidate.decode_tps.toFixed(1)} tok/s`}</td>
              <td>{candidate.delta_percent == null ? '—' : `${candidate.delta_percent > 0 ? '+' : ''}${candidate.delta_percent.toFixed(1)}%`}</td>
              <td>{candidate.vram_required_gb.toFixed(1)} GB</td>
              <td><code>{candidate.protocol_signature}</code></td>
            </tr>)}</tbody></table></div>
        </section>

        <section className="advisor-section">
          <div className="advisor-heading"><Bot size={20} /><div><h2>GPT-5.6 advisor</h2><p>Explains the deterministic verdict; never computes it.</p></div><span className="advisor-backend">{advisor?.backend ?? (props.account?.authenticated ? props.account.backend : 'offline')}</span></div>
          <div className="advisor-body">
            <p>{advisor?.rationale ?? 'Ask the advisor to translate the measured trade-offs into the next concrete experiment.'}</p>
            {advisor?.risk_flags.length ? <div className="risk-list">{advisor.risk_flags.map((flag) => <span key={flag}>{flag}</span>)}</div> : null}
          </div>
          <div className="advisor-actions">
            <button onClick={props.account?.authenticated ? props.onAdvisor : props.onConnect} disabled={busy}>{props.account?.authenticated ? <><Bot size={16} />Explain with GPT-5.6</> : <><LogIn size={16} />Connect ChatGPT</>}</button>
            {report && <button className="icon-command" title="Export JSON" onClick={() => downloadReport('json', report)}><FileJson size={17} /></button>}
            {report && <button className="icon-command" title="Export HTML report" onClick={() => downloadReport('html', report)}><Download size={17} /></button>}
          </div>
        </section>
      </section>
    </main>
  )
}

function Metric({ label, value, sub }: { label: string; value: string; sub: string }) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong><small>{sub}</small></div>
}

function CoverageChart({ evidence }: { evidence: FixtureRunData | null }) {
  const runs = evidence?.runs ?? []
  const baseline = runs.find((run) => run.role === 'baseline')
  const data = runs
    .filter((run) => run.decode_tps != null && run.protocol.signature === baseline?.protocol.signature)
    .map((run) => ({ name: run.label, coverage: (run.coverage ?? 0) * 100, decode: run.decode_tps }))
  return <div className="chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={data} margin={{ top: 10, right: 18, bottom: 4, left: 0 }}><CartesianGrid stroke="#dde3de" vertical={false} /><XAxis dataKey="coverage" tickFormatter={(value) => `${Number(value).toFixed(1)}%`} tick={{ fontSize: 11 }} /><YAxis domain={[(minimum: number) => minimum - 4, (maximum: number) => maximum + 4]} tickFormatter={(value) => Number(value).toFixed(1)} tick={{ fontSize: 11 }} width={42} /><Tooltip formatter={(value) => typeof value === 'number' ? value.toFixed(1) : value} /><Line type="monotone" dataKey="decode" stroke="#216e4e" strokeWidth={2} dot={{ r: 4, fill: '#216e4e' }} isAnimationActive={false} /></LineChart></ResponsiveContainer></div>
}

function LatencyChart({ report }: { report: AnalysisReport | null }) {
  const compatible = report?.candidates.filter((candidate) => candidate.candidate_latency_s != null) ?? []
  const baseline = compatible[0]?.baseline_latency_s
  const data = [{ name: 'Baseline', seconds: baseline }, ...compatible.map((candidate) => ({ name: candidate.label, seconds: candidate.candidate_latency_s }))]
  return <div className="chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 10, right: 12, bottom: 4, left: 0 }}><CartesianGrid stroke="#dde3de" vertical={false} /><XAxis dataKey="name" tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 11 }} width={42} /><Tooltip formatter={(value) => typeof value === 'number' ? `${value.toFixed(3)} s` : value} /><Bar dataKey="seconds" radius={[3, 3, 0, 0]} isAnimationActive={false}>{data.map((_, index) => <Cell key={index} fill={index === 0 ? '#5f6b64' : '#2d6cdf'} />)}</Bar></BarChart></ResponsiveContainer></div>
}

function VramChart({ evidence }: { evidence: FixtureRunData | null }) {
  const data = (evidence?.runs ?? []).map((run) => ({ name: run.label, VRAM: run.model_vram_gb, RAM: run.ram_required_gb }))
  return <div className="chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={data} margin={{ top: 10, right: 12, bottom: 4, left: 0 }}><CartesianGrid stroke="#dde3de" vertical={false} /><XAxis dataKey="name" tick={{ fontSize: 10 }} /><YAxis tick={{ fontSize: 11 }} width={34} /><Tooltip /><Legend wrapperStyle={{ fontSize: 11 }} /><Bar dataKey="VRAM" fill="#2d6cdf" radius={[3, 3, 0, 0]} isAnimationActive={false} /><Bar dataKey="RAM" fill="#d28a22" radius={[3, 3, 0, 0]} isAnimationActive={false} /></BarChart></ResponsiveContainer></div>
}

function EvidenceView({ fixture, evidence, onImportError }: { fixture?: FixtureSummary; evidence: FixtureRunData | null; onImportError: (value: string) => void }) {
  const [kind, setKind] = useState('server_timing')
  const [imported, setImported] = useState<Record<string, unknown> | null>(null)
  async function importFile(file?: File) {
    if (!file) return
    try { setImported((await api.import(kind, await file.text(), file.name)).summary) }
    catch (reason) { onImportError(reason instanceof Error ? reason.message : String(reason)) }
  }
  return <main className="page-view">
    <div className="page-heading"><div><span>Evidence registry</span><h1>{fixture?.name ?? 'Select a fixture'}</h1><p>{fixture?.summary}</p></div><Database size={28} /></div>
    <div className="evidence-layout">
      <section className="evidence-table"><div className="section-title"><div><h2>Measured arms</h2><p>No prompt content is distributed</p></div><ShieldCheck size={18} /></div>
        <div className="table-wrap"><table><thead><tr><th>Arm</th><th>Instrument</th><th>Coverage</th><th>Decode</th><th>Prefill</th><th>Source</th></tr></thead><tbody>
          {evidence?.runs.map((run) => <tr key={run.id}><td><b>{run.label}</b><small>{run.role} · {run.evidence}</small></td><td>{run.protocol.instrument}<small>{run.protocol.build_id}</small></td><td>{run.coverage == null ? '—' : `${(run.coverage * 100).toFixed(1)}%`}</td><td>{formatNumber(run.decode_tps)} tok/s</td><td>{formatNumber(run.prefill_tps)} tok/s</td><td><code>{run.source_hashes[0]?.slice(0, 12) ?? '—'}</code></td></tr>)}
        </tbody></table></div>
      </section>
      <aside className="import-panel"><div className="section-title"><div><h2>Inspect an artifact</h2><p>Parsed locally, capped at 25 MiB</p></div><FileJson size={18} /></div>
        <label>Format<select value={kind} onChange={(event) => setKind(event.target.value)}><option value="server_timing">Server timing</option><option value="llama_bench">llama-bench JSON</option><option value="profile">Activation profile</option><option value="hotlist">Hot-list</option></select></label>
        <label className="file-drop"><input type="file" onChange={(event) => importFile(event.target.files?.[0])} /><Download size={22} /><span>Choose a local artifact</span></label>
        {imported && <pre>{JSON.stringify(imported, null, 2).slice(0, 5000)}</pre>}
        <div className="limitations"><h3>Protocol limits</h3>{evidence?.limitations.map((item) => <p key={item}>{item}</p>)}</div>
      </aside>
    </div>
  </main>
}

function RunsView({ fixture, runs, refresh, onError }: { fixture?: FixtureSummary; runs: RunRecord[]; refresh: () => Promise<void>; onError: (value: string) => void }) {
  const [binaryDir, setBinaryDir] = useState('')
  const [modelPath, setModelPath] = useState('')
  const [hotlistPath, setHotlistPath] = useState('')
  const [ncmoe, setNcmoe] = useState(24)
  const [hotN, setHotN] = useState(96)
  const executable = `${binaryDir.replace(/[\\/]$/, '')}\\llama-bench.exe`
  async function queue() {
    const common = ['-m', modelPath, '-ngl', '999', '-ncmoe', String(ncmoe), '-mmp', '0', '-t', '16', '-p', '0', '-n', '128', '-r', '3', '-fa', '1', '-o', 'json']
    const protocol = { instrument: 'llama-bench/tg128', model_id: fixture?.model.id ?? 'local-model', build_id: 'local', flags: { n_cpu_moe: ncmoe, repetitions: 3 } }
    try {
      await api.createRun({ label: `${fixture?.name ?? 'Local model'} A/B`, protocol, commands: [
        { executable, argv: common, env: {}, timeout_seconds: 1800 },
        { executable, argv: common, env: { AIPC_MOE_HOT_LIST: hotlistPath, AIPC_MOE_HOT_N: String(hotN) }, timeout_seconds: 1800 },
      ] })
      await refresh()
    } catch (reason) { onError(reason instanceof Error ? reason.message : String(reason)) }
  }
  return <main className="page-view"><div className="page-heading"><div><span>Local experiment queue</span><h1>Baseline → split A/B</h1><p>Commands execute as argv arrays; no shell or arbitrary executables.</p></div><Server size={28} /></div>
    <div className="runs-layout"><section className="run-builder"><div className="section-title"><div><h2>Run specification</h2><p>Windows llama.cpp build</p></div><FlaskConical size={18} /></div>
      <label>Binary directory<input value={binaryDir} onChange={(event) => setBinaryDir(event.target.value)} placeholder="C:\llama.cpp\build\bin\Release" /></label>
      <label>Model GGUF<input value={modelPath} onChange={(event) => setModelPath(event.target.value)} placeholder="C:\models\model.gguf" /></label>
      <label>Session hot-list<input value={hotlistPath} onChange={(event) => setHotlistPath(event.target.value)} placeholder="C:\profiles\session.hotlist" /></label>
      <div className="input-grid"><label>CPU MoE layers<input type="number" value={ncmoe} onChange={(event) => setNcmoe(Number(event.target.value))} /></label><label>HOT_N<input type="number" value={hotN} onChange={(event) => setHotN(Number(event.target.value))} /></label></div>
      <button className="primary-command" disabled={!binaryDir || !modelPath || !hotlistPath} onClick={queue}><Play size={16} />Queue measured A/B</button>
    </section>
    <section className="run-list"><div className="section-title"><div><h2>Recent runs</h2><p>SQLite-backed local history</p></div><button className="icon-command" title="Refresh runs" onClick={refresh}><RefreshCw size={16} /></button></div>
      {runs.length === 0 && <div className="empty-state"><Activity size={28} /><p>No local runs yet.</p></div>}
      {runs.map((run) => <article key={run.id} className="run-row"><div className={`run-state state-${run.status}`}>{run.status === 'running' ? <RefreshCw size={15} className="spin" /> : run.status === 'completed' ? <Check size={15} /> : <Square size={14} />}</div><div><b>{run.label}</b><small>{run.id.slice(0, 10)} · VRAM baseline {run.vram_baseline_mb ?? '—'} MiB</small>{run.error && <p>{run.error}</p>}</div><code>{run.return_codes.join(', ') || 'pending'}</code>{run.status === 'running' && <button className="icon-command" title="Cancel run" onClick={() => api.cancelRun(run.id).then(refresh)}><Square size={15} /></button>}</article>)}
    </section></div>
  </main>
}

export default App
