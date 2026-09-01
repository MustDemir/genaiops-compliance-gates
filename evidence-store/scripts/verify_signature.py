#!/usr/bin/env python3
"""
verify_signature.py — Verify the evidence manifest's signature, identity-bound.

SPEC-05 Teil 4. Runs `cosign verify-blob` against the manifest and its bundle
and writes a verification document. It does NOT decide anything: there is no
`decision` field, and there never will be. The detector verifies, Rego decides
(B-04) — a script that both measures and judges is the split responsibility
this project removed from the drift detector in SPEC-04.

What the signature proves, and what it does not:

    It states ORIGIN and TIME. This workflow, in this repository, on this
    commit, asserted this chain head and these verdicts at this moment. It
    says NOTHING about whether the values are correct — that depends on the
    rules, and where the numbers came from was SPEC-04's question. A
    compromised CI signs a wrong record flawlessly; what rises is the cost of
    forgery, from "edit a row" to "take over the CI identity", and E-1 claims
    no more than that.

The three ways to make this call worthless (SPEC-05 Abschnitt 6.1) are refused
here rather than merely avoided:

  * a permissive `--certificate-identity-regexp` (".*", ".+") makes the call
    green while pinning nothing. This script takes an EXACT identity and
    records `identity_pinned` as its own field, because `verified: true` alone
    does not answer the question.
  * `--insecure-ignore-tlog` drops the transparency-log check. Without the log
    there is no independent timestamp and no public verifiability, and the
    proof falls back to "trust whoever hands it to you".
  * `--insecure-ignore-sct` drops the certificate-transparency proof.

None of the three is reachable through this script: it builds the cosign
invocation itself and passes no insecure flag, and `SIGNATURE_VERIFY_PINS_IDENTITY`
holds the whole repository to the same rule.

Exit codes: 0 = signature verified, 1 = verification failed (the document is
written either way — a failed verification is evidence too), 2 = error.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SIGSTORE_ISSUER = "https://token.actions.githubusercontent.com"


def load_manifest(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("evidence_manifest", {})


def read_log_index(bundle_path: Path):
    """
    Pull the Rekor log index out of the Sigstore bundle.

    The index is what makes the entry findable by a third party: it is the
    coordinate in the public log, not a value this script computes. If the
    bundle carries none, the field stays null and says so — an invented index
    would be worse than an absent one.
    """
    try:
        with open(bundle_path, encoding="utf-8") as f:
            bundle = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None

    material = bundle.get("verificationMaterial") or {}
    entries = material.get("tlogEntries") or []
    if entries and entries[0].get("logIndex") is not None:
        try:
            return int(entries[0]["logIndex"])
        except (TypeError, ValueError):
            return None

    # Older bundle layout kept the entry under rekorBundle.Payload.
    payload = ((bundle.get("rekorBundle") or {}).get("Payload") or {})
    if payload.get("logIndex") is not None:
        try:
            return int(payload["logIndex"])
        except (TypeError, ValueError):
            return None
    return None


def run_cosign(cosign: str, manifest: Path, bundle: Path, identity: str,
               issuer: str, repository: str, sha: str) -> tuple:
    cmd = [
        cosign, "verify-blob",
        "--bundle", str(bundle),
        "--certificate-identity", identity,
        "--certificate-oidc-issuer", issuer,
    ]
    # Both claims come straight out of the OIDC token. The workflow-sha binds
    # the signature to THE COMMIT: the document then states not merely "this
    # workflow signed", but "this workflow signed on this state" — which is
    # the claim a project about traceability actually needs.
    if repository:
        cmd += ["--certificate-github-workflow-repository", repository]
    if sha:
        cmd += ["--certificate-github-workflow-sha", sha]
    cmd.append(str(manifest))

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0, result, cmd


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the evidence manifest signature and write the "
                    "verification document (SPEC-05 Teil 4). Sets no decision."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--certificate-identity", required=True,
                        help="EXACT expected signer identity. No regexp option "
                             "exists here on purpose (SPEC-05 6.1).")
    parser.add_argument("--certificate-oidc-issuer", default=SIGSTORE_ISSUER)
    parser.add_argument("--workflow-repository", default=os.environ.get("GITHUB_REPOSITORY", ""))
    parser.add_argument("--workflow-sha", default=os.environ.get("GITHUB_SHA", ""))
    parser.add_argument("--cosign", default="cosign")
    args = parser.parse_args()

    manifest_path, bundle_path, out_path = Path(args.manifest), Path(args.bundle), Path(args.out)

    for path, what in ((manifest_path, "manifest"), (bundle_path, "bundle")):
        if not path.is_file():
            print(f"ERROR: {what} not found: {path}")
            return 2
    if shutil.which(args.cosign) is None and not Path(args.cosign).is_file():
        print(f"ERROR: cosign not found: {args.cosign}")
        return 2

    manifest = load_manifest(manifest_path)
    verified, result, cmd = run_cosign(
        args.cosign, manifest_path, bundle_path,
        args.certificate_identity, args.certificate_oidc_issuer,
        args.workflow_repository, args.workflow_sha,
    )

    log_index = read_log_index(bundle_path)

    document = {
        "signature_verification": {
            "gate_id": "G-OPS-05",
            "verified": verified,
            "certificate_identity": args.certificate_identity,
            "certificate_oidc_issuer": args.certificate_oidc_issuer,
            # Its own field, because `verified: true` does not answer the
            # question from SPEC-05 6.1: verified AGAINST WHAT identity.
            # True only for an exact identity — this script offers no other.
            "identity_pinned": bool(args.certificate_identity)
            and not args.certificate_identity.strip() in (".*", ".+"),
            "workflow_repository_pinned": bool(args.workflow_repository),
            "workflow_sha_pinned": bool(args.workflow_sha),
            "signed_chain_head": manifest.get("chain_head"),
            "signed_gate_verdicts_digest": manifest.get("gate_verdicts_digest"),
            # cosign checks the transparency log BY DEFAULT; it has to be
            # switched off deliberately. This script never switches it off, so
            # a successful verification means the log was checked.
            "tlog_verified": verified,
            "rekor_log_index": log_index,
            "verified_at": datetime.now(timezone.utc).isoformat(),
            # The verification reads a signature, it does not observe the
            # system — same provenance vocabulary as SPEC-04.
            "provenance": "derived",
            "signing_context": manifest.get("signing_context"),
            "manifest_run_id": manifest.get("pipeline_run_id"),
            "manifest_commit_sha": manifest.get("commit_sha"),
        }
    }
    if not verified:
        document["signature_verification"]["failure_output"] = (
            (result.stderr or result.stdout).strip()[:2000]
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(document, f, indent=2, ensure_ascii=False)
        f.write("\n")

    body = document["signature_verification"]
    print(f"Signature verification written: {out_path}")
    print(f"  verified:        {body['verified']}")
    print(f"  identity:        {body['certificate_identity']}")
    print(f"  identity pinned: {body['identity_pinned']}")
    print(f"  tlog verified:   {body['tlog_verified']} (rekor index {body['rekor_log_index']})")
    print(f"  signed head:     {body['signed_chain_head']}")
    print("  NOTE: this states origin and time, not that the values are correct.")
    if not verified:
        print((result.stderr or result.stdout).strip()[:2000])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
