"""
Ambient AI Scribe — Healthcare PoC Application
================================================
Minimal FastAPI service simulating a medical transcription/summarization system.
Serves as the workload governed by the GenAIOps Quality Gate framework.

Endpoints:
    POST /transcribe  — Mock medical transcription (no real LLM call)
    GET  /health      — Kubernetes liveness/readiness probe
    GET  /metrics     — Prometheus metrics (Pillar S5)

Design Decisions:
    - Mock mode (Option B): No Azure OpenAI costs during development
    - Traceability fields (DP2): model_version, run_id, pipeline_id in every response
    - Prometheus metrics: Required for G-OPS-03 (Performance Monitoring & Drift Detection)
"""

import os
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# ---------------------------------------------------------------------------
# Configuration (from environment / ConfigMap)
# ---------------------------------------------------------------------------
MODEL_VERSION = os.getenv("MODEL_VERSION", "mock-v1.0.0")
PIPELINE_ID = os.getenv("PIPELINE_ID", "local-dev")

# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Ambient AI Scribe",
    version="1.0.0",
    description="Healthcare PoC — GenAIOps Quality Gate Reference Architecture",
)

# ---------------------------------------------------------------------------
# Prometheus Metrics (Pillar S5 — Monitoring & PMS)
# ---------------------------------------------------------------------------
REQUEST_COUNT = Counter(
    "scribe_requests_total",
    "Total number of transcription requests",
    ["endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "scribe_latency_seconds",
    "Request latency in seconds",
    ["endpoint"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.0, 5.0],
)
MOCK_MODE = Gauge(
    "scribe_mock_mode",
    "1 if running in mock mode (no real LLM), 0 if live",
)
MOCK_MODE.set(1)


# ---------------------------------------------------------------------------
# POST /transcribe — Mock Medical Transcription
# ---------------------------------------------------------------------------
@app.post("/transcribe")
async def transcribe(request: Request):
    """
    Simulates medical transcription/summarization.

    In production: forwards audio/text to Azure OpenAI and returns structured summary.
    In mock mode: returns a deterministic demo response for walkthrough reproducibility.

    Traceability (DP2): Every response carries model_version, run_id, pipeline_id
    so the Evidence Store can link inference results to gate decisions.
    """
    start = time.time()
    run_id = str(uuid.uuid4())

    body = await request.json()
    input_text = body.get("text", "")

    # --- Mock response (Option B: no LLM costs) ---
    mock_summary = (
        "Patient berichtet ueber wiederkehrende Kopfschmerzen seit zwei Wochen. "
        "Keine neurologischen Auffaelligkeiten. "
        "Empfehlung: Kontrolltermin in 4 Wochen, bei Verschlechterung frueher."
    )

    duration = time.time() - start

    REQUEST_COUNT.labels(endpoint="/transcribe", status="success").inc()
    REQUEST_LATENCY.labels(endpoint="/transcribe").observe(duration)

    return JSONResponse(
        content={
            "summary": mock_summary,
            "input_length": len(input_text),
            "model_version": MODEL_VERSION,
            "run_id": run_id,
            "pipeline_id": PIPELINE_ID,
            "mock_mode": True,
            "processing_time_seconds": round(duration, 4),
        }
    )


# ---------------------------------------------------------------------------
# GET /health — Kubernetes Probe
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    """
    Liveness and readiness probe for Kubernetes.
    Returns 200 if the service is operational.
    """
    return {"status": "healthy", "model_version": MODEL_VERSION}


# ---------------------------------------------------------------------------
# GET /metrics — Prometheus Endpoint (G-OPS-03)
# ---------------------------------------------------------------------------
@app.get("/metrics")
async def metrics():
    """
    Exposes Prometheus metrics for scraping.

    Required by G-OPS-03 (Performance Monitoring & Drift Detection):
    - scribe_requests_total: Request volume
    - scribe_latency_seconds: Latency distribution (p95 SLO: 2000ms)
    - scribe_mock_mode: Operating mode indicator

    The monitoring sidecar (Phase 9) will add drift metrics:
    - drift_psi_score: Population Stability Index
    - drift_js_divergence: Jensen-Shannon Divergence
    """
    return PlainTextResponse(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )
