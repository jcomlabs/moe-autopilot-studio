from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from moe_autopilot_studio.models import ProtocolFingerprint, RunRecord, RunSpec, CommandSpec
from moe_autopilot_studio.storage import StudioStore


def test_run_roundtrip(tmp_path: Path) -> None:
    store = StudioStore(tmp_path / "studio.db")
    now = datetime.now(timezone.utc)
    spec = RunSpec(label="test", protocol=ProtocolFingerprint(instrument="x", model_id="m", build_id="b"), commands=[CommandSpec(executable="llama-bench.exe")])
    record = RunRecord(id="abc", label="test", status="queued", created_at=now, updated_at=now, spec=spec)
    store.save_run(record)
    loaded = store.get_run("abc")
    assert loaded is not None
    assert loaded.spec.protocol.signature == spec.protocol.signature
