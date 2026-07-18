from __future__ import annotations

import json

import pytest

from moe_autopilot_studio.models import ImportRequest
from moe_autopilot_studio.parsers import parse_import


def test_server_import_drops_prompt_content() -> None:
    content = json.dumps({"choices": [{"message": {"content": "private"}}], "timings": {"predicted_per_second": 91.5}})
    result = parse_import(ImportRequest(kind="server_timing", content=content, filename="run.json"))
    assert result.summary == {"filename": "run.json", "decode_tps": 91.5, "repetitions": [91.5]}
    assert "private" not in result.model_dump_json()


def test_hotlist_rejects_duplicate_experts() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        parse_import(ImportRequest(kind="hotlist", content="0 1 1", filename="bad.hotlist"))


def test_profile_requires_integer_counts() -> None:
    with pytest.raises(ValueError, match="invalid counts"):
        parse_import(ImportRequest(kind="profile", content='{"layers":{"0":{"counts":[1,-1]}}}', filename="bad.json"))

