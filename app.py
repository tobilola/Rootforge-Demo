import streamlit as st

from rootforge.engine import EngineError, provider, run_investigation
from rootforge.ingest import corpus_from, load_uploads
from rootforge.report import build_report
from rootforge.sources import CASES, corpus_for, by_ref_for, documents_for

st.set_page_config(page_title="Rootforge", page_icon="◆", layout="wide",
                   initial_sidebar_state="collapsed")

# ---------------------------------------------------------------------------
# Design system. Instrument-panel aesthetic: deep ink, signal green for
# verified, clear red for caught. Monospace utility face for evidence (refs
# and quotes read like terminal output, because that is what they are: the
# machine showing its work). Everything derives from these tokens.
# ---------------------------------------------------------------------------
st.html("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&family=Inter:wght@400;450;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --ink:#0B1F2A; --ink-2:#12303D; --paper:#F7F9F8; --line:#DDE6E3;
  --mut:#5E7169; --sig:#0E8A6A; --sig-bg:#E6F5EF; --sig-line:#9FDCC7;
  --warn:#B23A2E; --warn-bg:#FBEDEB; --warn-line:#E6B3AC;
  --amber:#B7791F; --amber-bg:#FBF3E4; --amber-line:#E7D3A3;
  --blue:#215C9B; --blue-bg:#EAF2FB; --blue-line:#B9D3ED;
}
html, body, [class*="css"]{ font-family:'Inter',system-ui,sans-serif; }
.stApp{ background:
  radial-gradient(1200px 400px at 80% -10%, #EAF3EF 0%, transparent 60%),
  var(--paper); color:var(--ink); }
.block-container{ max-width:1120px; padding-top:1.4rem; }
#MainMenu, footer, header{ visibility:hidden; }

/* Masthead */
.rf-top{ display:flex; align-items:center; gap:.7rem; margin-bottom:.2rem; }
.rf-mark{ width:26px; height:26px; border-radius:6px; background:var(--ink);
  position:relative; box-shadow:0 2px 8px rgba(11,31,42,.25); }
.rf-mark:after{ content:""; position:absolute; inset:7px; border:2px solid var(--sig);
  border-radius:2px; transform:rotate(45deg); }
.rf-word{ font-family:'Space Grotesk'; font-weight:700; letter-spacing:-.02em;
  font-size:1.15rem; color:var(--ink); }
.rf-ey{ font-family:'IBM Plex Mono'; text-transform:uppercase; letter-spacing:.22em;
  font-size:.62rem; color:var(--mut); font-weight:500; }
.rf-h1{ font-family:'Space Grotesk'; font-weight:700; font-size:2.05rem;
  line-height:1.08; letter-spacing:-.025em; margin:.5rem 0 .1rem; color:var(--ink); }
.rf-sub{ color:var(--mut); font-size:.95rem; }
.rf-caseid{ font-family:'IBM Plex Mono'; font-size:.72rem; color:var(--sig);
  font-weight:600; letter-spacing:.04em; }

/* Verdict chip: the signature element */
.chip{ display:inline-flex; align-items:center; gap:.4rem; font-family:'IBM Plex Mono';
  font-size:.66rem; font-weight:600; padding:.16rem .5rem; border-radius:999px;
  letter-spacing:.03em; text-transform:uppercase; white-space:nowrap; }
.chip.ok{ background:var(--sig-bg); color:var(--sig); border:1px solid var(--sig-line); }
.chip.near{ background:#EAF2FB; color:#215C9B; border:1px solid #B9D3ED; }
.chip.bad{ background:var(--warn-bg); color:var(--warn); border:1px solid var(--warn-line); }
.dot{ width:6px; height:6px; border-radius:50%; background:currentColor; }

/* Claim card */
.claim{ border:1px solid var(--line); border-left:3px solid var(--sig);
  border-radius:12px; padding:.85rem 1rem; background:#fff; margin-bottom:.55rem;
  box-shadow:0 1px 2px rgba(11,31,42,.04); }
.claim.flag{ border-left-color:var(--warn); background:var(--warn-bg); }
.claim.missing{ border-left-color:var(--amber); background:var(--amber-bg); }
.claim.contradiction{ border-left-color:var(--warn); }
.claim.hypothesis{ border-left-color:var(--blue); background:var(--blue-bg); }
.claim-top{ display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; }
.claim-txt{ font-size:.96rem; line-height:1.5; color:var(--ink); }
.claim-txt b{ font-family:'IBM Plex Mono'; font-weight:600; color:var(--ink-2); }
.meta{ margin-top:.5rem; font-family:'IBM Plex Mono'; font-size:.72rem; color:var(--mut); }
.ref{ color:var(--sig); font-weight:600; }
.quote{ margin-top:.5rem; padding:.45rem .7rem; border-left:2px solid var(--line);
  background:var(--paper); border-radius:0 6px 6px 0; font-size:.83rem;
  color:#40514B; font-style:italic; }
.flag .quote{ border-left-color:var(--warn-line); }
.detail{ margin-top:.4rem; font-family:'IBM Plex Mono'; font-size:.7rem; }
.detail.bad{ color:var(--warn); font-weight:500; }
.rf-footer{ margin-top:1.5rem; padding:1rem 0 .25rem; border-top:1px solid var(--line);
  font-family:'IBM Plex Mono'; font-size:.68rem; color:var(--mut); text-align:center; }

/* Section headers */
.sec{ font-family:'Space Grotesk'; font-weight:600; font-size:1.05rem;
  color:var(--ink); margin:.2rem 0 .1rem; display:flex; align-items:baseline; gap:.55rem; }
.sec .n{ font-family:'IBM Plex Mono'; font-size:.72rem; color:var(--sig); font-weight:600; }
.sec-note{ color:var(--mut); font-size:.82rem; margin-bottom:.7rem; }

/* Stat rail */
.rail{ display:grid; grid-template-columns:repeat(4,1fr); gap:.6rem; margin:.2rem 0 .4rem; }
.stat{ border:1px solid var(--line); border-radius:12px; padding:.75rem .9rem; background:#fff; }
.stat .v{ font-family:'Space Grotesk'; font-weight:700; font-size:1.5rem; color:var(--ink); line-height:1; }
.stat .v.good{ color:var(--sig); } .stat .v.warn{ color:var(--warn); }
.stat .k{ font-family:'IBM Plex Mono'; font-size:.62rem; text-transform:uppercase;
  letter-spacing:.1em; color:var(--mut); margin-top:.35rem; }

/* Banner */
.banner{ border-radius:12px; padding:.7rem .95rem; font-size:.85rem; margin:.3rem 0 .6rem;
  display:flex; gap:.6rem; align-items:center; }
.banner.live{ background:var(--sig-bg); border:1px solid var(--sig-line); color:#0A5C47; }
.banner.replay{ background:var(--amber-bg); border:1px solid #E7D3A3; color:#7A5312; }
.banner code{ font-family:'IBM Plex Mono'; font-size:.78rem; }
.result{ font-family:'IBM Plex Mono'; font-size:.82rem; color:var(--ink-2);
  background:#fff; border:1px solid var(--line); border-radius:10px;
  padding:.6rem .8rem; margin:.3rem 0; }
.result b{ color:var(--sig); }

/* Buttons */
.stButton>button, .stDownloadButton>button{
  font-family:'Space Grotesk'!important; font-weight:600!important; letter-spacing:-.01em;
  border-radius:10px!important; border:1px solid var(--ink)!important;
  background:var(--ink)!important; color:#fff!important; box-shadow:0 2px 10px rgba(11,31,42,.18)!important; }
.stButton>button:hover, .stDownloadButton>button:hover{ background:var(--ink-2)!important; }
.stTabs [data-baseweb="tab-list"]{ gap:.3rem; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"]{ font-family:'IBM Plex Mono'; font-size:.78rem;
  letter-spacing:.04em; text-transform:uppercase; color:var(--mut); }
.stTabs [aria-selected="true"]{ color:var(--ink)!important; }
[data-testid="stExpander"]{ border:1px solid var(--line); border-radius:10px; background:#fff; }
hr{ border:none; border-top:1px solid var(--line); margin:1rem 0; }
</style>
""")

CHIP = {
    "verified": ('<span class="chip ok"><span class="dot"></span>Verified</span>'),
    "paraphrase": ('<span class="chip near"><span class="dot"></span>Source match</span>'),
    "unverified": ('<span class="chip bad"><span class="dot"></span>Not grounded</span>'),
    "bad_ref": ('<span class="chip bad"><span class="dot"></span>Bad citation</span>'),
}


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def claim_card(lead, item, category="confirmed"):
    v = item.get("verification", {})
    status = v.get("status", "")
    flag = status in ("unverified", "bad_ref")
    refs = "; ".join(item.get("refs", [])) or "uncited"
    quote = item.get("quote", "")
    detail = v.get("detail", "")
    category_class = {
        "missing": "missing", "contradictions": "contradiction",
        "hypothesis": "hypothesis",
    }.get(category, "")
    html = f'<div class="claim {"flag" if flag else category_class}">'
    html += '<div class="claim-top">'
    html += f'<div class="claim-txt">{lead}</div>{CHIP.get(status, "")}</div>'
    html += f'<div class="meta"><span class="ref">{esc(refs)}</span></div>'
    if quote:
        html += f'<div class="quote">&ldquo;{esc(quote)}&rdquo;</div>'
    if flag:
        html += (f'<div class="detail bad">✕ {esc(detail)} · excluded from confirmed '
                 'findings and retained for reviewer inspection</div>')
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# --- Masthead --------------------------------------------------------------
st.markdown(
    '<div class="rf-top"><div class="rf-mark"></div>'
    '<div class="rf-word">Rootforge</div>'
    '<div class="rf-ey">&nbsp;· Investigation workspace</div></div>',
    unsafe_allow_html=True,
)

# --- Case selector ---------------------------------------------------------
case_ids = list(CASES.keys())
labels = {cid: f"{cid} · {CASES[cid]['case']['title']}" for cid in case_ids}
chosen = st.radio("Case", case_ids, format_func=lambda c: labels[c],
                  horizontal=True, label_visibility="collapsed")
entry = CASES[chosen]
CASE = entry["case"]

st.markdown(f'<div class="rf-h1">{esc(CASE["title"])}</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="rf-sub"><span class="rf-caseid">{CASE["id"]}</span> &nbsp;·&nbsp; '
    f'{esc(entry["blurb"])}</div>', unsafe_allow_html=True)

prov = provider()
if prov == "replay":
    st.markdown(
        '<div class="banner replay">◆ <div><b>Replay mode.</b> No API key set, so a '
        'recorded run is being replayed for offline reliability. Grounding '
        'verification runs live against source text either way. Set '
        '<code>ANTHROPIC_API_KEY</code> to generate fresh.</div></div>',
        unsafe_allow_html=True)
else:
    st.markdown(
        f'<div class="banner live">◆ <div><b>Live · {esc(prov)}.</b> Every claim below '
        'is checked against source text before you see it.</div></div>',
        unsafe_allow_html=True)

setup, evidence, timeline_tab, findings_tab, review = st.tabs(
    ["Run", "Evidence", "Timeline", "Findings", "Report"]
)

with setup:
    uploads = st.file_uploader(
        "Add your own documents, or run the built-in synthetic case",
        accept_multiple_files=True, type=["pdf", "docx", "txt", "md"])
    docs = load_uploads(uploads) if uploads else documents_for(chosen)
    corpus = corpus_from(docs) if uploads else corpus_for(chosen)
    refs = ", ".join(d["ref"] for d in docs)
    st.markdown(f'<div class="meta">{len(docs)} document(s) staged &nbsp;·&nbsp; '
                f'<span class="ref">{esc(refs)}</span></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown(
        "In live mode, the documents are sent to the model as raw text. In replay "
        "mode, this demonstration replays a recorded model response. The model "
        "response contains a timeline, findings and hypotheses, each "
        "carrying a citation and a verbatim quote. Every quote is then checked "
        "live against the displayed source documents. Anything that fails is excluded "
        "from confirmed findings and retained for reviewer inspection.")

    if st.button("Run investigation", width="stretch"):
        with st.spinner("Reading evidence · reconstructing · verifying"):
            try:
                st.session_state["inv"] = run_investigation(
                    CASE, corpus, {d["ref"]: d for d in docs})
                st.session_state["docs"] = docs
                st.session_state["for"] = chosen
            except EngineError as exc:
                st.error(f"Engine failed: {exc}")

    inv = st.session_state.get("inv") if st.session_state.get("for") == chosen else None
    if inv:
        run, ver = inv["run"], inv["verification"]
        caught = len(ver["failures"])
        rate = f"{ver['pass_rate']:.0%}"
        st.markdown(
            f'<div class="rail">'
            f'<div class="stat"><div class="v">{run["documents"]}</div><div class="k">Documents read</div></div>'
            f'<div class="stat"><div class="v">{len(inv["timeline"])}</div><div class="k">Timeline events</div></div>'
            f'<div class="stat"><div class="v {"good" if not caught else "warn"}">{rate}</div><div class="k">Claims grounded</div></div>'
            f'<div class="stat"><div class="v {"warn" if caught else "good"}">{caught}</div><div class="k">Flagged assertions</div></div>'
            f'</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result">{esc(ver["summary"])} &nbsp;·&nbsp; '
                    f'{run["seconds"]}s &nbsp;·&nbsp; <b>{esc(run["model"])}</b></div>',
                    unsafe_allow_html=True)
        if caught:
            st.markdown(
                f'<div class="banner replay">✕ <div><b>{caught} assertion flagged.</b> '
                'The model asserted something the documents do not support. It is '
                'excluded from confirmed findings and retained below and in the report '
                'for reviewer inspection.</div></div>', unsafe_allow_html=True)
        st.success("Investigation complete. Continue with the Timeline, Findings, and Report tabs above.")

with evidence:
    for d in st.session_state.get("docs", documents_for(chosen)):
        with st.expander(f"{d['name']}  ·  {d['ref']}"):
            st.text(d["text"])

inv = st.session_state.get("inv") if st.session_state.get("for") == chosen else None

with timeline_tab:
    if not inv:
        st.info("Run the investigation to reconstruct the timeline.")
    else:
        st.markdown('<div class="sec"><span class="n">01</span>Reconstructed timeline</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="sec-note">Each event resolves to a source span.</div>',
                    unsafe_allow_html=True)
        for e in inv["timeline"]:
            claim_card(f'<b>{esc(e.get("time",""))}</b>&nbsp;&nbsp;{esc(e.get("text",""))} '
                       f'<span style="color:var(--mut);font-size:.8rem">'
                       f'({esc(e.get("confidence","?"))})</span>', e)

with findings_tab:
    if not inv:
        st.info("Run the investigation to see findings.")
    else:
        blocks = [
            ("02", "Confirmed by the record", "Stated in the documents.", "confirmed"),
            ("03", "Missing from the record", "Should be present and is not.", "missing"),
            ("04", "Contradictions", "The record disagrees with itself.", "contradictions"),
        ]
        for n, title, note, key in blocks:
            st.markdown(f'<div class="sec"><span class="n">{n}</span>{title}</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="sec-note">{note}</div>', unsafe_allow_html=True)
            items = inv["findings"][key]
            if not items:
                st.markdown('<div class="meta">None identified.</div>', unsafe_allow_html=True)
            for item in items:
                status = item.get("verification", {}).get("status", "")
                if status in ("verified", "paraphrase"):
                    claim_card(esc(item.get("text", "")), item, key)

        flagged = [
            item for section in inv["findings"].values() for item in section
            if item.get("verification", {}).get("status") in ("unverified", "bad_ref")
        ]
        if flagged:
            st.markdown('<div class="sec"><span class="n">!</span>Flagged model assertions</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="sec-note">Excluded from confirmed findings and retained for reviewer inspection.</div>',
                        unsafe_allow_html=True)
            for item in flagged:
                claim_card(esc(item.get("text", "")), item)

        st.markdown('<div class="sec"><span class="n">05</span>Root-cause hypotheses</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="sec-note">Proposed lines of enquiry. None established. '
                    'Each states what would disconfirm it.</div>', unsafe_allow_html=True)
        for i, h in enumerate(inv["hypotheses"], 1):
            with st.expander(f"H{i} · {h.get('statement','')}  ·  {h.get('confidence','?')}"):
                st.markdown(f"**Reasoning.** {h.get('reasoning','')}")
                st.markdown(f"**Would be disconfirmed by.** {h.get('disconfirming_evidence','')}")
                st.markdown(f'<div class="meta"><span class="ref">'
                            f'{esc("; ".join(h.get("refs", [])))}</span> · '
                            f'{esc(h.get("status",""))}</div>', unsafe_allow_html=True)

with review:
    if not inv:
        st.info("Run the investigation to draft actions and export.")
    else:
        st.markdown('<div class="sec"><span class="n">06</span>Draft corrective &amp; preventive actions</div>',
                    unsafe_allow_html=True)
        edited = st.data_editor(inv["capa"], width="stretch",
                                num_rows="dynamic", key="capa_editor")
        if hasattr(edited, "to_dict"):
            edited = edited.to_dict(orient="records")
        elif isinstance(edited, list):
            edited = [row for row in edited if isinstance(row, dict)]
        else:
            edited = inv["capa"]

        st.markdown('<div class="sec"><span class="n">07</span>Qualified human review</div>',
                    unsafe_allow_html=True)
        reviewer = st.text_input("Reviewer name")
        decision = st.selectbox("Decision", ["Draft — not reviewed",
                                             "Return for more information",
                                             "Approve investigation draft"])
        notes = st.text_area("Review notes",
                             placeholder="Rationale, required follow-up, rejected hypotheses.")

        out = dict(inv, capa=edited)
        st.download_button(
            "Download investigation report (.docx)",
            build_report(CASE, out, st.session_state.get("docs", documents_for(chosen)),
                         reviewer, decision, notes),
            file_name=f"Rootforge_{CASE['id']}_Investigation_Draft.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            width="stretch")

st.markdown(
    '<div class="rf-footer">Rootforge · Human-reviewed investigation support · Synthetic demonstration</div>',
    unsafe_allow_html=True,
)
