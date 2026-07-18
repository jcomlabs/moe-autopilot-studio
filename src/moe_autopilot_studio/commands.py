from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .models import CommandSpec
from .security import ENV_KEY, redact_secrets, sanitized_child_env


def quote_powershell(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def render_powershell(command: CommandSpec) -> str:
    lines: list[str] = []
    for key, value in sorted(command.env.items()):
        if not ENV_KEY.fullmatch(key):
            raise ValueError(f"invalid environment key: {key}")
        lines.append(f"$env:{key} = {quote_powershell(value)}")
    invocation = " ".join(
        ["&", quote_powershell(command.executable), *(quote_powershell(arg) for arg in command.argv)]
    )
    lines.append(invocation)
    return "\n".join(lines)


def server_command(
    binary_dir: str,
    model_path: str,
    n_cpu_moe: int,
    hotlist_path: str | None = None,
    hot_n: int = 96,
    context: int = 8192,
    port: int = 18201,
) -> CommandSpec:
    executable = str(Path(binary_dir) / ("llama-server.exe" if os.name == "nt" else "llama-server"))
    argv = [
        "-m", model_path, "-ngl", "999", "--n-cpu-moe", str(n_cpu_moe),
        "--no-mmap", "--poll", "100", "-c", str(context), "-t", "16", "--jinja", "--port", str(port),
    ]
    env: dict[str, str] = {}
    if hotlist_path and n_cpu_moe:
        env = {"AIPC_MOE_HOT_LIST": hotlist_path, "AIPC_MOE_HOT_N": str(hot_n)}
    return CommandSpec(executable=executable, argv=argv, env=env, timeout_seconds=1800)


def run_profiler_atomic(command: CommandSpec, hotlist_out: Path, profile_out: Path) -> None:
    """Run the profiler and publish both outputs only after a complete success."""
    with tempfile.TemporaryDirectory(prefix="moe-profile-") as temporary:
        cwd = Path(temporary)
        env = sanitized_child_env(command.env)
        try:
            completed = subprocess.run(
                [command.executable, *command.argv],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                timeout=command.timeout_seconds,
                shell=False,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError(f"profiler timed out after {command.timeout_seconds} seconds") from exc
        if completed.returncode != 0:
            raise RuntimeError(f"profiler failed ({completed.returncode}): {redact_secrets(completed.stderr[-2000:], 2000)}")
        generated_hotlist = cwd / "aipc_moe_profile.hotlist"
        generated_profile = cwd / "aipc_moe_profile.json"
        if not generated_hotlist.is_file() or not generated_profile.is_file():
            raise RuntimeError("profiler exited successfully but did not produce both outputs")
        hotlist_out.parent.mkdir(parents=True, exist_ok=True)
        profile_out.parent.mkdir(parents=True, exist_ok=True)
        staged_hotlist = hotlist_out.with_suffix(hotlist_out.suffix + ".tmp")
        staged_profile = profile_out.with_suffix(profile_out.suffix + ".tmp")
        shutil.copy2(generated_hotlist, staged_hotlist)
        shutil.copy2(generated_profile, staged_profile)
        staged_hotlist.replace(hotlist_out)
        staged_profile.replace(profile_out)
