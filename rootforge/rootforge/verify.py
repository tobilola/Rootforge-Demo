"""Grounding verification.

This is the part of Rootforge that is not "call an LLM". A model asked to
investigate will happily assert things no document supports. In a regulated
setting an unsupported assertion inside an investigation record is not a
cosmetic defect -- it is the defect. So nothing reaches the user without
passing here.

Every claim the engine produces carries (a) one or more citation refs and
(b) a `quote`: a span the engine says appears verbatim in that source. We
check both. A claim whose quote cannot be located in the cited document is
demoted to `unverified` and rendered separately, never silently dropped --
suppressing a model's unsupported claim hides a signal the reviewer needs.

Hypotheses are exempt from quote matching (they are by definition not stated
in the record) but must still cite refs that exist, and are always labelled.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field


def _normalise(s: str) -> str:
    """Collapse the differences that don't change meaning."""
    s = unicodedata.normalize("NFKD", s)
    s = s.replace("\u2019", "'").replace("\u2018", "'")
    s = s.replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2013", "-").replace("\u2014", "-")
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def _token_recall(quote: str, source: str) -> float:
    """Fraction of the quote's content tokens present in the source.

    Used as a near-miss score so we can distinguish "model paraphrased
    slightly" from "model invented this". Only the former is recoverable.
    """
    q = set(re.findall(r"[a-z0-9]+", _normalise(quote)))
    if not q:
        return 0.0
    s = set(re.findall(r"[a-z0-9]+", _normalise(source)))
    return len(q & s) / len(q)


@dataclass
class Verdict:
    status: str  # "verified" | "paraphrase" | "unverified" | "bad_ref"
    detail: str
    score: float = 0.0

    @property
    def ok(self) -> bool:
        return self.status in ("verified", "paraphrase")


@dataclass
class VerificationReport:
    total: int = 0
    verified: int = 0
    paraphrase: int = 0
    unverified: int = 0
    bad_ref: int = 0
    failures: list = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        return (self.verified + self.paraphrase) / self.total if self.total else 0.0

    def summary(self) -> str:
        return (
            f"{self.verified + self.paraphrase}/{self.total} claims grounded "
            f"({self.verified} exact, {self.paraphrase} near-match, "
            f"{self.unverified} unsupported, {self.bad_ref} bad citation)"
        )


# A near-match at or above this recall is treated as an acceptable paraphrase
# of real source text rather than an invention. Tuned on the eval set in
# tests/test_engine.py; raise it if you start seeing plausible-sounding
# fabrications slip through.
PARAPHRASE_THRESHOLD = 0.80


def verify_claim(claim: dict, documents_by_ref: dict) -> Verdict:
    """Check one claim against the source corpus."""
    refs = [r.strip() for r in claim.get("refs", []) if r and r.strip()]
    if not refs:
        return Verdict("bad_ref", "Claim carries no citation.")

    unknown = [r for r in refs if r not in documents_by_ref]
    if unknown:
        return Verdict("bad_ref", f"Cites unknown source(s): {', '.join(unknown)}")

    quote = (claim.get("quote") or "").strip()
    if not quote:
        return Verdict("unverified", "Claim carries no supporting quote.")

    haystack = "\n".join(documents_by_ref[r]["text"] for r in refs)

    if _normalise(quote) in _normalise(haystack):
        return Verdict("verified", f"Exact span found in {', '.join(refs)}.", 1.0)

    score = _token_recall(quote, haystack)
    if score >= PARAPHRASE_THRESHOLD:
        return Verdict(
            "paraphrase",
            f"Close match in {', '.join(refs)} (recall {score:.0%}).",
            score,
        )
    return Verdict(
        "unverified",
        f"Quoted span not found in {', '.join(refs)} (recall {score:.0%}).",
        score,
    )


def verify_investigation(investigation: dict, documents_by_ref: dict) -> tuple[dict, VerificationReport]:
    """Annotate every claim in an investigation with a verdict.

    Returns the annotated investigation and an aggregate report. The
    investigation is mutated in place as well as returned, for convenience.
    """
    report = VerificationReport()

    def _check(items, exempt_quote=False):
        for item in items:
            if exempt_quote and not (item.get("quote") or "").strip():
                # Hypotheses need a valid ref but need not quote the record.
                refs = [r for r in item.get("refs", []) if r]
                if not refs:
                    v = Verdict("bad_ref", "Hypothesis carries no citation.")
                elif any(r not in documents_by_ref for r in refs):
                    v = Verdict("bad_ref", "Hypothesis cites an unknown source.")
                else:
                    v = Verdict("paraphrase", "Inference; refs valid, not quoted.", 1.0)
            else:
                v = verify_claim(item, documents_by_ref)
            item["verification"] = {"status": v.status, "detail": v.detail, "score": v.score}
            report.total += 1
            setattr(report, v.status, getattr(report, v.status) + 1)
            if not v.ok:
                report.failures.append({"text": item.get("text") or item.get("statement", ""), "detail": v.detail})

    _check(investigation.get("timeline", []))
    for key in ("confirmed", "missing", "contradictions"):
        _check(investigation.get("findings", {}).get(key, []))
    _check(investigation.get("hypotheses", []), exempt_quote=True)
    _check(investigation.get("capa", []), exempt_quote=True)

    investigation["verification"] = {
        "summary": report.summary(),
        "pass_rate": report.pass_rate,
        "failures": report.failures,
    }
    return investigation, report
