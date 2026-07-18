from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceGrade(str, Enum):
    MEASURED = "measured"
    DERIVED = "derived"
    ESTIMATED = "estimated"


class Verdict(str, Enum):
    ENABLE = "ENABLE"
    DISABLE = "DISABLE"
    MEASURE = "MEASURE"


class Objective(str, Enum):
    TOTAL_LATENCY = "total_latency"
    DECODE_THROUGHPUT = "decode_throughput"


class ProtocolFingerprint(StrictModel):
    instrument: str
    model_id: str
    build_id: str
    flags: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @computed_field
    @property
    def signature(self) -> str:
        raw = self.model_dump(exclude={"signature"})
        payload = json.dumps(raw, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class WorkloadIntent(StrictModel):
    description: str = "Generation-heavy local chat"
    prompt_tokens: int = Field(default=500, ge=0, le=2_000_000)
    output_tokens: int = Field(default=300, ge=1, le=1_000_000)
    objective: Objective = Objective.TOTAL_LATENCY


class HardwareProfile(StrictModel):
    name: str = "Windows consumer GPU"
    vram_total_gb: float = Field(default=32.0, gt=0)
    vram_baseline_gb: float = Field(default=1.0, ge=0)
    vram_reserve_gb: float = Field(default=0.5, ge=0)
    ram_budget_gb: float = Field(default=48.0, gt=0)
    ram_bandwidth_gbps: float = Field(default=42.0, gt=0)
    vram_bandwidth_gbps: float = Field(default=1050.0, gt=0)

    @property
    def model_vram_budget_gb(self) -> float:
        return max(0.0, self.vram_total_gb - self.vram_baseline_gb - self.vram_reserve_gb)


class ModelProfile(StrictModel):
    id: str
    name: str
    architecture: str
    layers: int = Field(gt=0)
    expert_count: int = Field(gt=0)
    experts_used: int = Field(gt=0)
    activation_family: str
    notes: list[str] = Field(default_factory=list)


class MeasuredRun(StrictModel):
    id: str
    label: str
    role: Literal["baseline", "candidate", "control"]
    protocol: ProtocolFingerprint
    evidence: EvidenceGrade
    decode_tps: float | None = Field(default=None, gt=0)
    prefill_tps: float | None = Field(default=None, gt=0)
    coverage: float | None = Field(default=None, ge=0, le=1)
    hot_n: int | None = Field(default=None, ge=0)
    n_cpu_moe: int = Field(default=0, ge=0)
    model_vram_gb: float = Field(default=0, ge=0)
    ram_required_gb: float = Field(default=0, ge=0)
    repetitions: list[float] = Field(default_factory=list)
    source_hashes: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ActivationProfile(StrictModel):
    layers: dict[str, list[int]]
    hotlist: dict[str, list[int]]
    hot_n: int = Field(gt=0)
    expected_coverage: float | None = Field(default=None, ge=0, le=1)

    @field_validator("layers")
    @classmethod
    def non_empty_counts(cls, value: dict[str, list[int]]) -> dict[str, list[int]]:
        if not value or any(not counts for counts in value.values()):
            raise ValueError("activation layers must contain counts")
        return value


class FixtureBundle(StrictModel):
    id: str
    name: str
    summary: str
    model: ModelProfile
    hardware: HardwareProfile
    default_workload: WorkloadIntent
    runs: list[MeasuredRun]
    activation_profile: ActivationProfile | None = None
    limitations: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class AnalysisRequest(StrictModel):
    fixture_id: str
    workload: WorkloadIntent
    hardware: HardwareProfile | None = None
    candidate_ids: list[str] | None = None


class CandidateReport(StrictModel):
    run_id: str
    label: str
    evidence: EvidenceGrade
    verdict: Verdict
    reason: str
    compatible: bool
    budget_ok: bool
    decode_tps: float | None = None
    prefill_tps: float | None = None
    coverage: float | None = None
    baseline_latency_s: float | None = None
    candidate_latency_s: float | None = None
    delta_percent: float | None = None
    break_even_prompt_output_ratio: float | None = None
    vram_required_gb: float
    ram_required_gb: float
    protocol_signature: str
    risk_flags: list[str] = Field(default_factory=list)


class AnalysisReport(StrictModel):
    fixture_id: str
    fixture_name: str
    generated_at: datetime
    workload: WorkloadIntent
    hardware: HardwareProfile
    baseline_run_id: str
    verdict: Verdict
    recommendation_id: str | None
    summary: str
    canonical_coverage: float | None = None
    candidates: list[CandidateReport]
    assumptions: list[str] = Field(default_factory=list)


class CommandSpec(StrictModel):
    executable: str
    argv: list[str] = Field(default_factory=list)
    env: dict[str, str] = Field(default_factory=dict)
    cwd: str | None = None
    timeout_seconds: int = Field(default=900, ge=1, le=86_400)

    @field_validator("executable")
    @classmethod
    def executable_required(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("executable cannot be empty")
        return value


class RunSpec(StrictModel):
    label: str
    commands: list[CommandSpec] = Field(min_length=1, max_length=16)
    protocol: ProtocolFingerprint


class RunRecord(StrictModel):
    id: str
    label: str
    status: Literal["queued", "running", "completed", "failed", "cancelled"]
    created_at: datetime
    updated_at: datetime
    spec: RunSpec
    current_command: int = 0
    return_codes: list[int] = Field(default_factory=list)
    stdout_tail: str = ""
    stderr_tail: str = ""
    vram_baseline_mb: int | None = None
    error: str | None = None


class ImportRequest(StrictModel):
    kind: Literal["profile", "hotlist", "llama_bench", "server_timing"]
    content: str
    filename: str = "upload"


class ImportResult(StrictModel):
    kind: str
    summary: dict[str, Any]


class CodexAccount(StrictModel):
    available: bool
    authenticated: bool
    auth_mode: str | None = None
    plan_type: str | None = None
    email: str | None = None
    backend: Literal["app-server", "exec", "offline"] = "offline"
    error: str | None = None


class CodexLoginResult(StrictModel):
    login_id: str | None = None
    auth_url: str | None = None
    verification_url: str | None = None
    user_code: str | None = None
    status: str


class AdvisorRequest(StrictModel):
    user_intent: str = Field(max_length=4000)
    report: AnalysisReport


class AdvisorDecision(StrictModel):
    recommendation_id: str | None
    rationale: str
    risk_flags: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    backend: Literal["app-server", "exec", "offline"]
    model: str


class ExportRequest(StrictModel):
    format: Literal["json", "markdown", "html", "powershell"]
    report: AnalysisReport
    run_spec: RunSpec | None = None
