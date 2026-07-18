from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from .codex_client import CodexBridge
from .engine import analyze
from .exporters import export_report
from .fixtures import fixture_summaries, get_fixture, manifest
from .models import (
    AdvisorRequest,
    AnalysisRequest,
    ExportRequest,
    ImportRequest,
    RunSpec,
)
from .parsers import parse_import
from .paths import static_dir
from .runner import RunManager
from .storage import StudioStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = StudioStore()
    app.state.run_manager = RunManager(store)
    app.state.codex = CodexBridge(model=os.getenv("STUDIO_CODEX_MODEL", "gpt-5.6-sol"))
    yield
    await app.state.codex.stop()


app = FastAPI(
    title="MoE Autopilot Studio",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["127.0.0.1", "localhost", "testserver", "*.hf.space"],
)


def hosted_mode() -> bool:
    return os.getenv("STUDIO_MODE", "local").lower() == "hosted"


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": app.version,
        "mode": "hosted" if hosted_mode() else "local",
        "fixtures": len(fixture_summaries()),
    }


@app.get("/api/fixtures")
async def fixtures() -> dict[str, Any]:
    return {"fixtures": fixture_summaries(), "manifest": manifest()}


@app.get("/api/fixtures/{fixture_id}/runs")
async def fixture_runs(fixture_id: str) -> dict[str, Any]:
    try:
        fixture = get_fixture(fixture_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "id": fixture.id,
        "name": fixture.name,
        "runs": [run.model_dump(mode="json") for run in fixture.runs],
        "limitations": fixture.limitations,
        "provenance": fixture.provenance,
    }


@app.post("/api/analyze")
async def analyze_endpoint(request: AnalysisRequest):
    try:
        return analyze(request)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/import")
async def import_endpoint(request: ImportRequest):
    try:
        return parse_import(request)
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/runs")
async def list_runs(request: Request):
    return {"runs": request.app.state.run_manager.list()}


@app.post("/api/runs", status_code=202)
async def create_run(spec: RunSpec, request: Request):
    if hosted_mode():
        raise HTTPException(status_code=403, detail="The hosted demo is fixture-only")
    try:
        return await request.app.state.run_manager.create(spec)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str, request: Request):
    record = request.app.state.run_manager.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="run not found")
    return record


@app.post("/api/runs/{run_id}/cancel")
async def cancel_run(run_id: str, request: Request):
    if hosted_mode():
        raise HTTPException(status_code=403, detail="The hosted demo is fixture-only")
    try:
        return await request.app.state.run_manager.cancel(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="run not found") from exc


@app.get("/api/codex/account")
async def codex_account(request: Request):
    if hosted_mode():
        return {
            "available": False,
            "authenticated": False,
            "backend": "offline",
            "error": "Hosted demo uses deterministic fixture mode; connect ChatGPT in the Windows app.",
        }
    return await request.app.state.codex.account()


@app.post("/api/codex/login")
async def codex_login(request: Request, device_code: bool = False):
    if hosted_mode():
        raise HTTPException(status_code=403, detail="ChatGPT login is local-only")
    try:
        return await request.app.state.codex.login(device_code=device_code)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/api/advisor")
async def advisor(payload: AdvisorRequest, request: Request):
    canonical = analyze(
        AnalysisRequest(
            fixture_id=payload.report.fixture_id,
            workload=payload.report.workload,
            hardware=payload.report.hardware,
        )
    )
    if canonical.recommendation_id != payload.report.recommendation_id:
        raise HTTPException(status_code=400, detail="advisor report does not match the deterministic engine")
    safe_payload = AdvisorRequest(user_intent=payload.user_intent, report=canonical)
    if hosted_mode():
        from .codex_client import _offline_decision

        return _offline_decision(safe_payload, "hosted fixture mode")
    return await request.app.state.codex.advise(safe_payload)


@app.post("/api/export")
async def export(payload: ExportRequest):
    try:
        media_type, content = export_report(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    extension = {"application/json": "json", "text/markdown": "md", "text/html": "html", "text/plain": "ps1"}[media_type]
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="moe-autopilot-report.{extension}"'},
    )


frontend = static_dir()
if frontend.exists() and (frontend / "index.html").exists():
    app.mount("/", StaticFiles(directory=frontend, html=True), name="studio")
else:
    @app.get("/", response_class=HTMLResponse)
    async def missing_frontend() -> str:
        return "<h1>MoE Autopilot Studio</h1><p>Frontend not built. Run <code>npm run build</code> in frontend/.</p>"

