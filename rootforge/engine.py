"""The investigation engine: raw documents in, structured cited findings out.

Provider-agnostic. Set ANTHROPIC_API_KEY or OPENAI_API_KEY. With neither, the
app runs in `replay` mode against a stored response so the demo is
reproducible offline -- but replay mode is labelled in the UI, because a demo
that silently fakes its own output is the thing we are trying not to build.
"""

from __future__ import annotations

import json
import os
import time

from .sources import DOCUMENTS_BY_REF, corpus_text
from .verify import verify_investigation

SYSTEM = """You are an investigation analyst supporting a regulated clinical-research \
quality function. You reconstruct what happened from source documents.

Absolute rules:
1. Every factual claim MUST cite the `ref` of the document(s) it comes from and \
MUST include a `quote` field containing text copied VERBATIM from that document. \
If you cannot quote it, you may not assert it.
2. Distinguish rigorously between what the record STATES, what the record does \
NOT contain, and what you INFER. These go in different fields. Never move an \
inference into `confirmed`.
3. Absence of evidence is a finding, not a gap to fill. If a required record is \
missing, say so and cite the document where it should have appeared.
4. You do not determine root cause. You propose hypotheses for a qualified human \
to accept, reject or investigate further.
5. Do not invent names, times, or document references not present in the sources.

Return ONLY valid JSON. No markdown fences, no preamble."""

SCHEMA_PROMPT = """Produce JSON with exactly this shape:

{
  "timeline": [
    {"time": "HH:MM", "text": "what happened", "refs": ["DEV-001"],
     "quote": "verbatim span from that document", "confidence": "High|Medium|Low"}
  ],
  "findings": {
    "confirmed":      [{"text": "...", "refs": ["..."], "quote": "..."}],
    "missing":        [{"text": "...", "refs": ["..."], "quote": "..."}],
    "contradictions": [{"text": "...", "refs": ["..."], "quote": "..."}]
  },
  "hypotheses": [
    {"statement": "...", "reasoning": "why the evidence points here",
     "refs": ["..."], "confidence": "High|Medium|Low",
     "disconfirming_evidence": "what would rule this out",
     "status": "Needs investigation|Needs verification"}
  ],
  "capa": [
    {"type": "Correction|Corrective|Preventive", "text": "...",
     "owner_role": "...", "refs": ["..."], "rationale": "which finding this addresses"}
  ]
}

For `missing` items, the quote should be the span showing where the record is
blank or incomplete. Order the timeline chronologically."""

USER_TEMPLATE = """Case {case_id}: {title}

Source documents:

{corpus}

{schema}

Investigate. Return JSON only."""


class EngineError(RuntimeError):
    pass


def _call_anthropic(system: str, user: str, model: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=4000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


def _call_openai(system: str, user: str, model: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content


def _strip_fences(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0]
    return raw.strip()


def provider() -> str:
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return "replay"


REPLAY_DIR = os.path.join(os.path.dirname(__file__), "replay")


def _replay_file(case: dict) -> str:
    """Map a case to its recorded run, defaulting to the id-based filename."""
    from .sources import CASES

    entry = CASES.get(case.get("id"), {})
    name = entry.get("replay") or f"{case.get('id', 'RF-DEMO-001')}.json"
    return os.path.join(REPLAY_DIR, name)


def run_investigation(case: dict, corpus: str | None = None,
                      documents_by_ref: dict | None = None) -> dict:
    """Run the full pipeline: extract -> parse -> verify.

    Returns the verified investigation dict, annotated with per-claim
    verdicts, a verification summary, and run metadata.
    """
    corpus = corpus if corpus is not None else corpus_text()
    docs = documents_by_ref if documents_by_ref is not None else DOCUMENTS_BY_REF
    prov = provider()
    started = time.time()

    if prov == "replay":
        with open(_replay_file(case)) as fh:
            data = json.load(fh)
        model_name = data.pop("_model", "recorded run")
    else:
        user = USER_TEMPLATE.format(
            case_id=case["id"], title=case["title"], corpus=corpus, schema=SCHEMA_PROMPT
        )
        if prov == "anthropic":
            model_name = os.getenv("ROOTFORGE_MODEL", "claude-sonnet-4-6")
            raw = _call_anthropic(SYSTEM, user, model_name)
        else:
            model_name = os.getenv("ROOTFORGE_MODEL", "gpt-4o")
            raw = _call_openai(SYSTEM, user, model_name)
        try:
            data = json.loads(_strip_fences(raw))
        except json.JSONDecodeError as exc:
            raise EngineError(f"Model returned unparseable JSON: {exc}") from exc

    data.setdefault("findings", {})
    for k in ("confirmed", "missing", "contradictions"):
        data["findings"].setdefault(k, [])
    for k in ("timeline", "hypotheses", "capa"):
        data.setdefault(k, [])

    data, _report = verify_investigation(data, docs)
    data["run"] = {
        "provider": prov,
        "model": model_name,
        "seconds": round(time.time() - started, 1),
        "documents": len(docs),
        "replay": prov == "replay",
    }
    return data
