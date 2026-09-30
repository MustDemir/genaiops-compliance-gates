#!/usr/bin/env python3
"""rego_inputs.py — which input fields each deny/warn/violation rule of every policy reads.

Basis of the element matrix (coverage review 07, run 2 in review 11): a duty's
element counts as checked only if some rule fails when that element is missing or
wrong. Check descriptions say what a check is meant to test; this reads what the
code tests, from the OPA AST (opa parse), helper rules resolved transitively.

Run 2 (package 3b) resolves what run 1 could not see:
  * aliases        _ce := input.change_event; _ce.evidence.x   -> change_event.evidence.x
  * object.get     object.get(_doc, "thresholds", [])          -> thresholds
  * iteration      some t in ...thresholds; t.status            -> thresholds[].status
  * local names    ref := _ce.evidence.y; ref != ""            -> change_event.evidence.y
  * annotations    _pod_annotations["genaiops.io/x"]           -> ...annotations[genaiops.io/x]
Run 1 stopped at the alias and reported 'input.change_event' for every rule of
G-OPS-06; a matrix built on that could not tell which rule reads the handover
record.

A field is rendered without the leading 'input.'. A Gatekeeper object is read
either as input.review.object or as input (Conftest); both spellings are listed.

Usage:
  python3 tools/rego_inputs.py out.json      # needs opa on PATH
"""
from __future__ import annotations

import glob
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OPA = "opa"
KINDS = {"deny", "warn", "violation"}
_ID = re.compile(r"^(G-[A-Z]+-\d+)(?:/([A-Za-z0-9-]+))?")
_PLAIN = re.compile(r"^[A-Za-z0-9_]+$")


def _render(segs: list[str]) -> str:
    out = ""
    for s in segs:
        if s == "[]":
            out += "[]"
        elif _PLAIN.match(s):
            out += ("." if out else "") + s
        else:
            out += f"[{s}]"
    return out


def _strings(node, acc):
    if isinstance(node, dict):
        if node.get("type") == "string":
            acc.append(node["value"])
        for v in node.values():
            _strings(v, acc)
    elif isinstance(node, list):
        for v in node:
            _strings(v, acc)


class _Policy:
    """Symbolic reader of one policy: which input paths does a rule depend on?"""

    def __init__(self, ast: dict):
        self.rules: dict[str, list] = {}
        for r in ast.get("rules", []):
            name = r["head"].get("name") or r["head"]["ref"][0]["value"]
            self.rules.setdefault(name, []).append(r)
        self._values: dict[str, list] = {}
        self._reads: dict[str, set] = {}

    # --- what a term denotes (a location in input) ---------------------------
    def denotes(self, term, env, seen=()) -> list[list[str]]:
        t = term.get("type")
        if t == "var":  # a rule or a local name used as a whole: _doc, _containers
            term = {"type": "ref", "value": [term]}
            t = "ref"
        if t == "ref":
            head, rest = term["value"][0], term["value"][1:]
            if head.get("type") != "var":
                return []
            name = head["value"]
            if name == "input":
                bases = [["input"]]
            elif name in env:
                bases = env[name]
            elif name in self.rules and name not in KINDS and name not in seen:
                bases = self.value_of(name, seen + (name,))
            else:
                return []
            segs = [r["value"] if r.get("type") == "string" else "[]" for r in rest]
            return [b + segs for b in bases]
        if t == "call":
            fn = term["value"][0]
            args = term["value"][1:]
            if fn.get("type") == "ref" and [x.get("value") for x in fn["value"]] == ["object", "get"] \
                    and len(args) >= 2 and args[1].get("type") == "string":
                return [b + [args[1]["value"]] for b in self.denotes(args[0], env, seen)]
        return []

    def value_of(self, name, seen) -> list[list[str]]:
        if name not in self._values:
            self._values[name] = []
            vals = []
            for r in self.rules[name]:
                v = r["head"].get("value")
                if v is not None:
                    vals += self.denotes(v, {}, seen)
            self._values[name] = vals
        return self._values[name]

    # --- what a rule reads --------------------------------------------------
    def reads_of_rule(self, rule, seen=()) -> set[str]:
        env: dict[str, list] = {}
        paths: set[str] = set()
        for expr in rule.get("body", []):
            terms = expr.get("terms")
            # local bindings, in body order
            if isinstance(terms, list) and len(terms) == 3 and terms[0].get("type") == "ref":
                op = [x.get("value") for x in terms[0]["value"]]
                if op in (["assign"], ["eq"]) and terms[1].get("type") == "var":
                    env[terms[1]["value"]] = self.denotes(terms[2], env, seen)
            if isinstance(terms, dict) and "symbols" in terms:
                for sym in terms["symbols"]:
                    if sym.get("type") == "call":
                        fn = [x.get("value") for x in sym["value"][0]["value"]]
                        args = sym["value"][1:]
                        if fn == ["internal", "member_2"] and args[0].get("type") == "var":
                            env[args[0]["value"]] = [p + ["[]"] for p in self.denotes(args[1], env, seen)]
                        elif fn == ["internal", "member_3"] and args[1].get("type") == "var":
                            env[args[1]["value"]] = [p + ["[]"] for p in self.denotes(args[2], env, seen)]
            paths |= self._walk(expr, env, seen)
        for part in ("key", "value"):
            if rule["head"].get(part) is not None:
                paths |= self._walk(rule["head"][part], env, seen)
        return paths

    def _walk(self, node, env, seen) -> set[str]:
        found: set[str] = set()
        if isinstance(node, dict):
            if node.get("type") in ("ref", "call", "var"):
                for p in self.denotes(node, env, seen):
                    if p[:1] == ["input"]:
                        found.add(_render(p[1:]) or "input")
                if node.get("type") in ("ref", "var"):
                    head = node["value"][0] if node.get("type") == "ref" else node
                    name = head.get("value") if head.get("type") == "var" else None
                    if name in self.rules and name not in KINDS and name not in seen and name not in env:
                        found |= self.reads_of_helper(name, seen + (name,))
            for v in node.values():
                found |= self._walk(v, env, seen)
        elif isinstance(node, list):
            for v in node:
                found |= self._walk(v, env, seen)
        return found

    def reads_of_helper(self, name, seen) -> set[str]:
        if name not in self._reads:
            self._reads[name] = set()
            acc: set[str] = set()
            for r in self.rules[name]:
                acc |= self.reads_of_rule(r, seen)
            self._reads[name] = acc
        return self._reads[name]


def inventar(repo: Path = REPO, opa: str = OPA) -> list[dict]:
    """Every deny/warn/violation rule: policy, kind, message, gate, check, fields read."""
    inv = []
    for f in sorted(glob.glob(str(repo / "policies/**/*.rego"), recursive=True)):
        if f.endswith("_test.rego"):
            continue
        ast = json.loads(subprocess.run([opa, "parse", "--format", "json", f],
                                        capture_output=True, text=True, check=True).stdout)
        pol = _Policy(ast)
        for kind in sorted(KINDS & set(pol.rules)):
            for r in pol.rules[kind]:
                s: list[str] = []
                _strings(r.get("body", []), s)
                _strings(r["head"].get("key", {}), s)
                msg = next((x for x in s if _ID.match(x)), s[0] if s else "")
                m = _ID.match(msg)
                felder = sorted(pol.reads_of_rule(r))
                inv.append({
                    "policy": Path(f).stem,
                    "kind": kind,
                    "gate": m.group(1) if m else None,
                    "check": m.group(2) if m else None,
                    "msg": msg,
                    "felder": felder,
                })
    return inv


def liest(regel: dict, feld: str) -> bool:
    """Does the rule read this field? Suffix match at a segment boundary, so that
    'annotations[genaiops.io/x]' matches both the Gatekeeper and the Conftest spelling."""
    return any(f == feld or f.endswith("." + feld) for f in regel["felder"])


if __name__ == "__main__":
    inv = inventar()
    json.dump(inv, open(sys.argv[1], "w"), ensure_ascii=False, indent=1)
    from collections import Counter
    print(len(inv), "Regeln", Counter(i["kind"] for i in inv), "Policies", len({i["policy"] for i in inv}),
          "ohne Feld", sum(1 for i in inv if not i["felder"]))
