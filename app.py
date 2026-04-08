"""
app.py — ResumeIQ Streamlit Entry Point
========================================
This file is the ONLY file that Streamlit runs.
Its sole job is to:
  1. Configure the page
  2. Inject the CSS theme
  3. Build the sidebar (inputs)
  4. Render the hero banner
  5. Trigger the analysis pipeline (via core.py)
  6. Pass results to the correct tab renderers (via ui_components.py)

No AI logic, no HTML strings, no CSS lives here —
everything is imported from core.py and ui_components.py.

Run:
    streamlit run app.py
"""

import streamlit as st

# ── Internal modules ──────────────────────────────────────────────────────────
from core import (
    DEMO_RESUME,
    DEMO_JD,
    extract_resume_text,
    run_full_analysis,
)
from ui_components import (
    inject_css,
    render_hero,
    render_sidebar_brand,
    render_sidebar_how_it_works,
    render_tab_dashboard,
    render_tab_skills,
    render_tab_suggestions,
    render_tab_jobs,
    render_empty_state,
)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ──────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="ResumeIQ · AI Resume Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject the full dark-theme CSS
inject_css()


# ──────────────────────────────────────────────────────────────────────────────
# SESSION STATE DEFAULTS
# ──────────────────────────────────────────────────────────────────────────────

if "results"   not in st.session_state: st.session_state["results"]   = None
if "demo_mode" not in st.session_state: st.session_state["demo_mode"] = False


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    render_sidebar_brand()

    st.markdown("### 📄 Upload Resume")
    uploaded_file = st.file_uploader(
        "PDF or DOCX",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed",
    )

    st.markdown("### 💼 Job Description")
    jd_input = st.text_area(
        "Paste JD here",
        height=220,
        placeholder="Paste the job description you want to match against...",
        label_visibility="collapsed",
    )

    st.markdown("---")
    analyze_btn = st.button("⚡  Analyze Resume", use_container_width=True)

    render_sidebar_how_it_works()


# ──────────────────────────────────────────────────────────────────────────────
# HERO BANNER
# ──────────────────────────────────────────────────────────────────────────────

render_hero()


# ──────────────────────────────────────────────────────────────────────────────
# DEMO TOGGLE
# ──────────────────────────────────────────────────────────────────────────────

_, demo_col = st.columns([6, 1])
with demo_col:
    if st.button("🎯 Load Demo"):
        st.session_state["demo_mode"] = True
        st.session_state["results"]   = None

if st.session_state["demo_mode"] and not uploaded_file:
    st.info(
        "💡 **Demo mode active** — using a sample AIML Engineer resume. "
        "Upload your own resume + JD in the sidebar for a real analysis."
    )


# ──────────────────────────────────────────────────────────────────────────────
# ANALYSIS TRIGGER
# ──────────────────────────────────────────────────────────────────────────────

if analyze_btn:
    # ── Resolve resume text ──
    resume_text = ""
    if uploaded_file:
        resume_text = extract_resume_text(uploaded_file)
    elif st.session_state["demo_mode"]:
        resume_text = DEMO_RESUME

    if not resume_text:
        st.error("⚠️ Please upload a resume or click 🎯 Load Demo first.")
        st.stop()

    # ── Resolve JD text ──
    jd_text = jd_input.strip() if jd_input.strip() else DEMO_JD

    # ── Run the four-stage AI pipeline ──
    with st.spinner("🔍 Parsing resume with NLP…"):
        from core import parse_resume
        parsed = parse_resume(resume_text)

    with st.spinner("🧠 Extracting skills & computing match score…"):
        from core import extract_skills_analysis
        analysis = extract_skills_analysis(resume_text, jd_text)

    with st.spinner("💡 Generating LLM suggestions…"):
        from core import get_llm_suggestions
        suggestions = get_llm_suggestions(resume_text, jd_text, analysis)

    with st.spinner("🎯 Finding best-fit job roles…"):
        from core import get_job_matches
        job_matches = get_job_matches(resume_text, parsed.get("skills", []))

    # ── Persist results in session state ──
    st.session_state["results"]   = {
        "parsed":      parsed,
        "analysis":    analysis,
        "suggestions": suggestions,
        "job_matches": job_matches,
    }
    st.session_state["demo_mode"] = False


# ──────────────────────────────────────────────────────────────────────────────
# RESULTS DISPLAY
# ──────────────────────────────────────────────────────────────────────────────

if st.session_state["results"]:
    R           = st.session_state["results"]
    parsed      = R["parsed"]
    analysis    = R["analysis"]
    suggestions = R["suggestions"]
    job_matches = R["job_matches"]

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard",
        "🧩 Skills Analysis",
        "💡 AI Suggestions",
        "🎯 Job Matches",
    ])

    with tab1:
        render_tab_dashboard(parsed, analysis)

    with tab2:
        render_tab_skills(parsed, analysis)

    with tab3:
        render_tab_suggestions(suggestions)

    with tab4:
        render_tab_jobs(job_matches)

else:
    render_empty_state()
