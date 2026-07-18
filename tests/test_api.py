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


def test_every_fixture_analyzes_and_exports_in_public_formats() -> None:
    with TestClient(app) as client:
        fixtures = client.get("/api/fixtures").json()["fixtures"]
        assert len(fixtures) >= 4
        for fixture in fixtures:
            response = client.post(
                "/api/analyze",
                json={
                    "fixture_id": fixture["id"],
                    "workload": fixture["default_workload"],
                    "hardware": fixture["hardware"],
                },
            )
            assert response.status_code == 200, fixture["id"]
            report = response.json()
            for export_format in ("json", "markdown", "html"):
                exported = client.post(
                    "/api/export",
                    json={"format": export_format, "report": report, "run_spec": None},
                )
                assert exported.status_code == 200, (fixture["id"], export_format)
                assert exported.content


def test_import_api_validates_supported_formats_and_size() -> None:
    with TestClient(app) as client:
        cases = (
            ("hotlist", "0 1 2\n1 3 4", "sample.hotlist"),
            ("profile", '{"layers":{"0":{"counts":[1,2,3]}}}', "profile.json"),
            ("server_timing", '{"timings":{"predicted_per_second":88.5}}', "timing.json"),
            ("llama_bench", '[{"n_prompt":128,"n_gen":0,"avg_ts":54.2}]', "bench.json"),
        )
        for kind, content, filename in cases:
            response = client.post(
                "/api/import", json={"kind": kind, "content": content, "filename": filename}
            )
            assert response.status_code == 200, kind
            assert response.json()["summary"]["filename"] == filename

        invalid = client.post(
            "/api/import", json={"kind": "hotlist", "content": "0 1 1", "filename": "bad.hotlist"}
        )
        assert invalid.status_code == 400


def test_hosted_mode_blocks_local_capabilities(monkeypatch) -> None:
    monkeypatch.setenv("STUDIO_MODE", "hosted")
    with TestClient(app) as client:
        account = client.get("/api/codex/account")
        assert account.status_code == 200
        assert account.json()["backend"] == "offline"
        assert client.post("/api/codex/login").status_code == 403
        run = client.post(
            "/api/runs",
            json={
                "label": "hosted",
                "protocol": {"instrument": "test", "model_id": "x", "build_id": "x", "flags": {}},
                "commands": [{"executable": "llama-bench.exe", "argv": [], "env": {}}],
            },
        )
        assert run.status_code == 403


def test_advisor_rejects_tampered_report() -> None:
    with TestClient(app) as client:
        fixture = next(
            item for item in client.get("/api/fixtures").json()["fixtures"] if item["id"] == "coder-next-e2e"
        )
        report = client.post(
            "/api/analyze",
            json={"fixture_id": fixture["id"], "workload": fixture["default_workload"], "hardware": fixture["hardware"]},
        ).json()
        report["recommendation_id"] = "invented-candidate"
        response = client.post("/api/advisor", json={"user_intent": "test", "report": report})
        assert response.status_code == 400
        assert "deterministic engine" in response.json()["detail"]


def test_export_replaces_tampered_metrics_with_canonical_values() -> None:
    with TestClient(app) as client:
        fixture = next(
            item for item in client.get("/api/fixtures").json()["fixtures"] if item["id"] == "coder-next-e2e"
        )
        report = client.post(
            "/api/analyze",
            json={"fixture_id": fixture["id"], "workload": fixture["default_workload"], "hardware": fixture["hardware"]},
        ).json()
        report["summary"] = "fabricated export claim"
        exported = client.post("/api/export", json={"format": "json", "report": report, "run_spec": None})
        assert exported.status_code == 200
        exported_report = exported.json()
        assert exported_report["summary"] != "fabricated export claim"
        assert exported_report["recommendation_id"] == "hot96"
