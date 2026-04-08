"""
ui_components.py — ResumeIQ UI Rendering Layer
================================================
Every reusable visual element lives here:
  - inject_css()           Dark theme stylesheet
  - render_donut()         Inline SVG score ring
  - render_progress()      Labeled gradient progress bar
  - render_skills()        Color-coded skill pill cloud
  - render_metric_card()   Single KPI card
  - render_hero()          Landing hero banner
  - render_profile_card()  Candidate profile block
  - render_edu_card()      Education + certifications card
  - render_experience()    Work-experience card list
  - render_tab_dashboard() Full Tab 1 content
  - render_tab_skills()    Full Tab 2 content
  - render_tab_suggestions() Full Tab 3 content
  - render_tab_jobs()      Full Tab 4 content
  - render_empty_state()   Placeholder when no results yet

This file imports streamlit but does NOT import core.py —
keeping the dependency arrow one-way:  app.py → core.py + ui_components.py
"""

import streamlit as st


# ──────────────────────────────────────────────────────────────────────────────
# THEME HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def score_color(score: int) -> str:
    """Map a 0-100 score to a semantic hex colour."""
    if score >= 75:
        return "#10b981"   # green
    if score >= 50:
        return "#f59e0b"   # amber
    return "#ef4444"       # red


# ──────────────────────────────────────────────────────────────────────────────
# 1. CSS INJECTION
# ──────────────────────────────────────────────────────────────────────────────

def inject_css() -> None:
    """
    Inject the full dark-theme stylesheet into the Streamlit page.
    Call once at the top of app.py, before any other st.* calls.
    """
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

/* ── Root Variables ── */
:root {
    --bg:       #0a0a0f;
    --surface:  #111118;
    --card:     #16161f;
    --border:   #2a2a3a;
    --accent:   #7c3aed;
    --accent2:  #06b6d4;
    --accent3:  #f59e0b;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --success:  #10b981;
    --danger:   #ef4444;
    --radius:   12px;
}

/* ── Global reset ── */
html, body, .stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1400px !important; }

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a0a2e 40%, #0a1a2e 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 3rem 3.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; top: -60%; right: -10%;
    width: 500px; height: 500px;
    background: radial-gradient(circle, rgba(124,58,237,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute; bottom: -40%; left: 20%;
    width: 350px; height: 350px;
    background: radial-gradient(circle, rgba(6,182,212,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(124,58,237,0.2);
    border: 1px solid rgba(124,58,237,0.4);
    color: #a78bfa;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    padding: 4px 14px;
    border-radius: 100px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 3.2rem !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
    margin: 0 0 1rem !important;
    background: linear-gradient(135deg, #e2e8f0 30%, #a78bfa 70%, #67e8f9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero p { color: var(--muted); font-size: 1.1rem; max-width: 600px; line-height: 1.7; }
.hero-stats { display: flex; gap: 2.5rem; margin-top: 1.8rem; }
.stat-item  { text-align: left; }
.stat-num   { font-family: 'Space Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
.stat-label { font-size: 0.78rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }

/* ── Cards ── */
.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.6rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.card:hover { border-color: rgba(124,58,237,0.5); }
.card-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--accent2);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.8rem;
}

/* ── Score ring ── */
.score-container { text-align: center; padding: 1.5rem; }
.score-label { font-size: 0.8rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1.5px; }

/* ── Skill pills ── */
.skill-cloud { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0.5rem; }
.skill-pill  {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    padding: 5px 14px;
    border-radius: 100px;
    border: 1px solid;
    letter-spacing: 0.5px;
}
.skill-match   { background: rgba(16,185,129,0.1);  border-color: rgba(16,185,129,0.4);  color: #34d399; }
.skill-missing { background: rgba(239,68,68,0.1);   border-color: rgba(239,68,68,0.4);   color: #f87171; }
.skill-neutral { background: rgba(100,116,139,0.1); border-color: rgba(100,116,139,0.3); color: #94a3b8; }

/* ── Progress bars ── */
.prog-wrap  { margin: 0.5rem 0; }
.prog-label { display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 4px; color: var(--text); }
.prog-track { background: var(--border); border-radius: 100px; height: 6px; overflow: hidden; }
.prog-fill  { height: 100%; border-radius: 100px; background: linear-gradient(90deg, var(--accent), var(--accent2)); transition: width 0.8s ease; }

/* ── Section dividers ── */
.section-header { display: flex; align-items: center; gap: 12px; margin: 2rem 0 1rem; }
.section-line   { flex: 1; height: 1px; background: var(--border); }
.section-tag    { font-family: 'Space Mono', monospace; font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 2px; white-space: nowrap; }

/* ── Suggestion cards ── */
.suggestion {
    background: rgba(124,58,237,0.06);
    border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
    padding: 1rem 1.2rem;
    margin: 0.6rem 0;
    font-size: 0.9rem;
    line-height: 1.6;
    color: var(--text);
}
.suggestion-num {
    font-family: 'Space Mono', monospace;
    font-size: 0.68rem;
    color: var(--accent);
    margin-bottom: 4px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Job match cards ── */
.job-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin: 0.6rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.2s;
}
.job-card:hover { border-color: rgba(6,182,212,0.4); background: rgba(6,182,212,0.04); }
.job-title { font-weight: 700; font-size: 1rem; margin-bottom: 3px; }
.job-meta  { font-size: 0.8rem; color: var(--muted); font-family: 'Space Mono', monospace; }
.job-score { font-family: 'Space Mono', monospace; font-size: 1.4rem; font-weight: 700; }

/* ── Animations ── */
@keyframes fadeSlide {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.animate  { animation: fadeSlide 0.5s ease forwards; }
.delay-1  { animation-delay: 0.1s; opacity: 0; }
.delay-2  { animation-delay: 0.2s; opacity: 0; }
.delay-3  { animation-delay: 0.3s; opacity: 0; }
.delay-4  { animation-delay: 0.4s; opacity: 0; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Streamlit widget overrides ── */
.stTextArea textarea, .stTextInput input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}
.stButton button {
    background: linear-gradient(135deg, var(--accent), #6d28d9) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.8rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.5px !important;
}
.stButton button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
}
.stSelectbox > div > div {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(124,58,237,0.2) !important;
    border-color: var(--accent) !important;
    color: var(--text) !important;
}
[data-testid="stFileUploader"] {
    background: var(--card) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(124,58,237,0.5) !important; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 2. ATOMIC COMPONENTS
# ──────────────────────────────────────────────────────────────────────────────

def render_donut(score: int, label: str = "Match Score") -> None:
    """Render an inline SVG donut ring showing score/100 with dynamic colour."""
    color = score_color(score)
    r, cx, cy  = 52, 70, 70
    circumference = 2 * 3.14159 * r
    dash          = circumference * score / 100

    st.markdown(f"""
    <div class="score-container">
      <svg width="140" height="140" viewBox="0 0 140 140">
        <circle cx="{cx}" cy="{cy}" r="{r}"
                fill="none" stroke="#2a2a3a" stroke-width="12"/>
        <circle cx="{cx}" cy="{cy}" r="{r}"
                fill="none" stroke="{color}" stroke-width="12"
                stroke-dasharray="{dash:.1f} {circumference:.1f}"
                stroke-dashoffset="{circumference / 4:.1f}"
                stroke-linecap="round"/>
        <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central"
              font-family="Space Mono,monospace" font-size="22"
              font-weight="700" fill="#e2e8f0">{score}</text>
        <text x="{cx}" y="{cy + 22}" text-anchor="middle"
              font-family="Syne,sans-serif" font-size="9"
              fill="#64748b" letter-spacing="1">/ 100</text>
      </svg>
      <div class="score-label" style="color:{color}">{label}</div>
    </div>""", unsafe_allow_html=True)


def render_progress(label: str, value: int, color: str = "#7c3aed") -> None:
    """Render a single labelled progress bar with gradient fill."""
    st.markdown(f"""
    <div class="prog-wrap">
      <div class="prog-label">
        <span>{label}</span>
        <span style="color:{color};font-family:'Space Mono',monospace">{value}%</span>
      </div>
      <div class="prog-track">
        <div class="prog-fill"
             style="width:{value}%;background:linear-gradient(90deg,{color},{color}cc)">
        </div>
      </div>
    </div>""", unsafe_allow_html=True)


def render_skills(skills: list[str], css_class: str) -> None:
    """
    Render a flex-wrapped cloud of skill pills.

    css_class options:
        "skill-match"   → green  (skills present in both resume & JD)
        "skill-missing" → red    (skills in JD but absent from resume)
        "skill-neutral" → gray   (extra / tool skills)
    """
    if not skills:
        st.markdown('<p style="color:#64748b;font-size:0.85rem">None found.</p>',
                    unsafe_allow_html=True)
        return
    pills = "".join(
        f'<span class="skill-pill {css_class}">{s}</span>' for s in skills
    )
    st.markdown(f'<div class="skill-cloud">{pills}</div>', unsafe_allow_html=True)


def render_metric_card(label: str, value, unit: str, color: str) -> None:
    """Render a single KPI card with large coloured value."""
    st.markdown(f"""
    <div class="card" style="text-align:center;padding:1.2rem">
      <div class="card-title" style="margin-bottom:0.5rem">{label}</div>
      <div style="font-family:'Space Mono',monospace;font-size:2rem;
                  font-weight:700;color:{color}">{value}{unit}</div>
    </div>""", unsafe_allow_html=True)


def _section_divider(tag: str) -> None:
    st.markdown(
        f'<div class="section-header">'
        f'  <div class="section-line"></div>'
        f'  <div class="section-tag">{tag}</div>'
        f'  <div class="section-line"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────────────────
# 3. COMPOSITE COMPONENTS
# ──────────────────────────────────────────────────────────────────────────────

def render_hero() -> None:
    """Full-width animated hero banner shown at the top of the page."""
    st.markdown("""
    <div class="hero animate">
      <div class="hero-badge">⚡ AI · NLP · LLM Powered</div>
      <h1>Resume Intelligence<br>Redefined.</h1>
      <p>Parse your resume with NLP, extract skills automatically,
         match against job descriptions, and get LLM-powered suggestions
         to land your dream AIML role.</p>
      <div class="hero-stats">
        <div class="stat-item">
          <div class="stat-num">98%</div>
          <div class="stat-label">Parse Accuracy</div>
        </div>
        <div class="stat-item">
          <div class="stat-num">50+</div>
          <div class="stat-label">Skill Categories</div>
        </div>
        <div class="stat-item">
          <div class="stat-num">8</div>
          <div class="stat-label">AI Suggestions</div>
        </div>
        <div class="stat-item">
          <div class="stat-num">6</div>
          <div class="stat-label">Job Matches</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_profile_card(parsed: dict) -> None:
    """Candidate identity card: avatar, name, contact, summary."""
    name    = parsed.get("name", "Candidate")
    email   = parsed.get("email", "—")
    phone   = parsed.get("phone", "—")
    loc     = parsed.get("location", "—")
    summary = parsed.get("summary", "—")
    initial = name[0].upper() if name else "C"

    st.markdown(f"""
    <div class="card animate delay-1">
      <div style="display:flex;align-items:center;gap:1.2rem;margin-bottom:1.2rem">
        <div style="width:52px;height:52px;
                    background:linear-gradient(135deg,#7c3aed,#06b6d4);
                    border-radius:50%;display:flex;align-items:center;
                    justify-content:center;font-size:1.4rem;
                    font-weight:800;color:white">{initial}</div>
        <div>
          <div style="font-size:1.3rem;font-weight:700">{name}</div>
          <div style="font-size:0.82rem;color:#64748b;
                      font-family:'Space Mono',monospace">{email} · {phone}</div>
        </div>
      </div>
      <div style="font-size:0.82rem;color:#64748b;margin-bottom:4px">📍 {loc}</div>
      <div style="margin-top:1rem;font-size:0.9rem;color:#94a3b8;line-height:1.7;
                  border-top:1px solid #2a2a3a;padding-top:1rem">{summary}</div>
    </div>""", unsafe_allow_html=True)


def render_edu_card(parsed: dict) -> None:
    """Education + certifications card."""
    edu   = parsed.get("education", [])
    certs = parsed.get("certifications", [])

    edu_html = "".join(
        f'<div style="margin:6px 0">'
        f'  <span style="color:#a78bfa">🎓</span> '
        f'  <b>{e.get("degree","")}</b> · '
        f'  <span style="color:#64748b;font-size:0.85rem">'
        f'    {e.get("institution","")} {e.get("year","")}'
        f'  </span>'
        f'</div>'
        for e in edu
    )
    cert_html = "".join(
        f'<div style="margin:6px 0;font-size:0.85rem">'
        f'  <span style="color:#f59e0b">🏅</span> {c}'
        f'</div>'
        for c in certs
    )

    st.markdown(f"""
    <div class="card animate delay-2">
      <div class="card-title">Education &amp; Certifications</div>
      {edu_html}
      {cert_html}
    </div>""", unsafe_allow_html=True)


def render_experience(experience: list[dict]) -> None:
    """Render a list of work-experience cards with highlights."""
    for i, exp in enumerate(experience):
        highlights = exp.get("highlights", [])
        hl_html = "".join(
            f'<li style="margin:4px 0;color:#94a3b8;font-size:0.85rem">{h}</li>'
            for h in highlights[:3]
        )
        delay = min(i + 1, 4)
        st.markdown(f"""
        <div class="card animate delay-{delay}">
          <div style="display:flex;justify-content:space-between;align-items:start">
            <div>
              <div style="font-weight:700;font-size:1rem">{exp.get("title","")}</div>
              <div style="color:#a78bfa;font-size:0.85rem;margin:2px 0">
                {exp.get("company","")}
              </div>
            </div>
            <div style="font-family:'Space Mono',monospace;font-size:0.75rem;
                        color:#64748b;background:#1a1a25;
                        padding:4px 10px;border-radius:6px">
              {exp.get("duration","")}
            </div>
          </div>
          <ul style="margin:10px 0 0 1rem;padding:0">{hl_html}</ul>
        </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 4. FULL TAB RENDERERS
# ──────────────────────────────────────────────────────────────────────────────

def render_tab_dashboard(parsed: dict, analysis: dict) -> None:
    """Render the complete Dashboard tab (Tab 1)."""

    # ── KPI metric row ──
    m1, m2, m3, m4, m5 = st.columns(5)
    kpis = [
        (m1, "Overall Match",  analysis.get("overall_score", 0),       "%"),
        (m2, "ATS Score",      analysis.get("ats_score", 0),            "%"),
        (m3, "Skill Match",    analysis.get("skill_match_score", 0),    "%"),
        (m4, "Experience",     analysis.get("experience_match_score", 0), "%"),
        (m5, "Years Exp.",     parsed.get("total_experience_years", "N/A"), "yr"),
    ]
    for col, label, val, unit in kpis:
        with col:
            color = score_color(val) if isinstance(val, int) else "#06b6d4"
            render_metric_card(label, val, unit, color)

    # ── Profile section ──
    _section_divider("Candidate Profile")

    left_col, right_col = st.columns([2, 1])

    with left_col:
        render_profile_card(parsed)
        render_edu_card(parsed)

    with right_col:
        render_donut(analysis.get("overall_score", 0), "Overall Match")

        breakdown = analysis.get("score_breakdown", {})
        score_colors = {
            "skills":     "#7c3aed",
            "experience": "#06b6d4",
            "keywords":   "#10b981",
            "format":     "#f59e0b",
            "education":  "#f472b6",
        }
        st.markdown(
            '<div class="card" style="margin-top:1rem">'
            '<div class="card-title">Score Breakdown</div>',
            unsafe_allow_html=True,
        )
        for key, val in breakdown.items():
            render_progress(key.title(), int(val), score_colors.get(key, "#7c3aed"))
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Experience section ──
    _section_divider("Work Experience")
    render_experience(parsed.get("experience", []))


def render_tab_skills(parsed: dict, analysis: dict) -> None:
    """Render the complete Skills Analysis tab (Tab 2)."""

    left_col, right_col = st.columns(2)

    with left_col:
        st.markdown('<div class="card"><div class="card-title">✅ Matched Skills</div>',
                    unsafe_allow_html=True)
        render_skills(analysis.get("matched_skills", []), "skill-match")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">⭐ Bonus Skills (Extra)</div>',
                    unsafe_allow_html=True)
        render_skills(analysis.get("bonus_skills", []), "skill-neutral")
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="card"><div class="card-title">❌ Missing Skills (Gap)</div>',
                    unsafe_allow_html=True)
        render_skills(analysis.get("missing_skills", []), "skill-missing")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title">🛠 Tools &amp; Technologies</div>',
                    unsafe_allow_html=True)
        tools = parsed.get("tools_technologies") or parsed.get("skills", [])
        render_skills(tools, "skill-neutral")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Match dimension donuts ──
    _section_divider("Match Dimensions")
    d1, d2, d3 = st.columns(3)
    dims = [
        (d1, "Skill Match",       analysis.get("skill_match_score", 0)),
        (d2, "Experience Match",  analysis.get("experience_match_score", 0)),
        (d3, "Keyword Density",   analysis.get("keyword_density", 0)),
    ]
    for col, label, score in dims:
        with col:
            render_donut(score, label)


def render_tab_suggestions(suggestions: list[str]) -> None:
    """Render the complete AI Suggestions tab (Tab 3)."""

    st.markdown("""
    <div class="card"
         style="background:rgba(124,58,237,0.06);
                border-color:rgba(124,58,237,0.3);
                margin-bottom:1.5rem">
      <div style="display:flex;gap:1rem;align-items:center">
        <div style="font-size:2rem">🤖</div>
        <div>
          <div style="font-weight:700;margin-bottom:4px">AI-Powered Career Coach</div>
          <div style="font-size:0.88rem;color:#94a3b8">
            These suggestions are generated by Claude based on your resume vs the job
            description. Implement them to significantly improve your match score.
          </div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    for i, suggestion in enumerate(suggestions):
        delay = min(i % 4 + 1, 4)
        st.markdown(f"""
        <div class="suggestion animate delay-{delay}">
          <div class="suggestion-num">Suggestion #{i + 1:02d}</div>
          {suggestion}
        </div>""", unsafe_allow_html=True)


def render_tab_jobs(job_matches: list[dict]) -> None:
    """Render the complete Job Matches tab (Tab 4)."""

    st.markdown("""
    <div style="margin-bottom:1.5rem;color:#94a3b8;font-size:0.9rem">
      🎯 Roles matched by AI based on your skills, experience, and profile —
      sorted by compatibility.
    </div>""", unsafe_allow_html=True)

    sorted_jobs = sorted(job_matches, key=lambda x: x.get("match_score", 0), reverse=True)

    for job in sorted_jobs:
        sc    = job.get("match_score", 0)
        color = score_color(sc)
        st.markdown(f"""
        <div class="job-card animate">
          <div>
            <div class="job-title">{job.get("title","")}</div>
            <div class="job-meta">
              {job.get("company_type","")} ·
              {job.get("location","")} ·
              {job.get("salary_range","")}
            </div>
            <div style="font-size:0.82rem;color:#64748b;margin-top:6px">
              {job.get("why_fit","")}
            </div>
          </div>
          <div class="job-score" style="color:{color};min-width:60px;text-align:right">
            {sc}<span style="font-size:0.9rem;color:#64748b">%</span>
          </div>
        </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# 5. PAGE-LEVEL COMPONENTS
# ──────────────────────────────────────────────────────────────────────────────

def render_sidebar_brand() -> None:
    """Logo / brand block at the top of the sidebar."""
    st.markdown("""
    <div style="padding:1rem 0 1.5rem">
      <div style="font-family:'Space Mono',monospace;font-size:0.65rem;
                  color:#64748b;letter-spacing:2px;text-transform:uppercase;
                  margin-bottom:6px">ResumeIQ</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800;
                  background:linear-gradient(135deg,#a78bfa,#67e8f9);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent">
        AI Resume Analyzer
      </div>
    </div>""", unsafe_allow_html=True)


def render_sidebar_how_it_works() -> None:
    """Short explainer box at the bottom of the sidebar."""
    st.markdown("""
    <div style="margin-top:2rem;padding:1rem;
                background:rgba(124,58,237,0.08);
                border:1px solid rgba(124,58,237,0.2);
                border-radius:10px">
      <div style="font-size:0.72rem;color:#a78bfa;font-family:'Space Mono',monospace;
                  letter-spacing:1px;text-transform:uppercase;margin-bottom:8px">
        How it works
      </div>
      <div style="font-size:0.82rem;color:#94a3b8;line-height:1.7">
        1. Upload your resume<br>
        2. Paste a job description<br>
        3. Get AI-powered analysis,<br>
        &nbsp;&nbsp;&nbsp;skill gaps &amp; match score<br>
        4. Receive tailored suggestions
      </div>
    </div>""", unsafe_allow_html=True)


def render_empty_state() -> None:
    """Placeholder shown before the first analysis is run."""
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#64748b">
      <div style="font-size:4rem;margin-bottom:1rem">📄</div>
      <div style="font-family:'Syne',sans-serif;font-size:1.3rem;
                  font-weight:700;margin-bottom:0.5rem;color:#94a3b8">
        Ready to analyze your resume
      </div>
      <div style="font-size:0.9rem;max-width:400px;margin:0 auto;line-height:1.7">
        Upload your resume and paste a job description in the sidebar,<br>
        then click <b style="color:#a78bfa">⚡ Analyze Resume</b> —
        or load the demo to see it in action.
      </div>
    </div>""", unsafe_allow_html=True)
