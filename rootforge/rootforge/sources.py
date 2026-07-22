"""Synthetic source documents for the Rootforge demonstration case.

IMPORTANT: this module contains ONLY raw source text, exactly as a customer
would supply it. It contains no timeline, no findings, no hypotheses and no
corrective actions. Everything downstream is derived by the engine at runtime
and verified against these strings. If you find yourself tempted to add a
conclusion here, that is the product, not the fixture.

All content is fictional. No patient, employer or confidential research data.
"""

CASE = {
    "id": "RF-DEMO-001",
    "title": "Delayed processing of research blood sample",
    "reported_by": "End-of-day review, Quality function",
    "reported_on": "2026-07-14",
}

# Each document is raw text. `ref` is the citation handle the engine must use.
DOCUMENTS = [
    {
        "ref": "DEV-001",
        "name": "Deviation Report",
        "kind": "incident record",
        "text": (
            "DEVIATION REPORT DEV-001\n"
            "Study: RF-ONC-2026-04. Sample ID: RF-104.\n"
            "Sample RF-104 was collected at 09:05 on 14 July 2026 in Clinic Room 2.\n"
            "Processing began at 10:40 in the on-site processing laboratory.\n"
            "The delay was discovered during end-of-day review of the sample log on "
            "14 July 2026 by the quality function.\n"
            "Reported impact: unknown at time of writing. Sample retained pending "
            "scientific assessment of analyte stability.\n"
            "Collector: Nurse practitioner PJ. Processing technician: LM."
        ),
    },
    {
        "ref": "PRO-7.2",
        "name": "Protocol RF-ONC-2026-04, Section 7.2",
        "kind": "protocol",
        "text": (
            "PROTOCOL RF-ONC-2026-04 — Section 7.2 Sample Handling\n"
            "7.2.1 Whole-blood samples for the biomarker sub-study must begin "
            "processing within 60 minutes of collection.\n"
            "7.2.2 Collection time and processing start time must be recorded in the "
            "sample log at the time of the activity.\n"
            "7.2.3 Any sample processed outside the 60-minute window must be reported "
            "as a protocol deviation and the sample disposition determined by the "
            "principal investigator."
        ),
    },
    {
        "ref": "SOP-014-v3",
        "name": "SOP-014 v3, Sample Receipt and Processing",
        "kind": "SOP",
        "text": (
            "SOP-014 v3 — Sample Receipt and Processing. Effective 1 July 2026. "
            "Supersedes SOP-014 v2.\n"
            "4.1 The receiving technician must record receipt in the sample handoff "
            "log, including printed name or initials, and must begin processing "
            "within 60 minutes of collection.\n"
            "4.2 Where a delay beyond 45 minutes from collection is expected, the "
            "receiving technician must escalate to the study coordinator by telephone "
            "and record the escalation in the sample log.\n"
            "4.3 Change note versus v2: the 45-minute escalation trigger in 4.2 is new "
            "in v3. Version 2 required escalation only after the 60-minute limit had "
            "already been exceeded.\n"
            "6.0 All staff performing sample receipt must complete training on the "
            "current version before performing the activity."
        ),
    },
    {
        "ref": "TR-LM-2026",
        "name": "Training Record, Technician LM",
        "kind": "training record",
        "text": (
            "TRAINING RECORD — Technician LM, Laboratory Operations.\n"
            "SOP-014 v2 — Sample Receipt and Processing. Completed 3 March 2026. "
            "Assessor: Lab manager RK. Status: Complete.\n"
            "SOP-014 v3 — Sample Receipt and Processing. Assigned 2 July 2026. "
            "Status: Assigned. No completion date recorded.\n"
            "GCP Refresher 2026. Completed 12 January 2026. Status: Complete."
        ),
    },
    {
        "ref": "LOG-14JUL-RF104",
        "name": "Sample Handoff Log, 14 July 2026",
        "kind": "log",
        "text": (
            "SAMPLE HANDOFF LOG — 14 July 2026 — Sample RF-104\n"
            "Collection time: 09:05. Collector initials: PJ.\n"
            "Transport to laboratory: field left blank.\n"
            "Receipt time: 10:17. Receiver initials: [blank].\n"
            "Processing start: 10:40. Processed by: LM.\n"
            "Escalation recorded: none.\n"
            "Note appended 14 July 2026 by quality function: receipt entry appears to "
            "have been completed retrospectively; handwriting differs from the "
            "collection entry."
        ),
    },
    {
        "ref": "EMAIL-PJ-14JUL",
        "name": "Email, Nurse Practitioner PJ to Study Coordinator",
        "kind": "correspondence",
        "text": (
            "From: PJ. To: Study coordinator. Sent: 14 July 2026 16:52.\n"
            "Subject: RE: RF-104 timings\n"
            "I drew RF-104 first thing and put it in the transport rack outside room 2 "
            "as usual. Clinic was very busy, we were two staff down. I do not know who "
            "took it across to the lab or when. I did not call anyone about it because "
            "I was not aware there was a delay until you asked me this afternoon."
        ),
    },
]

DOCUMENTS_BY_REF = {d["ref"]: d for d in DOCUMENTS}


def corpus_text() -> str:
    """Render the corpus as the model sees it, with citation handles."""
    blocks = []
    for d in DOCUMENTS:
        blocks.append(
            f"<document ref=\"{d['ref']}\" name=\"{d['name']}\" kind=\"{d['kind']}\">\n"
            f"{d['text']}\n</document>"
        )
    return "\n\n".join(blocks)
