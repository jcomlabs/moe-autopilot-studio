"""Generate the fixture-only GitHub Pages fallback from deterministic reports."""

from __future__ import annotations

import json
from pathlib import Path

from moe_autopilot_studio.engine import analyze
from moe_autopilot_studio.fixtures import get_fixture
from moe_autopilot_studio.models import AnalysisRequest


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pages" / "index.html"


def scenario(fixture_id: str, name: str, prompt: int | None = None, output: int | None = None) -> dict:
    fixture = get_fixture(fixture_id)
    workload = fixture.default_workload.model_copy(
        update={
            "prompt_tokens": prompt if prompt is not None else fixture.default_workload.prompt_tokens,
            "output_tokens": output if output is not None else fixture.default_workload.output_tokens,
        }
    )
    report = analyze(AnalysisRequest(fixture_id=fixture.id, workload=workload)).model_dump(mode="json")
    report.pop("generated_at")
    return {"id": f"{fixture_id}-{prompt or 'default'}", "name": name, "report": report}


def main() -> None:
    scenarios = [
        scenario("coder-next-e2e", "Coder-Next · interactive chat"),
        scenario("coder-next-e2e", "Coder-Next · prompt-heavy", 16_000, 300),
        scenario("coder-next-decode", "Coder-Next · session transfer"),
        scenario("qwen35-decode", "Qwen3.6-35B · architecture check"),
        scenario("gptoss-adaptive", "gpt-oss · routing flatness"),
    ]
    payload = json.dumps(scenarios, separators=(",", ":")).replace("</", "<\\/")
    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MoE Autopilot Studio · Fixture Report</title>
<style>
:root{font-family:Inter,Segoe UI,sans-serif;color:#17211b;background:#eef2ef}*{box-sizing:border-box}body{margin:0}header{height:58px;background:#10231a;color:#f7fbf8;display:flex;align-items:center;justify-content:space-between;padding:0 24px}header b{font-size:15px}header a{color:#bde8d2;font-size:13px}.shell{max-width:1180px;margin:0 auto;padding:28px 22px 48px}.eyebrow{font-size:11px;text-transform:uppercase;font-weight:700;color:#567064}.chooser{display:flex;gap:12px;align-items:center;margin:12px 0 20px}.chooser select{min-width:310px;padding:10px;border:1px solid #b9c6be;background:#fff;border-radius:4px}.verdict{display:grid;grid-template-columns:1fr auto;gap:16px;background:#fff;border:1px solid #d4ddd7;border-left:4px solid #25825b;padding:18px;margin-bottom:14px;border-radius:5px}.verdict.disable{border-left-color:#bd4c3e}.verdict.measure{border-left-color:#c3842a}.verdict h1{font-size:24px;margin:3px 0 5px}.badge{align-self:start;padding:5px 8px;background:#e4f2ea;color:#17613f;font-size:11px;font-weight:800}.metrics{display:grid;grid-template-columns:repeat(4,1fr);background:#fff;border:1px solid #d4ddd7;margin-bottom:14px}.metric{padding:16px;border-right:1px solid #d4ddd7}.metric:last-child{border:0}.metric span,.metric small{display:block;color:#68766e;font-size:11px}.metric strong{display:block;font-size:21px;margin:5px 0}.panel{background:#fff;border:1px solid #d4ddd7;border-radius:5px;overflow:auto}.panel h2{font-size:15px;margin:0;padding:15px;border-bottom:1px solid #d4ddd7}table{border-collapse:collapse;width:100%;min-width:760px}th,td{text-align:left;padding:12px 14px;border-bottom:1px solid #e3e9e5;font-size:12px}th{font-size:10px;text-transform:uppercase;color:#627168;background:#f7f9f8}td b,td small{display:block}td small{color:#6d7972;margin-top:3px}.note{font-size:12px;color:#607168;margin-top:14px;line-height:1.5}@media(max-width:700px){header{padding:0 14px}.shell{padding:18px 12px}.chooser{display:block}.chooser select{width:100%;min-width:0;margin-top:8px}.verdict{grid-template-columns:1fr}.metrics{grid-template-columns:1fr 1fr}.metric:nth-child(2){border-right:0}.metric:nth-child(-n+2){border-bottom:1px solid #d4ddd7}}
</style></head><body>
<header><b>MoE Autopilot Studio · Fixture Report</b><a href="https://github.com/JigSawPT/moe-autopilot-studio/releases/latest">Windows release</a></header>
<main class="shell"><div class="eyebrow">Deterministic offline evidence</div><div class="chooser"><label for="scenario">Measured scenario</label><select id="scenario"></select></div><section id="report"></section><p class="note">This Pages fallback contains precomputed, protocol-gated fixture reports. The Windows Studio accepts custom workloads, imports evidence, runs local A/B experiments, and adds the optional GPT-5.6 Sol explanation layer.</p></main>
<script>const scenarios=__PAYLOAD__;
const select=document.querySelector('#scenario'),root=document.querySelector('#report');
const fmt=(v,d=1)=>v==null?'—':Number(v).toFixed(d); const pct=v=>v==null?'—':`${v>0?'+':''}${fmt(v)}%`;
for(const item of scenarios){const option=document.createElement('option');option.value=item.id;option.textContent=item.name;select.append(option)}
function render(){const item=scenarios.find(x=>x.id===select.value)||scenarios[0],r=item.report,c=r.candidates.find(x=>x.run_id===r.recommendation_id);const cls=r.verdict.toLowerCase();root.innerHTML=`<section class="verdict ${cls}"><div><div class="eyebrow">Workload verdict</div><h1>${r.verdict}</h1><div>${r.summary}</div></div><span class="badge">${r.recommendation_id||'NO CANDIDATE'}</span></section><section class="metrics"><div class="metric"><span>Coverage</span><strong>${r.canonical_coverage==null?'Protocol only':fmt(r.canonical_coverage*100)+'%'}</strong><small>canonical mean</small></div><div class="metric"><span>Delta</span><strong>${pct(c?.delta_percent)}</strong><small>${r.workload.objective.replace('_',' ')}</small></div><div class="metric"><span>Break-even</span><strong>${c?.break_even_prompt_output_ratio?fmt(c.break_even_prompt_output_ratio)+' : 1':'Not bounded'}</strong><small>prompt / output</small></div><div class="metric"><span>VRAM</span><strong>${c?fmt(c.vram_required_gb)+' GB':'—'}</strong><small>${c?.budget_ok?'inside budget':'measure'}</small></div></section><section class="panel"><h2>Candidate matrix</h2><table><thead><tr><th>Configuration</th><th>Verdict</th><th>Coverage</th><th>Decode</th><th>Delta</th><th>Protocol</th></tr></thead><tbody>${r.candidates.map(x=>`<tr><td><b>${x.label}</b><small>${x.risk_flags.join(' · ')||x.evidence}</small></td><td>${x.verdict}</td><td>${x.coverage==null?'—':fmt(x.coverage*100)+'%'}</td><td>${x.decode_tps==null?'—':fmt(x.decode_tps)+' tok/s'}</td><td>${pct(x.delta_percent)}</td><td><code>${x.protocol_signature}</code></td></tr>`).join('')}</tbody></table></section>`}
select.addEventListener('change',render);render();</script></body></html>""".replace("__PAYLOAD__", payload)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
