"""Tests that fail when the product is broken, not when python-docx is broken."""

import pytest

from rootforge.engine import run_investigation
from rootforge.sources import CASE, CASES, DOCUMENTS_BY_REF, by_ref_for, corpus_for
from rootforge.verify import verify_claim, verify_investigation


@pytest.fixture(scope="module")
def investigation():
    return run_investigation(CASE)


@pytest.fixture(scope="module")
def catch_case():
    entry = CASES["RF-DEMO-002"]
    return run_investigation(entry["case"], corpus_for("RF-DEMO-002"),
                             by_ref_for("RF-DEMO-002"))


# --- The catch: case 2 must flag the planted fabrication ----------------

def test_catch_case_flags_exactly_one_claim(catch_case):
    """The demo's wow moment must be reproducible: one, and only one, claim
    is caught, and it is the invented back-dating motive."""
    failures = catch_case["verification"]["failures"]
    assert len(failures) == 1, failures
    assert "back-dated" in failures[0]["text"].lower()


def test_catch_case_quarantines_not_deletes(catch_case):
    """The flagged claim must still be present, marked, not silently removed."""
    confirmed = catch_case["findings"]["confirmed"]
    flagged = [c for c in confirmed
               if c["verification"]["status"] in ("unverified", "bad_ref")]
    assert len(flagged) == 1
    assert flagged[0]["quote"]  # the fabricated quote is retained for the reviewer


def test_catch_case_still_grounds_the_real_findings(catch_case):
    """Catching one fabrication must not poison the genuine findings."""
    assert catch_case["verification"]["pass_rate"] > 0.9


# --- Grounding: the core safety property --------------------------------

def test_every_claim_is_grounded(investigation):
    """No claim reaches a reviewer without resolving to source text."""
    assert investigation["verification"]["pass_rate"] == 1.0, (
        investigation["verification"]["failures"]
    )


def test_verifier_rejects_fabricated_quote():
    """The verifier must catch a plausible-sounding invention."""
    claim = {
        "text": "The technician was verbally instructed to delay processing.",
        "refs": ["DEV-001"],
        "quote": "The technician was verbally instructed to delay processing.",
    }
    v = verify_claim(claim, DOCUMENTS_BY_REF)
    assert v.status == "unverified"
    assert not v.ok


def test_verifier_rejects_quote_attributed_to_wrong_document():
    """Real text, wrong source, is still a citation failure."""
    claim = {
        "text": "Processing must begin within 60 minutes.",
        "refs": ["TR-LM-2026"],  # this text lives in PRO-7.2
        "quote": "Whole-blood samples for the biomarker sub-study must begin processing within 60 minutes of collection.",
    }
    assert verify_claim(claim, DOCUMENTS_BY_REF).status == "unverified"


def test_verifier_rejects_unknown_ref():
    claim = {"text": "x", "refs": ["SOP-999"], "quote": "anything"}
    assert verify_claim(claim, DOCUMENTS_BY_REF).status == "bad_ref"


def test_verifier_rejects_uncited_claim():
    claim = {"text": "The delay was caused by understaffing.", "refs": [], "quote": ""}
    assert verify_claim(claim, DOCUMENTS_BY_REF).status == "bad_ref"


def test_failures_are_surfaced_not_dropped():
    """A bad claim must appear in the report, not vanish silently."""
    bad = {
        "timeline": [{"time": "11:00", "text": "invented event",
                      "refs": ["DEV-001"], "quote": "no such text exists here at all"}],
        "findings": {"confirmed": [], "missing": [], "contradictions": []},
        "hypotheses": [], "capa": [],
    }
    result, report = verify_investigation(bad, DOCUMENTS_BY_REF)
    assert report.unverified == 1
    assert len(result["verification"]["failures"]) == 1
    assert result["timeline"][0]["verification"]["status"] == "unverified"


# --- Gold set: does the engine find what a good investigator finds? ------

# Each entry names a finding a competent human investigator produces on this
# case, plus the alternative phrasings that count as having found it. Models
# reword; the finding is what matters. If one disappears, that is a regression.
GOLD = [
    ("missing", ("receiver", "who received", "receipt initials"), "Unidentified receiver at 10:17"),
    ("missing", ("transport", "custody", "chain of custody"), "No transport/custody record"),
    ("confirmed", ("95 minutes", "95-minute", "35 minutes"), "Quantified the breach"),
    ("confirmed", ("escalat",), "No escalation recorded"),
    ("contradictions", ("retrospectiv", "after the fact", "post hoc", "back-dated"),
     "Log entry made after the fact"),
]


@pytest.mark.parametrize("section,needles,label", GOLD)
def test_gold_findings_present(investigation, section, needles, label):
    blob = " ".join(i["text"] for i in investigation["findings"][section]).lower()
    assert any(n.lower() in blob for n in needles), f"Missed: {label}"


def test_training_gap_hypothesis_is_found(investigation):
    """The v2-vs-v3 training inference is the hard one; it requires joining
    three documents. If the engine loses this, the demo loses its punch."""
    blob = " ".join(h["statement"] + h["reasoning"] for h in investigation["hypotheses"]).lower()
    assert "v2" in blob and "train" in blob


def test_hypotheses_are_falsifiable(investigation):
    """Every hypothesis states what would disconfirm it."""
    for h in investigation["hypotheses"]:
        assert h.get("disconfirming_evidence", "").strip(), h["statement"]


def test_no_hypothesis_leaks_into_confirmed(investigation):
    """Confirmed findings must not contain hedging language."""
    hedges = ("likely", "probably", "may have been caused", "appears to suggest")
    for f in investigation["findings"]["confirmed"]:
        low = f["text"].lower()
        assert not any(h in low for h in hedges), f["text"]


def test_capa_traces_to_findings(investigation):
    for action in investigation["capa"]:
        assert action.get("rationale", "").strip()
        assert action.get("refs")
