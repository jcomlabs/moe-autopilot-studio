from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

from moe_autopilot_studio.models import CommandSpec, ProtocolFingerprint, RunSpec
from moe_autopilot_studio.runner import ALLOWED_EXECUTABLES, RunManager
from moe_autopilot_studio.storage import StudioStore


async def wait_for_status(manager: RunManager, run_id: str, statuses: set[str], timeout: float = 5) -> str:
    async with asyncio.timeout(timeout):
        while True:
            record = manager.get(run_id)
            assert record is not None
            if record.status in statuses:
                return record.status
            await asyncio.sleep(0.02)


@pytest.fixture
def allow_python() -> None:
    name = Path(sys.executable).name.lower()
    ALLOWED_EXECUTABLES.add(name)
    yield
    ALLOWED_EXECUTABLES.discard(name)


@pytest.mark.asyncio
async def test_runner_captures_argv_output_and_return_code(tmp_path: Path, allow_python: None) -> None:
    manager = RunManager(StudioStore(tmp_path / "studio.db"))
    spec = RunSpec(
        label="capture",
        protocol=ProtocolFingerprint(instrument="test", model_id="model", build_id="build"),
        commands=[CommandSpec(executable=sys.executable, argv=["-c", "print('argv-ok')"], timeout_seconds=10)],
    )
    queued = await manager.create(spec)
    assert await wait_for_status(manager, queued.id, {"completed", "failed"}) == "completed"
    record = manager.get(queued.id)
    assert record is not None
    assert record.return_codes == [0]
    assert "argv-ok" in record.stdout_tail


@pytest.mark.asyncio
async def test_runner_cancel_stops_only_its_active_process(tmp_path: Path, allow_python: None) -> None:
    manager = RunManager(StudioStore(tmp_path / "studio.db"))
    spec = RunSpec(
        label="cancel",
        protocol=ProtocolFingerprint(instrument="test", model_id="model", build_id="build"),
        commands=[CommandSpec(executable=sys.executable, argv=["-c", "import time; time.sleep(30)"], timeout_seconds=60)],
    )
    queued = await manager.create(spec)
    assert await wait_for_status(manager, queued.id, {"running"}) == "running"
    cancelled = await manager.cancel(queued.id)
    assert cancelled.status == "cancelled"
    assert await wait_for_status(manager, queued.id, {"cancelled"}) == "cancelled"
    await asyncio.sleep(0.05)
    assert queued.id not in manager._processes
