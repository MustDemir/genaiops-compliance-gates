#!/usr/bin/env python3
"""
eval_runner.py — produce eval_results.json instead of finding it.

SPEC-04 Teil 2. Until 2026-08, G-DEP-02 evaluated a hand-maintained
fixture: `"model_version": "mock-v1.0.0"`, no code anywhere produced it,
CI and the local pipeline only ever read it. Meanwhile the application
exported `scribe_latency_seconds` and nothing consumed that. Two
separate worlds (HANDBUCH 7.5 (1)):

    app measures  -> scribe_latency_seconds -> Prometheus -> (ends there)
    gate checks   <- eval_results.json (hand file, invented values)

The file was not even consistent with itself: `quality_metrics.accuracy`
said 0.89 while `gate_result.details` said 0.91 for the same metric, and
no rule compared the two (HANDBUCH 7.5 (1a)). Where a number is not
produced, it cannot even be consistent with itself.

What this script changes, and what it deliberately does not:

    latency, throughput   now MEASURED from the running app
    model_version         now READ from the app, not copied from a manifest
    runtime_mode          now MEASURED from scribe_mock_mode
    accuracy, safety      still DECLARED — and now labelled as such
    gate_result           gone; the gate decides, not the document

The policy `policy_safety_metrics.rego` is unchanged. The thresholds
were never wrong. What was wrong was where the number came from — the
evidence level sits in the provenance of the input, not in the rule
(HANDBUCH 7.7).

Usage:
    # measure against a running app
    python eval_runner.py --app-url http://localhost:8080

    # scrape an endpoint without driving load (app already has traffic)
    python eval_runner.py --metrics-url http://localhost:8080/metrics --requests 0
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "monitoring"))

from metrics_source import (  # noqa: E402  (path set above)
    MetricsUnavailable,
    PROVENANCE_DECLARED,
    PROVENANCE_MEASURED,
    fetch_metrics_text,
    histogram_sum_count,
    parse_counter_total,
    parse_gauge,
    parse_histogram_buckets,
    provenance_block,
    quantile_from_buckets,
    quantile_resolution,
)

SCENARIO_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DECLARED = Path(__file__).resolve().parent / "declared_metrics.json"
DEFAULT_OUTPUT = SCENARIO_DIR / "fixtures" / "eval_results.json"

# Thresholds are configuration, not measurement. They stay an input.
GATE_THRESHOLDS = {
    "accuracy_min": 0.85,
    "latency_p95_max_ms": 2000,
    "safety_score_min": 0.90,
}

SAMPLE_TEXT = (
    "Patient berichtet ueber wiederkehrende Kopfschmerzen seit zwei Wochen. "
    "Keine neurologischen Auffaelligkeiten in der Untersuchung."
)


def drive_load(app_url: str, n: int) -> dict:
    """Send N requests to /transcribe so the histogram has observations.

    Returns whatever the app reports about itself. Reading model_version
    from a live response rather than copying it out of a manifest is the
    difference between "the app says which model it is" and "someone
    wrote down which model it should be".
    """
    endpoint = app_url.rstrip("/") + "/transcribe"
    payload = json.dumps({"text": SAMPLE_TEXT}).encode("utf-8")
    last = {}

    for i in range(n):
        req = urllib.request.Request(
            endpoint, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                last = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
            print(f"ERROR: request {i + 1}/{n} to {endpoint} failed: {e}")
            print("  No evaluation document was written. There is no fallback.")
            sys.exit(2)

    return last


def resolve_runtime_mode(metrics_text: str) -> str:
    """live | mock | unknown, read from scribe_mock_mode.

    An absent gauge is 'unknown', never 'live'. Whoever cannot tell
    whether a real model ran has no evidence that a real model ran
    (SPEC-04 Teil 1, HANDBUCH 7.8).
    """
    try:
        return "mock" if parse_gauge(metrics_text, "scribe_mock_mode") == 1.0 else "live"
    except MetricsUnavailable:
        return "unknown"


def build_evaluation(
    metrics_text: str,
    metrics_url: str,
    declared: dict,
    app_response: dict,
    request_count: int,
    elapsed_seconds: float,
) -> dict:
    buckets = parse_histogram_buckets(metrics_text, "scribe_latency_seconds")

    def ms(q: float) -> float:
        return round(quantile_from_buckets(buckets, q) * 1000, 3)

    latency_sum, latency_count = histogram_sum_count(metrics_text, "scribe_latency_seconds")
    p95_resolution = quantile_resolution(buckets, quantile_from_buckets(buckets, 0.95))

    total_requests = parse_counter_total(metrics_text, "scribe_requests_total")
    error_requests = parse_counter_total(
        metrics_text, "scribe_requests_total", {"status": "error"}
    )

    runtime_mode = resolve_runtime_mode(metrics_text)
    measured_from = f"{metrics_url} (scribe_latency_seconds, scribe_requests_total)"

    return {
        "_spec": "SPEC-04 Teil 2 — generated document. Do not hand-edit; "
                 "rerun eval_runner.py. Declared values live in eval/declared_metrics.json.",

        "evaluation": {
            **provenance_block(PROVENANCE_MEASURED, measured_from),
            "model_name": app_response.get("model_name", "ambient-ai-scribe"),
            # Read from the app's own response, not copied from a manifest.
            "model_version": app_response.get("model_version", "unknown"),
            "pipeline_id": app_response.get("pipeline_id", "local-dev"),
            "run_id": f"eval-{datetime.now(timezone.utc):%Y%m%d}-{uuid.uuid4().hex[:8]}",
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            # SPEC-04 Teil 1 lands here too: the document states whether a
            # real model was behind the numbers it reports.
            "runtime_mode": runtime_mode,
        },

        "performance_metrics": {
            **provenance_block(PROVENANCE_MEASURED, measured_from),
            "latency_p50_ms": ms(0.50),
            "latency_p95_ms": ms(0.95),
            "latency_p99_ms": ms(0.99),
            # Exact: derived from _sum/_count, no bucket boundary involved.
            # The only latency figure here that is not an estimate.
            "latency_mean_ms": round(latency_sum / latency_count * 1000, 4),
            "throughput_rps": round(request_count / elapsed_seconds, 2) if elapsed_seconds > 0 else 0.0,
            "requests_total": total_requests,
            "requests_error": error_requests,
            "error_rate": round(error_requests / total_requests, 6) if total_requests else 0.0,
            # How much the bucket layout can actually resolve at the p95.
            # `within_finest_bucket: true` means the p95 is pure interpolation
            # between zero and the finest bound: it moves with the layout, not
            # with the system, and a threshold applied to it is a threshold
            # applied to an artefact. Machine-readable on purpose — the same
            # move as `provenance`, one level deeper: the number stays, its
            # trustworthiness stops being invisible.
            "latency_p95_resolution": p95_resolution,
            "_estimation_note": (
                "Quantiles are interpolated from histogram buckets, the same "
                "approximation Prometheus' histogram_quantile() makes, and bounded "
                "by the bucket layout. latency_mean_ms is exact (_sum/_count). "
                "Check latency_p95_resolution.within_finest_bucket before treating "
                "the p95 as a statement about the system."
            ),
        },

        "quality_metrics": {
            **provenance_block(
                PROVENANCE_DECLARED,
                declared.get("_source", "offline evaluation set, manually maintained"),
                declared.get("_note"),
            ),
            **declared["quality_metrics"],
        },

        "safety_metrics": {
            **provenance_block(
                PROVENANCE_DECLARED,
                declared.get("_source", "offline evaluation set, manually maintained"),
                declared.get("_note"),
            ),
            **declared["safety_metrics"],
        },

        "subgroup_analysis": {
            **provenance_block(
                PROVENANCE_DECLARED,
                declared.get("_source", "offline evaluation set, manually maintained"),
                "Einmalige Pruefung vor Freigabe. Subgruppen-Performance ueber Zeit "
                "fehlt weiterhin — HANDBUCH 7.6 Luecke 3.",
            ),
            **declared["subgroup_analysis"],
        },

        "adversarial_tests": {
            **provenance_block(
                PROVENANCE_DECLARED,
                declared.get("_source", "offline evaluation set, manually maintained"),
                declared.get("_note"),
            ),
            **declared["adversarial_tests"],
        },

        # Configuration, not measurement — legitimately an input.
        "gate_thresholds": GATE_THRESHOLDS,

        # `gate_result` is deliberately absent. See SPEC-04 Teil 2.4: it was
        # a claim about the verdict, carried inside the document being
        # judged — a candidate bringing its own report card. Conftest
        # decides whether the thresholds hold; the document does not get
        # to have an opinion about it.
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Produce eval_results.json from a running app (SPEC-04 Teil 2)"
    )
    parser.add_argument("--app-url", default="http://localhost:8080",
                        help="Base URL of the scribe app")
    parser.add_argument("--metrics-url", default=None,
                        help="Metrics endpoint (default: <app-url>/metrics)")
    parser.add_argument("--requests", type=int, default=20,
                        help="Requests to drive before scraping (0 = scrape only)")
    parser.add_argument("--declared", default=str(DEFAULT_DECLARED),
                        help="File holding the metrics that cannot be measured")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT),
                        help="Where to write the evaluation document")
    args = parser.parse_args()

    metrics_url = args.metrics_url or args.app_url.rstrip("/") + "/metrics"

    with open(args.declared, "r", encoding="utf-8") as f:
        declared = json.load(f)

    app_response: dict = {}
    started = time.time()
    if args.requests > 0:
        print(f"[eval] Driving {args.requests} requests at {args.app_url}/transcribe ...")
        app_response = drive_load(args.app_url, args.requests)
    elapsed = time.time() - started

    print(f"[eval] Scraping {metrics_url} ...")
    try:
        metrics_text = fetch_metrics_text(metrics_url)
        document = build_evaluation(
            metrics_text, metrics_url, declared, app_response,
            args.requests, elapsed,
        )
    except MetricsUnavailable as e:
        print(f"ERROR: {e}")
        print(
            "  No evaluation document was written. This is deliberate: there is\n"
            "  no fallback. A gate fed an invented number is worse than a gate\n"
            "  that did not run, because it answers the question."
        )
        return 2

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(document, f, indent=2, ensure_ascii=False)
        f.write("\n")

    perf = document["performance_metrics"]
    mode = document["evaluation"]["runtime_mode"]
    print(f"[eval] Written: {out}")
    print(f"[eval]   mean = {perf['latency_mean_ms']} ms (exact, from _sum/_count)")
    print(f"[eval]   p95  = {perf['latency_p95_ms']} ms (interpolated)")
    if perf["latency_p95_resolution"]["within_finest_bucket"]:
        print(f"[eval]   WARNING: the p95 sits inside the finest bucket "
              f"({perf['latency_p95_resolution']['finest_bucket_ms']} ms) — it is "
              "interpolation, not a statement about the system.")
    print(f"[eval]   error rate = {perf['error_rate']} (measured)")
    print(f"[eval]   accuracy = {document['quality_metrics']['accuracy']} (DECLARED — not measured)")
    print(f"[eval]   runtime_mode = {mode}")
    if mode != "live":
        print(f"[eval]   WARNING: runtime_mode is '{mode}' — these numbers did not "
              "come from a real model run.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
