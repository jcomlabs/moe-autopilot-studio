from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

from moe_autopilot_studio.models import CommandSpec, ProtocolFingerprint, RunSpec
from moe_autopilot_studio.runner import ALLOWED_EXECUTABLES, RunManager, validate_run_spec
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


@pytest.mark.asyncio
async def test_runner_does_not_inherit_provider_credentials(
    tmp_path: Path, allow_python: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XIAOMI_API_KEY", "must-not-reach-child")
    manager = RunManager(StudioStore(tmp_path / "studio.db"))
    spec = RunSpec(
        label="sanitized-env",
        protocol=ProtocolFingerprint(instrument="test", model_id="model", build_id="build"),
        commands=[
            CommandSpec(
                executable=sys.executable,
                argv=["-c", "import os; print(os.getenv('XIAOMI_API_KEY', 'missing'))"],
                timeout_seconds=10,
            )
        ],
    )
    queued = await manager.create(spec)
    assert await wait_for_status(manager, queued.id, {"completed", "failed"}) == "completed"
    record = manager.get(queued.id)
    assert record is not None
    assert "missing" in record.stdout_tail
    assert "must-not-reach-child" not in record.stdout_tail


@pytest.mark.asyncio
async def test_runner_redacts_secrets_from_persisted_output(tmp_path: Path, allow_python: None) -> None:
    manager = RunManager(StudioStore(tmp_path / "studio.db"))
    spec = RunSpec(
        label="redacted-output",
        protocol=ProtocolFingerprint(instrument="test", model_id="model", build_id="build"),
        commands=[
            CommandSpec(
                executable=sys.executable,
                argv=["-c", "print('sk-' + '1234567890abcdefghijkl')"],
                timeout_seconds=10,
            )
        ],
    )
    queued = await manager.create(spec)
    assert await wait_for_status(manager, queued.id, {"completed", "failed"}) == "completed"
    record = manager.get(queued.id)
    assert record is not None
    assert "[REDACTED]" in record.stdout_tail
    assert "sk-" not in record.stdout_tail


@pytest.mark.asyncio
async def test_runner_persists_the_tail_of_long_output(tmp_path: Path, allow_python: None) -> None:
    manager = RunManager(StudioStore(tmp_path / "studio.db"))
    spec = RunSpec(
        label="long-output",
        protocol=ProtocolFingerprint(instrument="test", model_id="model", build_id="build"),
        commands=[
            CommandSpec(
                executable=sys.executable,
                argv=["-c", "print('x' * 25000); print('final-marker')"],
                timeout_seconds=10,
            )
        ],
    )
    queued = await manager.create(spec)
    assert await wait_for_status(manager, queued.id, {"completed", "failed"}) == "completed"
    record = manager.get(queued.id)
    assert record is not None
    assert "final-marker" in record.stdout_tail
    assert len(record.stdout_tail) <= 20_000


@pytest.mark.asyncio
async def test_runner_timeout_is_persisted(tmp_path: Path, allow_python: None) -> None:
    manager = RunManager(StudioStore(tmp_path / "studio.db"))
    spec = RunSpec(
        label="timeout",
        protocol=ProtocolFingerprint(instrument="test", model_id="model", build_id="build"),
        commands=[
            CommandSpec(
                executable=sys.executable,
                argv=["-c", "import time; time.sleep(30)"],
                timeout_seconds=1,
            )
        ],
    )
    queued = await manager.create(spec)
    assert await wait_for_status(manager, queued.id, {"failed"}, timeout=5) == "failed"
    record = manager.get(queued.id)
    assert record is not None
    assert record.error == "command 1 timed out"


def test_runner_rejects_public_server_bind(tmp_path: Path) -> None:
    executable = tmp_path / "llama-server.exe"
    executable.write_text("placeholder", encoding="utf-8")
    spec = RunSpec(
        label="unsafe-bind",
        protocol=ProtocolFingerprint(instrument="test", model_id="model", build_id="build"),
        commands=[CommandSpec(executable=str(executable), argv=["--host", "0.0.0.0"])],
    )
    with pytest.raises(ValueError, match="loopback"):
        validate_run_spec(spec)
