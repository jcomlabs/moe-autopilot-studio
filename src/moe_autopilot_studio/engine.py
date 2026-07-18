from __future__ import annotations

from datetime import datetime, timezone
import re

from .coverage import canonical_coverage
from .fixtures import get_fixture
from .models import (
    AnalysisReport,
    AnalysisRequest,
    CandidateReport,
    EvidenceGrade,
    MeasuredRun,
    Objective,
    Verdict,
)


GUARD_BAND_PERCENT = 3.0


def _break_even_ratio(baseline: MeasuredRun, candidate: MeasuredRun) -> float | None:
    if not all((baseline.decode_tps, baseline.prefill_tps, candidate.decode_tps, candidate.prefill_tps)):
        return None
    decode_gain = (1 / baseline.decode_tps) - (1 / candidate.decode_tps)
    prefill_cost = (1 / candidate.prefill_tps) - (1 / baseline.prefill_tps)
    if decode_gain <= 0 or prefill_cost <= 0:
        return None
    return decode_gain / prefill_cost


def _budget_ok(run: MeasuredRun, hardware) -> bool:
    return (
        run.model_vram_gb <= hardware.model_vram_budget_gb
        and run.ram_required_gb <= hardware.ram_budget_gb
    )


def _risk_flags(run: MeasuredRun, fixture) -> list[str]:
    flags: list[str] = []
    run_text = " ".join(run.notes).lower()
    fixture_text = " ".join(fixture.limitations).lower()
    if re.search(r"(?<!non-)circular", run_text) or "ceiling" in run.id.lower():
        flags.append("circular-ceiling")
    if "flat" in run_text or "flat" in fixture_text or "flat" in fixture.summary.lower():
        flags.append("routing-flatness")
    if run.evidence == EvidenceGrade.ESTIMATED:
        flags.append("estimated")
    if run.prefill_tps is None:
        flags.append("decode-only")
    if run.role == "control":
        flags.append("isolation-control")
    return flags


def _analyze_candidate(baseline: MeasuredRun, candidate: MeasuredRun, request, fixture, hardware) -> CandidateReport:
    compatible = baseline.protocol.signature == candidate.protocol.signature
    budget_ok = _budget_ok(candidate, hardware)
    risks = _risk_flags(candidate, fixture)
    delta: float | None = None
    baseline_latency: float | None = None
    candidate_latency: float | None = None
    reason: str
    verdict = Verdict.MEASURE

    if not compatible:
        reason = "Protocol fingerprints differ; this comparison would mix instruments or run settings."
        risks.append("protocol-mismatch")
    elif not budget_ok:
        verdict = Verdict.DISABLE
        reason = "The configuration exceeds the current RAM or model-VRAM budget."
        risks.append("budget-exceeded")
    elif request.workload.objective == Objective.DECODE_THROUGHPUT:
        if baseline.decode_tps is None or candidate.decode_tps is None:
            reason = "Decode throughput is missing from one arm."
            risks.append("missing-decode")
        else:
            delta = ((candidate.decode_tps / baseline.decode_tps) - 1) * 100
            if delta >= GUARD_BAND_PERCENT:
                verdict = Verdict.ENABLE
                reason = f"Measured decode throughput improves by {delta:.1f}%."
            elif delta <= -GUARD_BAND_PERCENT:
                verdict = Verdict.DISABLE
                reason = f"Measured decode throughput regresses by {abs(delta):.1f}%."
            else:
                reason = f"The {delta:+.1f}% decode change is inside the {GUARD_BAND_PERCENT:.0f}% guard band."
    else:
        metrics = (baseline.decode_tps, baseline.prefill_tps, candidate.decode_tps, candidate.prefill_tps)
        if not all(metrics):
            reason = "A total-latency verdict requires prefill and decode from the same protocol."
            risks.append("missing-e2e-metrics")
        else:
            baseline_latency = (
                request.workload.prompt_tokens / baseline.prefill_tps
                + request.workload.output_tokens / baseline.decode_tps
            )
            candidate_latency = (
                request.workload.prompt_tokens / candidate.prefill_tps
                + request.workload.output_tokens / candidate.decode_tps
            )
            delta = ((candidate_latency / baseline_latency) - 1) * 100
            if delta <= -GUARD_BAND_PERCENT:
                verdict = Verdict.ENABLE
                reason = f"Total latency improves by {abs(delta):.1f}% for this prompt/output shape."
            elif delta >= GUARD_BAND_PERCENT:
                verdict = Verdict.DISABLE
                reason = f"Total latency regresses by {delta:.1f}% because prefill dominates."
            else:
                reason = f"The {delta:+.1f}% total-latency change is inside the {GUARD_BAND_PERCENT:.0f}% guard band."

    if candidate.role == "control":
        verdict = Verdict.MEASURE
        reason = "This is an isolation control, not a deployable candidate."
    if "circular-ceiling" in risks:
        verdict = Verdict.MEASURE
        reason = "This circular arm is a measured ceiling, not a production recommendation."

    return CandidateReport(
        run_id=candidate.id,
        label=candidate.label,
        evidence=candidate.evidence,
        verdict=verdict,
        reason=reason,
        compatible=compatible,
        budget_ok=budget_ok,
        decode_tps=candidate.decode_tps,
        prefill_tps=candidate.prefill_tps,
        coverage=candidate.coverage,
        baseline_latency_s=baseline_latency,
        candidate_latency_s=candidate_latency,
        delta_percent=delta,
        break_even_prompt_output_ratio=_break_even_ratio(baseline, candidate),
        vram_required_gb=candidate.model_vram_gb,
        ram_required_gb=candidate.ram_required_gb,
        protocol_signature=candidate.protocol.signature,
        risk_flags=risks,
    )


def analyze(request: AnalysisRequest) -> AnalysisReport:
    fixture = get_fixture(request.fixture_id)
    hardware = request.hardware or fixture.hardware
    baselines = [run for run in fixture.runs if run.role == "baseline"]
    if len(baselines) != 1:
        raise ValueError("fixture must contain exactly one baseline")
    baseline = baselines[0]
    selected = [run for run in fixture.runs if run.role != "baseline"]
    if request.candidate_ids is not None:
        wanted = set(request.candidate_ids)
        selected = [run for run in selected if run.id in wanted]
        unknown = wanted - {run.id for run in fixture.runs}
        if unknown:
            raise ValueError(f"unknown candidate ids: {', '.join(sorted(unknown))}")
    reports = [_analyze_candidate(baseline, run, request, fixture, hardware) for run in selected]
    rank = {Verdict.ENABLE: 0, Verdict.MEASURE: 1, Verdict.DISABLE: 2}

    def score(report: CandidateReport) -> tuple[int, float]:
        if "isolation-control" in report.risk_flags:
            return 3, float("inf")
        if report.delta_percent is None:
            numeric = float("inf")
        elif request.workload.objective == Objective.DECODE_THROUGHPUT:
            numeric = -report.delta_percent
        else:
            numeric = report.delta_percent
        return rank[report.verdict], numeric

    reports.sort(key=score)
    deployable = [report for report in reports if "circular-ceiling" not in report.risk_flags and report.run_id != "hot0"]
    recommendation = deployable[0] if deployable else None
    verdict = recommendation.verdict if recommendation else Verdict.MEASURE
    canonical: float | None = None
    assumptions = list(fixture.limitations)
    if fixture.activation_profile is not None:
        canonical = canonical_coverage(fixture.activation_profile)
        expected = fixture.activation_profile.expected_coverage
        if expected is not None and abs(canonical - expected) > 0.001:
            raise ValueError(f"fixture coverage drift: computed {canonical:.4f}, expected {expected:.4f}")
        assumptions.append("Coverage is the unweighted mean of per-layer covered-hit fractions.")
    summary = (
        recommendation.reason
        if recommendation
        else "No deployable candidate has sufficient compatible evidence."
    )
    return AnalysisReport(
        fixture_id=fixture.id,
        fixture_name=fixture.name,
        generated_at=datetime.now(timezone.utc),
        workload=request.workload,
        hardware=hardware,
        baseline_run_id=baseline.id,
        verdict=verdict,
        recommendation_id=recommendation.run_id if recommendation else None,
        summary=summary,
        canonical_coverage=canonical,
        candidates=reports,
        assumptions=assumptions,
    )
