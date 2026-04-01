"""
Streamlit Frontend — Autonomous Content Factory Dashboard
"""

import streamlit as st
import requests
import json
import time

st.set_page_config(
    page_title="Autonomous Content Factory",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .agent-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border-left: 4px solid;
    }
    .agent-researcher { border-left-color: #3b82f6; }
    .agent-copywriter { border-left-color: #10b981; }
    .agent-editor { border-left-color: #f59e0b; }
    .agent-brand { border-left-color: #8b5cf6; }
    .agent-system { border-left-color: #6b7280; }
    .content-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .status-approved { color: #10b981; font-weight: bold; }
    .status-rejected { color: #ef4444; font-weight: bold; }
    .status-draft { color: #f59e0b; font-weight: bold; }
    .metric-box {
        background: linear-gradient(135deg, #667eea20, #764ba220);
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

# ── Sidebar — Inputs ──
with st.sidebar:
    st.markdown("## ⚙️ Campaign Configuration")
    st.markdown("---")

    # Source Material
    st.markdown("### 📄 Source Material")
    input_method = st.radio("Input method:", ["Paste Text", "Enter URL"], horizontal=True)

    source_text = ""
    source_url = ""

    if input_method == "Paste Text":
        source_text = st.text_area(
            "Paste your source document:",
            height=200,
            placeholder="Paste your product description, technical document, press release, or any source material here..."
        )
    else:
        source_url = st.text_input(
            "Source document URL:",
            placeholder="https://example.com/product-announcement"
        )

    st.markdown("---")

    # NEW FEATURE 1: Brand URL
    st.markdown("### 🎨 Brand Style")
    brand_url = st.text_input(
        "Brand website URL (optional):",
        placeholder="https://your-brand.com",
        help="We'll analyze your website to match your brand's tone and voice"
    )

    st.markdown("---")

    # NEW FEATURE 2: Target Audience
    st.markdown("### 🎯 Target Audience")
    audience_presets = {
        "Custom": "",
        "Tech Decision Makers (CTOs, VPs)": "C-level technology executives and VP-level decision makers at mid-to-large enterprises who evaluate and procure technology solutions",
        "Software Developers": "Software developers and engineers aged 25-40 who actively seek tools to improve their workflow and code quality",
        "Small Business Owners": "Small business owners and entrepreneurs running businesses with 5-50 employees who need practical, cost-effective solutions",
        "Marketing Professionals": "Marketing managers and directors at B2B companies responsible for demand generation and content strategy",
        "General Professionals": "Working professionals across industries who want to stay current with technology and business trends",
    }

    audience_preset = st.selectbox("Quick select:", list(audience_presets.keys()))

    if audience_preset == "Custom":
        target_audience = st.text_area(
            "Describe your target audience:",
            height=100,
            placeholder="e.g., Healthcare IT administrators at hospitals with 200+ beds who need HIPAA-compliant solutions..."
        )
    else:
        target_audience = st.text_area(
            "Target audience description:",
            value=audience_presets[audience_preset],
            height=100
        )

    st.markdown("---")

    # NEW FEATURE 3: Domain Selection
    st.markdown("### 📱 Content Channels")
    col1, col2 = st.columns(2)
    with col1:
        do_linkedin = st.checkbox("LinkedIn", value=True)
        do_blog = st.checkbox("Blog Post", value=True)
    with col2:
        do_tweet = st.checkbox("Tweet Thread", value=True)
        do_email = st.checkbox("Email", value=True)

    st.markdown("---")

    # Launch button
    launch = st.button("🚀 Launch Content Factory", use_container_width=True, type="primary")

# ── Main Content Area ──
st.markdown('<p class="main-header">🏭 Autonomous Content Factory</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Multi-agent AI pipeline that transforms source material into platform-ready content</p>', unsafe_allow_html=True)

# Show configuration summary
if not launch:
    st.markdown("### 👈 Configure your campaign in the sidebar and hit Launch")

    with st.expander("ℹ️ How it works", expanded=True):
        cols = st.columns(4)
        with cols[0]:
            st.markdown("""
            **🎨 Brand Analyst**
            Scrapes your website to understand your brand voice, tone, and style
            """)
        with cols[1]:
            st.markdown("""
            **🔍 Researcher**
            Extracts facts, features, and value propositions from your source material
            """)
        with cols[2]:
            st.markdown("""
            **✍️ Copywriter**
            Generates platform-specific content matching your brand voice
            """)
        with cols[3]:
            st.markdown("""
            **📋 Editor**
            Reviews for hallucinations, tone issues, and quality — sends revisions back
            """)

# ── Run Campaign ──
if launch:
    # Validate inputs
    selected_domains = []
    if do_linkedin:
        selected_domains.append("linkedin")
    if do_blog:
        selected_domains.append("blog")
    if do_tweet:
        selected_domains.append("tweet")
    if do_email:
        selected_domains.append("email")

    if not source_text.strip() and not source_url.strip():
        st.error("⚠️ Please provide source material (text or URL)")
        st.stop()

    if not selected_domains:
        st.error("⚠️ Please select at least one content channel")
        st.stop()

    if not target_audience.strip():
        target_audience = "general professionals"

    # Build request
    payload = {
        "source_text": source_text,
        "source_url": source_url if source_url else None,
        "brand_url": brand_url if brand_url else None,
        "target_audience": target_audience,
        "selected_domains": selected_domains,
    }

    # ── Agent Activity Feed ──
    st.markdown("---")
    st.markdown("### 🤖 Agent Room — Live Activity")

    agent_log_container = st.container()
    progress_bar = st.progress(0, text="Initializing agents...")

    # ── Run via API ──
    with st.spinner(""):
        try:
            response = requests.post(
                f"{API_URL}/api/campaign",
                json=payload,
                timeout=300
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to the backend. Make sure the FastAPI server is running on port 8000.")
            st.code("cd backend && uvicorn main:app --reload --port 8000", language="bash")
            st.stop()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.stop()

    progress_bar.progress(100, text="Campaign complete!")

    # ── Display Agent Logs ──
    with agent_log_container:
        if result.get("agent_logs"):
            for log in result["agent_logs"]:
                agent = log.get("agent", "System")
                action = log.get("action", "")
                message = log.get("message", "")
                ts = log.get("timestamp", "")

                # Color coding
                if "Brand" in agent:
                    css_class = "agent-brand"
                elif "Research" in agent:
                    css_class = "agent-researcher"
                elif "Copy" in agent or "Writ" in agent:
                    css_class = "agent-copywriter"
                elif "Editor" in agent:
                    css_class = "agent-editor"
                else:
                    css_class = "agent-system"

                st.markdown(
                    f'<div class="agent-card {css_class}">'
                    f'<strong>[{ts}] {agent}</strong> {action}<br>'
                    f'<span style="color:#4b5563">{message}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    st.markdown("---")

    # ══════════════════════════════════════════════
    # RESULTS DISPLAY
    # ══════════════════════════════════════════════

    # ── Brand Style Summary ──
    if result.get("brand_style") and result["brand_style"].get("tone"):
        bs = result["brand_style"]
        with st.expander("🎨 Brand Style Analysis", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Brand:** {bs.get('brand_name', 'N/A')}")
                st.markdown(f"**Tone:** {bs.get('tone', 'N/A')}")
                if bs.get("voice_characteristics"):
                    st.markdown(f"**Voice:** {', '.join(bs['voice_characteristics'])}")
            with col2:
                if bs.get("messaging_themes"):
                    st.markdown(f"**Themes:** {', '.join(bs['messaging_themes'][:5])}")
                if bs.get("do_not_use"):
                    st.markdown(f"**Avoid:** {', '.join(bs['do_not_use'][:5])}")

    # ── Fact Sheet ──
    if result.get("fact_sheet"):
        fs = result["fact_sheet"]
        with st.expander("📊 Source of Truth — Fact Sheet", expanded=False):
            st.markdown(f"**Product:** {fs.get('product_name', 'N/A')}")
            st.markdown(f"**Value Proposition:** {fs.get('value_proposition', 'N/A')}")

            col1, col2 = st.columns(2)
            with col1:
                if fs.get("core_features"):
                    st.markdown("**Core Features:**")
                    for f in fs["core_features"]:
                        st.markdown(f"- {f}")
            with col2:
                if fs.get("key_benefits"):
                    st.markdown("**Key Benefits:**")
                    for b in fs["key_benefits"]:
                        st.markdown(f"- {b}")

            if fs.get("ambiguous_statements"):
                st.warning("⚠️ **Ambiguous Statements Flagged:**")
                for a in fs["ambiguous_statements"]:
                    st.markdown(f"- _{a}_")

    # ── Content Outputs ──
    st.markdown("### 📦 Generated Content")

    if result.get("content_pieces"):
        # Summary metrics
        pieces = result["content_pieces"]
        metric_cols = st.columns(len(pieces))
        for i, piece in enumerate(pieces):
            with metric_cols[i]:
                domain = piece.get("domain", "unknown")
                status = piece.get("status", "unknown")
                revisions = piece.get("revision_count", 0)

                icon_map = {
                    "linkedin": "💼",
                    "blog": "📝",
                    "tweet": "🐦",
                    "email": "📧",
                }
                icon = icon_map.get(domain, "📄")

                status_color = "🟢" if "approved" in status else "🟡" if status == "draft" else "🔴"

                st.markdown(
                    f'<div class="metric-box">'
                    f'<h3>{icon} {domain.upper()}</h3>'
                    f'<p>{status_color} {status.replace("_", " ").title()}</p>'
                    f'<small>Revisions: {revisions}</small>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ── Side-by-Side Content View ──
        # Determine layout based on number of pieces
        if len(pieces) <= 2:
            cols = st.columns(len(pieces))
        else:
            cols = st.columns(2)

        for i, piece in enumerate(pieces):
            domain = piece.get("domain", "unknown")
            content = piece.get("content", "")
            status = piece.get("status", "unknown")
            editor_notes = piece.get("editor_notes", "")

            icon_map = {"linkedin": "💼", "blog": "📝", "tweet": "🐦", "email": "📧"}
            domain_labels = {"linkedin": "LinkedIn Post", "blog": "Blog Post", "tweet": "Tweet Thread", "email": "Email"}

            col = cols[i % len(cols)]

            with col:
                st.markdown(f"#### {icon_map.get(domain, '📄')} {domain_labels.get(domain, domain)}")

                if "approved" in status:
                    st.success(f"Status: {status.replace('_', ' ').title()}")
                else:
                    st.warning(f"Status: {status}")

                # Content display with proper formatting
                if domain == "blog":
                    st.markdown(content)
                elif domain == "tweet":
                    # Display each tweet separately
                    tweets = [t.strip() for t in content.split("\n") if t.strip() and t.strip()[0:2] in ["1/", "2/", "3/", "4/", "5/"]]
                    if not tweets:
                        tweets = [t.strip() for t in content.split("\n\n") if t.strip()]

                    for tweet in tweets:
                        st.info(tweet)
                elif domain == "email":
                    st.markdown(content)
                else:
                    st.markdown(content)

                if editor_notes:
                    st.caption(f"📋 Editor: {editor_notes}")

                # Copy button
                st.text_area(
                    f"Copy {domain} content:",
                    value=content,
                    height=100,
                    key=f"copy_{domain}_{i}",
                    label_visibility="collapsed"
                )

        # ── Export All ──
        st.markdown("---")
        st.markdown("### 📥 Export Campaign Kit")

        export_content = ""
        for piece in pieces:
            domain = piece.get("domain", "unknown")
            content = piece.get("content", "")
            export_content += f"{'='*60}\n"
            export_content += f"  {domain.upper()}\n"
            export_content += f"{'='*60}\n\n"
            export_content += content
            export_content += f"\n\n"

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Download Campaign Kit (.txt)",
                data=export_content,
                file_name="campaign_kit.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                "📥 Download as JSON",
                data=json.dumps(result, indent=2),
                file_name="campaign_data.json",
                mime="application/json",
                use_container_width=True,
            )

    # ── Side-by-Side: Source vs Output ──
    if source_text.strip() and result.get("content_pieces"):
        st.markdown("---")
        st.markdown("### 🔄 Source vs. Output Comparison")
        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            st.markdown("**📄 Original Source**")
            st.text_area("source_original", source_text[:3000], height=400, label_visibility="collapsed")
        with comp_col2:
            domain_select = st.selectbox(
                "Compare with:",
                [p.get("domain", "unknown") for p in result["content_pieces"]]
            )
            selected_piece = next(
                (p for p in result["content_pieces"] if p.get("domain") == domain_select), None
            )
            if selected_piece:
                st.markdown(f"**{domain_select.upper()} Output**")
                st.text_area("output_compare", selected_piece.get("content", ""), height=400,
                           label_visibility="collapsed")