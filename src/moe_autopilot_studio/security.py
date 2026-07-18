from __future__ import annotations

import os
import re
from collections.abc import Mapping


ENV_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SENSITIVE_NAMES = (
    "API_KEY",
    "ACCESS_KEY",
    "AUTHORIZATION",
    "BEARER",
    "COOKIE",
    "PASSWORD",
    "PASSWD",
    "PRIVATE_KEY",
    "SECRET",
    "SESSION_TOKEN",
    "TOKEN",
)
_SECRET_VALUES = re.compile(
    r"(?i)(?:sk|tp)-[a-z0-9_-]{16,}|bearer\s+[a-z0-9._~+/-]{12,}|"
    r"(?:api[_-]?key|token|secret|password)\s*[:=]\s*[^\s,;]+"
)


def is_sensitive_env_key(name: str) -> bool:
    upper = name.upper()
    return any(marker in upper for marker in _SENSITIVE_NAMES)


def looks_like_secret(value: str) -> bool:
    return bool(_SECRET_VALUES.search(value))


def validate_public_env(values: Mapping[str, str]) -> dict[str, str]:
    validated: dict[str, str] = {}
    for key, value in values.items():
        if not ENV_KEY.fullmatch(key):
            raise ValueError(f"invalid environment key: {key}")
        if is_sensitive_env_key(key) or looks_like_secret(value):
            raise ValueError(f"sensitive environment values are not permitted in RunSpec: {key}")
        validated[key] = value
    return validated


def validate_public_text(value: str, *, field: str) -> str:
    if "\x00" in value:
        raise ValueError(f"{field} cannot contain NUL bytes")
    if looks_like_secret(value):
        raise ValueError(f"sensitive values are not permitted in {field}")
    return value


def validate_public_argv(values: list[str]) -> list[str]:
    validated: list[str] = []
    for value in values:
        normalized = ""
        if value.startswith(("-", "/")) and not any(character.isspace() for character in value):
            normalized = value.lstrip("-/").split("=", 1)[0].replace("-", "_")
        if normalized and is_sensitive_env_key(normalized):
            raise ValueError(f"sensitive flags are not permitted in argv: {value}")
        validated.append(validate_public_text(value, field="argv"))
    return validated


def sanitized_child_env(additions: Mapping[str, str] | None = None) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if not is_sensitive_env_key(key)}
    if additions:
        env.update(validate_public_env(additions))
    return env


def redact_secrets(value: object, limit: int = 500, *, preserve_lines: bool = False) -> str:
    text = str(value)
    if not preserve_lines:
        text = text.replace("\r", " ").replace("\n", " ")
    text = _SECRET_VALUES.sub("[REDACTED]", text)
    return text[:limit]
