#!/usr/bin/env bash
# run_gate.sh — evaluate ONE gate over all of its input documents.
#
# Extracted from .github/workflows/gate-pipeline.yml on 02.09.2026 (SPEC-05
# Teil 5). It lived as a heredoc inside one job, which was fine while every
# gate ran in that job. G-OPS-05 now runs in the signing job — the signature
# it judges cannot exist before the gates have finished — and a second copy
# of this script would be two runners that drift apart. One file, two callers.
#
# Ein Gate, mehrere Eingabedokumente, EIN Ergebnis.
#
# Argumente 1-4 sind die Primaerauswertung (Manifest, Dokumentation,
# Fixture). Zusaetzlich liest das Skript die Pflichtinputs, die
# ci_required_inputs.py aus der Gate-Definition aufgeloest hat:
#
#   /tmp/<gate>-inputs.args   pfad TAB policy TAB namespace, je Zeile
#   /tmp/<gate>-inputs.fail   Meldungen, wenn ein Pflichtinput fehlt
#
# Beide Auswertungen fliessen in EINEN Evidence-Record — dieselbe Form
# wie role_scope BOTH in SPEC-03, das ebenfalls einmal wertet und
# einmal aufzeichnet. Sie getrennt aufzuzeichnen hiesse, ein Gate mit
# zwei Urteilen zu fuehren; genau das wurde bei G-OPS-03 in SPEC-04
# aufgeloest und wird hier nicht wieder eingefuehrt.
GATE_ID="$1"; FIXTURE="$2"; POLICY="$3"; NAMESPACE="$4"
LOWER="${GATE_ID,,}"
RESULT_FILE="/tmp/${LOWER}-result.json"
STDERR_FILE="/tmp/${LOWER}-result.stderr"
PARTS_LIST="/tmp/${LOWER}-parts.tsv"

: > "$STDERR_FILE"
rm -f /tmp/${LOWER}-part-*.json

printf '%s\t%s\t%s\n' "$FIXTURE" "$POLICY" "$NAMESPACE" > "$PARTS_LIST"
if [ -f "/tmp/${LOWER}-inputs.args" ]; then
  cat "/tmp/${LOWER}-inputs.args" >> "$PARTS_LIST"
fi

PART=0
while IFS=$'\t' read -r F P N; do
  [ -z "$F" ] && continue
  PART=$((PART + 1))
  conftest test "$F" \
    --policy "$P" \
    --namespace "$N" \
    --no-color --output json \
    > "/tmp/${LOWER}-part-${PART}.json" 2>> "$STDERR_FILE"
done < "$PARTS_LIST"

# Zusammenfuehren. Ein Pflichtinput, der FEHLT, wird als Verstoss in
# dasselbe Ergebnis geschrieben — nicht als Abbruch. Ein Gate, das
# seine Messung nicht vorgelegt bekommen hat, ist FAIL mit benanntem
# Grund, und dieser Grund gehoert in die Evidenz.
FAILURES=$(GATE_ID="$GATE_ID" LOWER="$LOWER" RESULT_FILE="$RESULT_FILE" python3 -c "
import glob, json, os, sys
gate, lower = os.environ['GATE_ID'], os.environ['LOWER']
merged, tool_error = [], False
for part in sorted(glob.glob(f'/tmp/{lower}-part-*.json')):
  try:
    with open(part) as f: merged.extend(json.load(f))
  except Exception: tool_error = True
missing = []
try:
  with open(f'/tmp/{lower}-inputs.fail') as f:
    missing = [l.strip() for l in f if l.strip()]
except FileNotFoundError: pass
if missing:
  merged.append({'filename': f'{gate}/required_inputs',
                 'namespace': 'orchestrator',
                 'successes': 0,
                 'failures': [{'msg': m} for m in missing]})
with open(os.environ['RESULT_FILE'], 'w') as f: json.dump(merged, f)
print(-1 if tool_error else sum(len(r.get('failures', [])) for r in merged))
" 2>/dev/null || echo -1)

if [ "$FAILURES" = "-1" ]; then
  echo "::error::$GATE_ID — Conftest tool error (not a policy violation)"
  echo "--- stderr ---"
  cat "$STDERR_FILE"
  echo "--- parts ---"
  cat /tmp/${LOWER}-part-*.json 2>/dev/null
  exit 1
fi

if [ "$PART" -gt 1 ]; then
  echo "   $GATE_ID: $PART Eingabedokumente ausgewertet, ein Ergebnis"
fi

# Log stderr if non-empty (warnings, deprecations)
if [ -s "$STDERR_FILE" ]; then
  echo "::warning::$GATE_ID stderr: $(cat "$STDERR_FILE" | head -3)"
fi

if [ "$FAILURES" = "0" ]; then
  echo "✅ $GATE_ID PASS"
  echo "result=PASS" >> "$GITHUB_OUTPUT"
else
  echo "❌ $GATE_ID FAIL ($FAILURES violations)"
  python3 -c "
import json
with open('$RESULT_FILE') as f: data = json.load(f)
for r in data:
  for f in r.get('failures', []):
    print(f'  → {f[\"msg\"]}')
" 2>/dev/null || true
  echo "result=FAIL" >> "$GITHUB_OUTPUT"
fi