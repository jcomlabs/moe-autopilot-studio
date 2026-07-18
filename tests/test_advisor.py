from __future__ import annotations

import json

import httpx
import pytest

from moe_autopilot_studio.advisor import (
    AdvisorCouncil,
    OpenAICompatibleAdvisor,
    ProviderConfig,
    ProviderError,
    provider_configs_from_environment,
)
from moe_autopilot_studio.codex_client import CodexProtocolError
from moe_autopilot_studio.engine import analyze
from moe_autopilot_studio.fixtures import get_fixture
from moe_autopilot_studio.models import (
    AdvisorDecision,
    AdvisorRequest,
    AnalysisRequest,
    CodexAccount,
)


def advisor_request() -> AdvisorRequest:
    fixture = get_fixture("coder-next-e2e")
    report = analyze(AnalysisRequest(fixture_id=fixture.id, workload=fixture.default_workload))
    return AdvisorRequest(user_intent="Interactive chat", report=report)


def provider_response(request: AdvisorRequest, rationale: str = "Use the measured recommendation.") -> dict[str, object]:
    return {
        "model": "test-model",
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "content": json.dumps(
                        {
                            "recommendation_id": request.report.recommendation_id,
                            "rationale": rationale,
                            "risk_flags": [],
                            "assumptions": [],
                        }
                    )
                },
            }
        ],
    }


def test_provider_config_rejects_insecure_or_credentialed_urls() -> None:
    with pytest.raises(ValueError, match="HTTPS"):
        ProviderConfig(id="x", label="X", model="m", base_url="http://example.com/v1", api_key="test")
    with pytest.raises(ValueError, match="invalid"):
        ProviderConfig(id="x", label="X", model="m", base_url="https://user:pass@example.com/v1", api_key="test")


def test_invalid_environment_config_does_not_crash_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XIAOMI_API_KEY", "test-key-material")
    monkeypatch.setenv("XIAOMI_BASE_URL", "http://example.com/v1")
    configs, errors = provider_configs_from_environment()
    assert not any(config.id == "xiaomi" for config in configs)
    assert "xiaomi" in errors
    assert "test-key-material" not in errors["xiaomi"]


@pytest.mark.asyncio
async def test_openai_provider_validates_envelope_and_grounding() -> None:
    request = advisor_request()

    async def handler(http_request: httpx.Request) -> httpx.Response:
        assert http_request.headers["Authorization"] == "Bearer test-key"
        return httpx.Response(200, json=provider_response(request))

    provider = OpenAICompatibleAdvisor(
        ProviderConfig(id="xiaomi", label="Xiaomi", model="test-model", base_url="https://provider.test/v1", api_key="test-key"),
        transport=httpx.MockTransport(handler),
    )
    decision = await provider.advise(request)
    assert decision.backend == "xiaomi"
    assert decision.recommendation_id == request.report.recommendation_id


@pytest.mark.asyncio
async def test_openai_provider_rejects_bad_status_and_unsupported_claim() -> None:
    request = advisor_request()

    async def unauthorized(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="secret body must not escape")

    provider = OpenAICompatibleAdvisor(
        ProviderConfig(id="deepseek", label="DeepSeek", model="test-model", base_url="https://provider.test/v1", api_key="test-key"),
        transport=httpx.MockTransport(unauthorized),
    )
    with pytest.raises(ProviderError, match="HTTP 401") as error:
        await provider.advise(request)
    assert "secret body" not in str(error.value)

    async def invented(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=provider_response(request, "This produces 999999 tok/s."))

    provider.transport = httpx.MockTransport(invented)
    with pytest.raises(CodexProtocolError, match="unsupported numeric"):
        await provider.advise(request)


@pytest.mark.asyncio
async def test_provider_probe_requires_configured_model() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "another-model"}]})

    provider = OpenAICompatibleAdvisor(
        ProviderConfig(id="xiaomi", label="Xiaomi", model="required-model", base_url="https://provider.test/v1", api_key="test-key"),
        transport=httpx.MockTransport(handler),
    )
    available, _, error = await provider.probe()
    assert available is False
    assert error == "configured model was not advertised"


@pytest.mark.asyncio
async def test_provider_rejects_oversized_response_before_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    request = advisor_request()
    monkeypatch.setattr("moe_autopilot_studio.advisor.MAX_PROVIDER_RESPONSE_BYTES", 32)

    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"{" + b"x" * 128 + b"}")

    provider = OpenAICompatibleAdvisor(
        ProviderConfig(id="xiaomi", label="Xiaomi", model="m", base_url="https://provider.test/v1", api_key="x"),
        httpx.MockTransport(handler),
    )
    with pytest.raises(ProviderError, match="size limit"):
        await provider.advise(request)


class FakeCodex:
    model = "gpt-5.6-sol"

    def __init__(self) -> None:
        self.peer_count = -1

    async def account(self) -> CodexAccount:
        return CodexAccount(available=True, authenticated=True, backend="app-server", auth_mode="chatgpt")

    async def advise(self, request: AdvisorRequest, peers=None) -> AdvisorDecision:
        self.peer_count = len(peers or [])
        return AdvisorDecision(
            recommendation_id=request.report.recommendation_id,
            rationale="The council confirms the measured recommendation.",
            backend="app-server",
            model=self.model,
        )

    async def stop(self) -> None:
        return None


@pytest.mark.asyncio
async def test_council_runs_parallel_scouts_then_chatgpt_synthesis() -> None:
    request = advisor_request()

    async def accepted(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=provider_response(request))

    async def rejected(_: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="unavailable")

    providers = [
        OpenAICompatibleAdvisor(
            ProviderConfig(id="xiaomi", label="Xiaomi", model="mimo", base_url="https://xiaomi.test/v1", api_key="x"),
            httpx.MockTransport(accepted),
        ),
        OpenAICompatibleAdvisor(
            ProviderConfig(id="deepseek", label="DeepSeek", model="deepseek", base_url="https://deepseek.test/v1", api_key="x"),
            httpx.MockTransport(rejected),
        ),
    ]
    codex = FakeCodex()
    decision = await AdvisorCouncil(codex, providers).advise(request)  # type: ignore[arg-type]
    assert decision.backend == "moa"
    assert decision.quorum == 2
    assert codex.peer_count == 1
    assert [member.status for member in decision.members] == ["accepted", "rejected", "accepted"]
    assert all("unavailable" not in (member.error or "") for member in decision.members)


@pytest.mark.asyncio
async def test_unexpected_scout_failure_is_contained() -> None:
    request = advisor_request()

    async def broken(_: httpx.Request) -> httpx.Response:
        raise RuntimeError("unexpected provider failure")

    provider = OpenAICompatibleAdvisor(
        ProviderConfig(id="xiaomi", label="Xiaomi", model="mimo", base_url="https://xiaomi.test/v1", api_key="x"),
        httpx.MockTransport(broken),
    )
    decision = await AdvisorCouncil(FakeCodex(), [provider]).advise(request)  # type: ignore[arg-type]
    assert decision.backend == "app-server"
    assert [member.status for member in decision.members] == ["rejected", "accepted"]
