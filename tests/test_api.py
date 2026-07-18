from __future__ import annotations

from fastapi.testclient import TestClient

from moe_autopilot_studio.app import app


def test_judge_flow_and_export() -> None:
    with TestClient(app) as client:
        fixture_data = client.get("/api/fixtures")
        assert fixture_data.status_code == 200
        fixtures = fixture_data.json()["fixtures"]
        fixture = next(item for item in fixtures if item["id"] == "coder-next-e2e")
        response = client.post(
            "/api/analyze",
            json={"fixture_id": fixture["id"], "workload": fixture["default_workload"], "hardware": fixture["hardware"]},
        )
        assert response.status_code == 200
        report = response.json()
        assert report["verdict"] == "ENABLE"
        exported = client.post("/api/export", json={"format": "html", "report": report, "run_spec": None})
        assert exported.status_code == 200
        assert "deterministic" in exported.text


def test_runner_rejects_arbitrary_executable() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/runs",
            json={
                "label": "unsafe",
                "protocol": {"instrument": "test", "model_id": "x", "build_id": "x", "flags": {}},
                "commands": [{"executable": "powershell.exe", "argv": ["-Command", "whoami"], "env": {}}],
            },
        )
        assert response.status_code == 400
        assert "only permits" in response.json()["detail"]
