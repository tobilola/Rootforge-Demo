# Rootforge

**Rootforge investigates protocol deviations for clinical-research teams.**
It reads the raw evidence — deviation report, protocol, SOP, training record,
handoff log, correspondence — and returns a cited timeline, an explicit list of
what the record is missing, falsifiable root-cause hypotheses, and draft
corrective actions for qualified human review.

## The part that matters

A language model asked to investigate will assert things no document supports.
In a regulated setting that is not a cosmetic defect, it is *the* defect.

So every claim Rootforge produces carries a citation **and a verbatim quote**,
and every quote is checked against the source text before a reviewer sees it
(`rootforge/verify.py`). Claims that fail are flagged in red and carried into
the exported report, never silently dropped — suppressing an ungrounded claim
hides the signal the reviewer most needs.

The workspace ships with two synthetic cases. **RF-DEMO-001** is the clean run: 28/28 claims grounded, 18 by exact span match. **RF-DEMO-002** is the deliberate safety case: the recorded model output asserts a motive the documents never state ("the coordinator back-dated the entry"). The verifier flags it, excludes it from confirmed findings, and retains it for reviewer inspection in the interface and report. This is intentional—not a finding about a real person or event. A safety mechanism that never visibly fires proves nothing.

Root cause is never determined autonomously. Hypotheses are labelled as such
and each must state what evidence would disconfirm it.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...     # or OPENAI_API_KEY
streamlit run app.py
```

Without a key the app runs in **replay mode** against a recorded response so the
demo is reproducible offline. Replay mode is labelled in the UI; grounding
verification runs against real source text either way.

```bash
pytest        # 15 tests, including adversarial grounding checks
```

## What the tests cover

- **Grounding.** Fabricated quotes, real quotes attributed to the wrong
  document, unknown refs and uncited claims must all be rejected.
- **Gold set.** The five findings a competent human investigator produces on
  this case must appear, matched against synonym sets so the test survives
  rewording.
- **Separation.** Hedging language must not appear in `confirmed`; every
  hypothesis must be falsifiable; every action must trace to a finding.

## The demo case

Synthetic and fictional throughout. No patient, employer, or confidential
research data. It is built so the interesting findings require *joining*
documents rather than looking anything up: the technician was trained on
SOP-014 **v2**, under which escalation was due only after the 60-minute limit
had passed, while **v3** — in force since 1 July, training assigned but never
completed — moved the trigger to 45 minutes. No single document says this.

## Boundaries

- Outputs are drafts. Never an autonomous quality decision.
- Hypotheses stay separated from confirmed evidence, structurally, not by
  convention.
- Production use requires validation, audit trail, access control, retention
  policy, and customer-specific governance. None of that is here yet.
