#!/usr/bin/env python3
"""
metrics_source.py — Shared Prometheus text-format reader.

SPEC-04 Teil 2/3. Single home for "read a number out of a running app",
so that drift_detector.py and eval_runner.py cannot drift apart on the
one thing they must agree about: how a bucket becomes a number.

Before SPEC-04 the bucket-parsing loop existed once, inside
drift_detector.load_distribution_from_app(). The eval runner would have
needed the same loop. Two copies of a parser that both feed compliance
gates is one copy too many — if they disagree, two gates disagree about
the same measurement and nothing in the system notices.

Design rule for this module (SPEC-04 Teil 3.1):

    No fallbacks. No mock values. No "for demo purposes".

If a measurement cannot be taken, these functions raise. They never
return a plausible-looking substitute. A fiction that carries a fresh
timestamp is worse than a missing value, because it answers the
question instead of raising it.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from datetime import datetime, timezone


class MetricsUnavailable(RuntimeError):
    """The metrics endpoint could not be reached or did not parse.

    Deliberately a hard error. See the module docstring: the caller must
    decide what to do with a missing measurement, and the only honest
    options are "fail" or "say explicitly that no measurement was taken".
    Silently substituting a distribution is not among them.
    """


def fetch_metrics_text(url: str, timeout: int = 10) -> str:
    """Fetch the Prometheus text exposition from `url`.

    Raises MetricsUnavailable rather than exiting, so callers stay testable.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, OSError, ValueError) as e:
        raise MetricsUnavailable(f"Could not reach metrics endpoint {url}: {e}") from e


# ──────────────────────────────────────────────────────────────
# Parsing
# ──────────────────────────────────────────────────────────────

def _labels_match(line: str, labels: dict[str, str] | None) -> bool:
    """True if every requested label=value appears in the sample line."""
    if not labels:
        return True
    return all(f'{k}="{v}"' in line for k, v in labels.items())


def parse_histogram_buckets(
    text: str, metric: str, labels: dict[str, str] | None = None
) -> dict[float, float]:
    """Parse `<metric>_bucket{le="..."}` samples into {upper_bound: cumulative_count}.

    The `+Inf` bucket is dropped: it carries no upper bound, so it cannot
    take part in a bounded distribution. Its count is recoverable from
    `<metric>_count` if ever needed.

    Raises MetricsUnavailable if no buckets are present — an empty
    histogram is not an empty distribution, it is an absent measurement.
    """
    prefix = f"{metric}_bucket"
    buckets: dict[float, float] = {}

    for line in text.split("\n"):
        if not line.startswith(prefix):
            continue
        if not _labels_match(line, labels):
            continue
        try:
            le_start = line.index('le="') + 4
            le_end = line.index('"', le_start)
            le_val = line[le_start:le_end]
            if le_val == "+Inf":
                continue
            # Buckets for the same `le` across other label dimensions
            # (e.g. several endpoints) are summed, matching Prometheus
            # aggregation semantics without a label selector.
            buckets[float(le_val)] = buckets.get(float(le_val), 0.0) + float(line.split()[-1])
        except (ValueError, IndexError):
            continue

    if not buckets:
        raise MetricsUnavailable(
            f"No histogram buckets for '{metric}' in the metrics output. "
            "The app exposes no observations for this metric — there is "
            "nothing to measure. Refusing to substitute a distribution."
        )
    return buckets


def buckets_to_distribution(buckets: dict[float, float]) -> tuple[list[float], list[str]]:
    """Convert cumulative histogram buckets to a probability distribution.

    Returns (distribution, bucket_labels). Prometheus buckets are
    cumulative, so each bin is the difference to its predecessor.
    """
    sorted_buckets = sorted(buckets.items())
    counts: list[float] = []
    prev = 0.0
    for _, cumulative in sorted_buckets:
        # max(0.0, ...) guards against a counter reset between scrapes,
        # which would otherwise produce a negative "probability".
        counts.append(max(0.0, cumulative - prev))
        prev = cumulative

    total = sum(counts)
    if total <= 0:
        raise MetricsUnavailable(
            "Histogram buckets are all zero — the app was scraped but has "
            "served no requests. No distribution can be derived from this."
        )

    return [c / total for c in counts], [str(b) for b, _ in sorted_buckets]


def quantile_from_buckets(buckets: dict[float, float], quantile: float) -> float:
    """Estimate a quantile from cumulative histogram buckets.

    Linear interpolation inside the containing bucket — the same
    approximation Prometheus' `histogram_quantile()` makes, and subject
    to the same limitation: resolution is bounded by the bucket layout,
    so the result is an estimate, not the true quantile.

    Returns the value in the histogram's own unit (seconds for
    `scribe_latency_seconds`).
    """
    if not 0.0 < quantile < 1.0:
        raise ValueError(f"quantile must be in (0,1), got {quantile}")

    sorted_buckets = sorted(buckets.items())
    total = sorted_buckets[-1][1]
    if total <= 0:
        raise MetricsUnavailable(
            "Histogram is empty — no observations recorded, no quantile to estimate."
        )

    target = quantile * total
    prev_bound, prev_count = 0.0, 0.0
    for bound, cumulative in sorted_buckets:
        if cumulative >= target:
            span = cumulative - prev_count
            if span <= 0:
                return bound
            frac = (target - prev_count) / span
            return prev_bound + frac * (bound - prev_bound)
        prev_bound, prev_count = bound, cumulative

    # Target beyond the last bounded bucket: everything above sits in
    # +Inf, which has no upper bound. The last bound is the most that
    # can be honestly asserted.
    return sorted_buckets[-1][0]


def histogram_sum_count(
    text: str, metric: str, labels: dict[str, str] | None = None
) -> tuple[float, float]:
    """Read `<metric>_sum` and `<metric>_count`.

    Unlike the quantiles, the mean derived from these two is EXACT: no bucket
    boundary is involved, so no interpolation happens. Prometheus histograms
    always expose both alongside the buckets.

    This matters because the bucket layout bounds quantile resolution but not
    this. Where every observation falls into the finest bucket, `p95` degrades
    into "0.95 x the finest bound" and says almost nothing, while the mean is
    still the true mean.
    """
    total = parse_counter_total(text, f"{metric}_sum", labels)
    count = parse_counter_total(text, f"{metric}_count", labels)
    if count <= 0:
        raise MetricsUnavailable(
            f"Histogram '{metric}' has a count of 0 — no observations, no mean."
        )
    return total, count


def quantile_resolution(buckets: dict[float, float], value_seconds: float) -> dict:
    """Describe how much the bucket layout can actually resolve at `value`.

    Returns the enclosing bucket and whether the value sits inside the FINEST
    one. That last flag is the honest part: inside the finest bucket a
    quantile is pure interpolation between 0 and that bound, so it moves with
    the layout rather than with the system. A threshold applied there is a
    threshold applied to an artefact.

    Making the weakness machine-readable rather than a footnote follows the
    same line as `provenance`: the number stays, its trustworthiness stops
    being invisible (HISTORIE 7.8).
    """
    bounds = sorted(buckets)
    finest = bounds[0]
    enclosing_lower = 0.0
    enclosing_upper = bounds[-1]
    for b in bounds:
        if value_seconds <= b:
            enclosing_upper = b
            break
        enclosing_lower = b

    return {
        "enclosing_bucket_ms": [round(enclosing_lower * 1000, 3), round(enclosing_upper * 1000, 3)],
        "finest_bucket_ms": round(finest * 1000, 3),
        "within_finest_bucket": value_seconds <= finest,
    }


def parse_gauge(text: str, metric: str, labels: dict[str, str] | None = None) -> float:
    """Read a single gauge sample.

    Raises MetricsUnavailable if the metric is absent. Callers must not
    treat "absent" as "zero" — for `scribe_mock_mode` in particular, an
    absent gauge means "unknown", and unknown is not "live" (SPEC-04 3.2).
    """
    for line in text.split("\n"):
        if line.startswith("#") or not line.startswith(metric):
            continue
        # Guard against prefix collisions (scribe_mock_mode vs scribe_mock_mode_extra)
        rest = line[len(metric):]
        if rest[:1] not in ("", " ", "{"):
            continue
        if not _labels_match(line, labels):
            continue
        try:
            return float(line.split()[-1])
        except (ValueError, IndexError):
            continue

    raise MetricsUnavailable(f"Gauge '{metric}' not present in the metrics output.")


def parse_counter_total(
    text: str, metric: str, labels: dict[str, str] | None = None
) -> float:
    """Sum all samples of a counter, optionally filtered by labels.

    Unlike the gauge reader, an absent counter returns 0.0: a counter
    that was never incremented is genuinely zero, which is a measurement,
    not a gap.
    """
    total = 0.0
    for line in text.split("\n"):
        if line.startswith("#") or not line.startswith(metric):
            continue
        rest = line[len(metric):]
        if rest[:1] not in ("", " ", "{"):
            continue
        if not _labels_match(line, labels):
            continue
        try:
            total += float(line.split()[-1])
        except (ValueError, IndexError):
            continue
    return total


# ──────────────────────────────────────────────────────────────
# Provenance (SPEC-04 Teil 2.3 / HISTORIE 7.8)
# ──────────────────────────────────────────────────────────────

PROVENANCE_MEASURED = "measured"
PROVENANCE_DERIVED = "derived"
PROVENANCE_DECLARED = "declared"

VALID_PROVENANCE = (PROVENANCE_MEASURED, PROVENANCE_DERIVED, PROVENANCE_DECLARED)


def provenance_block(kind: str, source: str, note: str | None = None) -> dict:
    """Build the provenance header carried by every metric group.

    E6 applied at field level: after this, every single number in an
    evaluation document says whether it was measured, computed, or
    merely asserted. It does not make a declared number true — it makes
    it legible as an assertion (HISTORIE 7.8).
    """
    if kind not in VALID_PROVENANCE:
        raise ValueError(f"provenance must be one of {VALID_PROVENANCE}, got '{kind}'")

    block = {"provenance": kind, "source": source}
    if kind in (PROVENANCE_MEASURED, PROVENANCE_DERIVED):
        block["measured_at"] = datetime.now(timezone.utc).isoformat()
    if note:
        block["note"] = note
    return block
