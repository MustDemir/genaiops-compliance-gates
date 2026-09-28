#!/usr/bin/env python3
"""rego_inputs.py — which input fields each deny/warn/violation rule of every policy reads.

Basis of the element matrix (coverage review 07): a duty's
element counts as checked only if some rule fails when that element is missing or
wrong. Check descriptions say what a check is meant to test; this reads what the
code tests, from the OPA AST (opa parse), helper rules resolved transitively.

Usage:
  python3 tools/rego_inputs.py out.json      # needs opa on PATH
"""
import json, subprocess, glob, re, sys, yaml
from pathlib import Path
REPO = Path(__file__).resolve().parent.parent; OPA = "opa"
KINDS = {"deny", "warn", "violation"}

def ref_path(ref):
    out = []
    for t in ref:
        if t["type"] in ("var",) : out.append(t["value"] if not out else "[" + t["value"] + "]")
        elif t["type"] == "string": out.append(t["value"])
        elif t["type"] == "number": out.append(str(t["value"]))
        else: out.append("[?]")
    return out

def walk(node, found):
    if isinstance(node, dict):
        if node.get("type") == "ref" and isinstance(node.get("value"), list) and node["value"]:
            found.append(node["value"])
        for v in node.values(): walk(v, found)
    elif isinstance(node, list):
        for v in node: walk(v, found)

def strings(node, acc):
    if isinstance(node, dict):
        if node.get("type") == "string": acc.append(node["value"])
        for v in node.values(): strings(v, acc)
    elif isinstance(node, list):
        for v in node: strings(v, acc)

inv = []
for f in sorted(glob.glob(str(REPO / "policies/**/*.rego"), recursive=True)):
    if f.endswith("_test.rego"): continue
    ast = json.loads(subprocess.run([OPA, "parse", "--format", "json", f], capture_output=True, text=True, check=True).stdout)
    rules = {}
    for r in ast.get("rules", []):
        name = r["head"].get("name") or r["head"]["ref"][0]["value"]
        r["_name"] = name
        rules.setdefault(name, []).append(r)
    memo = {}
    def inputs_of(node, seen=()):
        refs = []; walk(node, refs); paths = set()
        for ref in refs:
            head = ref[0]
            if head["type"] == "var" and head["value"] == "input":
                p = ref_path(ref); paths.add(".".join(p).replace(".[", "["))
            elif head["type"] == "var" and head["value"] in rules and head["value"] not in KINDS and head["value"] not in seen:
                name = head["value"]
                if name not in memo:
                    memo[name] = set()
                    for rr in rules[name]:
                        memo[name] |= inputs_of(rr, seen + (name,))
                paths |= memo[name]
        return paths
    for kind in sorted(KINDS & set(rules)):
        for r in rules[kind]:
            s = []; strings(r.get("body", []), s); strings(r["head"].get("key", {}), s)
            msg = next((x for x in s if re.match(r"G-[A-Z]+-\d+", x)), s[0] if s else "")
            inv.append({"policy": Path(f).stem, "kind": kind, "msg": msg, "inputs": sorted(inputs_of(r))})
json.dump(inv, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
from collections import Counter
print(len(inv), "Regeln", Counter(i["kind"] for i in inv), "Policies", len({i["policy"] for i in inv}))
