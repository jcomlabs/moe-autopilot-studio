from __future__ import annotations

import asyncio
import os
import shutil
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .models import RunRecord, RunSpec
from .storage import StudioStore


ALLOWED_EXECUTABLES = {
    "llama-bench",
    "llama-bench.exe",
    "llama-server",
    "llama-server.exe",
    "llama-aipc-moe-profile",
    "llama-aipc-moe-profile.exe",
}
TAIL_LIMIT = 20_000


def validate_run_spec(spec: RunSpec) -> None:
    for command in spec.commands:
        name = Path(command.executable).name.lower()
        if name not in ALLOWED_EXECUTABLES:
            raise ValueError(f"runner only permits known llama.cpp tools, got: {name}")
        resolved = Path(command.executable)
        if not resolved.is_file() and shutil.which(command.executable) is None:
            raise ValueError(f"executable not found: {command.executable}")
        if command.cwd and not Path(command.cwd).is_dir():
            raise ValueError(f"working directory not found: {command.cwd}")


def _vram_baseline_mb() -> int | None:
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
            check=False,
        )
        if result.returncode == 0:
            return int(result.stdout.strip().splitlines()[0])
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    return None


class RunManager:
    def __init__(self, store: StudioStore) -> None:
        self.store = store
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._processes: dict[str, asyncio.subprocess.Process] = {}
        self._lock = asyncio.Lock()

    async def create(self, spec: RunSpec) -> RunRecord:
        validate_run_spec(spec)
        now = datetime.now(timezone.utc)
        record = RunRecord(
            id=uuid.uuid4().hex,
            label=spec.label,
            status="queued",
            created_at=now,
            updated_at=now,
            spec=spec,
        )
        self.store.save_run(record)
        async with self._lock:
            self._tasks[record.id] = asyncio.create_task(self._execute(record.id))
        return record

    async def _execute(self, run_id: str) -> None:
        record = self.store.get_run(run_id)
        if record is None:
            return
        record.status = "running"
        record.vram_baseline_mb = await asyncio.to_thread(_vram_baseline_mb)
        record.updated_at = datetime.now(timezone.utc)
        self.store.save_run(record)
        try:
            for index, command in enumerate(record.spec.commands):
                record.current_command = index
                env = os.environ.copy()
                env.update(command.env)
                process = await asyncio.create_subprocess_exec(
                    command.executable,
                    *command.argv,
                    cwd=command.cwd,
                    env=env,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                async with self._lock:
                    self._processes[run_id] = process
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(), timeout=command.timeout_seconds
                    )
                except TimeoutError:
                    process.terminate()
                    await process.wait()
                    raise RuntimeError(f"command {index + 1} timed out")
                finally:
                    async with self._lock:
                        self._processes.pop(run_id, None)
                record.return_codes.append(process.returncode or 0)
                record.stdout_tail = (record.stdout_tail + stdout.decode("utf-8", "replace"))[-TAIL_LIMIT:]
                record.stderr_tail = (record.stderr_tail + stderr.decode("utf-8", "replace"))[-TAIL_LIMIT:]
                record.updated_at = datetime.now(timezone.utc)
                self.store.save_run(record)
                if process.returncode != 0:
                    raise RuntimeError(f"command {index + 1} failed with exit code {process.returncode}")
            record.status = "completed"
        except asyncio.CancelledError:
            record.status = "cancelled"
        except Exception as exc:
            record.status = "failed"
            record.error = str(exc)
        finally:
            record.updated_at = datetime.now(timezone.utc)
            self.store.save_run(record)
            async with self._lock:
                self._tasks.pop(run_id, None)
                self._processes.pop(run_id, None)

    async def cancel(self, run_id: str) -> RunRecord:
        async with self._lock:
            process = self._processes.get(run_id)
            task = self._tasks.get(run_id)
            if process and process.returncode is None:
                process.terminate()
            if task:
                task.cancel()
        record = self.store.get_run(run_id)
        if record is None:
            raise KeyError(run_id)
        if record.status in {"queued", "running"}:
            record.status = "cancelled"
            record.updated_at = datetime.now(timezone.utc)
            self.store.save_run(record)
        return record

    def get(self, run_id: str) -> RunRecord | None:
        return self.store.get_run(run_id)

    def list(self) -> list[RunRecord]:
        return self.store.list_runs()
