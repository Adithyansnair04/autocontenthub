"""
Streamlit Frontend — Autonomous Content Factory
"""

import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Content Factory",
    page_icon="⚡",
    layout="wide",
    # initial_sidebar_state="collapsed"  # Removed sidebar configuration
)

# ══════════════════════════════════════════════════════════════
# STYLES
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; font-family: 'Inter', sans-serif; }

/* ── App bg ── */
.stApp {
    background: #08090d;
    color: #f0f0f0;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2.4rem !important; padding-bottom: 3rem !important; }

/* --- REMOVED ALL SIDEBAR/HAMBURGER RELATED CSS --- */

/* ── Main header ── */
.hero-eyebrow {
    font-size: 0.70rem;
    font-weight: 600;
    letter-spacing: 0.20em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.30);
    margin-bottom: 10px;
    /* margin-left: 54px;  -- Removed as no hamburger icon present */
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.12;
    background: linear-gradient(110deg, #ffffff 30%, rgba(255,255,255,0.45));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}
.hero-sub {
    font-size: 0.95rem;
    font-weight: 400;
    color: rgba(255,255,255,0.40);
    letter-spacing: 0.01em;
    margin-bottom: 0;
}

/* ── Section label ── */
.field-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.30);
    margin-bottom: 6px;
    margin-top: 20px;
}

/* ── Inputs ── */
div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.04) !important;
    color: #f0f0f0 !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 12px !important;
    font-size: 0.88rem !important;
    transition: border-color 0.2s;
}
div[data-testid="stTextArea"] textarea:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: rgba(255,255,255,0.26) !important;
    box-shadow: 0 0 0 3px rgba(255,255,255,0.04) !important;
}
div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 12px !important;
}
.stRadio > div { gap: 12px !important; }
.stRadio label { font-size: 0.85rem !important; color: rgba(255,255,255,0.65) !important; }

/* ── Channel cards ── */
.ch-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 14px;
    padding: 18px 14px 14px;
    text-align: center;
    transition: all 0.22s ease;
    cursor: pointer;
}
.ch-card:hover {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.18);
    transform: translateY(-2px);
}
.ch-card .ch-name {
    font-size: 0.80rem;
    font-weight: 500;
    color: rgba(255,255,255,0.75);
    margin-top: 10px;
    letter-spacing: 0.02em;
}
.stCheckbox { justify-content: center !important; }
.stCheckbox label { font-size: 0 !important; width: 20px; height: 20px; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.8rem 0 !important; }

/* ── Launch button ── */
.stButton > button {
    background: #ffffff !important;
    color: #08090d !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.90rem !important;
    letter-spacing: 0.01em !important;
    padding: 13px !important;
    transition: all 0.22s ease !important;
    box-shadow: 0 0 0 0 rgba(255,255,255,0);
}
.stButton > button:hover {
    background: #e8e8e8 !important;
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(255,255,255,0.10) !important;
}

/* ── Expander ── */
div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
}
div[data-testid="stExpander"] summary {
    font-size: 0.82rem !important;
    color: rgba(255,255,255,0.50) !important;
}

/* ── Steps ── */
.step-row {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.step-row:last-child { border-bottom: none; }
.step-num {
    font-size: 0.65rem;
    font-weight: 700;
    color: rgba(255,255,255,0.20);
    width: 18px;
    padding-top: 2px;
    flex-shrink: 0;
}
.step-body {
    font-size: 0.83rem;
    color: rgba(255,255,255,0.55);
    line-height: 1.55;
}
.step-body b {
    color: rgba(255,255,255,0.85);
    font-weight: 500;
}

/* ── Agent log cards ── */
.agent-card {
    background: rgba(255,255,255,0.03);
    border-left: 2px solid rgba(255,255,255,0.12);
    border-radius: 0 10px 10px 0;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.82rem;
}
.agent-brand      { border-left-color: #a78bfa; }
.agent-researcher { border-left-color: #60a5fa; }
.agent-trend      { border-left-color: #f472b6; }
.agent-copywriter { border-left-color: #34d399; }
.agent-editor     { border-left-color: #fbbf24; }
.agent-system     { border-left-color: rgba(255,255,255,0.20); }

/* ── Metric box ── */
.metric-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 12px;
    text-align: center;
    transition: all 0.22s ease;
}
.metric-box:hover {
    background: rgba(255,255,255,0.07);
    transform: translateY(-3px);
}
.metric-box h3 { font-size: 0.88rem; font-weight: 600; margin: 0 0 6px; }
.metric-box p  { font-size: 0.78rem; color: rgba(255,255,255,0.50); margin: 0; }
.metric-box small { font-size: 0.70rem; color: rgba(255,255,255,0.28); }
</style>
""", unsafe_allow_html=True)


API_URL = "http://localhost:8000"

# ══════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="hero-eyebrow">Autonomous Content Factory</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-title">Your brand voice.<br>Every platform.</div>', unsafe_allow_html=True)

st.markdown("&nbsp;", unsafe_allow_html=True)

with st.expander("How it works"):
    st.markdown("""
    <div class="step-row"><div class="step-num">01</div><div class="step-body"><b>Add your source</b> — any text, URL, or doc.</div></div>
    <div class="step-row"><div class="step-num">02</div><div class="step-body"><b>Set your audience</b> — who this is for.</div></div>
    <div class="step-row"><div class="step-num">03</div><div class="step-body"><b>Pick channels</b> — LinkedIn, blog, tweets, email.</div></div>
    <div class="step-row"><div class="step-num">04</div><div class="step-body"><b>Launch</b> — agents run, content ships.</div></div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# FORM
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="field-label">Source Material</div>', unsafe_allow_html=True)
input_method = st.radio("", ["Paste Text", "Enter URL"], horizontal=True, label_visibility="collapsed")

source_text = ""
source_url  = ""

if input_method == "Paste Text":
    source_text = st.text_area(
        "", height=160,
        placeholder="Drop your source — product brief, press release, doc, anything…",
        label_visibility="collapsed"
    )
else:
    source_url = st.text_input(
        "", placeholder="https://example.com/announcement",
        label_visibility="collapsed"
    )

col_l, col_r = st.columns(2, gap="large")

with col_l:
    st.markdown('<div class="field-label">Brand Website <span style="color:rgba(255,255,255,0.15)">· optional</span></div>', unsafe_allow_html=True)
    brand_url = st.text_input(
        "", placeholder="https://your-brand.com",
        key="brand_url", label_visibility="collapsed"
    )

with col_r:
    st.markdown('<div class="field-label">Target Audience</div>', unsafe_allow_html=True)
    audience_presets = {
        "General Professionals": "Working professionals who want to stay current with business and technology trends.",
        "Tech Decision Makers": "C-level and VP-level technology leaders evaluating enterprise solutions.",
        "Software Developers": "Engineers aged 25–40 looking for tools that sharpen their craft.",
        "Small Business Owners": "Entrepreneurs running 5–50 person teams who need practical solutions.",
        "Marketing Professionals": "B2B marketing leads responsible for demand generation and content.",
        "Custom →": "",
    }
    audience_preset = st.selectbox("", list(audience_presets.keys()), label_visibility="collapsed")
    if audience_preset == "Custom →":
        target_audience = st.text_area(
            "", height=68,
            placeholder="Describe your audience…",
            label_visibility="collapsed", key="custom_audience"
        )
    else:
        target_audience = audience_presets[audience_preset]

st.markdown('<div class="field-label">Channels</div>', unsafe_allow_html=True)

# Real SVG brand logos
_LI_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 72 72' width='36' height='36'>
  <rect width='72' height='72' rx='8' fill='#0A66C2'/>
  <path fill='#fff' d='M21 25a5 5 0 110-10 5 5 0 010 10zm-4 5h8v25h-8V30zm13 0h7.7v3.4h.1c1.1-2 3.7-4 7.6-4 8.1 0 9.6 5.3 9.6 12.2V55H47V43.4c0-2.8-.05-6.4-3.9-6.4-3.9 0-4.5 3-4.5 6.2V55H30V30z'/>
</svg>"""

_X_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 72 72' width='36' height='36'>
  <rect width='72' height='72' rx='8' fill='#000'/>
  <path fill='#fff' d='M41.2 32.7L54.5 17h-3.2L39.8 30.7 30.5 17H19l14 20.3L19 55h3.2l12.2-14.2L44.5 55H56L41.2 32.7zm-4.3 5L35.4 35l-11-15.8h5.3l9.3 13.3 1.5 2.2 11.3 16.2h-5.3l-9.6-13.8z'/>
</svg>"""

_GMAIL_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 72 72' width='36' height='36'>
  <rect width='72' height='72' rx='8' fill='#fff'/>
  <path fill='#EA4335' d='M12 54V28l24 16 24-16v26H12z'/>
  <path fill='#FBBC04' d='M12 28l24 16-24-16z' />
  <path fill='#4285F4' d='M60 28l-24 16 24-16z' />
  <path fill='#34A853' d='M60 54V28H12v26h48z' fill-opacity='0'/>
  <path fill='#EA4335' d='M12 23v5l24 16 24-16v-5L36 38 12 23z'/>
  <rect x='12' y='23' width='48' height='31' rx='0' fill='none'/>
  <path fill='#C5221F' d='M12 23v4l24 16 24-16v-4L36 37 12 23z' />
  <path fill='#EA4335' d='M12 27v-4l-4-3v34l4 4V27z'/>
  <path fill='#4285F4' d='M60 27v-4l4-3v34l-4 4V27z'/>
  <path fill='#EA4335' d='M12 23h48l4-4H8l4 4z'/>
</svg>"""

_BLOG_SVG = """<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 72 72' width='36' height='36'>
  <rect width='72' height='72' rx='8' fill='#FF6B35'/>
  <path fill='#fff' d='M20 50h32v4H20zm0-10h32v4H20zm0-10h20v4H20zm26.4-10.4l-2.8 2.8 5.6 5.6 2.8-2.8a2 2 0 000-2.8l-2.8-2.8a2 2 0 00-2.8 0zM20 38.2V44h5.8l17-17-5.8-5.8L20 38.2z'/>
</svg>"""

ch1, ch2, ch3, ch4 = st.columns(4, gap="medium")
with ch1:
    st.markdown(f'<div class="ch-card">{_LI_SVG}<div class="ch-name">LinkedIn</div></div>', unsafe_allow_html=True)
    do_linkedin = st.checkbox("LinkedIn", value=True, key="ch_li", label_visibility="collapsed")
with ch2:
    st.markdown(f'<div class="ch-card">{_X_SVG}<div class="ch-name">X  /  Twitter</div></div>', unsafe_allow_html=True)
    do_tweet = st.checkbox("Tweets", value=True, key="ch_tw", label_visibility="collapsed")
with ch3:
    st.markdown(f'<div class="ch-card">{_GMAIL_SVG}<div class="ch-name">Email</div></div>', unsafe_allow_html=True)
    do_email = st.checkbox("Email", value=True, key="ch_em", label_visibility="collapsed")
with ch4:
    st.markdown(f'<div class="ch-card">{_BLOG_SVG}<div class="ch-name">Blog Post</div></div>', unsafe_allow_html=True)
    do_blog = st.checkbox("Blog", value=True, key="ch_bl", label_visibility="collapsed")

st.markdown("&nbsp;", unsafe_allow_html=True)
launch = st.button("Generate Content", use_container_width=False, type="primary")

# ══════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════
if launch:
    selected_domains = []
    if do_linkedin: selected_domains.append("linkedin")
    if do_blog:     selected_domains.append("blog")
    if do_tweet:    selected_domains.append("tweet")
    if do_email:    selected_domains.append("email")

    if not source_text.strip() and not source_url.strip():
        st.error("Add source material to continue.")
        st.stop()
    if not selected_domains:
        st.error("Select at least one channel.")
        st.stop()
    if not target_audience.strip():
        target_audience = "general professionals"

    payload = {
        "source_text": source_text,
        "source_url":  source_url or None,
        "brand_url":   brand_url  or None,
        "target_audience":  target_audience,
        "selected_domains": selected_domains,
    }

    st.markdown("---")
    st.markdown('<div class="field-label">Agent Activity</div>', unsafe_allow_html=True)
    log_container = st.container()
    bar = st.progress(0, text="Starting…")

    with st.spinner(""):
        try:
            resp = requests.post(f"{API_URL}/api/campaign", json=payload, timeout=300)
            resp.raise_for_status()
            result = resp.json()
        except requests.exceptions.ConnectionError:
            st.error("Backend unreachable — is the FastAPI server on port 8000?")
            st.stop()
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

    bar.progress(100, text="Done ✓")

    with log_container:
        for log in result.get("agent_logs", []):
            agent = log.get("agent", "System")
            if "Brand"    in agent: css = "agent-brand"
            elif "Research" in agent: css = "agent-researcher"
            elif "Trend"   in agent: css = "agent-trend"
            elif "Copy" in agent or "Writ" in agent: css = "agent-copywriter"
            elif "Editor"  in agent: css = "agent-editor"
            else: css = "agent-system"
            st.markdown(
                f'<div class="agent-card {css}">'
                f'<strong>{agent}</strong> · {log.get("action","")}'
                f'<br><span style="color:rgba(255,255,255,0.35)">{log.get("message","")}</span>'
                f'</div>', unsafe_allow_html=True
            )

    st.markdown("---")

    # Brand / Fact expanders
    if result.get("brand_style") and result["brand_style"].get("tone"):
        bs = result["brand_style"]
        with st.expander("Brand Analysis"):
            b1, b2 = st.columns(2)
            with b1:
                st.markdown(f"**Brand** · {bs.get('brand_name','—')}")
                st.markdown(f"**Tone** · {bs.get('tone','—')}")
            with b2:
                if bs.get("messaging_themes"):
                    st.markdown(f"**Themes** · {', '.join(bs['messaging_themes'][:4])}")

    if result.get("fact_sheet"):
        fs = result["fact_sheet"]
        with st.expander("Fact Sheet"):
            st.markdown(f"**{fs.get('product_name','—')}** — {fs.get('value_proposition','')}")
            f1, f2 = st.columns(2)
            with f1:
                for f in fs.get("core_features", []):
                    st.markdown(f"· {f}")
            with f2:
                for b in fs.get("key_benefits", []):
                    st.markdown(f"· {b}")

    # ── Trend Intelligence panel ──
    if result.get("trend_context"):
        tc = result["trend_context"]
        with st.expander("📈 Trend Intelligence (used to shape content)"):
            t1, t2 = st.columns(2)
            with t1:
                if tc.get("industry_trends"):
                    st.markdown("**🌐 Industry Trends**")
                    for t in tc["industry_trends"][:5]:
                        st.markdown(f"· {t}")
                if tc.get("dominant_tensions"):
                    st.markdown("**⚡ Audience Tensions**")
                    for t in tc["dominant_tensions"][:3]:
                        st.markdown(f"· {t}")
            with t2:
                if tc.get("content_angles"):
                    st.markdown("**🎯 Fresh Content Angles**")
                    for a in tc["content_angles"][:4]:
                        st.markdown(f"· {a}")
                if tc.get("urgency_signals"):
                    st.markdown("**🚨 Urgency Signals**")
                    for u in tc["urgency_signals"][:2]:
                        st.markdown(f"· {u}")
            if tc.get("trending_vocabulary"):
                vocab = " · ".join(tc["trending_vocabulary"][:6])
                st.caption(f"Trending vocabulary used: {vocab}")

    # Content
    icon_map  = {"linkedin": "💼", "blog": "📝", "tweet": "🐦", "email": "📧"}
    label_map = {"linkedin": "LinkedIn", "blog": "Blog", "tweet": "Tweets", "email": "Email"}

    pieces = result.get("content_pieces", [])
    if pieces:
        st.markdown('<div class="field-label" style="margin-top:1.8rem">Output</div>', unsafe_allow_html=True)
        mcols = st.columns(len(pieces))
        for i, piece in enumerate(pieces):
            d = piece.get("domain","unknown")
            s = piece.get("status","—")
            dot = "●" if "approved" in s else "○"
            with mcols[i]:
                st.markdown(
                    f'<div class="metric-box">'
                    f'<h3>{icon_map.get(d,"📄")} {label_map.get(d,d)}</h3>'
                    f'<p>{dot} {s.replace("_"," ").title()}</p>'
                    f'<small>{piece.get("revision_count",0)} revision(s)</small>'
                    f'</div>', unsafe_allow_html=True
                )

        st.markdown("&nbsp;", unsafe_allow_html=True)
        cols = st.columns(2) if len(pieces) > 2 else st.columns(len(pieces))
        for i, piece in enumerate(pieces):
            d       = piece.get("domain","unknown")
            content = piece.get("content","")
            status  = piece.get("status","—")
            with cols[i % len(cols)]:
                st.markdown(f"**{icon_map.get(d,'📄')} {label_map.get(d,d)}**")
                if "approved" in status: st.success(status.replace("_"," ").title())
                else: st.warning(status)
                if d == "tweet":
                    for tw in [t.strip() for t in content.split("\n\n") if t.strip()]:
                        st.info(tw)
                else:
                    st.markdown(content)
                if piece.get("editor_notes"):
                    st.caption(f"Editor · {piece['editor_notes']}")
                st.text_area("", value=content, height=90,
                             key=f"cp_{d}_{i}", label_visibility="collapsed")

        st.markdown("---")
        export_txt = "\n\n".join(
            f"{'—'*40}\n{label_map.get(p.get('domain'),'')}\n{'—'*40}\n\n{p.get('content','')}"
            for p in pieces
        )
        dl1, dl2, _ = st.columns([1, 1, 3])
        with dl1:
            st.download_button("↓ Text", data=export_txt,
                               file_name="campaign.txt", mime="text/plain",
                               use_container_width=True)
        with dl2:
            st.download_button("↓ JSON", data=json.dumps(result, indent=2),
                               file_name="campaign.json", mime="application/json",
                               use_container_width=True)

    if source_text.strip() and pieces:
        st.markdown("---")
        st.markdown('<div class="field-label">Compare</div>', unsafe_allow_html=True)
        cm1, cm2 = st.columns(2)
        with cm1:
            st.caption("Source")
            st.text_area("", source_text[:3000], height=320, label_visibility="collapsed")
        with cm2:
            domain_sel = st.selectbox("", [p.get("domain") for p in pieces], label_visibility="collapsed")
            sel = next((p for p in pieces if p.get("domain") == domain_sel), None)
            if sel:
                st.caption(label_map.get(domain_sel, domain_sel))
                st.text_area("", sel.get("content",""), height=320, label_visibility="collapsed")