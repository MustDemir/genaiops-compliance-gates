# Signature fixtures

> They live in `tests/signature/` and not under `tests/fixtures/`, because
> `opa test` loads that directory as one data document: two JSON files with the
> same top-level key merge and the whole suite fails to load. Fixtures for a
> policy input are not the same thing as data for the policy.

`signed_manifest.json` and `signed_manifest.sigstore.json` come from a REAL run:
[33507718663](https://github.com/MustDemir/genaiops-compliance-gates/actions/runs/33507718663),
branch `spec05-signing`, commit `2eaffda`. The signature is genuine and still
verifies — that is what the transparency log is for.

They are here because verification needs no OIDC token, only signing does, and
`id-token: write` stays in exactly one job. The negative cases can therefore run
real `cosign verify-blob` calls against real material without a second signing
identity ever existing.

**What these fixtures prove and what they do not.** They demonstrate the
MECHANISM: that a tampered manifest fails verification, and that verification
against a wrong identity fails. They say nothing about the current run — the
signature belongs to a past one. `verify_signature.py --input-provenance fixture`
records that in the document, and `policy_evidence_signature.rego` denies any
gate input marked that way, so a fixture can never be mistaken for this run's
evidence (B-03).

| File | What it is |
|---|---|
| `signed_manifest.json` | the signed manifest of run 33507718663 |
| `signed_manifest.sigstore.json` | its Sigstore bundle: certificate and log entry |
| `tampered_manifest.json` | the same manifest with `record_count` changed to 99 |
| `verification_valid.json` | a verification document that passes C-04..C-07 |
| `verification_head_mismatch.json` | signed head ≠ observed head → C-06 |
| `verification_tlog_off.json` | the transparency log was not checked → C-07 |

The three `verification_*.json` documents are constructed, not produced: the
states they describe cannot be created honestly. The tlog switch is forbidden
across the repository (`SIGNATURE_VERIFY_PINS_IDENTITY`), so a document saying
"the log was not checked" can only be written by hand.
