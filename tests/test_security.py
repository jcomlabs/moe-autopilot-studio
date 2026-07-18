from __future__ import annotations

import pytest
from pydantic import ValidationError

from moe_autopilot_studio.models import CommandSpec
from moe_autopilot_studio.security import redact_secrets, sanitized_child_env


def test_child_environment_drops_credentials_and_keeps_runtime_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XIAOMI_API_KEY", "provider-secret")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "another-secret")
    monkeypatch.setenv("PATH", "runtime-path")
    env = sanitized_child_env({"AIPC_MOE_HOT_N": "96"})
    assert "XIAOMI_API_KEY" not in env
    assert "DEEPSEEK_API_KEY" not in env
    assert env["PATH"] == "runtime-path"
    assert env["AIPC_MOE_HOT_N"] == "96"


def test_run_spec_rejects_secret_keys_and_values() -> None:
    with pytest.raises(ValidationError, match="sensitive environment"):
        CommandSpec(executable="llama-bench.exe", env={"XIAOMI_API_KEY": "secret"})
    with pytest.raises(ValidationError, match="sensitive environment"):
        CommandSpec(executable="llama-bench.exe", env={"SAFE_NAME": "sk-1234567890abcdefghijkl"})


def test_error_redaction_covers_common_key_shapes() -> None:
    value = redact_secrets("Authorization: Bearer abcdefghijklmnop and sk-1234567890abcdefghijkl")
    assert "abcdefghijklmnop" not in value
    assert "sk-" not in value
    assert value.count("[REDACTED]") == 2


def test_redaction_can_preserve_log_lines() -> None:
    value = redact_secrets("first\nsk-1234567890abcdefghijkl\nlast", preserve_lines=True)
    assert value == "first\n[REDACTED]\nlast"


def test_run_spec_rejects_secrets_in_arguments() -> None:
    with pytest.raises(ValidationError, match="sensitive flags"):
        CommandSpec(executable="llama-bench.exe", argv=["--api-key", "sk-1234567890abcdefghijkl"])
    with pytest.raises(ValidationError, match="sensitive flags"):
        CommandSpec(executable="llama-bench.exe", argv=["--password", "short-value"])
