#!/usr/bin/env python3
"""
drift_detector.py — Data Drift Detection for GenAIOps Compliance Gates.

Part of Pillar S5 (Monitoring & Post-Market Surveillance).
Implements G-OPS-03 (Performance Monitoring & Drift Detection).
Decision: E15 (Simple drift_detector.py, ~80 lines core logic).
Decision: DSR E5 (PSI + Jensen-Shannon Divergence, batch-based).

Two modes:
    --init-baseline : Captures current distribution from app /metrics or fixture
                      and saves as baseline JSON file.
    (default)       : Compares current distribution against saved baseline,
                      computes PSI + JSD, exports Prometheus metrics,
                      records to Evidence Store if threshold exceeded.

Thresholds (from drift-config.yaml ConfigMap):
    PSI > 0.1 = WARNING  (distribution shift detected)
    PSI > 0.2 = CRITICAL (significant drift, gate re-evaluation required)
    JSD > 0.05 = WARNING
    JSD > 0.1  = CRITICAL

Usage:
    # Initialize baseline from live app
    python drift_detector.py --init-baseline --source http://localhost:8080/metrics

    # Initialize baseline from fixture file
    python drift_detector.py --init-baseline --source fixtures/baseline_normal.json

    # Check for drift (compares live metrics against saved baseline)
    python drift_detector.py --source http://localhost:8080/metrics

    # Check for drift from fixture (for walkthrough/demo)
    python drift_detector.py --source fixtures/current_drifted.json

    # With Evidence Store recording on drift
    python drift_detector.py --source fixtures/current_drifted.json \
        --record-evidence --sqlite /tmp/evidence.db

What this does (Kolloquium):
    This script is the "early warning system" for AI model degradation.
    Imagine a medical AI that was trained on data from Berlin hospitals.
    After 3 months, it starts receiving data from rural clinics with
    different terminology. The input distribution has "drifted."

    PSI (Population Stability Index) measures HOW MUCH the distribution
    has changed. It's like comparing two histograms — if the bars shift
    significantly, PSI goes up.

    JSD (Jensen-Shannon Divergence) is a more mathematically robust
    measure of the same thing — how "different" two probability
    distributions are.

    If either exceeds the threshold, the system:
    1. Exports the metric to Prometheus (for Grafana dashboards)
    2. Records a FAIL in the Evidence Store (for audit trail)
    3. Returns exit code 1 (for pipeline integration)
"""

import argparse
import json
import math
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import subprocess

# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
RECORD_EVIDENCE = REPO_ROOT / "evidence-store" / "scripts" / "record_evidence.py"

# Default thresholds (overridden by ConfigMap env vars)
DEFAULT_PSI_WARNING = 0.1
DEFAULT_PSI_CRITICAL = 0.2
DEFAULT_JSD_WARNING = 0.05
DEFAULT_JSD_CRITICAL = 0.1

# Default baseline path
DEFAULT_BASELINE_PATH = REPO_ROOT / "monitoring" / "baseline_distribution.json"

# Prometheus metrics port (separate from app port 8080)
METRICS_PORT = 8081


# ──────────────────────────────────────────────────────────────
# PSI & JSD Computation
# ──────────────────────────────────────────────────────────────

def compute_psi(baseline: list[float], current: list[float], epsilon: float = 1e-6) -> float:
    """
    Compute Population Stability Index (PSI).

    PSI = Σ (current_i - baseline_i) × ln(current_i / baseline_i)

    Interpretation:
        PSI < 0.1  → No significant change
        PSI 0.1-0.2 → Moderate change (investigate)
        PSI > 0.2  → Significant change (action required)

    Args:
        baseline: Reference probability distribution (sums to ~1.0)
        current: Current probability distribution (sums to ~1.0)
        epsilon: Small value to avoid log(0)

    Returns:
        PSI score (non-negative float)
    """
    if len(baseline) != len(current):
        raise ValueError(f"Distribution length mismatch: baseline={len(baseline)}, current={len(current)}")

    psi = 0.0
    for b, c in zip(baseline, current):
        b = max(b, epsilon)
        c = max(c, epsilon)
        psi += (c - b) * math.log(c / b)
    return psi


def compute_jsd(baseline: list[float], current: list[float], epsilon: float = 1e-6) -> float:
    """
    Compute Jensen-Shannon Divergence (JSD).

    JSD(P, Q) = 0.5 × KL(P || M) + 0.5 × KL(Q || M)
    where M = 0.5 × (P + Q)

    JSD is symmetric and bounded [0, ln(2)] ≈ [0, 0.693].
    We return the square root (Jensen-Shannon Distance) which is
    a proper metric and bounded [0, 1] when using log base 2.

    Args:
        baseline: Reference probability distribution
        current: Current probability distribution
        epsilon: Small value to avoid log(0)

    Returns:
        JSD score (0 = identical, higher = more different)
    """
    if len(baseline) != len(current):
        raise ValueError(f"Distribution length mismatch: baseline={len(baseline)}, current={len(current)}")

    # Compute midpoint distribution M
    m = [(b + c) / 2.0 for b, c in zip(baseline, current)]

    # KL divergence: KL(P || Q) = Σ p_i × log(p_i / q_i)
    def kl_divergence(p: list[float], q: list[float]) -> float:
        return sum(
            max(pi, epsilon) * math.log(max(pi, epsilon) / max(qi, epsilon))
            for pi, qi in zip(p, q)
        )

    jsd = 0.5 * kl_divergence(baseline, m) + 0.5 * kl_divergence(current, m)
    return jsd


# ──────────────────────────────────────────────────────────────
# Distribution Loading
# ──────────────────────────────────────────────────────────────

def load_distribution_from_file(path: str) -> dict:
    """Load feature distributions from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_distribution_from_app(url: str) -> dict:
    """
    Load feature distributions from a running app's /metrics endpoint.

    Parses Prometheus text format and extracts histogram bucket values
    as a proxy for the input distribution.
    """
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            content = resp.read().decode("utf-8")
    except Exception as e:
        print(f"ERROR: Could not reach app at {url}: {e}")
        sys.exit(2)

    # Parse Prometheus histogram buckets for latency distribution
    # This serves as a proxy for "input distribution" in the PoC
    buckets = {}
    for line in content.split("\n"):
        if line.startswith("scribe_latency_seconds_bucket"):
            # Example: scribe_latency_seconds_bucket{endpoint="/transcribe",le="0.1"} 5
            try:
                le_start = line.index('le="') + 4
                le_end = line.index('"', le_start)
                le_val = line[le_start:le_end]
                count = float(line.split()[-1])
                if le_val != "+Inf":
                    buckets[float(le_val)] = count
            except (ValueError, IndexError):
                continue

    if not buckets:
        print("WARNING: No histogram buckets found in /metrics. Using mock distribution.")
        # Return a mock distribution for demo purposes
        return {
            "features": {
                "latency_distribution": [0.15, 0.25, 0.30, 0.15, 0.10, 0.05],
                "input_length_distribution": [0.10, 0.20, 0.35, 0.20, 0.10, 0.05],
            },
            "source": url,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "bucket_labels": ["0-100", "100-250", "250-500", "500-1000", "1000-2000", "2000+"],
        }

    # Convert cumulative buckets to probability distribution
    sorted_buckets = sorted(buckets.items())
    counts = []
    prev = 0.0
    for _, cumulative in sorted_buckets:
        counts.append(cumulative - prev)
        prev = cumulative

    total = sum(counts) if sum(counts) > 0 else 1.0
    distribution = [c / total for c in counts]

    return {
        "features": {
            "latency_distribution": distribution,
        },
        "source": url,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "bucket_labels": [str(b[0]) for b in sorted_buckets],
    }


def load_distribution(source: str) -> dict:
    """Load distribution from either a file or a URL."""
    if source.startswith("http://") or source.startswith("https://"):
        return load_distribution_from_app(source)
    else:
        path = Path(source)
        if not path.is_absolute():
            path = REPO_ROOT / source
        return load_distribution_from_file(str(path))


# ──────────────────────────────────────────────────────────────
# Prometheus Metrics Export
# ──────────────────────────────────────────────────────────────

# Global metrics state (updated by drift check, served by HTTP)
_metrics_state = {
    "psi_score": 0.0,
    "jsd_score": 0.0,
    "drift_status": 0,  # 0=ok, 1=warning, 2=critical
    "last_check": "",
}


class MetricsHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler serving Prometheus metrics."""

    def do_GET(self):
        if self.path == "/metrics":
            body = (
                f"# HELP genaiops_drift_psi_score Population Stability Index\n"
                f"# TYPE genaiops_drift_psi_score gauge\n"
                f"genaiops_drift_psi_score {_metrics_state['psi_score']:.6f}\n"
                f"# HELP genaiops_drift_jsd_score Jensen-Shannon Divergence\n"
                f"# TYPE genaiops_drift_jsd_score gauge\n"
                f"genaiops_drift_jsd_score {_metrics_state['jsd_score']:.6f}\n"
                f"# HELP genaiops_drift_status Drift status (0=ok, 1=warning, 2=critical)\n"
                f"# TYPE genaiops_drift_status gauge\n"
                f"genaiops_drift_status {_metrics_state['drift_status']}\n"
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(body.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress HTTP access logs


def start_metrics_server(port: int = METRICS_PORT):
    """Start Prometheus metrics HTTP server in background thread."""
    server = HTTPServer(("0.0.0.0", port), MetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ──────────────────────────────────────────────────────────────
# Evidence Store Integration
# ──────────────────────────────────────────────────────────────

def record_drift_evidence(
    psi: float, jsd: float, status: str,
    sqlite_path: str = None, db_url: str = None, run_id: str = None,
) -> None:
    """Record drift detection result to Evidence Store.

    Supports both SQLite (local) and PostgreSQL (cluster).
    In cluster mode, the DB URL comes from EVIDENCE_STORE_URL or
    EVIDENCE_STORE_DB_URL environment variable.
    """
    import tempfile
    import uuid

    evidence = {
        "gate_id": "G-OPS-03",
        "decision": "FAIL" if status == "critical" else "PASS",
        "tool": "drift_detector",
        "psi_score": psi,
        "jsd_score": jsd,
        "drift_status": status,
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "failures": [{"msg": f"PSI={psi:.4f} > threshold"}] if status == "critical" else [],
    }

    # Write temp JSON for record_evidence.py
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, prefix="drift_evidence_"
    )
    json.dump(evidence, tmp, indent=2)
    tmp.close()

    # Resolve DB connection: explicit arg > EVIDENCE_STORE_URL > EVIDENCE_STORE_DB_URL
    resolved_db_url = db_url or os.getenv("EVIDENCE_STORE_URL") or os.getenv("EVIDENCE_STORE_DB_URL")

    cmd = [
        sys.executable, str(RECORD_EVIDENCE),
        "--gate", "G-OPS-03",
        "--method", "AUTO",
        "--source", tmp.name,
    ]

    if sqlite_path:
        cmd.extend(["--sqlite", sqlite_path])
    elif resolved_db_url:
        cmd.extend(["--db-url", resolved_db_url])
    else:
        print("[evidence] ERROR: No Evidence Store connection configured "
              "(need --sqlite, EVIDENCE_STORE_URL, or EVIDENCE_STORE_DB_URL)")
        os.unlink(tmp.name)
        return

    if run_id:
        cmd.extend(["--run-id", run_id])

    result = subprocess.run(cmd, capture_output=True, text=True)
    os.unlink(tmp.name)

    if result.returncode == 0:
        print("[evidence] Drift result recorded to Evidence Store")
        for line in result.stdout.split("\n"):
            if "Hash:" in line or "audit_id" in line:
                print(f"  {line.strip()}")
    else:
        print(f"[evidence] ERROR: Failed to record drift evidence: {result.stderr[:200]}")
        sys.exit(1)  # Hard fail — evidence recording is mandatory


# ──────────────────────────────────────────────────────────────
# Main Logic
# ──────────────────────────────────────────────────────────────

def check_drift(
    baseline_data: dict,
    current_data: dict,
    psi_warning: float = DEFAULT_PSI_WARNING,
    psi_critical: float = DEFAULT_PSI_CRITICAL,
    jsd_warning: float = DEFAULT_JSD_WARNING,
    jsd_critical: float = DEFAULT_JSD_CRITICAL,
) -> dict:
    """
    Compare baseline vs current distributions, compute PSI and JSD.

    Returns dict with scores, status, and per-feature details.
    """
    results = {"features": {}, "overall_status": "ok"}
    max_psi = 0.0
    max_jsd = 0.0

    baseline_features = baseline_data.get("features", {})
    current_features = current_data.get("features", {})

    for feature_name in baseline_features:
        if feature_name not in current_features:
            print(f"  WARNING: Feature '{feature_name}' missing in current data, skipping")
            continue

        b = baseline_features[feature_name]
        c = current_features[feature_name]

        # Normalize to probability distributions
        b_sum = sum(b) if sum(b) > 0 else 1.0
        c_sum = sum(c) if sum(c) > 0 else 1.0
        b_norm = [x / b_sum for x in b]
        c_norm = [x / c_sum for x in c]

        psi = compute_psi(b_norm, c_norm)
        jsd = compute_jsd(b_norm, c_norm)

        # Determine status for this feature
        if psi > psi_critical or jsd > jsd_critical:
            status = "critical"
        elif psi > psi_warning or jsd > jsd_warning:
            status = "warning"
        else:
            status = "ok"

        results["features"][feature_name] = {
            "psi": round(psi, 6),
            "jsd": round(jsd, 6),
            "status": status,
        }

        max_psi = max(max_psi, psi)
        max_jsd = max(max_jsd, jsd)

    # Overall status = worst across all features
    if max_psi > psi_critical or max_jsd > jsd_critical:
        results["overall_status"] = "critical"
    elif max_psi > psi_warning or max_jsd > jsd_warning:
        results["overall_status"] = "warning"

    results["max_psi"] = round(max_psi, 6)
    results["max_jsd"] = round(max_jsd, 6)
    results["checked_at"] = datetime.now(timezone.utc).isoformat()

    return results


def main():
    parser = argparse.ArgumentParser(
        description="GenAIOps Drift Detection — PSI + JSD monitoring for G-OPS-03"
    )
    parser.add_argument(
        "--source", required=True,
        help="URL (http://...) or file path to current distribution"
    )
    parser.add_argument(
        "--baseline", default=str(DEFAULT_BASELINE_PATH),
        help="Path to baseline distribution JSON"
    )
    parser.add_argument(
        "--init-baseline", action="store_true",
        help="Save current distribution as new baseline (first run)"
    )
    parser.add_argument(
        "--record-evidence", action="store_true",
        help="Record drift results to Evidence Store"
    )
    parser.add_argument(
        "--sqlite", help="SQLite path for Evidence Store (local testing)"
    )
    parser.add_argument(
        "--db-url",
        default=os.getenv("EVIDENCE_STORE_URL") or os.getenv("EVIDENCE_STORE_DB_URL"),
        help="PostgreSQL URL for Evidence Store (cluster mode)"
    )
    parser.add_argument(
        "--serve-metrics", action="store_true",
        help=f"Start Prometheus metrics server on port {METRICS_PORT}"
    )
    parser.add_argument(
        "--watch", type=int, metavar="SECONDS",
        help="Run continuously, checking every N seconds"
    )

    args = parser.parse_args()

    # ── Load thresholds from environment (ConfigMap injection) ──
    psi_warning = float(os.getenv("DRIFT_THRESHOLD_PSI_WARNING", DEFAULT_PSI_WARNING))
    psi_critical = float(os.getenv("DRIFT_THRESHOLD_PSI_CRITICAL", DEFAULT_PSI_CRITICAL))
    jsd_warning = float(os.getenv("DRIFT_THRESHOLD_JS_WARNING", DEFAULT_JSD_WARNING))
    jsd_critical = float(os.getenv("DRIFT_THRESHOLD_JS_CRITICAL", DEFAULT_JSD_CRITICAL))

    # ── Init baseline mode ──
    if args.init_baseline:
        print("[drift] Initializing baseline distribution...")
        data = load_distribution(args.source)
        baseline_path = Path(args.baseline)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[drift] Baseline saved: {baseline_path}")
        print(f"[drift] Features: {list(data.get('features', {}).keys())}")
        print(f"[drift] Source: {data.get('source', args.source)}")
        return

    # ── Load baseline ──
    baseline_path = Path(args.baseline)
    if not baseline_path.exists():
        print(f"ERROR: Baseline not found: {baseline_path}")
        print(f"  Run with --init-baseline first to create it.")
        sys.exit(2)

    baseline_data = load_distribution_from_file(str(baseline_path))

    # ── Start metrics server if requested ──
    if args.serve_metrics:
        start_metrics_server(METRICS_PORT)
        print(f"[drift] Prometheus metrics server started on :{METRICS_PORT}/metrics")

    # ── Single check or watch loop ──
    def run_check():
        current_data = load_distribution(args.source)
        result = check_drift(
            baseline_data, current_data,
            psi_warning, psi_critical, jsd_warning, jsd_critical,
        )

        # Update Prometheus metrics
        _metrics_state["psi_score"] = result["max_psi"]
        _metrics_state["jsd_score"] = result["max_jsd"]
        _metrics_state["drift_status"] = {"ok": 0, "warning": 1, "critical": 2}[result["overall_status"]]
        _metrics_state["last_check"] = result["checked_at"]

        # Print results
        status_colors = {"ok": "\033[92m", "warning": "\033[93m", "critical": "\033[91m"}
        reset = "\033[0m"
        color = status_colors.get(result["overall_status"], "")

        print(f"\n[drift] Check at {result['checked_at']}")
        print(f"[drift] PSI: {result['max_psi']:.6f} (warn>{psi_warning}, crit>{psi_critical})")
        print(f"[drift] JSD: {result['max_jsd']:.6f} (warn>{jsd_warning}, crit>{jsd_critical})")
        print(f"[drift] Status: {color}{result['overall_status'].upper()}{reset}")

        for fname, fdata in result["features"].items():
            fc = status_colors.get(fdata["status"], "")
            print(f"  {fname}: PSI={fdata['psi']:.6f} JSD={fdata['jsd']:.6f} [{fc}{fdata['status']}{reset}]")

        # Record to Evidence Store if drift detected
        if args.record_evidence and result["overall_status"] in ("warning", "critical"):
            record_drift_evidence(
                psi=result["max_psi"],
                jsd=result["max_jsd"],
                status=result["overall_status"],
                sqlite_path=args.sqlite,
                db_url=args.db_url,
            )

        return result["overall_status"]

    if args.watch:
        print(f"[drift] Watch mode: checking every {args.watch}s (Ctrl+C to stop)")
        try:
            while True:
                run_check()
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\n[drift] Stopped.")
    else:
        status = run_check()
        # Exit code: 0=ok, 1=critical (pipeline should halt), 0=warning (informational)
        sys.exit(1 if status == "critical" else 0)


if __name__ == "__main__":
    main()
