from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

from moe_autopilot_studio import codex_client
from moe_autopilot_studio.codex_client import CodexBridge, CodexProtocolError, _parse_decision
from moe_autopilot_studio.engine import analyze
from moe_autopilot_studio.fixtures import get_fixture
from moe_autopilot_studio.models import AdvisorRequest, AnalysisRequest


def advisor_request() -> AdvisorRequest:
    fixture = get_fixture("coder-next-e2e")
    report = analyze(AnalysisRequest(fixture_id=fixture.id, workload=fixture.default_workload))
    return AdvisorRequest(user_intent="Interactive chat", report=report)


def test_advisor_rejects_unknown_id_and_numbers() -> None:
    request = advisor_request()
    with pytest.raises(CodexProtocolError, match="unknown"):
        _parse_decision('{"recommendation_id":"invented","rationale":"x","risk_flags":[],"assumptions":[]}', request, "app-server", "gpt-5.6-sol")
    with pytest.raises(CodexProtocolError, match="unsupported numeric"):
        _parse_decision('{"recommendation_id":"hot96","rationale":"This gives 999999 tok/s","risk_flags":[],"assumptions":[]}', request, "app-server", "gpt-5.6-sol")


@pytest.mark.asyncio
async def test_app_server_protocol_and_chatgpt_auth(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake = tmp_path / "fake_codex.py"
    decision = {
        "recommendation_id": "hot96",
        "rationale": "The measured total latency improves by 4.4%.",
        "risk_flags": [],
        "assumptions": [],
    }
    decision_text = json.dumps(decision)
    completed_item = json.dumps({"method": "item/completed", "params": {"turnId": "turn_test", "item": {"type": "agentMessage", "text": decision_text}}})
    completed_turn = json.dumps({"method": "turn/completed", "params": {"turn": {"id": "turn_test"}}})
    fake.write_text(
        "import json,sys\n"
        "for line in sys.stdin:\n"
        " m=json.loads(line); method=m.get('method'); mid=m.get('id')\n"
        " if method=='initialize': print(json.dumps({'id':mid,'result':{'userAgent':'fake'}}),flush=True)\n"
        " elif method=='account/read': print(json.dumps({'id':mid,'result':{'account':{'type':'chatgpt','planType':'plus'}}}),flush=True)\n"
        " elif method=='thread/start': print(json.dumps({'id':mid,'result':{'thread':{'id':'thr_test'}}}),flush=True)\n"
        " elif method=='turn/start':\n"
        "  print(json.dumps({'id':mid,'result':{'turn':{'id':'turn_test'}}}),flush=True)\n"
        f"  print({completed_item!r},flush=True)\n"
        f"  print({completed_turn!r},flush=True)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(codex_client, "codex_command", lambda: [sys.executable, str(fake)])
    monkeypatch.setattr(codex_client, "data_dir", lambda: tmp_path)
    bridge = CodexBridge()
    bridge.scratch = tmp_path
    try:
        account = await bridge.account()
        assert account.authenticated is True
        result = await bridge.advise(advisor_request())
        assert result.backend == "app-server"
        assert result.recommendation_id == "hot96"
    finally:
        await bridge.stop()
