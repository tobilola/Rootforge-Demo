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

# ---------------------------------------------------------------------------
# Second case. Same shape, different failure. This one exists to demonstrate
# the verifier CATCHING an over-reach: on this evidence a model is tempted to
# assert *why* the consent was mis-dated ("the coordinator back-dated it to
# stay within the window"), which no document supports. The recorded run does
# exactly that, and verify.py flags it red. Nothing here states a motive; the
# documents support only that the dates disagree.
# ---------------------------------------------------------------------------

CASE_2 = {
    "id": "RF-DEMO-002",
    "title": "Consent form dated after the first study procedure",
    "reported_by": "Monitoring visit, Sponsor CRA",
    "reported_on": "2026-07-18",
}

DOCUMENTS_2 = [
    {
        "ref": "MON-002",
        "name": "Monitoring Visit Finding",
        "kind": "incident record",
        "text": (
            "MONITORING FINDING MON-002. Study RF-CARD-2026-02, Subject 019.\n"
            "During source data verification the CRA found the informed consent "
            "form for Subject 019 is dated 16 July 2026. The first study-specific "
            "procedure, a fasting blood draw, is recorded as performed on "
            "15 July 2026. A study procedure appears to precede documented consent "
            "by one day. Raised as a potential ICH-GCP consent deviation."
        ),
    },
    {
        "ref": "ICF-019",
        "name": "Informed Consent Form, Subject 019",
        "kind": "consent record",
        "text": (
            "INFORMED CONSENT FORM. Study RF-CARD-2026-02. Subject 019.\n"
            "Subject signature present. Subject date field: 16 July 2026.\n"
            "Person obtaining consent: Study Coordinator DR. Coordinator signature "
            "present. Coordinator date field: 16 July 2026.\n"
            "Version: Main ICF v4.0. No witness section completed."
        ),
    },
    {
        "ref": "PROC-019",
        "name": "Procedure Log, Subject 019",
        "kind": "log",
        "text": (
            "PROCEDURE LOG. Subject 019.\n"
            "15 July 2026, 08:10. Fasting blood draw performed. Phlebotomist: MT.\n"
            "16 July 2026, 09:30. Baseline ECG performed. Technician: SH.\n"
            "Note: the 15 July entry has an asterisk; no legend for the asterisk "
            "is present on this page."
        ),
    },
    {
        "ref": "EMAIL-DR-18JUL",
        "name": "Email, Coordinator DR to Principal Investigator",
        "kind": "correspondence",
        "text": (
            "From: DR. To: PI. Sent: 18 July 2026 11:04.\n"
            "Subject: RE: Subject 019 consent query\n"
            "I remember consenting Subject 019 and I am sure we talked through the "
            "form before anything was done. I filled in the dates when I completed "
            "the file. I cannot say from memory what date I wrote against the "
            "signatures. I have not compared the form to the procedure log."
        ),
    },
    {
        "ref": "DELEG-CARD02",
        "name": "Delegation Log Extract",
        "kind": "log",
        "text": (
            "DELEGATION LOG, Study RF-CARD-2026-02.\n"
            "Coordinator DR: authorised to obtain informed consent from 1 June 2026. "
            "Phlebotomist MT: authorised for sample collection from 1 June 2026.\n"
            "No entry delegates consent to any other staff member."
        ),
    },
]


def _by_ref(docs):
    return {d["ref"]: d for d in docs}


def _corpus(docs):
    return "\n\n".join(
        f"<document ref=\"{d['ref']}\" name=\"{d['name']}\" kind=\"{d['kind']}\">\n"
        f"{d['text']}\n</document>"
        for d in docs
    )


# Registry: everything the app and engine need, keyed by case id.
CASES = {
    CASE["id"]: {
        "case": CASE,
        "documents": DOCUMENTS,
        "replay": "RF-DEMO-001.json",
        "blurb": "The clean run. 28 of 28 claims ground, 18 by exact match.",
    },
    CASE_2["id"]: {
        "case": CASE_2,
        "documents": DOCUMENTS_2,
        "replay": "RF-DEMO-002.json",
        "blurb": "The catch. The model asserts a motive the record never states, "
                 "and the verifier flags it before a reviewer sees it.",
    },
}

DOCUMENTS_BY_REF = _by_ref(DOCUMENTS)


def documents_for(case_id: str):
    return CASES[case_id]["documents"]


def by_ref_for(case_id: str):
    return _by_ref(CASES[case_id]["documents"])


def corpus_for(case_id: str) -> str:
    return _corpus(CASES[case_id]["documents"])


def corpus_text() -> str:
    """Backwards-compatible: corpus for the default (first) case."""
    return _corpus(DOCUMENTS)
