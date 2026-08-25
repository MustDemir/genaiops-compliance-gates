#!/usr/bin/env python3
"""
test_eval_runner.py — verify that the evaluation document is PRODUCED.

SPEC-04 Teil 2, test section. The point of these tests is not that the
numbers are pretty; it is that they are numbers the system went and got.

A stdlib stand-in serves the same metric contract as the real app
(scribe_latency_seconds histogram, scribe_requests_total counter,
scribe_mock_mode gauge). It exists because FastAPI cannot be installed
on this machine — pip is unusable here (see the repo notes on the
PyYAML workaround). The stand-in is NOT the app: it proves the runner
reads a Prometheus endpoint correctly, not that the scribe behaves
correctly. Those are different claims and only the first is tested here.

Run:
    python3 scenarios/healthcare-ambient-ai-scribe/eval/test_eval_runner.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
RUNNER = HERE / "eval_runner.py"

GREEN, RED, BOLD, RESET = "\033[92m", "\033[91m", "\033[1m", "\033[0m"
_results: list[tuple[bool, str]] = []


def check(ok: bool, label: str) -> None:
    _results.append((ok, label))
    print(f"  {GREEN}PASS{RESET} {label}" if ok else f"  {RED}FAIL{RESET} {label}")


# ──────────────────────────────────────────────────────────────
# Stand-in app: same metric contract, stdlib only
# ──────────────────────────────────────────────────────────────

# Must mirror app/main.py. The stand-in exists to exercise the reader, and a
# reader tested against a different bucket layout than the app emits would
# prove the wrong thing.
BUCKETS = [
    0.001, 0.0025, 0.005, 0.01, 0.025, 0.05,
    0.1, 0.25, 0.5, 1.0, 2.0, 5.0,
]


class _State:
    def __init__(self, latency_seconds: float, mock_mode: int = 1):
        self.latency = latency_seconds
        self.mock_mode = mock_mode
        self.observations: list[float] = []
        self.errors = 0


class _Handler(BaseHTTPRequestHandler):
    state: _State = None  # set per server

    def _send(self, body: bytes, ctype: str = "text/plain") -> None:
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)
        time.sleep(self.state.latency)
        self.state.observations.append(self.state.latency)
        self._send(
            json.dumps({
                "summary": "…",
                "model_version": "standin-v9.9.9",
                "pipeline_id": "test-harness",
                "run_id": "r-1",
                "mock_mode": bool(self.state.mock_mode),
            }).encode(),
            "application/json",
        )

    def do_GET(self):
        s = self.state
        lines = [
            "# TYPE scribe_latency_seconds histogram",
        ]
        for b in BUCKETS:
            count = sum(1 for o in s.observations if o <= b)
            lines.append(f'scribe_latency_seconds_bucket{{endpoint="/transcribe",le="{b}"}} {count}')
        lines.append(
            f'scribe_latency_seconds_bucket{{endpoint="/transcribe",le="+Inf"}} {len(s.observations)}'
        )
        # _sum/_count are what make the exact mean possible. prometheus_client
        # emits them automatically; the stand-in has to do it by hand.
        lines.append(f"scribe_latency_seconds_sum {sum(s.observations)}")
        lines.append(f"scribe_latency_seconds_count {len(s.observations)}")
        lines.append("# TYPE scribe_requests_total counter")
        lines.append(
            f'scribe_requests_total{{endpoint="/transcribe",status="success"}} {len(s.observations)}'
        )
        lines.append(f'scribe_requests_total{{endpoint="/transcribe",status="error"}} {s.errors}')
        if s.mock_mode is not None:
            lines.append("# TYPE scribe_mock_mode gauge")
            lines.append(f"scribe_mock_mode {float(s.mock_mode)}")
        self._send(("\n".join(lines) + "\n").encode())

    def log_message(self, *_args):
        pass


def start_standin(latency: float, mock_mode: int | None = 1):
    state = _State(latency, mock_mode)
    handler = type("H", (_Handler,), {"state": state})
    server = HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}", state


def run_runner(app_url: str, out: Path, requests: int = 8) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RUNNER),
         "--app-url", app_url, "--requests", str(requests), "--output", str(out)],
        capture_output=True, text=True, timeout=120,
    )


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="eval_runner_test_"))

    # ── The document is produced, and it reflects the app ──
    print(f"\n{BOLD}A: the document is produced, not found{RESET}")
    srv, url, _ = start_standin(latency=0.05)
    out_fast = tmp / "fast.json"
    proc = run_runner(url, out_fast)
    check(proc.returncode == 0, f"runner exit 0 (actual {proc.returncode})")
    check(out_fast.exists(), "evaluation document written")

    doc_fast = json.loads(out_fast.read_text())
    check(doc_fast["evaluation"]["model_version"] == "standin-v9.9.9",
          "model_version read from the app, not from a manifest")
    check(doc_fast["performance_metrics"]["provenance"] == "measured",
          "performance_metrics labelled 'measured'")
    check(doc_fast["quality_metrics"]["provenance"] == "declared",
          "quality_metrics labelled 'declared' — accuracy is still not measured")
    srv.shutdown()

    # ── The number MOVES. A constant would mean nothing was measured. ──
    print(f"\n{BOLD}B: two different loads must yield two different p95{RESET}")
    srv2, url2, _ = start_standin(latency=0.4)
    out_slow = tmp / "slow.json"
    run_runner(url2, out_slow)
    doc_slow = json.loads(out_slow.read_text())
    srv2.shutdown()

    p95_fast = doc_fast["performance_metrics"]["latency_p95_ms"]
    p95_slow = doc_slow["performance_metrics"]["latency_p95_ms"]
    # An identical value across two different runs is a FAILURE here, not a
    # success: it would mean a constant is being checked again.
    check(p95_fast != p95_slow,
          f"p95 differs between runs ({p95_fast} ms vs {p95_slow} ms)")
    check(p95_slow > p95_fast, "the slower app measures slower")

    # ── The contradiction class from HANDBUCH 7.5 (1a) ──
    print(f"\n{BOLD}C: no metric may appear twice with different values{RESET}")
    check("gate_result" not in doc_fast,
          "gate_result is gone — the document no longer carries its own verdict")

    def collect(node, name, found):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == name and isinstance(v, (int, float)):
                    found.append(v)
                collect(v, name, found)
        elif isinstance(node, list):
            for item in node:
                collect(item, name, found)
        return found

    contradictions = []
    for metric in ("accuracy", "latency_p95_ms", "safety_score"):
        values = set(collect(doc_fast, metric, []))
        if len(values) > 1:
            contradictions.append(f"{metric}={sorted(values)}")
    check(not contradictions,
          f"no self-contradicting metric (found: {contradictions or 'none'})")

    # ── The exact mean, and the honesty flag on the estimate ──
    print(f"\n{BOLD}B2: the mean is exact; the p95 admits when it is not{RESET}")
    perf_slow = doc_slow["performance_metrics"]
    # Stand-in sleeps a known 0.4s per request, so the true mean is ~0.4s.
    # The mean comes from _sum/_count and must land there regardless of buckets.
    check(380 <= perf_slow["latency_mean_ms"] <= 460,
          f"mean lands on the true latency ({perf_slow['latency_mean_ms']} ms for a 400 ms app)")
    check(perf_slow["latency_p95_resolution"]["within_finest_bucket"] is False,
          "a 400 ms latency is NOT flagged as unresolvable")

    perf_fast = doc_fast["performance_metrics"]
    check(perf_fast["latency_mean_ms"] < perf_slow["latency_mean_ms"],
          "the faster app has the smaller mean")

    # ── Mock detection ──
    print(f"\n{BOLD}D: runtime_mode is measured, and 'unknown' is not 'live'{RESET}")
    check(doc_fast["evaluation"]["runtime_mode"] == "mock",
          "scribe_mock_mode=1 is reported as 'mock'")

    srv3, url3, _ = start_standin(latency=0.05, mock_mode=0)
    out_live = tmp / "live.json"
    run_runner(url3, out_live)
    srv3.shutdown()
    check(json.loads(out_live.read_text())["evaluation"]["runtime_mode"] == "live",
          "scribe_mock_mode=0 is reported as 'live'")

    srv4, url4, _ = start_standin(latency=0.05, mock_mode=None)
    out_unknown = tmp / "unknown.json"
    run_runner(url4, out_unknown)
    srv4.shutdown()
    check(json.loads(out_unknown.read_text())["evaluation"]["runtime_mode"] == "unknown",
          "absent gauge is 'unknown', never 'live'")

    # ── No fallback ──
    print(f"\n{BOLD}E: an unreachable app writes nothing{RESET}")
    out_none = tmp / "never.json"
    proc = subprocess.run(
        [sys.executable, str(RUNNER), "--app-url", "http://127.0.0.1:59998",
         "--requests", "2", "--output", str(out_none)],
        capture_output=True, text=True, timeout=60,
    )
    check(proc.returncode != 0, f"runner exits non-zero (actual {proc.returncode})")
    check(not out_none.exists(), "no document written — there is no fallback")

    # ── The produced document must still satisfy the unchanged policy ──
    print(f"\n{BOLD}F: the unchanged G-DEP-02 policy accepts the produced document{RESET}")
    conftest = subprocess.run(
        ["conftest", "test", str(out_fast),
         "--policy", str(REPO_ROOT / "policies" / "deployment"),
         "--namespace", "genaiops.deployment.safety_metrics",
         "--output", "json", "--no-color"],
        capture_output=True, text=True, timeout=60,
    )
    try:
        results = json.loads(conftest.stdout or "[]")
        failures = [f for r in results for f in r.get("failures", [])]
        warnings = [w for r in results for w in r.get("warnings", [])]
    except json.JSONDecodeError:
        failures, warnings = [{"msg": "could not parse conftest output"}], []
    check(not failures, f"no blocking failures (got: {[f.get('msg') for f in failures]})")
    check(any("C-03" in w.get("msg", "") for w in warnings),
          "C-03 warns that a MUST check rests on declared values")

    passed = sum(1 for ok, _ in _results if ok)
    failed = len(_results) - passed
    print(f"\n{BOLD}{'=' * 60}{RESET}")
    print(f"  {GREEN}PASSED: {passed}{RESET}  /  {RED}FAILED: {failed}{RESET}  /  Total: {len(_results)}")
    print(f"{BOLD}{'=' * 60}{RESET}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
