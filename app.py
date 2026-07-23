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
.hero{ display:grid; grid-template-columns:minmax(0,1.45fr) minmax(280px,.75fr); gap:1rem;
  margin:.7rem 0 1rem; align-items:stretch; }
.hero-copy{ background:var(--ink); color:#fff; border-radius:18px; padding:1.45rem 1.55rem;
  box-shadow:0 18px 40px rgba(11,31,42,.14); }
.hero-kicker{ font-family:'IBM Plex Mono'; color:#8FE0C5; text-transform:uppercase;
  letter-spacing:.14em; font-size:.65rem; font-weight:600; }
.hero h1{ font-family:'Space Grotesk'; font-size:2.15rem; line-height:1.03;
  letter-spacing:-.035em; margin:.55rem 0 .65rem; color:#fff; }
.hero p{ color:#C9D8D3; margin:0; line-height:1.55; max-width:700px; }
.promise{ background:#fff; border:1px solid var(--line); border-radius:18px; padding:1.15rem;
  box-shadow:0 8px 24px rgba(11,31,42,.06); }
.promise-label{ font-family:'IBM Plex Mono'; font-size:.62rem; color:var(--mut);
  text-transform:uppercase; letter-spacing:.12em; }
.promise-item{ display:flex; gap:.65rem; padding:.7rem 0; border-bottom:1px solid var(--line);
  font-size:.86rem; color:var(--ink-2); line-height:1.35; }
.promise-item:last-child{ border-bottom:0; padding-bottom:0; }
.check{ color:var(--sig); font-weight:800; }
.story{ display:grid; grid-template-columns:repeat(3,1fr); gap:.65rem; margin:.65rem 0 1rem; }
.story-card{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:1rem; }
.story-card b{ display:block; font-family:'Space Grotesk'; font-size:.95rem; margin:.25rem 0; }
.story-card span{ color:var(--mut); font-size:.8rem; line-height:1.4; }
.step{ font-family:'IBM Plex Mono'; color:var(--sig); font-size:.63rem; letter-spacing:.1em; }
.reveal{ border:1px solid var(--sig-line); background:linear-gradient(135deg,#F1FBF7,#fff);
  border-radius:16px; padding:1.15rem 1.25rem; margin:.8rem 0; }
.reveal-label{ font-family:'IBM Plex Mono'; color:var(--sig); text-transform:uppercase;
  letter-spacing:.1em; font-size:.64rem; font-weight:600; }
.reveal h2{ font-family:'Space Grotesk'; font-size:1.28rem; line-height:1.25;
  margin:.35rem 0; color:var(--ink); }
.reveal p{ color:var(--mut); margin:.2rem 0 0; font-size:.88rem; }
.repair-grid{ display:grid; grid-template-columns:repeat(3,1fr); gap:.65rem; margin:.6rem 0 1rem; }
.repair{ background:#fff; border:1px solid var(--line); border-top:3px solid var(--blue);
  border-radius:12px; padding:.85rem; }
.repair b{ font-family:'Space Grotesk'; display:block; font-size:.88rem; margin-bottom:.3rem; }
.repair span{ color:var(--mut); font-size:.78rem; line-height:1.4; }
.safety{ border:1px solid var(--warn-line); background:var(--warn-bg); border-radius:16px;
  padding:1.1rem 1.2rem; margin:.8rem 0; }
.safety h2{ font-family:'Space Grotesk'; margin:.25rem 0; font-size:1.2rem; color:var(--warn); }
.safety p{ margin:.2rem 0; color:#74443D; font-size:.86rem; }
.proof{ border:1px solid var(--line); background:#fff; border-radius:16px; padding:1rem;
  margin:.7rem 0 1rem; box-shadow:0 8px 24px rgba(11,31,42,.05); }
.proof-grid{ display:grid; grid-template-columns:repeat(4,1fr); gap:.55rem; }
.proof-node{ position:relative; border:1px solid var(--line); border-radius:12px;
  padding:.8rem; background:var(--paper); min-height:150px; }
.proof-node:after{ content:"→"; position:absolute; right:-.48rem; top:42%; color:var(--sig);
  font-weight:800; z-index:2; }
.proof-node:last-child:after{ display:none; }
.proof-node .num{ font-family:'IBM Plex Mono'; color:var(--sig); font-size:.62rem;
  letter-spacing:.1em; font-weight:600; }
.proof-node b{ display:block; font-family:'Space Grotesk'; font-size:.88rem;
  margin:.25rem 0 .4rem; line-height:1.25; }
.proof-node .proof-quote{ color:var(--mut); font-size:.72rem; line-height:1.35; }
.proof-node .proof-ref{ display:block; color:var(--sig); font-family:'IBM Plex Mono';
  font-size:.64rem; margin-top:.45rem; font-weight:600; }
.action{ border:1px solid var(--line); border-radius:14px; background:#fff; padding:.95rem;
  margin:.55rem 0; display:grid; grid-template-columns:1.4fr .8fr; gap:1rem; }
.action h3{ font-family:'Space Grotesk'; font-size:.98rem; margin:0 0 .3rem; }
.action p{ color:var(--mut); font-size:.8rem; line-height:1.4; margin:.2rem 0; }
.action-meta{ border-left:1px solid var(--line); padding-left:.9rem; font-size:.75rem; }
.action-meta div{ margin-bottom:.35rem; }
.compare{ display:grid; grid-template-columns:1fr 1fr; gap:.7rem; margin:.7rem 0; }
.compare-card{ border:1px solid var(--line); border-radius:14px; padding:1rem; background:#fff; }
.compare-card.rootforge{ border-color:var(--sig-line); background:var(--sig-bg); }
.compare-card h3{ font-family:'Space Grotesk'; margin:0 0 .5rem; font-size:1rem; }
.compare-card div{ font-size:.8rem; line-height:1.5; margin:.25rem 0; }
.impact{ font-family:'Space Grotesk'; font-size:1.05rem; color:var(--ink); padding:.9rem 1rem;
  border-left:4px solid var(--sig); background:#fff; margin:.7rem 0 1rem; }

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
@media(max-width:760px){ .hero,.story,.repair-grid,.proof-grid,.compare,.action{ grid-template-columns:1fr; }
  .proof-node:after{ content:"↓"; right:50%; top:auto; bottom:-.65rem; }
  .action-meta{ border-left:0; border-top:1px solid var(--line); padding:.7rem 0 0; }
  .hero h1{ font-size:1.75rem; } .rail{ grid-template-columns:repeat(2,1fr); } }
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


def find_item(items, *terms):
    """Select evidence from the investigation output, never from display copy."""
    for item in items:
        haystack = " ".join(str(item.get(k, "")) for k in ("text", "quote", "rationale")).lower()
        if all(term.lower() in haystack for term in terms):
            return item
    return {}


def evidence_chain(inv):
    confirmed = inv.get("findings", {}).get("confirmed", [])
    timeline = inv.get("timeline", [])
    return [
        ("Control changed", find_item(confirmed, "45-minute", "introduced")),
        ("Training lagged", find_item(confirmed, "training", "never completed")),
        ("Escalation missed", find_item(timeline, "45 minutes", "no escalation")),
        ("Failure occurred", find_item(confirmed, "95 minutes", "60-minute")),
    ]


def selected_repairs(inv):
    capa = inv.get("capa", [])
    picks = [
        (find_item(capa, "restrict sample receipt"), "Prevents untrained execution"),
        (find_item(capa, "mandatory receiver signature"), "Creates accountable custody"),
        (find_item(capa, "45-minute elapsed-time alert"), "Intervenes before the deadline"),
    ]
    return [(item, benefit) for item, benefit in picks if item]


def render_proof(inv):
    chain = evidence_chain(inv)
    if not all(item for _, item in chain):
        return
    html = '<div class="proof"><div class="proof-grid">'
    for i, (label, item) in enumerate(chain, 1):
        refs = "; ".join(item.get("refs", []))
        html += (f'<div class="proof-node"><span class="num">0{i}</span>'
                 f'<b>{esc(label)}</b><div class="proof-quote">“{esc(item.get("quote", ""))}”</div>'
                 f'<span class="proof-ref">{esc(refs)} · verified</span></div>')
    st.markdown(html + '</div></div>', unsafe_allow_html=True)


def render_repairs(inv):
    for item, benefit in selected_repairs(inv):
        refs = "; ".join(item.get("refs", []))
        st.markdown(
            '<div class="action"><div>'
            f'<h3>{esc(item.get("text", ""))}</h3>'
            f'<p><b>Why:</b> {esc(item.get("rationale", ""))}</p></div>'
            '<div class="action-meta">'
            f'<div><b>Owner</b><br>{esc(item.get("owner_role", "Unassigned"))}</div>'
            f'<div><b>Evidence</b><br><span class="ref">{esc(refs)}</span></div>'
            f'<div><b>Expected benefit</b><br>{esc(benefit)}</div>'
            '<div><span class="chip near"><span class="dot"></span>Human approval required</span></div>'
            '</div></div>', unsafe_allow_html=True)


# --- Outcome-led masthead --------------------------------------------------
st.markdown(
    '<div class="rf-top"><div class="rf-mark"></div>'
    '<div class="rf-word">Rootforge</div>'
    '<div class="rf-ey">&nbsp;· Investigation workspace</div></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><div class="hero-copy">'
    '<div class="hero-kicker">Evidence-grounded investigations</div>'
    '<h1>From scattered records to a defensible action plan.</h1>'
    '<p>Rootforge reconstructs what happened, connects failures across documents, '
    'checks every assertion against source evidence, and shows operators exactly '
    'what to repair.</p></div>'
    '<div class="promise"><div class="promise-label">What the reviewer gets</div>'
    '<div class="promise-item"><span class="check">✓</span><span><b>One traceable story</b><br>from procedures, logs, training and email</span></div>'
    '<div class="promise-item"><span class="check">✓</span><span><b>Evidence on every claim</b><br>with unsupported assertions quarantined</span></div>'
    '<div class="promise-item"><span class="check">✓</span><span><b>Repair suggestions</b><br>with owners and rationale for human review</span></div>'
    '</div></div>', unsafe_allow_html=True)

# --- Case selector ---------------------------------------------------------
case_ids = list(CASES.keys())
labels = {
    "RF-DEMO-001": "Main investigation — find the operational failure",
    "RF-DEMO-002": "AI safety check — catch an unsupported allegation",
}
if "next_demo" in st.session_state:
    st.session_state["demo_scenario"] = st.session_state.pop("next_demo")
st.markdown('<div class="sec"><span class="n">STEP 1</span>Choose the story to show</div>',
            unsafe_allow_html=True)
chosen = st.selectbox(
    "Demo scenario",
    case_ids,
    format_func=lambda c: labels[c],
    help="Start with the main investigation. Use the AI safety check briefly at the end.",
    key="demo_scenario",
)
if chosen == "RF-DEMO-001":
    st.caption("Recommended first: shows the operational discovery, its evidence, and a repair plan.")
else:
    st.caption("Use second: shows Rootforge rejecting one deliberately unsupported model assertion.")
entry = CASES[chosen]
CASE = entry["case"]

st.markdown(f'<div class="rf-h1">{esc(CASE["title"])}</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="rf-sub"><span class="rf-caseid">{CASE["id"]}</span> &nbsp;·&nbsp; '
    f'{esc(entry["blurb"])}</div>', unsafe_allow_html=True)

prov = provider()
with st.expander("About this demonstration"):
    if prov == "replay":
        st.markdown("A recorded model response keeps the demo reliable. Rootforge's "
                    "grounding verifier still runs live against the displayed source "
                    "documents, and the reviewer can inspect every quote and citation.")
    else:
        st.markdown(f"Live model run via **{esc(prov)}**. Every generated claim is "
                    "checked against source text before it reaches confirmed findings.")

setup, evidence, timeline_tab, findings_tab, review = st.tabs(
    ["1 · Run demo", "2 · Evidence", "3 · Timeline", "4 · Findings", "5 · Repair plan"]
)

with setup:
    st.markdown(
        '<div class="story">'
        '<div class="story-card"><div class="step">01 · INGEST</div><b>Read the whole record</b><span>Six documents that normally require manual cross-checking.</span></div>'
        '<div class="story-card"><div class="step">02 · VERIFY</div><b>Prove every assertion</b><span>Quotes and citations resolve directly to source text.</span></div>'
        '<div class="story-card"><div class="step">03 · REPAIR</div><b>Turn findings into action</b><span>Suggested controls, owners and rationale stay editable.</span></div>'
        '</div>', unsafe_allow_html=True)
    with st.expander("Use your own documents"):
        uploads = st.file_uploader(
            "Upload investigation records",
            accept_multiple_files=True, type=["pdf", "docx", "txt", "md"])
    docs = load_uploads(uploads) if uploads else documents_for(chosen)
    corpus = corpus_from(docs) if uploads else corpus_for(chosen)
    refs = ", ".join(d["ref"] for d in docs)
    st.markdown(f'<div class="meta">{len(docs)} document(s) staged &nbsp;·&nbsp; '
                f'<span class="ref">{esc(refs)}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec"><span class="n">STEP 2</span>Run Rootforge</div>',
                unsafe_allow_html=True)
    button_label = ("Run main investigation" if chosen == "RF-DEMO-001"
                    else "Run AI safety check")
    if st.button(button_label, width="stretch", type="primary"):
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
        if chosen == "RF-DEMO-001":
            chain = evidence_chain(inv)
            st.markdown(
                '<div class="reveal"><div class="reveal-label">Key operational finding</div>'
                '<h2>The control changed—but the operation did not.</h2>'
                '<p>Rootforge joined four independently verified facts across procedure, training, '
                'handoff, and deviation records. The chain below is assembled from the investigation '
                'result—not written as a dashboard conclusion.</p></div>',
                unsafe_allow_html=True)
            st.markdown('<div class="sec"><span class="n">PROOF</span>The evidence chain</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="sec-note">Four records become one defensible explanation. '
                        'Every step carries its source and verified quotation.</div>',
                        unsafe_allow_html=True)
            render_proof(inv)
            st.markdown('<div class="sec"><span class="n">ACTION</span>Evidence-linked repair plan</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="sec-note">Suggestions come from the investigation output and '
                        'remain proposals until a qualified reviewer approves them.</div>',
                        unsafe_allow_html=True)
            render_repairs(inv)
            st.markdown('<div class="impact"><b>Demonstration target:</b> compress initial '
                        'reconstruction from hours of manual cross-checking to minutes, while '
                        'keeping every conclusion reviewable.</div>', unsafe_allow_html=True)
            st.markdown('<div class="sec"><span class="n">WHY</span>Why this is not generic AI</div>',
                        unsafe_allow_html=True)
            st.markdown(
                '<div class="compare">'
                '<div class="compare-card"><h3>Generic AI</h3>'
                '<div>Summarizes documents</div><div>Produces plausible answers</div>'
                '<div>May repeat unsupported claims</div><div>Stops at findings</div></div>'
                '<div class="compare-card rootforge"><h3>Rootforge</h3>'
                '<div>Reconstructs the incident across records</div>'
                '<div>Checks each quotation against source text</div>'
                '<div>Excludes unsupported assertions</div>'
                '<div>Creates an accountable, editable repair plan</div></div></div>',
                unsafe_allow_html=True)
            if st.button("Show how Rootforge handles an AI mistake →", width="stretch"):
                st.session_state["next_demo"] = "RF-DEMO-002"
                st.rerun()
        else:
            failure = ver["failures"][0] if ver["failures"] else {}
            st.markdown(
                '<div class="safety"><div class="reveal-label">Safety layer activated</div>'
                '<h2>Rootforge stopped an unsupported allegation.</h2>'
                f'<p>The model claimed: “{esc(failure.get("text", ""))}” The cited quote does '
                'not exist in the records, so the assertion was excluded from confirmed findings '
                'and preserved for reviewer inspection.</p></div>', unsafe_allow_html=True)
            st.success("Benefit: reviewers see the discrepancy without inheriting an invented motive.")
        if chosen == "RF-DEMO-001":
            st.caption("Optional deep dive: use Timeline, Findings, and Repair plan only if the audience asks.")
        else:
            st.caption("Safety proof complete. Return to the main investigation for the full operating story.")

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
            "Export review-ready Word report",
            build_report(CASE, out, st.session_state.get("docs", documents_for(chosen)),
                         reviewer, decision, notes),
            file_name=f"Rootforge_{CASE['id']}_Investigation_Draft.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            width="stretch")

st.markdown(
    '<div class="rf-footer">Rootforge · Human-reviewed investigation support · Synthetic demonstration</div>',
    unsafe_allow_html=True,
)
