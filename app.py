from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from rootforge.engine import EngineError, run_investigation
from rootforge.report import build_report
from rootforge.sources import CASE, DOCUMENTS

st.set_page_config(page_title="Rootforge", page_icon="🔎", layout="wide")
st.markdown(
    """
    <style>
      .block-container {max-width: 1120px; padding-top: 2rem;}
      .rf-kicker {color:#176B5B; font-weight:700; letter-spacing:.08em; font-size:.8rem;}
      .rf-note {background:#f2f8f6; border-left:4px solid #176B5B; padding:.8rem 1rem; border-radius:6px;}
    </style>
    """,
    unsafe_allow_html=True,
)


def source_line(item):
    verification = item.get("verification", {})
    status = verification.get("status", "unverified")
    label = {
        "verified": "Source text verified",
        "paraphrase": "Source match found",
        "unverified": "Needs source confirmation",
        "bad_ref": "Citation needs correction",
    }.get(status, "Needs review")
    refs = "; ".join(item.get("refs", [])) or "No source"
    return f"{label} · {refs}"


def evidence_item(item, prefix=""):
    st.markdown(f"{prefix}{item.get('text', '')}")
    st.caption(source_line(item))
    quote = item.get("quote")
    if quote:
        st.code(quote, language=None)


st.markdown('<div class="rf-kicker">ROOTFORGE · PROTOCOL DEVIATION REVIEW</div>', unsafe_allow_html=True)
st.title("Turn scattered evidence into a review-ready investigation draft")
st.write(
    "Rootforge reconstructs a cited timeline, surfaces missing or conflicting "
    "information, and proposes root-cause hypotheses and actions for qualified human review."
)
st.markdown(
    '<div class="rf-note"><strong>Synthetic demonstration:</strong> every person, study, '
    'sample, and document in this case is fictional. No patient or employer data is used.</div>',
    unsafe_allow_html=True,
)

overview, evidence, timeline, findings, review = st.tabs(
    ["Case", "Evidence", "Timeline", "Findings", "Actions & export"]
)

with overview:
    st.subheader(CASE["title"])
    st.caption(f'{CASE["id"]} · Reported {CASE["reported_on"]}')
    st.write(
        "A research blood sample was processed outside the protocol window. The evidence "
        "is spread across a deviation report, protocol, SOP, training record, handoff log, "
        "and follow-up email."
    )
    st.write("Run the prepared case to see how Rootforge assembles and checks the record.")
    if st.button("Run synthetic investigation", type="primary", use_container_width=True):
        with st.spinner("Reconstructing and checking the evidence..."):
            try:
                st.session_state["investigation"] = run_investigation(CASE)
            except EngineError as exc:
                st.error(f"The investigation could not run: {exc}")

    inv = st.session_state.get("investigation")
    if inv:
        c1, c2, c3 = st.columns(3)
        c1.metric("Evidence sources", inv["run"]["documents"])
        c2.metric("Timeline events", len(inv["timeline"]))
        c3.metric("Open questions", len(inv["findings"]["missing"]))
        if inv["run"].get("replay"):
            st.info(
                "Demo mode is showing a previously generated response for this fixed synthetic case. "
                "Rootforge is checking its citations against the source documents now."
            )
        else:
            st.success("Live analysis complete. Citations were checked against the source documents.")
        if inv["verification"].get("failures"):
            st.warning("Some statements need source confirmation and are visibly flagged for review.")

with evidence:
    st.subheader("Source documents")
    st.write("Open any record to inspect the exact fictional source text used in this demonstration.")
    for document in DOCUMENTS:
        with st.expander(f'{document["name"]} · {document["ref"]}'):
            st.text(document["text"])

inv = st.session_state.get("investigation")

with timeline:
    if not inv:
        st.info("Run the synthetic investigation from the Case tab first.")
    else:
        st.subheader("Evidence-linked timeline")
        for event in inv["timeline"]:
            evidence_item(event, f'**{event.get("time", "")}** — ')

with findings:
    if not inv:
        st.info("Run the synthetic investigation from the Case tab first.")
    else:
        for heading, key in (
            ("Confirmed by the record", "confirmed"),
            ("Missing from the record", "missing"),
            ("Contradictions and doubts", "contradictions"),
        ):
            st.subheader(heading)
            for item in inv["findings"][key]:
                evidence_item(item, "- ")

        st.subheader("Root-cause hypotheses")
        st.caption("These are proposed lines of inquiry—not conclusions. A qualified reviewer must evaluate them.")
        for index, hypothesis in enumerate(inv["hypotheses"], 1):
            with st.expander(f'H{index}: {hypothesis.get("statement", "")}'):
                st.write(f'**Why investigate it:** {hypothesis.get("reasoning", "")}')
                st.write(f'**Evidence that would rule it out:** {hypothesis.get("disconfirming_evidence", "")}')
                st.caption(f'Sources: {"; ".join(hypothesis.get("refs", []))}')

with review:
    if not inv:
        st.info("Run the synthetic investigation from the Case tab first.")
    else:
        st.subheader("Draft corrective and preventive actions")
        edited_actions = st.data_editor(
            inv["capa"], use_container_width=True, num_rows="dynamic", key="capa_editor"
        )
        try:
            edited_actions = edited_actions.to_dict("records")
        except AttributeError:
            edited_actions = list(edited_actions)

        st.subheader("Reviewer notes")
        reviewer = st.text_input("Reviewer name (optional)")
        decision = st.selectbox(
            "Review status",
            ["Not reviewed", "More information required", "Ready for qualified review"],
        )
        notes = st.text_area("Notes", placeholder="Questions, rejected hypotheses, or required follow-up")
        output = dict(inv, capa=edited_actions)
        st.download_button(
            "Download review draft (.docx)",
            build_report(CASE, output, DOCUMENTS, reviewer, decision, notes),
            file_name=f'Rootforge_{CASE["id"]}_Review_Draft.docx',
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            type="primary",
            use_container_width=True,
        )
        st.caption("This export is an AI-assisted draft, not a regulatory decision or root-cause determination.")
