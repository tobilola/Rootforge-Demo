from rootforge.engine import run_investigation
from rootforge.report import build_report
from rootforge.sources import CASES, by_ref_for, corpus_for, documents_for


def test_report_handles_streamlit_edited_rows():
    entry = CASES["RF-DEMO-001"]
    inv = run_investigation(entry["case"], corpus_for("RF-DEMO-001"),
                            by_ref_for("RF-DEMO-001"))
    inv["capa"] = [
        "type",  # Defensive check for the old DataFrame-to-list failure mode.
        {
            "type": "Corrective",
            "text": "Test action",
            "owner": "Quality",
            "refs": "DEV-001",
            "verification": "verified",
        },
    ]

    report = build_report(
        entry["case"], inv, documents_for("RF-DEMO-001"),
        "Reviewer", "Draft — not reviewed", "",
    )

    assert report.startswith(b"PK")
    assert len(report) > 10_000


def test_safety_case_retains_one_flagged_assertion():
    entry = CASES["RF-DEMO-002"]
    inv = run_investigation(entry["case"], corpus_for("RF-DEMO-002"),
                            by_ref_for("RF-DEMO-002"))

    assert len(inv["verification"]["failures"]) == 1
    assert "back-dated" in inv["verification"]["failures"][0]["text"].lower()
