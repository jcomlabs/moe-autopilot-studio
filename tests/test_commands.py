from __future__ import annotations

import sys
from pathlib import Path

import pytest

from moe_autopilot_studio.commands import render_powershell, run_profiler_atomic
from moe_autopilot_studio.models import CommandSpec


def test_powershell_renderer_quotes_untrusted_paths() -> None:
    hostile = "C:\\models\\x'; Write-Host PWN; '.gguf"
    rendered = render_powershell(
        CommandSpec(executable="C:\\llama tools\\llama-server.exe", argv=["-m", hostile], env={"AIPC_MOE_HOT_LIST": hostile})
    )
    assert "x''; Write-Host PWN; ''.gguf" in rendered
    assert "& 'C:\\llama tools\\llama-server.exe'" in rendered


def test_profiler_failure_preserves_existing_outputs(tmp_path: Path) -> None:
    hotlist = tmp_path / "session.hotlist"
    profile = tmp_path / "session.json"
    hotlist.write_text("old-hot", encoding="utf-8")
    profile.write_text("old-profile", encoding="utf-8")
    command = CommandSpec(executable=sys.executable, argv=["-c", "raise SystemExit(9)"])
    with pytest.raises(RuntimeError, match="profiler failed"):
        run_profiler_atomic(command, hotlist, profile)
    assert hotlist.read_text(encoding="utf-8") == "old-hot"
    assert profile.read_text(encoding="utf-8") == "old-profile"


def test_profiler_publishes_both_outputs_atomically(tmp_path: Path) -> None:
    hotlist = tmp_path / "session.hotlist"
    profile = tmp_path / "session.json"
    code = (
        "from pathlib import Path; "
        "Path('aipc_moe_profile.hotlist').write_text('0 1 2'); "
        "Path('aipc_moe_profile.json').write_text('{\"layers\":{}}')"
    )
    run_profiler_atomic(CommandSpec(executable=sys.executable, argv=["-c", code]), hotlist, profile)
    assert hotlist.read_text(encoding="utf-8") == "0 1 2"
    assert profile.read_text(encoding="utf-8") == '{"layers":{}}'


def test_profiler_timeout_preserves_existing_outputs(tmp_path: Path) -> None:
    hotlist = tmp_path / "session.hotlist"
    profile = tmp_path / "session.json"
    hotlist.write_text("old-hot", encoding="utf-8")
    profile.write_text("old-profile", encoding="utf-8")
    command = CommandSpec(executable=sys.executable, argv=["-c", "import time; time.sleep(5)"], timeout_seconds=1)
    with pytest.raises(TimeoutError):
        run_profiler_atomic(command, hotlist, profile)
    assert hotlist.read_text(encoding="utf-8") == "old-hot"
    assert profile.read_text(encoding="utf-8") == "old-profile"


def test_profiler_missing_output_preserves_existing_outputs(tmp_path: Path) -> None:
    hotlist = tmp_path / "session.hotlist"
    profile = tmp_path / "session.json"
    hotlist.write_text("old-hot", encoding="utf-8")
    profile.write_text("old-profile", encoding="utf-8")
    command = CommandSpec(executable=sys.executable, argv=["-c", "print('success without files')"])
    with pytest.raises(RuntimeError, match="did not produce both outputs"):
        run_profiler_atomic(command, hotlist, profile)
    assert hotlist.read_text(encoding="utf-8") == "old-hot"
    assert profile.read_text(encoding="utf-8") == "old-profile"
