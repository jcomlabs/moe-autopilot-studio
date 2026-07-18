from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from .models import FixtureBundle
from .paths import fixtures_dir


@lru_cache(maxsize=1)
def load_fixtures() -> dict[str, FixtureBundle]:
    directory = fixtures_dir()
    fixtures: dict[str, FixtureBundle] = {}
    for path in sorted(directory.glob("*.json")):
        if path.name == "manifest.json":
            continue
        fixture = FixtureBundle.model_validate_json(path.read_text(encoding="utf-8"))
        if fixture.id in fixtures:
            raise ValueError(f"duplicate fixture id: {fixture.id}")
        fixtures[fixture.id] = fixture
    if not fixtures:
        raise RuntimeError(f"no fixtures found in {directory}")
    return fixtures


def get_fixture(fixture_id: str) -> FixtureBundle:
    try:
        return load_fixtures()[fixture_id]
    except KeyError as exc:
        raise KeyError(f"unknown fixture: {fixture_id}") from exc


def fixture_summaries() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for fixture in load_fixtures().values():
        result.append(
            {
                "id": fixture.id,
                "name": fixture.name,
                "summary": fixture.summary,
                "model": fixture.model.model_dump(),
                "hardware": fixture.hardware.model_dump(exclude_computed_fields=True),
                "default_workload": fixture.default_workload.model_dump(),
                "run_count": len(fixture.runs),
                "limitations": fixture.limitations,
                "has_activation_profile": fixture.activation_profile is not None,
                "provenance": fixture.provenance,
            }
        )
    return result


def manifest() -> dict[str, Any]:
    path = Path(fixtures_dir()) / "manifest.json"
    return json.loads(path.read_text(encoding="utf-8"))
