from __future__ import annotations

from copy import deepcopy

import pytest

from moe_autopilot_studio.coverage import canonical_coverage
from moe_autopilot_studio.engine import _analyze_candidate, analyze
from moe_autopilot_studio.fixtures import get_fixture
from moe_autopilot_studio.models import AnalysisRequest, Objective, Verdict


def test_session_fixture_reproduces_canonical_coverage() -> None:
    fixture = get_fixture("coder-next-decode")
    assert fixture.activation_profile is not None
    assert canonical_coverage(fixture.activation_profile) == pytest.approx(0.685557, abs=1e-6)
    report = analyze(AnalysisRequest(fixture_id=fixture.id, workload=fixture.default_workload))
    session = next(candidate for candidate in report.candidates if candidate.run_id == "session")
    assert session.verdict == Verdict.ENABLE
    assert session.coverage == pytest.approx(0.686)
    assert session.delta_percent == pytest.approx(22.22, abs=0.1)
    legacy = next(candidate for candidate in report.candidates if candidate.run_id == "generic")
    assert legacy.verdict == Verdict.MEASURE
    assert legacy.compatible is False


def test_e2e_break_even_is_recomputed_from_measured_arms() -> None:
    fixture = get_fixture("coder-next-e2e")
    report = analyze(AnalysisRequest(fixture_id=fixture.id, workload=fixture.default_workload))
    hot = next(candidate for candidate in report.candidates if candidate.run_id == "hot96")
    assert report.verdict == Verdict.ENABLE
    assert hot.break_even_prompt_output_ratio == pytest.approx(19.18, abs=0.02)
    assert hot.delta_percent == pytest.approx(-4.36, abs=0.02)
    assert any("historical write-up" in assumption for assumption in report.assumptions)


def test_prompt_heavy_workload_disables_split() -> None:
    fixture = get_fixture("coder-next-e2e")
    workload = fixture.default_workload.model_copy(
        update={"prompt_tokens": 16000, "output_tokens": 300, "objective": Objective.TOTAL_LATENCY}
    )
    report = analyze(AnalysisRequest(fixture_id=fixture.id, workload=workload))
    assert report.verdict == Verdict.DISABLE
    assert report.candidates[0].delta_percent == pytest.approx(3.91, abs=0.1)


def test_budget_gate_disables_candidate() -> None:
    fixture = get_fixture("qwen35-decode")
    hardware = fixture.hardware.model_copy(update={"vram_total_gb": 16.0})
    report = analyze(AnalysisRequest(fixture_id=fixture.id, workload=fixture.default_workload, hardware=hardware))
    assert report.verdict == Verdict.DISABLE
    assert "budget-exceeded" in report.candidates[0].risk_flags


def test_protocol_mismatch_is_not_compared() -> None:
    fixture = get_fixture("qwen35-decode")
    baseline = next(run for run in fixture.runs if run.role == "baseline")
    candidate = deepcopy(next(run for run in fixture.runs if run.role == "candidate"))
    candidate.protocol = candidate.protocol.model_copy(update={"instrument": "different"})
    request = AnalysisRequest(fixture_id=fixture.id, workload=fixture.default_workload)
    report = _analyze_candidate(baseline, candidate, request, fixture, fixture.hardware)
    assert report.verdict == Verdict.MEASURE
    assert report.compatible is False
    assert "protocol-mismatch" in report.risk_flags
