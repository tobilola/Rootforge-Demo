"""Report safety and export regressions."""

from docx import Document
from io import BytesIO

from rootforge.engine import run_investigation
from rootforge.report import build_report
from rootforge.sources import CASES, by_ref_for, corpus_for, documents_for


def report_text(blob):
    doc = Document(BytesIO(blob))
    return "\n".join(p.text for p in doc.paragraphs)


def test_clean_case_exports():
    entry = CASES["RF-DEMO-001"]
    inv = run_investigation(entry["case"], corpus_for("RF-DEMO-001"),
                            by_ref_for("RF-DEMO-001"))
    blob = build_report(entry["case"], inv, documents_for("RF-DEMO-001"),
                        "Demo Reviewer", "Draft — not reviewed", "")
    assert blob.startswith(b"PK")


def test_flagged_assertion_is_not_confirmed_in_report():
    entry = CASES["RF-DEMO-002"]
    inv = run_investigation(entry["case"], corpus_for("RF-DEMO-002"),
                            by_ref_for("RF-DEMO-002"))
    text = report_text(build_report(entry["case"], inv, documents_for("RF-DEMO-002"),
                                    "", "Draft — not reviewed", ""))
    flagged = "The coordinator back-dated the procedure entry"
    assert flagged in text
    assert "Flagged model assertions — excluded from confirmed findings" in text
    confirmed = text.split("Confirmed by the record", 1)[1].split("Missing from the record", 1)[0]
    assert flagged not in confirmed


def test_non_dict_capa_rows_do_not_crash_export():
    entry = CASES["RF-DEMO-001"]
    inv = run_investigation(entry["case"], corpus_for("RF-DEMO-001"),
                            by_ref_for("RF-DEMO-001"))
    edited = dict(inv["capa"][0], verification="{'status': 'verified'}")
    inv["capa"] = ["type", "text", edited]
    blob = build_report(entry["case"], inv, documents_for("RF-DEMO-001"),
                        "", "Draft — not reviewed", "")
    assert blob.startswith(b"PK")
