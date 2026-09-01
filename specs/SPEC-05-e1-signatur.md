# SPEC-05 — E-1: die Signatur, die eine Erzeuger-Identität trägt

**Status:** Entwurf · 31.08.2026
**Voraussetzung:** SPEC-04 und SPEC-04b abgeschlossen (Commit `c5bd2bd`)
**Bezug:** HANDBUCH 3.3 (E6-Achse), 5.3, Teil 7 Punkt 5 · HISTORIE H4.19/H4.20 · B-18

> **Werkzeugangaben geprüft.** Alle `cosign`-Aufrufe, Flags und Voreinstellungen in dieser SPEC sind gegen die cosign-Dokumentation abgeglichen (31.08.2026), nicht aus der Erinnerung geschrieben. Drei Punkte des ersten Entwurfs waren dadurch zu korrigieren: die Bundle-Endung (`.sigstore.json`, nicht `.bundle`), die Annahme, ein Aufruf ohne Identitätsangabe laufe grün durch (er bricht ab — cosign erzwingt die Angabe), und die Einstufung der Transparenzlog-Prüfung als Kür statt als Voreinstellung. Ein Vorhaben, das Behauptungen gegen ihren Gegenstand hält, fängt bei den eigenen an.

---

## 1. Anlass

SPEC-04 hat die Reihenfolge begründet: erst messen, dann signieren. „Eine Signatur auf einem erfundenen Wert ist eine kryptografisch einwandfrei bewiesene Lüge." Die Rückfrage im Fachgespräch lautet nicht „ist das signiert?", sondern **„woher kommt die Zahl?"** — seit SPEC-04b ist sie beantwortet. Damit ist diese SPEC an der Reihe.

### 1.1 Der Befund, der sie auslöst (B-18)

**Genau ein Check im Katalog trägt heute `evidence_level: "E-1"`:** G-OPS-05/C-02, „Hash-Chain-Integrität über alle Evidence-Records". Die Begründung im Gate sagt, der Verifikationsanteil sei „für sich genommen bereits ein berechneter Integritätsnachweis auf E-1-Niveau".

**Das trifft nicht zu, gemessen an der eigenen Definition.** HANDBUCH 3.3 verlangt für E-1 ein „erzeugtes und **signiertes** Artefakt; Signatur und **Erzeuger-Identität** geprüft", mit Fälschungskosten „Kompromittierung der CI-Identität". Die Kette leistet davon nichts:

| Was E-1 verlangt | Was die Hash-Kette heute leistet |
|---|---|
| Signatur | keine — SHA-256 ist eine Prüfsumme, kein Signaturverfahren |
| Erzeuger-Identität geprüft | `inserted_by` ist eine Zeichenkette, die der Schreiber selbst wählt (Default `'poc_local'`). Sie ist hash-gedeckt, also *unveränderlich festgehalten* — aber nicht *belegt* |
| Fälschungskosten = CI-Identität | Schreibzugriff auf die Datenbank. Wer die Kette ändern will, rechnet sie ab Genesis neu und legt eine formal einwandfreie Kette vor |

Die Kette ist **manipulationsevident gegen Teiländerungen**, und das ist wertvoll — aber es ist eine Aussage über innere Konsistenz, nicht über Herkunft. Nach der Fälschungskosten-Ordnung der E6-Achse liegt sie damit auf E-0 mit einer Zusatzeigenschaft, nicht auf E-1.

### 1.2 Der zweite Teil des Befunds: in der CI überlebt die Kette den Lauf nicht

`EVIDENCE_DB: /tmp/evidence_pipeline.db`. Die Pipeline legt die Datenbank an, schreibt 17 Records hinein, verifiziert die Kette — und der Runner wird zerstört. **Es gibt keinen `upload-artifact`-Schritt.** Verifiziert wird die innere Konsistenz einer Datenbank, die zwanzig Sekunden existiert hat und die niemand je wiedersehen wird.

> Das ist kein Nebenaspekt, sondern die eigentliche Pointe dieser SPEC. Die Signatur ist **keine Verzierung auf der Kette** — sie ist das, was die Evidenz eines Laufs überhaupt aus dem Runner herausträgt. Ohne sie ist der lückenlose Audit-Trail eine Eigenschaft, die pro Lauf entsteht und mit dem Lauf vergeht.

### 1.3 Derselbe Fehlertyp, zum sechsten Mal

Eine Deklaration existiert, der Mechanismus nicht (B-02, B-11, B-12, B-13, B-17). Hier ist es die Beweisstufe selbst: das Feld `evidence_level` wurde eingeführt, um Beweiskraft prüfbar zu machen, und der einzige Wert oberhalb von E-0, den der Katalog trägt, hält seiner eigenen Definition nicht stand. **Die Korrektur der Einstufung ist deshalb Teil 1 und hängt an nichts** — eine falsche Einstufung ist schädlicher als eine niedrige, weil sie den Leser beruhigt.

---

## 2. Was diese SPEC nicht enthält

| Nicht enthalten | Warum, und wohin es gehört |
|---|---|
| **Image-Signatur und SLSA-Provenance** für `ghcr.io/.../ambient-ai-scribe` | Naheliegend und billig, aber eine Aussage über die **Lieferkette**, nicht über die **Evidenz**. Das Vorhaben handelt vom Nachweis der Konformitätsprüfung, nicht vom Artefakttransport. Eigene SPEC |
| **Kettenkontinuität über Läufe hinweg** | Die CI baut je Lauf eine neue SQLite; in Betrieb ist der Store PostgreSQL und persistent. Eine Kette über die Lebensdauer des Systems ist eine eigene Frage — diese SPEC macht den **einzelnen Lauf** überprüfbar, und benennt die Lücke, statt sie zu schließen (6.3) |
| **Die Fristenuhr aus Art. 73** | Ein Transparenzlog-Eintrag liefert einen unabhängigen Zeitstempel, und genau den braucht eine Fristenaussage. **Aber:** Art. 26 Abs. 5 und Art. 73 sind nicht EUR-Lex-abgeglichen. HANDBUCH 6.1 verbietet den Bau der Meldekaskade davor, und das gilt auch, wenn der technische Baustein plötzlich vorliegt |
| **Eigene PKI, Schlüsselverwaltung, HSM** | Keyless ist die Entscheidung, Begründung in 4.1. Ein langlebiger privater Schlüssel in einem GitHub-Secret wäre eine schlechtere Erzeuger-Identität als gar keine, weil er wie eine gute aussieht |
| **E-2** | Braucht einen Cluster (D-29). Unberührt |

---

## 3. Teil 1 — Die Einstufung korrigieren

Vor allem anderen, unabhängig vom Rest der SPEC:

- G-OPS-05/C-02: `evidence_level: "E-1"` → **`"E-0"`**
- `evidence_level.rationale` des Gates nachziehen: die Kette ist manipulationsevident gegen Teiländerungen und bindet keine Herkunft; E-1 folgt mit dieser SPEC
- HISTORIE: B-18 aufnehmen, README-Satz „G-OPS-05 pairs an E-0 annotation check with an E-1 hash-chain check" korrigieren

**Damit trägt der Katalog vorübergehend keinen einzigen E-1-Check.** Das ist der ehrliche Zwischenzustand und soll sichtbar sein.

---

## 4. Teil 2 — Das Evidenz-Manifest

Am Ende eines Laufs entsteht ein Dokument, das den Lauf zusammenfasst und **signierbar** ist:

```json
{
  "evidence_manifest": {
    "pipeline_run_id": "pipeline-20260831-122132-c5bd2bd3",
    "commit_sha": "c5bd2bd37442ae19cf725d757c37c11588c553af",
    "schema_version": "v06",
    "record_count": 17,
    "genesis_hash": "<hash des ersten Records>",
    "chain_head": "<hash des letzten Records>",
    "gate_verdicts_digest": "<sha256 ueber 'gate_id:decision', sortiert>",
    "runtime_mode": "mock",
    "signing_context": "ci",
    "created_at": "2026-08-31T12:21:53+00:00"
  }
}
```

**Warum ein Manifest und nicht 17 Signaturen.** Die Kette bindet die Records bereits aneinander; signiert werden muss ihr Kopf. Siebzehn Transparenzlog-Einträge für eine Aussage wären Aufwand ohne Zugewinn.

**Warum `gate_verdicts_digest` zusätzlich zum `chain_head`.** Die Urteile stecken über das Feld `decision` bereits in der gehashten Payload, der Kopf deckt sie also ab. Der Digest macht das Manifest aber **ohne die Datenbank prüfbar**: ein Leser, der nur den Pipeline-Report hat, kann ihn gegen die Signatur halten. Evidenz, deren Prüfung die Datenbank voraussetzt, die gerade gelöscht wurde, hilft niemandem.

**Warum `signing_context`.** Siehe 6.1 — und es ist derselbe Baustein wie `runtime_mode` in SPEC-04: ein Feld, das den Erzeugungskontext benennt, in die gehashte Payload gehört und in der CI gegen einen erwarteten Wert geprüft wird.

**Das Manifest wird auf jedem Lauf geschrieben**, auch lokal und auch bei blockierender Pipeline. Ein Nachweis, der nur bei Erfolg entsteht, kann den Fehlschlag nicht belegen — dieselbe Begründung wie beim Drift-Messdokument in SPEC-04.

---

## 5. Teil 3 — Signieren, keyless

### 5.1 Warum keyless

`cosign sign-blob --yes` ohne Schlüsselmaterial: die Signatur wird mit einem kurzlebigen Zertifikat erzeugt, das Sigstore gegen das **OIDC-Token des GitHub-Actions-Laufs** ausstellt. Die Erzeuger-Identität ist damit nicht „wer hatte den Schlüssel", sondern „welcher Workflow, in welchem Repository, auf welchem Ref" — und das ist genau die Identität, die E-1 meint.

Die Alternative — ein langlebiger privater Schlüssel in einem Repository-Secret — wäre **schlechter als keine Signatur**, weil sie wie eine gute aussieht: Fälschungskosten wären „Zugriff auf ein Secret", nicht „Kompromittierung der CI-Identität", und nichts am Artefakt würde den Unterschied zeigen.

### 5.2 Umsetzung

- `cosign` als **SHA-gepinnte** Installation, wie alle Actions seit `ecf4af9`. Eine Signaturkette, deren Werkzeug über einen beweglichen Tag bezogen wird, hat ihre Vertrauensbasis an anderer Stelle wieder aufgegeben
- `permissions: id-token: write` für den signierenden Job. **Das ist eine bewusste Rechteerhöhung** gegenüber dem heutigen `contents: read` und gehört als solche in den Commit begründet — sie ist die Voraussetzung dafür, dass Sigstore die Identität überhaupt bestätigen kann
- `cosign sign-blob --yes evidence_manifest.json --bundle evidence_manifest.sigstore.json` — die Endung `.sigstore.json` ist die geltende Bundle-Konvention, nicht `.bundle`
- Bundle **und** Manifest als `upload-artifact` — sonst wiederholt sich 1.2 mit einem zusätzlichen Schritt

---

## 6. Teil 4 — Verifizieren, und zwar identitätsgebunden

### 6.1 Der Aufruf, und die drei Wege, ihn wertlos zu machen

**Cosign selbst verhindert den naheliegendsten Fehler:** im keyless-Fluss verlangt `verify-blob`, dass entweder `--certificate-identity` oder `--certificate-identity-regexp` gesetzt ist, und ebenso für den Issuer. Ein Aufruf ohne Identitätsangabe läuft nicht grün durch, sondern bricht ab. Das ist eine gute Voreinstellung und nimmt dieser SPEC eine Sorge ab — **die verbleibenden Wege sind dafür weniger auffällig.**

```
cosign verify-blob \
  --bundle evidence_manifest.sigstore.json \
  --certificate-identity "https://github.com/$GITHUB_REPOSITORY/.github/workflows/gate-pipeline.yml@$GITHUB_REF" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  --certificate-github-workflow-repository "$GITHUB_REPOSITORY" \
  --certificate-github-workflow-sha "$GITHUB_SHA" \
  evidence_manifest.json
```

Die beiden `--certificate-github-workflow-*`-Flags prüfen Claims aus dem OIDC-Token direkt. `--certificate-github-workflow-sha` bindet die Signatur an **den Commit** — damit belegt der Nachweis nicht nur „dieser Workflow hat signiert", sondern „dieser Workflow hat auf diesem Stand signiert". Für ein Vorhaben, dessen Kern die Rückführbarkeit ist, ist das der eigentlich interessante Claim.

> **Drei Flags sind verboten, und jedes einzelne hebt die Beweisstufe auf:**
>
> - **`--certificate-identity-regexp` mit einem alles zulassenden Muster** (`.*`, `.+`). Der Aufruf wird grün und prüft nichts. Dieselbe Lücke wie B-17: der Mechanismus ist da und wirkt nicht
> - **`--insecure-ignore-tlog`** hebt die Prüfung des Transparenzlogs auf. Cosign sagt es im Hilfetext selbst: „Artifacts cannot be publicly verified when not included in a log." Ohne Log gibt es keinen unabhängigen Zeitstempel und keine öffentliche Nachprüfbarkeit — der Nachweis fällt auf „vertraue dem, der ihn vorlegt" zurück
> - **`--insecure-ignore-sct`** hebt den Nachweis der Aufnahme ins Certificate-Transparency-Log auf
>
> Sie heißen nicht ohne Grund `insecure-*`. Ein Repository, das Beweiskraft zum Gegenstand hat, benutzt sie nicht — und verlässt sich nicht darauf, dass niemand auf die Idee kommt, sondern prüft es (Abschnitt 9).

### 6.2 Der Detektor verifiziert, Rego entscheidet

Wie in SPEC-04 (Drift) und SPEC-04b: die Verifikation erzeugt ein **Nachweisdokument**, conftest wertet es aus, und das Urteil von Rego ist das, was aufgezeichnet wird. Ein Verifikationsskript, das seine eigene `decision` setzt, wäre die Doppelzuständigkeit aus B-04 an neuer Stelle.

```json
{
  "signature_verification": {
    "gate_id": "G-OPS-05",
    "verified": true,
    "certificate_identity": "https://github.com/.../gate-pipeline.yml@refs/heads/domain_netzbetrieb",
    "certificate_oidc_issuer": "https://token.actions.githubusercontent.com",
    "identity_pinned": true,
    "signed_chain_head": "<hash aus dem Manifest>",
    "tlog_verified": true,
    "rekor_log_index": 123456789,
    "verified_at": "...",
    "provenance": "derived",
    "signing_context": "ci"
  }
}
```

`identity_pinned` ist ein eigenes Feld, weil `verified: true` allein die Frage aus 6.1 nicht beantwortet.

---

## 7. Teil 5 — Das Gate nachziehen

G-OPS-05 bekommt einen zweiten Input und vier Checks. Zwei Inputs, ein Gate, **ein** Evidence-Record — die Form aus SPEC-03/SPEC-04b, nicht zwei Urteile unter einer Gate-ID.

```yaml
required_inputs:
  - kind: "signature_verification"
    observes_runtime: false
    evaluated_by: "policies/operations/policy_evidence_signature.rego"
    produced_by: "evidence-store/scripts/verify_signature.py"
    rationale: "C-04 bis C-07 pruefen eine Signaturpruefung. Fehlt sie, wurde nicht geprueft."
```

| Check | Prüft | Severity | E |
|---|---|---|---|
| **C-04** | Ein Signaturnachweis liegt vor und die Signatur ist gültig | MUST | E-1 |
| **C-05** | Die Signatur stammt von der **erwarteten** Identität und dem erwarteten OIDC-Issuer (`identity_pinned`) | MUST | E-1 |
| **C-06** | Der signierte `chain_head` stimmt mit dem Kopf der geprüften Kette überein | MUST | E-1 |
| **C-07** | Die Transparenzlog-Prüfung war aktiv (`tlog_verified`) und ein Log-Index liegt vor | MUST | E-1 |

**C-06 ist der Check, den man beim Entwurf übersieht.** Ohne ihn ließe sich ein gültig signiertes Manifest vorlegen, das mit der Datenbank, die verifiziert wurde, nichts zu tun hat — eine einwandfreie Signatur auf einer unbeteiligten Aussage. Genau die Lücke, gegen die SPEC-04 „Messung vor Signatur" gesetzt hat, hier auf der Signaturseite.

**C-07 war im Entwurf als SHOULD gedacht — das war falsch herum gedacht.** Cosign prüft den Transparenzlog **standardmäßig**; man muss ihn mit `--insecure-ignore-tlog` aktiv abschalten. Ein SHOULD hätte also nicht eine Kür beschrieben, sondern die Voreinstellung zur Option erklärt und damit eingeladen, sie abzuschalten, wenn der Dienst klemmt. C-07 ist deshalb MUST und prüft, dass die Log-Verifikation **stattgefunden hat**.

Der Preis ist zu benennen: Sigstore ist ein Dienst Dritter, und seine Nichterreichbarkeit blockiert damit den Lauf. Das ist dieselbe Abwägung wie beim fail-closed Evidenzpfad (B-16) — ein Nachweissystem, dessen Ausfall durchwinkt, ist keines — und dieselbe Einschränkung: es entsteht eine Außenabhängigkeit, die in Betrieb als solche zu führen ist.

**`evidence_level.current` von G-OPS-05 bleibt E-0.** C-01 prüft weiterhin als MUST eine Pod-Annotation, und ein Gate ist so stark wie sein schwächster bindender Check. Die Regel gilt hier gegen das eigene Interesse — sie wurde bei G-OPS-03 so angewandt und wird nicht gelockert, weil das Ergebnis diesmal unbequem ist.

---

## 8. Teil 6 — Lokale Läufe

Keyless braucht eine OIDC-Identität. Lokal gibt es keine. **Das ist kein zu behebender Mangel, sondern die Definition:** HANDBUCH 5.3 sagt „E-1 braucht die CI".

### 8.1 `signing_context`, und warum es keine Hintertür ist

Das Manifest deklariert seinen Erzeugungskontext:

- **`ci`** — Signatur ist Pflicht, C-04/C-05 sind `deny`
- **`local`** — das Manifest sagt von sich, dass es unsigniert ist. C-04 **warnt**, statt zu blockieren; der Lauf bleibt fahrbar und die Evidenz sagt, auf welcher Stufe er steht

Der offensichtliche Einwand: dann setzt jemand in der CI `local` und ist fein raus. Deshalb, wörtlich analog zur `runtime_mode`-Prüfung aus SPEC-04b Teil 2:

> Die CI prüft nach dem Erzeugen, dass das Manifest `signing_context: "ci"` trägt, und **bricht andernfalls ab**. Ein Integrity-Check hält fest, dass diese Prüfung im Workflow steht.

`prepare_inputs.py` darf **niemals** einen Signaturnachweis erzeugen. Ein Walkthrough, der sich seine eigene Signatur ausstellt, ist der stille Fallback aus B-03 in neuem Gewand.

---

## 9. Integrity-Checks

Drei neue, jeder in **beide Richtungen** gegenzuprüfen (B-16, und zuletzt zweimal in Folge nötig gewesen, H4.19):

| Check | Severity | Hält fest |
|---|---|---|
| **`E1_CLAIMS_ARE_SIGNED`** | HIGH | Jeder Check mit `evidence_level: E-1` gehört zu einem Gate, das einen Signatur-Input deklariert. Verhindert die Wiederkehr von B-18 — eine E-1-Behauptung ohne Signaturmechanismus |
| **`SIGNATURE_VERIFY_PINS_IDENTITY`** | HIGH | Jeder `cosign verify-blob`-Aufruf trägt `--certificate-identity` und `--certificate-oidc-issuer`; **keiner** trägt `--certificate-identity-regexp` mit einem alles zulassenden Muster, `--insecure-ignore-tlog` oder `--insecure-ignore-sct`. Die drei Abschaltwege aus 6.1, in Testform |
| **`SIGNING_CONTEXT_ASSERTED`** | MEDIUM | Der Workflow prüft `signing_context == "ci"` und bricht sonst ab |

`E1_CLAIMS_ARE_SIGNED` ist die Verallgemeinerung von `REQUIRED_INPUTS_ENFORCED` auf die Beweisstufen-Achse — und **auf beiden Aufrufern zu prüfen**, Orchestrator und Workflow. Die Lehre aus B-17 lautet nicht „gründlicher prüfen", sondern: bei einem neuen Mechanismus ist zu fragen, **wo überall** er wirken muss.

---

## 10. Reihenfolge

1. **Teil 1** — Einstufung korrigieren. Hängt an nichts, sofort machbar, und der ehrliche Zwischenzustand ist erwünscht
2. **Teil 2** — Manifest erzeugen, unsigniert, mit `chain_head` und `signing_context`. Läuft lokal und in der CI
3. **Teil 3** — Signieren in der CI, `id-token: write`, `upload-artifact`
4. **Teil 4** — identitätsgebundene Verifikation, Nachweisdokument, Rego
5. **Teil 5** — Gate nachziehen, `required_inputs`, C-04…C-07
6. **Negativfälle** in den bestehenden `negative-cases`-Job
7. Doku: CHANGELOG, README, HANDBUCH 5.2/5.3, HISTORIE B-18

Teil 1 und 2 sind unabhängig voneinander machbar. Ab Teil 3 ist die Reihenfolge bindend.

---

## 11. Tests

Jeder Negativfall mit Gegenprobe daneben — ein Fall, der aus dem falschen Grund rot ist, sieht aus wie einer, der aus dem richtigen rot ist:

| Fall | Erwartung | Gegenprobe |
|---|---|---|
| Manifest nach dem Signieren verändert | `verify` schlägt fehl | unverändertes Manifest verifiziert |
| Verifikation gegen die **falsche** erwartete Identität | schlägt fehl | gegen die richtige besteht sie |
| Signaturnachweis fehlt | G-OPS-05 FAIL über `required_inputs`, mit benanntem Input | vorhanden → PASS |
| `chain_head` im Manifest ≠ Kopf der Datenbank | C-06 `deny` | übereinstimmend → PASS |
| `signing_context: "local"` in der CI | Job bricht ab | `"ci"` → Lauf geht weiter |
| Verifikation mit `--insecure-ignore-tlog` | `tlog_verified: false` → C-07 `deny` | ohne das Flag → `true`, PASS |
| Verifikation mit `--certificate-identity-regexp '.*'` | `SIGNATURE_VERIFY_PINS_IDENTITY` schlägt an | exakte Identität → Check grün |

Zusätzlich:

- **Hash-Parität bleibt grün** — `signing_context` gehört in die gehashte Payload, also greifen `test_hash_parity.py` (4 Payload-Varianten) und die Chain-Migration. Bei Schema-Änderung: Migration `v06 → v07` mit Cutoff-Eintrag, wie bei `runtime_mode`
- **Gesamtsuite unverändert:** 199 Rego, 36 `test_all.py`, Integrity 0 actionable, 21 Drift-E2E, 19 eval_runner
- **Kein hartkodierter Zählstand** in neuen Workflow-Ausgaben (`WORKFLOW_CLAIMS_NO_COUNTS`)

---

## 12. Definition of Done

- [ ] G-OPS-05/C-02 auf E-0 zurückgestuft, `rationale` nachgezogen, README-Satz korrigiert
- [ ] B-18 in HISTORIE aufgenommen, im Befundregister und als eigener Abschnitt
- [ ] `evidence_manifest.json` wird auf **jedem** Lauf erzeugt, lokal wie in der CI, auch bei blockierender Pipeline
- [ ] Manifest trägt `chain_head`, `genesis_hash`, `gate_verdicts_digest`, `record_count`, `signing_context`
- [ ] `cosign` SHA-gepinnt installiert; `id-token: write` nur im signierenden Job, Rechteerhöhung im Commit begründet
- [ ] Manifest **und** Bundle als `upload-artifact` — die Evidenz verlässt den Runner
- [ ] `verify_signature.py` verifiziert identitätsgebunden und schreibt ein Nachweisdokument, ohne eigene `decision`
- [ ] Verifikation bindet zusätzlich `--certificate-github-workflow-repository` und `--certificate-github-workflow-sha` — die Signatur hängt am Commit, nicht nur am Workflow
- [ ] Kein `--insecure-ignore-tlog`, kein `--insecure-ignore-sct`, kein alles zulassendes `--certificate-identity-regexp` im gesamten Repository
- [ ] Integrity-Check `SIGNATURE_VERIFY_PINS_IDENTITY` (HIGH), beidseitig gegengeprüft
- [ ] Integrity-Check `SIGNING_CONTEXT_ASSERTED` (MEDIUM), beidseitig gegengeprüft
- [ ] G-OPS-05: `required_inputs: signature_verification`, C-04…C-07 mit Severity und `evidence_level`; C-07 als MUST, mit der Außenabhängigkeit als begründeter Abwägung im Gate
- [ ] Orchestrator **und** Workflow erzwingen den neuen Pflichtinput (die Lehre aus B-17)
- [ ] Integrity-Check `E1_CLAIMS_ARE_SIGNED` (HIGH), beidseitig gegengeprüft
- [ ] `evidence_level.current` von G-OPS-05 **bleibt E-0**, Begründung im Gate nachgezogen
- [ ] Sechs Negativfälle aus Abschnitt 11 im `negative-cases`-Job, je mit Gegenprobe
- [ ] Hash-Parität und Chain-Migration grün; bei Payload-Änderung Migration v06 → v07 mit Cutoff
- [ ] README, CHANGELOG, HANDBUCH 5.2/5.3 und Teil 7 nachgezogen; `README_COUNTS_CURRENT` grün
- [ ] Formulierung geprüft: nirgends steht, die Signatur belege die **Richtigkeit** der Werte (6.3)

---

## 13. Was E-1 nicht leistet

Gehört in die Außendarstellung, bevor jemand mehr hineinliest (B-13):

**Die Signatur belegt Herkunft und Zeitpunkt, nicht Wahrheit.** Sie sagt: dieser Workflow, in diesem Repository, auf diesem Ref hat zu diesem Zeitpunkt diese Kette und diese Urteile behauptet. Ob die Urteile richtig sind, hängt an den Regeln; ob die Werte stimmen, hing an SPEC-04. Eine kompromittierte CI signiert einen falschen Record einwandfrei — die Fälschungskosten steigen von „eine Zeile ändern" auf „die CI-Identität übernehmen", und mehr behauptet die E6-Achse für E-1 auch nicht.

**Die Kettenkontinuität über Läufe hinweg bleibt offen.** Diese SPEC macht den einzelnen Lauf überprüfbar und aus dem Runner heraustragbar. Eine Kette über die Lebensdauer des Systems — mit persistentem Store, Anker je Lauf und einer Aussage über Lücken *zwischen* Läufen — ist eine eigene Frage und wird hier nicht beantwortet, sondern benannt.

**Und E-1 hebt kein Gate auf E-1.** Solange G-OPS-05/C-01 als MUST eine Pod-Annotation prüft, bleibt das Gate auf E-0. Was steigt, ist die Beweiskraft einzelner Checks — sichtbar in `policy_checks[].evidence_level`, und genau dafür ist die Feldebene da.
