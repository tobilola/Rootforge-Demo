# Rootforge YC demo v2.1

Rootforge helps clinical-research teams turn scattered protocol-deviation evidence into a cited, review-ready investigation draft.

This YC-focused demo deliberately shows one complete synthetic case. It reconstructs a timeline, surfaces missing and conflicting information, proposes falsifiable root-cause hypotheses, drafts corrective and preventive actions, and exports a Word review draft. All outputs remain subject to qualified human review.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

No API key is required for the reliable demonstration path. Without a key, the app transparently displays a previously generated response for the fixed synthetic case and runs citation checks against the included source text. With `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` set, the engine runs live analysis.

## Test

```bash
pytest -q
```

The test suite checks citation failures, expected investigation findings, separation of hypotheses from confirmed facts, falsifiability, and action traceability.

## Demo boundaries

- The case and all evidence are fictional.
- This prototype is not validated for production or clinical use.
- Rootforge proposes hypotheses; it does not determine root cause.
- Human reviewers retain responsibility for conclusions and actions.
- Production use would require appropriate validation, security, access control, audit trails, retention, and customer governance.

## Suggested YC recording flow

1. Show the synthetic case and its six evidence sources.
2. Run the investigation.
3. Open the cited timeline and inspect one source quote.
4. Show one missing record and one contradiction.
5. Open a root-cause hypothesis and the evidence that would disconfirm it.
6. Edit an action and download the review draft.
