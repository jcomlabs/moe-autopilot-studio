# MoE Autopilot Studio

MoE Autopilot Studio is a Windows-first laboratory for deciding whether a
local mixture-of-experts model should use a measured hot-expert split. It turns
workload shape, hardware budgets, and protocol-compatible evidence into one of
three verdicts: `ENABLE`, `DISABLE`, or `MEASURE`.

The arithmetic is deterministic. The optional advisor can run as a bounded
mixture of agents: Xiaomi MiMo and DeepSeek independently review the report,
then GPT-5.6 Sol synthesizes only validated opinions through Codex App Server
and ChatGPT OAuth. No model can change metrics, commands, or the selected
experiment.

![MoE Autopilot Studio deterministic workload analysis](docs/assets/studio-desktop.png)

## Quickstart

1. Download and extract the latest Windows x64 ZIP from
   [Releases](https://github.com/jcomlabs/moe-autopilot-studio/releases/latest).
2. Run `MoEAutopilotStudio.exe`. No Python, GPU, model, or Codex is required.
3. Open `Coder-Next: prefill versus decode` and select `Total latency`.
4. Compare the default chat workload with a prompt-heavy workload such as
   16,000 prompt tokens and 300 output tokens.
5. Open `Coder-Next: session transfer` to see the protocol-compatible
   68.56% coverage and +22.22% decode result.
6. Optionally connect ChatGPT and ask GPT-5.6 to explain the current verdict.
   Configure Xiaomi and DeepSeek to enable the full three-member council.

The fixture path is fully offline and deterministic. The `Runs` view is the
optional Windows path for launching a local `llama-bench.exe` A/B.

The [fixture-only web report](https://jcomlabs.github.io/moe-autopilot-studio/)
is the no-install fallback. Custom workloads, imports, local runs, and ChatGPT
OAuth remain exclusive to the Windows/source application.

## Run from source

Requirements: Python 3.11+, Node.js 22+, and Windows, Linux, or WSL.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
Push-Location frontend
npm ci
npm run build
Pop-Location
$env:STUDIO_OPEN_BROWSER = "0"
.\.venv\Scripts\moe-autopilot-studio.exe
```

Open the printed loopback URL. To use the live advisor, install Codex CLI and
sign in with ChatGPT. Tokens remain owned by Codex; Studio never stores them.

```powershell
codex login
```

The external council members are opt-in and configured only through process
environment variables. Never place real keys in a project file or run spec.

```powershell
$env:XIAOMI_API_KEY = "<xiaomi-api-key>"
$env:XIAOMI_BASE_URL = "https://token-plan-ams.xiaomimimo.com/v1"
$env:DEEPSEEK_API_KEY = "<deepseek-api-key>"
MoEAutopilotStudio.exe
```

Optional overrides are `XIAOMI_MODEL`, `DEEPSEEK_MODEL`,
`DEEPSEEK_BASE_URL`, `XIAOMI_TIMEOUT_SECONDS`, and
`DEEPSEEK_TIMEOUT_SECONDS`. Provider keys are held in memory, are never written
to SQLite, and are removed from every Codex, profiler, and llama.cpp child
process environment. Without either key, the remaining advisors and the fully
offline deterministic engine continue to work.

## What the evidence says

All public fixtures are prompt-free transformations with hashes of their source
artifacts. Values are labelled `measured`, `derived`, or `estimated`.

| Fixture | Compatible result | Meaning |
|---|---:|---|
| Coder-Next decode | 72.29 -> 88.35 tok/s, +22.22% | Session hot-list, 68.56% canonical coverage |
| Coder-Next end-to-end | prefill -9.90%, decode +5.22% | Measured break-even is 19.18 prompt tokens per output token |
| Qwen3.6-35B decode | 116.68 -> 128.35 tok/s, +9.99% | Same direction on a second MoE architecture |
| gpt-oss adaptive | 38.03 -> 41.85 tok/s, +10.04% | Routing-flatness limitation remains visible |

The historical source write-up stated a break-even near 2.3 and a non-circular
decode gain of +19.3%. Recalculation found that 2.3 is inconsistent with the
measured prefill/decode arms, while the +19.3% comparison crossed build
fingerprints. Studio therefore reports 19.18 and uses the same-build V2.2
comparison (+22.22%). The older arms remain visible but are rejected by the
protocol gate.

These are measurements from one Windows workstation, not universal speed
claims. Recalibrate before applying them to another model, build, or machine.

## Maturity and limits

Studio is experimental `v0.2` research tooling, not an automatic production
optimizer. It does not implement a new cache algorithm, dynamic caching, V3,
training, or DeltaMoE. Its bundled measurements come from one Windows
workstation and must not be generalized to a different model, build, or machine
without recalibration. Local runs require the compatible llama.cpp fork and do
not alter model files.

The earlier research repository remains frozen at
`JigSawPT/moe-autopilot@e1170152ed074a062c235ee685af08fd3dde6dec`.
See [NOTICE](NOTICE) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the
technical boundary and immutable provenance. Event-specific material is kept on
the `submission/openai-build-week` branch so the general product remains clean.

## Development

```powershell
.\.venv\Scripts\python.exe -m pytest
Push-Location frontend
npm test
npm run build
Pop-Location
```

Build the Windows release with:

```powershell
.\scripts\build_release.ps1
```

The local API binds only to `127.0.0.1`. Experiment commands are stored as
`executable`, `argv`, and `env`, executed without a shell, and restricted to
known llama.cpp binaries. Secret-bearing fields are rejected, child
environments are sanitized, logs are redacted before persistence, and
`llama-server` is restricted to loopback. Project and run state lives under
`%LOCALAPPDATA%\MoEAutopilotStudio`.

## License

MIT. Third-party and pre-existing source provenance is in [NOTICE](NOTICE).
